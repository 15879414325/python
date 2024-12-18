# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 19:23:53 2024

@author: 33501

此代码用于处理下载的未来数据
"""
import numpy as np
import xarray as xr
import os
from scipy import ndimage
import rasterio as ra
from osgeo import ogr,gdal
import cftime
import warnings
warnings.filterwarnings("ignore")


def resample(array,target_shape):
    zoom_factors = [target_shape[i] / array.shape[i] for i in range(len(target_shape))]
    resampled_array = ndimage.zoom(array, zoom_factors, order=1)
    return resampled_array


shp = ogr.Open(r"D:\work\code\yuan\data\中国标准行政区划数据GS（2024）0650号\shp格式\中国_省.shp")
lyr = shp.GetLayer()
driver = gdal.GetDriverByName('MEM')
shp_ds_SM = driver.Create('', 273, 221, 1, gdal.GDT_UInt32)
shp_ds_SM.SetProjection('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]')
shp_ds_SM.SetGeoTransform((70,0.25,0,55,0,-0.25))
options = ['ATTRIBUTE=gb']
gdal.RasterizeLayer(shp_ds_SM, [1], lyr, options=options)
cn_mask = shp_ds_SM.ReadAsArray().astype(np.int16)



data = xr.open_dataset(r"D:\work\code\yuan\data\soil_moisture\Nc\swvl30_pentad.nc")
time_sam = data['time'].values
lon_sam = data['lon'].values
lat_sam = data['lat'].values
pentad = data['pentad'].values


# #evp

# evp_hist_dataset = xr.open_dataset(r"D:\work\code\yuan\data\CMIP_all\CMIP\evspsblpot\his\evspsblpot_Emon_IPSL-CM6A-LR_historical_r1i1p1f1_gr_185001-201412.nc")
# # list(evp_hist_dataset.variables)
# lat = evp_hist_dataset['lat'].values
# lon = evp_hist_dataset['lon'].values
# time = list(evp_hist_dataset['time'].values)
# time_bounds = list(evp_hist_dataset['time_bounds'].values)
# evp_hist = evp_hist_dataset['evspsblpot'].values[612:,71:115,28:56]
# evp_hist = resample(evp_hist[:,::-1,:],(evp_hist.shape[0],221,273))
# evp_hist[np.array([cn_mask for i in range(evp_hist.shape[0])])==0]=np.nan
# evp_hist_mean = np.zeros(evp_hist[0].shape)
# evp_hist_mean[:100,:] = np.nanmean(np.array([np.nanmean(evp_hist[i+2:i+10,:100,:],axis=0) for i in range(0,evp_hist.shape[0],12)]),axis=0)
# evp_hist_mean[100:,:] = np.nanmean(np.array([np.nanmean(evp_hist[i:i+12,100:,:],axis=0) for i in range(0,evp_hist.shape[0],12)]),axis=0)
# nc_out = xr.Dataset({'evp':(['lat','lon'],evp_hist_mean)},{'lon':lon_sam,'lat':lat_sam})
# nc_out.to_netcdf(r"D:\work\code\yuan\data\CMIP6\ssp\hist_evp.nc")


# evp_126_dataset = xr.open_dataset(r"D:\work\code\yuan\data\CMIP6\evspsblpot\ssp126\evspsblpot_Emon_IPSL-CM6A-LR_ssp126_r1i1p1f1_gr_201501-210012.nc")
# # list(evp_126_dataset.variables)
# lat = evp_126_dataset['lat'].values
# lon = evp_126_dataset['lon'].values
# time = list(evp_126_dataset['time'].values)
# time_bounds = list(evp_126_dataset['time_bounds'].values)
# evp_126 = evp_126_dataset['evspsblpot'].values[612:,71:115,28:56]
# evp_126 = resample(evp_126[:,::-1,:],(evp_126.shape[0],221,273))
# evp_126[np.array([cn_mask for i in range(evp_126.shape[0])])==0]=np.nan
# evp_126_mean = np.zeros(evp_126[0].shape)
# evp_126_mean[:100,:] = np.nanmean(np.array([np.nanmean(evp_126[i+2:i+10,:100,:],axis=0) for i in range(0,evp_126.shape[0],12)]),axis=0)
# evp_126_mean[100:,:] = np.nanmean(np.array([np.nanmean(evp_126[i:i+12,100:,:],axis=0) for i in range(0,evp_126.shape[0],12)]),axis=0)
# nc_out = xr.Dataset({'evp':(['lat','lon'],evp_126_mean)},{'lon':lon_sam,'lat':lat_sam})
# nc_out.to_netcdf(r"D:\work\code\yuan\data\CMIP6\ssp\ssp126_evp.nc")

# evp_245_dataset = xr.open_dataset(r"D:\work\code\yuan\data\CMIP6\evspsblpot\ssp245\evspsblpot_Emon_IPSL-CM6A-LR_ssp245_r1i1p1f1_gr_201501-210012.nc")
# # list(evp_126_dataset.variables)
# lat = evp_245_dataset['lat'].values
# lon = evp_245_dataset['lon'].values
# time = list(evp_245_dataset['time'].values)
# time_bounds = list(evp_245_dataset['time_bounds'].values)
# evp_245 = evp_245_dataset['evspsblpot'].values[612:,71:115,28:56]
# evp_245 = resample(evp_245[:,::-1,:],(evp_245.shape[0],221,273))
# evp_245[np.array([cn_mask for i in range(evp_245.shape[0])])==0]=np.nan
# evp_245_mean = np.zeros(evp_245[0].shape)
# evp_245_mean[:100,:] = np.nanmean(np.array([np.nanmean(evp_245[i+2:i+10,:100,:],axis=0) for i in range(0,evp_245.shape[0],12)]),axis=0)
# evp_245_mean[100:,:] = np.nanmean(np.array([np.nanmean(evp_245[i:i+12,100:,:],axis=0) for i in range(0,evp_245.shape[0],12)]),axis=0)
# nc_out = xr.Dataset({'evp':(['lat','lon'],evp_245_mean)},{'lon':lon_sam,'lat':lat_sam})
# nc_out.to_netcdf(r"D:\work\code\yuan\data\CMIP6\ssp\ssp245_evp.nc")

# evp_585_dataset = xr.open_dataset(r"D:\work\code\yuan\data\CMIP6\evspsblpot\ssp585\evspsblpot_Emon_IPSL-CM6A-LR_ssp585_r1i1p1f1_gr_201501-210012.nc")
# # list(evp_126_dataset.variables)
# lat = evp_585_dataset['lat'].values
# lon = evp_585_dataset['lon'].values
# time = list(evp_585_dataset['time'].values)
# time_bounds = list(evp_585_dataset['time_bounds'].values)
# evp_585 = evp_585_dataset['evspsblpot'].values[612:,71:115,28:56]
# evp_585 = resample(evp_585[:,::-1,:],(evp_585.shape[0],221,273))
# evp_585[np.array([cn_mask for i in range(evp_585.shape[0])])==0]=np.nan
# evp_585_mean = np.zeros(evp_585[0].shape)
# evp_585_mean[:100,:] = np.nanmean(np.array([np.nanmean(evp_585[i+2:i+10,:100,:],axis=0) for i in range(0,evp_585.shape[0],12)]),axis=0)
# evp_585_mean[100:,:] = np.nanmean(np.array([np.nanmean(evp_585[i:i+12,100:,:],axis=0) for i in range(0,evp_585.shape[0],12)]),axis=0)
# nc_out = xr.Dataset({'evp':(['lat','lon'],evp_585_mean)},{'lon':lon_sam,'lat':lat_sam})
# nc_out.to_netcdf(r"D:\work\code\yuan\data\CMIP6\ssp\ssp585_evp.nc")
# print('evp')




# #mosos

# path_head = r'D:\work\code\yuan\data\CMIP6\mosos'
# folders = os.listdir(path_head)

# #hist
# dataset1 = xr.open_dataset(f"{path_head}\\IPSL-CM6A-LR-INCA_hist\\mrsos_day_IPSL-CM6A-LR-INCA_historical_r1i1p1f1_gr_18500101-20141231.nc")
# lon1 = dataset1['lon'].values
# lat1 = dataset1['lat'].values
# time1 = dataset1['time'].values
# lon_s1 = np.argwhere(((lon1>70)&(lon1<138)))[:,0]
# lat_s1 = np.argwhere(((lat1>=0)&(lat1<=55)))[:,0]
# t_s1 = np.argwhere((time1>=np.datetime64('1980-01-01T12:00:00.000000000'))&(time1<=np.datetime64('2014-12-31T12:00:00.000000000')))[:,0]
# mrsos1 = dataset1['mrsos'][t_s1,lat_s1[0]:lat_s1[-1]+1,lon_s1[0]:lon_s1[-1]+1].values
# # dataset1.variables
# i = 0
# files = os.listdir(f'{path_head}\\MPI-ESM1-2-HR_hist')
# for file in files:
#     if file[-2:]=='nc':
#         try:
#             dataset2 = xr.open_dataset(f'{path_head}\\MPI-ESM1-2-HR_hist\\{file}')
#         except:
#             print(file)
#             continue
            
#         list(dataset2.variables)
#         lon2 = dataset2['lon'].values
#         lat2 = dataset2['lat'].values
#         time2 = dataset2['time'].values
#         lon_s2 = np.argwhere(((lon2>70)&(lon2<138)))[:,0]
#         lat_s2 = np.argwhere(((lat2>0)&(lat2<55)))[:,0]
#         t_s2 = np.argwhere((time2>=np.datetime64('1980-01-01T12:00:00.000000000'))&(time2<=np.datetime64('2014-12-31T12:00:00.000000000')))[:,0]
#         if t_s2.shape[0]==0:
#             continue
#         if i==0:
#             mrsos2 = dataset2['mrsos'][t_s2,lat_s2[0]:lat_s2[-1]+1,lon_s2[0]:lon_s2[-1]+1].values
#             i+=1
#         else:
#             mrsos2 = np.concatenate((mrsos2,dataset2['mrsos'][t_s2,lat_s2[0]:lat_s2[-1]+1,lon_s2[0]:lon_s2[-1]+1].values))
        
# i=0
# files = os.listdir(f'{path_head}\\MPI-ESM1-2-LR_hist')
# for file in files:
#     if file[-2:]=='nc':
#         try:
#             dataset3 = xr.open_dataset(f'{path_head}\\MPI-ESM1-2-LR_hist\\{file}')
#         except:
#             print(file)
#             continue
            
#         list(dataset3.variables)
#         lon3 = dataset3['lon'].values
#         lat3 = dataset3['lat'].values
#         time3 = dataset3['time'].values
#         lon_s3 = np.argwhere(((lon3>70)&(lon3<138)))[:,0]
#         lat_s3 = np.argwhere(((lat3>0)&(lat3<55)))[:,0]
#         t_s3 = np.argwhere((time3>=np.datetime64('1980-01-01T12:00:00.000000000'))&(time3<=np.datetime64('2014-12-31T12:00:00.000000000')))[:,0]
#         if t_s3.shape[0]==0:
#             continue
#         if i==0:
#             mrsos3 = dataset3['mrsos'][t_s3,lat_s3[0]:lat_s3[-1]+1,lon_s3[0]:lon_s3[-1]+1].values
#             i+=1
#         else:
#             mrsos3 = np.concatenate((mrsos3,dataset3['mrsos'][t_s3,lat_s3[0]:lat_s3[-1]+1,lon_s3[0]:lon_s3[-1]+1].values))

# i=0
# ts = []
# files = os.listdir(f'{path_head}\\MRI-ESM2-0_hist')
# for file in files:
#     if file[-2:]=='nc':
#         try:
#             dataset4 = xr.open_dataset(f'{path_head}\\MRI-ESM2-0_hist\\{file}')
#         except:
#             pass
#             print(file)
#         list(dataset4.variables)
#         lon4 = dataset4['lon'].values
#         lat4 = dataset4['lat'].values
#         time4 = dataset4['time'].values
#         lon_s4 = np.argwhere(((lon4>70)&(lon4<138)))[:,0]
#         lat_s4 = np.argwhere(((lat4>0)&(lat4<55)))[:,0]
#         t_s4 = np.argwhere((time4>=np.datetime64('1980-01-01T12:00:00.000000000'))&(time4<=np.datetime64('2014-12-31T12:00:00.000000000')))[:,0]
#         time4 = time4[t_s4]
#         ts+=[(int(str(t).split('-')[0]),int(str(t).split('-')[1]),int(str(t).split('-')[2][:2])) for t in time4]
#         if t_s4.shape[0]==0:
#             continue
#         if i==0:
#             mrsos4 = dataset4['mrsos'][t_s4,lat_s4[0]:lat_s4[-1]+1,lon_s4[0]:lon_s4[-1]+1].values
#             i+=1
#         else:
#             mrsos4 = np.concatenate((mrsos4,dataset4['mrsos'][t_s4,lat_s4[0]:lat_s4[-1]+1,lon_s4[0]:lon_s4[-1]+1].values))


# mrsos = (resample(mrsos1,(mrsos1.shape[0],221,273))+resample(mrsos2,(mrsos2.shape[0],221,273))+resample(mrsos3,(mrsos3.shape[0],221,273))+resample(mrsos3,(mrsos3.shape[0],221,273)))/4
# d = np.argwhere(((np.array(ts)[:,1]==2)&((np.array(ts)[:,2]==29))))
# mrsos = np.delete(mrsos,d[:,0],axis=0)
# mrsos = np.array([np.nanmean(mrsos[i:i+5],axis=0) for i in range(0,mrsos.shape[0],5)])
# mrsos = mrsos[:,::-1,:]
# mrsos[np.array([cn_mask for i in range(mrsos.shape[0])])==0]=np.nan
# mrsos = xr.Dataset({'pentad':(['time','lat','lon'],mrsos)},{'lon':lon_sam,'lat':lat_sam,'time':list(range(1,mrsos.shape[0]+1))})
# mrsos.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\hist_soil.nc')


# #ssp126
# mos_126_1 = 0
# mos_126_2 = 0
# mos_126_3 = 0
# mos_126_4 = 0
# ts=[]
# i = 1
# for folder in folders:
#     if 'ssp126' in folder:
        
#         files = os.listdir(path_head+os.sep+folder)
#         for file in files:
#             if file[-3:] == '.nc':
#                 dataset = xr.open_dataset(path_head+os.sep+folder+os.sep+file)
#                 time = dataset['time'].values
#                 lon = dataset['lon'].values
#                 lat = dataset['lat'].values
#                 mrsos = dataset['mrsos'].values
#                 if type(time[0])==np.datetime64:
#                     w_time = np.argwhere(((time>=np.datetime64('2015-01-01 00:00:00'))&(time<np.datetime64('2101-01-01 00:00:00'))))
#                     if w_time.shape[0]!=0:
#                         ts+=[(int(str(m).split('-')[0]),int(str(m).split('-')[1]),int(str(m).split('-')[2][:2])) for m in time[w_time[0][0]:]]
#                 elif type(time[0])==cftime._cftime.DatetimeGregorian:
#                     w_time = np.argwhere(((time>=cftime.DatetimeGregorian(2015, 1, 1, 0, 0, 0, 0, has_year_zero=False)) & (time<cftime.DatetimeGregorian(2101, 1, 1, 0, 0, 0, 0, has_year_zero=False))))
#                 else:
#                     w_time = np.argwhere(((time>=cftime.DatetimeNoLeap(2015, 1, 1, 0, 0, 0, 0, has_year_zero=True)) & (time<cftime.DatetimeNoLeap(2101, 1, 1, 0, 0, 0, 0, has_year_zero=True))))
#                 if w_time.shape[0]==0:
#                     continue
                
#                 w_lon = np.argwhere((lon>=70) & (lon<=138))
#                 w_lat = np.argwhere((lat>=0) & (lat<=55))
#                 # mrsos = 
#                 if i==1:
#                     if type(mos_126_1)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_126_1=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_126_1=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_126_1=np.concatenate((mos_126_1,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==2:
#                     if type(mos_126_2)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_126_2=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_126_2=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_126_2=np.concatenate((mos_126_2,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==3:
#                     if type(mos_126_3)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_126_3=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_126_3=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_126_3=np.concatenate((mos_126_3,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==4:
#                     if type(mos_126_4)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_126_4=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_126_4=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_126_4=np.concatenate((mos_126_4,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 print(file)
                
#         i+=1



# ts = list(set(ts))
# d = np.argwhere(((np.array(ts)[:,1]==2)&((np.array(ts)[:,2]==29))))
# mos_126_1 = np.delete(mos_126_1,d[:,0],axis=0)
# mos_126_1 = np.array([np.nanmean(mos_126_1[i:i+5],axis=0) for i in range(0,mos_126_1.shape[0],5)])
# mos_126_2 = np.delete(mos_126_2,d[:,0],axis=0)
# mos_126_2 = np.array([np.nanmean(mos_126_2[i:i+5],axis=0) for i in range(0,mos_126_2.shape[0],5)])
# mos_126_3 = np.delete(mos_126_3,d[:,0],axis=0)
# mos_126_3 = np.array([np.nanmean(mos_126_3[i:i+5],axis=0) for i in range(0,mos_126_3.shape[0],5)])
# mos_126_4 = np.delete(mos_126_4,d[:,0],axis=0)
# mos_126_4 = np.array([np.nanmean(mos_126_4[i:i+5],axis=0) for i in range(0,mos_126_4.shape[0],5)])
# out = resample(mos_126_1,(mos_126_1.shape[0],221,273))
# out = out+resample(mos_126_2,(mos_126_2.shape[0],221,273))
# out = out+resample(mos_126_3,(mos_126_3.shape[0],221,273))
# out = out+resample(mos_126_4,(mos_126_4.shape[0],221,273))
# out/=4
# out = out[:,::-1,:]
# out[np.array([cn_mask for i in range(out.shape[0])])==0]=np.nan
# out = xr.Dataset({'pentad':(['time','lat','lon'],out)},{'lon':lon_sam,'lat':lat_sam,'time':list(range(1,out.shape[0]+1))})
# out.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\dry126_soil.nc')
# print('ssp126_soil')

# #ssp245
# mos_245_1 = 0
# mos_245_2 = 0
# mos_245_3 = 0
# mos_245_4 = 0
# ts=[]
# i = 1
# for folder in folders:
#     if '245' in folder:
        
#         files = os.listdir(path_head+os.sep+folder)
#         for file in files:
#             if file[-3:] == '.nc':
#                 dataset = xr.open_dataset(path_head+os.sep+folder+os.sep+file)
#                 time = dataset['time'].values
#                 lon = dataset['lon'].values
#                 lat = dataset['lat'].values
#                 mrsos = dataset['mrsos'].values
#                 if type(time[0])==np.datetime64:
#                     w_time = np.argwhere(((time>=np.datetime64('2015-01-01 00:00:00'))&(time<np.datetime64('2101-01-01 00:00:00'))))
#                     if w_time.shape[0]!=0:
#                         ts+=[(int(str(m).split('-')[0]),int(str(m).split('-')[1]),int(str(m).split('-')[2][:2])) for m in time[w_time[0][0]:]]
#                 elif type(time[0])==cftime._cftime.DatetimeGregorian:
#                     w_time = np.argwhere(((time>=cftime.DatetimeGregorian(2015, 1, 1, 0, 0, 0, 0, has_year_zero=False)) & (time<cftime.DatetimeGregorian(2101, 1, 1, 0, 0, 0, 0, has_year_zero=False))))
#                 else:
#                     w_time = np.argwhere(((time>=cftime.DatetimeNoLeap(2015, 1, 1, 0, 0, 0, 0, has_year_zero=True)) & (time<cftime.DatetimeNoLeap(2101, 1, 1, 0, 0, 0, 0, has_year_zero=True))))
#                 if w_time.shape[0]==0:
#                     continue
                
#                 w_lon = np.argwhere((lon>=70) & (lon<=138))
#                 w_lat = np.argwhere((lat>=0) & (lat<=55))
#                 if i==1:
#                     if type(mos_245_1)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_245_1=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_245_1=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_245_1=np.concatenate((mos_245_1,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==2:
#                     if type(mos_245_2)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_245_2=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_245_2=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_245_2=np.concatenate((mos_245_2,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==3:
#                     if type(mos_245_3)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_245_3=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_245_3=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_245_3=np.concatenate((mos_245_3,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==4:
#                     if type(mos_245_4)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_245_4=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_245_4=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_245_4=np.concatenate((mos_245_4,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 # print(file)
                
#         i+=1



# ts = list(set(ts))
# d = np.argwhere(((np.array(ts)[:,1]==2)&((np.array(ts)[:,2]==29))))
# mos_245_1 = np.delete(mos_245_1,d[:,0],axis=0)
# mos_245_1 = np.array([np.nanmean(mos_245_1[i:i+5],axis=0) for i in range(0,mos_245_1.shape[0],5)])
# mos_245_2 = np.delete(mos_245_2,d[:,0],axis=0)
# mos_245_2 = np.array([np.nanmean(mos_245_2[i:i+5],axis=0) for i in range(0,mos_245_2.shape[0],5)])
# mos_245_3 = np.delete(mos_245_3,d[:,0],axis=0)
# mos_245_3 = np.array([np.nanmean(mos_245_3[i:i+5],axis=0) for i in range(0,mos_245_3.shape[0],5)])
# mos_245_4 = np.delete(mos_245_4,d[:,0],axis=0)
# mos_245_4 = np.array([np.nanmean(mos_245_4[i:i+5],axis=0) for i in range(0,mos_245_4.shape[0],5)])
# out = resample(mos_245_1,(mos_245_1.shape[0],221,273))
# out = out+resample(mos_245_2,(mos_245_2.shape[0],221,273))
# out = out+resample(mos_245_3,(mos_245_3.shape[0],221,273))
# out = out+resample(mos_245_4,(mos_245_4.shape[0],221,273))
# out = out[:,::-1,:]
# out[np.array([cn_mask for i in range(out.shape[0])])==0]=np.nan
# out = xr.Dataset({'pentad':(['time','lat','lon'],out)},{'lon':lon_sam,'lat':lat_sam,'time':list(range(1,out.shape[0]+1))})
# out.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\dry245_soil.nc')
# print('ssp245_soil')



# #ssp585
# mos_585_1 = 0
# mos_585_2 = 0
# mos_585_3 = 0
# mos_585_4 = 0
# ts=[]
# i = 1
# for folder in folders:
#     if '585' in folder:
        
#         files = os.listdir(path_head+os.sep+folder)
#         for file in files:
#             if file[-3:] == '.nc':
#                 dataset = xr.open_dataset(path_head+os.sep+folder+os.sep+file)
#                 time = dataset['time'].values
#                 lon = dataset['lon'].values
#                 lat = dataset['lat'].values
#                 mrsos = dataset['mrsos'].values
#                 if type(time[0])==np.datetime64:
#                     w_time = np.argwhere(((time>=np.datetime64('2015-01-01 00:00:00'))&(time<np.datetime64('2101-01-01 00:00:00'))))
#                     if w_time.shape[0]!=0:
#                         ts+=[(int(str(m).split('-')[0]),int(str(m).split('-')[1]),int(str(m).split('-')[2][:2])) for m in time[w_time[0][0]:]]
#                 elif type(time[0])==cftime._cftime.DatetimeGregorian:
#                     w_time = np.argwhere(((time>=cftime.DatetimeGregorian(2015, 1, 1, 0, 0, 0, 0, has_year_zero=False)) & (time<cftime.DatetimeGregorian(2101, 1, 1, 0, 0, 0, 0, has_year_zero=False))))
#                 else:
#                     w_time = np.argwhere(((time>=cftime.DatetimeNoLeap(2015, 1, 1, 0, 0, 0, 0, has_year_zero=True)) & (time<cftime.DatetimeNoLeap(2101, 1, 1, 0, 0, 0, 0, has_year_zero=True))))
#                 if w_time.shape[0]==0:
#                     continue
                
#                 w_lon = np.argwhere((lon>=70) & (lon<=138))
#                 w_lat = np.argwhere((lat>=0) & (lat<=55))
#                 if i==1:
#                     if type(mos_585_1)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_585_1=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_585_1=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_585_1=np.concatenate((mos_585_1,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==2:
#                     if type(mos_585_2)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_585_2=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_585_2=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_585_2=np.concatenate((mos_585_2,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==3:
#                     if type(mos_585_3)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_585_3=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_585_3=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_585_3=np.concatenate((mos_585_3,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==4:
#                     if type(mos_585_4)==int:
#                         if w_time.shape[0]==mrsos.shape[0]:
#                             mos_585_4=mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         else:
#                             mos_585_4=mrsos[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         mos_585_4=np.concatenate((mos_585_4,mrsos[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 # print(file)
                
#         i+=1



# ts = list(set(ts))
# d = np.argwhere(((np.array(ts)[:,1]==2)&((np.array(ts)[:,2]==29))))
# mos_585_1 = np.delete(mos_585_1,d[:,0],axis=0)
# mos_585_1 = np.array([np.nanmean(mos_585_1[i:i+5],axis=0) for i in range(0,mos_585_1.shape[0],5)])
# mos_585_2 = np.delete(mos_585_2,d[:,0],axis=0)
# mos_585_2 = np.array([np.nanmean(mos_585_2[i:i+5],axis=0) for i in range(0,mos_585_2.shape[0],5)])
# mos_585_3 = np.delete(mos_585_3,d[:,0],axis=0)
# mos_585_3 = np.array([np.nanmean(mos_585_3[i:i+5],axis=0) for i in range(0,mos_585_3.shape[0],5)])
# mos_585_4 = np.delete(mos_585_4,d[:,0],axis=0)
# mos_585_4 = np.array([np.nanmean(mos_585_4[i:i+5],axis=0) for i in range(0,mos_585_4.shape[0],5)])
# out = resample(mos_585_1,(mos_585_1.shape[0],221,273))
# out = out+resample(mos_585_2,(mos_585_2.shape[0],221,273))
# out = out+resample(mos_585_3,(mos_585_3.shape[0],221,273))
# out = out+resample(mos_585_4,(mos_585_4.shape[0],221,273))
# out = out[:,::-1,:]
# out[np.array([cn_mask for i in range(out.shape[0])])==0]=np.nan
# out = xr.Dataset({'pentad':(['time','lat','lon'],out)},{'lon':lon_sam,'lat':lat_sam,'time':list(range(1,out.shape[0]+1))})
# out.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\dry585_soil.nc')
# print('ssp585_soil')












# # pr

# path_head = r"D:\work\code\yuan\data\CMIP_all\CMIP\pr_his"
# folders = os.listdir(path_head)
# ind = 0
# pr_hist = np.zeros((4,221,273))
# for folder in folders:
#     files = os.listdir(path_head+os.sep+folder)
#     temp = 0
#     for file in files:
#         dataset = xr.open_dataset(path_head+os.sep+folder+os.sep+file)
#         time = dataset['time'].values
#         lon = dataset['lon'].values
#         lat = dataset['lat'].values
#         pr = dataset['pr'].values*30
#         if type(time[0])==np.datetime64:
#             w_time = np.argwhere(((time>=np.datetime64('1980-01-01 00:00:00'))&(time<np.datetime64('2015-01-01 00:00:00'))))
#             t = [(int(str(i).split('-')[0]),int(str(i).split('-')[1])) for i in time]
#         elif type(time[0])==cftime._cftime.DatetimeGregorian:
#             w_time = np.argwhere(((time>=cftime.DatetimeGregorian(1980, 1, 1, 0, 0, 0, 0, has_year_zero=False)) & (time<cftime.DatetimeGregorian(2015, 1, 1, 0, 0, 0, 0, has_year_zero=False))))
#             t = [(i.year,i.month,i.day) for i in time]
#         else:
#             w_time = np.argwhere(((time>=cftime.DatetimeNoLeap(1980, 1, 1, 0, 0, 0, 0, has_year_zero=True)) & (time<cftime.DatetimeNoLeap(2015, 1, 1, 0, 0, 0, 0, has_year_zero=True))))
#             t = [(i.year,i.month,i.day) for i in time]
#         if w_time.shape[0]==0:
#             continue
#         t = t[w_time[0,0]:w_time[-1,0]+1]
#         w_lat = np.where(((lat>lat_sam[-1])&(lat<lat_sam[0])))[0]
#         w_lon = np.where((lon>lon_sam[0])&(lon<lon_sam[-1]))[0]
#         lat_c = np.where(lat[w_lat]>30)[0]
#         data_pr = pr[w_time[:,0],w_lat[0]:w_lat[-1]+1,w_lon[0]:w_lon[-1]+1]
#         m = 1
#         y = 0
#         data = np.zeros((int(data_pr.shape[0]/12),data_pr.shape[1],data_pr.shape[2]))
#         for ii in range(len(t)):
#             if m==13:
#                 y+=1
#                 m=1

#             if (t[ii][1]<3) or (t[ii][1]>10):
#                 data_pr[ii,lat_c[0]:lat_c[-1]+1,:]*=0
#             data[y] += data_pr[ii]
#             m+=1
#         if type(temp)==int:
#             temp = data
#         else:
#             temp = np.concatenate((temp,data))
#     temp = np.nanmean(temp,axis=0)
#     pr_hist[ind] = resample(temp,(221,273))
#     ind+=1

# pr_hist = np.nanmean(pr_hist,axis=0)
# pr_hist = pr_hist[::-1,:]
# pr_hist[cn_mask==0]=np.nan
# out = xr.Dataset({'pr':(['lat','lon'],pr_hist)},{'lon':lon_sam,'lat':lat_sam})
# out.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\hist_pr.nc')
# print('hist_pr')


# path_head = r'D:\work\code\yuan\data\CMIP6\pr'
# folders = os.listdir(path_head)

# #ssp126
# pr_126_1 = 0
# pr_126_2 = 0
# pr_126_3 = 0
# pr_126_4 = 0

# i = 1
# for folder in folders:
#     if '126' in folder:
#         files = os.listdir(path_head+os.sep+folder)
#         for file in files:
#             if file[-3:] == '.nc':
#                 dataset = xr.open_dataset(path_head+os.sep+folder+os.sep+file)
#                 time = dataset['time'].values
#                 lon = dataset['lon'].values
#                 lat = dataset['lat'].values
#                 pr = dataset['pr'].values
#                 if type(time[0])==np.datetime64:
#                     w_time = np.argwhere(((time>=np.datetime64('2066-01-01 00:00:00'))&(time<np.datetime64('2101-01-01 00:00:00'))))
#                     t = [int(str(i).split('-')[0]) for i in time]
#                 elif type(time[0])==cftime._cftime.DatetimeGregorian:
#                     w_time = np.argwhere(((time>=cftime.DatetimeGregorian(2066, 1, 1, 0, 0, 0, 0, has_year_zero=False)) & (time<cftime.DatetimeGregorian(2101, 1, 1, 0, 0, 0, 0, has_year_zero=False))))
#                     t = [i.year for i in time]
#                 else:
#                     w_time = np.argwhere(((time>=cftime.DatetimeNoLeap(2066, 1, 1, 0, 0, 0, 0, has_year_zero=True)) & (time<cftime.DatetimeNoLeap(2101, 1, 1, 0, 0, 0, 0, has_year_zero=True))))
#                     t = [i.year for i in time]
#                 if w_time.shape[0]==0:
#                     continue
#                 w_lon = np.argwhere((lon>=70) & (lon<=138))
#                 w_lat = np.argwhere((lat>=0) & (lat<=55))
#                 if w_time.shape[0]==pr.shape[0]:
#                     data = pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                 else:
#                     data = pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                 data = resample(data, (data.shape[0],221,273))
#                 out = np.zeros((np.unique(t[w_time[0][0]:]).shape[0],data.shape[1],data.shape[2]))
#                 p = 0
#                 t = t[w_time[0][0]:]
#                 m = 1
#                 for j,y in enumerate(t):
#                     if j==0:
#                         out[0,:-100,:]+=data[0,:-100,:]
#                         continue
#                     if y==t[j-1]:
#                         m+=1
#                         if (m<60) or (m>304):
#                             out[p,:-100,:]+=data[j,:-100,:]
#                         else:
#                             out[p]+=data[j]
#                     else:
#                         m = 1
#                         p+=1
#                         out[p,:-100,:]+=data[j,:-100,:]
                        
                
#                 if i==1:
#                     if type(pr_126_1)==int:
#                         pr_126_1=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_126_1=data
#                         # else:
#                         #     pr_126_1=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         # pr_126_1=np.concatenate((pr_126_1,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                         pr_126_1=np.concatenate((pr_126_1,out))
#                 if i==2:
#                     if type(pr_126_2)==int:
#                         pr_126_2=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_126_2=pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         # else:
#                         #     pr_126_2=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         pr_126_2=np.concatenate((pr_126_2,out))
#                         # pr_126_2=np.concatenate((pr_126_2,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==3:
                    
#                     if type(pr_126_3)==int:
#                         pr_126_3=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_126_3=pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         # else:
#                         #     pr_126_3=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         pr_126_3=np.concatenate((pr_126_3,out))
#                         # pr_126_3=np.concatenate((pr_126_3,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==4:
#                     if type(pr_126_4)==int:
#                         pr_126_4=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_126_4=pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         # else:
#                         #     pr_126_4=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         pr_126_4=np.concatenate((pr_126_4,out))
#                         # pr_126_4=np.concatenate((pr_126_4,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 # print(file)
#         i+=1


# # out = (resample(pr_126_1,(pr_126_1.shape[0],221,273))+resample(pr_126_2,(pr_126_2.shape[0],221,273))+resample(pr_126_3,(pr_126_3.shape[0],221,273))+resample(pr_126_4,(pr_126_4.shape[0],221,273)))/4
# out = (pr_126_1+pr_126_2+pr_126_3+pr_126_4)/4
# out = np.nanmean(out,axis=0)
# out = out[::-1,:]
# out[cn_mask==0]=np.nan
# out = xr.Dataset({'pr':(['lat','lon'],out)},{'lon':lon_sam,'lat':lat_sam})
# out.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\ssp126_pr.nc')
# print('ssp126_pr')

# #ssp245
# pr_245_1 = 0
# pr_245_2 = 0
# pr_245_3 = 0
# pr_245_4 = 0

# i = 1
# for folder in folders:
#     if '245' in folder:
#         files = os.listdir(path_head+os.sep+folder)
#         for file in files:
#             if file[-3:] == '.nc':
#                 dataset = xr.open_dataset(path_head+os.sep+folder+os.sep+file)
#                 time = dataset['time'].values
#                 lon = dataset['lon'].values
#                 lat = dataset['lat'].values
#                 pr = dataset['pr'].values
#                 if type(time[0])==np.datetime64:
#                     w_time = np.argwhere(((time>=np.datetime64('2066-01-01 00:00:00'))&(time<np.datetime64('2101-01-01 00:00:00'))))
#                     t = [int(str(i).split('-')[0]) for i in time]
#                 elif type(time[0])==cftime._cftime.DatetimeGregorian:
#                     w_time = np.argwhere(((time>=cftime.DatetimeGregorian(2066, 1, 1, 0, 0, 0, 0, has_year_zero=False)) & (time<cftime.DatetimeGregorian(2101, 1, 1, 0, 0, 0, 0, has_year_zero=False))))
#                     t = [i.year for i in time]
#                 else:
#                     w_time = np.argwhere(((time>=cftime.DatetimeNoLeap(2066, 1, 1, 0, 0, 0, 0, has_year_zero=True)) & (time<cftime.DatetimeNoLeap(2101, 1, 1, 0, 0, 0, 0, has_year_zero=True))))
#                     t = [i.year for i in time]
#                 if w_time.shape[0]==0:
#                     continue
#                 w_lon = np.argwhere((lon>=70) & (lon<=138))
#                 w_lat = np.argwhere((lat>=0) & (lat<=55))
#                 if w_time.shape[0]==pr.shape[0]:
#                     data = pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                 else:
#                     data = pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                 data = resample(data, (data.shape[0],221,273))
#                 out = np.zeros((np.unique(t[w_time[0][0]:]).shape[0],data.shape[1],data.shape[2]))
#                 p = 0
#                 t = t[w_time[0][0]:]
#                 m = 1
#                 for j,y in enumerate(t):
#                     if j==0:
#                         out[0,:-100,:]+=data[0,:-100,:]
#                         continue
#                     if y==t[j-1]:
#                         m+=1
#                         if (m<60) or (m>304):
#                             out[p,:-100,:]+=data[j,:-100,:]
#                         else:
#                             out[p]+=data[j]
#                     else:
#                         m = 1
#                         p+=1
#                         out[p,:-100,:]+=data[j,:-100,:]
                        
#                 if i==1:
#                     if type(pr_245_1)==int:
#                         pr_245_1=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_245_1=data
#                         # else:
#                         #     pr_245_1=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         # pr_245_1=np.concatenate((pr_245_1,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                         pr_245_1=np.concatenate((pr_245_1,out))
#                 if i==2:
#                     if type(pr_245_2)==int:
#                         pr_245_2=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_245_2=pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         # else:
#                         #     pr_245_2=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         pr_245_2=np.concatenate((pr_245_2,out))
#                         # pr_245_2=np.concatenate((pr_245_2,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==3:
                    
#                     if type(pr_245_3)==int:
#                         pr_245_3=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_245_3=pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         # else:
#                         #     pr_245_3=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         pr_245_3=np.concatenate((pr_245_3,out))
#                         # pr_245_3=np.concatenate((pr_245_3,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==4:
#                     if type(pr_245_4)==int:
#                         pr_245_4=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_245_4=pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         # else:
#                         #     pr_245_4=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         pr_245_4=np.concatenate((pr_245_4,out))
#                         # pr_245_4=np.concatenate((pr_245_4,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 # print(file)
#         i+=1


# # out = (resample(pr_245_1,(pr_245_1.shape[0],221,273))+resample(pr_245_2,(pr_245_2.shape[0],221,273))+resample(pr_245_3,(pr_245_3.shape[0],221,273))+resample(pr_245_4,(pr_245_4.shape[0],221,273)))/4
# out = (pr_245_1+pr_245_2+pr_245_3+pr_245_4)/4
# out = np.nanmean(out,axis=0)
# out = out[::-1,:]
# out[cn_mask==0]=np.nan
# out = xr.Dataset({'pr':(['lat','lon'],out)},{'lon':lon_sam,'lat':lat_sam})
# out.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\ssp245_pr.nc')
# print('ssp245_pr')



# #ssp585
# pr_585_1 = 0
# pr_585_2 = 0
# pr_585_3 = 0
# pr_585_4 = 0

# i = 1
# for folder in folders:
#     if '585' in folder:
#         files = os.listdir(path_head+os.sep+folder)
#         for file in files:
#             if file[-3:] == '.nc':
#                 dataset = xr.open_dataset(path_head+os.sep+folder+os.sep+file)
#                 time = dataset['time'].values
#                 lon = dataset['lon'].values
#                 lat = dataset['lat'].values
#                 pr = dataset['pr'].values
#                 if type(time[0])==np.datetime64:
#                     w_time = np.argwhere(((time>=np.datetime64('2066-01-01 00:00:00'))&(time<np.datetime64('2101-01-01 00:00:00'))))
#                     t = [int(str(i).split('-')[0]) for i in time]
#                 elif type(time[0])==cftime._cftime.DatetimeGregorian:
#                     w_time = np.argwhere(((time>=cftime.DatetimeGregorian(2066, 1, 1, 0, 0, 0, 0, has_year_zero=False)) & (time<cftime.DatetimeGregorian(2101, 1, 1, 0, 0, 0, 0, has_year_zero=False))))
#                     t = [i.year for i in time]
#                 else:
#                     w_time = np.argwhere(((time>=cftime.DatetimeNoLeap(2066, 1, 1, 0, 0, 0, 0, has_year_zero=True)) & (time<cftime.DatetimeNoLeap(2101, 1, 1, 0, 0, 0, 0, has_year_zero=True))))
#                     t = [i.year for i in time]
#                 if w_time.shape[0]==0:
#                     continue
#                 w_lon = np.argwhere((lon>=70) & (lon<=138))
#                 w_lat = np.argwhere((lat>=0) & (lat<=55))
#                 if w_time.shape[0]==pr.shape[0]:
#                     data = pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                 else:
#                     data = pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                 data = resample(data, (data.shape[0],221,273))
#                 out = np.zeros((np.unique(t[w_time[0][0]:]).shape[0],data.shape[1],data.shape[2]))
#                 p = 0
#                 t = t[w_time[0][0]:]
#                 m = 1
#                 for j,y in enumerate(t):
#                     if j==0:
#                         out[0,100:,:]+=data[0,100:,:]
#                         continue
#                     if y==t[j-1]:
#                         m+=1
#                         if (m<60) or (m>304):
#                             out[p,100:,:]+=data[j,100:,:]
#                         else:
#                             out[p]+=data[j]
#                     else:
#                         m = 1
#                         p+=1
#                         out[p,100:,:]+=data[j,100:,:]
                        
#                 if i==1:
#                     if type(pr_585_1)==int:
#                         pr_585_1=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_585_1=data
#                         # else:
#                         #     pr_585_1=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         # pr_585_1=np.concatenate((pr_585_1,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                         pr_585_1=np.concatenate((pr_585_1,out))
#                 if i==2:
#                     if type(pr_585_2)==int:
#                         pr_585_2=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_585_2=pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         # else:
#                         #     pr_585_2=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         pr_585_2=np.concatenate((pr_585_2,out))
#                         # pr_585_2=np.concatenate((pr_585_2,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==3:
                    
#                     if type(pr_585_3)==int:
#                         pr_585_3=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_585_3=pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         # else:
#                         #     pr_585_3=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         pr_585_3=np.concatenate((pr_585_3,out))
#                         # pr_585_3=np.concatenate((pr_585_3,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 if i==4:
#                     if type(pr_585_4)==int:
#                         pr_585_4=out
#                         # if w_time.shape[0]==pr.shape[0]:
#                         #     pr_585_4=pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                         # else:
#                         #     pr_585_4=pr[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
#                     else:
#                         pr_585_4=np.concatenate((pr_585_4,out))
#                         # pr_585_4=np.concatenate((pr_585_4,pr[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
#                 # print(file)
#         i+=1


# # out = (resample(pr_585_1,(pr_585_1.shape[0],221,273))+resample(pr_585_2,(pr_585_2.shape[0],221,273))+resample(pr_585_3,(pr_585_3.shape[0],221,273))+resample(pr_585_4,(pr_585_4.shape[0],221,273)))/4
# out = (pr_585_1+pr_585_2+pr_585_3+pr_585_4)/4
# out = np.nanmean(out,axis=0)
# out = out[::-1,:]
# out[cn_mask==0]=np.nan
# out = xr.Dataset({'pr':(['lat','lon'],out)},{'lon':lon_sam,'lat':lat_sam})
# out.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\ssp585_pr.nc')
# print('ssp585_pr')



#tas

path_head = r"D:\work\code\yuan\data\CMIP_all\CMIP\tas_his"
folders = os.listdir(path_head)
ind = 0
tas_hist = np.zeros((5,221,273))
for folder in folders:
    files = os.listdir(path_head+os.sep+folder)
    temp = 0
    for file in files:
        dataset = xr.open_dataset(path_head+os.sep+folder+os.sep+file)
        time = dataset['time'].values
        lon = dataset['lon'].values
        lat = dataset['lat'].values
        pr = dataset['tas'].values
        w_lon = np.argwhere((lon>70)&(lon<138))
        w_lat = np.argwhere((lat>70)&(lat<138))
        if type(time[0])==np.datetime64:
            w_time = np.argwhere(((time>=np.datetime64('1980-01-01 00:00:00'))&(time<np.datetime64('2015-01-01 00:00:00'))))
            t = [int(str(i).split('-')[0]) for i in time]
        elif type(time[0])==cftime._cftime.DatetimeGregorian:
            w_time = np.argwhere(((time>=cftime.DatetimeGregorian(1980, 1, 1, 0, 0, 0, 0, has_year_zero=False)) & (time<cftime.DatetimeGregorian(2015, 1, 1, 0, 0, 0, 0, has_year_zero=False))))
            t = [i.year for i in time]
        else:
            w_time = np.argwhere(((time>=cftime.DatetimeNoLeap(1980, 1, 1, 0, 0, 0, 0, has_year_zero=True)) & (time<cftime.DatetimeNoLeap(2015, 1, 1, 0, 0, 0, 0, has_year_zero=True))))
            t = [i.year for i in time]
        if w_time.shape[0]==0:
            continue
        t = t[w_time[0,0]:w_time[-1,0]+1]
        if type(temp)==int:
            temp = pr[w_time[:,0],w_lat[0][0]:w_lat[-1][0],w_lon[0][0]:w_lon[-1][0]]
        else:
            temp = np.concatenate((temp,pr[w_time[:,0],w_lat[0][0]:w_lat[-1][0],w_lon[0][0]:w_lon[-1][0]]))
    temp = np.nanmean(temp,axis=0)
    tas_hist[ind] = resample(temp,(221,273))
    ind+=1

tas_hist = np.nanmean(tas_hist,axis=0)
tas_hist = tas_hist[::-1,:]
tas_hist[cn_mask==0]=np.nan
out = xr.Dataset({'tas':(['lat','lon'],tas_hist)},{'lon':lon_sam,'lat':lat_sam})
out.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\hist_tas.nc')
print('hist_tas')



path_head = r'D:\work\code\yuan\data\CMIP6\tas'
folders = os.listdir(path_head)

#ssp126
tas_126_1 = 0
tas_126_2 = 0
tas_126_3 = 0
tas_126_4 = 0

i = 1
for folder in folders:
    if '126' in folder:
        files = os.listdir(path_head+os.sep+folder)
        for file in files:
            if file[-3:] == '.nc':
                dataset = xr.open_dataset(path_head+os.sep+folder+os.sep+file)
                time = dataset['time'].values
                lon = dataset['lon'].values
                lat = dataset['lat'].values
                tas = dataset['tas'].values
                if type(time[0])==np.datetime64:
                    w_time = np.argwhere(((time>=np.datetime64('2066-01-01 00:00:00'))&(time<np.datetime64('2101-01-01 00:00:00'))))
                    t = [int(str(i).split('-')[0]) for i in time]
                elif type(time[0])==cftime._cftime.DatetimeGregorian:
                    w_time = np.argwhere(((time>=cftime.DatetimeGregorian(2066, 1, 1, 0, 0, 0, 0, has_year_zero=False)) & (time<cftime.DatetimeGregorian(2101, 1, 1, 0, 0, 0, 0, has_year_zero=False))))
                    t = [i.year for i in time]
                else:
                    w_time = np.argwhere(((time>=cftime.DatetimeNoLeap(2066, 1, 1, 0, 0, 0, 0, has_year_zero=True)) & (time<cftime.DatetimeNoLeap(2101, 1, 1, 0, 0, 0, 0, has_year_zero=True))))
                    t = [i.year for i in time]
                if w_time.shape[0]==0:
                    continue
                w_lon = np.argwhere((lon>=70) & (lon<=138))
                w_lat = np.argwhere((lat>=0) & (lat<=55))
                if w_time.shape[0]==tas.shape[0]:
                    data = tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                else:
                    data = tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                print(np.nanmean(data))
                data = resample(data, (data.shape[0],221,273))
                out = np.zeros((np.unique(t[w_time[0][0]:]).shape[0],data.shape[1],data.shape[2]))
                t = t[w_time[0][0]:]
                p = 0
                count=np.zeros(out[0].shape)
                m=1
                for j,y in enumerate(t):
                    if j==0:
                        out[0,100:,:]+=data[0,100:,:]
                        count[100:,:]+=1
                        continue
                    if y==t[j-1]:
                        m+=1
                        if (m<3) or (m>10):
                            out[p,:,:]+=data[j,:,:]
                            count[:,:]+=1
                        else:
                            out[p]+=data[j]
                            count+=1
                    else:
                        out[p]/=count
                        m = 1
                        count[::]=0
                        p+=1
                        out[p,:,:]+=data[j,:,:]
                        count[:,:]+=1       
                out[p]/=count
                # print(np.nanmean(out))
                if i==1:
                    if type(tas_126_1)==int:
                        tas_126_1=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_126_1=data
                        # else:
                        #     tas_126_1=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        # tas_126_1=np.concatenate((tas_126_1,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                        tas_126_1=np.concatenate((tas_126_1,out))
                if i==2:
                    if type(tas_126_2)==int:
                        tas_126_2=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_126_2=tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                        # else:
                        #     tas_126_2=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        tas_126_2=np.concatenate((tas_126_2,out))
                        # tas_126_2=np.concatenate((tas_126_2,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                if i==3:
                    
                    if type(tas_126_3)==int:
                        tas_126_3=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_126_3=tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                        # else:
                        #     tas_126_3=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        tas_126_3=np.concatenate((tas_126_3,out))
                        # tas_126_3=np.concatenate((tas_126_3,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                if i==4:
                    if type(tas_126_4)==int:
                        tas_126_4=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_126_4=tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                        # else:
                        #     tas_126_4=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        tas_126_4=np.concatenate((tas_126_4,out))
                        # tas_126_4=np.concatenate((tas_126_4,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                # print(file)
        i+=1

# out = (resample(tas_126_1,(tas_126_1.shape[0],221,273))+resample(tas_126_2,(tas_126_2.shape[0],221,273))+resample(tas_126_3,(tas_126_3.shape[0],221,273))+resample(tas_126_4,(tas_126_4.shape[0],221,273)))/4
out = (tas_126_1+tas_126_2+tas_126_3+tas_126_4)/4
out = np.nanmean(out,axis=0)
out = out[::-1,:]
out[cn_mask==0]=np.nan
out = xr.Dataset({'tas':(['lat','lon'],out)},{'lon':lon_sam,'lat':lat_sam})
out.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\ssp126_tas.nc')
print('ssp126_tas')




#ssp245
tas_245_1 = 0
tas_245_2 = 0
tas_245_3 = 0
tas_245_4 = 0

i = 1
for folder in folders:
    if '245' in folder:
        files = os.listdir(path_head+os.sep+folder)
        for file in files:
            if file[-3:] == '.nc':
                dataset = xr.open_dataset(path_head+os.sep+folder+os.sep+file)
                time = dataset['time'].values
                lon = dataset['lon'].values
                lat = dataset['lat'].values
                tas = dataset['tas'].values
                if type(time[0])==np.datetime64:
                    w_time = np.argwhere(((time>=np.datetime64('2066-01-01 00:00:00'))&(time<np.datetime64('2101-01-01 00:00:00'))))
                    t = [int(str(i).split('-')[0]) for i in time]
                elif type(time[0])==cftime._cftime.DatetimeGregorian:
                    w_time = np.argwhere(((time>=cftime.DatetimeGregorian(2066, 1, 1, 0, 0, 0, 0, has_year_zero=False)) & (time<cftime.DatetimeGregorian(2101, 1, 1, 0, 0, 0, 0, has_year_zero=False))))
                    t = [i.year for i in time]
                else:
                    w_time = np.argwhere(((time>=cftime.DatetimeNoLeap(2066, 1, 1, 0, 0, 0, 0, has_year_zero=True)) & (time<cftime.DatetimeNoLeap(2101, 1, 1, 0, 0, 0, 0, has_year_zero=True))))
                    t = [i.year for i in time]
                if w_time.shape[0]==0:
                    continue
                w_lon = np.argwhere((lon>=70) & (lon<=138))
                w_lat = np.argwhere((lat>=0) & (lat<=55))
                if w_time.shape[0]==tas.shape[0]:
                    data = tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                else:
                    data = tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                data = resample(data, (data.shape[0],221,273))
                out = np.zeros((np.unique(t[w_time[0][0]:]).shape[0],data.shape[1],data.shape[2]))
                t = t[w_time[0][0]:]
                p = 0
                count=np.zeros(out[0].shape)
                m=1
                for j,y in enumerate(t):
                    if j==0:
                        out[0,:,:]+=data[0,:,:]
                        count[:,:]+=1
                        continue
                    if y==t[j-1]:
                        m+=1
                        if (m<3) or (m>10):
                            out[p,:,:]+=data[j,:,:]
                            count[:,:]+=1
                        else:
                            out[p]+=data[j]
                            count+=1
                    else:
                        out[p]/=count
                        m = 1
                        count[::]=0
                        p+=1
                        out[p,100:,:]+=data[j,100:,:]
                        count[100:,:]+=1
                out[p]/=count
                if i==1:
                    if type(tas_245_1)==int:
                        tas_245_1=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_245_1=data
                        # else:
                        #     tas_245_1=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        # tas_245_1=np.concatenate((tas_245_1,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                        tas_245_1=np.concatenate((tas_245_1,out))
                if i==2:
                    if type(tas_245_2)==int:
                        tas_245_2=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_245_2=tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                        # else:
                        #     tas_245_2=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        tas_245_2=np.concatenate((tas_245_2,out))
                        # tas_245_2=np.concatenate((tas_245_2,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                if i==3:
                    
                    if type(tas_245_3)==int:
                        tas_245_3=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_245_3=tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                        # else:
                        #     tas_245_3=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        tas_245_3=np.concatenate((tas_245_3,out))
                        # tas_245_3=np.concatenate((tas_245_3,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                if i==4:
                    if type(tas_245_4)==int:
                        tas_245_4=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_245_4=tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                        # else:
                        #     tas_245_4=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        tas_245_4=np.concatenate((tas_245_4,out))
                        # tas_245_4=np.concatenate((tas_245_4,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                # print(file)
        i+=1

# out = (resample(tas_245_1,(tas_245_1.shape[0],221,273))+resample(tas_245_2,(tas_245_2.shape[0],221,273))+resample(tas_245_3,(tas_245_3.shape[0],221,273))+resample(tas_245_4,(tas_245_4.shape[0],221,273)))/4
out = (tas_245_1+tas_245_2+tas_245_3+tas_245_4)/4
out = np.nanmean(out,axis=0)
out = out[::-1,:]
out[cn_mask==0]=np.nan
out = xr.Dataset({'tas':(['lat','lon'],out)},{'lon':lon_sam,'lat':lat_sam})
out.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\ssp245_tas.nc')
print('ssp245_tas')


#ssp585
tas_585_1 = 0
tas_585_2 = 0
tas_585_3 = 0
tas_585_4 = 0

i = 1
for folder in folders:
    if '585' in folder:
        files = os.listdir(path_head+os.sep+folder)
        for file in files:
            if file[-3:] == '.nc':
                dataset = xr.open_dataset(path_head+os.sep+folder+os.sep+file)
                time = dataset['time'].values
                lon = dataset['lon'].values
                lat = dataset['lat'].values
                tas = dataset['tas'].values
                if type(time[0])==np.datetime64:
                    w_time = np.argwhere(((time>=np.datetime64('2066-01-01 00:00:00'))&(time<np.datetime64('2101-01-01 00:00:00'))))
                    t = [int(str(i).split('-')[0]) for i in time]
                elif type(time[0])==cftime._cftime.DatetimeGregorian:
                    w_time = np.argwhere(((time>=cftime.DatetimeGregorian(2066, 1, 1, 0, 0, 0, 0, has_year_zero=False)) & (time<cftime.DatetimeGregorian(2101, 1, 1, 0, 0, 0, 0, has_year_zero=False))))
                    t = [i.year for i in time]
                else:
                    w_time = np.argwhere(((time>=cftime.DatetimeNoLeap(2066, 1, 1, 0, 0, 0, 0, has_year_zero=True)) & (time<cftime.DatetimeNoLeap(2101, 1, 1, 0, 0, 0, 0, has_year_zero=True))))
                    t = [i.year for i in time]
                if w_time.shape[0]==0:
                    continue
                w_lon = np.argwhere((lon>=70) & (lon<=138))
                w_lat = np.argwhere((lat>=0) & (lat<=55))
                if w_time.shape[0]==tas.shape[0]:
                    data = tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                else:
                    data = tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                data = resample(data, (data.shape[0],221,273))
                out = np.zeros((np.unique(t[w_time[0][0]:]).shape[0],data.shape[1],data.shape[2]))
                t = t[w_time[0][0]:]
                p = 0
                count=np.zeros(out[0].shape)
                m=1
                for j,y in enumerate(t):
                    if j==0:
                        out[0,:,:]+=data[0,:,:]
                        count[:,:]+=1
                        continue
                    if y==t[j-1]:
                        m+=1
                        if (m<3) or (m>10):
                            out[p,:,:]+=data[j,:,:]
                            count[:,:]+=1
                        else:
                            out[p]+=data[j]
                            count+=1
                    else:
                        out[p]/=count
                        m = 1
                        count[::]=0
                        p+=1
                        out[p,100:,:]+=data[j,100:,:]
                        count[100:,:]+=1
                out[p]/=count
                if i==1:
                    if type(tas_585_1)==int:
                        tas_585_1=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_585_1=data
                        # else:
                        #     tas_585_1=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        # tas_585_1=np.concatenate((tas_585_1,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                        tas_585_1=np.concatenate((tas_585_1,out))
                if i==2:
                    if type(tas_585_2)==int:
                        tas_585_2=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_585_2=tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                        # else:
                        #     tas_585_2=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        tas_585_2=np.concatenate((tas_585_2,out))
                        # tas_585_2=np.concatenate((tas_585_2,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                if i==3:
                    
                    if type(tas_585_3)==int:
                        tas_585_3=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_585_3=tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                        # else:
                        #     tas_585_3=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        tas_585_3=np.concatenate((tas_585_3,out))
                        # tas_585_3=np.concatenate((tas_585_3,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                if i==4:
                    if type(tas_585_4)==int:
                        tas_585_4=out
                        # if w_time.shape[0]==tas.shape[0]:
                        #     tas_585_4=tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                        # else:
                        #     tas_585_4=tas[w_time[0][0]:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1].copy()
                    else:
                        tas_585_4=np.concatenate((tas_585_4,out))
                        # tas_585_4=np.concatenate((tas_585_4,tas[:,w_lat[0][0]:w_lat[-1][0]+1,w_lon[0][0]:w_lon[-1][0]+1]))
                # print(file)
        i+=1

# out = (resample(tas_585_1,(tas_585_1.shape[0],221,273))+resample(tas_585_2,(tas_585_2.shape[0],221,273))+resample(tas_585_3,(tas_585_3.shape[0],221,273))+resample(tas_585_4,(tas_585_4.shape[0],221,273)))/4
out = (tas_585_1+tas_585_2+tas_585_3+tas_585_4)/4
out = np.nanmean(out,axis=0)
out = out[::-1,:]
out[cn_mask==0]=np.nan
out = xr.Dataset({'tas':(['lat','lon'],out)},{'lon':lon_sam,'lat':lat_sam})
out.to_netcdf(r'D:\work\code\yuan\data\CMIP6\ssp\ssp585_tas.nc')
print('ssp585_tas')

























