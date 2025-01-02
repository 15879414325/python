# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 10:34:18 2024

@author: 33501
"""

import netCDF4 as nc
import pandas as pd
from osgeo import gdal,osr
import os
import numpy as np
import time
import rasterio
from rasterio.transform import from_origin

start_all = time.time()
path = r"D:\Pandas__Python\python_work\11 nc-tif\pet_2001.nc"
out_path = r"D:\作业\代码\nc\结果"


nf = nc.Dataset(path) #将nc读取为dataset

var_s = [var for var in nf.variables.keys()] #获取nc各个参数

lon = nf.variables['lon'][:] #经度
lat = nf.variables['lat'][:] #纬度
d_time = nf.variables['time'][:] #时间
etp = nf.variables['etp'][:] #研究对象(潜在蒸发量)
lon_max,lat_max,lon_min,lat_min = [max(lon),max(lat),min(lon),min(lat)] #获取经纬度最大最小值

l_lon = len(lon) #像元列数
l_lat = len(lat) #像元行数


lon_res = (lon_max-lon_min)/(float(l_lon)-1) #像元宽度
lat_res = (lat_max-lat_min)/(float(l_lat)-1) #像元高度

#——————————————————————————————————————————————————————————————————————————————
#用gdal nc转tif
for i in range(len(d_time)):
    start_time = time.time()
    arr = etp[i,:,:]    #提取其中一层数据
    driver = gdal.GetDriverByName('GTiff')  #选择GTiff驱动器
    tif_path = f'{out_path}{os.sep}etp_{i+1}月.tif' #输出路径
    out_tif = driver.Create(tif_path,l_lon,l_lat,1,gdal.GDT_Float32) #用驱动器创建输出文件
    geotransform = (lon_min,lon_res,0,lat_min,0,-lat_res) #获得地理变换数据，像元高度一定要是负数
    out_tif.SetGeoTransform(geotransform) #对输出数据进行地理变换
    srs = osr.SpatialReference() #创建空的空间参考对象
    srs.ImportFromEPSG(4326) #添加空间参考
    out_tif.SetProjection(srs.ExportToWkt()) #为输出文件添加投影
    arr[arr == 1e+30] = -99 #替换无效值
    out_tif.GetRasterBand(1).WriteArray(arr) #将nc数据写入输出文件
    out_tif.GetRasterBand(1).SetNoDataValue(-99) #替换数据中的无效值
    out_tif.FlushCache #将数据写入磁盘
    del out_tif #关闭文件
    end_time = time.time()
    print(f'{i+1}月:{end_time-start_time}s')
end_all = time.time()
print(f'转换完成,用时：{end_all-start_all}s')

#——————————————————————————————————————————————————————————————————————————————
#用rasterio nc转tif
for i in range(len(d_time)):
    start_time = time.time()
    arr = etp[i,:,:] #提取其中一层数据
    tif_path = f'{out_path}{os.sep}etp_{i+1}月.tif'
    with rasterio.open(tif_path,'w',driver = 'GTiff',width =l_lon,height =l_lat,count=1,crs=4326,
                       transform=from_origin(lon_min,lat_min,lon_res,lat_res),dtype='float32') as out_tif:
        out_tif.write(arr,1)
    end_time = time.time()
    print(f'{i+1}月:{end_time-start_time}s')
end_all = time.time()
print(f'转换完成,用时：{end_all-start_all}s')





















