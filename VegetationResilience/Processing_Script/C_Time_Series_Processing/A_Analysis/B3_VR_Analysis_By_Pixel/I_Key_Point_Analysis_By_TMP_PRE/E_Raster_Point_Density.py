import json
import os
import re

import numpy as np
import tqdm
from osgeo import gdal

if __name__ == '__main__':
    # definition and path set
    sta_dict = {}
    npy_dir = r"F:\DATA\DRAW\PIC\3_KEY_POINT_LOCATION"
    out_json_path = r"/VegetationResilience/Processing_Script/C_Time_Series_Processing/A_Analysis/B3_VR_Analysis_By_Pixel/I_Key_Point_Analysis_By_TMP_PRE\Analysis_Json\A_Statistic_by_Time_for_Hist.json"

    # iteration about npy to statistic
    npy_ls = os.listdir(npy_dir)
    npy_ls = [file for file in npy_ls if file.endswith('.npy')]
    class_ls = [1, 2, 3 ,4, 11]
    sum_arr = None
    for n_path in tqdm.tqdm(npy_ls):
        match = re.findall(r'\d+', n_path)[0]
        if eval(match) not in class_ls:
            continue

        n_arr = np.load(os.path.join(npy_dir, n_path))
        if sum_arr is None:
            sum_arr = n_arr
        else:
            sum_arr += n_arr

    re_arr = np.sum(sum_arr, axis=0)

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
    n_r_path = r"F:\DATA\DRAW\PIC\3_KEY_POINT_LOCATION\KP_LOCATION_Forest_123411.tif"
    driver: gdal.Driver = gdal.GetDriverByName('GTiff')
    ds = driver.Create(n_r_path, width, height, 1, gdal.GDT_Int8)
    ds.SetProjection(proj)
    ds.SetGeoTransform(geo)
    ds.WriteArray(re_arr)
    ds.FlushCache()
    del ds
    print('Done')