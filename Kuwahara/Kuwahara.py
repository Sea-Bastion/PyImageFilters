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

"""
I'm just going to hard code the values for now but eventually I want to make them args
"""

N = 8
windowRadius = 25
MaskPath  = 'resources/Mask.json'
ImgInPath = 'resources/monkey.jpg'

# ----------------------- Import Masks -------------------

with open(MaskPath, 'r') as MaskFile:
    Masks = json.load(MaskFile)
    
Masks = [np.array(i) for i in Masks]


# ----------------------- Import Input Image ----------------------


with Image.open(ImgInPath) as rawImage:
    Img = np.array( rawImage ).transpose(1,0,2).astype('float32')

Img /= 255
dims = Img.shape


# ---------------------- directional StDev -------------------------

Means = np.zeros( (N, dims[0], dims[1], 3) )
StDev = np.zeros( (N, dims[0], dims[1]) )

          
for n in range(N):
    FullMask = np.stack( [np.zeros((51,51)), Masks[n], np.zeros((51,51))] ,2)
    
    Mean = ndimage.correlate(Img, FullMask, mode='wrap')
    SqMean = ndimage.correlate(Img*Img, FullMask, mode='wrap')
    
    Means[n, :, :] = Mean
    StDev[n, :, :] = np.sqrt( np.mean(SqMean - (Mean*Mean), 2) ) #mean go to euc dist
    #because this is pre sqrt you may just be able to sum before sqrt to get dist
    
    
    print('finished n: {:n}'.format(n))
    

# ---------------------- Final Image Gen-------------------------------
#%% Final Image Gen

q=8
alpha = 1 / (1 + (StDev**q) )
alphaSum = np.sum(alpha, 0)

outputImg = np.sum(alpha * Means, 0)/alphaSum
