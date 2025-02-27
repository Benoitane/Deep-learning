# -*- coding: utf-8 -*-
"""preprocessing_data.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WudZdSkOv8cQkJoyx3-VBguT-iKdErhf
"""

import neural_tangents as nt
from neural_tangents import stax
import numpy as np
import jax
from jax import random
from neural_tangents import stax
from scipy.signal import gaussian, decimate
from scipy.sparse import csr_matrix
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from sklearn.model_selection import StratifiedShuffleSplit
from keras.preprocessing.sequence import pad_sequences
from scipy.sparse import vstack

def split_dataset(data, labels, Deep, modele, validation=True , val_prop = 0.2):
    """
    splits dataset into (train,test) or (train,validation,test)
    arguments
    ---------
    data: features (X), array-like
    labels : classes (y), array-like
    validation: bool, if True split in (train,validation,test) with proportion (0.6,0.2,0.2)
                      if False split in (train,test) with proportion (0.8,0.2)
    returns
    -------
    xtrain,xtest,(xval): splitted versions of data
    ytrain,ytest,(yval): splitted versions of labels as one hot encoding if more than 2 classes
    y_test_true,(y_val_true): not one hot encoded versions of labels
    """
    labels = np.array(labels,dtype=int)
    data = np.array(data)

    if validation:
        val_proportion = val_prop*2
    else:
        val_proportion = val_prop
    
    sss = StratifiedShuffleSplit(n_splits=1, test_size=val_proportion, random_state=0)
    for train_index,test_index  in sss.split(data,labels):
        xtrain,xtest = data[train_index],data[test_index]
        ytrain,ytest = labels[train_index],labels[test_index]
    
     
    if validation:
        sss = StratifiedShuffleSplit(n_splits=1, test_size=0.5, random_state=0)
        for val_index,test_index in sss.split(xtest,ytest):
            xval,xtest = xtest[val_index],xtest[test_index]
            yval,ytest = ytest[val_index],ytest[test_index]
    y_val_true = yval
    y_test_true = ytest
    if Deep == True:
        ytrain = to_categorical(ytrain, 5)
        y_val_true = yval
        yval = to_categorical(yval, 5)
        y_test_true = ytest
        ytest = to_categorical(ytest, 5)
        if modele == 'CNN':
            xtrain = xtrain.reshape(xtrain.shape[0],xtrain.shape[1],1)
            xval = xval.reshape(xval.shape[0],xval.shape[1],1)
            xtest = xtest.reshape(xtest.shape[0],xtest.shape[1],1)
        if modele == 'RNN':
            xtrain = pad_sequences(xtrain, maxlen=200)
            xval = pad_sequences(xval, maxlen=200)
            xtest = pad_sequences(xtest, maxlen=200)
        if modele == 'NTK':
            nb_train = 10000
            nb_test = 10000
            xtrain = jax.numpy.array(xtrain[:nb_train,:])
            xval = jax.numpy.array(xval[:nb_test,:])
            xtest = jax.numpy.array(xtest[:nb_test,:])
            ytrain = jax.numpy.array(ytrain[:nb_train,:].astype(int))
            yval = jax.numpy.array(yval[:nb_test,:].astype(int))
            ytest = jax.numpy.array(ytest[:nb_test,:].astype(int))
            y_val_true = y_val_true[:nb_test]

    if validation:
        return xtrain,ytrain,xval,yval,y_val_true,xtest,ytest,y_test_true
    else:
        return xtrain,ytrain,xtest,ytest,y_test_true

  
def read_dataset(path_1,path_2):
    data1 = pd.read_csv(path_1,header=None)
    data2 = pd.read_csv(path_2,header=None)
    data = pd.concat([data1, data2], ignore_index=True)

    labels = data[187].astype(int)
    data.drop(187,axis=1,inplace=True)
    data = data.values
    labels = labels.values
	
    return data,labels