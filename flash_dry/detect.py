# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 20:47:32 2024

@author: 33501

This code identifies soil weight data, calculates the number of flash droughts each year, and generates corresponding graphs.

Flash drought:
A flash drought commences when the soil moisture weight drops from no less than 0.4 to below 0.2 within 5 pentads.
A flash drought concludes when the soil moisture weight rises back to no less than 0.2 and remains at this level for 2 pentads.
Only droughts with a duration of 6 - 18 pentads can be classified as flash droughts.
Droughts lasting less than 6 pentads are considered short - term droughts, while those lasting more than 18 pentads are long - term droughts.
Main reference:
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
    The function for resampling the images
    """
    zoom_factors = [target_shape[i] / array.shape[i] for i in range(len(target_shape))]
    resampled_array = ndimage.zoom(array, zoom_factors, order=1)
    return resampled_array

#Obtain the mask for the Chinese region.
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

#Obtain data on potential evapotranspiration, precipitation, vegetation, and air temperature.
pev = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['pev'].values
tp = xr.open_dataset(r"D:\work\code\yuan\data\total_precipitation\tp.nc")['tp'].values
vc = xr.open_dataset(r"D:\work\code\yuan\data\Vegetation_Continuous_Fields\vc_mean.nc")['vc'].values
temp = xr.open_dataset(r"D:\work\code\yuan\data\2m_temperature\tem.nc")['tem'].values
lon = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lon'].values
lat = xr.open_dataset(r"D:\work\code\yuan\data\potential_evaporate\pev_mean.nc")['lat'].values

#Calculate the dryness index and tree coverage rate
dry_index = abs(pev)/tp
tc_index = vc[0]/(vc[0]+vc[1])

arid = dry_index


for year in range(2001,2023):       #Merge the annual weight data
    quan_dataset = xr.open_dataset(f"D:/work/code/yuan/data/soil_moisture/Nc/quan_30/swvl_{year}_quan.nc")
    quan = quan_dataset['quan'].values
    # quan[quan==quan[0,220,272]]=np.nan
    if year == 2001:
        quans = quan.copy()
        continue
    quans = np.concatenate((quans,quan))
quans = xr.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\histquan_30s.nc")['quan'].values

#Obtain the mask data, which is the same as the cn_mask data.
mask = np.empty((quans.shape[1],quans.shape[2]),dtype=int)
mask[::] = 1
mask[arid>4]=0
mask[temp<273.15]=0
mask[~(np.nanmean(quans,axis=0)>=0.01)]=0

ind = 0
#You can obtain the total data for all years as well as the data for each individual year.
dro_num = np.zeros(mask.shape,dtype=float)

for year in range(0,quans.shape[0],73):
    arr = quans[year:year+73]   #The annual weight data
c
    switch = np.empty(mask.shape,dtype=bool)    #Drought Control Switch
    switch[::] = False
    count = np.zeros(mask.shape,dtype=int)  #Drought day counter
    
    st_switch = np.empty(mask.shape,dtype=bool) #Drought begins to occur
    st_switch[::] = False
    st_count = np.zeros(mask.shape,dtype=int)   #Drought start counter
    
    ed_switch = np.empty(mask.shape,dtype=bool) #Drought end switch
    ed_switch[::] = False
    ed_count = np.zeros(mask.shape,dtype=int)   #Drought End Counter
    
    for i in range(73):
        arr[i][mask==0]=np.nan
        
        st_switch[st_count>5]=False     #When the value exceeds 0.4 and does not drop below 0.2 within 5 pentads, the drought switch is activated.
        
        st_count[(~st_switch)]=0        #When the drought switch is turned off, the drought counter is reset to zero.
        
        ed_count[switch & ed_switch]=-3 #When the drought activation switch and the drought termination switch are both in the on position, 
                                        #the drought termination counter is -3 (distinguished from the drought start counter)
        
        ed_switch[(arr[i]>=0.2) & switch]=True   #When the value is greater than 0.2 and the drought total switch is in the on position, the drought end switch is activated.
        
        ed_switch[(arr[i]<0.2) & switch]=False   #When the value is less than 0.2 and the drought total switch is in the on position, the drought end switch will be turned off.
        
        ed_count[(arr[i]<0.2) & switch]=0   #When the value is less than 0.2 and the drought total switch is in the on position, the drought end counter is reset to zero.
        
        st_switch[arr[i]>=0.4]=True    #When the value is greater than 0.4, the drought switch is activated.
        
        st_count[(arr[i]>=0.4)]=0     #When the value is greater than 0.4, the drought counter is reset to zero.
        
        st_count[st_switch]+=1        #When the drought switch is turned on, the drought counter increments by one.
        
        ed_count[ed_switch]+=1        #When the drought end switch is in the on position, the drought end counter increments by one.
        
        switch[(ed_count==-2) & (ed_switch)] = False   #When the drought counter reaches -2 and the drought end switch is in the on position, the main drought switch will be turned off.
        
        count[(ed_count==-2) & (ed_switch)]-=1  #When the drought counter reaches -2 and the drought end switch is in the on position, the drought day counter is decremented by one (counting is not included during periods less than 0.2).
        
        #TODO
        dro_num[(count>=6) & (count<=18) & (ed_count==-2) & (ed_switch)]+=1  #When the drought day counter is greater than 6 but less than 18, and the drought end counter is -2 while the drought end switch is in the on position, the number of lightning drought occurrences is incremented by one.
        # dro_num[int(year/73)][(count>=6) & (count<=18) & (ed_count==-2) & (ed_switch)]+=1
        
        count[(ed_count==-2) & (ed_switch)] = 0    #When the drought counter reaches -2 and the drought end switch is in the on position, the drought day counter is reset to zero.
        
        ed_switch[(ed_count==-2) & (ed_switch)] = False   #When the drought counter reaches -2 and the drought end switch is in the on position, the drought end switch will be turned off.
        
        ed_count[(ed_count==-2) & (ed_switch)] = 0   #When the drought counter reaches -2 and the drought end switch is in the on position, the drought end counter is reset to zero.
        
        switch[(arr[i]<0.2) & (st_switch)]=True     #When the value is less than 0.2 and the drought start switch is in the on position, the drought master switch is activated.
        
        st_switch[(arr[i]<0.2) & (st_switch)]=False  #When the value is less than 0.2 and the drought start switch is in the on position, the drought start switch will be turned off.
        
        count[switch & (~np.isnan(arr[i]))]+=1  #When the drought switch is in the on position and the pentad weight is not a NaN value, the drought day counter is incremented by one.

    ind+=1


#out = xr.Dataset({'hist':(['time','lat','lon'],dro_num)},{'time':[i for i in range(1980,2015)],'lat':lat,'lon':lon})

# out.to_netcdf(r'D:\\work\\code\\yuan\\data\\CMIP6\\ssp\\hist_30s.nc')

dro_num[mask==0] = np.nan
dro_num[cn_mask==0] = np.nan


#plot

proj = ccrs.PlateCarree(central_longitude=0)
fig = plt.figure(figsize=(6.5,4))
ax = fig.add_axes([0.05, 0.05, 0.9, 0.9], projection=proj)

#Draw a graph showing the number of droughts
colors = ['#00BBFF', '#77DDFF', '#FFFF33','#FF8800','#FF0000'] 
cmap = mpl.colors.ListedColormap(colors)
bounds = [3,5,7,9,11,13]
norm = mpl.colors.BoundaryNorm(bounds, 6)
ap=ax.pcolormesh(lon,lat,dro_num,transform=ccrs.PlateCarree(),cmap=cmap,norm=norm,zorder=10)

#Add national boundaries and the nine-dash line
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省line.shp").geometries()
ax.add_geometries(shp_cn,proj, lw=1, fc='none')
shp_cn = Reader(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp").geometries()
ax.add_geometries(shp_cn,proj, lw=0.3,facecolor='none',zorder=11)

#Resize the map to the Chinese region and add latitude and longitude coordinates.
ax.set_extent([73, 136, 15, 55],crs=ccrs.PlateCarree())
plt.xticks(list(range(75,136,10)),[str(i)+'°E' for i in range(75,136,10)],size=10)
plt.yticks(list(range(15,56,10)),[str(i)+'°N' for i in range(15,56,10)],size=10)
plt.tick_params(direction='in')

#Border bolding and legend
plt.plot([73,136],[15,15],lw=2,c='black',zorder=12)
plt.plot([73,136],[55,55],lw=2,c='black',zorder=12)
plt.plot([73,73],[15,55],lw=2,c='black',zorder=12)
plt.plot([136,136],[15,55],lw=2,c='black',zorder=12)
plt.colorbar(ap,location='bottom',pad = -0.1,shrink=0.3,aspect=12,anchor=(0.1,1.2))

#Add map of the South China Sea Islands
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



    











































