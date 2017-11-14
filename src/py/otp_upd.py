#!python3.6
# encoding: utf-8
'''
 -- shortdesc

 is a description

It defines classes_and_methods

@author:     Andy S Alic

@copyright:  2017 Universitat Politecnica de Valencia. All rights reserved.

@license:    Apache 2.0

@contact:    asalic@upv.es
@deffield    updated: Updated
'''

import sys
import os
import json
import zipfile
import shutil
import subprocess
import csv
import logging
from contextlib import closing

from params import Params
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from osm_rect import OSMRect

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


__all__ = []
__version__ = 0.5
__date__ = '2017-10-23'
__updated__ = '2017-10-23'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg
    
"""Generate the OTP graph for a country/city using the OTP build facility"""
def genOTPGraphs(countryCode: str, cityCode: str, params: Params):
    pathCity = os.path.join(params.outDir, countryCode, cityCode)
    subprocess.run(["java",  "-Xmx{0}".format(params.otpMemory), "-jar", params.otpJar, "--build", 
                    pathCity], stdout=subprocess.PIPE)
    
    # Now move the created object
    os.makedirs(os.path.join(pathCity, "graphs"), exist_ok = True)
    os.rename(os.path.join(pathCity, "Graph.obj"), os.path.join(pathCity, "graphs", "Graph.obj"))
    
"""Download the regions from a URL"""
def getRegions(urlRegions):
    response = urlopen(urlRegions, timeout = 20)
    data : str = response.read()
    response.close()
    return json.loads(data)  

"""Determine the max/min lat/lng using the stops.txt from the GTFS file of a
    city; Extend these coordinates by a user defined value"""
def getCityBoundingBox(cityStopsGTFSPath: str, params: Params):
    
    #df = pandas.read_csv(cityStopsGTFSPath, keep_default_na=False, delimiter='[ \t]*,[ \t]*', header=0 ,index_col=0, engine='python', quotechar='"')#, usecols=["stop_lat", "stop_lon"])
    with open(cityStopsGTFSPath, "r") as f:
        reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL, quotechar='"', skipinitialspace=True)
        oR = OSMRect(91.0, -91.0, 181.0, -181.0)
        headers = next(reader)[0:]
        idxLatCol: int = headers.index("stop_lat")
        idxLngCol: int = headers.index("stop_lon")
        for row in reader:
            if float(row[idxLatCol]) < float(oR.latMin):
                oR.latMin = row[idxLatCol]
            if float(row[idxLatCol]) > float(oR.latMax):
                oR.latMax = row[idxLatCol]
            if float(row[idxLngCol]) < float(oR.lngMin):
                oR.lngMin = row[idxLngCol]
            if float(row[idxLngCol]) > float(oR.lngMax):
                oR.lngMax = row[idxLngCol]
        # Extend a bit the limits
        oR.extend(params.extensionLimits)    
        return oR
    return None

"""Using a bounding box create by getCityBoundingBox, extract the OSM data
    for the city from the country's OSM"""
def extractCityOSM(countryCode: str, cityCode: str, params: Params):
    pathCountry = os.path.join(params.outDir, countryCode)
    pathCity = os.path.join(pathCountry, cityCode)
    pathGTFS = os.path.join(pathCity, cityCode + "-latest.zip")
    pathGTFSExtr = os.path.join(pathCity, "gtfs")
    with zipfile.ZipFile(pathGTFS, "r") as zipper:
        zipper.extractall(pathGTFSExtr)
        pathStops = os.path.join(pathGTFSExtr, "stops.txt")
        if os.path.isfile(pathStops):
            oR = getCityBoundingBox(pathStops, params)
            #logger.info("Coords for {0} are: {1}".format(cityCode, oR.toString()))
            subprocess.run([params.osmiumPath, "extract", "--overwrite", "-b", 
                            "{0},{1},{2},{3}".format(oR.lngMin, oR.latMin, oR.lngMax, oR.latMax), 
                            os.path.join(pathCountry, countryCode + "-latest.osm.pbf"),
                            "-o", os.path.join(pathCity, cityCode + "-latest.osm.pbf")], stdout=subprocess.PIPE)
        else:
            raise EnvironmentError("Unable to find the stops.txt file in the GTFS for city of {0}".format(cityCode))
    

"""Download the GTFS file for a city"""
def getGTFS(urlGTFS : str, countryCode : str, cityCode : str, params: Params):
    path : str = os.path.join(params.outDir, countryCode, cityCode)
    os.makedirs(path, exist_ok = True)
    with closing(urlopen(urlGTFS)) as r:
        with open(os.path.join(path, cityCode + "-latest.zip"), 'wb') as f:
            shutil.copyfileobj(r, f)

"""Download the OSM extract for a country"""
def getOSMDataCountry(urlOSM : str, countryCode : str, params: Params):
    #r = requests.get(urlOSM, stream = True)
    path : str = os.path.join(params.outDir, countryCode)
    os.makedirs(path, exist_ok = True)
    with closing(urlopen(urlOSM)) as r:
        with open(os.path.join(path, countryCode + "-latest.osm.pbf"), 'wb') as f:
            shutil.copyfileobj(r, f)
#             for chunk in r.iter_content(chunk_size = 1024): 
#                 if chunk:
#                     f.write(chunk)

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2017 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        logger = logging.getLogger("OTP_upd")
        logger.setLevel(logging.INFO)
        logging.basicConfig()
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-u", "--regionsURL", required=True,
                            help="The URL where the regions JSON file can be found.")
        parser.add_argument("-o", "--outDir", required=True, 
                            help="Output directory for the generated data. Under this path, the folder structure for country/region/graphs will be created using the cities/countries from the regions file. Be sure that you have enough free space as the required data from the internet is downloaded here too.")
        parser.add_argument("-t", "--otpJar", required=True, 
                            help="Full path to the jar file representing the OTP builder")
        parser.add_argument("-s", "--osmiumPath", required=True, 
                            help="The full path including the executable name for osmium tool.")
        parser.add_argument("-m", "--otpMemory", required=True, 
                            help="The RAM memory needed to run one OTP builder. This parameter is sent to the JAVA virtual machine. Ex: 800M, 20G")
        parser.add_argument("-l", "--extensionLimits", required=True, 
                            help="The decimal coordinate value that will extend the limits for a OSM city bounding box.")
        # Process arguments
        args = parser.parse_args()
        params = Params(args)
            
        logger.info("Loading regions")    
        regions = getRegions(params.regionsURL)
        logger.info("Looping through regions")  
        for region in regions:
            if not region["osmDlURL"]:
                logger.info("{0} doesn't have an OSM download URL".format(region["name"]))
            else:
                logger.info("Get {0}'s osm data".format(region["name"]))
                getOSMDataCountry(region["osmDlURL"], region["code"], params) 
                for city in region["cities"]:
                    if len(city["gtfsDlURL"]) > 0:
                        logger.info("Get GTFS for {0}/{1}".format(region["name"], city["name"]))
                        getGTFS(city["gtfsDlURL"][0], region["code"], city["code"], params)
                        logger.info("Extract OSM for {0}/{1}".format(region["name"], city["name"]))
                        extractCityOSM(region["code"], city["code"], params)
                        logger.info("Generate OTP graph for {0}/{1}".format(region["name"], city["name"]))
                        genOTPGraphs(region["code"], city["code"], params)
                    else:
                        logger.info("{0}/{1} doesn't have any GTFS download URLs".format(region["name"], city["name"]))
        
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())