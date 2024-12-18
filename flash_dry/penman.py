# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 15:02:55 2024

@author: 33501

利用彭曼公式计算蒸散数据
"""

import math
import numpy as np
import os
import xarray as xa
from scipy import ndimage
from penman_data import ea

def resample(array,target_shape):
    zoom_factors = [target_shape[i] / array.shape[i] for i in range(len(target_shape))]
    resampled_array = ndimage.zoom(array, zoom_factors, order=1)
    return resampled_array

def e0(T):
    e = 0.6108*(math.e**( (17.27*T/(T+237.3))))
    return e

def PM_ET0(Tmax,Tmin,Tmean,ea,P,u2,Rn): 
    #Tmax、Tmin、Tmean为最高、最低、平均气温；Tdew为露点温度；P为本站气压;u2为2m风速;Rn为净辐射
    Tmean = 0.5*(Tmax+Tmin)
    #土壤热通量
    G = 0
    #饱和水汽压
    es = 0.5*( e0(Tmax)+e0(Tmin) )
    #实际水汽压
    # ea = ea
    #饱和水汽压曲线斜率
    delta = 4098*e0(Tmean)/( (Tmean+237.3)*(Tmean+237.3) )
    #湿度计常数
    r = 0.665*0.001*P
    # ET0 = ( 0.408*delta*(Rn-G) + r*900*u2*(es-ea)/(Tmean+273) )/( delta + r*(1 + 0.34*u2) )
    
    ET0_1 = 0.408 * delta * (Rn-G)
    ET0_2 = r * 900* u2 * (es-ea)/(Tmean+273)
    ET0_3 = delta + r * (1 + 0.34*u2)
    ET0 = (ET0_1 + ET0_2)/ET0_3
    
    return ET0

Tmax = xa.open_dataset(r"D:\work\code\yuan\data\tem\tmax.nc")['tmax'].values
Tmin = xa.open_dataset(r"D:\work\code\yuan\data\tem\tmin.nc")['tmin'].values
Tmean = xa.open_dataset(r"D:\work\code\yuan\data\2m_temperature\tem_penman.nc")['tem'].values
P = xa.open_dataset(r"D:\work\code\yuan\data\surface_pressure\00-23.nc")['sp'].values/1000
u2 = xa.open_dataset(r"D:\work\code\yuan\data\wind\wind.nc")['wind'].values
Rn = xa.open_dataset(r"D:\work\code\yuan\data\dry\sr.nc")['sr'].values

Tmax = resample(Tmax, Tmean.shape)
Tmin = resample(Tmin, Tmean.shape)
Tmean = Tmean-273.15
P = resample(P, Tmean.shape)
u2 = resample(u2, Tmean.shape)
Rn = resample(Rn, Tmean.shape)
ea = resample(ea, Tmean.shape)

lat = xa.open_dataset(r"D:\work\code\yuan\data\2m_temperature\tem_penman.nc")['lat'].values
lon = xa.open_dataset(r"D:\work\code\yuan\data\2m_temperature\tem_penman.nc")['lon'].values

ET0 = PM_ET0(Tmax,Tmin,Tmean,ea,P,u2,Rn)

ET0 = np.nanmean(ET0,axis=0)

nc_out = xa.Dataset({'pev':(['lat','lon'],ET0)},{'lat':lat,'lon':lon})

nc_out.to_netcdf(r'D:\work\code\yuan\data\pev_penman.nc')

# pev = abs(xa.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['pev'].values*1000)


# pev.variables








