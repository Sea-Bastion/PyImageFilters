#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 22:48:32 2023

might help to speed up
https://stackoverflow.com/questions/9786102/how-do-i-parallelize-a-simple-python-loop
only uses CPU tho. it's basically impossible to use this on GPU resonably

@author: sebas
"""

import numpy as np
from PIL import Image
from scipy import ndimage
import argparse
import json
from matplotlib import pyplot as plt
from multiprocessing import Pool
from functools import partial
import pickle
from PaddedImage import PaddedImage
from tqdm import tqdm


"""
I'm just going to hard code the values for now but eventually I want to make them args
"""

N = 8
MaskPath  = 'resources/Mask.json'
ImgInPath = 'resources/SmolMonkey.jpg'

# ----------------------- Import Masks -------------------
#%% Import Masks

with open(MaskPath, 'r') as MaskFile:
    Masks = json.load(MaskFile)
    
Masks = [PaddedImage(np.array(i), 'constant', 0) for i in Masks]
WindowSize = Masks[0].shape[0]
WindowRadius = np.floor(WindowSize/2).astype(int)
del MaskFile


# ----------------------- Import Input Image ----------------------
#%% Import Img

with Image.open(ImgInPath) as rawImage:
    Img = np.array( rawImage ).transpose(1,0,2).astype('float32')

#Img /= 255
dims = Img.shape
del rawImage


# ------------------------- Import Input Anisotropy Values-----------------
#%% Import Aniso


with open(ImgInPath + ".eigen.pickle", 'rb') as IsoFile:
    RawAnisoData = pickle.load(IsoFile)
    
del IsoFile
LocalOrientation = RawAnisoData['LocalOri']
LocalOrientation = np.mean(LocalOrientation, axis=2).T
Scalers = np.array([ RawAnisoData['a'], RawAnisoData['b'] ]).transpose(2,1,3,0)
Scalers = np.mean(Scalers, axis=2)



#------------------------------Modified Correlation-------------------------
#%% Modified Correlation

#make grid
SideNum = np.arange(WindowSize)
GridCoords = np.meshgrid(SideNum, SideNum)
CoordList = np.vstack([GridCoords[0].flatten(), GridCoords[1].flatten()])
CoordList -=WindowRadius

def ModCorr(ImageSample, Mask, ScaleFactors, Rotation):
    
    ScaleMtx = np.array([[ 1/ScaleFactors[0], 0 ], [ 0, 1/ScaleFactors[1] ]])
    RotationMtx = np.array([ [ np.cos(-Rotation), np.sin(-Rotation) ], [ -np.sin(-Rotation), np.cos(-Rotation) ] ])
    
    MaskCords = ScaleMtx @ RotationMtx @ CoordList
    MaskCords = np.round(MaskCords).astype(int)
    
    Weights = np.array([Mask.arrget(i) for i in (MaskCords+WindowRadius).T])
    
    Values = np.array([ImageSample.arrget(i) for i in (MaskCords+2*WindowRadius).T])

    
    
    return np.dot(Values.T, Weights)
    

    

    
    


# ---------------------- directional StDev & Mean -------------------------
#%% Mean and StDev Gen

SqImage = PaddedImage(Img*Img, 'mirror')
PImage = PaddedImage(Img, 'mirror')

def ProcessDirection(n):
    
    # FullMask = np.stack( [np.zeros(Masks[n].shape), Masks[n], np.zeros(Masks[n].shape)] ,2)
    
    # Mean = ndimage.correlate(image, FullMask, mode='mirror')

    
    print("Calculateing Mean Values")
    Mean = np.zeros(dims)
    for y in range(dims[1]):
        print("y = {y_print}".format(y_print=y))
        for x in range(dims[0]):
            SubImage = PaddedImage( PImage.getRange([x-2*WindowRadius, x+2*WindowRadius], [y-2*WindowRadius, y+2*WindowRadius]), 'clamp' )
            Mean[x,y] = ModCorr(SubImage, Masks[n], Scalers[x,y], LocalOrientation[x,y])
    
    
    
    # SqMean = ndimage.correlate(image*image, FullMask, mode='mirror')
    
    print("Calculateing Mean Values")
    SqMean = np.zeros(dims)
    for y in range(dims[1]):
        print("y = {y_print}".format(y_print=y))
        for x in range(dims[0]):
            SubImage = PaddedImage( SqImage.getRange([x-2*WindowRadius, x+2*WindowRadius], [y-2*WindowRadius, y+2*WindowRadius]), 'clamp' )
            SqMean[x,y] = ModCorr(SubImage, Masks[n], Scalers[x,y], LocalOrientation[x,y])
    
    Varriance = np.sum( SqMean - (Mean*Mean), 2 ) #Euclidian Distance, trust me
    Varriance[Varriance < 0] = 0
    
    
    print('finished n: {:n}'.format(n))
    return Mean, np.sqrt(Varriance), n
    


Means = np.zeros((8,) + dims)
StDev = np.zeros((8,) + dims)

# Test = ProcessDirection(0)

with Pool(10) as p:
    for o in tqdm(p.imap_unordered(ProcessDirection, range(N)), total=N):
        
        Means[ o[2] ] = o[0]
        StDev[ o[2] ] = o[1]
    
    
    
# ---------------------- Final Image Gen-------------------------------
#%% Final Image Gen

q=8
alpha = 1 / ( 1 + (StDev**q) )
alpha = np.stack(3*[alpha], axis=3)
alphaSum = np.sum(alpha, 0)

outputImg = np.sum(alpha * Means, 0)/alphaSum

# ----------------------- Display Image -----------------------------
#%% Show Img

plt.imshow( outputImg.transpose(1,0,2)/255 )
plt.show()


#%% Save Img

SaveImg = outputImg.transpose(1,0,2)
Image.fromarray(np.uint8(SaveImg)).save("KuwaharaOut.jpg")