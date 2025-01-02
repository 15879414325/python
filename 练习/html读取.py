# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 21:14:03 2024

@author: 33501
"""
import os
import re
from bs4 import BeautifulSoup
from glob import glob
import pandas as pd
import warnings
import numpy as np
import requests
from pdf import result 

warnings.filterwarnings('ignore')   #不报警告

os.chdir(r"D:\work\code\科研资料\腺病毒肺炎首页") #设置工作空间
result_path = r"D:\作业\代码\科研资料\结果"  #结果路径
files = os.listdir()        #获取姓名文件夹名
names = []
for file in files:
    names.append(file.split(' ')[0])
database = pd.DataFrame(columns=["性别",
                                 "年龄",
                                 # "塑型性支气管炎(0:否|1:是)",
                                 "咳嗽天数",
                                 "发烧天数",
                                 "住院天数",
                                 "胸腔积液(0:否|1:是)",
                                 "支气管镜灌洗次数",
                                 "白细胞计数(次数:数量(10^9/L))",
                                 "中性粒细胞比例(%)",
                                 "淋巴细胞比例(%)",
                                 "C-反应蛋白(mg/L)",
                                 "乳酸脱氢酶(U/L)"],
                                 index=names)  #创建用于储存数据的dataframe


# for name in names:
#     f = open(os.path.join(name,(name+" - 结构化---新病案首页.html")))
#     data = f.read()
#     soup = BeautifulSoup(data)
#     txt = soup.find_all(style="BORDER-COLLAPSE: collapse; TABLE-LAYOUT: fixed; WORD-BREAK: break-all")
#     # txt = re.findall('以“(.*?)为',txt)[0]
#     # print(txt)
#     table=txt[1].text.split('\n')
#     one=re.findall('[发热|咳嗽](\d+|半)(天|周|月)',txt)
#     print(name)
#     for t in table:
#         if '支气管镜' in t:
#             print(t)
#             if '灌洗' in t:
#                 print(t+'2')
#     print(one)
#     if name=='林宇航':
#         continue
#     a = txt[0].string
#     print(name)
#     for i in range(len(txt)):
#         print(txt[i].text)
#     if '积液' in txt:
#         print(name)
#         if '未见积液' in txt:
#             print(name+'2')
#     m=txt.split('\n')
#     print(f"{[m[24],m[29]]+[m[n] for n in range(35,135,11)]}")

#性别
for name in names:
    f = open(name+" - 结构化---新病案首页.html") #打开文件
    data = f.read() #读取文件
    soup = BeautifulSoup(data)  #创建html数据解析器
    txt = soup.find(id="EXT_DE_SEX_CODE").text  #按id提取文件中我们所需内容
    if txt == "1":  #进行判断
        database["性别"][name] = "男" #传入数据
    if txt == "2":
        database["性别"][name] = "女"
f.close()   #关闭文件
#年龄
# ages = 0    
for name in names:
    f = open(name+" - 结构化---新病案首页.html")
    data = f.read()
    soup = BeautifulSoup(data)
    # txt = soup.find(id="STD_DE_AGE").text.split("岁")
    txt = soup.find(id="STD_DE_AGE").text  #按id提取年龄
    database["年龄"][name] = txt  #传入数据
    # if txt[1] == "":
    #     database["年龄"][name] = int(txt[0])
    # else:
    #     database["年龄"][name] =(int(txt[0])+int(txt[1][:-2])/12)
f.close()
#胸腔积液
for name in names:
    xqjy = ""   #初始化xqjy以储存胸腔积液数据
    f = open(name+" - 结构化---新病案首页.html")
    # files = os.listdir(name)    #获取名字文件夹下辖文件名
    # for file in files:      #遍历文件名
    #     if "入院" in file:    #判断是否为入院检查报告数据(胸腔积液数据用此文件便于提取)
    #         f = open(os.path.join(name,file))
    data = f.read()
    soup = BeautifulSoup(data)
    # txt = soup.find(id="STD_DE_DIAGNOSIS_NAME|3|2").text #获取初步诊断数据
    # if "胸腔积液" in txt:  #判断是否存在胸腔积液
    #     xqjy+="a1"  #小写字母为诊断次数,0为不存在,1为存在
    # else:
    #     xqjy+="a0"
    # txt = soup.find(class_="$03E9F93C-64A3-43a0-8FFD-E79542ABF756$1").text  #获取入院诊断数据
    # if "胸腔积液" in txt:
    #     xqjy+="|b1"
    # else:
    #     xqjy+="|b0"
    # txt = soup.find(id="STD_DE_DIAGNOSIS_NAME|1|2").text  #获取出院诊断数据
    # if "胸腔积液" in txt:
    #     xqjy+="|c1"
    # else:
    #     xqjy+="|c0"
    # database["胸腔积液(0:否|1:是)"][name] = xqjy
    txt = soup.find(id="EXT_DE_644BFB3B_CAF2_4A81_8644_597B0BE0727B").text
    data = re.findall('入院诊断[:|：](.*?)出院诊断[:|：](.*?)入院情况',txt)[0]
    # print(name)
    # print(data)
    if '胸腔积液' in data[0]:
        xqjy+="b1"
    else:
        xqjy+="b0"
    if '胸腔积液' in data[1]:
        xqjy+="|c1"
    else:
        xqjy+="|c0"
    database["胸腔积液(0:否|1:是)"][name] = xqjy
f.close()
#咳嗽、发烧
for name in names:
    tran = {'天':1,'周':7,'月':30}
    cough = 0   #初始化cough数据以储存咳嗽天数，若没有则0天
    hot = 0     #初始化hot数据以储存发热天数，若没有则0天
    f = open(name+" - 结构化---新病案首页.html")
    # try:        #文件有两种命名形式，所以用try来进行判断
    #     f = open(os.path.join(name,(name+" - 结构化入院记录【儿科】--通用.html")))
    # except:
    #     f = open(os.path.join(name,(name+" - 结构化入院记录【儿科】--肺炎.html")))
    data = f.read() 
    soup = BeautifulSoup(data)
    # txt = soup.find(id="STD_DE_C_C_DESCRIBE").text  #按id提取主诉数据(内含咳嗽、发热天数数据)
    # # print(name+txt)
    # ut = re.findall(r'天|周|月',txt)   #查找时间单位，方便转换
    # kf = re.findall(r"[发热|咳嗽]*[发热|咳嗽]",txt) #查找咳嗽、发热顺序，以便读取数据
    # # print(kf)
    # days = re.findall(r'[咳嗽|发热](\d+|半)[个|天|周|月]',txt)   #获取天数信息
    # a = txt.split("半")[0][-2:]  #如有半月的，找出是咳嗽还是发热持续了半个月
    txt = soup.find(id="EXT_DE_644BFB3B_CAF2_4A81_8644_597B0BE0727B").text
    txt = re.findall('以“(.*?)为',txt)[0]
    data=re.findall('[发热|咳嗽](\d+|半)(天|周|月)',txt)
    kf = re.findall(r"[发热|咳嗽|热]*[发热|咳嗽|热]",txt)
    print(name)
    print(kf+data)
    if len(data)==0:
        database["咳嗽天数"][name] = cough
        database["发烧天数"][name] = hot
        continue
    if data[0][0]=='半':
        data[0]=list(data[0])
        data[0][0]=15
        data[0][1]='天'
    if len(data)==2:
        if data[1][0]=='半':
            data[1]=list(data[1])
            data[1][0]=15
            data[1][1]='天'
    if '发热' in txt or '热' in txt:
        if len(data)==1:
            hot+=int(data[0][0])*tran[data[0][1]]
        else:
            i = kf.index("发热")
            hot = int(data[i][0])*tran[data[i][1]]
    if '咳嗽' in txt:
        if len(data)==1:
            cough+=int(data[0][0])*tran[data[0][1]]
        else:
            i = kf.index("咳嗽")
            cough = int(data[i][0])*tran[data[i][1]]
    # if "发热" in txt:     #判断是否有发热信息
    #     if a == "发热":   #判断发热是否为半月
    #         hot=15        #是则天数为15
    #     else:
    #         if len(days)==1:    #判断是否咳嗽、发烧天数一样
    #             hot = int(days[0])  #一样则将数据写入
    #             if ut[0] == "周":    #判断单位
    #                 hot = hot*7     #进行单位转换
    #             if ut[0] =="月":
    #                 hot = hot*30
    #         if len(days)==2:
    #             i = kf.index("发热")
    #             hot = int(days[i])
    #             if ut[i] == "周":
    #                 hot = hot*7
    #             if ut[i] =="月":
    #                 hot = hot*30
    # if "咳嗽" in txt:
    #     if a == "咳嗽":
    #         cough =15
    #     else:
    #         if len(days) == 2:
    #             i = kf.index("咳嗽")
    #             cough = int(days[i])
    #             if ut[i] == "周":
    #                 cough = cough*7
    #             if ut[i] =="月":
    #                 cough = cough*30
    #         if len(days)==1:
    #             cough = int(days[0])
    #             if ut[0] == "周":
    #                 cough = cough*7
    #             if ut[0] =="月":
    #                 cough = cough*30
    database["咳嗽天数"][name] = cough
    database["发烧天数"][name] = hot
f.close()
# #塑型性支气管炎
# for name in names:
#     su = ""    #初始化su储存塑型性支气管炎存在情况
#     files = os.listdir(name)    
#     for file in files:
#         if "入院" in file:
#             f = open(os.path.join(name,file))
#     data = f.read()
#     soup = BeautifulSoup(data)
#     txt = soup.find(id="STD_DE_DIAGNOSIS_NAME|3|2").text  #按id提取初步诊断信息
#     if "塑型性支气管炎" in txt:
#         su+="a1"
#     else:
#         su+="a0"
#     txt = soup.find(class_="$03E9F93C-64A3-43a0-8FFD-E79542ABF756$1").text  #按class提取入院诊断信息
#     if "塑型性支气管炎" in txt:
#         su+="|b1"
#     else:
#         su+="|b0"
#     txt = soup.find(id="STD_DE_DIAGNOSIS_NAME|1|2").text  #按id提取出院诊断信息
#     if "塑型性支气管炎" in txt:
#         su+="|c1"
#     else:
#         su+="|c0"
#     database["塑型性支气管炎(0:否|1:是)"][name] = su
# f.close()
#住院天数
for name in names:
    # files = os.listdir(name)
    f = open(name+" - 结构化---新病案首页.html")
    # for file in files:
    #     if "出院" in file:
    #         f = open(os.path.join(name,file))
    data = f.read()
    soup = BeautifulSoup(data)
    txt = soup.find(id="EXT_DE_IN_DAYS").text
    database["住院天数"][name] = int(txt)
f.close()
#支气管镜灌洗次数
for name in names:
    count = 0
    # files = os.listdir(name)
    # for file in files:
    #     if "出院" in file:
    #         f = open(os.path.join(name,file))
    f = open(name+" - 结构化---新病案首页.html")
    data = f.read()
    soup = BeautifulSoup(data)
    txt = soup.find_all(style="BORDER-COLLAPSE: collapse; TABLE-LAYOUT: fixed; WORD-BREAK: break-all")[1].text  #按id提取支气管灌洗次数信息
    # if '拒绝' in txt:     
        # count -=1
    txts = txt.split('\n')   #其中支气管灌洗次数信息所在短句有以'，'分割和以'；'分割两种
    for t in txts:
        if '支气管镜' in t:
            print(t)
            if '灌洗' in t:
                count+=1
    # for t in txts:
    #     t = t.split('；')
    #     for p in t:
    #         """
    #         气管镜灌洗次数数据中，有表达为气管镜灌洗和气管镜治疗两种，而写成拟或建议进行气管镜治
    #         疗的，最后都被家属拒绝了，所以不计入次数
    #         """
    #         if "气管镜" in p and ('灌洗' in p or '治疗' in p) and ('拟' not in p and '建议' not in p):
    #             # print(name)
    #             # print(p)
    #             count += 1
    #             x = re.findall(r'\d([、|和])\d',p)    #寻找到日期的分割'、'或'和'
    #             count+=len(x)
    # if count <0:
    #     count = 0
    database["支气管镜灌洗次数"][name] = count
f.close()
#白细胞计数
for name in names:
    # print(name)
    count = 0
    # files = os.listdir(name)
    # for file in files:
    #     if "出院" in file:
    #         f = open(os.path.join(name,file))
    f = open(name+" - 结构化---新病案首页.html")
    data = f.read()
    soup = BeautifulSoup(data)
    txt = soup.find(id="EXT_DE_644BFB3B_CAF2_4A81_8644_597B0BE0727B").text  #按id获取白细胞计数数据
    # m = txt.split(":") #从这里到下一个循环结束都为检查错误语句
    # for n in m:
    #     x=n.split(";")
    #     for y in x:
    #         if "白细胞" in y:
    #             print(y)
    white = list(set(re.findall(r'白细胞计数\s(\S+)',txt))) #查找以白细胞计数\s开头的多个非空格字符(\s为空格，\S为非空格字符)
    if len(list(set(re.findall(r'白细胞计数(\S+)',txt))))!=0:
        white+= list(set(re.findall(r'白细胞计数(\S+)',txt)))
    print(name)
    print(white)
    i = 96      #将i初始化为96，因为96以后的ASCII码值为小写字母，如:97代表"a"，100代表"d"
    strw = ""  #初始化strw字段数据，用以储存白细胞计数信息
    done = []
    for w in white:
        if w in done:
            continue
        done.append(w)
        i+=1
        if i==97:
            strw += f"{chr(i)}:{w}"   #将chr(i)所表示字母作为次数，w为白细胞计数
            continue
        strw += f"|{chr(i)}:{w}"
    database["白细胞计数(次数:数量(10^9/L))"][name] = strw
f.close()
#中性粒细胞比例
for name in names:
    # print(name)
    count = 0
    # files = os.listdir(name)
    # for file in files:
    #     if "出院" in file:
    #         f = open(os.path.join(name,file))
    f = open(name+" - 结构化---新病案首页.html")
    data = f.read()
    soup = BeautifulSoup(data)
    txt = soup.find(id="EXT_DE_644BFB3B_CAF2_4A81_8644_597B0BE0727B").text
    # m = txt.split(":")
    # for n in m:
    #     x=n.split(";")
    #     for y in x:
    #         if "中性粒细胞" in y:
    #             print(y)
    medium = re.findall(r'中性粒细胞比率\s(\S+)',txt)
    if len(re.findall(r'中性粒细胞比率(\S+)',txt))!=0:
        medium+=re.findall(r'中性粒细胞比率(\S+)',txt)
    print(name)
    print(medium)
    i = 96
    strm = ""
    done = []
    for m in medium:
        if m in done:
            continue
        done.append(m)
        i+=1
        if i==97:
            strm += f"{chr(i)}:{m}"
            continue
        strm += f"|{chr(i)}:{m}"
    database["中性粒细胞比例(%)"][name] = strm
f.close()
#淋巴细胞比例
for name in names:
    # print(name)
    count = 0
    # files = os.listdir(name)
    # for file in files:
    #     if "出院" in file:
    #         f = open(os.path.join(name,file))
    f = open(name+" - 结构化---新病案首页.html")
    data = f.read()
    soup = BeautifulSoup(data)
    txt = soup.find(id="EXT_DE_644BFB3B_CAF2_4A81_8644_597B0BE0727B").text
    # m = txt.split(":")
    # for n in m:
    #     x=n.split(";")
    #     for y in x:
    #         if "淋巴细胞" in y:
    #             print(y)
    lb = re.findall(r'淋巴细胞比率\s(\S+)',txt)
    if len(re.findall(r'淋巴细胞比率(\S+)',txt))!=0:
        lb+=re.findall(r'淋巴细胞比率(\S+)',txt)
    print(name)
    print(lb)
    i = 96
    strl = ""
    done = []
    for l in lb:
        if l in done:
            continue
        done.append(l)
        i+=1
        if i==97:
            strl += f"{chr(i)}:{l}"
            continue
        strl += f"|{chr(i)}:{l}"
    database["淋巴细胞比例(%)"][name] = strl
f.close()
#C-反应蛋白
for name in names:
    # print(name)
    count = 0
    # files = os.listdir(name)
    # for file in files:
    #     if "出院" in file:
    #         f = open(os.path.join(name,file))
    f = open(name+" - 结构化---新病案首页.html")
    data = f.read()
    soup = BeautifulSoup(data)
    txt = soup.find(id="EXT_DE_644BFB3B_CAF2_4A81_8644_597B0BE0727B").text
    # m = txt.split("。")
    # for n in m:
    #     x=n.split(";")
    #     for y in x:
    #         if "C-反应蛋白" in y:
    #             print(y)
    protein = re.findall(r'C-反应蛋白\s(\S+)',txt)
    if len(re.findall(r'C-反应蛋白(\S+)',txt))!=0:
        protein+=re.findall(r'C-反应蛋白(\S+)',txt)
    print(name)
    print(protein)
    i = 96
    strp = ""
    done = []
    for p in protein:
        if p in done:
            continue
        done.append(p)
        i+=1
        if i==97:
            strp += f"{chr(i)}:{p}"
            continue
        strp += f"|{chr(i)}:{p}"
    database["C-反应蛋白(mg/L)"][name] = strp
f.close()
#乳酸脱氢酶
for name in names:
    # print(name)
    count = 0
    # files = os.listdir(name)
    # for file in files:
    #     if "出院" in file:
    #         f = open(os.path.join(name,file))
    f = open(name+" - 结构化---新病案首页.html")
    data = f.read()
    soup = BeautifulSoup(data)
    txt = soup.find(id="EXT_DE_644BFB3B_CAF2_4A81_8644_597B0BE0727B").text
    # m = txt.split(":")
    # for n in m:
    #     k=n.split("。")
    #     for g in k:
    #         x=g.split(";")
    #         for y in x:
    #             if "乳酸脱氢酶" in y and "U/L" in y:
    #                 print(y)
    LDH = re.findall(r'乳酸脱氢酶\s(\S+)',txt)
    # if re.findall(r'乳酸脱氢酶(\S+)',txt)!=0:
    #     LDH+=re.findall(r'乳酸脱氢酶(\S+)',txt)
    print(name)
    print(LDH)
    i = 96
    strL = ""
    done = []
    for L in LDH:
        if L in done:
            continue
        done.append(L)
        i+=1
        if i==97:
            strL += f"{chr(i)}:{L}"
            continue
        strL += f"|{chr(i)}:{L}"
    database["乳酸脱氢酶(U/L)"][name] = strL
f.close()
database['降钙素原(ng/ml)'] = result['降钙素原(ng/ml)']
#导出
# database.to_excel(r"D:\work\code\科研资料\结果\病例数据3.xlsx",sheet_name="病例数据")  #将dataframe数据导出为excel格式














































































































































