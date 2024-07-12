import sys

import numpy as np
from osgeo import ogr

from TreeHeightToDiameter.script import TreeFunction
from UtilitiesForDealingImage.ReadMain import vector_read


def find_attribution(ds: ogr.DataSource, _find_condition: str = None):
    _layer = ds.GetLayer(0)
    if _find_condition is not None:
        _layer.SetAttributeFilter(_find_condition)
    return _layer


if __name__ == '__main__':
    pass
    # trees = {
    #     (330000, 310000, 320000, 340000): TreeFunction.ShaMu,
    #     (220000, 180000, 190000, 260000, 261000, 262000, 290000): TreeFunction.SongLei,
    #     (410000, 711000, 801000, 710000, 804000, 580000, 480000, 490000, 620000, 819000, 849000): TreeFunction.LiLei,
    #     (530000, 535000, 761000, 540000, 590000, 630000): TreeFunction.YangShu,
    #     (440000, ): TreeFunction.ZhangShu,
    #     (350000, ): TreeFunction.BaiLei,
    #     (701000, 702000, 703000, 704000, 706000, 707000, 709000, 749000, 769000): TreeFunction.GuoShuLei
    # }
    # file_path = r"C:\Users\PZH\Desktop\dm_tcl\tree_yssz.shp"
    # datasource = vector_read(file_path, 0)
    # # find_condition = f"YOU_SHI_SZ = {i}"
    # # layer = find_attribution(datasource, find_condition)
    # layer = find_attribution(datasource)
    # defn = layer.GetLayerDefn()
    # feature: ogr.Feature = layer.GetNextFeature()
    # while feature is not None:
    #     species = feature.GetField("YOU_SHI_SZ")
    #     get_height = feature.GetField("Tree_heigh")
    #     cal_function = None
    #     for i in trees.keys():
    #         if species in i:
    #             cal_function = trees[i]
    #     if get_height is not None:
    #         xj = cal_function(get_height)
    #         feature.SetField("xj", xj)
    #         layer.SetFeature(feature)
    #         feature = layer.GetNextFeature()
    # # feature.Destroy()
    # datasource.Destroy()
