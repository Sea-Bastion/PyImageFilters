# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 13:45:49 2023

@author: sebas
"""

class PaddedImage:
    
    Modes = {'constant':0, 'clamp':1, 'mirror':2, 'wrap':3}
    
    def __init__(self, image, mode, constant=0):
        
        self.Image = image
        self.Mode = Modes[mode]
        self.Const = constant
        self.Dim = image.shape
        
    
    def get(self, x, y):
        
        if ( 0 <= x <= self.Dim[0] ) and ( 0 <= y <= self.Dim[1] ):
            return self.Image[x,y,:]
        
        else:
            
            match self.Mode:
                case 0:
                    return self.Const
                
                case 1:
                    
                    return 0
                case 2:
                    return 0
                case 3:
                    new_x = x % self.Dim[0]
                    new_y = y % self.Dim[1]
                    
                    return self.Image[x,y,:]
                
                case default:
                    return 0