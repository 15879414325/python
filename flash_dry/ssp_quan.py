# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 19:42:30 2024

@author: 33501

此代码对未来土壤数据计算权重
"""
import xarray as xa
from osgeo import gdal,ogr
import numpy as np
from scipy.stats.mstats import mquantiles,meppf

def nanmeppf(li):
    l = li.copy()
    out = np.zeros(l.shape)
    pos = np.where(np.isnan(l))
    if pos[0].shape[0] == l.shape[0]:
        return np.array([np.nan for i in range(l.shape[0])])
    for p in pos[0]:
        out[p] = np.nan
    if pos[0].shape[0]!=0:
        ll = np.delete(l,pos[0])
        lm = meppf(ll)
    else:
        return meppf(l)
    c = 0
    for i in range(out.shape[0]):
        if np.isnan(out[i]):
            continue
        out[i] = lm[c]
        c +=1
    return out

swvl_dataset = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\dry585_soil.nc")

# swvl_ea5 = np.nanmean(xa.open_dataarray(r"D:\work\code\yuan\data\soil_moisture\Nc\hist\swvl30_pentad.nc").values,axis=0)
# swvl_cmip6 = np.nanmean(xa.open_dataarray(r"D:\work\code\yuan\data\CMIP6\ssp\hist.nc").values,axis=0)

time = swvl_dataset['time'].values

lon = swvl_dataset['lon'].values
lat = swvl_dataset['lat'].values
swvl = swvl_dataset['pentad'].values

# swvl = (swvl/100-swvl_cmip6)+swvl_ea5

swvl_quan = np.zeros(swvl.shape)
time = []
for year in range(0,swvl.shape[0],73):
    for x in range(swvl.shape[1]):
        for y in range(swvl.shape[2]):
            if x<100:
                swvl[year:year+11,x,y] = np.nan
                swvl[year+61:year+73,x,y] = np.nan
            swvl_quan[year:year+73,x,y] = [nanmeppf(swvl[i::73,x,y])[int(year/73)] for i in range(73)]
    time+=[str(int(year/73+2015))+'-'+str(i) for i in range(1,74)]
    print(str(int(year/73+2015)))



out_nc = xa.Dataset({'quan':(['time','lat','lon'],swvl_quan)},{'lon':lon,'lat':lat,'time':time})

out_nc.to_netcdf(r"D:\work\code\yuan\data\CMIP6\ssp\dry585_quan_30s.nc")



# time = []
# for year in range(1980,2015):
#     swvl_dataset = xa.open_dataset(f"D:\\work\\code\\yuan\\data\\soil_moisture\\Nc\\quan\\swvl_{year}_quan.nc")
#     data = swvl_dataset['quan'].values
#     lon = swvl_dataset['lon'].values
#     lat = swvl_dataset['lat'].values
#     time+=[f'{year}-{i}' for i in range(1,74)]
#     if year==1980:
#         out = data.copy()
#     else:
#         out = np.concatenate((out,data))
#         print(year)


# out_nc = xa.Dataset({'quan':(['time','lat','lon'],out)},{'lon':lon,'lat':lat,'time':time})
# out_nc.to_netcdf(r'D:\work\code\yuan\data\soil_moisture\Nc\swvl_quan.nc')
















