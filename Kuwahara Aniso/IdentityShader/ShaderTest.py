#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 01:15:19 2024

@author: sebas
"""

from cupyx.scipy import ndimage
from cupy import RawKernel
from PIL import Image
import cupy as cp
import numpy as np
from matplotlib import pyplot as plt
import json
import pickle


MaskPath  = '../resources/Mask.json'
ShaderPath = "FilterShader.cu"
ImagePath = "../resources/monkey.jpg"



# -------------------------------Import Image, ShaderCode, and Masks----------------
#%% Import Main
with open(ShaderPath, 'r') as Infile:
    ShaderCode = Infile.read()
    
with Image.open(ImagePath, 'r') as Infile:
    Img = cp.array(Infile).astype(cp.uint8)
dims = np.array(Img.shape[:2])
Img = cp.concatenate( ( Img, cp.ones( tuple(dims) + (1, ), dtype=cp.uint8 ) ), axis=2)
Original = Img.get()

with open(MaskPath, 'r') as MaskFile:
    Masks = cp.array(json.load(MaskFile)[0])
    

# ------------------------- Import Input Anisotropy Values-----------------
#%% Import Aniso


with open(ImagePath + ".eigen.pickle", 'rb') as IsoFile:
    RawAnisoData = pickle.load(IsoFile)
    
del IsoFile
LocalOrientation = cp.array(RawAnisoData['LocalOri'])
LocalOrientation = cp.mean(LocalOrientation, axis=2).T
Scalers = cp.array([ RawAnisoData['a'], RawAnisoData['b'] ]).transpose(2,1,3,0)
Scalers = cp.mean(Scalers, axis=2)
    
#%% Load Image as Texture

ChannelFormat = cp.cuda.texture.ChannelFormatDescriptor(8, 8, 8, 8, cp.cuda.runtime.cudaChannelFormatKindUnsigned)
CudaArray = cp.cuda.texture.CUDAarray(ChannelFormat, dims[1], dims[0])
CudaArray.copy_from(Img.reshape(dims[0], dims[1]*4))



ResourceDesc = cp.cuda.texture.ResourceDescriptor(cp.cuda.runtime.cudaResourceTypeArray, cuArr=CudaArray)

TextureDesc = cp.cuda.texture.TextureDescriptor(addressModes=3*[cp.cuda.runtime.cudaAddressModeMirror], filterMode=cp.cuda.runtime.cudaFilterModePoint, readMode=cp.cuda.runtime.cudaReadModeElementType)
ImageTexture = cp.cuda.texture.TextureObject(ResourceDesc, TextureDesc)


#%% Run Shader

ShaderFunction = RawKernel( ShaderCode, "Kuwahara")

FlatOutput = cp.zeros(Img.shape, dtype=cp.uint8).flatten()
FlatMask = Masks[0].flatten().astype(cp.float32)

threadsPerBlock = ( dims[0], )
BlocksPerGrid = ( dims[1], )
Args = (ImageTexture, cp.array(dims, dtype=cp.int32), FlatMask, 51, FlatOutput)

ShaderFunction( threadsPerBlock, BlocksPerGrid, Args )



Output = FlatOutput.reshape( Img.shape ).get()

# print(FlatOutput - FlatImage)
# print( Output )
# print( 100* np.sum( Output != Original ) / Img.size )

plt.imshow(Output[:,:,:3]/255)
