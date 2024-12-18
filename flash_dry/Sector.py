# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 19:24:56 2024

@author: ql

此代码计算每10年干旱频率平均数，并制作成扇形图
"""

import numpy as np
import pandas as pd
import rasterio
import glob
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from matplotlib.colors import LinearSegmentedColormap
import xarray as xa
from osgeo import gdal
# import ssp_pic


# hist_dataset = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\hist.nc")
# hist_data = hist_dataset['hist'].values
# # hist_era5 = xa.open_dataset(r'D:\work\code\yuan\data\dry.nc')['pl'].values
# ssp585_data = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\dry585.nc")['pl'].values
# blocks = np.concatenate((hist_data,ssp585_data))
# lat = np.argwhere((hist_dataset['lat'].values>21)&(hist_dataset['lat'].values<32))[:,0]
# lon = np.argwhere((hist_dataset['lon'].values>98)&(hist_dataset['lon'].values<123))[:,0]
# cn_mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()
# mask = np.array([cn_mask for i in range(blocks.shape[0])])
# blocks[mask==0]=np.nan
# max_smadi_values = []

# periods = {f"{start_year}-{start_year+19}":(start_year-1980,start_year-1980+20) for start_year in range(2001,2101,20)}
# periods['1980-2000'] = (0,21)

# period_means = {}

# df = pd.DataFrame()
# mask = np.sum(blocks,axis=0)
# for period_name, (start_idx, end_idx) in periods.items():
#     year_sum = np.sum(blocks[start_idx:end_idx],axis=0)
#     df[period_name] = year_sum[~np.isnan(mask)]

# periods1 = np.arange(1980, 2100)

# periods1 = {f"{start_year}-{start_year+10}":(start_year-1980,start_year-1980+10) for start_year in range(1991,2091,10)}
# periods1['1980-1990'] = (0,11)
# periods1['2091-2100'] = (111,121)
# df1 = pd.DataFrame()
# for period_name, (start_idx, end_idx) in periods1.items():
#     year_sum = np.sum(blocks[start_idx:end_idx],axis=0)
#     df1[period_name] = year_sum[~np.isnan(mask)]

# years = np.arange(1981, 2100,10)

# years[0]=1980

# max_smadi_values1 = pd.Series(np.nanmean(df1,axis=0),index=df1.columns)
# max_smadi_values1 = max_smadi_values1.sort_values(ascending=True)
# angles = np.linspace(0, 2 * np.pi, len(max_smadi_values1), endpoint=False).tolist()

# cmap = LinearSegmentedColormap.from_list('custom_cmap', ['#FFFFCB', '#069AF3']) 

# norm = plt.Normalize(min(max_smadi_values1), max(max_smadi_values1))

# # fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(polar=True))
# # ax = plt.subplot(2,2,2, polar=True)
# plt.figure(figsize=(18, 10))
# ax = plt.axes([0.57, 0.51, 0.35, 0.35], polar=True)
# bars = ax.bar(angles, max_smadi_values1, width=0.5, color=cmap(norm(max_smadi_values1)),
#               edgecolor='white', linewidth=1.5)

# plt.yticks(size=0)

# plt.xticks(np.array(angles)+angles[1]/2,['' for i in range(len(np.array(angles)+angles[1]/2))],size=0)

# # ax.plot([0,1000],[3,3])

# for angle, data, lab in zip(angles, max_smadi_values1, list(max_smadi_values1.index)):
#     ax.text(angle + 0.03, np.nanmax(max_smadi_values1)+np.nanmean(max_smadi_values1)*0.28, lab, 
#             horizontalalignment='center', 
#             verticalalignment='center_baseline',size=8)  # 将标签对齐到数据点的下方

# # ax.set_axis_off()



# sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# sm.set_array([])
# cbar = plt.colorbar(sm, ax=ax, shrink=0.9, pad=0.1,label='Frequency')
# # cbar.set_label('CHN_Wheat SMADI')
# # plt.show()
# # plt.savefig(r'D:\work\code\yuan\图\flash_dry\DT585.tif')


#打包成函数便于画图
def ST(code):
    if code == 126:
        pos = (2/3)
    if code == 245:
        pos = (1/3)
    if code == 585:
        pos = 0
    #获取所需数据
    hist_dataset = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\hist_30s.nc")
    hist_data = hist_dataset['hist'].values
    # hist_era5 = xa.open_dataset(r'D:\work\code\yuan\data\dry.nc')['pl'].values
    ssp585_data = xa.open_dataset(f"D:\\work\\code\\yuan\\data\\CMIP6\\ssp\\dry{code}_30s.nc")['pl'].values
    blocks = np.concatenate((hist_data,ssp585_data))
    lat = np.argwhere((hist_dataset['lat'].values>21)&(hist_dataset['lat'].values<32))[:,0]
    lon = np.argwhere((hist_dataset['lon'].values>98)&(hist_dataset['lon'].values<123))[:,0]
    cn_mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()
    mask = np.array([cn_mask for i in range(blocks.shape[0])])
    blocks[mask==0]=np.nan
    
    max_smadi_values = []
    
    periods = {f"{start_year}-{start_year+19}":(start_year-1980,start_year-1980+20) for start_year in range(2001,2101,20)}
    periods['1980-2000'] = (0,21)
    
    period_means = {}
    
    mask = np.sum(blocks,axis=0)

    periods1 = np.arange(1980, 2100)
    
    #将数据整理成每十年平均值
    periods1 = {f"{start_year}-{start_year+10}":(start_year-1980,start_year-1980+10) for start_year in range(1991,2091,10)}
    periods1['1980-1990'] = (0,11)
    periods1['2091-2100'] = (111,121)
    df1 = pd.DataFrame()
    for period_name, (start_idx, end_idx) in periods1.items():
        year_sum = np.sum(blocks[start_idx:end_idx],axis=0)
        df1[period_name] = year_sum[~np.isnan(mask)]
    
    years = np.arange(1981, 2100,10)
    years[0]=1980
    
    #对所求平均值进行排序
    max_smadi_values1 = pd.Series(np.nanmean(df1,axis=0),index=df1.columns)
    max_smadi_values1 = max_smadi_values1.sort_values(ascending=True)
    
    #设置每10年数据的扇形角度
    angles = np.linspace(0, 2 * np.pi, len(max_smadi_values1), endpoint=False).tolist()
    
    #绘图
    cmap = LinearSegmentedColormap.from_list('custom_cmap', ['#FFFFCB', '#069AF3']) 
    norm = plt.Normalize(min(max_smadi_values1), max(max_smadi_values1))
    
    ax = plt.axes([0.57, 0.51/3+pos, 0.35, 0.35/3], polar=True)
    bars = ax.bar(angles, max_smadi_values1, width=0.5, color=cmap(norm(max_smadi_values1)),
                  edgecolor='white', linewidth=1.5)
    
    plt.yticks(size=0)
    
    plt.xticks(np.array(angles)+angles[1]/2,['' for i in range(len(np.array(angles)+angles[1]/2))],size=0)

    for angle, data, lab in zip(angles, max_smadi_values1, list(max_smadi_values1.index)):
        ax.text(angle + 0.03, np.nanmax(max_smadi_values1)+np.nanmean(max_smadi_values1)*0.28, lab, 
                horizontalalignment='center', 
                verticalalignment='center_baseline',size=5)  # 将标签对齐到数据点的下方
    
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.9, pad=0.1,label='Frequency')

    # plt.savefig(r'D:\work\code\yuan\图\flash_dry\DT585.tif')













