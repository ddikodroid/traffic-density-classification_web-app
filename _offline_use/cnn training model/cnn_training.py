from numpy.random import seed
seed=27
import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import AveragePooling2D
from tensorflow.keras.callbacks import History
from tensorflow.keras.callbacks import CSVLogger
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator

model = Sequential()

model.add(Conv2D(40, (3,3), (287,304,3)))
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Conv2D(40, (3,3)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D((2,2)))

model.add(Conv2D(16, (3,3)))
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Conv2D(16, (3,3)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(AveragePooling2D((2,2)))

model.add(Conv2D(32, (3,3)))
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Conv2D(32, (3,3)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D((2,2)))

model.add(Conv2D(8, (3,3)))
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Conv2D(8, (3,3)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(AveragePooling2D((2,2)))

model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(6, activation='softmax'))

lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=0.01,
    decay_steps=10000,
    decay_rate=0.9)
optimizer = tf.keras.optimizers.SGD(learning_rate=lr_schedule)

model.compile(
    optimizer=optimizer, 
    loss='categorical_crossentropy', 
    metrics=['accuracy'])
model.summary()

image_datagen = ImageDataGenerator(validation_split=0.2)
n_batch = 16 #32, 64

train_set = image_datagen.flow_from_directory(
    'DATASET_DIR', 
    target_size=(287,304),
    batch_size=n_batch, 
    class_mode='categorical', 
    subset='training')

validation_set = image_datagen.flow_from_directory(
    'DATASET_DIR', 
    target_size=(287,304),
    batch_size=n_batch, 
    class_mode='categorical', 
    subset='validation')

csv_logger = CSVLogger('FILE_NAME.log')
checkpointer = ModelCheckpoint(
    filepath='DIR/MODEL.{epoch:02d}-{val_loss:.2f}.hdf5', 
    verbose=1, 
    save_best_only=True)

history = model.fit_generator(
    train_set, 
    epochs=50, 
    validation_data=validation_set, 
    callbacks=[csv_logger, checkpointer])

model.save_weights("WEIGHT.h5")
model.save("MODEL.h5")