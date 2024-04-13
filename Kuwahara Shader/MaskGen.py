# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 11:45:50 2023

https://diglib.eg.org/bitstream/handle/10.2312/LocalChapterEvents.TPCG.TPCG10.025-030/025-030.pdf?sequence=1

instead of using there polynomial. I'm using just a filled in sector.
the reason they use a polynomial is to live computer the mask.
live computing is faster for some GPU stuff, but for us baking the mask will be better.


@author: sebas
"""

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy import signal
import argparse
import json


# angle subtraction is weird trust me you can't make it better :(
def _AngleDistance(angleA, angleB):
    return abs( ( angleA - angleB + np.pi ) % ( 2*np.pi ) - np.pi )
    

def GenerateMask(N, WindowRadius, I, BlurCoeff=1, MaskCoeff=1):
    
    WindowLen = 2*WindowRadius + 1
    dims = (WindowLen, WindowLen)
    MaskBlurSigma = BlurCoeff * (WindowRadius+1)/7.5
    GausMaskSigma = MaskCoeff * (WindowRadius+1)/2.5

    WinBasis = np.array([
        np.pi/N >= _AngleDistance(np.arctan2(-x,y), I*2*np.pi/N)
        for x in range(-WindowRadius, WindowRadius+1)
        for y in range(-WindowRadius, WindowRadius+1)
        ], dtype=float).reshape(dims)
    
    WinBlur = ndimage.gaussian_filter(WinBasis, MaskBlurSigma)      # blur the mask to give soft edges
    Gaussian = signal.windows.gaussian(WindowLen, GausMaskSigma)    # generate 1D gaussian
    WinMask = WinBlur * np.outer(Gaussian, Gaussian)                # mask window with 2D gaussian to fade out
    WinNorm = WinMask / np.sum(WinMask)                             # normalize to 1
    
    return WinNorm


if __name__=='__main__':
    
    parser = argparse.ArgumentParser(prog="Kuwahara Mask Generator",
                                     description="genrates masks for Kuwahara filters")
    
    parser.add_argument('-N', type=int, action='store', default=8)      # slices
    parser.add_argument('-W', type=int, action='store', default=25)     # window size
    parser.add_argument('-B', type=int, action='store', default=1)      # blur coeff
    parser.add_argument('-M', type=int, action='store', default=1)      # mask coeff
    parser.add_argument('-Img', action='store_true')                    # output image or json
    parser.add_argument('--outfile', '-O', default='out.jpg')           # blur coeff
    
    args = parser.parse_args()
    
    output = [GenerateMask(args.N, args.W, i, args.B, args.M) for i in range(args.N)]
    
    if args.Img:
        for i in range(args.N):
            ScaledOut = output[i] * 255 / np.max(output[i])
            Image.fromarray(np.uint8( ScaledOut )).save(args.outfile + str(i) + '.jpg')
            
    else:
        jsonStr = json.dumps([i.tolist() for i in output], indent=4)
        with open(args.outfile, 'w') as outfile:
            outfile.write(jsonStr)