# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 21:20:01 2024

@author: 33501

This code analyzes the average time required for LAI to drop to 0 after outlier processing following the onset of lightning drought, and
The minimum value of LAI after outlier processing during the lightning drought is influenced by both the dryness index and the tree coverage rate.
"""

import numpy as np
import xarray as xr
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
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

#Chinese regional mask
# shp = ogr.Open(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp")
# lyr = shp.GetLayer()
# driver = gdal.GetDriverByName('MEM')
# shp_ds_SM = driver.Create('', 273, 221, 1, gdal.GDT_UInt32)
# shp_ds_SM.SetProjection('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]')
# shp_ds_SM.SetGeoTransform((70,0.25,0,55,0,-0.25))
# options = ['ATTRIBUTE=gb']
# gdal.RasterizeLayer(shp_ds_SM, [1], lyr, options=options)
# cn_mask = shp_ds_SM.ReadAsArray().astype(np.int16)

#Obtain the mask
cn_mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()

#Obtain net radiation, potential evapotranspiration, precipitation, vegetation, and temperature data
sr = xr.open_dataset(r"D:\work\code\yuan\data\dry\sr_use.nc")['sr'].values
pev = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['pev'].values
tp = xr.open_dataset(r"D:\work\code\yuan\data\total_precipitation\tp.nc")['tp'].values
vc = xr.open_dataset(r"D:\work\code\yuan\data\Vegetation_Continuous_Fields\vc_mean.nc")['vc'].values
temp = xr.open_dataset(r"D:\work\code\yuan\data\2m_temperature\tem.nc")['tem'].values
lon = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lon'].values
lat = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lat'].values


#Obtain the data of the dryness index
dry_index = ra.open(r"D:\work\gee_\gee_download\yuan\test\dry.tif").read()[0]
dry_index = resample(dry_index,(221,273))
dry_index[dry_index>4]=np.nan
dry_index[cn_mask==0]=np.nan

#Calculate the tree coverage rate
tc_index = vc[0]/(vc[0]+vc[1])

#Combine the dryness index with the tree coverage rate
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

#drying index
arid = dry_index

#Calculate the tree coverage rate
tc_index = vc[0]/(vc[0]+vc[1])

#Package the calculation and plotting together into a function
def fun(path,key):
    #Obtain soil data
    path_head = r'D:\work\code\yuan\data\soil_moisture\Nc'
    data = xr.open_dataset(path_head + os.sep + r"swvl30_pentad.nc")
    time = data['time'].values
    lon = data['lon'].values
    lat = data['lat'].values
    pentad = data['pentad'].values
    S = (pentad-np.nanmean(pentad,axis=0))/np.nanstd(pentad,axis=0)
    
    #Obtain the weight data
    for year in range(2001,2024):
        quan_dataset = xr.open_dataset(f"D:/work/code/yuan/data/soil_moisture/Nc/quan/swvl_{year}_quan.nc")
        quan = quan_dataset['quan'].values
        if year == 2001:
            quans = quan.copy()
            continue
        quans = np.concatenate((quans,quan))

    #Obtain the LAI data and perform outlier processing
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
    
    #Similar to the flash drought identification code
    count_all = np.zeros(quans[0].shape)    #The number of droughts where LAI drops below 0
    t_all = np.zeros(quans[0].shape)    #The total time required for the LAI to drop below 0 during all periods of drought
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
        
        LAI_switch = np.zeros(mask.shape,dtype=bool) #LAI Statistical Switch
        LAI_switch[::] = False
        
        per_count = np.zeros(mask.shape,dtype=int)  #A count where the LAI value drops below 0
        
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
    
    #To eliminate the influence of extreme values, the 99th percentile is taken.
    LAI_min = np.percentile(LAI, 99,axis=0)
    
    #Obtain the average number of days required for LAI to drop below 0 and the influence matrix of dryness index - tree coverage
    pic = np.array([[np.nanmean(L_mean[(p_arr<14.5)&(p_arr>13.5)]),np.nanmean(L_mean[(p_arr<24.5)&(p_arr>23.5)]),np.nanmean(L_mean[(p_arr<34.5)&(p_arr>33.5)]),np.nanmean(L_mean[(p_arr<44.5)&(p_arr>43.5)])],
          [np.nanmean(L_mean[(p_arr<13.5)&(p_arr>12.5)]),np.nanmean(L_mean[(p_arr<23.5)&(p_arr>22.5)]),np.nanmean(L_mean[(p_arr<33.5)&(p_arr>32.5)]),np.nanmean(L_mean[(p_arr<43.5)&(p_arr>42.5)])],
          [np.nanmean(L_mean[(p_arr<12.5)&(p_arr>11.5)]),np.nanmean(L_mean[(p_arr<22.5)&(p_arr>21.5)]),np.nanmean(L_mean[(p_arr<32.5)&(p_arr>31.5)]),np.nanmean(L_mean[(p_arr<42.5)&(p_arr>41.5)])],
          [np.nanmean(L_mean[(p_arr<11.5)&(p_arr>10.5)]),np.nanmean(L_mean[(p_arr<21.5)&(p_arr>20.5)]),np.nanmean(L_mean[(p_arr<31.5)&(p_arr>30.5)]),np.nanmean(L_mean[(p_arr<41.5)&(p_arr>40.5)])]])
    
    #Obtain the minimum value of LAI and the influence matrix of dryness index - tree coverage
    pic_b = np.array([[np.nanmean(LAI_min[(p_arr<14.5)&(p_arr>13.5)]),np.nanmean(LAI_min[(p_arr<24.5)&(p_arr>23.5)]),np.nanmean(LAI_min[(p_arr<34.5)&(p_arr>33.5)]),np.nanmean(LAI_min[(p_arr<44.5)&(p_arr>43.5)])],
          [np.nanmean(LAI_min[(p_arr<13.5)&(p_arr>12.5)]),np.nanmean(LAI_min[(p_arr<23.5)&(p_arr>22.5)]),np.nanmean(LAI_min[(p_arr<33.5)&(p_arr>32.5)]),np.nanmean(LAI_min[(p_arr<43.5)&(p_arr>42.5)])],
          [np.nanmean(LAI_min[(p_arr<12.5)&(p_arr>11.5)]),np.nanmean(LAI_min[(p_arr<22.5)&(p_arr>21.5)]),np.nanmean(LAI_min[(p_arr<32.5)&(p_arr>31.5)]),np.nanmean(LAI_min[(p_arr<42.5)&(p_arr>41.5)])],
          [np.nanmean(LAI_min[(p_arr<11.5)&(p_arr>10.5)]),np.nanmean(LAI_min[(p_arr<21.5)&(p_arr>20.5)]),np.nanmean(LAI_min[(p_arr<31.5)&(p_arr>30.5)]),np.nanmean(LAI_min[(p_arr<41.5)&(p_arr>40.5)])]])
    
    #plot
    colors = ['#C74D26','#E38D26','#F1CC74','#F2F2F2','#A4C97C','#5F9C61','#2C6344']
    cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)
    colors2 = ['#D8412B','#FEE79A','#E7F6EB','#4A7BB7']
    cmap2 = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors2)
    def pth(label,pos):
        plt.text(pos,-0.6,label,size=30,ha='center',color='#A8A8A8')
        plt.text(pos-0.95,-0.65,'_'*(10-len(label)),size=30,color='#A8A8A8')
        plt.text(pos-0.95,-0.61,'|',size=12,color='#A8A8A8',va='center')
        plt.text(pos-0.955,-0.61,'|',size=12,color='#A8A8A8',va='center')
        plt.text(pos-0.96,-0.61,'|',size=12,color='#A8A8A8',va='center')
        plt.text(pos-0.965,-0.61,'|',size=12,color='#A8A8A8',va='center')
        plt.text(pos+0.9,-0.65,'_'*(10-len(label)),size=30,color='#A8A8A8',ha='right')
        plt.text(pos+0.9,-0.61,'|',size=12,color='#A8A8A8',va='center')
        plt.text(pos+0.895,-0.61,'|',size=12,color='#A8A8A8',va='center')
        plt.text(pos+0.89,-0.61,'|',size=12,color='#A8A8A8',va='center')
        plt.text(pos+0.885,-0.61,'|',size=12,color='#A8A8A8',va='center')
    
    def pts(label,pos):
        plt.text(3.64,pos,label,rotation=270,size=30,c='#A8A8A8',va='center',ha='center')
        plt.text(3.58,pos+0.9,'_',color='#A8A8A8',va='center',size=22)
        plt.text(3.58,pos+0.895,'_',color='#A8A8A8',va='center',size=22)
        plt.text(3.58,pos+0.89,'_',color='#A8A8A8',va='center',size=22)
        for i in range((20-len(label))//5):
            plt.text(3.59,pos+0.75-i*0.2,'|',size=30,va='top',color='#A8A8A8')
        plt.text(3.58,pos-1.015,'_',color='#A8A8A8',va='center',size=22)
        plt.text(3.58,pos-1.02,'_',color='#A8A8A8',va='center',size=22)
        plt.text(3.58,pos-1.025,'_',color='#A8A8A8',va='center',size=22)
        for i in range((20-len(label))//5):
            plt.text(3.59,pos-0.75+i*0.2,'|',size=30,va='bottom',color='#A8A8A8')
    
    fig = plt.figure(figsize=(25, 10))
    plt.axis('off')
    plt.text(0.47,1,path.split('\\')[-1].split('.')[0],size=50,ha='center',va='center')
    ax1 = fig.add_axes([0.05, 0.1, 0.45, 0.8])
    P_max = int(np.nanmax(pic))+1
    P_min = int(np.nanmin(pic))
    im1 = plt.imshow(pic,vmin=P_min,vmax=P_max,cmap=cmap2)
    jg_P = int((P_max-P_min)/4)
    if jg_P<1:
        jg_P=1
    cb1 = plt.colorbar(im1,ax=ax1,ticks=[i for i in range(P_min,P_max+1,jg_P)],pad=0.1)
    cb1.set_label('Timing',font={'size':35})
    
    cb1.ax.tick_params(labelsize=20)
    cb1.ax.spines['left'].set_linewidth(2)
    
    plt.xlabel('Dryness index[-]',{'fontsize':35})
    plt.xlim(-0.5,3.5)
    plt.xticks([-0.5,0.5,1.5,2.5,3.5],[0,0.5,1,2,4],size=20)
    plt.ylabel('Tree dominance[-]',{'fontsize':35})
    plt.ylim(3.5,-0.5)
    plt.yticks([-0.5,0.5,1.5,2.5,3.5],['1','.75','.50','.25','0'],size=20)
    
    pth('Humid',0.5)
    pth('Arid',2.5)
    pts('Short veg.',2.5)
    pts('Trees',0.5)
    
    ax1.spines[['left','bottom','top', 'right']].set_linewidth(2)
    ax1.tick_params(axis='both', which='major', width=2,length=10)
    
    ax2 = fig.add_axes([0.5, 0.1, 0.45, 0.8])
    B_max = int('%.0f'%(np.nanmax(pic_b)*10+1))/10
    B_min = int('%.0f'%(np.nanmin(pic_b)*10-1))/10
    im2 = plt.imshow(pic_b,vmin=B_min,vmax=B_max,cmap=cmap)
    jg_B = int((B_max-B_min)/4*10)
    cb2 = plt.colorbar(im2,ax=ax2,ticks=[i/10 for i in range(int(B_min*10),int(B_max*10)+1,jg_B)],pad=0.1)
    cb2.set_label('Intensity',font={'size':35})
    
    cb2.ax.tick_params(labelsize=20)
    cb2.ax.spines['left'].set_linewidth(2)
    
    plt.xlabel('Dryness index[-]',{'fontsize':35})
    plt.xlim(-0.5,3.5)
    plt.xticks([-0.5,0.5,1.5,2.5,3.5],[0,0.5,1,2,4],size=20)
    plt.ylim(3.5,-0.5)
    plt.yticks([-0.5,0.5,1.5,2.5,3.5],['1','.75','.50','.25','0'],size=20)
    
    pth('Humid',0.5)
    pth('Arid',2.5)
    pts('Short veg.',2.5)
    pts('Trees',0.5)
    
    ax2.spines[['left','bottom','top', 'right']].set_linewidth(2)
    ax2.tick_params(axis='both', which='major', width=2,length=10)
    fig.tight_layout()
    plt.show()
    
    # plt.savefig(f'D:\\work\\code\\yuan\\图\\flash_dry\\affect_{key}.tif',dpi=600)

fun(r"D:\work\code\yuan\data\LAI\LAI.nc",'LAI')
fun(r"D:\work\code\yuan\data\GPP\GPP.nc",'GPP')
fun(r"D:\work\code\yuan\data\PET\PET.nc",'PET')















