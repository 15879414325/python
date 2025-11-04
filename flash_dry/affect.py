# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 21:20:01 2024

@author: 33501

This code analyzes:
1. The mean time required for LAI to drop to 0 after flash drought onset (after outlier processing)
2. The dual influence of aridity index and tree cover on the minimum LAI value during flash drought periods (after outlier processing)
"""

import numpy as np
import xarray as xr
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import Normalize
import cartopy.crs as ccrs
from osgeo import ogr,gdal
from cartopy.io.shapereader import Reader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import seaborn as sns
from scipy import ndimage
import rasterio as ra
import warnings
warnings.filterwarnings("ignore")

def resample(array,target_shape):   #Resampling function
    zoom_factors = [target_shape[i] / array.shape[i] for i in range(len(target_shape))]
    resampled_array = ndimage.zoom(array, zoom_factors, order=1)
    return resampled_array

#China region mask
# shp = ogr.Open(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp")
# lyr = shp.GetLayer()
# driver = gdal.GetDriverByName('MEM')
# shp_ds_SM = driver.Create('', 273, 221, 1, gdal.GDT_UInt32)
# shp_ds_SM.SetProjection('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]')
# shp_ds_SM.SetGeoTransform((70,0.25,0,55,0,-0.25))
# options = ['ATTRIBUTE=gb']
# gdal.RasterizeLayer(shp_ds_SM, [1], lyr, options=options)
# cn_mask = shp_ds_SM.ReadAsArray().astype(np.int16)

#Get mask
cn_mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()

#Get net radiation, potential evapotranspiration, precipitation, vegetation, temperature data
# sr = xr.open_dataset(r"D:\work\code\yuan\data\dry\sr_use.nc")['sr'].values
# pev = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['pev'].values
# tp = xr.open_dataset(r"D:\work\code\yuan\data\total_precipitation\tp.nc")['tp'].values
# temp = xr.open_dataset(r"D:\work\code\yuan\data\2m_temperature\tem.nc")['tem'].values

vc = xr.open_dataset(r"D:\work\code\yuan\data\Vegetation_Continuous_Fields\vc_mean.nc")['vc'].values

lon = xr.open_dataset(r"D:\work\code\yuan\data\Vegetation_Continuous_Fields\vc_mean.nc")['lon'].values
lat = xr.open_dataset(r"D:\work\code\yuan\data\Vegetation_Continuous_Fields\vc_mean.nc")['lat'].values


#Get aridity index data
dry_index = ra.open(r"D:\work\gee_\gee_download\yuan\test\dry.tif").read()[0]
dry_index = resample(dry_index,(221,273))
dry_index[dry_index>4]=np.nan
dry_index[cn_mask==0]=np.nan

#Calculate tree cover fraction
tc_index = vc[0]/(vc[0]+vc[1])

#Combine aridity index and tree cover
p_dry = np.zeros(dry_index.shape,dtype=float)
p_dry[::] = np.nan
p_dry[(dry_index>=0) & (dry_index<0.5)]=10
p_dry[(dry_index>=0.5) & (dry_index<1)]=20
p_dry[(dry_index>=1) & (dry_index<2)]=30
p_dry[(dry_index>=2) & (dry_index<=4)]=40

p_tc = np.zeros(tc_index.shape,dtype=float)
p_tc[::] = np.nan
p_tc[(tc_index>=0) & (tc_index<0.25)]=1
p_tc[(tc_index>=0.25) & (tc_index<0.5)]=2
p_tc[(tc_index>=0.5) & (tc_index<0.75)]=3
p_tc[(tc_index>=0.75) & (tc_index<=1)]=4

p_arr = p_dry+p_tc
p_arr[cn_mask==0]=np.nan

#Aridity index
arid = dry_index

#Calculate tree cover fraction
tc_index = vc[0]/(vc[0]+vc[1])

#Package calculation and plotting together as a function
def fun(path,key,ind):
    #Get soil data
    path_head = r'D:\work\code\yuan\data\soil_moisture\Nc\hist'
    data = xr.open_dataset(path_head + os.sep + r"swvl30_pentad.nc")
    time = data['time'].values
    lon = data['lon'].values
    lat = data['lat'].values
    pentad = data['pentad'].values
    S = (pentad-np.nanmean(pentad,axis=0))/np.nanstd(pentad,axis=0)
    
    LUCC_data = ra.open(r"D:\work\code\yuan\data\LUCC\LUCC.tif").read()[0]
    
    #Get weight data
    for year in range(2001,2024):
        quan_dataset = xr.open_dataset(path_head+f"/quan/swvl_{year}_quan.nc")
        quan = quan_dataset['quan'].values
        if year == 2001:
            quans = quan.copy()
            continue
        quans = np.concatenate((quans,quan))

    #Get LAI data and perform outlier processing
    LAI_dataset = xr.open_dataset(path)[key].values
    for year in range(23):
        if year ==0:
            LAI = LAI_dataset[year]
        else:
            LAI = np.concatenate((LAI,LAI_dataset[year]))
    std = np.nanstd(LAI,axis=0)
    LAI = (LAI-np.nanmean(LAI,axis=0))/std
    
    mask = np.empty((quans.shape[1],quans.shape[2]),dtype=int)
    mask[::] = 1
    mask[~(np.nanmean(quans,axis=0)>=0.01)]=0
    
    #Similar to flash drought identification code
    count_all = np.zeros(quans[0].shape)    #Number of droughts where LAI drops below 0
    t_all = np.zeros(quans[0].shape)    #Total time required for LAI to drop below 0 during all droughts
    dro_num = np.zeros(mask.shape,dtype=float)
    for year in range(0,quans.shape[0],73):
        arr = quans[year:year+73]
        LAI_arr = LAI[year:year+73]
        count = np.zeros(mask.shape,dtype=int)
        switch = np.empty(mask.shape,dtype=bool)
        switch[::] = False
        st_switch = np.empty(mask.shape,dtype=bool)
        st_switch[::] = False
        st_count = np.zeros(mask.shape,dtype=int)
        ed_switch = np.empty(mask.shape,dtype=bool)
        ed_switch[::] = False
        ed_count = np.zeros(mask.shape,dtype=int)
        
        LAI_switch = np.zeros(mask.shape,dtype=bool) #LAI statistics switch
        LAI_switch[::] = False
        
        per_count = np.zeros(mask.shape,dtype=int)  #Counter for single LAI drop below 0
        
        for i in range(73):
            st_switch[st_count>5]=False
            st_count[(~st_switch)]=0
            ed_count[switch & ed_switch]=-3
            ed_switch[(arr[i]>=0.2) & switch]=True
            ed_switch[(arr[i]<0.2) & switch]=False
            ed_count[(arr[i]<0.2) & switch]=0
            st_switch[arr[i]>=0.4]=True
            st_count[(arr[i]>=0.4)]=0
            st_count[st_switch]+=1
            ed_count[ed_switch]+=1
            switch[(ed_count==-2) & (ed_switch)] = False
            count[(ed_count==-2) & (ed_switch)]-=1
            dro_num[(count>=6) & (count<=18) & (ed_count==-2) & (ed_switch)]+=count[(count>=6) & (count<=18) & (ed_count==-2) & (ed_switch)]
            count_all[(count>=6) & (count<=18) & (ed_count==-2) & (ed_switch)&(per_count<count)&(per_count!=0)]+=1
            t_all[(count>=6) & (count<=18) & (ed_count==-2) & (ed_switch)&(per_count<count)&(per_count!=0)]+=per_count[(count>=6) & (count<=18) & (ed_count==-2) & (ed_switch)&(per_count<count)&(per_count!=0)]
            LAI_switch[(ed_count==-2) & (ed_switch)] = False
            per_count[(ed_count==-2) & (ed_switch)]=0
            count[(ed_count==-2) & (ed_switch)] = 0
            ed_switch[(ed_count==-2) & (ed_switch)] = False
            ed_count[(ed_count==-2) & (ed_switch)] = 0
            switch[(arr[i]<0.2) & (st_switch)]=True
            LAI_switch[(arr[i]<0.2) & (st_switch)]=True
            LAI_switch[LAI_arr[i]<0]=False
            per_count[LAI_switch] +=1
            st_switch[(arr[i]<0.2) & (st_switch)]=False
            count[switch & (~np.isnan(arr[i]))]+=1
    L_mean = t_all/count_all
    L_mean[np.isnan(p_arr)]=np.nan
    
    #To exclude extreme values, take the 99th percentile
    # LAI_min = np.nanpercentile(LAI, 99,axis=0)
    LAI_min = np.nanmin(LAI,axis=0)
    #Get mean days for LAI to drop below 0 and aridity index-tree cover influence matrix
    pic = np.array([[np.nanmean(L_mean[(p_arr<14.5)&(p_arr>13.5)]),np.nanmean(L_mean[(p_arr<24.5)&(p_arr>23.5)]),np.nanmean(L_mean[(p_arr<34.5)&(p_arr>33.5)]),np.nanmean(L_mean[(p_arr<44.5)&(p_arr>43.5)])],
          [np.nanmean(L_mean[(p_arr<13.5)&(p_arr>12.5)]),np.nanmean(L_mean[(p_arr<23.5)&(p_arr>22.5)]),np.nanmean(L_mean[(p_arr<33.5)&(p_arr>32.5)]),np.nanmean(L_mean[(p_arr<43.5)&(p_arr>42.5)])],
          [np.nanmean(L_mean[(p_arr<12.5)&(p_arr>11.5)]),np.nanmean(L_mean[(p_arr<22.5)&(p_arr>21.5)]),np.nanmean(L_mean[(p_arr<32.5)&(p_arr>31.5)]),np.nanmean(L_mean[(p_arr<42.5)&(p_arr>41.5)])],
          [np.nanmean(L_mean[(p_arr<11.5)&(p_arr>10.5)]),np.nanmean(L_mean[(p_arr<21.5)&(p_arr>20.5)]),np.nanmean(L_mean[(p_arr<31.5)&(p_arr>30.5)]),np.nanmean(L_mean[(p_arr<41.5)&(p_arr>40.5)])]])
    
    #Get LAI minimum and aridity index-tree cover influence matrix
    pic_b = np.array([[np.nanmean(LAI_min[(p_arr<14.5)&(p_arr>13.5)]),np.nanmean(LAI_min[(p_arr<24.5)&(p_arr>23.5)]),np.nanmean(LAI_min[(p_arr<34.5)&(p_arr>33.5)]),np.nanmean(LAI_min[(p_arr<44.5)&(p_arr>43.5)])],
          [np.nanmean(LAI_min[(p_arr<13.5)&(p_arr>12.5)]),np.nanmean(LAI_min[(p_arr<23.5)&(p_arr>22.5)]),np.nanmean(LAI_min[(p_arr<33.5)&(p_arr>32.5)]),np.nanmean(LAI_min[(p_arr<43.5)&(p_arr>42.5)])],
          [np.nanmean(LAI_min[(p_arr<12.5)&(p_arr>11.5)]),np.nanmean(LAI_min[(p_arr<22.5)&(p_arr>21.5)]),np.nanmean(LAI_min[(p_arr<32.5)&(p_arr>31.5)]),np.nanmean(LAI_min[(p_arr<42.5)&(p_arr>41.5)])],
          [np.nanmean(LAI_min[(p_arr<11.5)&(p_arr>10.5)]),np.nanmean(LAI_min[(p_arr<21.5)&(p_arr>20.5)]),np.nanmean(LAI_min[(p_arr<31.5)&(p_arr>30.5)]),np.nanmean(LAI_min[(p_arr<41.5)&(p_arr>40.5)])]])
    
    p_south = p_arr[92:137,112:213]
    L_mean_south = L_mean[92:137,112:213]
    L_min_south = LAI_min[92:137,112:213]
    pic_south = np.array([[np.nanmean(L_mean_south[(p_south<14.5)&(p_south>13.5)]),np.nanmean(L_mean_south[(p_south<24.5)&(p_south>23.5)]),np.nanmean(L_mean_south[(p_south<34.5)&(p_south>33.5)]),np.nanmean(L_mean_south[(p_south<44.5)&(p_south>43.5)])],
          [np.nanmean(L_mean_south[(p_south<13.5)&(p_south>12.5)]),np.nanmean(L_mean_south[(p_south<23.5)&(p_south>22.5)]),np.nanmean(L_mean_south[(p_south<33.5)&(p_south>32.5)]),np.nanmean(L_mean_south[(p_south<43.5)&(p_south>42.5)])],
          [np.nanmean(L_mean_south[(p_south<12.5)&(p_south>11.5)]),np.nanmean(L_mean_south[(p_south<22.5)&(p_south>21.5)]),np.nanmean(L_mean_south[(p_south<32.5)&(p_south>31.5)]),np.nanmean(L_mean_south[(p_south<42.5)&(p_south>41.5)])],
          [np.nanmean(L_mean_south[(p_south<11.5)&(p_south>10.5)]),np.nanmean(L_mean_south[(p_south<21.5)&(p_south>20.5)]),np.nanmean(L_mean_south[(p_south<31.5)&(p_south>30.5)]),np.nanmean(L_mean_south[(p_south<41.5)&(p_south>40.5)])]])

    pic_b_south = np.array([[np.nanmean(L_min_south[(p_south<14.5)&(p_south>13.5)]),np.nanmean(L_min_south[(p_south<24.5)&(p_south>23.5)]),np.nanmean(L_min_south[(p_south<34.5)&(p_south>33.5)]),np.nanmean(L_min_south[(p_south<44.5)&(p_south>43.5)])],
          [np.nanmean(L_min_south[(p_south<13.5)&(p_south>12.5)]),np.nanmean(L_min_south[(p_south<23.5)&(p_south>22.5)]),np.nanmean(L_min_south[(p_south<33.5)&(p_south>32.5)]),np.nanmean(L_min_south[(p_south<43.5)&(p_south>42.5)])],
          [np.nanmean(L_min_south[(p_south<12.5)&(p_south>11.5)]),np.nanmean(L_min_south[(p_south<22.5)&(p_south>21.5)]),np.nanmean(L_min_south[(p_south<32.5)&(p_south>31.5)]),np.nanmean(L_min_south[(p_south<42.5)&(p_south>41.5)])],
          [np.nanmean(L_min_south[(p_south<11.5)&(p_south>10.5)]),np.nanmean(L_min_south[(p_south<21.5)&(p_south>20.5)]),np.nanmean(L_min_south[(p_south<31.5)&(p_south>30.5)]),np.nanmean(L_min_south[(p_south<41.5)&(p_south>40.5)])]])


    p_north = p_arr[52:92,112:225]
    L_mean_north = L_mean[52:92,112:225]
    L_min_north = LAI_min[52:92,112:225]
    pic_north = np.array([[np.nanmean(L_mean_north[(p_north<14.5)&(p_north>13.5)]),np.nanmean(L_mean_north[(p_north<24.5)&(p_north>23.5)]),np.nanmean(L_mean_north[(p_north<34.5)&(p_north>33.5)]),np.nanmean(L_mean_north[(p_north<44.5)&(p_north>43.5)])],
          [np.nanmean(L_mean_north[(p_north<13.5)&(p_north>12.5)]),np.nanmean(L_mean_north[(p_north<23.5)&(p_north>22.5)]),np.nanmean(L_mean_north[(p_north<33.5)&(p_north>32.5)]),np.nanmean(L_mean_north[(p_north<43.5)&(p_north>42.5)])],
          [np.nanmean(L_mean_north[(p_north<12.5)&(p_north>11.5)]),np.nanmean(L_mean_north[(p_north<22.5)&(p_north>21.5)]),np.nanmean(L_mean_north[(p_north<32.5)&(p_north>31.5)]),np.nanmean(L_mean_north[(p_north<42.5)&(p_north>41.5)])],
          [np.nanmean(L_mean_north[(p_north<11.5)&(p_north>10.5)]),np.nanmean(L_mean_north[(p_north<21.5)&(p_north>20.5)]),np.nanmean(L_mean_north[(p_north<31.5)&(p_north>30.5)]),np.nanmean(L_mean_north[(p_north<41.5)&(p_north>40.5)])]])

    pic_b_north = np.array([[np.nanmean(L_min_north[(p_north<14.5)&(p_north>13.5)]),np.nanmean(L_min_north[(p_north<24.5)&(p_north>23.5)]),np.nanmean(L_min_north[(p_north<34.5)&(p_north>33.5)]),np.nanmean(L_min_north[(p_north<44.5)&(p_north>43.5)])],
          [np.nanmean(L_min_north[(p_north<13.5)&(p_north>12.5)]),np.nanmean(L_min_north[(p_north<23.5)&(p_north>22.5)]),np.nanmean(L_min_north[(p_north<33.5)&(p_north>32.5)]),np.nanmean(L_min_north[(p_north<43.5)&(p_north>42.5)])],
          [np.nanmean(L_min_north[(p_north<12.5)&(p_north>11.5)]),np.nanmean(L_min_north[(p_north<22.5)&(p_north>21.5)]),np.nanmean(L_min_north[(p_north<32.5)&(p_north>31.5)]),np.nanmean(L_min_north[(p_north<42.5)&(p_north>41.5)])],
          [np.nanmean(L_min_north[(p_north<11.5)&(p_north>10.5)]),np.nanmean(L_min_north[(p_north<21.5)&(p_north>20.5)]),np.nanmean(L_min_north[(p_north<31.5)&(p_north>30.5)]),np.nanmean(L_min_north[(p_north<41.5)&(p_north>40.5)])]])


    p_northeast = p_arr[12:52,196:261]
    L_mean_northeast = L_mean[12:52,196:261]
    L_min_northeast = LAI_min[12:52,196:261]
    pic_northeast = np.array([[np.nanmean(L_mean_northeast[(p_northeast<14.5)&(p_northeast>13.5)]),np.nanmean(L_mean_northeast[(p_northeast<24.5)&(p_northeast>23.5)]),np.nanmean(L_mean_northeast[(p_northeast<34.5)&(p_northeast>33.5)]),np.nanmean(L_mean_northeast[(p_northeast<44.5)&(p_northeast>43.5)])],
          [np.nanmean(L_mean_northeast[(p_northeast<13.5)&(p_northeast>12.5)]),np.nanmean(L_mean_northeast[(p_northeast<23.5)&(p_northeast>22.5)]),np.nanmean(L_mean_northeast[(p_northeast<33.5)&(p_northeast>32.5)]),np.nanmean(L_mean_northeast[(p_northeast<43.5)&(p_northeast>42.5)])],
          [np.nanmean(L_mean_northeast[(p_northeast<12.5)&(p_northeast>11.5)]),np.nanmean(L_mean_northeast[(p_northeast<22.5)&(p_northeast>21.5)]),np.nanmean(L_mean_northeast[(p_northeast<32.5)&(p_northeast>31.5)]),np.nanmean(L_mean_northeast[(p_northeast<42.5)&(p_northeast>41.5)])],
          [np.nanmean(L_mean_northeast[(p_northeast<11.5)&(p_northeast>10.5)]),np.nanmean(L_mean_northeast[(p_northeast<21.5)&(p_northeast>20.5)]),np.nanmean(L_mean_northeast[(p_northeast<31.5)&(p_northeast>30.5)]),np.nanmean(L_mean_northeast[(p_northeast<41.5)&(p_northeast>40.5)])]])

    pic_b_northeast = np.array([[np.nanmean(L_min_northeast[(p_northeast<14.5)&(p_northeast>13.5)]),np.nanmean(L_min_northeast[(p_northeast<24.5)&(p_northeast>23.5)]),np.nanmean(L_min_northeast[(p_northeast<34.5)&(p_northeast>33.5)]),np.nanmean(L_min_northeast[(p_northeast<44.5)&(p_northeast>43.5)])],
          [np.nanmean(L_min_northeast[(p_northeast<13.5)&(p_northeast>12.5)]),np.nanmean(L_min_northeast[(p_northeast<23.5)&(p_northeast>22.5)]),np.nanmean(L_min_northeast[(p_northeast<33.5)&(p_northeast>32.5)]),np.nanmean(L_min_northeast[(p_northeast<43.5)&(p_northeast>42.5)])],
          [np.nanmean(L_min_northeast[(p_northeast<12.5)&(p_northeast>11.5)]),np.nanmean(L_min_northeast[(p_northeast<22.5)&(p_northeast>21.5)]),np.nanmean(L_min_northeast[(p_northeast<32.5)&(p_northeast>31.5)]),np.nanmean(L_min_northeast[(p_northeast<42.5)&(p_northeast>41.5)])],
          [np.nanmean(L_min_northeast[(p_northeast<11.5)&(p_northeast>10.5)]),np.nanmean(L_min_northeast[(p_northeast<21.5)&(p_northeast>20.5)]),np.nanmean(L_min_northeast[(p_northeast<31.5)&(p_northeast>30.5)]),np.nanmean(L_min_northeast[(p_northeast<41.5)&(p_northeast>40.5)])]])
    
    dic = {}
    for cl in range(1,6):
        dic[cl] = []
        dic[cl] += [np.array([[np.nanmean(L_mean[(p_arr<14.5)&(p_arr>13.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<24.5)&(p_arr>23.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<34.5)&(p_arr>33.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<44.5)&(p_arr>43.5)&(LUCC_data==cl)])],
              [np.nanmean(L_mean[(p_arr<13.5)&(p_arr>12.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<23.5)&(p_arr>22.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<33.5)&(p_arr>32.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<43.5)&(p_arr>42.5)&(LUCC_data==cl)])],
              [np.nanmean(L_mean[(p_arr<12.5)&(p_arr>11.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<22.5)&(p_arr>21.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<32.5)&(p_arr>31.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<42.5)&(p_arr>41.5)&(LUCC_data==cl)])],
              [np.nanmean(L_mean[(p_arr<11.5)&(p_arr>10.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<21.5)&(p_arr>20.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<31.5)&(p_arr>30.5)&(LUCC_data==cl)]),np.nanmean(L_mean[(p_arr<41.5)&(p_arr>40.5)&(LUCC_data==cl)])]])]
        dic[cl] += [np.array([[np.nanmean(LAI_min[(p_arr<14.5)&(p_arr>13.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<24.5)&(p_arr>23.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<34.5)&(p_arr>33.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<44.5)&(p_arr>43.5)&(LUCC_data==cl)])],
              [np.nanmean(LAI_min[(p_arr<13.5)&(p_arr>12.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<23.5)&(p_arr>22.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<33.5)&(p_arr>32.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<43.5)&(p_arr>42.5)&(LUCC_data==cl)])],
              [np.nanmean(LAI_min[(p_arr<12.5)&(p_arr>11.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<22.5)&(p_arr>21.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<32.5)&(p_arr>31.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<42.5)&(p_arr>41.5)&(LUCC_data==cl)])],
              [np.nanmean(LAI_min[(p_arr<11.5)&(p_arr>10.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<21.5)&(p_arr>20.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<31.5)&(p_arr>30.5)&(LUCC_data==cl)]),np.nanmean(LAI_min[(p_arr<41.5)&(p_arr>40.5)&(LUCC_data==cl)])]])]
    
    #Plotting
    def plot_image(pic,pic_b,area):
        colors = ['#090991','#15209e','#192fa8','#2049ba','#205ec9','#3d90e3','#5ca3e6','#9fd8ed','#b6edf0']
        cmap2 = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)
        colors2 = ['#db0804','#ffcccc']
        cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors2)
        
        def pth(label,pos):
                plt.text(pos,-0.6,label,size=18,ha='center',color='#A8A8A8')
            
        def pts(label,pos):
                plt.text(3.7,pos,label,rotation=270,size=18,c='#A8A8A8',va='center',ha='center')
        
        ax1 = fig.add_axes([0.05, 0.1+0.31*ind, 0.45, 0.22], fc='#FFFFFF')
        P_max = int(np.nanmax(pic))
        P_min = int(np.nanmin(pic))
        im1 = plt.imshow(pic,vmin=P_min,vmax=P_max,cmap=cmap2)
        jg_P = int((P_max-P_min)/4)
        if jg_P<1:
            jg_P=1
        # cb1 = plt.colorbar(im1,ax=ax1,ticks=[i for i in range(P_min,P_max+1,jg_P)],pad=0.1,reposition=True)
        cb1 = plt.colorbar(im1,ax=ax1,ticks=[i for i in range(P_min,P_max+1,jg_P)],pad=0.1)
        cb1.set_label('Timing',font={'size':20})
        
        cb1.ax.tick_params(labelsize=12)
        cb1.ax.spines['left'].set_linewidth(2)
        
        plt.xlabel('Dryness index[-]',{'fontsize':20})
        plt.xlim(-0.5,3.5)
        plt.xticks([-0.5,0.5,1.5,2.5,3.5],[0,0.5,1,2,4],size=12)
        plt.ylabel('Tree dominance[-]',{'fontsize':20})
        plt.ylim(3.5,-0.5)
        plt.yticks([-0.5,0.5,1.5,2.5,3.5],['1','.75','.50','.25','0'],size=12)
        
        pth('Humid',0.5)
        pth('Arid',2.5)
        pts('Short veg.',2.5)
        pts('Trees',0.5)
        
        ax1.spines[['left','bottom','top', 'right']].set_linewidth(2)
        ax1.tick_params(axis='both', which='major', width=2,length=10)
        
        # ax2 = fig.add_axes([0.5, 0.1, 0.45, 0.8], fc='#FFFFFF')
        ax2 = fig.add_axes([0.5, 0.1+0.31*ind, 0.45, 0.22], fc='#FFFFFF')
        B_max = int('%.0f'%(np.nanmax(pic_b)*10+1))/10
        B_min = int('%.0f'%(np.nanmin(pic_b)*10-1))/10
        im2 = plt.imshow(pic_b,vmin=B_min,vmax=B_max,cmap=cmap)
        # jg_B = int((B_max-B_min)/4*10)
        if (key=='PET') and (area=='northeast'):
            jg_B = 1
        else:
            jg_B = int((B_max*10-B_min*10)/40*10)
        # cb2 = plt.colorbar(im2,ax=ax2,ticks=[i/10 for i in range(int(B_min*10),int(B_max*10)+1,jg_B)],pad=0.1,reposition=True)
        cb2 = plt.colorbar(im2,ax=ax2,ticks=[i/10 for i in range(int(B_min*10),int(B_max*10)+1,jg_B)],pad=0.1)
        cb2.set_label('Intensity',font={'size':20})
        
        cb2.ax.tick_params(labelsize=12)
        cb2.ax.spines['left'].set_linewidth(2)
        
        plt.xlabel('Dryness index[-]',{'fontsize':20})
        plt.xlim(-0.5,3.5)
        plt.xticks([-0.5,0.5,1.5,2.5,3.5],[0,0.5,1,2,4],size=12)
        plt.ylim(3.5,-0.5)
        plt.yticks([-0.5,0.5,1.5,2.5,3.5],['1','.75','.50','.25','0'],size=12)
        
        pth('Humid',0.5)
        pth('Arid',2.5)
        pts('Short veg.',2.5)
        pts('Trees',0.5)
        
        ax2.spines[['left','bottom','top', 'right']].set_linewidth(2)
        ax2.tick_params(axis='both', which='major', width=2,length=10)
        fig.tight_layout()
        plt.show()
        # plt.rcParams['font.sans-serif'] = ['Arial']
        # plt.savefig(f'D:\\work\\code\\yuan\\图\\flash_dry\\affect_{key}_{area}.tif',dpi=600)
    plot_image(pic,pic_b,'total')
    # plot_image(pic_south,pic_b_south,'south')
    # plot_image(pic_north,pic_b_north,'north')
    # plot_image(pic_northeast,pic_b_northeast,'northeast')
    # for cl in range(1,6):
    #     plot_image(dic[cl][0],dic[cl][1],str(cl))

fig = plt.figure(figsize=(11, 30))

fun(r"D:\work\code\yuan\data\LAI.nc",'LAI',2)
fun(r"D:\work\code\yuan\data\GPP.nc",'GPP',0)
fun(r"D:\work\code\yuan\data\PET.nc",'PET',1)

ax = fig.add_axes([0,0,1,1])
plt.axis('off')
plt.ylim((0,1))
plt.xlim((0,1))
plt.text(0.47,0.975,'LAI',size=25,ha='center',va='center',weight='bold')
plt.text(0.47,0.365,'GPP',size=25,ha='center',va='center',weight='bold')
plt.text(0.47,0.67,'PET',size=25,ha='center',va='center',weight='bold')

t = 97

for y in range(3):
    for x in range(2):
        plt.hlines(0.946-y*0.31, 0.081+x*0.45, 0.122+x*0.45, colors='#A8A8A8')
        plt.hlines(0.946-y*0.31, 0.195+x*0.45, 0.234+x*0.45, colors='#A8A8A8')
        plt.hlines(0.946-y*0.31, 0.238+x*0.45, 0.289+x*0.45, colors='#A8A8A8')
        plt.hlines(0.946-y*0.31, 0.331+x*0.45, 0.386+x*0.45, colors='#A8A8A8')
        plt.vlines(0.081+x*0.45, 0.942-y*0.31, 0.95-y*0.31, colors='#A8A8A8')
        plt.vlines(0.234+x*0.45, 0.942-y*0.31, 0.95-y*0.31, colors='#A8A8A8')
        plt.vlines(0.238+x*0.45, 0.942-y*0.31, 0.95-y*0.31, colors='#A8A8A8')
        plt.vlines(0.386+x*0.45, 0.942-y*0.31, 0.95-y*0.31, colors='#A8A8A8')
        
        plt.vlines(0.399+x*0.45, 0.94-y*0.31, 0.905-y*0.31, colors='#A8A8A8')
        plt.vlines(0.399+x*0.45, 0.863-y*0.31, 0.832-y*0.31, colors='#A8A8A8')
        plt.vlines(0.399+x*0.45, 0.828-y*0.31, 0.812-y*0.31, colors='#A8A8A8')
        plt.vlines(0.399+x*0.45, 0.736-y*0.31, 0.72-y*0.31, colors='#A8A8A8')
        plt.hlines(0.94-y*0.31, 0.393+x*0.45, 0.405+x*0.45, colors='#A8A8A8')
        plt.hlines(0.832-y*0.31, 0.393+x*0.45, 0.405+x*0.45, colors='#A8A8A8')
        plt.hlines(0.828-y*0.31, 0.393+x*0.45, 0.405+x*0.45, colors='#A8A8A8')
        plt.hlines(0.72-y*0.31, 0.393+x*0.45, 0.405+x*0.45, colors='#A8A8A8')

        plt.text(0.06+x*0.45,0.96-y*0.31,f'{chr(t)}.',size=25,ha='center',va='center',weight='bold')
        t+=1

plt.rcParams['font.sans-serif'] = ['Arial']

# plt.savefig(r"D:\work\code\yuan\图\flash_dry\affect.tif",dpi=600)
