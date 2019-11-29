import datetime
import os
from PIL import Image, ImageDraw
import numpy
import glob
import scipy
import random
from sklearn.utils import shuffle

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.callbacks import TensorBoard, LearningRateScheduler

import resnet


NUM_GPUS = 1
BS_PER_GPU = 64
NUM_EPOCHS = 60

HEIGHT = 96
WIDTH = 96
NUM_CHANNELS = 3
NUM_CLASSES = 1

BASE_LEARNING_RATE = 0.001
LR_SCHEDULE = [(0.1, 30), (0.01, 45)]

IMG_NUM =  100


def normalize(x, y):
	x = tf.image.per_image_standardization(x)
	return x, y


def augmentation(x):
	#x = tf.image.resize_with_crop_or_pad(x, HEIGHT + 8, WIDTH + 8)
	#x = tf.image.random_crop(x, [HEIGHT, WIDTH, NUM_CHANNELS])
	x = tf.image.random_flip_left_right(x)
	angle = random.uniform(-0.5, 0.5)
	x = scipy.ndimage.rotate(x, angle , axes=(1, 0), reshape=False, order=3, mode='constant', cval=0.0, prefilter=True)
	return x
	

def standardize_img(x):
	mean = numpy.mean(x, axis=None, keepdims=True)
	std = numpy.sqrt(((x - mean)**2).mean(axis=None, keepdims=True))
	return (x - mean) / std


def schedule(epoch):
	initial_learning_rate = BASE_LEARNING_RATE * BS_PER_GPU / 128
	learning_rate = initial_learning_rate
	for mult, start_epoch in LR_SCHEDULE:
		if epoch >= start_epoch:
			learning_rate = initial_learning_rate * mult
		else:
			break
	tf.summary.scalar('learning rate', data=learning_rate, step=epoch)
	return learning_rate


def load_img(file_path):
	img = Image.open(file_path)
	img.load()
	img = img.resize((WIDTH, HEIGHT))
	img = numpy.asarray(img, dtype="int32")
	img = img.astype("float")
	return img


def load_imgs(path_list, use_augmentation = False, use_shuffle = False):
	# Load image
	
	num_images = len(path_list)
	if use_augmentation:
		num_images *= IMG_NUM
	
	X = numpy.zeros((num_images, WIDTH, HEIGHT, 3), dtype=float)
	Y = numpy.zeros((num_images), dtype=float)
	
	i = 0
	for file_path in path_list:
		imgx = load_img(file_path)
		file_name = os.path.basename(file_path)
		imgy = max(params[file_name])
		if use_augmentation:
			for j in range(IMG_NUM):
				X[i * IMG_NUM + j,:,:,:] = augmentation(imgx)
				X[i * IMG_NUM + j,:,:,:] = standardize_img(X[i * IMG_NUM + j,:,:,:])
				Y[i * IMG_NUM] = imgy
		else:
			X[i,:,:,:] = standardize_img(imgx)
			Y[i] = imgy
		
		i += 1
		
	if use_shuffle:
		X, Y = shuffle(X, Y, random_state=0)
	
	# Create tensor from numpy array
	#X = tf.constant(X)
	#X = tf.compat.v2.image.per_image_standardization(X)
	#Y = tf.constant(Y)

	return X, Y
	
def load_annotation(file_path):
	params = {}
	file = open(file_path, "r")
	for line in file.readlines():
		line = line.strip()
		values = []
		data = line.split(',')
		if len(data) > 1:
			for i in range(1,len(data)):
				values.append(float(data[i].strip()))
			params[data[0]] = values
		
	return params


def build_model(int_shape, num_params):
	model = keras.Sequential([
		tf.keras.layers.Dense(64, activation='relu', input_shape=int_shape, name='fc1'),
		tf.keras.layers.Dense(64, activation='relu', name='fc2'),
		tf.keras.layers.GlobalAveragePooling2D(name='avg_pool'),
		tf.keras.layers.Dense(num_params, name='fc3')
	])

	optimizer = tf.keras.optimizers.RMSprop(0.001)

	model.compile(loss='mse',
		optimizer=optimizer,
		metrics=['mae', 'mse'])
	return model
  

# Load parameters
params = load_annotation("facade_annotation.txt")


# Split the tensor into train and test dataset
train_path_list = glob.glob("../ECP/image_train/*.jpg")
trainX, trainY = load_imgs(train_path_list, use_augmentation = True, use_shuffle = True)
test_path_list = glob.glob("../ECP/image_test/*.jpg")
testX, testY = load_imgs(test_path_list)
print(trainX.shape)
print(testX.shape)


# Build model
model = build_model((HEIGHT, WIDTH, NUM_CHANNELS), NUM_CLASSES)


# Setup for Tensorboard
log_dir="logs\\fit\\" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
file_writer = tf.summary.create_file_writer(log_dir + "\\metrics")
file_writer.set_as_default()
tensorboard_callback = TensorBoard(
	log_dir=log_dir,
	update_freq='batch',
	histogram_freq=1)


# Training model
lr_schedule_callback = LearningRateScheduler(schedule)
model.fit(trainX, trainY,
	epochs=NUM_EPOCHS,
	validation_split = 0.2,
	callbacks=[tensorboard_callback, lr_schedule_callback])
		  
		  
# Evaluation
model.evaluate(testX, testY)

# Prediction
predictedY = model.predict(testX).flatten()


# Write the prediction to a file
file = open("prediction.txt", "w")
for i in range(len(test_path_list)):
	file_name = os.path.basename(test_path_list[i])
	file.write("{},{}\n".format(file_name, predictedY[i]))
file.close()


# Save the predicted images
output_dir = "prediction_img"
if not os.path.isdir(output_dir):
	os.mkdir(output_dir)
for i in range(len(test_path_list)):
	file_name = os.path.basename(test_path_list[i])
	img = Image.open(test_path_list[i])
	w, h = img.size
	imgdraw = ImageDraw.Draw(img)
	imgdraw.line([(0, h * predictedY[i]), (w, h * predictedY[i])], fill = "yellow", width = 3)
	img.save("{}/{}".format(output_dir, file_name))


# Save the model
model.save('model.h5')


# Load the model
#new_model = keras.models.load_model('model.h5')
