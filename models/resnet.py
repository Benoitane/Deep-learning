import tensorflow.keras as keras
import tensorflow as tf
import numpy as np
import time

import matplotlib
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, LearningRateScheduler, ModelCheckpoint

class Classifier_RESNET:

    def __init__(self, output_directory, input_shape, nb_classes, Early_Stopping, reduce_lr, n_feature_maps=64,kernel_size=5  ,verbose=False, build=True):
        self.output_directory = output_directory
        if build == True:
            self.model = self.build_model(input_shape, nb_classes,Early_Stopping,reduce_lr,n_feature_maps,kernel_size)
            if (verbose == True):
                self.model.summary()
            self.verbose = verbose
            self.model.save_weights(self.output_directory + 'model_init.resnet')
        return

    def build_model(self, input_shape, nb_classes,Early_Stopping,reduce_lr,n_feature_maps=64,kernel_size=5):

        loss = 'categorical_crossentropy'
        n_units_dense = nb_classes

        if isinstance(n_feature_maps,int):
            n_feature_maps = 3 * (n_feature_maps,)
        if isinstance(kernel_size,int):
            kernel_size = 4 * (kernel_size,)

        input_layer = keras.layers.Input(input_shape)

        # BLOCK 1

        conv_x = keras.layers.Conv1D(filters=n_feature_maps[0], kernel_size=kernel_size[0], padding='same')(input_layer)
        conv_x = keras.layers.BatchNormalization()(conv_x)
        conv_x = keras.layers.Activation('relu')(conv_x)

        conv_y = keras.layers.Conv1D(filters=n_feature_maps[0], kernel_size=kernel_size[1], padding='same')(conv_x)
        conv_y = keras.layers.BatchNormalization()(conv_y)
        conv_y = keras.layers.Activation('relu')(conv_y)

        conv_z = keras.layers.Conv1D(filters=n_feature_maps[0], kernel_size=kernel_size[2], padding='same')(conv_y)
        conv_z = keras.layers.BatchNormalization()(conv_z)

        # expand channels for the sum
        shortcut_y = keras.layers.Conv1D(filters=n_feature_maps[0], kernel_size=kernel_size[3], padding='same')(input_layer)
        shortcut_y = keras.layers.BatchNormalization()(shortcut_y)

        output_block_1 = keras.layers.add([shortcut_y, conv_z])
        output_block_1 = keras.layers.Activation('relu')(output_block_1)

        # BLOCK 2

        conv_x = keras.layers.Conv1D(filters=n_feature_maps[1] , kernel_size=kernel_size[0], padding='same')(output_block_1)
        conv_x = keras.layers.BatchNormalization()(conv_x)
        conv_x = keras.layers.Activation('relu')(conv_x)

        conv_y = keras.layers.Conv1D(filters=n_feature_maps[1] , kernel_size=kernel_size[1], padding='same')(conv_x)
        conv_y = keras.layers.BatchNormalization()(conv_y)
        conv_y = keras.layers.Activation('relu')(conv_y)

        conv_z = keras.layers.Conv1D(filters=n_feature_maps[1] , kernel_size=kernel_size[2], padding='same')(conv_y)
        conv_z = keras.layers.BatchNormalization()(conv_z)

        # expand channels for the sum
        shortcut_y = keras.layers.Conv1D(filters=n_feature_maps[1] , kernel_size=kernel_size[3], padding='same')(output_block_1)
        shortcut_y = keras.layers.BatchNormalization()(shortcut_y)

        output_block_2 = keras.layers.add([shortcut_y, conv_z])
        output_block_2 = keras.layers.Activation('relu')(output_block_2)

        # BLOCK 3

        conv_x = keras.layers.Conv1D(filters=n_feature_maps[2] , kernel_size=kernel_size[0], padding='same')(output_block_2)
        conv_x = keras.layers.BatchNormalization()(conv_x)
        conv_x = keras.layers.Activation('relu')(conv_x)

        conv_y = keras.layers.Conv1D(filters=n_feature_maps[2] , kernel_size=kernel_size[1], padding='same')(conv_x)
        conv_y = keras.layers.BatchNormalization()(conv_y)
        conv_y = keras.layers.Activation('relu')(conv_y)

        conv_z = keras.layers.Conv1D(filters=n_feature_maps[2] , kernel_size=kernel_size[2], padding='same')(conv_y)
        conv_z = keras.layers.BatchNormalization()(conv_z)

        # no need to expand channels because they are equal
        shortcut_y = keras.layers.BatchNormalization()(output_block_2)
        output_block_3 = keras.layers.add([shortcut_y, conv_z])
        output_block_3 = keras.layers.Activation('relu')(output_block_3)

        # FINAL
        gap_layer = keras.layers.GlobalAveragePooling1D()(output_block_3)
        output_layer = keras.layers.Dense(n_units_dense, activation='softmax')(gap_layer)
        model = keras.models.Model(inputs=input_layer, outputs=output_layer)
        model.compile(loss=loss, optimizer=keras.optimizers.Adam(lr = 0.001, beta_1 = 0.9, beta_2 = 0.999),metrics=['accuracy'])
        earlystopper = Early_Stopping 
        reducelr = reduce_lr
		
        file_path = self.output_directory + 'best_model.resnet'
        model_checkpoint = keras.callbacks.ModelCheckpoint(filepath=file_path, monitor='loss', save_best_only=True)
		
        self.callbacks = [earlystopper, reducelr, model_checkpoint]

        return model


    def fit(self, x_train, y_train, epochs, callbacks, batch_size, validation_data):
        if not tf.test.is_gpu_available:
            print('error')
            exit()

        batch_size = int(min(x_train.shape[0] / 10, batch_size))
        hist = self.model.fit(x_train, y_train, epochs = epochs, callbacks=self.callbacks, batch_size = batch_size, validation_data = validation_data)
        keras.backend.clear_session()
        return hist

    def predict(self, x_test):
        model_path = self.output_directory + 'best_model.resnet'
        model = keras.models.load_model(model_path)
        ypred = model.predict(x_test)
        return ypred