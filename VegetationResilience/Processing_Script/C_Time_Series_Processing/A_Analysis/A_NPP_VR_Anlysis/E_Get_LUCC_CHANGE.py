"""
通过在二十年中曾是或一直是植被覆盖的栅格TYPE_RANGE_LUCC_12345711.tif(由D_Get_Forest_Grass_Shrub_LUCC_MAX.py)区域.
与二十年中一直是植被覆盖的栅格TYPE_SAME_VEGETATION_LUCC.tif(由C_Construct_LUCC_Constant_Type_1114.py)的非植被覆盖区域
按位与运算
得到二十年中由植被类型转变为不透水面或耕地的栅格
"""

import tqdm
from osgeo import gdal
import numpy as np
import os


if __name__ == "__main__":
    # directory
    lucc_range_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_ALL_SAME_TYPE\TYPE_SAME_VEGETATION_LUCC.tif"

    # condition judgement
    init_ds:gdal.Dataset = gdal.Open(lucc_range_path)
    init_trans = init_ds.GetGeoTransform()
    init_proj = init_ds.GetProjection()

    merge_arr = init_ds.ReadAsArray().astype(np.int64)

    lucc_max_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_ALL_SAME_TYPE\TYPE_RANGE_LUCC_12345711.tif"
    #create specific tiff
    output_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_ALL_SAME_TYPE\LUCC_TYPE_CHANGE_TO_CITY_CULTIVATE.tif"
    driver:gdal.Driver = gdal.GetDriverByName('GTiff')
    re_ds: gdal.Dataset = driver.CreateCopy(output_path, init_ds)
    del init_ds

    max_ds = gdal.Open(lucc_max_path)
    max_arr = max_ds.ReadAsArray().astype(np.int64)
    del max_ds

    re_arr = ((merge_arr == 0) | (merge_arr == 6) | (merge_arr == 8)) & (max_arr != 0)

    # write
    re_ds.WriteArray(re_arr)
    re_ds.FlushCache()
    del re_ds