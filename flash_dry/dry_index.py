# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 21:20:01 2024

@author: 33501

此代码绘制干燥指数和干燥指数-树木覆盖度双变量图
"""

import numpy as np
import xarray as xr
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
from scipy import ndimage
from osgeo import ogr,gdal
from cartopy.io.shapereader import Reader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import rasterio as ra
from brokenaxes import brokenaxes
import warnings
# from detect import dro_num
warnings.filterwarnings("ignore")


def resample(array,target_shape):   #重采样函数
    zoom_factors = [target_shape[i] / array.shape[i] for i in range(len(target_shape))]
    resampled_array = ndimage.zoom(array, zoom_factors, order=1)
    return resampled_array

#中国区域mask
# shp = ogr.Open(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp")
# lyr = shp.GetLayer()
# driver = gdal.GetDriverByName('MEM')
# shp_ds_SM = driver.Create('', 273, 221, 1, gdal.GDT_UInt32)
# shp_ds_SM.SetProjection('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]')
# shp_ds_SM.SetGeoTransform((70,0.25,0,55,0,-0.25))
# options = ['ATTRIBUTE=gb']
# gdal.RasterizeLayer(shp_ds_SM, [1], lyr, options=options)
# cn_mask = shp_ds_SM.ReadAsArray().astype(np.int16)

#获取mask
cn_mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()

#获取净辐射、潜在蒸散、降水、植被数据
sr = xr.open_dataset(r"D:\work\code\yuan\data\dry\sr_use.nc")['sr'].values
pev = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['pev'].values
tp = xr.open_dataset(r"D:\work\code\yuan\data\total_precipitation\tp.nc")['tp'].values*1000
vc = xr.open_dataset(r"D:\work\code\yuan\data\Vegetation_Continuous_Fields\vc_mean.nc")['vc'].values
lon = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lon'].values
lat = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lat'].values

#获取干燥指数数据
dry_index = ra.open(r"D:\work\gee_\gee_download\yuan\test\dry.tif").read()[0]
dry_index = resample(dry_index,(221,273))
dry_index[dry_index>4]=np.nan
dry_index[cn_mask==0]=np.nan
tc_index = vc[0]/(vc[0]+vc[1])

#绘制干燥指数图
colors = ['#0000FF', '#00BBFF', '#77DDFF', '#FFFF33','#FF8800','#FF0000','#880000'] 
cmap = mpl.colors.ListedColormap(colors)
bounds = [0,0.25,0.5,1,1.5,2,4]
norm = mpl.colors.BoundaryNorm(bounds, 6)
proj = ccrs.PlateCarree(central_longitude=0)
fig2 = plt.figure(figsize=(6.5,4))
ax = fig2.add_axes([0.05, 0.05, 0.9, 0.9], projection=proj)
ax.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())
plt.plot([98,123],[21,21],lw=1.5,zorder=11,c='black')
plt.plot([98,123],[32,32],lw=1.5,zorder=11,c='black')
plt.plot([98,98],[21,32],lw=1.5,zorder=11,c='black')
plt.plot([123,123],[21,32],lw=1.5,zorder=11,c='black')

plt.plot([98,126],[42,42],lw=1.5,zorder=11,c='black')
plt.plot([98,126],[32,32],lw=1.5,zorder=11,c='black')
plt.plot([98,98],[42,32],lw=1.5,zorder=11,c='black')
plt.plot([126,126],[42,32],lw=1.5,zorder=11,c='black')

plt.plot([119,135],[42,42],lw=1.5,zorder=11,c='black')
plt.plot([119,135],[54,54],lw=1.5,zorder=11,c='black')
plt.plot([119,119],[42,54],lw=1.5,zorder=11,c='black')
plt.plot([135,135],[42,54],lw=1.5,zorder=11,c='black')

dry_index[cn_mask==0] = np.nan
coler = ax.contourf(lon,lat,dry_index,levels=bounds,cmap=cmap,norm=norm)
color_b = plt.colorbar(coler,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
color_b.set_ticklabels([int(0),0.25,0.5,int(1),1.5,int(2),int(4)])
plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax.add_geometries(shp_cn,proj, lw=1, fc='none')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)
ax1 = fig2.add_axes([0.762, 0.12, 0.2, 0.2], projection=proj,anchor=(0.5,0.5))
ax1.contourf(lon,lat,dry_index,levels=bounds,cmap=cmap,norm=norm)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax1.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)
plt.tight_layout()
# plt.savefig(r'D:\\work\\code\\yuan\\图\\flash_dry\\dry_index.tif',dpi=600)


#将干燥指数和树木覆盖度组合
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
p_arr[cn_mask==0] = np.nan

#统计各个干燥指数的数量
numb_dry = {}
for i in [10,20,30,40]:
    numb_dry[i] = len(p_dry[p_dry==i])
numb_dry = pd.Series(numb_dry)
numb_dry = numb_dry/np.nansum(numb_dry)

#统计各个树木覆盖度的数量
numb_vc = {}
for i in [1,2,3,4]:
    numb_vc[i] = len(p_tc[p_tc==i])
numb_vc = pd.Series(numb_vc)
numb_vc = numb_vc/np.nansum(numb_vc)

#用于绘制图例的矩阵
ld = np.array([[14,24,34,44],
      [13,23,33,43],
      [12,22,32,42],
      [11,21,31,41]])
colors = ['#FFFF77','#00DD00','#7EB65A','#003100',
          '#FFDD55','#00FF5C','#7ECE5A','#114900',
          '#FFAA33','#87FF5C','#A1D85A','#246500',
          '#FF0000','#DBFF5C','#A3FF00','lightgray']

#出图
cmap = mpl.colors.ListedColormap(colors)
bounds = [10.5,11.5,12.5,13.5,20.5,21.5,22.5,23.5,30.5,31.5,32.5,33.5,40.5,41.5,42.5,43.5,50.5]
norm = mpl.colors.BoundaryNorm(bounds, 17)
proj = ccrs.PlateCarree(central_longitude=0)
fig2 = plt.figure(figsize=(15, 10))
ax1 = fig2.add_axes([0.05, 0.05, 0.9, 0.9], projection=proj)
ax1.set_extent([73, 136, 14.9, 55.1],
                  crs=ccrs.PlateCarree())
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)
ap=ax1.pcolormesh(lon,lat,p_arr,transform=ccrs.PlateCarree(),cmap=cmap,norm=norm,zorder=10)
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')
ax1.spines[['left','bottom','top', 'right']].set_zorder(11)
plt.plot([73,136],[14.9,14.9],lw=5,c='black',zorder=12)
plt.plot([73,136],[55.1,55.1],lw=5,c='black',zorder=12)
plt.plot([73,73],[14.9,55.1],lw=5,c='black',zorder=12)
plt.plot([136,136],[14.9,55.1],lw=5,c='black',zorder=12)
ax1.tick_params(axis='both', which='major', width=3,length=5,direction='in')
plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=20)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=20)
ax2 = fig2.add_axes([0.12, 0.2, 0.14, 0.14])
coler = ax2.imshow(ld,cmap=cmap,norm=norm,extent=[-0.5,3.5,3.5,-0.5])
plt.xlim(-0.5,4.5)
plt.xticks([-0.5,0.5,1.5,2.5,3.5],[0,0.5,1,2,4],size=15)
plt.ylim(3.5,-1.5)
plt.yticks([-0.5,0.5,1.5,2.5,3.5],['1','.75','.50','.25','0'],size=15)
plt.xlabel('DryIdx',size=20)
plt.ylabel('Tree dominance',size=20)
ax2.bar([0,1,2,3],numb_dry*(-1),bottom=-0.56,color='#F0A73A')
ax2.barh([3,2,1,0],numb_vc,left=3.56,color='#3ABF99')
ax2.hlines(-0.5,-0.5,3.5,color='black',lw=3)
ax2.vlines(3.5,-0.55,3.5,color='black',lw=3)
ax2.spines[['left','bottom',]].set_linewidth(3)
ax2.spines[['left']].set_bounds(3.5,-0.5)
ax2.spines[['bottom']].set_bounds(-0.5,3.5)
ax2.spines[['top', 'right']].set_linewidth(0)
ax2.tick_params(axis='both', which='major', width=3,length=10)
ax1 = fig2.add_axes([0.78, 0.1, 0.2, 0.2], projection=proj,anchor=(0.5,0.5))
ap=ax1.pcolormesh(lon,lat,p_arr,transform=ccrs.PlateCarree(),cmap=cmap,norm=norm,zorder=10)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax1.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=3,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=3,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=3,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=3,c='black',zorder=12)

plt.tight_layout()
# plt.savefig(r'D:\work\code\yuan\图\flash_dry\双轴.tif',dpi=600)

















