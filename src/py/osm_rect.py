'''
Created on Nov 2, 2017

@author: asalic
'''

import json

class OSMRect:
    """
    Class used to create a rectangular BBox around a city
    """
    def __init__(self, latMin: float, latMax: float, lngMin: float, lngMax: float):
        self.latMin: float = latMin
        self.latMax: float = latMax
        self.lngMin: float = lngMin
        self.lngMax: float = lngMax
        
    def extend(self, extensionLimits: float):
        self.latMin = float(self.latMin) - extensionLimits
        self.latMax = float(self.latMax) + extensionLimits
        self.lngMin = float(self.lngMin) - extensionLimits
        self.lngMax = float(self.lngMax) + extensionLimits
        
    def toString(self):
        return json.dumps(self.__dict__)