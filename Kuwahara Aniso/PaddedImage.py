# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 13:45:49 2023

save me, even if you don't need me now, you may later

@author: sebas
"""
import numpy as np

class PaddedImage:
    
    Modes = {'constant':0, 'clamp':1, 'mirror':2, 'wrap':3}
    
    def __init__(self, image, mode, constant=0):
        
        self.Image = image
        self.Mode = self.Modes[mode]
        self.Const = constant
        self.Dim = image.shape
        self.shape = self.Dim
        
    def getRange(self, xLim, yLim):
        
        xRange = xLim[1] - xLim[0] + 1
        yRange = yLim[1] - yLim[0] + 1
        
        ReturnVal = np.zeros( (xRange, yRange, 3) )
        
        for x in range(xRange):
            for y in range(yRange):
                
                ReturnVal[x,y,:] = self.get(x + xLim[0], y + yLim[0])
                
                
        return ReturnVal
        
    
    def get(self, x, y):
        
        if ( 0 <= x <= (self.Dim[0] - 1) ) and ( 0 <= y <= (self.Dim[1] - 1) ):
            
            new_x = x
            new_y = y
        
        else:
            
            match self.Mode:
                case 0: # constant
                
                    if len(self.shape) == 3:
                        return self.shape[2]*[self.Const]
                    else:
                        return self.Const
                
                case 1: # clamp
                    
                    new_x = np.clip( x, 0, self.Dim[0] -1)
                    new_y = np.clip( y, 0, self.Dim[1] -1)
                    
                
                case 2: # mirror
                
                    new_x = x % self.Dim[0]
                    new_y = y % self.Dim[1]
                    
                    if ( x//self.Dim[0] ) % 2 and new_x != 0:
                        new_x = self.Dim[0] - new_x
                    
                    if ( y//self.Dim[1] ) % 2 and new_y != 0:
                        new_y = self.Dim[1] - new_y
                    
                
                case 3: # wrap
                
                    new_x = x % self.Dim[0]
                    new_y = y % self.Dim[1]
                    
                
                case _:
                    return 0
                
        return self.Image[new_x, new_y]


    def arrget(self, r):
        assert len(r) == 2
        
        return self.get(r[0],r[1])


    def __getitem__(self, index):
        x,y = index
        return self.get(x,y)
            