# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 17:02:40 2024

@author: 33501

处理下载的彭曼公式所需数据
"""

import numpy as np
import xarray as xa
import os
import rasterio as ra
import math
import warnings
warnings.filterwarnings("ignore")

# #wind
# def wind_s(path_head):
#     time = []
#     for year in range(2000,2024):
#         files = os.listdir(f"{path_head}\\{year}")
#         for file in files:
#             dataset = xa.open_dataset(f"{path_head}\\{year}\\{file}")
#             var = list(dataset.variables)[-1]
#             data = dataset[var].values
#             data = data*(4.87/np.log(672.58))
#             time.append(dataset['time'].values[0])
#             lat = dataset['latitude'].values
#             lon = dataset['longitude'].values
#             if (file == files[0]) and (year==2000):
#                 wind_speed = data
#             else:
#                 wind_speed = np.concatenate((wind_speed,data))
#         # if year == 2000:
#         #     wind_speed = np.array([np.nanmean(win,axis=0)])
#         # else:
#         #     wind_speed = np.concatenate((wind_speed,np.array([np.nanmean(win,axis=0)])))
#     return [wind_speed,[np.array(time),lat,lon]]

# wind_u,profile = wind_s(r"D:\work\code\yuan\data\wind\10m_u_component_of_wind")
# wind_v,profile = wind_s(r"D:\work\code\yuan\data\wind\10m_v_component_of_wind")
# wind = ((wind_u**2)+(wind_v**2))**(1/2)

# nc_out = xa.Dataset({'wind':(['time','lat','lon'],wind)},{'time':profile[0],'lat':profile[1],'lon':profile[2]})
# nc_out.to_netcdf(r'D:\work\code\yuan\data\wind\wind.nc')


# #tmin

# path_head = r'D:\work\code\yuan\data\tem\tmin'

# files = os.listdir(path_head)
# for file in files:
#     dataset = ra.open(f"{path_head}\\{file}")
#     data = dataset.read()[0]
#     if file == files[0]:
#         tmin = np.zeros((len(files),data.shape[0],data.shape[1]))
#         tmin[0] = data.copy()
#         i = 1
#     else:
#         tmin[i] = data.copy()
#         i+=1
# # tmin = np.nanmean(tmin,axis=0)
# tansform = dataset.get_transform()
# lon = []
# for i in range(data.shape[1]):
#     lon.append(tansform[0]+i*tansform[1])
# lat = []
# for i in range(data.shape[0]):
#     lat.append(tansform[3]+i*tansform[5])

# time = list(map(lambda x:x[4:-4],files))

# nc_out = xa.Dataset({'tmin':(['time','lat','lon'],tmin)},{'time':time,'lat':lat,'lon':lon})
# nc_out.to_netcdf(r'D:\work\code\yuan\data\tem\tmin.nc')

# #tmax
# path_head = r'D:\work\code\yuan\data\tem\tmax'

# files = os.listdir(path_head)
# for file in files:
#     dataset = ra.open(f"{path_head}\\{file}")
#     data = dataset.read()[0]
#     if file == files[0]:
#         tmax = np.zeros((len(files),data.shape[0],data.shape[1]))
#         tmax[0] = data.copy()
#         i = 1
#     else:
#         tmax[i] = data.copy()
#         i+=1
# # tmax = np.nanmean(tmax,axis=0)
# tansform = dataset.get_transform()
# lon = []
# for i in range(data.shape[1]):
#     lon.append(tansform[0]+i*tansform[1])
# lat = []
# for i in range(data.shape[0]):
#     lat.append(tansform[3]+i*tansform[5])

# time = list(map(lambda x:x[4:-4],files))

# nc_out = xa.Dataset({'tmax':(['time','lat','lon'],tmax)},{'time':time,'lat':lat,'lon':lon})
# nc_out.to_netcdf(r'D:\work\code\yuan\data\tem\tmax.nc')



#dew_tem

path_head = r"D:\work\code\yuan\data\2m_dewpoint_temperature"
time = []
for year in range(2000,2024):
    files = os.listdir(f'{path_head}\\{year}')
    for file in files:
        dataset = xa.open_dataset(f"{path_head}\\{year}\\{file}")
        list(dataset.variables)
        data = dataset['d2m'].values-273.15
        lon = dataset['longitude'].values
        lat = dataset['latitude'].values
        time.append(dataset['time'].values[0])
        if (year==2000) and (file==files[0]):
            ea = 0.6108*math.e**(17.27*data/(data+237.3))
        else:
            ea = np.concatenate((ea,0.6108*math.e**(17.27*data/(data+237.3))))
        

















