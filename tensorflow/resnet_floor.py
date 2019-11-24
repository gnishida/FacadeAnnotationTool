import datetime
import os

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.callbacks import TensorBoard, LearningRateScheduler

import resnet


NUM_GPUS = 1
BS_PER_GPU = 128
NUM_EPOCHS = 60

HEIGHT = 256
WIDTH = 256
NUM_CHANNELS = 3
NUM_CLASSES = 10
NUM_TRAIN_SAMPLES = 50000

BASE_LEARNING_RATE = 0.1
LR_SCHEDULE = [(0.1, 30), (0.01, 45)]


def normalize(x, y):
  x = tf.image.per_image_standardization(x)
  return x, y


def augmentation(x, y):
    x = tf.image.resize_with_crop_or_pad(
        x, HEIGHT + 8, WIDTH + 8)
    x = tf.image.random_crop(x, [HEIGHT, WIDTH, NUM_CHANNELS])
    x = tf.image.random_flip_left_right(x)
    return x, y	


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
	#load data as string
	img = tf.io.read_file(file_path)
	#convert string to 3d uint8 tensor
	img = tf.image.decode_jpeg(img, channels=3)
	# Use `convert_image_dtype` to convert to floats in the [0,1] range.
	img = tf.image.convert_image_dtype(img, tf.float32)

	print(file_path)
	
	return tf.image.resize(img, [WIDTH, HEIGHT])

def load_annotation(file_path):
	params = {}
	file = open(file_path, "r")
	for line in file.readlines():
		values = []
		data = line.split(',')
		if len(data) > 1:
			for i in range(1,len(data)):
				values.append(float(data[i].strip()))
			params[data[0]] = values
	return params


params = load_annotation("facade_annotation.txt")

# Load all the images into dataset
#list_ds = tf.data.Dataset.list_files("D:/Users/Gen Nishida/Documents/facade/ECP/images/*.jpg")
#list_ds = list_ds.map(load_img)
#for image in list_ds.take(1):
#	print("Image shape: ", image.numpy().shape)


img = load_annotation("D:/Users/Gen Nishida/Documents/facade/ECP/images/monge_1.jpg")
print(img)
quit()


# Split dataset into train and test
train_ds = list_ds.take(70) 
test_ds = list_ds.skip(70)


quit()

(x,y), (x_test, y_test) = keras.datasets.cifar10.load_data()

train_dataset = tf.data.Dataset.from_tensor_slices((x,y))
test_dataset = tf.data.Dataset.from_tensor_slices((x_test, y_test))

tf.random.set_seed(22)
train_dataset = train_dataset.map(augmentation).map(normalize).shuffle(NUM_TRAIN_SAMPLES).batch(BS_PER_GPU * NUM_GPUS, drop_remainder=True)
test_dataset = test_dataset.map(normalize).batch(BS_PER_GPU * NUM_GPUS, drop_remainder=True)


input_shape = (HEIGHT, WIDTH, NUM_CHANNELS)
img_input = tf.keras.layers.Input(shape=input_shape)
opt = keras.optimizers.SGD(learning_rate=0.1, momentum=0.9)

if NUM_GPUS == 1:
    model = resnet.resnet56(img_input=img_input, classes=NUM_CLASSES)
    model.compile(
              optimizer=opt,
              loss='sparse_categorical_crossentropy',
              metrics=['sparse_categorical_accuracy'])
else:
    mirrored_strategy = tf.distribute.MirroredStrategy()
    with mirrored_strategy.scope():
      model = resnet.resnet56(img_input=img_input, classes=NUM_CLASSES)
      model.compile(
                optimizer=opt,
                loss='sparse_categorical_crossentropy',
                metrics=['sparse_categorical_accuracy'])  

log_dir="logs\\fit\\" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#log_dir="logs"
file_writer = tf.summary.create_file_writer(log_dir + "\\metrics")
file_writer.set_as_default()
tensorboard_callback = TensorBoard(
  log_dir=log_dir,
  update_freq='batch',
  histogram_freq=1)

lr_schedule_callback = LearningRateScheduler(schedule)

model.fit(train_dataset,
          epochs=NUM_EPOCHS,
          validation_data=test_dataset,
          validation_freq=1,
          callbacks=[tensorboard_callback, lr_schedule_callback])
model.evaluate(test_dataset)

model.save('model.h5')

new_model = keras.models.load_model('model.h5')
 
new_model.evaluate(test_dataset)