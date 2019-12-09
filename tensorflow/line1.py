import datetime
import os
from PIL import Image, ImageDraw
import numpy
import scipy.misc
import glob
import scipy
import random
import argparse
import cv2

import tensorflow as tf
from tensorflow.keras.callbacks import TensorBoard


HEIGHT = 160
WIDTH = 160
NUM_CHANNELS = 3
NUM_CLASSES = 1
MODEL_FILE_NAME = "line1_model.h5"

DEBUG_DIR = "__debug__"

def augmentation(x, y):
	height, width, num_channels = x.shape
	
	# crop
	#shift_h = int(width * 0.1)
	#shift_v = int(height * 0.1)
	shift_h = 4
	shift_v = 4
	offset_x = int(random.uniform(0, shift_h * 2))
	offset_y = int(random.uniform(0, shift_v * 2))
	x = tf.image.resize_with_crop_or_pad(x, height + shift_v * 2, width + shift_h * 2)
	x = x[offset_y:offset_y+height, offset_x:offset_x+width,:]
	y = (y * height + shift_v - offset_y) / height
	if y < 0 or y > 1:
		y = 0
	
	# flip
	x = tf.image.random_flip_left_right(x)
		
	# rotate
	angle = random.uniform(-0.5, 0.5)
	x = scipy.ndimage.rotate(x, angle , axes=(1, 0), reshape=False, order=3, mode='constant', cval=0.0, prefilter=True)
	
	return x, y
	

def standardize_img(x):
	mean = numpy.mean(x, axis=None, keepdims=True)
	std = numpy.sqrt(((x - mean)**2).mean(axis=None, keepdims=True))
	return (x - mean) / std


def load_img(file_path):
	img = Image.open(file_path)
	img.load()
	img = numpy.asarray(img, dtype="int32")
	
	# Convert image to grayscale
	r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]
	gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
	img[:,:,0] = gray
	img[:,:,1] = gray
	img[:,:,2] = gray
	
	img = img.astype("float")
	return img


def load_imgs(params, use_shuffle = False):
	num_images = len(params)
	
	X = numpy.zeros((num_images, HEIGHT, WIDTH, NUM_CHANNELS), dtype=float)
	Y = numpy.zeros((num_images), dtype=float)
	
	# Load images
	for i in range(num_images):
		img = numpy.ones((HEIGHT, WIDTH, NUM_CHANNELS), dtype=float)
		row = int(params[i] * HEIGHT)
		
		# Draw horizontal line
		img[row,:,:] = numpy.zeros((WIDTH, NUM_CHANNELS), dtype=float)
		
		X[i,:,:,:] = standardize_img(img)
		Y[i] = params[i]
			
	if use_shuffle:
		randomize = numpy.arange(len(X))
		numpy.random.shuffle(randomize)
		X = X[randomize]
		Y = Y[randomize]

	return X, Y

def output_img(x, y, filename):
	print(x.shape)
	img = Image.fromarray(x.astype(numpy.uint8))
	w, h = img.size
	imgdraw = ImageDraw.Draw(img)
	
	imgdraw.line([(0, h * y), (w, h * y)], fill = "yellow", width = 3)
	img.save("{}".format(filename))		
		
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
		tf.keras.applications.MobileNetV2(input_shape=(WIDTH, HEIGHT, 3), include_top=False, weights='imagenet'),
		tf.keras.layers.Flatten(),
		tf.keras.layers.Dense(512, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),
		tf.keras.layers.Dropout(0.5),
		tf.keras.layers.Dense(512, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),
		tf.keras.layers.Dropout(0.5),
		tf.keras.layers.Dense(num_params),
	])
	
	optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
	
	model.compile(
		loss='mse',
		optimizer=optimizer,
		metrics=['mae', 'mse'])
	
	return model
  

def train(num_images, model_dir, num_epochs, learning_late, output_dir):
	params = []
	for i in range(num_images):
		params.append(random.uniform(0.1, 0.9))
	params = numpy.array(params)	
	X, Y = load_imgs(params, use_shuffle = True)
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
	model.save("{}/{}".format(model_dir, MODEL_FILE_NAME))


def test(num_images, model_dir, all_floors, output_dir):
	params = []
	for i in range(num_images):
		params.append(random.uniform(0.1, 0.9))
	params = numpy.array(params)	
	X, Y = load_imgs(path_list, params, all_floors = all_floors)
		  
	# Load the model
	model = tf.keras.models.load_model("{}/{}".format(model_dir, MODEL_FILE_NAME))
		
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
		print(path_list[i])
		orig_x = load_img(path_list[i])
		orig_height = orig_x.shape[0]

		x = cv2.resize(orig_x, dsize=(WIDTH, HEIGHT), interpolation=cv2.INTER_CUBIC)
		height = orig_height
		
		# Repeatedly predict floors
		Y = []
		while True:		
			# Prediction
			X = numpy.zeros((1, WIDTH, HEIGHT, 3), dtype=float)
			X[0,:,:,:] = standardize_img(x)
			y = model.predict(X).flatten()[0]
			y = numpy.clip(y * height / orig_height, a_min = 0, a_max = 1)
			if height * y < 20: break
			Y.append(y)
			
			if not all_floors: break
			
			# Update image
			height = int(orig_height * y)
			x = orig_x[0:height,:,:]
			x = cv2.resize(x, dsize=(WIDTH, HEIGHT), interpolation=cv2.INTER_CUBIC)
		
		# Load image
		file_name = os.path.basename(path_list[i])
		img = Image.open(path_list[i])
		w, h = img.size
		imgdraw = ImageDraw.Draw(img)
		
		for y in Y:
			imgdraw.line([(0, h * y), (w, h * y)], fill = "yellow", width = 3)
		img.save("{}/{}".format(output_dir, file_name))


def main():	
	parser = argparse.ArgumentParser()
	parser.add_argument('--mode', required=True, choices=["train", "test"])
	parser.add_argument('--output_dir', default="out", help="where to put output files")
	parser.add_argument('--model_dir', default="models", help="path to folder containing models")
	parser.add_argument('--num_epochs', type=int, default=10)
	parser.add_argument('--learning_rate', type=float, default=0.0001)
	args = parser.parse_args()	

	# Create output directory
	if not os.path.isdir(args.output_dir):
		os.mkdir(args.output_dir)

	if args.mode == "train":
		train(10000, args.model_dir, args.num_epochs, args.learning_rate, args.output_dir)
	elif args.mode == "test":
		test(20, args.model_dir, args.all_floors, args.output_dir)
	else:
		print("Invalid mode is specified {}".format(args.mode))
		exit(1)
	

if __name__== "__main__":
	main()
