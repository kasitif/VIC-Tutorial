"""
Utility functions for creating grid files from Area of Interest (AOI) shapefiles.
"""
import os
import numpy as np
from osgeo import gdal, ogr, osr

def create_aoi_grid(input_aoi, output_grid, grid_size):
    """
    Create a raster grid from an Area of Interest (AOI) shapefile.
    
    Args:
        input_aoi (str): Path to input AOI shapefile
        output_grid (str): Path for output grid file
        grid_size (float): Size of grid cells in degrees
        
    Returns:
        bool: True if successful, raises exception otherwise
    """
    # Define constants
    NO_DATA_VALUE = 0
    HI_RES_RATIO = 50.0
    
    # Open the data source and read in the extent
    source_ds = ogr.Open(input_aoi)
    if source_ds is None:
        raise ValueError(f"Could not open input AOI file: {input_aoi}")
        
    source_layer = source_ds.GetLayer()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    
    # Create high res source for boundary accuracy
    high_res_grid = grid_size / HI_RES_RATIO
    x_hres = int(np.ceil((x_max - x_min) / high_res_grid))
    y_hres = int(np.ceil((y_max - y_min) / high_res_grid))
    
    # Create memory dataset
    mem_ds = gdal.GetDriverByName('MEM').Create('', x_hres, y_hres, 1, gdal.GDT_Byte)
    if mem_ds is None:
        raise RuntimeError("Failed to create memory dataset")
        
    mem_ds.SetGeoTransform((x_min, high_res_grid, 0, y_max, 0, -high_res_grid))
    band = mem_ds.GetRasterBand(1)
    band.SetNoDataValue(NO_DATA_VALUE)
    
    # Rasterize shapefile
    gdal.RasterizeLayer(mem_ds, [1], source_layer, burn_values=[1])
    array = band.ReadAsArray()
    
    # Create the destination data source
    x_res = int(np.ceil((x_max - x_min) / grid_size))
    y_res = int(np.ceil((y_max - y_min) / grid_size))
    
    # Process grid cells
    out_mask = np.zeros([y_res, x_res])
    for i in range(y_res):
        y1 = int(i * HI_RES_RATIO)
        y2 = int(y1 + HI_RES_RATIO)
        for j in range(x_res):
            x1 = int(j * HI_RES_RATIO)
            x2 = int(x1 + HI_RES_RATIO)
            
            tmp = array[y1:y2, x1:x2]
            if np.any(tmp == 1):
                out_mask[i, j] = 1
    
    # Create output raster
    spatial_ref = osr.SpatialReference()
    spatial_ref.SetWellKnownGeogCS('WGS84')
    
    drv = gdal.GetDriverByName('GTiff')
    target_ds = drv.Create(output_grid, x_res, y_res, 1, gdal.GDT_Byte)
    if target_ds is None:
        raise RuntimeError(f"Failed to create output file: {output_grid}")
        
    target_ds.SetGeoTransform((x_min, grid_size, 0, y_max, 0, -grid_size))
    target_ds.SetProjection(spatial_ref.ExportToWkt())
    
    band = target_ds.GetRasterBand(1)
    band.WriteArray(out_mask)
    band.SetNoDataValue(NO_DATA_VALUE)
    
    # Cleanup
    source_ds = None
    mem_ds = None
    target_ds = None
    
    return True

def create_grid_from_bounds(output_grid, bounds, grid_size):
    """
    Create a regular grid from coordinate bounds.
    
    Args:
        output_grid (str): Path for output grid file
        bounds (tuple): (xmin, xmax, ymin, ymax) in degrees
        grid_size (float): Size of grid cells in degrees
        
    Returns:
        bool: True if successful, raises exception otherwise
    """
    x_min, x_max, y_min, y_max = bounds
    
    # Calculate grid dimensions
    x_res = int(np.ceil((x_max - x_min) / grid_size))
    y_res = int(np.ceil((y_max - y_min) / grid_size))
    
    # Create output mask
    out_mask = np.ones([y_res, x_res])
    
    # Create output raster
    spatial_ref = osr.SpatialReference()
    spatial_ref.SetWellKnownGeogCS('WGS84')
    
    drv = gdal.GetDriverByName('GTiff')
    target_ds = drv.Create(output_grid, x_res, y_res, 1, gdal.GDT_Byte)
    if target_ds is None:
        raise RuntimeError(f"Failed to create output file: {output_grid}")
        
    target_ds.SetGeoTransform((x_min, grid_size, 0, y_max, 0, -grid_size))
    target_ds.SetProjection(spatial_ref.ExportToWkt())
    
    band = target_ds.GetRasterBand(1)
    band.WriteArray(out_mask)
    band.SetNoDataValue(0)
    
    # Cleanup
    target_ds = None
    
    return True

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python aoi_grid_utils.py <input_aoi> <output_grid> <grid_size>")
        sys.exit(1)
        
    try:
        create_aoi_grid(sys.argv[1], sys.argv[2], float(sys.argv[3]))
        print(f"Successfully created grid: {sys.argv[2]}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
