#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 22:48:32 2023

@author: sebas
"""

import numpy as np
from PIL import Image
from scipy import ndimage
import argparse
import json

"""
I'm just going to hard code the values for now but eventually I want to make them args
"""

N = 8
MaskPath  = 'resources/Mask.json'
ImgInPath = 'resources/monkey.jpg'

# ----------------------- Import Masks -------------------

with open(MaskPath, 'r') as MaskFile:
    Masks = json.load(MaskFile)
    
Masks = [np.array(i) for i in Masks]


# ----------------------- Import Input Image ----------------------


with Image.open(ImgInPath) as rawImage:
    Img = np.asarray( rawImage ).transpose(1,0,2)

dims = Img.shape



# ---------------------- directional StDev -------------------------

StDev = np.zeros( (N, dims[0], dims[1]) )

for n in range(N):
    for x in range(dims[0]):
        for y in range(dims[1]):
            
            

        
        