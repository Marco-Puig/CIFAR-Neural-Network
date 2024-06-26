"""
Generated by Colab.

Deep Learning CNN Trained on the CIFAR10 Dataset

*   Marco Puig
*   April 15th 2024
"""

# SECTION A

# Imports
from keras.datasets import cifar10
import matplotlib.pyplot as plt
import numpy as np
from random import randint
from keras.utils import to_categorical
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten, Dropout, Activation, MaxPooling2D, BatchNormalization
from keras.callbacks import ModelCheckpoint
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score

# Helper functions
def feat_plot(features, labels, classes):
    for class_i in classes:
        plt.plot(features[labels == class_i, 0], features[labels == class_i, 1], 'o', markersize=15)
    plt.axis([-2, 2, -2, 2])
    plt.xlabel('x: feature 1')
    plt.ylabel('y: feature 2')
    plt.legend(['class'+str(class_i) for class_i in classes])
    plt.show()

def acc_fun(labels_actual, labels_pred):
    acc = np.sum(labels_actual == labels_pred) / len(labels_actual) * 100
    return acc

def img_plt(images, labels):
    plt.figure() # figsize=(15,6)
    for i in range(1, 11):
        plt.subplot(2, 5, i)
        plt.imshow(images[i-1], cmap='gray')
        plt.title('Label: ' + str(labels[i-1]))
    plt.show()

def plot_curve(accuracy_train, loss_train, accuracy_val, loss_val):
    epochs = np.arange(loss_train.shape[0])
    plt.subplot(1, 2, 1)
    plt.plot(epochs,accuracy_train,epochs,accuracy_val)
    #plt.axis([1, , , ])
    plt.xlabel('Epoch#')
    plt.ylabel('Accuracy')
    plt.title('Accuracy')
    plt.legend(['Training', 'Validation'])

    plt.subplot(1, 2, 2)
    plt.plot(epochs,loss_train,epochs,loss_val)
    plt.xlabel('Epoch#$')
    plt.ylabel('Binary crossentropy loss')
    plt.title('Loss')
    plt.legend(['Training', 'Validation'])
    plt.show()

# Load the CIFAR-10 dataset
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
classes = np.arange(10)

# Selecting 20% of training data as the validation set & then shuffling
num_train_img=x_train.shape[0]
train_ind=np.arange(0, num_train_img)
train_ind_s=np.random.permutation(train_ind)
x_train=x_train[train_ind_s, :, :]
y_train=y_train[train_ind_s]

# Selecting 20% of training images for validation
x_val=x_train[:int(0.2*num_train_img),:,:]
y_val=y_train[:int(0.2*num_train_img)]

# The rest of the training set
x_train=x_train[int(0.2*num_train_img):,:,:]
y_train=y_train[int(0.2*num_train_img):]

# SECTION B

# Plot training images
print('Samples of the training images')
img_plt(x_train[0:10,:,:], y_train[0:10])

# Scaling the images
x_train=x_train.astype('float32')
x_val=x_val.astype('float32')
x_test=x_test.astype('float32')

x_train/=255
x_val/=255
x_test/=255

# SECTION C

# Convert the label vectors for all the sets to binary class matrices using to_categorical() Keras function.
y_train_c = to_categorical(y_train, len(classes))
y_val_c = to_categorical(y_val, len(classes))
y_test_c = to_categorical(y_test, len(classes))

# SECTION D

# Defining the model
model_a = Sequential()
model_a.add(Conv2D(32, (3, 3), padding='same', input_shape=x_train.shape[1:]))
model_a.add(Activation('relu'))
model_a.add(Conv2D(32, (3, 3), padding='same'))
model_a.add(Activation('relu'))
model_a.add(MaxPooling2D(pool_size=(2, 2)))

model_a.add(Conv2D(64, (3, 3), padding='same'))
model_a.add(Activation('relu'))
model_a.add(Conv2D(64, (3, 3), padding='same'))
model_a.add(Activation('relu'))
model_a.add(MaxPooling2D(pool_size=(2, 2)))

model_a.add(Flatten())
model_a.add(Dense(units=512, activation='relu'))
model_a.add(Dropout(0.5))
model_a.add(Dense(units=len(classes), activation='softmax'))
model_a.summary()

# SECTION E

# Compiling and using Adam
opt = tf.keras.optimizers.Adam(learning_rate=0.001)
model_a.compile(loss='categorical_crossentropy',
                optimizer=opt,
                metrics=['accuracy'])

#compute quantities required for featurewise normalization
#(std, mean, and principal components if ZCA whitening is applied)

#creating a checkpoint to save the best model based on the lowest validation loss.
save_path='/content/drive/My Drive/model_a_fashion_mnist.h5'
callbacks_save=ModelCheckpoint(save_path, monitor='val_loss', verbose=0, save_best_only=True, save_freq='epoch')

#fits the model on batches with real-time data augmentation:
history = model_a.fit(x_train, y_train_c, batch_size=16,
                      epochs=50,
                      verbose=1,
                      validation_data=(x_val, y_val_c),
                      callbacks=[callbacks_save])

plt.figure(figsize=[9,5])
acc_curve_train=np.array(history.history['accuracy'])
loss_curve_train=np.array(history.history['loss'])
acc_curve_val=np.array(history.history['val_accuracy'])
loss_curve_val=np.array(history.history['val_loss'])
plot_curve(acc_curve_train, loss_curve_train, acc_curve_val, loss_curve_val)

# loading the best model- saved based on the lowest validation loss
model_a = load_model(save_path)

#evaluating the model on the training samples
score = model_a.evaluate(x_train, y_train_c)
print('Total loss on training set: ', score[0])
print('Accuracy of training set: ', score[1])

#evaluating the model on the validation samples
score = model_a.evaluate(x_val, y_val_c)
print('Total loss on validation set: ', score[0])

# SECTION F

# Compiling and using Adam
opt = tf.keras.optimizers.Adam(learning_rate=0.001)
model_a.compile(loss='categorical_crossentropy',
                optimizer=opt,
                metrics=['accuracy'])

#creating a data generator for real-time data augmentation
datagen = ImageDataGenerator(
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True)

#compute quantities required for featurewise normalization
#(std, mean, and principal components if ZCA whitening is applied)
datagen.fit(x_train)

#creating a checkpoint to save the best model based on the lowest validation loss.
save_path='/content/drive/My Drive/model_a_fashion_mnist.h5'
callbacks_save=ModelCheckpoint(save_path, monitor='val_loss', verbose=0, save_best_only=True, save_freq='epoch')

#fits the model on batches with real-time data augmentation:
history = model_a.fit(datagen.flow(x_train, y_train_c, batch_size=16),
                      steps_per_epoch=len(x_train) / 16, epochs=50,
                      verbose=1,
                      validation_data=(x_val, y_val_c),
                      callbacks=[callbacks_save])

plt.figure(figsize=[9,5])
acc_curve_train=np.array(history.history['accuracy'])
loss_curve_train=np.array(history.history['loss'])
acc_curve_val=np.array(history.history['val_accuracy'])
loss_curve_val=np.array(history.history['val_loss'])
plot_curve(acc_curve_train, loss_curve_train, acc_curve_val, loss_curve_val)

# loading the best model- saved based on the lowest validation loss
model_a = load_model(save_path)

#evaluating the model on the training samples
score = model_a.evaluate(x_train, y_train_c)
print('Total loss on training set: ', score[0])
print('Accuracy of training set: ', score[1])

#evaluating the model on the validation samples
score = model_a.evaluate(x_val, y_val_c)
print('Total loss on validation set: ', score[0])

# SECTION H

# Defining the model
model_a = Sequential()
model_a.add(Conv2D(32, (3, 3), padding='same', input_shape=x_train.shape[1:]))
model_a.add(BatchNormalization())
model_a.add(Activation('relu'))
model_a.add(Conv2D(32, (3, 3), padding='same'))
model_a.add(Activation('relu'))
model_a.add(MaxPooling2D(pool_size=(2, 2)))

model_a.add(Conv2D(64, (3, 3), padding='same'))
model_a.add(BatchNormalization())
model_a.add(Activation('relu'))
model_a.add(Conv2D(64, (3, 3), padding='same'))
model_a.add(Activation('relu'))
model_a.add(MaxPooling2D(pool_size=(2, 2)))

model_a.add(Flatten())
model_a.add(Dense(units=512, activation='relu'))
model_a.add(BatchNormalization())
model_a.add(Dropout(0.5))
model_a.add(Dense(units=len(classes), activation='softmax'))
model_a.summary()

# Compiling and using Adam
opt = tf.keras.optimizers.Adam(learning_rate=0.01)
model_a.compile(loss='categorical_crossentropy',
                optimizer=opt,
                metrics=['accuracy'])

#compute quantities required for featurewise normalization
#(std, mean, and principal components if ZCA whitening is applied)

#creating a checkpoint to save the best model based on the lowest validation loss.
save_path='/content/drive/My Drive/model_a_fashion_mnist.h5'
callbacks_save=ModelCheckpoint(save_path, monitor='val_loss', verbose=0, save_best_only=True, save_freq='epoch')

#fits the model on batches with real-time data augmentation:
history = model_a.fit(x_train, y_train_c, batch_size=64,
                      epochs=50,
                      verbose=1,
                      validation_data=(x_val, y_val_c),
                      callbacks=[callbacks_save])

plt.figure(figsize=[9,5])
acc_curve_train=np.array(history.history['accuracy'])
loss_curve_train=np.array(history.history['loss'])
acc_curve_val=np.array(history.history['val_accuracy'])
loss_curve_val=np.array(history.history['val_loss'])
plot_curve(acc_curve_train, loss_curve_train, acc_curve_val, loss_curve_val)

# loading the best model- saved based on the lowest validation loss
model_a = load_model(save_path)

#evaluating the model on the training samples
score = model_a.evaluate(x_train, y_train_c)
print('Total loss on training set: ', score[0])
print('Accuracy of training set: ', score[1])

#evaluating the model on the validation samples
score = model_a.evaluate(x_val, y_val_c)
print('Total loss on validation set: ', score[0])