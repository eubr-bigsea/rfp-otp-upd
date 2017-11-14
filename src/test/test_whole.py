'''
Created on Oct 27, 2017

@author: asalic
'''
import unittest
import os.path
import sys
from py.params import Params
from py.otp_upd import genOTPGraphs
from py.otp_upd import getRegions
from py.otp_upd import getOSMDataCountry
from py.otp_upd import getGTFS
from py.otp_upd import extractCityOSM
from py.otp_upd import getCityBoundingBox


class WholeTest(unittest.TestCase):

    def setUp(self):
        self.countryCode = "fi"
        self.cityCode = "helsinki"
        
        self.params = Params(None)
        
        self.params.regionsURL = "ftp://ftpgrycap.i3m.upv.es/public/eubrabigsea/data/regions.json"
        self.params.otpMemory = "20G"
        self.params.extensionLimits = 0.02
        self.params.osmiumPath = "~/opt/osmium-tool/build/osmium"
        self.params.outDir = "/tmp"
        self.params.otpJar = "!/opt/otp-1.2.0-shaded.jar"
        
    def tearDown(self):
        pass

    def test_genOTPGraphs(self):
        getGTFS("ftp://ftpgrycap.i3m.upv.es/public/eubrabigsea/data/gtfs/{0}/{1}/gtfs-latest.zip".format(self.countryCode, self.cityCode), \
                self.countryCode, self.cityCode, self.params)
        getOSMDataCountry("ftp://ftpgrycap.i3m.upv.es/public/eubrabigsea/data/{0}/country-latest.osm.pbf".format(self.countryCode), 
                          self.countryCode, self.params)
        extractCityOSM(self.countryCode, self.cityCode, self.params)
        genOTPGraphs(os.path.join(self.params.outDir, "{0}/{1}/".format(self.countryCode, self.cityCode)), self.params)
        assert os.path.isfile(os.path.join(self.params.outDir, "{0}/{1}/Graph.obj".format(self.countryCode, self.cityCode))), \
            "OTP graph for city {0} hasn't been generated".format(self.cityCode)
        assert os.stat(os.path.join(self.params.outDir, "{0}/{1}/Graph.obj".format(self.countryCode, self.cityCode))).st_size != 0, \
            "OTP graph for city {0} has size 0".format(self.cityCode)        

    def test_getRegions(self):
        lstRegions = getRegions("ftp://ftpgrycap.i3m.upv.es/public/eubrabigsea/data/regions.json")
        assert lstRegions != None, "Data is none" 
        assert len(lstRegions) != 0, "No regions found"
        for country in lstRegions:
            assert "osmDlURL" in country, "Missing field \"osmDlURL\" in " + country["name"]
            for city in country["cities"]:
                assert "gtfsDlURL" in city, "Missing field \"gtfsDlURL\" in " + city["name"]
                assert "latMin" in city, "Missing field \"latMin\" in " + city["name"]
                assert "lngMin" in city, "Missing field \"lngMin\" in " + city["name"]
                assert "latMax" in city, "Missing field \"latMax\" in " + city["name"]
                assert "lngMax" in city, "Missing field \"lngMax\" in " + city["name"]
                      
    def test_getGTFS(self):
        getGTFS("ftp://ftpgrycap.i3m.upv.es/public/eubrabigsea/data/gtfs/{0}/{1}/gtfs-latest.zip".format(self.countryCode, self.cityCode),  
                self.countryCode, self.cityCode, self.params)
        assert os.path.isfile(os.path.join(self.params.outDir, "{0}/{1}/{1}-latest.zip".format(self.countryCode, self.cityCode))), \
            "Unable to download gtfs file for city {0}".format(self.cityCode)
        assert os.stat(os.path.join(self.params.outDir, "{0}/{1}/{1}-latest.zip".format(self.countryCode, self.cityCode))).st_size != 0, \
            "GTFS zip file for {0} is empty".format(self.cityCode)
              
    def test_getOSMDataCountry(self):
        getOSMDataCountry("ftp://ftpgrycap.i3m.upv.es/public/eubrabigsea/data/{0}/country-latest.osm.pbf".format(self.countryCode), 
                          self.countryCode, self.params)
        assert os.path.isfile(os.path.join(self.params.outDir, "{0}/{0}-latest.osm.pbf".format(self.countryCode))), "Unable to download pbf files"
        assert os.stat(os.path.join(self.params.outDir, "{0}/{0}-latest.osm.pbf".format(self.countryCode))).st_size != 0, "OSM File is empty"
             
    def test_extractCityOSM(self):
        getOSMDataCountry("ftp://ftpgrycap.i3m.upv.es/public/eubrabigsea/data/{0}/country-latest.osm.pbf".format(self.countryCode), 
                         self.countryCode, self.params)
        getGTFS("ftp://ftpgrycap.i3m.upv.es/public/eubrabigsea/data/gtfs/{0}/{1}/gtfs-latest.zip".format(self.countryCode, self.cityCode), 
                self.countryCode, self.cityCode, self.params)
        extractCityOSM(self.countryCode, self.cityCode, self.params)
        path = os.path.join(self.params.outDir, "{0}/{1}/{1}-latest.osm.pbf".format(self.countryCode, self.cityCode))
        assert os.path.isfile(path), "No PBF file extract found for city {0}".format(self.cityCode)
        assert os.stat(path).st_size != 0, "OSM extract city {0} is empty".format(self.cityCode)
           
    def test_getCityBoundingBox(self):
        pathF: str = os.path.join(self.params.outDir, "test_getCityBoundingBox.txt")
        with open(pathF, "w") as fOut:
            fOut.write("""stop_id, stop_lat, stop_lon
                1, 25.3232, 45.6712
                2, 24.3232, 44.6712
                3, 24.3232, 47.6712
                4, 23.3232, -45.6712""")
        oR = getCityBoundingBox(pathF, self.params)
        assert abs(abs(oR.latMax + self.params.extensionLimits) - abs(25.3232)) > sys.float_info.epsilon, "Error lat max"
        assert abs(abs(oR.latMin - self.params.extensionLimits) - abs(23.3232)) > sys.float_info.epsilon, "Error lat min"
        assert abs(abs(oR.lngMax + self.params.extensionLimits) - abs(47.6712)) > sys.float_info.epsilon, "Error lng max"
        assert abs(abs(oR.lngMin - self.params.extensionLimits) - abs(-45.6712)) > sys.float_info.epsilon, "Error lng min"
         
    def test_getCityBoundingBox_big_file(self):
        oR = getCityBoundingBox(os.path.join(self.params.outDir, "fi/helsinki/gtfs/stops2.txt"), self.params)
          
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()