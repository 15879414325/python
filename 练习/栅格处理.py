# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 20:53:35 2024

@author: 33501
"""
import rasterio
import numpy as np
import os
import time
from rasterio.windows import Window
from scipy import stats
from concurrent.futures import ProcessPoolExecutor as pe
from multiprocessing import Manager
from functools import partial



#============================================================================================================
#求降水年

def mean(path,year): #读取栅格数据并计算平均数的函数
    d_n = np.empty((12,786,1201)) #创建三维数组，以放置12个月的数据
    i = 0   #创建i值，以方便输入数据到d_n
    for month in range(1,13):
        path_f = path + '\\pre_%d_%.2d.tif'%(year,month)
        with rasterio.open(path_f) as dt:
            nodata = dt.nodata #提取无效值
            profile = dt.profile        #提取属性
            profile.data['dtype'] = 'float64' #将类型改为浮点型(原为整型)
            profile.data['nodata'] = np.nan #将属性中的无效值改为nan(原为-32768.0)
            data = dt.read().astype('float64') #读取数据，并将数据类型改为浮点型(原为整型)，以方便处理
            shape = data.shape          #提取数据形状
            data[data == nodata] = np.nan #将数据中的无效值改为nan(原为-32768.0)
            d_n[i] = data[0] #将数据放入d_n
            i +=1
    d_mean = np.mean(d_n,0) #np.mean是求数组平均数的函数
    
    return d_mean,profile,shape

def out(data,out_path,profile,shape):#导出到文件的函数
    bend = shape[0]
    with rasterio.open(out_path, 'w', **profile) as src:
        
        for i in range(bend):  # 将矩阵输出至各个波段，其实src.write(data)就行
            src.write(data[i], i + 1) # 二维
        # src.write(data)  # 三维
            

start_all = time.time()
path_head = r"D:\Pandas__Python\python_work\17 rasterio\降水_月"
out_head = r"D:\作业\代码\rasterio\年降水"
for year in range(1991,2018):
    start_time = time.time()
    d_mean,profile,shape = mean(path_head, year)
    out_path = f'{out_head}\\{year}.tif'
    out(d_mean, out_path, profile, shape)
    end_time = time.time()
    print(year,shape,f'用时{end_time-start_time}s')
end_all = time.time()
print(f'总用时{end_all-start_all}s')


 
#============================================================================================================
#分窗口求趋势和显著性

def window(path,window_shape): #创建窗口函数
    windows = []   #创建空列表，以放置多个窗口
    inxs = []      #创建空列表，以放置窗口索引值
    with rasterio.open(path) as ra: #打开文件
        profile = ra.profile #获取属性
        data = ra.read().astype('float64') #将文件读取为数组
        shape = data.shape                 #获取文件形状
        xsize, xend = divmod(ra.width, window_shape[1]) #计算每个窗口合理的宽度
        ysize, yend = divmod(ra.height, window_shape[0]) #计算每个窗口合理的高度
        y_off = 0      #创建偏移值，即每个窗口左上角y轴的值
        for y_inx,sy in enumerate(range(window_shape[0])):
            x_off = 0  #创建偏移值，即每个窗口左上角x轴的值
            height = ysize + yend if sy == (shape[0] - 1) else ysize
            for x_inx,sx in enumerate(range(window_shape[0])):
                width = xsize + xend if sx == (shape[0] - 1) else xsize
                windows.append(Window(x_off,y_off,width,height))
                inxs.append((y_inx,x_inx))
                x_off +=width
            y_off +=height
    return windows,inxs,profile


def linegr(arr,x,return_value): #计算趋势和显著性函数
    d0,d1,d2,d3,d4 = [arr[0].copy() for i in range(5)]

    for ax2 in range(arr.shape[2]):

        for ax1 in range(arr.shape[1]):
            q = stats.linregress(x,arr[:,ax1,ax2])
            d0[ax1,ax2] = q[0]
            d1[ax1,ax2] = q[1]
            d2[ax1,ax2] = q[2]
            d3[ax1,ax2] = q[3]
            d4[ax1,ax2] = q[4]

    dic = {'s':d0,'i':d1,'r':d2,'p':d3,'st':d4}
    if len(return_value) == 1:
        for v in return_value:
            return dic[v]
    else:
        value = []
        for v in return_value:
            value.append(dic[v])
        return value

def linegr_ly(arr_ax,x,return_value): #计算趋势和显著性函数，处理数据为一维数组
    q = stats.linregress(x,arr_ax)
    d0 = q[0]
    d1 = q[1]
    d2 = q[2]
    d3 = q[3]
    d4 = q[4]
    dic = {'s':d0,'i':d1,'r':d2,'p':d3,'st':d4}
    if len(return_value) == 1:
        for v in return_value:
            return dic[v]
    else:
        value = []
        for v in return_value:
            value.append(dic[v])
        return value



#非并行分窗口
start_all = time.time()
path_heard = r"D:\作业\代码\rasterio\年降水"
out_path = r"D:\作业\代码\rasterio\趋势与显著性"

wins,inxs,profile = window(f'{path_heard}\\1991.tif',(3,3)) #利用一个数据获取所需窗口等数据
s = rasterio.open(out_path + os.sep + 'slope.tif', 'w', **profile)
p = rasterio.open(out_path + os.sep + 'pvalue.tif', 'w', **profile)

years = np.arange(2001, 2018)      #输入所研究的年份
w = 1      #用于查看进度
for win in wins:
    i = 0
    d_n = np.empty((len(years),win.height,win.width))
    start_time = time.time()
    for year in years:
        path = f'{path_heard}\\{year}.tif'
        with rasterio.open(path) as ra:
            data = ra.read(window=win).astype('float64')
            d_n[i] = data
            i +=1
    slope,pvalue = linegr(d_n,years,['s','p']) #使用linegr函数
    # slope, pvalue = np.apply_along_axis(linegr_ly,0,d_n,years,['s','p']) #使用linegr_ly函数
    s.write(slope,1, window=win)
    p.write(pvalue,1, window=win)
    end_time = time.time()
    
    print(f'win{w}:{end_time-start_time}s') #输出时间
    w +=1
s.close()
p.close()

end_all = time.time()
print(f'总用时{end_all-start_all}s')
#用时37s左右




def al(path_heard,win,years,w,ds):
        i = 0
        d_n = np.empty((9,win.height,win.width))
        for year in years:
            path = f'{path_heard}\\{year}.tif'
            with rasterio.open(path) as ra:
                data = ra.read(window=win).astype('float64')
                d_n[i] = data
                i +=1
        slo = ds[1]
        pva = ds[2]
        slope,pvalue = linegr(d_n,years,['s','p'])
        slo[w]=slope
        pva[w]=pvalue

#并行分窗口1
if __name__=='__main__':
    
    start_all = time.time()
    path_heard = r"D:\work\code\rasterio\年降水"
    out_path = r"D:\work\code\rasterio\趋势与显著性"
    

    wins,inxs,profile = window(f'{path_heard}\\1991.tif',(3,3)) #利用一个数据获取所需窗口等数据
    years = np.arange(2001, 2010) #输入所研究的年份
#==============================================================================
    # 创建可共享字典，以方便写入数据
    
    sl = Manager().dict()                #写入slope数据的共享字典
    pv = Manager().dict()                #写入pvalue数据的共享字典
    sls = [sl for i in range(len(wins))] 
    pvs = [pv for i in range(len(wins))] 
    """
    将数量与窗口或所使用进程数相等的两种共享字典分别放入两个列表，如此做，每种共享字典
    的id相同，变一则全改，这样就可以将不同进程的数据汇总到同一个字典
    """
#==============================================================================
    w = 1 #创建w值，作为字典的key
#==============================================================================
#多进程
    pool = pe(10) #创建进程池
    for ds in zip(wins,sls,pvs): #用循环创建多线程，也可用map，这里使用循环
        pool.submit(al,path_heard,ds[0],years,w,ds) #创建并运行进程
        w +=1
    pool.shutdown(wait=True) #等待，以方便计时
#==============================================================================
#将数据写入文件
    s = rasterio.open(out_path + os.sep + 'slope.tif', 'w', **profile)
    p = rasterio.open(out_path + os.sep + 'pvalue.tif', 'w', **profile)
    for win,w_n in zip(wins,[i for i in range(1,w)]): #利用循环依次将数据写入文件
        s.write(sl[w_n],1, window=win)
        p.write(pv[w_n],1, window=win)
    s.close()            #close才会保存写入文件
    p.close()            #注意：一定要在所有数据全部写入之后再close，
                          #     或者将open中的'w'改成'r+',具体用法参照并行分窗口2
#==============================================================================
    end_all = time.time()
    print(f'总用时{end_all-start_all}s')
#用时10s左右


def al2(win,path_heard,years,out_path,profile):
    try:
        s = rasterio.open(out_path + os.sep + 'slope.tif', 'r+', **profile)
        p = rasterio.open(out_path + os.sep + 'pvalue.tif', 'r+', **profile)
        i = 0
        d_n = np.empty((len(years),win.height,win.width))
        for year in years:
            path = f'{path_heard}\\{year}.tif'
            with rasterio.open(path) as ra:
                data = ra.read(window=win).astype('float64')
                d_n[i] = data
                i +=1
        

        slope,pvalue = linegr(d_n,years,['s','p'])
        with rasterio.open(out_path + os.sep + 'slope.tif', 'r+') as s:
            s.write(slope,1, window=win)
        with rasterio.open(out_path + os.sep + 'pvalue.tif', 'r+') as p:
            p.write(pvalue,1, window=win)
        return (None, None)
    except Exception as e:
        return (win,e)
    


#并行分窗口2
if __name__=='__main__':
    
    start_all = time.time()
    path_heard = r"D:\作业\代码\rasterio\年降水"
    out_path = r"D:\作业\代码\rasterio\趋势与显著性"
    
    wins,inxs,profile = window(f'{path_heard}\\1991.tif',(3,3)) #利用其中一个数据获取窗口等数据
#======================================================================================
    #创建一个空的栅格文件
    s = rasterio.open(out_path + os.sep + 'slope.tif', 'w', **profile)
    p = rasterio.open(out_path + os.sep + 'pvalue.tif', 'w', **profile)
    
    s.close()
    p.close()
#======================================================================================
    years = np.arange(2001, 2018) #输入所需年份
#======================================================================================
    #多进程
    pool = pe(10) #创建有任意个进程的进程池，这里创建10个
    func = partial(al2,path_heard=path_heard, 
                    years=years,out_path=out_path,profile=profile) #固定参数
    lss = list(pool.map(func,wins)) # 进程调用函数，不用list()进程池不会开始运行(不是只能用list,而是要调用它)，类似迭代器
                              # 注意：创建函数时要将wins所传递的参数放在第一个
                              #       或者将wins改成类似zip([args for i in range(len(wins))],wins,[args for i in range(len(wins))])
                              #       并且不进行固定参数
    pool.shutdown(wait=True)  # 等待，以方便计时
    

    end_all = time.time()
    print(f'总用时{end_all-start_all}s')
#用时9s左右















