# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 20:47:32 2024

@author: 33501

此代码将土壤权重数据进行识别，求出每年闪电干旱的次数，并出图

闪电干旱：
当土壤湿度权重在 5 pentad内从不小于0.4下降到0.2以下时，闪旱开始
当土壤湿度权重回升至不小于0.2，并持续 2 pentad时，闪旱结束
干旱持续时间在 6-18 pentad的才能被称作闪电干旱
小于6为短期干旱，大于18为长期干旱
主要参考文献：
https://www.nature.com/articles/s43247-024-01247-4#Sec7
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import ndimage
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from osgeo import ogr,gdal
import warnings
# from dry_index import dry_index
# import prep_quan
warnings.filterwarnings("ignore")

def resample(array,target_shape):
    """
    对影像进行重采样的函数
    """
    zoom_factors = [target_shape[i] / array.shape[i] for i in range(len(target_shape))]
    resampled_array = ndimage.zoom(array, zoom_factors, order=1)
    return resampled_array

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

#获取mask
cn_mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()

#获取潜在蒸散、降水、植被、气温数据
pev = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['pev'].values
tp = xr.open_dataset(r"D:\work\code\yuan\data\total_precipitation\tp.nc")['tp'].values
vc = xr.open_dataset(r"D:\work\code\yuan\data\Vegetation_Continuous_Fields\vc_mean.nc")['vc'].values
temp = xr.open_dataset(r"D:\work\code\yuan\data\2m_temperature\tem.nc")['tem'].values
lon = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lon'].values
lat = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lat'].values

#计算干燥指数和树木覆盖度
dry_index = abs(pev)/tp
tc_index = vc[0]/(vc[0]+vc[1])

arid = dry_index


for year in range(2001,2023):       #合并每年权重数据
    quan_dataset = xr.open_dataset(f"D:/work/code/yuan/data/soil_moisture/Nc/quan_30/swvl_{year}_quan.nc")
    quan = quan_dataset['quan'].values
    # quan[quan==quan[0,220,272]]=np.nan
    if year == 2001:
        quans = quan.copy()
        continue
    quans = np.concatenate((quans,quan))
quans = xr.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\histquan_30s.nc")['quan'].values

#获取mask数据，与cn_mask数据相同
mask = np.empty((quans.shape[1],quans.shape[2]),dtype=int)
mask[::] = 1
mask[arid>4]=0
mask[temp<273.15]=0
mask[~(np.nanmean(quans,axis=0)>=0.01)]=0

ind = 0
#TODO可获取所有年份总数据和每个年份数据
dro_num = np.zeros(mask.shape,dtype=float)
# dro_num = np.zeros((2015-1980,mask.shape[0],mask.shape[1]),dtype=float)

for year in range(0,quans.shape[0],73):
    arr = quans[year:year+73]   #一年的权重数据
    
    switch = np.empty(mask.shape,dtype=bool)    #干旱总开关
    switch[::] = False
    count = np.zeros(mask.shape,dtype=int)  #干旱天数计数器
    
    st_switch = np.empty(mask.shape,dtype=bool) #干旱开始开关
    st_switch[::] = False
    st_count = np.zeros(mask.shape,dtype=int)   #干旱开始计数器
    
    ed_switch = np.empty(mask.shape,dtype=bool) #干旱结束开关
    ed_switch[::] = False
    ed_count = np.zeros(mask.shape,dtype=int)   #干旱结束计数器
    
    for i in range(73):
        arr[i][mask==0]=np.nan
        
        st_switch[st_count>5]=False     #当大于0.4后未在 5 pentad之内下降到0.2以下，干旱开始开关启动
        
        st_count[(~st_switch)]=0        #当干旱开始开关处于关闭状态时，干旱开始计数器归零
        
        ed_count[switch & ed_switch]=-3 #当干旱总开关和干旱结束开关处于开启状态时，
                                        #干旱结束计数器为-3(与干旱开始计数器相区分)
        
        ed_switch[(arr[i]>=0.2) & switch]=True   #当大于0.2且干旱总开关处于开启状态时，干旱结束开关启动
        
        ed_switch[(arr[i]<0.2) & switch]=False   #当小于0.2且干旱总开关处于开启状态时，干旱结束开关关闭
        
        ed_count[(arr[i]<0.2) & switch]=0   #当小于0.2且干旱总开关处于开启状态时，干旱结束计数器归零
        
        st_switch[arr[i]>=0.4]=True    #当大于0.4时，干旱开始开关开启
        
        st_count[(arr[i]>=0.4)]=0     #当大于0.4时，干旱开始计数器归零
        
        st_count[st_switch]+=1        #当干旱开始开关处于开启状态时，干旱开始计数器加一
        
        ed_count[ed_switch]+=1        #干旱结束开关处于开启状态时，干旱结束计数器加一
        
        switch[(ed_count==-2) & (ed_switch)] = False   #当干旱结束计数器为-2且干旱结束开关处于开启状态时，干旱总开关关闭
        
        count[(ed_count==-2) & (ed_switch)]-=1  #当干旱结束计数器为-2且干旱结束开关处于开启状态时，
                                                #干旱天数计数器减一(小于0.2期间计数不计入干旱天数)
        
        #TODO
        dro_num[(count>=6) & (count<=18) & (ed_count==-2) & (ed_switch)]+=1  #当干旱天数计数器大于6小于18且
                                                                             #干旱结束计数器为-2干旱结束开关处于开启状态时，闪电干旱次数加一
        # dro_num[int(year/73)][(count>=6) & (count<=18) & (ed_count==-2) & (ed_switch)]+=1
        
        count[(ed_count==-2) & (ed_switch)] = 0    #当干旱结束计数器为-2且干旱结束开关处于开启状态时，
                                                   #干旱天数计数器归零
        
        ed_switch[(ed_count==-2) & (ed_switch)] = False   #当干旱结束计数器为-2且干旱结束开关处于开启状态时，
                                                          #干旱结束开关关闭
        
        ed_count[(ed_count==-2) & (ed_switch)] = 0   #当干旱结束计数器为-2且干旱结束开关处于开启状态时，
                                                     #干旱结束计数器归零
        
        switch[(arr[i]<0.2) & (st_switch)]=True     #当小于0.2且干旱开始开关处于开启状态时，干旱总开关启动
        
        st_switch[(arr[i]<0.2) & (st_switch)]=False  #当小于0.2且干旱开始开关处于开启状态时，干旱开始开关关闭
        
        count[switch & (~np.isnan(arr[i]))]+=1  #当干旱总开关处于开启状态且此pentad权重不为nan值时，干旱天数计数器加一

    ind+=1


out = xr.Dataset({'hist':(['time','lat','lon'],dro_num)},{'time':[i for i in range(1980,2015)],'lat':lat,'lon':lon})

# out.to_netcdf(r'D:\\work\\code\\yuan\\data\\CMIP6\\ssp\\hist_30s.nc')

dro_num[mask==0] = np.nan
dro_num[cn_mask==0] = np.nan


#出图

proj = ccrs.PlateCarree(central_longitude=0)
fig = plt.figure(figsize=(6.5,4))
ax = fig.add_axes([0.05, 0.05, 0.9, 0.9], projection=proj)

#绘制干旱次数图
colors = ['#00BBFF', '#77DDFF', '#FFFF33','#FF8800','#FF0000'] 
cmap = mpl.colors.ListedColormap(colors)
bounds = [3,5,7,9,11,13]
norm = mpl.colors.BoundaryNorm(bounds, 6)
ap=ax.pcolormesh(lon,lat,dro_num,transform=ccrs.PlateCarree(),cmap=cmap,norm=norm,zorder=10)

#添加国界和九段线
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax.add_geometries(shp_cn,proj, lw=1, fc='none')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax.add_geometries(shp_cn,proj, lw=0.3,facecolor='none',zorder=11)

#将图缩放到中国区域并添加经纬度
ax.set_extent([73, 136, 15, 55],crs=ccrs.PlateCarree())
plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')

#边框加粗及图例
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)
plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))

#添加南海诸岛图
ax1 = fig.add_axes([0.762, 0.12, 0.2, 0.2], projection=proj,anchor=(0.5,0.5))
ap1=ax1.pcolormesh(lon,lat,dro_num,transform=ccrs.PlateCarree(),cmap=cmap,norm=norm,zorder=10)
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=1, fc='none')
shp_cn1 = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax1.add_geometries(shp_cn1,proj, lw=0.3,facecolor='none',zorder=11)
ax1.set_extent([107, 123, 3, 25],crs=ccrs.PlateCarree())
plt.plot([107,123],[3,3],lw=2,c='black',zorder=12)
plt.plot([107,123],[25,25],lw=2,c='black',zorder=12)
plt.plot([107,107],[3,25],lw=2,c='black',zorder=12)
plt.plot([123,123],[3,25],lw=2,c='black',zorder=12)

# plt.savefig(r'D:\work\code\yuan\图\flash_dry\闪旱频率.tif',dpi=600)



    









































