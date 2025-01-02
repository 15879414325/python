# -*-*- coding: utf-8 -*
import sys

import arcpy
import arcpy.mapping as mapping
import os,re



fdir = u"D:\\作业\\代码\\arcmapping作业\\结果"
fmxd1 = u"D:\\Pandas__Python\\python_work\\arcppy.mapping_数据样例\\test.mxd"
dir_rasters = u"D:\\Pandas__Python\\python_work\\arcppy.mapping_数据样例\\土壤侵蚀"
feapath = u"D:\\Pandas__Python\\python_work\\arcppy.mapping_数据样例\\江西边界shp"
arcpy.env.workspace = feapath
feature = arcpy.ListFeatureClasses(feature_type="Polygon")[0][0:2]
arcpy.env.workspace = dir_rasters
f_rasters = arcpy.ListRasters('*prj*', 'TIF')

for f_raster in f_rasters:
    fn = os.path.basename(f_raster).split('_')[0]
    mxd = mapping.MapDocument(fmxd1)
    df = mapping.ListDataFrames(mxd)[0]
    layers = mapping.ListLayers(mxd,"",df)
    strs = '"NAME" = \'%s\'' % (fn)
    for ly in layers:
        if ly.isFeatureLayer:
            ly.replaceDataSource(feapath, "SHAPEFILE_WORKSPACE", feature)
            ly.definitionQuery = strs
        else:
            ly.replaceDataSource(dir_rasters, "RASTER_WORKSPACE", f_raster)
            ly_extend = ly.getExtent()
            df.extent = ly_extend
            df.scale = int(df.scale * 0.0001) * 10000
    tl = '\n'.join(list(fn))
    # titl = [fs + '\n' for fs in fn]
    for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
        if elm.text[-1] == u'布':
            TlName = elm.text.split(u'土')[1]
            elm.text = tl + '\n' + u'土' + TlName
            break
    arcpy.RefreshActiveView()  # 刷新地图和布局窗口
    arcpy.RefreshTOC()  # 刷新内容列表
    TifName = fdir + os.sep + fn + '.tif'
    mapping.ExportToTIFF(mxd, TifName, resolution=600)  # 输出为png,分辨率为300
    del mxd
    print(fn)































