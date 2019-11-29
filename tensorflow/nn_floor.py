import datetime
import os
from PIL import Image, ImageDraw
import numpy
import glob
import scipy
import random
import argparse
from sklearn.utils import shuffle

import tensorflow as tf
from tensorflow.keras.callbacks import TensorBoard


HEIGHT = 96
WIDTH = 96
NUM_CHANNELS = 3
NUM_CLASSES = 1


def augmentation(x):
	# crop
	x = tf.image.resize_with_crop_or_pad(x, HEIGHT + 8, WIDTH + 8)
	x = tf.image.random_crop(x, [HEIGHT, WIDTH, NUM_CHANNELS])
	
	# flip
	x = tf.image.random_flip_left_right(x)
	
	
	# rotate
	angle = random.uniform(-0.5, 0.5)
	x = scipy.ndimage.rotate(x, angle , axes=(1, 0), reshape=False, order=3, mode='constant', cval=0.0, prefilter=True)
	
	return x
	

def standardize_img(x):
	mean = numpy.mean(x, axis=None, keepdims=True)
	std = numpy.sqrt(((x - mean)**2).mean(axis=None, keepdims=True))
	return (x - mean) / std


def load_img(file_path):
	img = Image.open(file_path)
	img.load()
	img = img.resize((WIDTH, HEIGHT))
	img = numpy.asarray(img, dtype="int32")
	img = img.astype("float")
	return img


def load_imgs(path_list, params, use_augmentation = False, augmentation_factor = 1, use_shuffle = False):	
	num_images = len(path_list)
	if use_augmentation:
		num_images *= augmentation_factor
	
	X = numpy.zeros((num_images, WIDTH, HEIGHT, 3), dtype=float)
	Y = numpy.zeros((num_images), dtype=float)
	
	i = 0
	for file_path in path_list:
		imgx = load_img(file_path)
		file_name = os.path.basename(file_path)
		imgy = max(params[file_name])
		if use_augmentation:
			for j in range(augmentation_factor):
				img_tmp = augmentation(imgx)
				X[i * augmentation_factor + j,:,:,:] = standardize_img(img_tmp)
				Y[i * augmentation_factor + j] = imgy
		else:
			X[i,:,:,:] = standardize_img(imgx)
			Y[i] = imgy
		
		i += 1
		
	if use_shuffle:
		X, Y = shuffle(X, Y, random_state=0)
	

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


def build_model(int_shape, num_params, learning_rate):
	model = tf.keras.Sequential([
		tf.keras.layers.Dense(64, activation='relu', input_shape=int_shape, name='fc1'),
		tf.keras.layers.Dense(64, activation='relu', name='fc2'),
		tf.keras.layers.GlobalAveragePooling2D(name='avg_pool'),
		tf.keras.layers.Dense(num_params, name='fc3')
	])

	optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

	model.compile(loss='mse',
		optimizer=optimizer,
		metrics=['mae', 'mse'])
	return model
  

def train(input_dir, num_epochs, learning_late, use_augmentation, augmentation_factor, output_dir):
	# Load parameters
	params = load_annotation("facade_annotation.txt")


	# Split the tensor into train and test dataset
	path_list = glob.glob("{}/*.jpg".format(input_dir))
	X, Y = load_imgs(path_list, params, use_augmentation = use_augmentation, augmentation_factor = augmentation_factor, use_shuffle = True)
	print(X.shape)


	# Build model
	model = build_model((HEIGHT, WIDTH, NUM_CHANNELS), NUM_CLASSES, learning_late)


	# Setup for Tensorboard
	log_dir="logs\\fit\\" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
	file_writer = tf.summary.create_file_writer(log_dir + "\\metrics")
	file_writer.set_as_default()
	tensorboard_callback = TensorBoard(
		log_dir=log_dir,
		update_freq='batch',
		histogram_freq=1)


	# Training model
	model.fit(X, Y,
		epochs=num_epochs,
		validation_split = 0.2,
		callbacks=[tensorboard_callback])


	# Save the model
	model.save("{}/nn_model.h5".format(output_dir))


def test(input_dir, output_dir):
	# Load parameters
	params = load_annotation("facade_annotation.txt")


	# Split the tensor into train and test dataset
	path_list = glob.glob("{}/*.jpg".format(input_dir))
	X, Y = load_imgs(path_list, params)

		  
	# Load the model
	model = tf.keras.models.load_model("{}/nn_model.h5".format(output_dir))
	
	
	# Evaluation
	model.evaluate(X, Y)
	

	# Prediction
	predictedY = model.predict(X).flatten()


	# Write the prediction to a file
	file = open("{}/prediction.txt".format(output_dir), "w")
	for i in range(len(path_list)):
		file_name = os.path.basename(path_list[i])
		file.write("{},{}\n".format(file_name, predictedY[i]))
	file.close()


	# Save the predicted images
	for i in range(len(path_list)):
		file_name = os.path.basename(path_list[i])
		img = Image.open(path_list[i])
		w, h = img.size
		imgdraw = ImageDraw.Draw(img)
		imgdraw.line([(0, h * predictedY[i]), (w, h * predictedY[i])], fill = "yellow", width = 3)
		img.save("{}/{}".format(output_dir, file_name))


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--mode', required=True, choices=["train", "test"])
	parser.add_argument('--input_dir', required=True, help="path to folder containing images")
	parser.add_argument('--output_dir', default="out", help="where to put output files")
	parser.add_argument('--num_epochs', type=int, default=10)
	parser.add_argument('--learning_rate', type=float, default=0.001)
	parser.add_argument('--use_augmentation', action="store_true", help="Use augmentation for training images")
	parser.add_argument('--augmentation_factor', type=int, default=100)
	args = parser.parse_args()


	# Create output directoryu
	if not os.path.isdir(args.output_dir):
		os.mkdir(args.output_dir)
	

	if args.mode == "train":
		train(args.input_dir, args.num_epochs, args.learning_rate, args.use_augmentation, args.augmentation_factor, args.output_dir)
	elif args.mode == "test":
		test(args.input_dir, args.output_dir)
	else:
		print("Invalid mode is specified {}".format(args.mode))
		exit(1)
	

if __name__== "__main__":
	main()
