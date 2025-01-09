import datetime
import os

import numpy as np
import tqdm
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt
from osgeo import gdal

if __name__ == "__main__":
    # kp_npy_path = r"./RF1_Ref_And_Processing_Files/C2_DETECT_KEY_POINT.npy"
    kp_npy_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\B4_KP_1221\C_DETECT_KEY_POINT.npy"
    kp_arr = np.load(kp_npy_path)

    # get location of key points
    location = np.nonzero(kp_arr)
    y = location[1]
    x = location[2]
    time_month = location[0]

    # # construct raster to visualize the location
    # # # ref raster
    # ref_r_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES\tac_series_0919_3w.tif"
    # ds = gdal.Open(ref_r_path)
    # proj = ds.GetProjection()
    # geo = ds.GetGeoTransform()
    # width = ds.RasterXSize
    # height = ds.RasterYSize
    # del ds
    # # # construct array to be written in
    # w_arr = np.zeros((height, width))
    # for i in tqdm.tqdm(range(len(y))):
    #     if w_arr[y[i], x[i]] != 0:
    #         w_arr[y[i], x[i]] = 300
    #     else:
    #         w_arr[y[i], x[i]] = time_month[i]
    # # # construct new raster
    # n_r_path = r"F:\DATA\DRAW\F_PIC\3_KEY_POINT_LOCATION\KP_LOCATION.tiff"
    # driver: gdal.Driver = gdal.GetDriverByName('GTiff')
    # ds = driver.Create(n_r_path, width, height, 1, gdal.GDT_Int8)
    # ds.SetProjection(proj)
    # ds.SetGeoTransform(geo)
    # ds.WriteArray(w_arr)
    # ds.FlushCache()
    # del ds
    # print('Done')

    # find location with different lucc
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\A4_LUCC_DILATE_EXCEPT_LUCC_CHANGE"
    # ori_time = ori_time + relativedelta(months=1)
    lucc_class = [1, 2, 3, 4, 5 ,6, 7, 8, 11]
    for c in lucc_class:
        c_arr = np.zeros(kp_arr.shape)
        ori_time = datetime.datetime(2001, 5, 1)
        for i in tqdm.tqdm(range(kp_arr.shape[0])):
            lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(ori_time.year) + "_albert.tif")
            lucc_ds = gdal.Open(lucc_path)
            lucc_arr = lucc_ds.ReadAsArray()
            del lucc_ds

            temp_arr = kp_arr[i, :, :]
            indices = np.where((lucc_arr == c))
            c_arr[i, indices[0], indices[1]] = kp_arr[i, indices[0], indices[1]]

        file_path = rf"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\B4_KEY_POINT_LOCATION_EXCEPT_LUCC_CHANGE\Class_{c}.npy"
        np.save(file_path, c_arr)