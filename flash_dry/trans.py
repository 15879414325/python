# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 14:46:24 2024

@author: 33501

This code combines three sets of soil data of different depths into one soil data set.
"""


import xarray as xr
import os
# import merge

#This method employs the weighting method. The following three parameters represent the weights of the three soil layers.
c1=0.2333
c2=0.7
c3=0.0667

path_head = r'D:\work\code\yuan\data\soil_moisture\Nc\hist'

#Research period
start_year = 1980
end_year = 2023

for year in range(start_year,end_year+1):
    data = xr.open_dataset(path_head+os.sep+'swvl'+os.sep+f"swvl_{year}.nc")
    time = data['time'].values
    lon = data['lon'].values
    lat = data['lat'].values
    swvl1 = data['swvl1'].values
    swvl2 = data['swvl2'].values
    swvl3 = data['swvl3'].values

    swvl30 = swvl1*c1+swvl2*c2+swvl3*c3  #Merge soil data
    
    out1 = xr.Dataset({'swvl30':(['time','lat','lon'],swvl30)},{'lon':lon,'lat':lat,'time':time})
    out1.to_netcdf(path_head+os.sep+f"\\swvl30\\swvl30_{year}.nc")
    print(year)






































