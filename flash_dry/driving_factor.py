# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 17:10:18 2024

@author: 33501

此代码分析闪电干旱频率、降水、潜在蒸散、根区土壤湿度的三个未来情景与历史的差异
"""
import xarray as xa
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from osgeo import ogr,gdal
from scipy import stats

#大体类似闪电干旱识别代码，并打包成函数减少代码复用
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


#获取权重数据
swvl_quan126 = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\ssp126_quan_era5.nc")['quan'].values
swvl_quan245 = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\ssp126_quan_era5.nc")['quan'].values
swvl_quan585 = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\ssp126_quan_era5.nc")['quan'].values
swvl_quan = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_quan.nc')['quan'].values

#利用权重数据获取干旱频率数据
dry126 = detect_dry(swvl_quan126,swvl_quan126[30])
dry245 = detect_dry(swvl_quan245,swvl_quan245[30])
dry585 = detect_dry(swvl_quan585,swvl_quan585[30])
dry = detect_dry(swvl_quan,swvl_quan126[30])

#获取各个mask数据
cn_mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()
ssp_mask = np.array([cn_mask for i in range(swvl_quan126.shape[0])])
hist_mask = np.array([cn_mask for i in range(swvl_quan.shape[0])])

#对权重数据进行掩膜处理
swvl_quan126[ssp_mask==0] = np.nan
swvl_quan245[ssp_mask==0] = np.nan
swvl_quan585[ssp_mask==0] = np.nan
swvl_quan[hist_mask==0] = np.nan

#去除干旱频率为零的值
dry126[(dry126==0)|(dry==0)]=np.nan
dry245[(dry245==0)|(dry==0)]=np.nan
dry585[(dry585==0)|(dry==0)]=np.nan

#计算干旱频率历史未来变化
change126 = (dry126-dry)/(dry+dry126)
change245 = (dry245-dry)/(dry+dry245)
change585 = (dry585-dry)/(dry+dry585)

#获取潜在蒸散数据，进行掩膜处理，并计算变化
ssp126_evp = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp126_evp.nc')['evp'].values
ssp245_evp = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp245_evp.nc')['evp'].values
ssp585_evp = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp585_evp.nc')['evp'].values
hist_evp = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\hist_evp.nc")['evp'].values

ssp126_evp[cn_mask==0] = np.nan
ssp245_evp[cn_mask==0] = np.nan
ssp585_evp[cn_mask==0] = np.nan
hist_evp[cn_mask==0] = np.nan

change_evp126 = (ssp126_evp-hist_evp)/(hist_evp+ssp126_evp)
change_evp245 = (ssp245_evp-hist_evp)/(hist_evp+ssp245_evp)
change_evp585 = (ssp585_evp-hist_evp)/(hist_evp+ssp585_evp)


#获取潜在降水数据，进行掩膜处理，并计算变化
ssp126_pr = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp126_pr.nc')['pr'].values
ssp245_pr = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp245_pr.nc')['pr'].values
ssp585_pr = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp585_pr.nc')['pr'].values
hist_pr = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\hist_pr.nc')['pr'].values

ssp126_pr[cn_mask==0] = np.nan
ssp245_pr[cn_mask==0] = np.nan
ssp585_pr[cn_mask==0] = np.nan
hist_pr[cn_mask==0] = np.nan

change_pr126 = (ssp126_pr-hist_pr)/(hist_pr+ssp126_pr)
change_pr245 = (ssp245_pr-hist_pr)/(hist_pr+ssp245_pr)
change_pr585 = (ssp585_pr-hist_pr)/(hist_pr+ssp585_pr)

#获取潜在土壤湿度数据，进行掩膜处理，并计算变化
ssp126_soil = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp126_soil.nc')['pentad'].values
ssp245_soil = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp245_soil.nc')['pentad'].values
ssp585_soil = xa.open_dataset(r'D:\work\code\yuan\data\CMIP6\ssp\ssp585_soil.nc')['pentad'].values
hist_soil = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\hist_soil.nc")['pentad'].values

ssp126_soil[ssp_mask==0] = np.nan
ssp245_soil[ssp_mask==0] = np.nan
ssp585_soil[ssp_mask==0] = np.nan
hist_soil[hist_mask==0] = np.nan

change_soil126 = np.nanmean((ssp126_soil-hist_soil)/(hist_soil+ssp126_soil),axis=0)
change_soil245 = np.nanmean((ssp245_soil-hist_soil)/(hist_soil+ssp245_soil),axis=0)
change_soil585 = np.nanmean((ssp585_soil-hist_soil)/(hist_soil+ssp585_soil),axis=0)

#求各个数据的中位数
S126_south = np.nanpercentile(change126[92:137,112:213],50)
evp126_south = np.nanpercentile(change_evp126[92:137,112:213],50)
pr126_south = np.nanpercentile(change_pr126[92:137,112:213],50)
soil126_south = np.nanpercentile(change_soil126[92:137,112:213],50)

S245_south = np.nanpercentile(change245[92:137,112:213],50)
evp245_south = np.nanpercentile(change_evp245[92:137,112:213],50)
pr245_south = np.nanpercentile(change_pr245[92:137,112:213],50)
soil245_south = np.nanpercentile(change_soil245[92:137,112:213],50)

S585_south = np.nanpercentile(change585[92:137,112:213],50)
evp585_south = np.nanpercentile(change_evp585[92:137,112:213],50)
pr585_south = np.nanpercentile(change_pr585[92:137,112:213],50)
soil585_south = np.nanpercentile(change_soil585[92:137,112:213],50)

S126_north = np.nanpercentile(change126[52:92,112:225],50)
evp126_north = np.nanpercentile(change_evp126[52:92,112:225],50)
pr126_north = np.nanpercentile(change_pr126[52:92,112:225],50)
soil126_north = np.nanpercentile(change_soil126[52:92,112:225],50)

S245_north = np.nanpercentile(change245[52:92,112:225],50)
evp245_north = np.nanpercentile(change_evp245[52:92,112:225],50)
pr245_north = np.nanpercentile(change_pr245[52:92,112:225],50)
soil245_north = np.nanpercentile(change_soil245[52:92,112:225],50)

S585_north = np.nanpercentile(change585[52:92,112:225],50)
evp585_north = np.nanpercentile(change_evp585[52:92,112:225],50)
pr585_north = np.nanpercentile(change_pr585[52:92,112:225],50)
soil585_north = np.nanpercentile(change_soil585[52:92,112:225],50)

S126_northeast = np.nanpercentile(change126[12:52,196:261],50)
evp126_northeast = np.nanpercentile(change_evp126[12:52,196:261],50)
pr126_northeast = np.nanpercentile(change_pr126[12:52,196:261],50)
soil126_northeast = np.nanpercentile(change_soil126[12:52,196:261],50)

S245_northeast = np.nanpercentile(change245[12:52,196:261],50)
evp245_northeast = np.nanpercentile(change_evp245[12:52,196:261],50)
pr245_northeast = np.nanpercentile(change_pr245[12:52,196:261],50)
soil245_northeast = np.nanpercentile(change_soil245[12:52,196:261],50)

S585_northeast = np.nanpercentile(change585[12:52,196:261],50)
evp585_northeast = np.nanpercentile(change_evp585[12:52,196:261],50)
pr585_northeast = np.nanpercentile(change_pr585[12:52,196:261],50)
soil585_northeast = np.nanpercentile(change_soil585[12:52,196:261],50)

#画图
fig, ax = plt.subplots(figsize=(36,8))
ax1 = plt.subplot(1,3,1)
center = np.array([0.5,1.5,2.5,3.5])
plt.bar(center-0.2,[S126_south,evp126_south,pr126_south,soil126_south],width=0.19,color='#8ECFC9',label='SSP126')
plt.bar(center,[S245_south,evp245_south,pr245_south,soil245_south],width=0.19,color='#FFBE7A',label='SSP245')
plt.bar(center+0.2,[S585_south,evp585_south,pr585_south,soil585_south],width=0.19,color='#FA7F6F',label='SSP585')

plt.ylim((-0.1,0.5))
plt.xlim((0,4))

ax1.axhline(0, 0, 5,color='#000000',lw=1)

plt.xticks([0.5,1.5,2.5,3.5],['FD','P','PET','RZSM'],size=20,weight='bold')
plt.yticks([-0.1,0,0.1,0.2,0.3,0.4,0.5],[-10,0,10,20,30,40,50],size=20,weight='bold')

plt.title('South',size=30,weight='bold')
plt.legend(edgecolor='none',handleheight=2,handlelength=4)
ax1.spines[['left','bottom','top', 'right']].set_linewidth(2)


ax1 = plt.subplot(1,3,2)
center = np.array([0.5,1.5,2.5,3.5])
plt.bar(center-0.2,[S126_north,evp126_north,pr126_north,soil126_north],width=0.19,color='#8ECFC9',label='SSP126')
plt.bar(center,[S245_north,evp245_north,pr245_north,soil245_north],width=0.19,color='#FFBE7A',label='SSP245')
plt.bar(center+0.2,[S585_north,evp585_north,pr585_north,soil585_north],width=0.19,color='#FA7F6F',label='SSP585')

plt.ylim((-0.1,0.5))
plt.xlim((0,4))

ax1.axhline(0, 0, 5,color='#000000',lw=1)

plt.xticks([0.5,1.5,2.5,3.5],['FD','P','PET','RZSM'],size=20,weight='bold')
plt.yticks([-0.1,0,0.1,0.2,0.3,0.4,0.5],[-10,0,10,20,30,40,50],size=20,weight='bold')

plt.title('North',size=30,weight='bold')
plt.legend(edgecolor='none',handleheight=2,handlelength=4)
ax1.spines[['left','bottom','top', 'right']].set_linewidth(2)


ax1 = plt.subplot(1,3,3)
center = np.array([0.5,1.5,2.5,3.5])
plt.bar(center-0.2,[S126_northeast,evp126_northeast,pr126_northeast,soil126_northeast],width=0.19,color='#8ECFC9',label='SSP126')
plt.bar(center,[S245_northeast,evp245_northeast,pr245_northeast,soil245_northeast],width=0.19,color='#FFBE7A',label='SSP245')
plt.bar(center+0.2,[S585_northeast,evp585_northeast,pr585_northeast,soil585_northeast],width=0.19,color='#FA7F6F',label='SSP585')

plt.ylim((-0.1,0.5))
plt.xlim((0,4))

ax1.axhline(0, 0, 5,color='#000000',lw=1)

plt.xticks([0.5,1.5,2.5,3.5],['FD','P','PET','RZSM'],size=20,weight='bold')
plt.yticks([-0.1,0,0.1,0.2,0.3,0.4,0.5],[-10,0,10,20,30,40,50],size=20,weight='bold')

plt.title('Northeast',size=30,weight='bold')
plt.legend(edgecolor='none',handleheight=2,handlelength=4)
ax1.spines[['left','bottom','top', 'right']].set_linewidth(2)

# plt.savefig(r'D:\work\code\yuan\图\flash_dry\柱状图.tif',dpi=600)


