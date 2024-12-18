# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 15:16:31 2024

@author: 33501
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
import Sector
import kdeplot 

#定义闪电干旱识别函数
def detect_dry(quans,mask):
    dro_num = np.zeros(mask.shape,dtype=float)
    dro_num[np.isnan(mask)] = np.nan
    for year in range(0,quans.shape[0],73):
        arr = quans[year:year+73]
        count = np.zeros(mask.shape,dtype=int)
        switch = np.empty(mask.shape,dtype=bool)
        switch[::] = False
        st_switch = np.empty(mask.shape,dtype=bool)
        st_switch[::] = False
        st_count = np.zeros(mask.shape,dtype=int)
        ed_switch = np.empty(mask.shape,dtype=bool)
        ed_switch[::] = False
        ed_count = np.zeros(mask.shape,dtype=int)
        count_all = np.zeros((73,arr.shape[1],arr.shape[2]),dtype=int)
        
        for i in range(73):
            arr[i][mask==0]=np.nan
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
            dro_num[(count>=6) & (count<=18) & (ed_count==-2) & (ed_switch)]+=1
            count[(ed_count==-2) & (ed_switch)] = 0
            ed_switch[(ed_count==-2) & (ed_switch)] = False
            ed_count[(ed_count==-2) & (ed_switch)] = 0
            switch[(arr[i]<0.2) & (st_switch)]=True
            st_switch[(arr[i]<0.2) & (st_switch)]=False
            count[switch & (~np.isnan(arr[i]))]+=1
    return dro_num

#定义闪电干旱识别函数(获得每年数据)
def detect_dry_year(quans,mask):
    dro_num = np.zeros((int((len(quans)/73)),mask.shape[0],mask.shape[1]),dtype=float)
    for year in range(0,quans.shape[0],73):
        dro_num[int(year/73)][np.isnan(mask)] = np.nan
        arr = quans[year:year+73]
        count = np.zeros(mask.shape,dtype=int)
        switch = np.empty(mask.shape,dtype=bool)
        switch[::] = False
        st_switch = np.empty(mask.shape,dtype=bool)
        st_switch[::] = False
        st_count = np.zeros(mask.shape,dtype=int)
        ed_switch = np.empty(mask.shape,dtype=bool)
        ed_switch[::] = False
        ed_count = np.zeros(mask.shape,dtype=int)
        count_all = np.zeros((73,arr.shape[1],arr.shape[2]),dtype=int)
        
        for i in range(73):
            arr[i][mask==0]=np.nan
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
            dro_num[int(year/73)][(count>=6) & (count<=18) & (ed_count==-2) & (ed_switch)]+=1
            count[(ed_count==-2) & (ed_switch)] = 0
            ed_switch[(ed_count==-2) & (ed_switch)] = False
            ed_count[(ed_count==-2) & (ed_switch)] = 0
            switch[(arr[i]<0.2) & (st_switch)]=True
            st_switch[(arr[i]<0.2) & (st_switch)]=False
            count[switch & (~np.isnan(arr[i]))]+=1
    return dro_num

#获取权重数据
swvl_dataset = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\ssp126quan_30s.nc")
swvl_quan126 = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\ssp126quan_30s.nc")['quan'].values
swvl_quan245 = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\ssp245quan_30s.nc")['quan'].values
swvl_quan585 = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\ssp585quan_30s.nc")['quan'].values
swvl_quan = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\histquan_30s.nc")['quan'].values
lon = swvl_dataset['lon'].values
lat = swvl_dataset['lat'].values


# swvl_dataset = xa.open_dataset(r"D:\work\code\yuan\data\sh\soil_ssp126_quan.nc")
# swvl_quan126 = xa.open_dataset(r"D:\work\code\yuan\data\sh\soil_ssp126_quan.nc")['ssp126'].values[-2555:]
# swvl_quan245 = xa.open_dataset(r"D:\work\code\yuan\data\sh\soil_ssp245_quan.nc")['ssp245'].values[-2555:]
# swvl_quan585 = xa.open_dataset(r"D:\work\code\yuan\data\sh\soil_ssp585_quan.nc")['ssp585'].values[-2555:]
# swvl_quan = xa.open_dataset(r"D:\work\code\yuan\data\sh\soil_hist_quan.nc")['hist'].values

#获取中国区域mask
# shp = ogr.Open(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp")
# lyr = shp.GetLayer()
# driver = gdal.GetDriverByName('MEM')
# shp_ds_SM = driver.Create('', 273, 221, 1, gdal.GDT_UInt32)
# shp_ds_SM.SetProjection('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]')
# shp_ds_SM.SetGeoTransform((70,0.25,0,55,0,-0.25))
# options = ['ATTRIBUTE=gb']
# gdal.RasterizeLayer(shp_ds_SM, [1], lyr, options=options)
# cn_mask = shp_ds_SM.ReadAsArray().astype(np.int16)

#获取mask数据
cn_mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()

swvl_quan[np.array([cn_mask for i in range(swvl_quan.shape[0])])==0] = np.nan

#利用权重数据求得各个时间段干旱频率数据
dry126 = detect_dry(swvl_quan126,swvl_quan[30])
dry245 = detect_dry(swvl_quan245,swvl_quan[30])
dry585 = detect_dry(swvl_quan585,swvl_quan[30])
dry = detect_dry(swvl_quan,swvl_quan[30])

#计算干旱频率历史未来变化百分比
change126 = (dry126-dry)/(dry+dry126)*100
change245 = (dry245-dry)/(dry245+dry)*100
change585 = (dry585-dry)/(dry585+dry)*100




#分别对三个情景的干旱频率历史未来变化进行绘图


#ssp126

fig2 = plt.figure(figsize=(12,33))

colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)
# fig2 = plt.figure(figsize=(18, 10))
# fig2 = plt.subplot(3,1,1)

ax = fig2.add_axes([0.001, (2/3), 0.98, 0.89/3])
plt.xlim(0,1)
plt.ylim(0,1)
plt.text(0.01,0.97,'a',size=25)
plt.text(0.58,0.97,'b',size=25)
plt.text(0.58,0.55,'c',size=25)
plt.tick_params(labelsize=0,length=0,width=0)

ax.spines[['top', 'right','left','bottom']].set_linewidth(0)

ax1 = fig2.add_axes([-0.075, 0.05/3+(2/3), 0.74, 0.8/3], projection=proj)
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')


ap=ax1.pcolormesh(lon,lat,change126,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=60,vmin=-60)
plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)
cb2 = plt.colorbar(ap,location='bottom',shrink=0.65,pad=0.05)

ax1 = fig2.add_axes([0.38, 0.25/3+(2/3), 0.18, 0.18/3], projection=proj)
ap1=ax1.pcolormesh(lon,lat,change126,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=60,vmin=-60)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax1.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)

kdeplot.kplot(r"D:\work\code\yuan\data\CMIP6\ssp\dry126_30s.nc",'dry126')
Sector.ST(126)

#ssp245

colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)
ax = fig2.add_axes([0.001, (1/3), 0.98, 0.89/3])
plt.xlim(0,1)
plt.ylim(0,1)
plt.text(0.01,0.97,'d',size=25)
plt.text(0.58,0.97,'e',size=25)
plt.text(0.58,0.55,'f',size=25)
plt.tick_params(labelsize=0,length=0,width=0)

ax.spines[['top', 'right','left','bottom']].set_linewidth(0)

ax1 = fig2.add_axes([-0.075, 0.05/3+(1/3), 0.74, 0.8/3], projection=proj)
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')


ap=ax1.pcolormesh(lon,lat,change245,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=60,vmin=-60)
plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)
cb2 = plt.colorbar(ap,location='bottom',shrink=0.7,pad=0.05)

ax1 = fig2.add_axes([0.38, 0.25/3+(1/3), 0.18, 0.18/3], projection=proj)
ap1=ax1.pcolormesh(lon,lat,change245,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=60,vmin=-60)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax1.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)


kdeplot.kplot(r"D:\work\code\yuan\data\CMIP6\ssp\dry245_30s.nc",'dry245')
Sector.ST(245)

#ssp585

colors = ['#0000CC','#0066FF','#00BBFF','#77DDFF','#FFFFFF','#FFFF33','#FFBB00','#FF0000','#880000']
cmap = mpl.colors.LinearSegmentedColormap.from_list("custom_cmap", colors)

proj = ccrs.PlateCarree(central_longitude=0)
ax = fig2.add_axes([0.001, 0.05, 0.98, 0.8/3])
plt.xlim(0,1)
plt.ylim(0,1)
plt.text(0.01,0.8,'g',size=25)
plt.text(0.58,0.8,'h',size=25)
plt.text(0.58,0.4,'i',size=25)
plt.tick_params(labelsize=0,length=0,width=0)

ax.spines[['top', 'right','left','bottom']].set_linewidth(0)

ax1 = fig2.add_axes([-0.075, 0, 0.74, 0.8/3], projection=proj)
ax1.set_extent([73, 136, 15, 55],
                  crs=ccrs.PlateCarree())

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=0.5,facecolor='none',zorder=11)

shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn,proj, lw=1, fc='none')


ap=ax1.pcolormesh(lon,lat,change585,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=60,vmin=-60)
plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)
cb2 = plt.colorbar(ap,location='bottom',shrink=0.7,pad=0.05)

ax1 = fig2.add_axes([0.38, 0.25/3, 0.18, 0.18/3], projection=proj)
ap1=ax1.pcolormesh(lon,lat,change585,transform=ccrs.PlateCarree(),cmap=cmap,zorder=10,vmax=60,vmin=-60)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax1.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)

kdeplot.kplot(r"D:\work\code\yuan\data\CMIP6\ssp\dry585_30s.nc",'dry585')
Sector.ST(585)

plt.savefig(f'D:\\work\\code\\yuan\\图\\flash_dry\\pic3_30.tif',dpi=600)






