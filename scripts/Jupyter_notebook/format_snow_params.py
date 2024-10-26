import os
import sys
import warnings
import numpy as np
from osgeo import gdal
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *

warnings.simplefilter("ignore")

def format_snow_params(basin_mask, elv_hi_res, out_snow, interval):
    """
    Format snow parameters from elevation and mask data.
    
    Args:
        basin_mask (str): Path to the basin mask file
        elv_hi_res (str): Path to the high resolution elevation file
        out_snow (str): Path to the output snow parameter file
        interval (str): Interval value for elevation bands
    """
    band = 1
    interval = int(interval)
    infiles = [basin_mask, elv_hi_res]
    
    # Read mask data
    ds = gdal.Open(infiles[0], GA_ReadOnly)
    if ds is None:
        raise ValueError(f"Could not open mask file: {infiles[0]}")
    b1 = ds.GetRasterBand(band)
    mask = BandReadAsArray(b1)
    mask_res = ds.GetGeoTransform()[1]
    ds = None
    b1 = None
    
    # Read elevation data
    ds = gdal.Open(infiles[1], GA_ReadOnly)
    if ds is None:
        raise ValueError(f"Could not open elevation file: {infiles[1]}")
    b1 = ds.GetRasterBand(band)
    elvhires = BandReadAsArray(b1)
    cls_res = ds.GetGeoTransform()[1]
    ds = None
    b1 = None

    # Handle precipitation data if it exists
    try:
        Precip
    except NameError:
        Precip = None
    
    if Precip is not None:
        ds = gdal.Open(infiles[3], GA_ReadOnly)
        b1 = ds.GetRasterBand(band)
        pr = BandReadAsArray(b1)
        ds = None
        b1 = None
        pr = np.ma.masked_where(pr < 0, pr)
    
    # Mask invalid elevation values
    elvhires = np.ma.masked_where(elvhires < 0, elvhires)
    
    # Calculate resolution ratio
    cls_ratio = int(mask_res / cls_res)
    
    # Remove existing output file if it exists
    if os.path.exists(out_snow):
        os.remove(out_snow)

    nbands = []
    
    # First pass: determine maximum number of bands
    for i in range(mask.shape[0]):
        cy1 = i * cls_ratio
        cy2 = cy1 + cls_ratio

        for j in range(mask.shape[1]):
            if mask[i, j] != 1:
                continue
                
            cx1 = j * cls_ratio
            cx2 = cx1 + cls_ratio
            tmp = elvhires[cy1:cy2, cx1:cx2]
            
            min_elv = np.min(tmp.astype(int)) - (np.min(tmp.astype(int)) % interval)
            max_elv = np.max(tmp.astype(int)) + (np.max(tmp.astype(int)) % interval)
            bands = np.arange(min_elv, max_elv + interval, interval)
            
            bcls = np.full_like(tmp, -1)
            
            for b in range(len(bands) - 1):
                bcls[np.where((tmp >= bands[b]) & (tmp < bands[b + 1]))] = b
            
            uniqcnt = np.unique(bcls[np.where(tmp > 0)])
            nbands.append(len(uniqcnt))

    max_bands = max(nbands)
    print(f'Number of maximum bands: {max_bands}')

    # Second pass: write data
    with open(out_snow, 'w') as f:
        cnt = 1
        
        for i in range(mask.shape[0]):
            cy1 = i * cls_ratio
            cy2 = cy1 + cls_ratio

            for j in range(mask.shape[1]):
                if mask[i, j] != 1:
                    continue
                    
                cx1 = j * cls_ratio
                cx2 = cx1 + cls_ratio
                tmp = elvhires[cy1:cy2, cx1:cx2]
                
                min_elv = np.min(tmp.astype(int)) - (np.min(tmp.astype(int)) % interval)
                max_elv = np.max(tmp.astype(int)) + (np.max(tmp.astype(int)) % interval)
                bands = np.arange(min_elv, max_elv + interval, interval)
                
                bcls = np.full_like(tmp, -1)
                
                for b in range(len(bands) - 1):
                    bcls[np.where((tmp >= bands[b]) & (tmp < bands[b + 1]))] = b
                
                uniqcnt = np.unique(bcls[np.where(tmp > 0)])
                
                f.write(f'{cnt}\t')
                
                # Write fractions for each band
                for c in range(max_bands):
                    try:
                        idx = np.where(bcls == uniqcnt[c])
                        frac = float(len(idx[0])) / float(len(bcls[bcls >= 0]))
                    except IndexError:
                        frac = 0
                    f.write(f'{frac:.4f}\t')
                
                # Write mean elevations for each band
                for c in range(max_bands):
                    try:
                        idx = np.where(bcls == uniqcnt[c])
                        muelv = np.nanmean(tmp[idx])
                    except IndexError:
                        muelv = 0
                    f.write(f'{muelv:.4f}\t')
                
                # Write additional fractions
                for c in range(max_bands):
                    try:
                        idx = np.where(bcls == uniqcnt[c])
                        frac = float(len(idx[0])) / float(len(bcls[bcls >= 0]))
                    except IndexError:
                        frac = 0
                    f.write(f'{frac:.4f}\t')
                
                f.write('\n')
                cnt += 1

def main():
    if len(sys.argv) != 5:
        print("Usage: python format_snow_params.py <basin_mask> <elv_hi_res> <out_snow> <interval>")
        sys.exit(1)
    
    try:
        format_snow_params(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()