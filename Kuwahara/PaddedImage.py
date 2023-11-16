# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 13:45:49 2023

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
        
    
    def get(self, x, y):
        
        if ( 0 <= x <= self.Dim[0] ) and ( 0 <= y <= self.Dim[1] ):
            return self.Image[x,y,:]
        
        else:
            
            match self.Mode:
                case 0: # constant
                
                    return np.arrya(3*[self.Const])
                
                case 1: # clamp
                    
                    new_x = np.clip( x, 0, self.Dim[0] )
                    new_y = np.clip( y, 0, self.Dim[1] )
                    
                    return self.Image[new_x, new_y, :]
                
                case 2: # mirror
                
                    new_x = x % self.Dim[0]
                    new_y = y % self.Dim[1]
                    
                    if ( x//self.Dim[0] ) % 2:
                        new_x = self.Dim[0] - new_x
                    
                    if ( x//self.Dim[1] ) % 2:
                        new_y = self.Dim[1] - new_y
                    
                    return self.Image[new_x, new_y, :]
                
                case 3: # wrap
                
                    new_x = x % self.Dim[0]
                    new_y = y % self.Dim[1]
                    
                    return self.Image[new_x, new_y, :]
                
                case _:
                    return 0