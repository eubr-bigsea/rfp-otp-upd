# [EUBRA-BIGSEA] Routes for People - Open Trip Planner - Updater

This project handles the automatic update of the graph object needed by Open Trip Planner (OTP). 
It automatically downloads the necessary data from the links specified in a json file.
Using this data, it generates a graph for each city specified in the input.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

The following programs must be available for the script to work:

```
[osmium tool](https://github.com/osmcode/osmium-tool) (version that supports the "extract" command)
[Open Trip Planner](https://github.com/opentripplanner/OpenTripPlanner)
Python 3.6
Java (version dependent on the Open Trip Planner requirements)
```

### Installing

Just clone this repository.

### Executing

The script supports a number of parameters specified bellow.
Please be sure that you specify values for all of them as there are no defaults.

```
	-u, --regionsURL		The URL where the regions JSON file can be found. An example of the file can be found on the [Routes for People Web](https://github.com/asalic/rfp-web) repository (regions-template.json). 
    
    -o, --outDir 			Output directory for the generated data. Under this path, the folder structure for country/region/graphs will be created using the cities/countries from the regions file. Be sure that you have enough free space as the required data from the internet is downloaded here too.
    
    -t, --otpJar   			Full path to the jar file representing the OTP builder. The java executable must be accessible from command line.
    
    -s, --osmiumPath		The full path including the executable name for osmium tool.
    
    -m, --otpMemory			The RAM memory needed to run one OTP builder. This parameter is sent to the JAVA virtual machine. It has to be in the format support by java when using the "-Xmx" flag on the command line, ex: 800M, 20G
    
    -l, --extensionLimits	The decimal coordinate value that will extend the limits for a OSM city bounding box. Right now, the algorithm searches for the stops found in the GTFS having the max/min latitude, longitude. The four values found are incremented (for the max) or decremented (for the min) by the value specified using this parameter. Please using only positive values, otherwise the bounding box is shrank. 
```

At the end of the execution, the folder specified with *outDir* should contain a folder called *otp*.
Inside it, based on the information found in the *regions* file, there should be directories named as the country codes.
Each directory contains sub-folders named by the city code.
This last level of folders holds the graph, called *Graph.obj*. 

Execution example:

```
cd <git cloned dir>/src/py && python3.6 otp_upd.py -u ftp://ftpgrycap.i3m.upv.es/public/eubrabigsea/data/regions.json -o /tmp -t /opt/otp/otp.jar -s /opt/osmium-tool/osmium -m 20G -l 0.002
```

## Running the tests

There a number of test method found in *src/test/test_whole.py*.
It includes a class that test all functionality.
The testing procedure is invoked like:

```
python3.6 -m unittest discover -v -s <git cloned dir>/src/
```

Please keep in mind that we used only Linux to test our program, but it may work on any other OS, given that the requirements are satisfied.

## Authors

* **Andy S Alic** - *Developer, Tester, Maintainer* - [asalic](https://github.com/asalic)

## License

This project is licensed under the Apache License version 2.0 - see the [LICENSE.md](LICENSE.md) file for details
