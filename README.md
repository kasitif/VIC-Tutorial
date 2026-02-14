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
- Python 3.6+
- GDAL
- NumPy
- SciPy
- Pandas

Data Requirements
All input files should be placed in the data folder (XXXX/XXXX/data):
Required Datasets

- Topographic Data
- SRTM elevation data
- Slope data
- Land Surface Data
- MODIS land cover data
- Leaf Area Index (LAI)
- Albedo
- Soil Data (HWSD (Harmonized World Soil Database)
- Basin Data (Delineated basin shapefile)
  
Meteorological Data
    - CHIRPS annual precipitation climatology
    - Daily precipitation records
    - Maximum and minimum temperature
    - Wind speed data

### Note that:
  #### -High-resolution datasets should be used for variables that capture sub-grid heterogeneity, such as elevation and vegetation parameters influencing snow variability (e.g., DEM, land cover, LAI, albedo).
  #### -Simulation-resolution (Lower Resolution) datasets (in this case, 1km) should be used for forcing data, soil properties, and most meteorological inputs.

Video Links on Input file preparations
1. https://youtu.be/lCJwYMlxuew
2. https://youtu.be/FdHT_K7ILRg
3. https://youtu.be/08uVoB_tBLA
4. https://youtu.be/ZOxnxcCPBJM
## Use the Jupyter notebook vic_tutorial.ipynb in the scripts folder
Contributing
Feel free to submit issues and enhancement requests.

