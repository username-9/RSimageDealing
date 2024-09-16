import datetime
import math
import multiprocessing

import numpy as np
import tqdm
from osgeo import gdal, gdalconst
from sklearn.linear_model import LinearRegression
from dateutil.relativedelta import relativedelta

import UtilitiesForProcessingImage.ImageBlock


def para_cal_static(arr, time):
    # set directory
    lucc_dir = r""
    re_dict = {}

    # statistic by LUCC
    year = time[:4]
    lucc_path = os.path.join(lucc_dir, str(year) + ".tif")

    lucc_ds = gdal.Open(lucc_path)
    lucc_array = lucc_ds.GetRasterBand(1).ReadAsArray()
    statistic_class_ls = [1, 2, 3, 4, 5, 6, 7, 8, 11]
    statistic_dict = {}
    for c in statistic_class_ls:
        re_arr = arr[lucc_array == str(c)]
        count = len(re_arr)
        re_avg = re_arr.mean()
        statistic_dict[c] = (re_avg, count)
    re_dict[time] = statistic_dict
    return re_dict


if __name__ == "__main__":
    # set directory and file path
    # lucc_dir = r""
    tac_series = (r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES\tac_series_0913"
                  r".tif")

    # read array from raster
    tac_s_ds = gdal.Open(tac_series)
    tac_s_array = tac_s_ds.ReadAsArray()
    ref_trans = tac_s_ds.GetGeoTransform()
    ref_proj = tac_s_ds.GetProjection()
    data_type = tac_s_ds.GetRasterBand(1).DataType
    del tac_s_ds

    # get trend by time windows and lucc(forest type)
    # by year first
    batch_num = 20
    this_batch_num = batch_num
    iterate_num = math.ceil(tac_s_array.shape[0] / batch_num)
    date = datetime.datetime(2000, 3, 1)
    bar = tqdm.tqdm(total=iterate_num, position=0)
    batch_index = 0
    while this_batch_num > 0:
        batch_index += 1
        bar.set_description(f"Processing Batch {batch_index}")
        bar.update(1)
        para_ls = []
        for i in range(iterate_num):
            ym = date.strftime("%Y-%m")
            para_ls.append((tac_s_array[i*batch_num:(this_batch_num+i*batch_num)], my))
            date = date + relativedelta(months=1)
        this_batch_num -= tac_s_array.shape[0] - batch_num
        with multiprocessing.Pool(processes=5) as pool:
            pool.starmap(para_cal_static, para_ls)




