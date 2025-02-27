# -*- coding: utf-8 -*-
"""mlp.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1w4qs0azGYCeUzSa_-MzOGl_DfU8A7kRX
"""

import tensorflow.keras as keras
import tensorflow as tf
import numpy as np
import time
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, LearningRateScheduler, ModelCheckpoint

class MLP:

	def __init__(self, output_directory, input_shape, nb_classes, hidden_layers_size, Early_Stopping, reduce_lr,min_lr=0.0001,verbose=False,build=True):
		self.output_directory = output_directory
		if build == True:
			self.model = self.build_model(input_shape, nb_classes,hidden_layers_size, Early_Stopping, reduce_lr,min_lr)
			if(verbose==True):
				self.model.summary()
			self.verbose = verbose
			self.model.save_weights(self.output_directory + 'model_init.mlp')

		return

	def build_model(self, input_shape, nb_classes,hidden_layers_size, Early_Stopping, reduce_lr,min_lr):


		loss = 'categorical_crossentropy'
		n_units_dense = nb_classes

		n_layers = len(hidden_layers_size)

		model = keras.models.Sequential()
		model.add(keras.layers.Input(input_shape))

		model.add(keras.layers.Flatten())

		for i in range(n_layers):
			model.add(keras.layers.Dropout(0.1))
			model.add(keras.layers.Dense(hidden_layers_size[i], activation='relu'))

		model.add(keras.layers.Dropout(0.3))
		model.add(keras.layers.Dense(n_units_dense, activation='softmax'))


		model.compile(loss=loss, optimizer=keras.optimizers.Adam(lr = 0.001, beta_1 = 0.9, beta_2 = 0.999),metrics=['accuracy'])

		reducelr = reduce_lr
		earlystopper = Early_Stopping 
		file_path = self.output_directory+'best_model.mlp'
		model_checkpoint = keras.callbacks.ModelCheckpoint(filepath=file_path, monitor='loss',save_best_only=True)

		self.callbacks = [earlystopper, reducelr, model_checkpoint]

		return model

	def fit(self, x_train, y_train, epochs, callbacks, batch_size, validation_data):
		if not tf.test.is_gpu_available:
			print('error')
			exit()

		mini_batch_size = int(min(x_train.shape[0]/10, batch_size))
		hist = self.model.fit(x_train, y_train, epochs = epochs, callbacks=self.callbacks, batch_size = batch_size, validation_data = validation_data)

		keras.backend.clear_session()
		return hist

	def predict(self, x_test):
		model_path = self.output_directory + 'best_model.mlp'
		model = keras.models.load_model(model_path)
		ypred = model.predict(x_test)
		return ypred