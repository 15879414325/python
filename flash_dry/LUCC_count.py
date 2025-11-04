# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 09:59:57 2025

@author: 33501
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
from scipy.interpolate import make_interp_spline
import pandas as pd
from dro_pic import *

warnings.filterwarnings("ignore")

def resample(array,target_shape):
    zoom_factors = [target_shape[i] / array.shape[i] for i in range(len(target_shape))]
    resampled_array = ndimage.zoom(array, zoom_factors, order=1)
    return resampled_array


path_head = r'D:\work\code\yuan\data\LUCC\count'

data = {}

for c in os.listdir(path_head):
    data[c[:-4]] = pd.read_csv(path_head+os.sep+c).loc[:,'1':]


vc = xr.open_dataset(r"D:\work\code\yuan\data\Vegetation_Continuous_Fields\vc_mean.nc")['vc'].values
arid = gdal.Open(r"D:\work\gee_\gee_download\yuan\test\dry.tif").ReadAsArray()
arid = resample(arid,(221,273))
tc_index = vc[0]/(vc[0]+vc[1])

LUCC_data = gdal.Open(r"D:\work\code\yuan\data\LUCC\LUCC.tif").ReadAsArray()

class_names = {1:'Forest',2:'Grassland',3:'Wetland',4:'Farmland',5:'Mixed Vegetation'}

class_pos = {1:(0,1),2:(0,8),3:(0,15),4:(10,1),5:(10,8)}

cl = 1

fig, ax = plt.subplots(figsize=(36, 12))


fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
plt.axis('off')
gs = gridspec.GridSpec(19,22)
pos = 4

oid = 96

for cl in range(1,6):

    fig.add_subplot(gs[class_pos[cl][0]:class_pos[cl][0]+8,class_pos[cl][1]:class_pos[cl][1]+6])
    
    plt.xlim(-5,20)
    plt.xticks([0,5,10,15,20],['drought\n starts',5,10,15,20],size=20)
    plt.xlabel('Time[pentad]',size=20,labelpad=-10)
    plt.ylabel('Normalized Value(Z-score)',size=20)
    
    
    plt.ylim(-2,2)
    plt.yticks([-2,-1,0,1,2],size=20)
    
    plt.text(11,-1.2,'DryIndex:%.2f'%np.nanmean(arid[LUCC_data==cl]),size=20)
    plt.text(11,-1.5,'TreeCover:%.2f'%np.nanmean(tc_index[LUCC_data==cl]),size=20)
    
    x_data = list(range(-5,21))
    
    win_size = 3

    
    S_smooth = np.convolve(data['S50'][str(cl)],np.ones(win_size)/win_size,mode="same")
    LAI_smooth = np.convolve(data['LAI50'][str(cl)],np.ones(win_size)/win_size,mode="same")
    GPP_smooth = np.convolve(data['GPP50'][str(cl)],np.ones(win_size)/win_size,mode="same")
    PET_smooth = np.convolve(data['PET50'][str(cl)],np.ones(win_size)/win_size,mode="same")
    S_south_data25 = np.convolve(data['S25'][str(cl)],np.ones(win_size)/win_size,mode="same")
    S_south_data75 = np.convolve(data['S75'][str(cl)],np.ones(win_size)/win_size,mode="same")
    
    plt.plot(x_data,S_smooth,c='black',lw=4,label='SM')
    plt.plot(x_data,LAI_smooth,c='#7DC69B',lw=4,label='LAI')
    plt.plot(x_data,GPP_smooth,c='#F2A1A7',lw=4,label='GPP')
    plt.plot(x_data,PET_smooth,c='#9BD7F3',lw=4,label='PET')
    plt.plot([-5,21],[0,0],color='black')
    
    plt.fill_between(x_data,S_south_data25,S_south_data75,alpha=0.1,color='black')

    plt.text(17,1.7,'LAI',c='#7DC69B',size=20)
    plt.text(17,1.1,'GPP',c='#F2A1A7',size=20)
    plt.text(17,1.4,'PET',c='#9BD7F3',size=20)
    plt.text(17,0.8,'SM',c='black',size=20)
    plt.text(-4.5,1.6,f'{chr(oid+cl)}.{class_names[cl]}',c='black',size=30,weight='bold')
    pos+=1



fig.add_subplot(gs[10:18,15:21])

plt.xlim(-5,20)
plt.xticks([0,5,10,15,20],['drought\n starts',5,10,15,20],size=20)
plt.xlabel('Time[pentad]',size=20,labelpad=-10)
plt.ylabel('Normalized Value(Z-score)',size=20)

plt.ylim(-2,2)
plt.yticks([-2,-1,0,1,2],size=20)

plt.plot([-5,21],[0,0],color='black')

plt.plot(x_data,LAI_all_data,c='#7DC69B',lw=4)
plt.plot(x_data,GPP_all_data,c='#F2A1A7',lw=4)
plt.plot(x_data,PET_all_data,c='#9BD7F3',lw=4)
plt.plot(x_data,S_all_data,c='black',lw=4)

plt.fill_between(x_data,S_all_data25,S_all_data75,alpha=0.1,color='black')

plt.text(11,-1.2,'DryIndex:%.2f'%arid_index_all,{'fontsize':20})
plt.text(11,-1.5,'TreeCover:%.2f'%VcT_index_all,{'fontsize':20})

plt.text(17,1.7,'LAI',c='#7DC69B',size=20)
plt.text(17,1.1,'GPP',c='#F2A1A7',size=20)
plt.text(17,1.4,'PET',c='#9BD7F3',size=20)
plt.text(17,0.8,'SM',c='black',size=20)
plt.text(-4.5,1.6,'f.Overall region',c='black',size=30,weight='bold')

plt.rcParams['font.sans-serif'] = ['Arial']


# plt.savefig(r"D:\work\code\yuan\图\flash_dry\LUCC_count2.tif",dpi=600)
