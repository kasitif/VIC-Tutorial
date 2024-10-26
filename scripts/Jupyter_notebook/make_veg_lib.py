
import os
import sys
import glob
import json
import warnings
import numpy as np
from osgeo import gdal
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *
from scipy import ndimage

warnings.simplefilter("ignore")

def make_veg_lib(LCFile, LAIFolder, ALBFolder, outVeg, scheme='IGBP'):
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    if scheme == 'IGBP':
        attriFile = os.path.join(__location__, 'veg_type_attributes_igbp.json')
        waterCls = 0
    elif scheme == 'GLCC':
        attriFile = os.path.join(__location__, 'veg_type_attributes_glcc.json')
        waterCls = 12
    elif scheme == 'IPCC':
        attriFile = os.path.join(__location__, 'veg_type_attributes_ipcc.json')
        waterCls = 0
    else:
        raise SyntaxError('Land cover classification scheme not supported')

    band = 1

    with open(attriFile) as data_file:
        attriData = json.load(data_file)

    clsAttributes = attriData['classAttributes']

    try:
        # Read land cover data and get its properties
        ds = gdal.Open(os.path.join(__location__, LCFile), GA_ReadOnly)
        lc_transform = ds.GetGeoTransform()
        lc_projection = ds.GetProjection()
        lc_band = ds.GetRasterBand(band)
        lccls = BandReadAsArray(lc_band)
        clsRes = lc_transform[1]
        ds = None
        lc_band = None

        # Get sorted lists of input files
        laifiles = sorted(glob.glob(os.path.join(__location__, LAIFolder, '*.tif')))
        albfiles = sorted(glob.glob(os.path.join(__location__, ALBFolder, '*.tif')))

        # Create memory driver for reprojection
        mem_driver = gdal.GetDriverByName('MEM')

        # Initialize arrays with land cover dimensions
        laiMon = np.zeros([lccls.shape[0], lccls.shape[1], 12])
        albMon = np.zeros([lccls.shape[0], lccls.shape[1], 12])

        for i in range(12):
            # Process LAI data
            laids = gdal.Open(laifiles[i], GA_ReadOnly)
            lai_data = laids.GetRasterBand(band).ReadAsArray()
            
            # Create target dataset for LAI
            lai_target = mem_driver.Create('', lccls.shape[1], lccls.shape[0], 1, gdal.GDT_Float32)
            lai_target.SetGeoTransform(lc_transform)
            lai_target.SetProjection(lc_projection)
            
            # Perform reprojection/resampling
            gdal.ReprojectImage(laids, lai_target, laids.GetProjection(), lc_projection, gdal.GRA_NearestNeighbour)
            
            # Read resampled data
            laiMon[:,:,i] = lai_target.ReadAsArray()
            
            laids = None
            lai_target = None

            # Process Albedo data
            albds = gdal.Open(albfiles[i], GA_ReadOnly)
            alb_data = albds.GetRasterBand(band).ReadAsArray()
            
            # Create target dataset for Albedo
            alb_target = mem_driver.Create('', lccls.shape[1], lccls.shape[0], 1, gdal.GDT_Float32)
            alb_target.SetGeoTransform(lc_transform)
            alb_target.SetProjection(lc_projection)
            
            # Perform reprojection/resampling
            gdal.ReprojectImage(albds, alb_target, albds.GetProjection(), lc_projection, gdal.GRA_NearestNeighbour)
            
            # Read resampled data
            albMon[:,:,i] = alb_target.ReadAsArray()
            
            albds = None
            alb_target = None

    except AttributeError:
        raise IOError('Raster file input error, check that all paths are correct')

    # Mask nodata values
    albMon[np.where(albMon >= 1000)] = np.nan

    veglib = os.path.join(__location__, outVeg)

    if os.path.exists(veglib):
        os.remove(veglib)

    try:
        with open(veglib, 'w') as f:
            for i in range(len(clsAttributes)):
                attributes = clsAttributes[i]['properties']

                if i == waterCls:
                    lai = [0.01] * 12
                    alb = [0.08] * 12
                else:
                    lai = []
                    alb = []
                    for j in range(12):
                        clsidx = np.where(lccls == i)
                        laiStep = laiMon[:,:,j]
                        albStep = albMon[:,:,j]
                        
                        # Handle potential empty indices
                        if len(clsidx[0]) > 0:
                            lai.append(np.nanmean(laiStep[clsidx])/1000.)
                            alb.append(np.nanmean(albStep[clsidx])/1000.)
                        else:
                            lai.append(0.01)
                            alb.append(0.08)

                overstory = int(attributes['overstory'])
                rarc = str(attributes['rarc'])
                rmin = str(attributes['rmin'])
                vegHeight = float(attributes['h'])
                rgl = str(attributes['rgl'])
                rad_atten = str(attributes['rad_atn'])
                wind_atten = str(attributes['wnd_atn'])
                trunk_ratio = str(attributes['trnk_r'])

                rough = 0.123 * vegHeight
                dis = 0.67 * vegHeight

                wind_h = vegHeight + 10 if overstory == 1 else vegHeight + 2

                comment = str(attributes['classname'])

                if i == 0:
                    f.write('#Class\tOvrStry\tRarc\tRmin\tJAN-LAI\tFEB-LAI\tMAR-LAI\tAPR-LAI\tMAY-LAI\tJUN-LAI\tJUL-LAI\tAUG-LAI\tSEP-LAI\tOCT-LAI\tNOV-LAI\tDEC-LAI\tJAN-ALB\tFEB_ALB\tMAR-ALB\tAPR-ALB\tMAY-ALB\tJUN-ALB\tJUL-ALB\tAUG-ALB\tSEP-ALB\tOCT-ALB\tNOV-ALB\tDEC-ALB\tJAN-ROU\tFEB-ROU\tMAR-ROU\tAPR-ROU\tMAY-ROU\tJUN-ROU\tJUL-ROU\tAUG-ROU\tSEP-ROU\tOCT-ROU\tNOV-ROU\tDEC-ROU\tJAN-DIS\tFEB-DIS\tMAR-DIS\tAPR-DIS\tMAY-DIS\tJUN-DIS\tJUL-DIS\tAUG-DIS\tSEP-DIS\tOCT-DIS\tNOV-DIS\tDEC-DIS\tWIND_H\tRGL\trad_atten\twind_atten\ttruck_ratio\tCOMMENT\n')

                f.write('{0}\t{1}\t{2}\t{3}\t{4:.4f}\t{5:.4f}\t{6:.4f}\t{7:.4f}\t{8:.4f}\t{9:.4f}\t{10:.4f}\t{11:.4f}\t{12:.4f}\t{13:.4f}\t{14:.4f}\t{15:.4f}\t{16:.4f}\t{17:.4f}\t{18:.4f}\t{19:.4f}\t{20:.4f}\t{21:.4f}\t{22:.4f}\t{23:.4f}\t{24:.4f}\t{25:.4f}\t{26:.4f}\t{27:.4f}\t{28}\t{28}\t{28}\t{28}\t{28}\t{28}\t{28}\t{28}\t{28}\t{28}\t{28}\t{28}\t{29}\t{29}\t{29}\t{29}\t{29}\t{29}\t{29}\t{29}\t{29}\t{29}\t{29}\t{29}\t{30}\t{31}\t{32}\t{33}\t{34}\t{35}\n'.format(
                    i, overstory, rarc, rmin, lai[0], lai[1], lai[2], lai[3], lai[4], lai[5], lai[6], lai[7], lai[8], lai[9], lai[10], lai[11],
                    alb[0], alb[1], alb[2], alb[3], alb[4], alb[5], alb[6], alb[7], alb[8], alb[9], alb[10], alb[11],
                    rough, dis, wind_h, rgl, rad_atten, wind_atten, trunk_ratio, comment))

    except IOError:
        raise IOError('Cannot write output file, error with output veg library file path')

    return

def main():

    n_args = len(sys.argv)

    # Check user inputs
    if n_args != 6:
        print("Wrong user input")
        print("Script writes the vegetation library file for the VIC model")
        print("usage: python make_veg_lib.py <land cover raster> <LAI data folder> <albedo data folder> <output veg lib file> <land cover classification scheme>")
        print("Exiting system...")
        sys.exit()

    else:
        # check that inputs are correct
        if sys.argv[2][-1] != '/':
            print("LAI DIR SHOULD CONTAIN TRAILING '/'")
            print("fixing it for you...")
            sys.argv[2] = sys.argv[2] + "/"

        if sys.argv[3][-1] != '/':
            print("ALBEDO DIR SHOULD CONTAIN TRAILING '/'")
            print("fixing it for you...")
            sys.argv[3] = sys.argv[3] + "/"
        

        # do the process
        make_veg_lib(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])

    return

# Execute the main level program if run as standalone
if __name__ == "__main__":
    main()
