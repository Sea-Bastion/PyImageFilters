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

"""
I'm just going to hard code the values for now but eventually I want to make them args
"""

N = 8
MaskPath  = 'resources/Mask.json'
ImgInPath = '../Images/Katelyn&Me2.jpg'

# ----------------------- Import Masks -------------------
#%% Import Masks

with open(MaskPath, 'r') as MaskFile:
    Masks = json.load(MaskFile)
    
Masks = [np.array(i) for i in Masks]
WindowSize = Masks[0].shape[0]
del MaskFile


# ----------------------- Import Input Image ----------------------
#%% Import Img

with Image.open(ImgInPath) as rawImage:
    Img = np.array( rawImage ).transpose(1,0,2).astype('float32')

#Img /= 255
dims = Img.shape
del rawImage

# ---------------------- directional StDev & Mean -------------------------
#%% Mean and StDev Gen



def ProcessDirection(n, image):
    global Means, StDev
    
    FullMask = np.stack( [np.zeros(Masks[n].shape), Masks[n], np.zeros(Masks[n].shape)] ,2)
    
    Mean = ndimage.correlate(image, FullMask, mode='mirror')
    SqMean = ndimage.correlate(image*image, FullMask, mode='mirror')
    
    Varriance = np.sum( SqMean - (Mean*Mean), 2 ) #Euclidian Distance, trust me
    Varriance[Varriance < 0] = 0
    
    
    print('finished n: {:n}'.format(n))
    return Mean, np.sqrt(Varriance)
    
with Pool(8) as p:
    f = partial( ProcessDirection, image=Img )
    PoolOut = p.map(f, np.arange(N))
    
Means = np.array([ x[0] for x in PoolOut ])
StDev = np.array([ x[1] for x in PoolOut ])
    
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
