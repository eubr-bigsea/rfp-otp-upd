'''
Created on Nov 10, 2017

@author: asalic
'''


class Params():
    """
    Class used to store the command line params for the app
    """
    def __init__(self, args):
        if not args == None: 
            self.regionsURL = args.regionsURL
            self.outDir = args.outDir
            self.otpJar = args.otpJar
            self.osmiumPath = args.osmiumPath
            self.otpMemory = args.otpMemory
            self.extensionLimits = float(args.extensionLimits)
        else:
            self.regionsURL = None
            self.outDir = None
            self.otpJar = None
            self.osmiumPath = None
            self.otpMemory = None
            self.extensionLimits = 0.0