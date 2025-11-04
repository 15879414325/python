# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 09:21:00 2024

@author: 33501

This code analyzes the changes in LAI, GPP, and PET (after outlier processing) 
5 pentads before and 20 pentads after flash drought onset,
and compares them with soil moisture data, studying three regions: South, North, and Northeast China
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings
import os
from scipy import ndimage
from osgeo import gdal
import mpl_toolkits.axisartist as axisartist
import matplotlib.gridspec as gridspec
import pandas as pd
warnings.filterwarnings("ignore")

def resample(array,target_shape):
    zoom_factors = [target_shape[i] / array.shape[i] for i in range(len(target_shape))]
    resampled_array = ndimage.zoom(array, zoom_factors, order=1)
    return resampled_array


sr = xr.open_dataset(r"D:\work\code\yuan\data\dry\sr_use.nc")['sr'].values
pev = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['pev'].values
tp = xr.open_dataset(r"D:\work\code\yuan\data\total_precipitation\tp.nc")['tp'].values
vc = xr.open_dataset(r"D:\work\code\yuan\data\Vegetation_Continuous_Fields\vc_mean.nc")['vc'].values
temp_dataset = xr.open_dataset(r"D:\work\code\yuan\data\2m_temperature\tem.nc")['tem'].values
lon = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lon'].values
lat = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lat'].values

mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()

arid = gdal.Open(r"D:\work\gee_\gee_download\yuan\test\dry.tif").ReadAsArray()
arid = resample(arid,(221,273))
tc_index = vc[0]/(vc[0]+vc[1])


arid_index_south = np.nanmean(arid[92:137,112:213])
VcT_index_south = np.nanmean(tc_index[92:137,112:213])
arid_index_north = np.nanmean(arid[52:92,112:225])
VcT_index_north = np.nanmean(tc_index[52:92,112:225])
arid_index_northeast = np.nanmean(arid[12:52,196:261])
VcT_index_northeast = np.nanmean(tc_index[12:52,196:261])
arid_index_all = np.nanmean(arid[mask==1])
VcT_index_all = np.nanmean(tc_index[mask==1])


x_data = list(range(-5,21))


p1 = pd.read_csv(r"D:\work\code\yuan\data\LUCC\count_region\P1.csv")
p2 = pd.read_csv(r"D:\work\code\yuan\data\LUCC\count_region\P2.csv")
p3 = pd.read_csv(r"D:\work\code\yuan\data\LUCC\count_region\P3.csv")
p4 = pd.read_csv(r"D:\work\code\yuan\data\LUCC\count_region\P4.csv")

S_south_data = np.array(p1['S'])
S_north_data = np.array(p2['S'])
S_northeast_data = np.array(p3[['S']])
S_all_data = np.array(p4['S'])
S_south_data25 = np.array(p1['S25'])
S_south_data75 = np.array(p1['S75'])
S_north_data25 = np.array(p2['S25'])
S_north_data75 = np.array(p2['S75'])
S_northeast_data25 = np.array(p3['S25'])
S_northeast_data75 = np.array(p3['S75'])
S_all_data25 = np.array(p4['S25'])
S_all_data75 = np.array(p4['S75'])

LAI_south_data = np.array(p1['LAI'])
LAI_north_data = np.array(p2['LAI'])
LAI_northeast_data = np.array(p3['LAI'])
LAI_all_data = np.array(p4['LAI'])
LAI_all_data25 = np.array(p4['LAI25'])
LAI_all_data75 = np.array(p4['LAI75'])

GPP_south_data = np.array(p1['GPP'])
GPP_north_data = np.array(p2['GPP'])
GPP_northeast_data = np.array(p3['GPP'])
GPP_all_data = np.array(p4['GPP'])
GPP_all_data25 = np.array(p4['GPP25'])
GPP_all_data75 = np.array(p4['GPP75'])

PET_south_data = np.array(p2['PET'])
PET_north_data = np.array(p2['PET'])
PET_northeast_data = np.array(p3['PET'])
PET_all_data = np.array(p4['PET'])
PET_all_data25 = np.array(p4['PET25'])
PET_all_data75 = np.array(p4['PET75'])

fig, ax = plt.subplots(figsize=(24, 6))

fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)

plt.ylim((0,1))
plt.xlim((0,1))

plt.axis('off')

gs = gridspec.GridSpec(7,24)

fig.add_subplot(gs[0:6,17:24])

plt.xlim(-5,20)
plt.xticks([0,5,10,15,20],['drought\n starts',5,10,15,20],size=20)
plt.xlabel('Time[pentad]',size=20,labelpad=-10)
plt.ylabel('Normalized Value(Z-score)',size=20)

plt.ylim(-2,2)
plt.yticks([-2,-1,0,1,2],size=20)

plt.plot(x_data,S_south_data,c='black',lw=4,label='SM')
plt.plot(x_data,LAI_south_data,c='#7DC69B',lw=4,label='LAI')
plt.plot(x_data,GPP_south_data,c='#F2A1A7',lw=4,label='GPP')
plt.plot(x_data,PET_south_data,c='#9BD7F3',lw=4,label='PET')
plt.plot([-5,21],[0,0],color='black')

plt.text(11,-1.2,'DryIndex:%.2f'%arid_index_south,{'fontsize':20})
plt.text(11,-1.5,'TreeCover:%.2f'%VcT_index_south,{'fontsize':20})
plt.text(17,1.7,'LAI',c='#7DC69B',size=20)
plt.text(17,1.1,'GPP',c='#F2A1A7',size=20)
plt.text(17,1.4,'PET',c='#9BD7F3',size=20)
plt.text(17,0.8,'SM',c='black',size=20)
plt.text(-4.5,1.6,'c.South',c='black',size=30,weight='bold')


plt.fill_between(x_data,S_south_data25,S_south_data75,alpha=0.1,color='black')

fig.add_subplot(gs[0:6,9:16])

plt.xlim(-5,20)
plt.xticks([0,5,10,15,20],['drought\n starts',5,10,15,20],size=20)
plt.xlabel('Time[pentad]',size=20,labelpad=-10)
plt.ylabel('Normalized Value(Z-score)',size=20)

plt.ylim(-2,2)
plt.yticks([-2,-1,0,1,2],size=20)

plt.plot(x_data,S_north_data,c='black',lw=4)
plt.plot(x_data,LAI_north_data,c='#7DC69B',lw=4)
plt.plot(x_data,GPP_north_data,c='#F2A1A7',lw=4)
plt.plot(x_data,PET_north_data,c='#9BD7F3',lw=4)
plt.plot([-5,21],[0,0],color='black')

plt.text(11,-1.2,'DryIndex:%.2f'%arid_index_north,{'fontsize':20})
plt.text(11,-1.5,'TreeCover:%.2f'%VcT_index_north,{'fontsize':20})
plt.text(17,1.7,'LAI',c='#7DC69B',size=20)
plt.text(17,1.1,'GPP',c='#F2A1A7',size=20)
plt.text(17,1.4,'PET',c='#9BD7F3',size=20)
plt.text(17,0.8,'SM',c='black',size=20)
plt.text(-4.5,1.6,'b.North',c='black',size=30,weight='bold')

plt.fill_between(x_data,S_north_data25,S_north_data75,alpha=0.1,color='black')

fig.add_subplot(gs[0:6,1:8])

plt.xlim(-5,20)
plt.xticks([0,5,10,15,20],['drought\n starts',5,10,15,20],size=20)
plt.xlabel('Time[pentad]',size=20,labelpad=-10)
plt.ylabel('Normalized Value(Z-score)',size=20)

plt.ylim(-2,2)
plt.yticks([-2,-1,0,1,2],size=20)


plt.plot(x_data,S_northeast_data,c='black',lw=4)
plt.plot(x_data,LAI_northeast_data,c='#7DC69B',lw=4)
plt.plot(x_data,GPP_northeast_data,c='#F2A1A7',lw=4)
plt.plot(x_data,PET_northeast_data,c='#9BD7F3',lw=4)
plt.plot([-5,21],[0,0],color='black')

plt.text(11,-1.2,'DryIndex:%.2f'%arid_index_northeast,{'fontsize':20})
plt.text(11,-1.5,'TreeCover:%.2f'%VcT_index_northeast,{'fontsize':20})
plt.text(17,1.7,'LAI',c='#7DC69B',size=20)
plt.text(17,1.1,'GPP',c='#F2A1A7',size=20)
plt.text(17,1.4,'PET',c='#9BD7F3',size=20)
plt.text(17,0.8,'SM',c='black',size=20)
plt.text(-4.5,1.6,'a.Northeast',c='black',size=30,weight='bold')

plt.fill_between(x_data,S_northeast_data25,S_northeast_data75,alpha=0.1,color='black')


plt.rcParams['font.sans-serif'] = ['Arial']

# plt.savefig(r'D:\\work\\code\\yuan\\图\\flash_dry\\region_count2.tif',dpi=600)
