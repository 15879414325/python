# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 14:55:35 2024

@author: 33501

This code combines the daily data into pentad (every five days) data.
"""

import numpy as np
import xarray as xr
import os
from datetime import datetime
#import trans

path_head = r'D:\work\code\yuan\data\soil_moisture\Nc\hist'
lst=[]

#Research period
start_year = 1980
end_year = 2023

for year in range(start_year,end_year+1):
    
    data = xr.open_dataset(path_head + os.sep + r'swvl30'+ os.sep + f"\\swvl30_{year}.nc")
    time = data['time'].values
    lon = data['lon'].values
    lat = data['lat'].values
    swvl30 = data['swvl30'].values
    
    if time.shape[0]==366:   #For February 29th of leap years, simply delete it.
        tmp = swvl30.copy()
        swvl30 = np.empty((365,tmp.shape[1],tmp.shape[2]))
        swvl30[:59] = tmp[:59]
        swvl30[59:] = tmp[60:]
    
    for i in range(0,365,5):    #Merge daily data
        lst.append(np.mean(swvl30[i:i+5],axis=0))

out = xr.Dataset({'pentad':(['time','lat','lon'],np.array(lst))},{'lon':lon,'lat':lat,'time':list(range(1,len(lst)+1))})
out.to_netcdf(path_head+os.sep+f"swvl30_pentad.nc")


































