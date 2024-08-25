from multiprocessing import Pool

from osgeo import ogr, osr
from osgeo import gdal
import os

from UtilitiesForDealingImage.UtilityFunction import workdir_filelist


def calculated_proportion(in_path1, in_path2, out_path):
    """
    面图层相交，属性字段保留，两个shp文件必须是同一个坐标系
    :param in_path1: 主shp文件
    :param in_path2: 用来相交的shp文件
    :param out_path: 输出结果路径
    :return:
    """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(in_path1, 1)
    layer_1 = dataSource.GetLayer()
    crs = layer_1.GetSpatialRef()
    epsg1 = crs.GetAttrValue('AUTHORITY', 1)

    RdataSource = driver.Open(in_path2, 1)
    layer_2 = RdataSource.GetLayer()
    crs = layer_2.GetSpatialRef()
    epsg2 = crs.GetAttrValue('AUTHORITY', 1)
    if epsg1 != epsg2:
        print("坐标系不一致")
    else:
        print("坐标系一致")

    # 新建DataSource，Layer
    out_ds = driver.CreateDataSource(out_path)
    out_lyr = out_ds.CreateLayer("out", layer_1.GetSpatialRef(), layer_1.GetGeomType())
    # 遍历原始的Shapefile文件给每个Geometry做Buffer操作
    # current_union = layer[0].Clone()
    print('the length of layer:', len(layer_1))
    if len(layer_1) == 0:
        return

    p = ["SKIP_FAILURES=YES", "PROMOTE_TO_MULTI=YES", "INPUT_PREFIX=1", "METHOD_PREFIX=2"]
    # gdal.TermProgress_nocb 控制台输出进度
    layer_1.Intersection(layer_2, out_lyr, p, gdal.TermProgress_nocb)
    out_lyr.SyncToDisk()
    del dataSource, RdataSource, out_ds


if __name__ == '__main__':
    # shp_dir = r""
    # shp_path = r"J:\kenniya222\kenya2010.shp"
    # out_dir = r"J:\新建文件夹\相交"

    # filelist = workdir_filelist(shp_dir, ".shp")
    #
    # ls = [(filelist[i], shp_path, os.path.join(out_dir, os.path.basename(filelist[i]))) for i in range(len(filelist))]

    # with Pool(processes=5) as pool:
    #     results = pool.starmap(calculated_proportion, ls)

    shp_path = r"D:\新建文件夹\kny_00_en.shp"
    shp_path2 = r"D:\新建文件夹\kny_10_en.shp"
    out_path = r"D:\新建文件夹\test.shp"
    calculated_proportion(shp_path, shp_path2, out_path)
