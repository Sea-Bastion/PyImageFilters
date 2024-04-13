#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 23:21:57 2023

@author: sebas
"""

import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from scipy import ndimage
import pickle


BlurSigma = 15
ImagePath = 'resources/monkey.jpg'


#%% Load in Image

with Image.open(ImagePath) as RawImage:
    Img = np.asarray(RawImage).astype('float32')
   
Img /= 255
dims = Img.shape


#%% Calculate Tensor

Sobelx = ndimage.sobel(Img, 0)
Sobely = ndimage.sobel(Img, 1)


StructTens = np.array([[Sobelx*Sobelx, Sobelx*Sobely],
                       [Sobelx*Sobely, Sobely*Sobely]]).transpose(2,3,4,0,1)

StructTens = ndimage.gaussian_filter(StructTens, BlurSigma, axes=(0,1))

#%% Calculate params for filter

eigval, eigvec = np.linalg.eig(StructTens)

#not always true that lambda1 > lambda2 but abs fixes this
lambda1 = eigval[:,:,:,0]
lambda2 = eigval[:,:,:,1]

A = np.where( (lambda1 + lambda2) > 0, ( lambda1 - lambda2 ) / ( lambda1 + lambda2 ) , 0.)
A = np.abs(A)

# sort eigan vectors
MinorArgs = np.argmax(eigval, axis=3, keepdims=True)
MinorEigVec = np.squeeze( np.take_along_axis(eigvec, MinorArgs[:,:,:,:,np.newaxis], 3) ) # may be wrong triple check the eigvec index to be sorted

LocalOri = np.arctan2(MinorEigVec[:,:,:,1], MinorEigVec[:,:,:,0])


# show local ori for diagnostics

# X = np.arange(0, dims[0], 10)
# Y = np.arange(0, dims[1], 10)
# X, Y = np.meshgrid(X, Y)

# LocalOri = LocalOri.transpose(1,0,2)
# plt.imshow(Img)
# plt.quiver(Y, X, np.cos(LocalOri[0::10,0::10,0]), np.sin(LocalOri[0::10,0::10,0]), scale_units='xy', scale=0.1)
# plt.show()


#find scaling factors for filter
alpha = 1       # tuning factor
r = 1          # radius of filter
IsoFactor = (alpha + A)/alpha
a = r * IsoFactor
b = r / IsoFactor


ExportData = {
    'a': a,
    'b': b,
    'LocalOri': LocalOri
}



with open(ImagePath + '.eigen.pickle', 'wb') as outFile:
    pickle.dump(ExportData, outFile)
    