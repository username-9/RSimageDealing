import sys
import typing
from typing import List, Tuple

import numpy as np
import tqdm
from osgeo import ogr, osr, gdal

from TreeHeightToDiameter.script import TreeFunction
from UtilitiesForProcessingImage.FurttherProceing.GetDataFromXlsx import load_csv_for_x_y_data
from UtilitiesForProcessingImage.FurttherProceing.PointLinkToFish import point_link_to_fish
from UtilitiesForProcessingImage.ReadMain import vector_read
from UtilitiesForProcessingImage.WriteMain import save_data_source_to_file


def find_attribution(ds: ogr.DataSource, _find_condition: str = None):
    _layer = ds.GetLayer(0)
    if _find_condition is not None:
        _layer.SetAttributeFilter(_find_condition)
    return _layer


wgs_84 = """GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],
AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,
AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]"""


def load_x_y_data(point_ls: List[Tuple[float, float, Tuple]] or typing.Generator, attribute_name: Tuple[str, ...] or list,
                  srs: str = wgs_84, field_width: int = 24, to_file: str = None, sheet_name = None) -> ogr.DataSource:
    # create a datasource
    driver = ogr.GetDriverByName('Memory')
    data_source = driver.CreateDataSource('in_memory')

    # create a srs
    srs_o = osr.SpatialReference()
    srs_o.ImportFromWkt(srs)
    # create a layer
    layer = data_source.CreateLayer("points", srs_o, ogr.wkbPoint)
    # # create field name for each attribute name
    if not (isinstance(attribute_name, list) or isinstance(attribute_name, tuple)):
        attribute_name = [attribute_name]
    for name in attribute_name:
        field_defn = ogr.FieldDefn(name, ogr.OFTString)
        field_defn.SetWidth(field_width)
        layer.CreateField(field_defn)

    # define the point feature
    for point_data in tqdm.tqdm(point_ls):
        x, y, attributes = point_data

        # create a new point feature
        feature_defn = layer.GetLayerDefn()
        feature = ogr.Feature(feature_defn)

        # set the coordination of the point
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x, y)
        feature.SetGeometry(point)

        # set attribution for points
        for i, value in enumerate(attributes):
            feature.SetField(attribute_name[i], value)

        # add feature to layer
        layer.CreateFeature(feature)

        del feature

    if to_file is not None:
        save_data_source_to_file(data_source, to_file)

    return data_source


def fish_to_tiff(ds, tif_path, value_field, pixel_size: int = 10, datatype = gdal.GDT_Float64, nodata = -9999):
    grid_layer = ds.GetLayer()

    srs = grid_layer.GetSpatialRef()

    x_min, x_max, y_min, y_max = grid_layer.GetExtent()
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)

    target_ds = gdal.GetDriverByName('GTiff').Create(tif_path, x_res, y_res, 1, datatype)
    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    target_ds.SetProjection(srs.ExportToWkt())

    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(nodata)

    g = ogr.Geometry(ogr.wkbPolygon)
    for feature in tqdm.tqdm(grid_layer):
        value = feature.GetField(value_field)
        geom = feature.GetGeometryRef()
        if geom is not None and geom.GetGeometryName() == 'POLYGON':
            # 将矢量多边形的坐标转换为栅格坐标
            x_off, y_off, x_count, y_count = geom.GetEnvelope()
            x_start = int((x_off - x_min) / pixel_size)
            y_start = int((y_max - y_off) / pixel_size)
            x_end = int((x_count - x_min) / pixel_size)
            y_end = int((y_max - y_count) / pixel_size)

            # 遍历栅格区域并设置值（这里简单地设置为1，你可以根据需求设置不同的值）
            for x in range(x_start, x_end):
                for y in range(y_start, y_end):
                    # 检查点是否在多边形内
                    point = ogr.Geometry(ogr.wkbPoint)
                    point.AddPoint(x_min + x * pixel_size, y_max - y * pixel_size)
                    if geom.Contains(point):
                        band.SetPixel(x, y, value)


def check_field_in_definition(ds, field_name):
    field_exist = False
    _layer = ds.GetLayer()
    for i in range(_layer.GetLayerDefn().GetFieldCount()):
        field_defn = _layer.GetLayerDefn().GetFieldDefn(i)
        if field_defn.GetName() == field_name:
            field_exist = True
            break
    return field_exist




if __name__ == '__main__':
    # pass
    # TEST 24 10 29
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

    # TEST load_x_y_data 24 10 31
    csv_file = r"C:\Users\PZH\Desktop\渔网与熵\point_cloud_count_percent_entropy_new.csv"
    shp_out = r"C:\Users\PZH\Desktop\渔网与熵\test1.shp"
    fishnet_path = r"C:\Users\PZH\Desktop\渔网与熵\shp\bhq_fish_all_10_select_intersect_gmdlidar_18.shp"
    generate_data = load_csv_for_x_y_data(csv_file, "mean_x", "mean_y", "Entropy")
    fishnet_ds = ogr.Open(fishnet_path, 1)
    srs = fishnet_ds.GetLayer().GetSpatialRef().ExportToWkt()
    load_x_y_data(generate_data, "Entropy", to_file=shp_out, srs=srs)
    point_ds = ogr.Open(shp_out, 1)
    point_link_to_fish(point_ds, fishnet_ds, "Entropy")
    fish_to_tiff(fishnet_ds, shp_out,"Entropy")