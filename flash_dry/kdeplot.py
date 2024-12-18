# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 08:50:17 2024

@author: 33501

对每20年干旱频率数据进行块自举法，得到核密度图
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xa
import os
import pandas as pd
import seaborn as sns
from osgeo import gdal
# import Decision_Tree

#将块自举法打包成函数，便于绘图
def kplot(path_head,dataname):
    if '126' in dataname:
        pos = 2/3
    if '245' in dataname:
        pos = 1/3
    if '585' in dataname:
        pos = 0
        
    #获取所需数据
    hist_dataset = xa.open_dataset(r"D:\work\code\yuan\data\CMIP6\ssp\hist_30s.nc")
    hist_data = hist_dataset['hist'].values
    # hist_era5 = xa.open_dataset(r'D:\work\code\yuan\data\dry.nc')['pl'].values
    ssp126_data = xa.open_dataset(path_head)['pl'].values
    blocks = np.concatenate((hist_data,ssp126_data))
    cn_mask = gdal.Open(r"D:\work\code\yuan\data\mask.tif").ReadAsArray()
    mask = np.array([cn_mask for i in range(blocks.shape[0])])
    blocks[mask==0]=np.nan
    # a = list(hist_dataset['time'].values)
    
    #将数据处理成每20年数据
    data_1980_2000 = np.nansum(blocks[0:21],axis=0)
    data_2001_2020 = np.nansum(blocks[21:41],axis=0)
    data_2021_2040 = np.nansum(blocks[41:61],axis=0)
    data_2041_2060 = np.nansum(blocks[61:81],axis=0)
    data_2061_2080 = np.nansum(blocks[81:101],axis=0)
    data_2081_2100 = np.nansum(blocks[101:121],axis=0)
    lat = np.argwhere((hist_dataset['lat'].values>21)&(hist_dataset['lat'].values<32))[:,0]
    lon = np.argwhere((hist_dataset['lon'].values>98)&(hist_dataset['lon'].values<123))[:,0]
    
    
    #定义块自举函数
    def block_bootstrap(data, block_size, n_samples=1000):
        n = len(data)
        n_blocks = n // block_size
        bootstrap_samples = np.zeros(n_samples)
        
        for i in range(n_samples):
            blocks = np.random.choice(range(n_blocks), size=n_blocks, replace=True)
            bootstrap_sample = []
            for block in blocks:
                bootstrap_sample.extend(data[block * block_size : (block + 1) * block_size])
            bootstrap_samples[i] = np.mean(bootstrap_sample)
        
        return bootstrap_samples
    
    #用块自举法处理数据
    block_size = 3
    bootstrap_1980_2000 = block_bootstrap(data_1980_2000[~np.isnan(data_1980_2000)], block_size)
    bootstrap_2001_2020 = block_bootstrap(data_2001_2020[~np.isnan(data_2001_2020)], block_size)
    bootstrap_2021_2040 = block_bootstrap(data_2021_2040[~np.isnan(data_2021_2040)], block_size)
    bootstrap_2041_2060 = block_bootstrap(data_2041_2060[~np.isnan(data_2041_2060)], block_size)
    bootstrap_2061_2080 = block_bootstrap(data_2061_2080[~np.isnan(data_2061_2080)], block_size)
    bootstrap_2081_2100 = block_bootstrap(data_2081_2100[~np.isnan(data_2081_2100)], block_size)
    
    #出图
    plt.axes([0.61, 0.1/3+pos, 0.35, 0.35/3])
    sns.kdeplot(bootstrap_1980_2000,label = "1980-2000",shade=True,fill=True)
    sns.kdeplot(bootstrap_2001_2020,label = "2001-2020",shade=True,fill=True)
    sns.kdeplot(bootstrap_2021_2040,label = "2021-2040",shade=True,fill=True)
    sns.kdeplot(bootstrap_2041_2060,label = "2041-2060",shade=True,fill=True)
    sns.kdeplot(bootstrap_2061_2080,label = "2061-2080",shade=True,fill=True)
    sns.kdeplot(bootstrap_2081_2100,label = "2081-2100",shade=True,fill=True)
    plt.xlabel('Flash drought frequency')
    plt.ylabel('Frequency of occurrence (%)')
    plt.legend(fontsize=5)
    # plt.title(f'ssp{dataname[3:]}')
    # plt.show()
    # plt.savefig(f'D:\\work\\code\\yuan\\图\\flash_dry\\pic3_{dataname}.tif',dpi=600)

# kplot(r"D:\work\code\yuan\data\CMIP6\ssp\dry126.nc",'dry126')
# kplot(r"D:\work\code\yuan\data\CMIP6\ssp\dry245.nc",'dry245')
# kplot(r"D:\work\code\yuan\data\CMIP6\ssp\dry585.nc",'dry585')




