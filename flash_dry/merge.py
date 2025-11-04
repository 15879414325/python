# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 14:20:16 2024

@author: 33501

This code combines the hourly data into daily data.
"""

import numpy as np
import xarray as xr
import os
from datetime import datetime

path_head = r"D:\work\code\yuan\data\soil_moisture"  

#Research period
start_year = 1980   
end_year = 2023


for year in range(start_year,end_year+1):
    t = []
    l1 = []
    l2 = []
    l3 = []
    for month in range(1,13):
        base_name=os.listdir(path_head+os.sep+f'soil_moisture_{str(year)}-{month}.netcdf')[0]
        data=xr.open_dataset(path_head+os.sep+f'soil_moisture_{str(year)}-{month}.netcdf'+os.sep+base_name)
        lon = data['longitude'].values
        lat = data['latitude'].values
        time=data['time'].values
        swvl1 = data['swvl1'].values
        swvl2 = data['swvl2'].values
        swvl3 = data['swvl3'].values
        
        for i in range(0,time.shape[0],24): #Calculate the average for every 24 hours
            l1.append(np.mean(swvl1[i:i+24,:,:],axis=0))
            l2.append(np.mean(swvl2[i:i+24,:,:], axis=0))
            l3.append(np.mean(swvl3[i:i+24,:,:], axis=0))
            t.append(time[i])
        
    out1 = xr.Dataset({'swvl1': (['time', 'lat', 'lon'], np.array(l1)),'swvl2': (['time', 'lat', 'lon'], np.array(l2)),'swvl3': (['time', 'lat', 'lon'], np.array(l3))},
                     {'lon': lon, 'lat': lat, 'time': np.array(t)})
    out1.to_netcdf(path_head+os.sep+'Nc'+os.sep+'hist'+os.sep+'swvl'+os.sep+'swvl'+'_'+ str(year)+'.nc')
    print(year)


















































