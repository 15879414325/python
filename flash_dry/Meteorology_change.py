# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 21:15:58 2024

@author: 33501

此代码用于分析降水、气温、潜在蒸散的历史未来变化
"""

import xarray as xa
from osgeo import gdal,ogr
import numpy as np
from scipy.stats.mstats import mquantiles,meppf
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from scipy import stats

#获取掩膜数据
cn_mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()

#PRCP
#获取所有时间段降水数据
prcp = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_pr.nc')['pr'].values
prcp_126 = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp126_pr.nc')['pr'].values
prcp_245 = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp245_pr.nc')['pr'].values
prcp_585= xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp585_pr.nc')['pr'].values
prcp[cn_mask==0]=np.nan
lon =xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_pr.nc')['lon'].values
lat =xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_pr.nc')['lat'].values

#计算情景126降水数据历史未来变化并绘图
change_pr_126 = (prcp_126-prcp)/(prcp_126+prcp)

colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)
fig2 = plt.figure(figsize=(24, 20))

ax1 = fig2.add_axes([0.05, 0.65, 0.25, 0.25], projection=proj)
plt.title('a.PR126',size=20,weight='bold')
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')

ap=ax1.pcolormesh(lon,lat,change_pr_126,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

ax2 = fig2.add_axes([0.235, 0.672, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
ax2.pcolormesh(lon,lat,change_pr_126,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)

# plt.savefig(r'D:\work\code\yuan\图\flash_dry\变化图pr126.tif',dpi=600)



#计算情景245降水数据历史未来变化并绘图
change_pr_245 = (prcp_245-prcp)/(prcp_245+prcp)

colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)

ax1 = fig2.add_axes([0.35, 0.65, 0.25, 0.25], projection=proj)
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())
plt.title('b.PR245',size=20,weight='bold')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')

ap=ax1.pcolormesh(lon,lat,change_pr_245,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

ax2 = fig2.add_axes([0.535, 0.672, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
ax2.pcolormesh(lon,lat,change_pr_245,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)



#计算情景585降水数据历史未来变化并绘图
change_pr_585 = (prcp_585-prcp)/(prcp_585+prcp)


colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)
ax1 = fig2.add_axes([0.65, 0.65, 0.25, 0.25], projection=proj)
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())
plt.title('c.PR585',size=20,weight='bold')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')

ap=ax1.pcolormesh(lon,lat,change_pr_585,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

ax2 = fig2.add_axes([0.835, 0.672, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
ax2.pcolormesh(lon,lat,change_pr_585,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)



# TAS
#获取所有时间段气温数据
tas = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_tas.nc')['tas'].values
tas_126 = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp126_tas.nc')['tas'].values
tas_245 = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp245_tas.nc')['tas'].values
tas_585= xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp585_tas.nc')['tas'].values
lon= xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_tas.nc')['lon'].values
lat = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_tas.nc')['lat'].values
tas[cn_mask==0]=np.nan



#计算情景126气温数据历史未来变化并绘图
change_tas_126 = (tas_126-tas)/(tas_126+tas)

colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)
ax1 = fig2.add_axes([0.05, 0.35, 0.25, 0.25], projection=proj)
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())
plt.title('d.TAS126',size=20,weight='bold')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')

ap=ax1.pcolormesh(lon,lat,change_tas_126,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

ax2 = fig2.add_axes([0.235, 0.372, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
ax2.pcolormesh(lon,lat,change_tas_126,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)




#计算情景245气温数据历史未来变化并绘图
change_tas_245 = (tas_245-tas)/(tas_245+tas)

colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)
ax1 = fig2.add_axes([0.35, 0.35, 0.25, 0.25], projection=proj)
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())
plt.title('e.TAS245',size=20,weight='bold')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')

ap=ax1.pcolormesh(lon,lat,change_tas_245,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

ax2 = fig2.add_axes([0.535, 0.372, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
ax2.pcolormesh(lon,lat,change_tas_245,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)




#计算情景585气温数据历史未来变化并绘图
change_tas_585 = (tas_585-tas)/(tas_585+tas)

colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)
ax1 = fig2.add_axes([0.65, 0.35, 0.25, 0.25], projection=proj)
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())
plt.title('f.TAS585',size=20,weight='bold')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')

ap=ax1.pcolormesh(lon,lat,change_tas_585,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

ax2 = fig2.add_axes([0.835, 0.372, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
ax2.pcolormesh(lon,lat,change_tas_585,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)


#soil
# soil_126 = np.nanmean(xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp126_soil.nc')['pentad'].values,axis=0)
# soil_245 = np.nanmean(xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp245_soil.nc')['pentad'].values,axis=0)
# soil_585 = np.nanmean(xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp585_soil.nc')['pentad'].values,axis=0)
# soil = np.nanmean(xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\hist_soil.nc")['pentad'].values,axis=0)

# soil[cn_mask==0]=np.nan

# change_soil_126 = (soil_126-soil)/(soil_126+soil)

# lon= xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\hist_soil.nc")['lon'].values
# lat = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\hist_soil.nc")['lat'].values


# colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
# cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)
# # colors = ['#33CCFF','#00DD00','#FFCC22']
# # cmap = mpl.colors.ListedColormap(colors)
# # bounds = [-1.5,-0.5,0.5,1.5]
# # norm = mpl.colors.BoundaryNorm(bounds, 4)

# proj = ccrs.PlateCarree(central_longitude=0)
# ax1 = fig2.add_axes([0.05, 0.35, 0.25, 0.25], projection=proj)
# ax1.set_extent([73, 136, 15, 55],
#                   crs=ccrs.PlateCarree())
# plt.title('d.MOSOS126',size=20,weight='bold')
# shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
# ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

# shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
# ax1.add_geometries(shp_cn,proj, lw=1, fc='none')
# # bounds = [-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1]
# # # bounds = [-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1]
# # norm = mpl.colors.BoundaryNorm(bounds, 11)

# ap=ax1.pcolormesh(lon,lat,change_soil_126,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

# cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
# cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

# plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
# plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
# plt.tick_params(direction='in')
# plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
# plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
# plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
# plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

# ax2 = fig2.add_axes([0.235, 0.372, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
# ax2.pcolormesh(lon,lat,change_soil_126,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
# shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
# ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
# shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
# ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
# ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
# plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
# plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
# plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
# plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)

# change_soil_245 = (soil_245-soil)/(soil_245+soil)

# lon= xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_tas.nc')['lon'].values
# lat = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_tas.nc')['lat'].values


# colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
# cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)
# # colors = ['#33CCFF','#00DD00','#FFCC22']
# # cmap = mpl.colors.ListedColormap(colors)
# # bounds = [-1.5,-0.5,0.5,1.5]
# # norm = mpl.colors.BoundaryNorm(bounds, 4)

# proj = ccrs.PlateCarree(central_longitude=0)
# ax1 = fig2.add_axes([0.35, 0.35, 0.25, 0.25], projection=proj)
# ax1.set_extent([73, 136, 15, 55],
#                   crs=ccrs.PlateCarree())
# plt.title('e.MOSOS245',size=20,weight='bold')
# shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
# ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

# shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
# ax1.add_geometries(shp_cn,proj, lw=1, fc='none')
# # bounds = [-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1]
# # # bounds = [-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1]
# # norm = mpl.colors.BoundaryNorm(bounds, 11)

# ap=ax1.pcolormesh(lon,lat,change_soil_245,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

# cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
# cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

# plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
# plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
# plt.tick_params(direction='in')
# plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
# plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
# plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
# plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

# ax2 = fig2.add_axes([0.535, 0.372, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
# ax2.pcolormesh(lon,lat,change_soil_245,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
# shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
# ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
# shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
# ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
# ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
# plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
# plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
# plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
# plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)

# change_soil_585 = (soil_585-soil)/(soil_585+soil)

# lon= xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_tas.nc')['lon'].values
# lat = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_tas.nc')['lat'].values


# colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
# cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)
# # colors = ['#33CCFF','#00DD00','#FFCC22']
# # cmap = mpl.colors.ListedColormap(colors)
# # bounds = [-1.5,-0.5,0.5,1.5]
# # norm = mpl.colors.BoundaryNorm(bounds, 4)

# proj = ccrs.PlateCarree(central_longitude=0)
# ax1 = fig2.add_axes([0.65, 0.35, 0.25, 0.25], projection=proj)
# ax1.set_extent([73, 136, 15, 55],
#                   crs=ccrs.PlateCarree())
# plt.title('f.MOSOS585',size=20,weight='bold')
# shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
# ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

# shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
# ax1.add_geometries(shp_cn,proj, lw=1, fc='none')
# # bounds = [-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1]
# # # bounds = [-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1]
# # norm = mpl.colors.BoundaryNorm(bounds, 11)

# ap=ax1.pcolormesh(lon,lat,change_soil_585,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

# cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
# cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

# plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
# plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
# plt.tick_params(direction='in')
# plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
# plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
# plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
# plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

# ax2 = fig2.add_axes([0.835, 0.372, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
# ax2.pcolormesh(lon,lat,change_soil_585,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
# shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
# ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
# shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
# ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
# ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
# plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
# plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
# plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
# plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)

#evp
#获取所有时间段潜在蒸散数据
evp = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_evp.nc')['evp'].values
evp_126 = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp126_evp.nc')['evp'].values
evp_245 = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp245_evp.nc')['evp'].values
evp_585= xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp585_evp.nc')['evp'].values

evp[cn_mask==0]=np.nan



#计算情景126潜在蒸散数据历史未来变化并绘图
change_evp_126 = (evp_126-evp)/(evp_126+evp)

colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)
ax1 = fig2.add_axes([0.05, 0.05, 0.25, 0.25], projection=proj)
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())
plt.title('g.PET126',size=20,weight='bold')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')

ap=ax1.pcolormesh(lon,lat,change_evp_126,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

ax2 = fig2.add_axes([0.235, 0.072, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
ax2.pcolormesh(lon,lat,change_evp_126,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)



#计算情景245潜在蒸散数据历史未来变化并绘图
change_evp_245 = (evp_245-evp)/(evp_245+evp)

colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)
ax1 = fig2.add_axes([0.35, 0.05, 0.25, 0.25], projection=proj)
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())
plt.title('h.PET245',size=20,weight='bold')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')

ap=ax1.pcolormesh(lon,lat,change_evp_245,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

ax2 = fig2.add_axes([0.535, 0.072, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
ax2.pcolormesh(lon,lat,change_evp_245,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)



#计算情景585潜在蒸散数据历史未来变化并绘图
change_evp_585 = (evp_585-evp)/(evp_585+evp)

colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)
ax1 = fig2.add_axes([0.65, 0.05, 0.25, 0.25], projection=proj)
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())
plt.title('i.PET585',size=20,weight='bold')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')

ap=ax1.pcolormesh(lon,lat,change_evp_585,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)

cb2 = plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))
cb2.set_ticklabels(['-0.5','-0.25','0','0.25','0.5'])

plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)

ax2 = fig2.add_axes([0.835, 0.072, 0.07, 0.07], projection=proj,anchor=(0.5,0.5))
ax2.pcolormesh(lon,lat,change_evp_585,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=0.5,vmin=-0.5)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax2.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax2.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)

# plt.savefig(r'D:\work\code\yuan\图\flash_dry\Meteorology_change.tif',dpi=600)




























