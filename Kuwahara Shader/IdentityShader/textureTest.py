#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 13:01:17 2024

@author: sebas
"""

import cupy as cp


source=r'''
extern "C"{
__global__ void copyKernel(float* output,
                           cudaTextureObject_t texObj,
                           int width, int height)
{
    unsigned int x = blockIdx.x * blockDim.x + threadIdx.x;
    unsigned int y = blockIdx.y * blockDim.y + threadIdx.y;

    // Read from texture and write to global memory
    float u = x;
    float v = y;
    unsigned int Index = 4*(y * width + x);
    if (x < width && y < height)
        output[Index + 0] = tex2D<float4>(texObj, u, v).x;
        output[Index + 1] = tex2D<float4>(texObj, u, v).y;
        output[Index + 2] = tex2D<float4>(texObj, u, v).z;
        output[Index + 3] = tex2D<float4>(texObj, u, v).w;
        
}
}
'''
width = 8
height = 16
channels = 4

# set up a texture object
ch = cp.cuda.texture.ChannelFormatDescriptor(32, 32, 32, 32, cp.cuda.runtime.cudaChannelFormatKindFloat)
arr2 = cp.cuda.texture.CUDAarray(ch, width, height)
res = cp.cuda.texture.ResourceDescriptor(cp.cuda.runtime.cudaResourceTypeArray, cuArr=arr2)
tex = cp.cuda.texture.TextureDescriptor((cp.cuda.runtime.cudaAddressModeClamp, cp.cuda.runtime.cudaAddressModeClamp),
                                        cp.cuda.runtime.cudaFilterModePoint,
                                        cp.cuda.runtime.cudaReadModeElementType)
texobj = cp.cuda.texture.TextureObject(res, tex)

# allocate input/output arrays
tex_data = cp.arange(width*height*channels, dtype=cp.float32).reshape(height, width, channels)
real_output = cp.zeros_like(tex_data)
expected_output = cp.zeros_like(tex_data)
arr2.copy_from(tex_data.reshape(height, width * channels))
arr2.copy_to(expected_output.reshape(height, width * channels))

# get the kernel, which copies from texture memory
ker = cp.RawKernel(source, 'copyKernel')

# launch it
block_x = 4
block_y = 4
grid_x = (width + block_x - 1)//block_x 
grid_y = (height + block_y - 1)//block_y
ker((grid_x, grid_y), (block_x, block_y), (real_output, texobj, width, height))


# test outcome
if cp.allclose(real_output, expected_output):
    print("OK!")
else:
    print("NOT OK!")