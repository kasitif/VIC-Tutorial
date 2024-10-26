import os
import sys
import netCDF4
import numpy as np
from osgeo import gdal
import pandas as pd
from osgeo.gdalnumeric import *  
from osgeo.gdalconst import *
from datetime import datetime

def find_nearest_idx(xx,yy,xval,yval):    
    xidx = (np.abs(xx-xval)).argmin()
    yidx = (np.abs(yy-yval)).argmin()

    ridx = yidx / xx.shape[1]
    cidx = xidx % xx.shape[1]
        
    return [ridx,cidx]
    
def format_meteo_forcing(basin_mask,inpath_precip, inpath_temp_wind,outpath,startyr,endyr):
    
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

    band = 1
    
    infiles = [os.path.join(__location__,basin_mask)]
                
    for i in range(len(infiles)):
        
            ds = gdal.Open(infiles[i],GA_ReadOnly)
            b1 = ds.GetRasterBand(band)
            var = BandReadAsArray(b1)
            
            if i == 0:
                data = np.zeros((ds.RasterYSize,ds.RasterXSize, len(infiles)))
                gt = ds.GetGeoTransform()
                lon0 = gt[0] + (gt[1] / 2.)
                lon1 = gt[0] + (data.shape[1]*gt[1])
                lat0 = gt[3] + (data.shape[0]*gt[-1])
                lat1 = gt[3] + (gt[-1] / 2.)
            
            data[:,:,i] = var[:,:]
                
            ds = None
            b1 = None
        
    lons = np.linspace(lon0,lon1,data.shape[1])
    lats = np.linspace(lat0,lat1,data.shape[0])
    xx,yy = np.meshgrid(lons,lats)

    yy = np.flipud(yy)
    
    years = np.arange(int(startyr),int(endyr)+1)
    
    mask = data[:,:,0].astype(uint8)
    mask = np.ma.masked_where(mask!=1,mask)
  
    
    print('Generating Forcings')
    for i in range(yy.shape[0]):
        for j in range(yy.shape[1]):
            if mask[i,j] == 1:
                x = xx[i,j]
                y = yy[i,j]
                ydi = 0

                for yrs in range(years.size):
        
                    #for CHIRPS data inpath_precip, inpath_temp_wind
                    ncdfs = [os.path.join(__location__,inpath_precip,'chirps-v2.0.{0}.days_p05.nc'.format(years[yrs])),
                             os.path.join(__location__,inpath_temp_wind,"tmax.2m.gauss.{0}.nc".format(years[yrs])),
                             os.path.join(__location__,inpath_temp_wind,"tmin.2m.gauss.{0}.nc".format(years[yrs])),
                             os.path.join(__location__,inpath_temp_wind,"vwnd.10m.gauss.{0}.nc".format(years[yrs])),
                             os.path.join(__location__,inpath_temp_wind,"uwnd.10m.gauss.{0}.nc".format(years[yrs]))]
                    # print(ncdfs)

                    prnc = netCDF4.Dataset(ncdfs[0])
                    # print(prnc)

                    pr = prnc.variables['precip']
                    # print(pr)


                    if yrs == 0:
                        
                        latpr = prnc.variables['latitude'];latpr = latpr[:]
                        lonpr = prnc.variables['longitude'];lonpr = lonpr[:]
                    
                        meteonc = netCDF4.Dataset(ncdfs[1])
                        tminn = netCDF4.Dataset(ncdfs[2])
                        vwinn = netCDF4.Dataset(ncdfs[3])
                        uwinn = netCDF4.Dataset(ncdfs[4])

                        latnc = meteonc.variables['lat'];latnc=latnc[:]
                        lonnc = meteonc.variables['lon'];lonnc=lonnc[:]
                        #time = meteonc.variables['time'][:]
                        
                        tmax = meteonc.variables['tmax']
                        tmin = tminn.variables['tmin']
                        uwind = uwinn.variables['uwnd']
                        vwind = vwinn.variables['vwnd']
                        
                        lons,lats = np.meshgrid(lonnc,latnc)
                        prlons,prlats = np.meshgrid(lonpr,latpr)

                        idx = find_nearest_idx(lons,lats,x,y)
                        pridx = find_nearest_idx(prlons,prlats,x,y)

                        
                        cnt1 = 0
                        cnt2 = 1
                    
                   
                    meteofile = os.path.join(__location__,outpath,'forcing_{0:.4f}_{1:.4f}'.format(y,x))
                    with open(meteofile, 'a') as f:
                        if years[yrs] % 4 == 0:
                            time = 366
                        else:
                            time = 365
                       
                        for t in range(time):
                            prval = np.mean(pr[t,pridx[0],pridx[1]])

                            prec1= str(round(prval, 2))
                            tminval = np.min(tmin[cnt1:cnt2+1,idx[0],idx[1]]-273.15).round(4)
                            tmaxval = np.max(tmax[cnt1:cnt2+1,idx[0],idx[1]]-273.15).round(4)
                            tminval1=str(round(tminval, 2))
                            tmaxval1=str(round(tmaxval, 2))
    
                            uwndval = uwind[cnt1:cnt2+1,idx[0],idx[1]].mean()

                            vwndval = vwind[cnt1:cnt2+1,idx[0],idx[1]].mean()
                            windval1 = np.sqrt(uwndval**2 + vwndval**2).round(4)


                            f.write('{0}\t {1}\t {2}\t {3}\n'.format(prec1,tmaxval1,tminval1,windval1))

                            cnt1+=1
                            cnt2+=1               
	
                    prnc.close()                   
                meteonc.close()
                
    
    return
    
def main():

    t1 = datetime.now()

    format_meteo_forcing(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    dt = datetime.now()-t1
    print ('Processing time: {0}'.format(dt))
    
    return
    
if __name__ == "__main__":
    main()
    
