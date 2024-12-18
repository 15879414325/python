# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 09:21:00 2024

@author: 33501

此代码分析闪电干旱开始前 5 pentad 和 开始后 20 pentad 异常值处理后LAI、GPP、PET变化情况，
并于土壤湿度数据进行对比，研究分南方、北方、东北三个地区
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings
import os
import rasterio as ra
from scipy import ndimage
from osgeo import gdal
# import prep_quan
warnings.filterwarnings("ignore")

def resample(array,target_shape):
    zoom_factors = [target_shape[i] / array.shape[i] for i in range(len(target_shape))]
    resampled_array = ndimage.zoom(array, zoom_factors, order=1)
    return resampled_array

#绘图函数
def plt_dro(lst_index,lst_S,arid_index,VcT_index,title):
    south_y = []
    south25 = []
    south75 = []
    for i in range(len(lst_index)):
        a = np.array(lst_index[i])
        south_y.append(np.nanpercentile(a, 50))
        south25.append(np.nanpercentile(a, 25))
        south75.append(np.nanpercentile(a, 75))
    
    S_south_y = []
    S_south25 = []
    S_south75 = []
    for i in range(len(lst_S)):
        a = np.array(lst_S[i])
        S_south_y.append(np.nanpercentile(a, 50))
        S_south25.append(np.nanpercentile(a, 25))
        S_south75.append(np.nanpercentile(a, 75))
    data = np.where(np.array(S_south_y)==np.min(np.array(S_south_y)))
    print((title,(S_south_y[data[0][0]+6]-S_south_y[data[0][0]])/6))
    # fig, ax = plt.subplots(figsize=(16,12))
    x = list(range(-5,21))

    plt.plot([-5,21],[0,0],color='black')
    plt.plot(x,south_y,color='g',linewidth=2.5)
    plt.plot(x,S_south_y,color='black',linewidth=2.5)

    plt.fill_between(x,south25,south75,alpha=0.1,color='g')
    plt.fill_between(x,S_south25,S_south75,alpha=0.1,color='black')
    
    plt.xlim(-5,20)
    plt.xticks([0,5,10,15,20],['drought\n starts',5,10,15,20],size=10)
    plt.xlabel('Time[pentad]',size=15)

    if 'PET' in title:
        plt.ylim(-4,2)
        plt.yticks([-4,-3,-2,-1,0,1,2],size=10)
        plt.text(11,-2.4,'DryIndex:%.2f'%arid_index,{'fontsize':15})
        plt.text(11,-2.7,'TreeCover:%.2f'%VcT_index,{'fontsize':15})
    else:
        plt.ylim(-2,1)
        plt.yticks([-2,-1,0,1],size=10)
        plt.text(11,-1.2,'DryIndex:%.2f'%arid_index,{'fontsize':15})
        plt.text(11,-1.35,'TreeCover:%.2f'%VcT_index,{'fontsize':15})
    
    plt.ylabel('Norm,Anomaly',size=15)
    plt.title(title,size=15,weight='bold')
    plt.tight_layout()
    # plt.savefig(f'D:\\work\\code\\yuan\\图\\flash_dry\\dro_{title}.tif',dpi=600)


sr = xr.open_dataset(r"D:\work\code\yuan\data\dry\sr_use.nc")['sr'].values
pev = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['pev'].values
tp = xr.open_dataset(r"D:\work\code\yuan\data\total_precipitation\tp.nc")['tp'].values
vc = xr.open_dataset(r"D:\work\code\yuan\data\Vegetation_Continuous_Fields\vc_mean.nc")['vc'].values
temp_dataset = xr.open_dataset(r"D:\work\code\yuan\data\2m_temperature\tem.nc")['tem'].values
lon = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lon'].values
lat = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lat'].values

mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()

arid = ra.open(r"D:\work\gee_\gee_download\yuan\test\dry.tif").read()[0]
arid = resample(arid,(221,273))
tc_index = vc[0]/(vc[0]+vc[1])

#获取各个区域土壤数据
path_head = r'D:\work\code\yuan\data\soil_moisture\Nc'
data = xr.open_dataset(path_head + os.sep + r"swvl30_pentad.nc")
time = data['time'].values
lon = data['lon'].values
lat = data['lat'].values
pentad = data['pentad'].values
S = (pentad-np.nanmean(pentad,axis=0))/np.nanstd(pentad,axis=0)
S_south_data = S[:,92:137,112:213]
S_north_data = S[:,52:92,112:225]
S_northeast_data = S[:,12:52,196:261]


#获取各个区域LAI数据，并进行异常值处理
LAI_dataset = xr.open_dataset(r"D:\work\code\yuan\data\LAI\LAI.nc")['LAI'].values
for year in range(20):
    if year ==0:
        LAI = LAI_dataset[year]
    else:
        LAI = np.concatenate((LAI,LAI_dataset[year]))
LAI = (LAI-np.nanmean(LAI,axis=0))/np.nanstd(LAI,axis=0)
LAI[np.array([mask for i in range(LAI.shape[0])])==0]=np.nan
LAI_south_data = LAI[:,92:137,112:213]
LAI_north_data = LAI[:,52:92,112:225]
LAI_northeast_data = LAI[:,12:52,196:261]

#获取各个区域GPP数据，并进行异常值处理
GPP_dataset = xr.open_dataset(r"D:\work\code\yuan\data\GPP\GPP.nc")['GPP'].values
for year in range(20):
    if year ==0:
        GPP = GPP_dataset[year]
    else:
        GPP = np.concatenate((GPP,GPP_dataset[year]))
GPP/=10000
GPP = (GPP-np.nanmean(GPP,axis=0))/np.nanstd(GPP,axis=0)
GPP[np.array([mask for i in range(LAI.shape[0])])==0]=np.nan
GPP_south_data = GPP[:,92:137,112:213]
# GPP_south = GPP[:,75:137,112:213]
GPP_north_data = GPP[:,52:92,112:225]
GPP_northeast_data = GPP[:,12:52,196:261]

#获取各个区域PET数据，并进行异常值处理
PET_dataset = xr.open_dataset(r"D:\work\code\yuan\data\PET\PET.nc")['PET'].values
for year in range(20):
    if year ==0:
        PET = PET_dataset[year]
    else:
        PET = np.concatenate((PET,PET_dataset[year]))
PET/=10000
PET = (PET-np.nanmean(PET,axis=0))/np.nanstd(PET,axis=0)
PET[np.array([mask for i in range(LAI.shape[0])])==0]=np.nan
PET_south_data = PET[:,92:137,112:213]
PET_north_data = PET[:,52:92,112:225]
PET_northeast_data = PET[:,12:52,196:261]

#创建空列表用于存放每pentad的各个数据
lst_S_south = [[] for i in range(26)]
lst_S_north = [[] for i in range(26)]
lst_S_northeast = [[] for i in range(26)]
lst_LAI_south = [[] for i in range(26)]
lst_LAI_north = [[] for i in range(26)]
lst_LAI_northeast = [[] for i in range(26)]
lst_GPP_south = [[] for i in range(26)]
lst_GPP_north = [[] for i in range(26)]
lst_GPP_northeast = [[] for i in range(26)]
lst_PET_south = [[] for i in range(26)]
lst_PET_north = [[] for i in range(26)]
lst_PET_northeast = [[] for i in range(26)]

#获取各个区域的权重数据
for year in range(2001,2024):
    quan_dataset = xr.open_dataset(f"D:/work/code/yuan/data/soil_moisture/Nc/quan1/swvl_{year}_quan.nc")
    quan = quan_dataset['quan'].values
    # quan[quan==quan[0,220,272]]=np.nan
    if year == 2001:
        quans = quan.copy()
        continue
    quans = np.concatenate((quans,quan))

quans[np.array([mask for i in range(quans.shape[0])])==0]=np.nan
quans_south = quans[:,92:137,112:213]
mask_south = np.empty((quans_south.shape[1],quans_south.shape[2]),dtype=int)
mask_south[::] = 1
mask_south[~(np.nanmean(quans_south,axis=0)>=0.01)]=0

quans_north = quans[:,52:92,112:225]
mask_north = np.empty((quans_north.shape[1],quans_north.shape[2]),dtype=int)
mask_north[::] = 1
mask_north[~(np.nanmean(quans_north,axis=0)>=0.01)]=0

quans_northeast = quans[:,12:52,196:261]
mask_northeast = np.empty((quans_northeast.shape[1],quans_northeast.shape[2]),dtype=int)
mask_northeast[::] = 1
mask_northeast[~(np.nanmean(quans_northeast,axis=0)>=0.01)]=0

#大体类似闪电干旱识别代码，分为三个区域
for year in range(0,quans_south.shape[0],73):
    LAI_south = LAI_south_data[year:year+73+25]
    LAI_north = LAI_north_data[year:year+73+25]
    LAI_northeast = LAI_northeast_data[year:year+73+25]
    
    GPP_south = GPP_south_data[year:year+73+25]
    GPP_north = GPP_north_data[year:year+73+25]
    GPP_northeast = GPP_northeast_data[year:year+73+25]
    
    PET_south = PET_south_data[year:year+73+25]
    PET_north = PET_north_data[year:year+73+25]
    PET_northeast = PET_northeast_data[year:year+73+25]
    
    S_south = S_south_data[year:year+73+25]
    S_north = S_north_data[year:year+73+25]
    S_northeast = S_northeast_data[year:year+73+25]
    
    arr_south = quans_south[year:year+73]
    arr_north = quans_north[year:year+73]
    arr_northeast = quans_northeast[year:year+73]
    
    count_south = np.zeros(mask_south.shape,dtype=int)
    count_north = np.zeros(mask_north.shape,dtype=int)
    count_northeast = np.zeros(mask_northeast.shape,dtype=int)
    
    switch_south = np.empty(mask_south.shape,dtype=bool)
    switch_north = np.empty(mask_north.shape,dtype=bool)
    switch_northeast = np.empty(mask_northeast.shape,dtype=bool)
    switch_south[::] = False
    switch_north[::] = False
    switch_northeast[::] = False
    
    st_switch_south = np.empty(mask_south.shape,dtype=bool)
    st_switch_north = np.empty(mask_north.shape,dtype=bool)
    st_switch_northeast = np.empty(mask_northeast.shape,dtype=bool)
    st_switch_south[::] = False
    st_switch_north[::] = False
    st_switch_northeast[::] = False
    
    st_count_south = np.zeros(mask_south.shape,dtype=int)
    st_count_north = np.zeros(mask_north.shape,dtype=int)
    st_count_northeast = np.zeros(mask_northeast.shape,dtype=int)
    
    ed_switch_south = np.empty(mask_south.shape,dtype=bool)
    ed_switch_north = np.empty(mask_north.shape,dtype=bool)
    ed_switch_northeast = np.empty(mask_northeast.shape,dtype=bool)
    ed_switch_south[::] = False
    ed_switch_north[::] = False
    ed_switch_northeast[::] = False
    
    ed_count_south = np.zeros(mask_south.shape,dtype=int)
    ed_count_north = np.zeros(mask_north.shape,dtype=int)
    ed_count_northeast = np.zeros(mask_northeast.shape,dtype=int)
    
    for i in range(73):
        st_switch_south[st_count_south>5]=False
        st_switch_north[st_count_north>5]=False
        st_switch_northeast[st_count_northeast>5]=False
        
        st_count_south[(~st_switch_south)]=0
        st_count_north[(~st_switch_north)]=0
        st_count_northeast[(~st_switch_northeast)]=0
        
        ed_count_south[switch_south & ed_switch_south]=-3
        ed_count_north[switch_north & ed_switch_north]=-3
        ed_count_northeast[switch_northeast & ed_switch_northeast]=-3
        
        ed_switch_south[(arr_south[i]>=0.2) & switch_south]=True
        ed_switch_north[(arr_north[i]>=0.2) & switch_north]=True
        ed_switch_northeast[(arr_northeast[i]>=0.2) & switch_northeast]=True
        
        ed_switch_south[(arr_south[i]<0.2) & switch_south]=False
        ed_switch_north[(arr_north[i]<0.2) & switch_north]=False
        ed_switch_northeast[(arr_northeast[i]<0.2) & switch_northeast]=False
        
        ed_count_south[(arr_south[i]<0.2) & switch_south]=0
        ed_count_north[(arr_north[i]<0.2) & switch_north]=0
        ed_count_northeast[(arr_northeast[i]<0.2) & switch_northeast]=0
        
        st_switch_south[arr_south[i]>=0.4]=True
        st_switch_north[arr_north[i]>=0.4]=True
        st_switch_northeast[arr_northeast[i]>=0.4]=True
        
        st_count_south[(arr_south[i]>=0.4)]=0
        st_count_north[(arr_north[i]>=0.4)]=0
        st_count_northeast[(arr_northeast[i]>=0.4)]=0
        
        st_count_south[st_switch_south]+=1
        st_count_north[st_switch_north]+=1
        st_count_northeast[st_switch_northeast]+=1
        
        ed_count_south[ed_switch_south]+=1
        ed_count_north[ed_switch_north]+=1
        ed_count_northeast[ed_switch_northeast]+=1
        
        switch_south[(ed_count_south==-2) & (ed_switch_south)] = False
        switch_north[(ed_count_north==-2) & (ed_switch_north)] = False
        switch_northeast[(ed_count_northeast==-2) & (ed_switch_northeast)] = False
        
        count_south[(ed_count_south==-2) & (ed_switch_south)]-=1
        count_north[(ed_count_north==-2) & (ed_switch_north)]-=1
        count_northeast[(ed_count_northeast==-2) & (ed_switch_northeast)]-=1
        
        """
        将干旱发生前后共26天LAI、GPP、PET数据加入空列表中
        """
        if i-5>0:
            for p in range(26):
                m_south = i-count_south-1
                m_north = i-count_north-1
                m_northeast = i-count_northeast-1
                
                for j in range(i-5):
                    if (j-5+p < LAI_north.shape[0]) and (j-5+p>=0):
                        lst_S_south[p]+=list(S_south[j-5+p][(count_south>=6) & (count_south<=18) & (ed_count_south==-2) & (ed_switch_south) & (m_south==j)])
                        lst_S_north[p]+=list(S_north[j-5+p][(count_north>=6) & (count_north<=18) & (ed_count_north==-2) & (ed_switch_north) & (m_north==j)])
                        lst_S_northeast[p]+=list(S_northeast[j-5+p][(count_northeast>=6) & (count_northeast<=18) & (ed_count_northeast==-2) & (ed_switch_northeast) & (m_northeast==j)])
                        
                        lst_LAI_south[p]+=list(LAI_south[j-5+p][(count_south>=6) & (count_south<=18) & (ed_count_south==-2) & (ed_switch_south) & (m_south==j)])
                        lst_LAI_north[p]+=list(LAI_north[j-5+p][(count_north>=6) & (count_north<=18) & (ed_count_north==-2) & (ed_switch_north) & (m_north==j)])
                        lst_LAI_northeast[p]+=list(LAI_northeast[j-5+p][(count_northeast>=6) & (count_northeast<=18) & (ed_count_northeast==-2) & (ed_switch_northeast) & (m_northeast==j)])
                        
                        lst_GPP_south[p]+=list(GPP_south[j-5+p][(count_south>=6) & (count_south<=18) & (ed_count_south==-2) & (ed_switch_south) & (m_south==j)])
                        lst_GPP_north[p]+=list(GPP_north[j-5+p][(count_north>=6) & (count_north<=18) & (ed_count_north==-2) & (ed_switch_north) & (m_north==j)])
                        lst_GPP_northeast[p]+=list(GPP_northeast[j-5+p][(count_northeast>=6) & (count_northeast<=18) & (ed_count_northeast==-2) & (ed_switch_northeast) & (m_northeast==j)])
                        
                        lst_PET_south[p]+=list(PET_south[j-5+p][(count_south>=6) & (count_south<=18) & (ed_count_south==-2) & (ed_switch_south) & (m_south==j)])
                        lst_PET_north[p]+=list(PET_north[j-5+p][(count_north>=6) & (count_north<=18) & (ed_count_north==-2) & (ed_switch_north) & (m_north==j)])
                        lst_PET_northeast[p]+=list(PET_northeast[j-5+p][(count_northeast>=6) & (count_northeast<=18) & (ed_count_northeast==-2) & (ed_switch_northeast) & (m_northeast==j)])
        
        count_south[(ed_count_south==-2) & (ed_switch_south)] = 0
        count_north[(ed_count_north==-2) & (ed_switch_north)] = 0
        count_northeast[(ed_count_northeast==-2) & (ed_switch_northeast)] = 0
        
        ed_switch_south[(ed_count_south==-2) & (ed_switch_south)] = False
        ed_switch_north[(ed_count_north==-2) & (ed_switch_north)] = False
        ed_switch_northeast[(ed_count_northeast==-2) & (ed_switch_northeast)] = False
        
        ed_count_south[(ed_count_south==-2) & (ed_switch_south)] = 0
        ed_count_north[(ed_count_north==-2) & (ed_switch_north)] = 0
        ed_count_northeast[(ed_count_northeast==-2) & (ed_switch_northeast)] = 0
        
        switch_south[(arr_south[i]<0.2) & (st_switch_south)]=True
        switch_north[(arr_north[i]<0.2) & (st_switch_north)]=True
        switch_northeast[(arr_northeast[i]<0.2) & (st_switch_northeast)]=True
        
        st_switch_south[(arr_south[i]<0.2) & (st_switch_south)]=False
        st_switch_north[(arr_north[i]<0.2) & (st_switch_north)]=False
        st_switch_northeast[(arr_northeast[i]<0.2) & (st_switch_northeast)]=False
        
        count_south[switch_south & (~np.isnan(arr_south[i]))]+=1
        count_north[switch_north & (~np.isnan(arr_north[i]))]+=1
        count_northeast[switch_northeast & (~np.isnan(arr_northeast[i]))]+=1

arid_index_south = np.nanmean(arid[92:137,112:213])
VcT_index_south = np.nanmean(tc_index[92:137,112:213])
arid_index_north = np.nanmean(arid[52:92,112:225])
VcT_index_north = np.nanmean(tc_index[52:92,112:225])
arid_index_northeast = np.nanmean(arid[12:52,196:261])
VcT_index_northeast = np.nanmean(tc_index[12:52,196:261])

#绘图，分九个子图
fig, ax = plt.subplots(figsize=(20,15))

ax1 = plt.subplot(3,3,1)
plt_dro(lst_LAI_south,lst_S_south,arid_index_south,VcT_index_south,'a.LAI_south')
ax1 = plt.subplot(3,3,2)
plt_dro(lst_LAI_north,lst_S_north,arid_index_north,VcT_index_north,'b.LAI_north')
ax1 = plt.subplot(3,3,3)
plt_dro(lst_LAI_northeast,lst_S_northeast,arid_index_northeast,VcT_index_northeast,'c.LAI_northeast')

ax1 = plt.subplot(3,3,4)
plt_dro(lst_GPP_south,lst_S_south,arid_index_south,VcT_index_south,'d.GPP_south')
ax1 = plt.subplot(3,3,5)
plt_dro(lst_GPP_north,lst_S_north,arid_index_north,VcT_index_north,'e.GPP_north')
ax1 = plt.subplot(3,3,6)
plt_dro(lst_GPP_northeast,lst_S_northeast,arid_index_northeast,VcT_index_northeast,'f.GPP_northeast')

ax1 = plt.subplot(3,3,7)
plt_dro(lst_PET_south,lst_S_south,arid_index_south,VcT_index_south,'g.PET_south')
ax1 = plt.subplot(3,3,8)
plt_dro(lst_PET_north,lst_S_north,arid_index_north,VcT_index_north,'h.PET_north')
ax1 = plt.subplot(3,3,9)
plt_dro(lst_PET_northeast,lst_S_northeast,arid_index_northeast,VcT_index_northeast,'i.PET_northeast')

# plt.savefig(r'D:\\work\\code\\yuan\\图\\flash_dry\\dro_pic_cahnge.tif',dpi=600)






























