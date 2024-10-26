# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 01:19:38 2024

@author: kasit
"""

import os
import sys
from osgeo import gdal
import numpy as np
#%%

#%%

def split_raster_bands(input_raster, in_file,output_dir=None, ):
    """
    Split a multi-band raster into separate single-band GeoTIFF files.
    
    Args:
        input_raster (str): Path to the input multi-band raster file
        output_dir (str, optional): Directory to save output files. If None, uses same directory as input
    
    Returns:
        list: List of paths to the created files
    """
    # Open the raster file
    ds = gdal.Open(input_raster)
    if ds is None:
        raise ValueError(f"Could not open raster file: {input_raster}")
    
    # Get basic information about the raster
    num_bands = ds.RasterCount
    if num_bands < 2:
        raise ValueError(f"Input raster has only {num_bands} band(s). Multi-band raster required.")
    
    # Get raster properties
    projection = ds.GetProjection()
    geotransform = ds.GetGeoTransform()
    rows = ds.RasterYSize
    cols = ds.RasterXSize
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.dirname(input_raster)
    os.makedirs(output_dir, exist_ok=True)
    
    # Get base filename without extension
    base_filename = os.path.splitext(os.path.basename(input_raster))[0]
    
    output_files = []
    
    # Process each band
    for band_num in range(1, num_bands + 1):
        # Read the band
        band = ds.GetRasterBand(band_num)
        band_data = band.ReadAsArray()
        
        # Get band metadata and properties
        data_type = band.DataType
        no_data_value = band.GetNoDataValue()
        
        # Create output filename
        output_file = os.path.join(output_dir, f"{in_file}_{band_num}.tif")
        output_files.append(output_file)
        
        # Create the output raster
        driver = gdal.GetDriverByName('GTiff')
        output_ds = driver.Create(
            output_file,
            cols,
            rows,
            1,  # Number of bands (1 since we're splitting them)
            data_type,
            options=['COMPRESS=LZW', 'TILED=YES']  # Use LZW compression and tiling
        )
        
        if output_ds is None:
            raise ValueError(f"Could not create output file: {output_file}")
        
        # Set the geotransform and projection
        output_ds.SetGeoTransform(geotransform)
        output_ds.SetProjection(projection)
        
        # Write the band data
        output_band = output_ds.GetRasterBand(1)
        if no_data_value is not None:
            output_band.SetNoDataValue(no_data_value)
        output_band.WriteArray(band_data)
        
        # Copy band metadata
        band_metadata = band.GetMetadata()
        output_band.SetMetadata(band_metadata)
        
        # Calculate statistics
        output_band.FlushCache()
        output_band.ComputeStatistics(False)
        
        # Clean up
        output_ds = None
        print(f"Saved band {band_num} to: {output_file}")
    
    # Clean up the input dataset
    ds = None
    
    return output_files

def main():
    """
    Main function to handle command line execution.
    """
    if len(sys.argv) < 2:
        print("Usage: python split_raster.py <input_raster> [output_directory]")
        print("\nExample:")
        print("python split_raster.py input.tif output_folder")
        sys.exit(1)
    
    input_raster = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        print(f"Processing raster: {input_raster}")
        # output_files = split_raster_bands(lai, out_path)
        print("\nProcessing complete!")
        # print(f"Created {len(output_files)} output files")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# split_raster_bands(lai, out_path)
