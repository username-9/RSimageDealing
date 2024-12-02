import datetime
import json
import math
import multiprocessing
import os

import tqdm
from dateutil.relativedelta import relativedelta
from osgeo import gdal


def para_cal_static(arr, time):
    # set directory
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_RESAMPLE"
    re_dict = {}

    # statistic by LUCC
    year = time[:4]
    lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(year) + "_albert.tif")

    lucc_ds = gdal.Open(lucc_path)
    lucc_array = lucc_ds.GetRasterBand(1).ReadAsArray().astype(int)
    del lucc_ds
    statistic_class_ls = [1, 2, 3, 4, 5, 6, 7, 8, 11]
    statistic_dict = {}
    for c in statistic_class_ls:
        re_arr = arr[lucc_array == int(c)]
        re_avg = None
        if re_arr is None:
            re_avg = 2
        else:
            count = len(re_arr)
            re_avg = re_arr.mean()
            statistic_dict[c] = [float(re_avg), count]
    re_dict[time] = statistic_dict
    return re_dict


if __name__ == "__main__":
    # set directory and file path
    tac_series = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES\tac_series_0919_3w.tif"

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
    this_batch_left = tac_s_array.shape[0]
    iterate_num = math.ceil(this_batch_left / batch_num)
    date = datetime.datetime(2001, 5, 1)
    bar = tqdm.tqdm(total=iterate_num, position=0)
    batch_index = 0
    result_dict = {}
    this_batch_num = batch_num
    while this_batch_num > 0:
        bar.set_description(f"Processing Batch {batch_index}")
        bar.update(1)
        para_ls = []
        this_batch_num = min(batch_num, this_batch_left)
        this_batch_left -= batch_num
        # print(this_batch_num)
        for i in range(this_batch_num):
            ym = date.strftime("%Y-%m")
            # print(i + batch_index * this_batch_num)
            para_ls.append((tac_s_array[(i + batch_index * this_batch_num), :, :], ym))
            date = date + relativedelta(months=1)
        batch_index += 1
        with multiprocessing.Pool(processes=5) as pool:
            re = pool.starmap(para_cal_static, para_ls)
        for item in re:
            result_dict.update(item)
    json.dump(result_dict, open(r"../F_Analysis_JSON/A_OUTPUT_S_LUCC_STA_1010.json", "w"), indent=4)



