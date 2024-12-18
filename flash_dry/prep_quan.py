# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 15:35:23 2024

@author: 33501

此代码将pentad数据进行求每pentad数据所在年份绘图位置(类似百分位数)运算，得到权重数据
"""

import pandas as pd
import numpy as np
from scipy.stats.mstats import mquantiles,meppf
import xarray as xr
import os
# import pentad

def nanmeppf(li):
    """
    此函数将meppf函数增加去除nan值计算得到
    """
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

path_head = r'D:\work\code\yuan\data\soil_moisture\Nc\hist'
data = xr.open_dataset(path_head + os.sep + r"swvl30_pentad.nc")
time = data['time'].values
lon = data['lon'].values
lat = data['lat'].values
pentad = data['pentad'].values

#研究时间段
start_year = 1980
end_year = 2023

for year in range(start_year,end_year+1):
    if year == start_year:      #只需研究生长期，中国范围的生长期为3-10月，其余去除
        pentad[0:(11+73*(year-(start_year-1))),:,:] = np.nan
        pentad[(61+73*(year-(start_year-1))):73,:,:] = np.nan
    else:
        pentad[73*(year-(start_year-1)):(11+73*(year-(start_year-1))),:,:] = np.nan
        pentad[(61+73*(year-(start_year-1))):73*(year-(start_year-2)),:,:] = np.nan
    
    out=np.empty((73,pentad.shape[1],pentad.shape[2]))
    out[::] = np.nan
    for x in range(pentad.shape[1]):
        for y in range(pentad.shape[2]):
            out[:,x,y] = [nanmeppf(pentad[i::73,x,y])[year-(start_year)] for i in range(73)]
            
    out_nc = xr.Dataset({'quan':(['time','lat','lon'],out)},{'lon':lon,'lat':lat,'time':list(range(1,74))})
    out_nc.to_netcdf(path_head+os.sep+'quan'+os.sep+f'swvl_{year}_quan.nc')
    print(year)



































