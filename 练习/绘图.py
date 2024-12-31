# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 15:01:43 2024

@author: 33501
"""

import matplotlib.pyplot as plt
import pandas as pd
import os
from matplotlib.ticker import MultipleLocator
from pypinyin import lazy_pinyin


names = os.listdir(r"D:\arcgis\任务\数据\max\excel")    #获取市名

name3 = names[3]    #
name4 = names[4]    #
names[4] = name3    #
names[3] = name4    #学长要求将吉安与宜春位置调换
years = [i for i in range(1990,2023)]    #获取年份(折线图x轴)
xuhaos = ['(a)','(b)','(c)','(d)','(e)','(f)','(g)','(h)','(i)','(j)','(k)']    #折线图1的11个图的序号

#——————————————————————————————————————————————————————————————————————————————
#图1
plt.figure(figsize=(33,12))    #图1的大小
win = 1    #图1中11个图的位置
for name in names:
    pynames = lazy_pinyin(name)    #获取拼音，返回值为列表
    pyname = pynames[0].capitalize()+pynames[1] if len(pynames)==3 else pynames[0].capitalize()+pynames[1]+pynames[2]
    """
    lazy_pinyin的返回值为列表，列表中的元素为每个字的拼音，pyname为处理后的市名的拼音，
    具体处理为：将第一个拼音的第一个字母大写，将最后一个“市”字的拼音排除，将剩余拼音连
    接起来，其中capitalize就是将字符串首字母大写的函数。
    上饶市例：pynames=['shang','rao','shi']经处理获得pyname='Shangrao'
    其中景德镇市为特例，故使用if判断语句来处理
    """
    yax_max = []    #存放最大值为y轴
    yax_min = []    #存放最小值为y轴
    yax_mean = []   #存放平均值为y轴
    for year in years:    #利用循环将三个值存放到对应的列表中
        dmax = pd.read_excel(f"D:\\arcgis\\任务\\数据\\max\\excel\\{name}\\_{year}.xls")
        dmin = pd.read_excel(f"D:\\arcgis\\任务\\数据\\min\\excel\\{name}\\_{year}.xls")
        dmean = pd.read_excel(f"D:\\arcgis\\任务\\数据\\mean\\excel\\{name}\\_{year}.xls")
        yax_max.append(dmax["MAX_area"][0])
        yax_min.append(dmin["MIN_area"][0])
        yax_mean.append(dmean["MEAN_area"][0])
    plt.subplot(2,6,win)    #将图分成2行6列，win为子图对应位置
    plt.plot(years,yax_max,color='lightgray',linestyle='-')    #绘制最大值折线
    plt.plot(years,yax_min,color='lightgray',linestyle='-')    #绘制最小值折线
    plt.plot(years,yax_mean,color='black',linestyle='-')       #绘制平均值折线
    plt.tick_params(axis='both',which='major',labelsize=20)    #调整坐标轴的刻度数大小
    plt.ylim(-0.5,11.5)      #设置y轴下限与上限
    jiange=MultipleLocator(2)    #创建y轴定位器，间隔2
    ax=plt.gca()    #获取轴对象
    plt.gca().yaxis.set_major_locator(jiange)    #设置y轴刻度间隔
    lfont = {'fontsize':22}    #创建一个字典，用于设置x,y轴标签的字体大小
    tfont = {'fontsize':28}    #序号与市名的字体大小
    plt.xlabel("Year",lfont)   #设置x的标签，标签的各项参数由字典形式设置
    plt.ylabel(r'Area($\mathregular{km^2}$)',lfont)    #y轴同上
    """
    两个$之间的为数学表达式，在\math后面加regular，使用与常规非数学文本相同的字体作为
    数学文本(统一字体)，{}中的^为上标符号，在其后面的将成为上标，而_则为下标符号。
    有关数学表达式的详解见：https://www.jianshu.com/p/cac3c5baaddd
    """
    plt.title(xuhaos[win-1],tfont,x=0.1,y=0.9)    #设置标题为序号，标题各项参数由字典形式设置
    plt.text(2000,0.92*11.5,pyname,tfont)    #设置文本为市名拼音，位置由x,y坐标确定，其他参数由字典形式设置
    plt.fill_between(years,yax_max,yax_min,facecolor='lightgray')
    """
    在最大值和最小值之间填充颜色，颜色为对应折线颜色，如此可以令折线与填充色合为一体，更加美观
    """
    plt.rcParams['font.sans-serif'] = ['Times New Roman'] #将所有字体改为Times New Roman
    win +=1    #子图位置后推
    print(f"1.{name}")    #方便看进度
plt.tight_layout()    #将所绘图的布局进行合理调整
plt.savefig(r"D:\\arcgis\\任务\\数据\\图\\图4.tif", dpi=600,format="tif")    #保存图，dpi为图片分辨率，300或600为论文标准
plt.show()    #结束绘图

#——————————————————————————————————————————————————————————————————————————————
#图2
plt.figure(figsize=(33,28))
names5 = ['九江市','南昌市','上饶市','宜春市','抚州市']
color_lst = ['lightcoral','violet','palegreen','wheat','skyblue']    #五个市的折线的颜色
c = 0    #用于调用颜色
for name in names5:
    pynames = lazy_pinyin(name)
    pyname = pynames[0].capitalize()+pynames[1] if len(pynames)==3 else pynames[0].capitalize()+pynames[1]+pynames[2]
    yax_mean5 = []
    for year in years:
        dmean5 = pd.read_excel(f"D:\\arcgis\\任务\\数据\\mean\\excel\\{name}\\_{year}.xls")
        yax_mean5.append(dmean5["MEAN_area"][0])
    plt.plot(years,yax_mean5,color=color_lst[c],linestyle='-',linewidth=10,label=pyname)    #linewidth为折线宽度，label为图例
    plt.grid()    #设置网格
    plt.legend(prop = {'size':50},loc = 2)    #显示上上行代码中的label，prop为字体参数，以字典方式实现，loc为位置参数，2为左上
    plt.ylim(-0.01,0.25)    
    plt.xlim(1989,2023)     #x轴下限和上限，左右各多出一年，留白更美观
    jiange=MultipleLocator(0.05)
    ax=plt.gca()
    ax.yaxis.set_major_locator(jiange)
    plt.tick_params(axis='both',which='major',labelsize=80)
    lfont = {'fontsize':80}
    plt.xlabel("Year",lfont)
    plt.ylabel(r'Area($\mathregular{km^2}$)',lfont)
    plt.rcParams['font.sans-serif'] = ['Times New Roman']
    c +=1
    print(f"2.{name}")
plt.tight_layout()
plt.savefig(r"D:\\arcgis\\任务\\数据\\图\\图2.png", dpi=600,format="png")
plt.show()

#——————————————————————————————————————————————————————————————————————————————
#图3(柱状图)
plt.figure(figsize=(33,28))
data = pd.read_excel(r"D:\arcgis\任务\analyze_pet_pre\Area.xlsx")
x_axis = ['1990','1995','2000','2005','2010','2015','2020','2022']
yax_mean = []
for y in [1990,1995,2000,2005,2010,2015,2020,2022]:
    yax_mean.append(data[y].mean())
plt.bar(x_axis,yax_mean,color='skyblue',width = 0.5)    #柱状图，第一个参数为x轴，第二个为y轴，color为柱的颜色，width为柱的宽
font = {'fontsize' : 80}
plt.xlabel("Year",font)
plt.ylabel(r' Area($\mathregular{km^2}$)',font)
plt.tick_params(axis='both',which='major',labelsize=80)
plt.rcParams['font.sans-serif'] = ['Times New Roman']
plt.tight_layout()
plt.savefig(r"D:\\arcgis\\任务\\数据\\图\\图3.png", dpi=600,format="png")
plt.show()



















