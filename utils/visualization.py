# -*- coding: utf-8 -*-
"""visualization.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WudZdSkOv8cQkJoyx3-VBguT-iKdErhf
"""

import keract
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import pandas as pd

#bloc display
Classes = { 0:'Normal beat',  1 : 'Supraventricular ectopic beats',  2: 'Ventricular ectopic beats',  3:'Fusion Beats',  4:'Unknown Beats'}

def plot_into_category(categorie,n):
  temp = mitbih_train[mitbih_train[187] == categorie].sample(n = n, random_state = 27)
  for i in range(n):
    plt.plot(temp.iloc[i,:186], color="red", alpha=.5)
    plt.title('Représentation enregistrements de la catégorie '+str(Classes[categorie]))
  plt.show()

def plot_hist(class_number,size,min_):
    img = mitbih_train.loc[mitbih_train[187] == class_number].values
    img = img[:,min_:size]
    img_flatten = img.flatten()
    final1 = np.arange(min_,size)
    for i in range(img.shape[0]-1):
      tempo1 = np.arange(min_,size)
      final1 = np.concatenate((final1, tempo1), axis=None)
    plt.hist2d(final1, img_flatten, bins=(80,80), cmap=plt.cm.jet)
    plt.show()

def display_conv_activations(model,sig):
    if len(sig.shape)==2:
        sig = sig.reshape(1,sig.shape[0],sig.shape[1])
    #get activations
    activations = keract.get_activations(model, sig)
    #get convolutional layers keys
    conv_keys = [key for key in activations.keys() if 'conv' in key]
    #prepare for plotting
    t = np.linspace(0, len(sig[0]),len(sig[0]))
    signal = sig[0].reshape(-1,)
    points = np.array([t, signal]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    #create fig and axs
    fig = plt.figure(figsize=(18,5))

    if len(conv_keys)>10:
        print('Warning: only the 10 last layers will be displayed')

    for i in range(1,min([11,len(conv_keys)])):
        ax = fig.add_subplot(2,5,i)
        key = conv_keys[-i]
        act = np.mean(activations[key][0],axis=1)
        # Create a continuous norm to map from data points to colors
        norm = plt.Normalize(act.min(), act.max())
        lc = LineCollection(segments, cmap='bwr', norm=norm)
        # Set the values used for colormapping
        lc.set_array(act)
        lc.set_linewidth(2)
        line = ax.add_collection(lc)
        fig.colorbar(line, ax=ax)
        ax.set_xlim(t.min(), t.max())
        ax.set_title(key)
    plt.tight_layout()


def display_conv_activations_transplant(model,sig,cols):
    """
    for transplant with 10 channels
    """

    #get activations
    sig = sig.reshape(1,sig.shape[0],sig.shape[1])
    activations = keract.get_activations(model, sig)
    conv_keys = [key for key in activations.keys() if 'conv' in key]
    #prepare for plotting
    t = np.linspace(0, len(sig[0]),len(sig[0]))
    #signal = sig[0].reshape(-1,)
    #create fig and axs
    fig = plt.figure(figsize=(14,5))
    key = conv_keys[-1] #last convolutional layer
    act = np.mean(activations[key][0],axis=1)
    # Create a continuous norm to map from data points to colors
    norm = plt.Normalize(act.min(), act.max())
    for i in range(1,11):

        signal = sig[0][:,i-1]
        points = np.array([t, signal]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        ax = fig.add_subplot(2,5,i)
        lc = LineCollection(segments, cmap='bwr', norm=norm)
        # Set the values used for colormapping
        lc.set_array(act)
        lc.set_linewidth(2)
        line = ax.add_collection(lc)
        fig.colorbar(line, ax=ax)
        ax.set_xlim(t.min(), t.max())
        ax.set_ylim(signal.min(),signal.max())
        ax.set_title(cols[i-1],fontsize=13)

    plt.tight_layout()

	
def plot_bar(labels):
  labels_train = pd.DataFrame(labels, columns=['labels']) 
  labels_train = labels_train['labels'].value_counts()
  ax = labels_train.plot(kind='bar',title="Nombre d'observations par catégorie")
  ax.set_xlabel("Catégorie")
  ax.set_ylabel("Nombre")
  plt.show()

  
def visualize_mitbih(X,y):
    fig = plt.figure(figsize=(14,5))
    for c in set(y):
        spe_ecg = X[y==c][0]
        plt.plot(spe_ecg,label='exemple de signal pour la classe '+str(c))

    plt.legend()
    plt.show()