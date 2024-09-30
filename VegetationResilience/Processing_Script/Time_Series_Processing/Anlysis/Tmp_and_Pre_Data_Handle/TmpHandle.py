import datetime
import json
import math
import multiprocessing
import os

import tqdm
from dateutil.relativedelta import relativedelta
from osgeo import gdal


def para_cal_static(path):
    # set directory
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_RESAMPLE"
    tmp_dir = os.path.join(r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\TMP\TMP_BTH_RESAMPLE", path)
    re_dict = {}

    # statistic by LUCC
    year = path[:4]
    month = path[5:8]
    time = year + "-" + month
    lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(year) + "_albert.tif")

    lucc_ds = gdal.Open(lucc_path)
    lucc_array = lucc_ds.GetRasterBand(1).ReadAsArray().astype(int)
    del lucc_ds
    tmp_ds = gdal.Open(tmp_dir)
    arr = tmp_ds.GetRasterBand(1).ReadAsArray()
    statistic_class_ls = [1, 2, 3, 4, 5, 6, 7, 8, 11]
    statistic_dict = {}
    for c in statistic_class_ls:
        re_arr = arr[lucc_array == int(c)]
        re_avg = None
        if re_arr is None:
            re_avg = 100
        else:
            count = len(re_arr)
            re_avg = re_arr.mean()
            statistic_dict[c] = [float(re_avg), count]
    re_dict[time] = statistic_dict
    return re_dict


if __name__ == "__main__":
    # set directory and file path
    tmp_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\TMP\TMP_BTH_RESAMPLE"

    # get tmp path
    tmp_path = os.listdir(tmp_dir)
    tmp_path = [file for file in tmp_path if file.endswith(".tif")]

    # get trend by time windows and lucc(forest type)
    # by year first
    batch_num = 20
    this_batch_left = len(tmp_path)
    iterate_num = math.ceil(this_batch_left / batch_num)
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
            index = i + batch_index * this_batch_num
            # print(i + batch_index * this_batch_num)
            para_ls.append(tmp_path[index])
        batch_index += 1
        with multiprocessing.Pool(processes=5) as pool:
            re = pool.map(para_cal_static, para_ls)
        for item in re:
            result_dict.update(item)
    json.dump(result_dict,  open(r"..\Analysis_JSON\OUTPUT_S_LUCC_Tmp_0923.json", "w"), indent=4)