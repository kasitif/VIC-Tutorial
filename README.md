# VIC-Tutorial
VIC Hydrologic Model Tutorial
A tutorial demonstrating the setup and execution of the Variable Infiltration Capacity (VIC) model version 4.2 with routing capabilities (based on Lohmann et al.) for the 1KA42 Basin in Tanzania.

Overview
This tutorial provides step-by-step guidance for implementing the VIC hydrologic model, including model setup, data preparation, execution, and analysis.
Prerequisites
Knowledge Requirements

- GIS fundamentals
- Remote Sensing basics
- Hydrology/hydrologic modelling understanding
- Python programming basics
- Linux command line familiarity

Software Requirements

- QGIS 2.8+ or ArcGIS
Python 3.6+
GDAL
NumPy
SciPy
Pandas

Data Requirements
All input files should be placed in the data folder (XXXX/XXXX/data):
Required Datasets

Topographic Data

SRTM elevation data
Slope data


Land Surface Data

MODIS land cover data
Leaf Area Index (LAI)
Albedo


Soil Data

HWSD (Harmonized World Soil Database)


Climate Data

CHIRPS annual precipitation climatology
Daily precipitation records
Maximum and minimum temperature
Wind speed data


Basin Data

Delineated basin shapefile



Model Execution
Running VIC Model

Navigate to the VIC executable directory
Execute the model using:

bashCopy./vicNl -g ./input/global.params
Flux File Processing
Python code for reading flux files is provided in the tutorial:
pythonCopyflux_dir = glob.glob('G:\\1KA42\\data\\output\\fluxes\\*')
flux_file = flux_dir[0]
flux_file = read_file(flux_file, file_type='txt', header=None)
The flux files contain the following variables:

Year
Month
Day
PREC (Precipitation)
EVAP (Evaporation)
RUNOFF
BASEFLOW
SWE (Snow Water Equivalent)
SOIL_MOIST (Soil Moisture)

Upcoming Features
Routing Model

Implementation details coming soon

Model Calibration

Calibration procedures using Shuffled Complex Evolution (SCE-UA) Method
Details to be added

Contributing
Feel free to submit issues and enhancement requests.
License
[Add appropriate license information]
