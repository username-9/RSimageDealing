import json
import os
import re

import numpy as np
import tqdm
from osgeo import gdal

if __name__ == '__main__':
    # definition and path set
    sta_dict = {}
    npy_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\B4_KEY_POINT_LOCATION_EXCEPT_LUCC_CHANGE"
    # out_json_path = r"\RF2_Ref_And_Processing_Files\H_Statistic_by_Time_for_Hist.json"

    # iteration about npy to statistic
    npy_ls = os.listdir(npy_dir)
    npy_ls = [file for file in npy_ls if file.endswith('.npy')]
    class_ls = [1, 2, 3 ,4, 11]
    sum_arr = None
    for n_path in tqdm.tqdm(npy_ls):
        match = re.findall(r'\d+', n_path)[0]
        if eval(match) not in class_ls:
            continue

        n_arr = np.load(os.path.join(npy_dir, n_path)).astype(np.int64)
        if sum_arr is None:
            sum_arr = n_arr
        else:
            sum_arr += n_arr

    # re_arr = np.sum(sum_arr, axis=0)
    re_arr = None
    for i in tqdm.tqdm(range(sum_arr.shape[0])):
        if re_arr is None:
            re_arr = sum_arr[i]
        else:
            re_arr[(re_arr == 0) & (sum_arr[i] == 1)] = 1
            re_arr[(re_arr == 0) & (sum_arr[i] == 2)] = 2
            re_arr[(re_arr != 0) & (sum_arr[i] != 0) & (re_arr != sum_arr[i])] = 3

    # construct raster to visualize the location
    # # ref raster
    ref_r_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES\tac_series_0919_3w.tif"
    ds = gdal.Open(ref_r_path)
    proj = ds.GetProjection()
    geo = ds.GetGeoTransform()
    width = ds.RasterXSize
    height = ds.RasterYSize
    del ds
    # # construct new raster
    n_r_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\B4_KEY_POINT_LOCATION_EXCEPT_LUCC_CHANGE\KP_LOCATION_Forest_123411_1221.tif"
    driver: gdal.Driver = gdal.GetDriverByName('GTiff')
    ds = driver.Create(n_r_path, width, height, 1, gdal.GDT_Int8)
    ds.SetProjection(proj)
    ds.SetGeoTransform(geo)
    ds.WriteArray(re_arr)
    ds.FlushCache()
    del ds
    print('Done')