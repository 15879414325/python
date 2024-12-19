# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 20:44:23 2024

@author: 33501

照片格式转换工具
"""

from PIL import Image
import os
import wx
import re

#定义拖放文件类
class FileDrop( wx.FileDropTarget ):
    def __init__(self,frame,grid):
        wx.FileDropTarget.__init__(self)    #调用父类
        self.frame = frame
        self.grid = grid
    
    def OnDropFiles(self, x, y, filePaths):
        try:
            for dir_path in filePaths:
                self.frame.files+=(os.listdir(dir_path))
                self.grid.write(os.path.basenam(dir_path)+' ')
        except:
                self.frame.files=filePaths
                for filePath in filePaths:
                    filename = os.path.basename(filePath)
                    self.grid.write(filename+' ')
        return True

#定义Transform类便于表示窗体
class Transform(wx.Frame):
    def __init__(self,*args, **kw):     #定义主函数
        super(Transform,self).__init__(*args, **kw) #调用父类
        
        #设置各个窗体属性
        self.SetSize(450, 300)  #窗体大小
        self.SetBackgroundColour('SKY BLUE')    #窗体背景色
        self.Bind(wx.EVT_CLOSE, self.exit_sys)  #添加关闭按钮
        self.b_font = wx.Font(10,wx.DEFAULT,wx.NORMAL,wx.LIGHT) #定义按钮样式
        self.t_font = wx.Font(12,wx.DEFAULT,wx.ITALIC, wx.BOLD) #定义提示语样式
        self.b_backcolor = 'TURQUOISE'    #定义按钮背景色
        
        #输入文件地址提示语
        self.tip_input = wx.StaticText(self,pos=(10,5),size=(230,25),label='请选择所需处理照片:')
        self.tip_input.SetFont(self.t_font)
        
        #打开文件浏览界面，选择所需处理文件
        self.input_button = wx.Button(self,label='打开',pos=(255,30),size=(50,25))
        self.input_button.SetBackgroundColour(self.b_backcolor)
        self.input_button.SetFont(self.b_font)
        self.input_dir = wx.TextCtrl(self,pos=(10,30),size=(230,25))
        input_fileDrop = FileDrop(self,self.input_dir)
        self.input_dir.SetDropTarget(input_fileDrop)
        self.input_button.Bind(wx.EVT_BUTTON,self.input_event)
        
        #输出文件地址提示语
        self.tip_output = wx.StaticText(self,pos=(10,65),size=(230,25),label='请选择输出照片保存地址:')
        self.tip_output.SetFont(self.t_font)
        
        #打开文件浏览界面，选择输出文件地址
        self.output_button = wx.Button(self,label='打开',pos=(255,90),size=(50,25))
        self.output_button.SetFont(self.b_font)
        self.output_button.SetBackgroundColour(self.b_backcolor)
        self.output_dir = wx.TextCtrl(self,pos=(10,90),size=(230,25))
        self.output_button.Bind(wx.EVT_BUTTON,self.output_event)
        
        #选择转换格式提示语
        self.tip_format = wx.StaticText(self,pos=(10,130),size=(100,25),label='选择转化后格式:')
        self.tip_format.SetFont(self.t_font)
        
        #选择转换格式下拉框
        self.format_button = wx.ComboBox(self,value='PNG(.png)',pos=(200,130),size=(130,30),choices=['PNG(.png)','JPGE(.jpg)','BMP(.bmp)','TIFF(.tif)','GIF(.gif)','ICO(.ico)'],style = wx.CB_READONLY)
        self.format_button.SetFont(self.b_font)
        self.format_button.SetBackgroundColour(self.b_backcolor)
        self.mat = 'PNG(.png)'
        self.format_button.Bind(wx.EVT_COMBOBOX,self.fmat)
        
        #开始转换按钮
        self.trans_button = wx.Button(self,label='转换',pos=(155,180),size=(50,25))
        self.trans_button.SetFont(self.b_font)
        self.trans_button.SetBackgroundColour(self.b_backcolor)
        self.trans_button.Bind(wx.EVT_BUTTON,self.transform)
        
        #创建列表储存文件
        self.files = []

    def input_event(self,event):
        """
        定义输入事件函数，处理点击输入按钮后的一系列操作
        """
        self.input_dir.Clear()
        wildcards = ""
        self.files = []
        input_fileDialog = wx.FileDialog(self, message="选择输入照片", wildcard=wildcards, style=wx.FD_OPEN | wx.FD_MULTIPLE)
        if input_fileDialog.ShowModal() == wx.ID_OK:
            self.files = input_fileDialog.GetPaths()
        for f in self.files:
            self.input_dir.write(os.path.basename(f)+' ')
        input_fileDialog.Destroy()
        
    def output_event(self,event):
        """
        定义输出事件函数，处理点击输出按钮后的一系列操作
        """
        self.output_dir.Clear()
        self.savepath=''
        output_dirDialog = wx.DirDialog(self, "选择输出文件夹", style=wx.DD_DEFAULT_STYLE)
        if output_dirDialog.ShowModal() == wx.ID_OK:
            self.savepath = output_dirDialog.GetPath()
        self.output_dir.write(self.savepath)
        output_dirDialog.Destroy()
        
    def fmat(self,event):
        """
        定义格式选择事件函数，处理下拉框选择格式后的一系列操作
        """
        self.mat = self.format_button.Value
        
    def transform(self,event):
        """
        定义照片格式转换事件函数，处理点击转换后的一系列操作
        """
        try:
            for file in self.files:
                im = Image.open(file)
                if os.path.exists(self.savepath+os.sep+os.path.basename(file).split('.')[0]+re.findall('\((.*)\)',self.mat)[0]):
                    im.save(self.savepath+os.sep+os.path.basename(file).split('.')[0]+'(副本)'+re.findall('\((.*)\)',self.mat)[0])
                else:
                    im.save(self.savepath+os.sep+os.path.basename(file).split('.')[0]+re.findall('\((.*)\)',self.mat)[0])
            self.tip_over = wx.MessageDialog(self,'转换成功!', "", wx.YES_DEFAULT | wx.ICON_QUESTION)
            if self.tip_over.ShowModal() == wx.ID_YES:
                self.tip_over.Destroy()
        except:
            self.tip_err = wx.MessageDialog(self,'出错啦!', "错误信息提示", wx.YES_DEFAULT | wx.ICON_QUESTION)
            if self.tip_err.ShowModal() == wx.ID_YES:
                self.tip_err.Destroy()
                
    def exit_sys(self,event):
        """
        定义退出程序提示
        """
        self.tip_close = wx.MessageDialog(self, "确定要退出系统吗？", "确认信息提示",
                                    wx.YES_NO | wx.ICON_QUESTION)
        if self.tip_close.ShowModal() == wx.ID_YES: 
            self.tip_close.Destroy()  
            self.Destroy()
        else:
            self.tip_close.Destroy()  
        

if __name__=='__main__':
    mean_ct= wx.App()
    main = Transform(None,title=u"照片格式转换",
                     style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER^wx.MAXIMIZE_BOX)
    main.Show()
    main.Center()
    mean_ct.MainLoop()



























