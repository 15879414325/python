# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 16:12:58 2024

@author: 33501
"""
import os
from PIL import Image
import numpy as np
from timeit import default_timer as timer
# from _snic.lib import SNIC_main
from ctypes import POINTER, c_int, c_double, cdll
import functools
import time
from osgeo import gdal
from scipy import ndimage



snic = cdll.LoadLibrary(r'./snic.dll')

def segment(img,numsuperpixels,compactness,doRGBtoLAB):
    """
    对影像进行处理并调用c语言程序进行超像素分割
    """
    
	#--------------------------------------------------------------
	# 将影像矩阵的形状由 (h,w,c) 转变为 (c,h,w)
	#--------------------------------------------------------------
    dims = img.shape
    h,w,c = dims[0],dims[1],1
    if len(dims) > 1:
        c = dims[2]
        img = img.transpose(2,0,1)
 	
	#--------------------------------------------------------------
	# 将影像矩阵变成一维数组
	#--------------------------------------------------------------
    img = img.reshape(-1).astype(np.double)
    labels = np.zeros((h,w), dtype = np.int32)
    numlabels = np.zeros(1,dtype = np.int32)
	#--------------------------------------------------------------
	# 准备传递给c语言函数的指针
	#--------------------------------------------------------------
    pinp = img.ctypes.data_as(POINTER(c_double))
    plabels = labels.reshape(-1).ctypes.data_as(POINTER(c_int))
    pnumlabels = numlabels.ctypes.data_as(POINTER(c_int))
    compactness_c = c_double(compactness)

    snic.SNIC_main(pinp,w,h,c,numsuperpixels,compactness_c,doRGBtoLAB,plabels,pnumlabels)

    return labels.reshape(h,w),numlabels[0]

def drawBoundaries(img,labels,numlabels):
    """
    将分割结果以0为边界分隔开来
    """
    ht,wd = labels.shape

    for y in range(1,ht-1):
        for x in range(1,wd-1):
            if labels[y,x-1] != labels[y,x+1] or labels[y-1,x] != labels[y+1,x]:
                img[y,x,:] = 0

    return img
	

def snicdemo(img):
    """
    进行超像素分割
    """
	#--------------------------------------------------------------
	# 输入参数并调用函数
	#--------------------------------------------------------------
    numsuperpixels = 30000 #种子数
    compactness = 20 #紧凑度
    doRGBtoLAB = True # 如果输入的格式为rgb，则将其转化为lab格式
    labels,numlabels = segment(img,numsuperpixels,compactness,doRGBtoLAB)
    
    #--------------------------------------------------------------
    # 绘制分割边框
    #------------------------------------------------------------
    segimg = drawBoundaries(img,labels,numlabels)
    
    return segimg

def get_neighbors(x, y, shape):
    """获取单元格(x, y)的有效相邻值"""
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < shape[0] and 0 <= ny < shape[1]:
            neighbors.append((nx, ny))
    return neighbors

def dfs(x, y, im_arr, visited,limit=0):
    """执行DFS(深度优先)查找连通区域内的所有单元格"""
    stack = [(x, y)]
    region = []
    
    while stack:
        cx, cy = stack.pop()
        if visited[cx, cy] or im_arr[cx, cy] in limit:
            continue
        visited[cx, cy] = True
        region.append((cx, cy))
        
        for nx, ny in get_neighbors(cx, cy, im_arr.shape):
            if not visited[nx, ny] and im_arr[nx, ny] not in limit:
                stack.append((nx, ny))
    
    return region

def find_connected_regions(im_arr,limit=[0]):
    """找到array内所有连通区域"""
    visited = np.zeros(im_arr.shape, dtype=bool)
    regions = []
    
    for x in range(im_arr.shape[0]):
        for y in range(im_arr.shape[1]):
            if not visited[x, y] and im_arr[x, y] not in  limit:
                region = dfs(x, y, im_arr, visited,limit=limit)
                if region:
                    regions.append(region)
    
    return regions


def deal_zero(pos,im_arr):
    """对array内的0值即区域边界进行处理"""
    x,y = pos
    vs = []
    r=0
    while(1):
        y_flag = False
        x_flag = False
        r+=1

        if (y+r<im_arr.shape[1]) and (y-r>=0):
            for add in range(0,r+1):

                if 0<=x+add<im_arr.shape[0]:
                    vs.append(im_arr[x+add,y+r])
                    vs.append(im_arr[x+add,y-r])

                if 0<=x-add<im_arr.shape[0]:
                    vs.append(im_arr[x-add,y+r])
                    vs.append(im_arr[x-add,y-r])
        else:
            y_flag = True
        
        if (x+r<im_arr.shape[0]) and (x-r>=0):
            for add in range(0,r):

                if 0<=y+add<im_arr.shape[1]:
                    vs.append(im_arr[x+r,y+add])
                    vs.append(im_arr[x-r,y+add])

                if 0<=y-add<im_arr.shape[1]:
                    vs.append(im_arr[x+r,y-add])
                    vs.append(im_arr[x-r,y-add])
        else:
            x_flag =True

        if y_flag and x_flag:
            return 1
        if sum(vs) !=0:
            break

    if sum(vs) >0:
        return 1
    if sum(vs) <0:
        return -1

def write_f(para,data,out_path,datatype = gdal.GDT_Float32):
    """
    将array数据导出成tif文件

    参数
    ----------
    para : gdal.Dataset
        模板数据，用于得到输出影像属性
    data : numpy.array
        需导出的array数据

    返回值
    -------
    无返回值,运行直接保存

    """

    driver   = gdal.GetDriverByName("GTiff")       # 明确写入数据驱动类型
    out      = driver.Create(out_path,
                             para.RasterXSize,
                             para.RasterYSize,
                             len(data),
                             datatype)             # 数据类型
    out.SetProjection(para.GetProjection())        # 设置一致的投影信息
    # print(para.GetProjection())
    out.SetGeoTransform(para.GetGeoTransform())
    # print(para.GetGeoTransform())
    for i in range(len(data)):
        out.GetRasterBand(i+1).WriteArray(data[i])
    del out

#Flag用于进行特殊处理
Flag = True


if Flag:
    path_head = r'D:\work\code\img_classify\use_image'
    path_out = r'D:\work\code\img_classify\output'
    
    #各个年份所取的粗略植被指数
    dic = {'2018':0.03,'2019':-0.02,'2020':0.035,'2021':0.04,'2022':0.05,'2023':-0.015}
    
    
    
    for year in [
                    # '2019-06',
                    # '2019-09',
                    # '2019-10',
                    # '2018',
                    '2019',
                    # '2020',
                    # '2021',
                    # '2022',
                    # '2023'
                  ]:
        im_paths = os.listdir(path_head+os.sep+year)
        if not os.path.exists(path_out+os.sep+year):
            os.makedirs(path_out+os.sep+year)
            os.makedirs(path_out+os.sep+year+os.sep+'index_classify')
            os.makedirs(path_out+os.sep+year+os.sep+'first_classify')
            os.makedirs(path_out+os.sep+year+os.sep+'deep_classify')
            os.makedirs(path_out+os.sep+year+os.sep+'class')
            os.makedirs(path_out+os.sep+year+os.sep+'label')
        for im_path in im_paths:
            if im_path[-3:] == 'tif':
                #超像素分割
                # print("开始超像素分割")
                source_geo = gdal.Open(path_head+os.sep+year+os.sep+im_path)
                # source_image = Image.open(path_head+os.sep+year+os.sep+im_path)
                source_im_arr = source_geo.ReadAsArray().astype(np.float64).transpose(1,2,0)
                
                # source_im_arr = np.array(source_image,dtype=float)
                # regions = find_connected_regions(source_im_arr[:,:,1],limit=[65535])
                # for r in regions:
                #     if np.mean([source_im_arr[:,:,1][x,y] for x,y in r]) == 256:
                #         for x,y in r:
                #             source_im_arr[x,y,:] = 65535
                
                source_im_arr_copy = source_im_arr.copy()
                seg_im_arr = snicdemo(source_im_arr_copy) #进行超像素分割
                
                seg_im_arr[source_im_arr==65535] = 0 #65535为影像无效值
                source_im_arr[source_im_arr==65535] = np.nan
                
                
                #初步分类
                # print("开始初步分类")
                
                #获取rgb波段以计算NGRDI指数
                red = source_im_arr[:,:,0]
                green = source_im_arr[:,:,1]
                blue = source_im_arr[:,:,2]
                ngrdi_value = (green - red) / (green + red)
                
                # write_f(source_geo,[ngrdi_value],r"D:\work\code\img_classify\use_image\ex\ngrdi.tif")
                
                # index_range = []
                # for i in range(-30,30):
                #     index_range.append(len(ngrdi_value[(ngrdi_value>i*0.01) & (ngrdi_value<(i+1)*0.01)]))
                # for i in range(0,100):
                #     index_range.append(np.percentile(ngrdi_value[~np.isnan(ngrdi_value)],i))
                # index_range = np.percentile(ngrdi_value[~np.isnan(ngrdi_value)],i)
                index_range = dic[year]
                
                
                # a = np.gradient(index_range)
                
                #以粗略指数范围进行分类
                index_value = np.empty(ngrdi_value.shape)
                index_value[~np.isnan(ngrdi_value)] = 1
                index_value[ngrdi_value<index_range] = -1
                # index_value[index_value==0] = np.nan
                write_f(source_geo,[index_value],path_out+os.sep+year+os.sep+'index_classify'+os.sep+im_path[:2]+'_'+year+'.tif')
                
                #获取超像素分割所得所有区域
                regions = find_connected_regions(np.sum(seg_im_arr,2)) 
                
                #对每个区域进行统计,基于超像素分割和粗略指数分类进行分类,以优势类填充区域
                for r in regions:
                    s = 0
                    for x,y in r:
                        s += index_value[x,y]
                    if s<0:
                        for x,y in r:
                            index_value[x,y] = -1
                    elif s>0:
                        for x,y in r:
                            index_value[x,y] = 1
                    else:
                        for x,y in r:
                            index_value[x,y] = np.nan
                
                # index_value[np.sum(seg_im_arr,2)==0] = 0
                
                start_time = time.time()
                
                #位置矩阵
                pos_arr = np.empty(index_value.shape,tuple)
                for x in range(pos_arr.shape[0]):
                   for y in range(pos_arr.shape[1]):
                       pos_arr[x,y] = (x,y)
                
                index_value[np.isnan(np.mean(source_im_arr,2))] = np.nan
                # deal_zero_im = functools.partial(deal_zero,im_arr=index_value)
                
                # func=np.frompyfunc(lambda im_arr,pos_arr:deal_zero_im(pos_arr) if im_arr ==0 else im_arr,2,1)
                
                # index_value=np.float64(func(index_value,pos_arr))
                # index_value[index_value==0] = np.nan
                write_f(source_geo,[index_value],path_out+os.sep+year+os.sep+'first_classify'+os.sep+im_path[:2]+'_'+year+'.tif')
                
                
                
                #精分类
                
                # print(r"开始精分类")
                # red = source_im_arr[:,:,0]
                # green = source_im_arr[:,:,1]
                # blue = source_im_arr[:,:,2]
                
                # ngrdi_value = (green - red) / (green + red)
                index_value[ngrdi_value<index_range] = -1
                coarse_range = ngrdi_value[index_value==-1] #获取初步分类后非健康植被NGRDI指数
                
                tail = np.nanpercentile(coarse_range,80)
                
                out = np.empty(ngrdi_value.shape,float)
                
                out[ngrdi_value<tail] = -1
                out[ngrdi_value>=tail] = 1
                
                # label_arr = np.empty(ngrdi_value.shape,float)
                # out_regions1 = find_connected_regions(out,limit=[0,1])
                # out_regions2 = find_connected_regions(out,limit=[0,-1])
                # i = 1
                # for r in out_regions1:
                #     for x,y in r:
                #         label_arr[x,y]=i
                #     i+=1
                # for r in out_regions2:
                #     for x,y in r:
                #         label_arr[x,y]=i
                #     i+=1
                label_arr1 = ndimage.label(out==-1)[0]
                label_arr2 = ndimage.label(out==1)[0]
                label_arr2[label_arr2!=0] += np.max(label_arr1)
                label_arr = label_arr1+label_arr2
                
                write_f(source_geo,[out,label_arr],path_out+os.sep+year+os.sep+'deep_classify'+os.sep+im_path[:2]+'_'+year+'.tif')
                write_f(source_geo,[out],path_out+os.sep+year+os.sep+'class'+os.sep+im_path[:2]+'_'+year+'.tif')
                write_f(source_geo,[label_arr],path_out+os.sep+year+os.sep+'label'+os.sep+im_path[:2]+'_'+year+'.tif')
                
                
                print(im_path[:2]+'完成')
        print(year+"年分类完成")


else:
    pos_arr = np.array([])
    year = 2021
    codes = ['F1']
    for code in codes:
        source_geo = gdal.Open(f"D:\\work\\code\\img_classify\\use_image\\{year}\\{code}-1-{year}-8.tif")
        # source_image = Image.open(path_head+os.sep+year+os.sep+im_path)
        source_im_arr = source_geo.ReadAsArray().astype(np.float64).transpose(1,2,0)
        # source_im_arr = np.array(source_image,dtype=float)
        # regions = find_connected_regions(source_im_arr[:,:,1],limit=[65535])
        # for r in regions:
        #     if np.mean([source_im_arr[:,:,1][x,y] for x,y in r]) == 256:
        #         for x,y in r:
        #             source_im_arr[x,y,:] = 65535
        source_im_arr_copy = source_im_arr.copy()
        seg_im_arr = snicdemo(source_im_arr_copy)
        seg_im_arr[source_im_arr==65535] = 0
        source_im_arr[source_im_arr==65535] = np.nan
        
        
        #初步分类
        # print("开始初步分类")
        
        
        red = source_im_arr[:,:,0]
        green = source_im_arr[:,:,1]
        blue = source_im_arr[:,:,2]
        ngrdi_value = (green - red) / (green + red)
        # write_f(source_geo,[ngrdi_value],r"D:\work\code\img_classify\use_image\ex\ngrdi.tif")
        index_range = 0.00
        
        index_value = np.empty(ngrdi_value.shape)
        index_value[~np.isnan(ngrdi_value)] = 1
        index_value[ngrdi_value<index_range] = -1
        # index_value[index_value==0] = np.nan
        # write_f(source_geo,[index_value],r"D:\work\code\img_classify\use_image\ex\index_classify\G1_2020.tif")
        
        regions = find_connected_regions(np.sum(seg_im_arr,2))
        
        for r in regions:
            s = 0
            for x,y in r:
                s += index_value[x,y]
            if s<0:
                for x,y in r:
                    index_value[x,y] = -1
            elif s>0:
                for x,y in r:
                    index_value[x,y] = 1
            else:
                for x,y in r:
                    index_value[x,y] = np.nan
        
        # index_value[np.sum(seg_im_arr,2)==0] = 0
        
        # start_time = time.time()
        
        if pos_arr.shape != index_value.shape:
            pos_arr = np.empty(index_value.shape,tuple)
            for x in range(pos_arr.shape[0]):
                for y in range(pos_arr.shape[1]):
                    pos_arr[x,y] = (x,y)
        
        index_value[np.isnan(np.mean(source_im_arr,2))] = np.nan
        # deal_zero_im = functools.partial(deal_zero,im_arr=index_value)
        
        # func=np.frompyfunc(lambda im_arr,pos_arr:deal_zero_im(pos_arr) if im_arr ==0 else im_arr,2,1)
        
        # index_value=np.float64(func(index_value,pos_arr))
        # index_value[index_value==0] = np.nan
        # write_f(source_geo,[index_value],r"D:\work\code\img_classify\use_image\ex\first_classify\G1_2020.tif")
        
        
        
        #精分类
        
        # print(r"开始精分类")
        # red = source_im_arr[:,:,0]
        # green = source_im_arr[:,:,1]
        # blue = source_im_arr[:,:,2]
        
        # ngrdi_value = (green - red) / (green + red)
        index_value[ngrdi_value<index_range] = -1
        coarse_range = ngrdi_value[index_value==-1]
        
        tail = np.nanpercentile(coarse_range,80)
        # if tail==0:
        #     tail+=0.00001
        out = np.empty(ngrdi_value.shape,int)
        
        out[ngrdi_value<tail] = -1
        out[ngrdi_value>=tail] = 1
        # out[red<150] = 1
        
        label_arr1 = ndimage.label(out==-1)[0]
        label_arr2 = ndimage.label(out==1)[0]
        label_arr2[label_arr2!=0] += np.max(label_arr1)
        label_arr = label_arr1+label_arr2
        
        
        write_f(source_geo,[out,label_arr],f"D:\\work\\code\\img_classify\\use_image\\ex\\deep_classify\\{code}_{year}.tif")
        write_f(source_geo,[out],f"D:\\work\\code\\img_classify\\use_image\\ex\\class\\{code}_{year}.tif")
        write_f(source_geo,[label_arr],f"D:\\work\\code\\img_classify\\use_image\\ex\\label\\{code}_{year}.tif")
        
        
        print(code)
































