#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 00:35:28 2023

https://stackoverflow.com/questions/384759/how-do-i-convert-a-pil-image-into-a-numpy-array

I = numpy.asarray(PIL.Image.open('test.jpg'))

im = PIL.Image.fromarray(numpy.uint8(I))
im.save("out.png")

@author: sebas
"""

from PIL import Image
import argparse
import numpy as np
from scipy.spatial import KDTree

BayerSizes = {"2":0, "4":1, "8":2}

#bayer matices add the noise to the image that cases dithering
Bayer2 = 255/4  * np.asarray([[0, 2], [3, 1]]) - 127.5
Bayer4 = 255/16 * np.asarray([[ 0,  8,  2, 10],
                              [12,  4, 14,  6],
                              [ 3, 11,  1,  9],
                              [15,  7, 13,  5]]) - 127.5
Bayer8 = 255/64 * np.asarray([[ 0, 32,  8, 40,  2, 34, 10, 42],
                              [48, 16, 56, 24, 50, 18, 58, 26],
                              [12, 44,  4, 36, 14, 46,  6, 38],
                              [60, 28, 52, 20, 62, 30, 54, 22],
                              [ 3, 35, 11, 43,  1, 33,  9, 41],
                              [51, 19, 59, 27, 49, 17, 57, 25],
                              [15, 47,  7, 39, 13, 45,  5, 37],
                              [63, 31, 55, 23, 61, 29, 53, 21]]) - 127.5
Bayers = [Bayer2, Bayer4, Bayer8]
BayerLength = [2, 4, 8]



def Dither(image, bayerSize, noiseScale, colorPalette):
    #yeah try changing to big for loop. It may work better. also way better on memory.
    #maybe try both methods and time them
    
    dims = image.shape
    
    # padd bayer matrix to image size then scale
    sizeResiduals = ( (0, dims[0]-BayerLength[bayerSize]), (0, dims[1]-BayerLength[bayerSize]))
    noise = np.pad(Bayers[bayerSize], sizeResiduals, 'wrap')
    noise *= noiseScale
    
    # apply noise
    noisyImage = np.array([image[:,:,i] + noise for i in range(dims[2]) ]).transpose(1,2,0)
    
    # set up a tree to qurry nearest color
    LooupTree = KDTree(colorPalette)
    
    #quantize image colors
    _, quantImage = LooupTree.query( noisyImage )
    
    #turn colormapped image into RGB image
    finalImage = np.array([colorPalette[i] for i in quantImage])
    
    return finalImage
    



if __name__ == '__main__':
    Colors = np.array([[255, 255, 255],  
                       [  0,   0,   0],
                       [180, 180, 180],
                       [ 64,  64,  64],
                       [168,  69, 111]])
    
    #memory leak if image not closed
    with Image.open("resources/monkey.jpg") as rawImage:
        Img = np.asarray( rawImage )
    
    output = Dither(Img, BayerSizes['8'], 1, Colors)
    
    Image.fromarray( np.uint8(output) ).save("output.png")