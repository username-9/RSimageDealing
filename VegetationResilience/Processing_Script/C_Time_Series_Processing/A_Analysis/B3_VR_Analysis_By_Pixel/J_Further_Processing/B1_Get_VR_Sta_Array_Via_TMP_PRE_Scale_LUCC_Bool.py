import json
import math
import multiprocessing
import os
from datetime import datetime

import numpy as np
import tqdm
from dateutil.relativedelta import relativedelta
from osgeo import gdal


def para_cal(npy_path, _key_ls):
    ref_dict = {}
    npy_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\CONSTRUCT_ARRAY_TMP_PRE_VR_1010"
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\A4_LUCC_DILATE_EXCEPT_LUCC_CHANGE"
    min_pre = 0
    max_pre = 350
    pre_batch_num = (max_pre - min_pre) / 10
    pre_batch_num = math.ceil(pre_batch_num)
    arr = np.load(os.path.join(npy_dir, npy_path))
    tmp_arr = arr[0, :, :] / 10
    pre_arr = arr[1, :, :] / 10
    vr_arr = arr[2, :, :]
    _time = f"{npy_path[:4]}-{npy_path[5:]}"
    lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(npy_path[:4]) + "_albert.tif")
    lucc_ds = gdal.Open(lucc_path)
    lucc_arr = lucc_ds.ReadAsArray()
    lucc_class = [1, 2, 3, 4, 5 ,6, 7, 8, 11]
    del lucc_ds
    for key in tqdm.tqdm(_key_ls):
        class_dict = {}
        for i in lucc_class:
            re_arr = vr_arr[(key[0] <= tmp_arr) & (tmp_arr < key[0] + 1) & (key[1] <= pre_arr) & (pre_arr < key[1] + 10) & (lucc_arr == i)].astype(float)
            class_dict[i] = list(re_arr[re_arr != 2].flatten())
        ref_dict[str(key)] = class_dict
    return _time, ref_dict


def merge_dicts_with_lists(d1, d2):
    """
    extend value list of d2 to the same key value in d1 list
    :param d1: target dictionary
    :param d2: handle dictionary
    :return: None
    """
    for key, value in d2.items():
        if key in d1:
            d1[key].extend(value)
        else:
            d1[key] = value
    return d1


if __name__ == '__main__':
    npy_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\CONSTRUCT_ARRAY_TMP_PRE_VR_1010"
    file_ls = os.listdir(npy_dir)
    file_ls = [file for file in file_ls if file.endswith(".npy")]
    key_ls = []
    min_tmp = -24
    max_tmp = 31
    min_pre = 0
    max_pre = 429
    pre_batch_num = (max_pre - min_pre) / 10
    pre_batch_num = math.ceil(pre_batch_num)
    for i in range(max_tmp - min_tmp + 1):
        for j in range(pre_batch_num):
            key_ls.append((min_tmp + i, min_pre + j * 10))
    para_ls = [(file, key_ls) for file in file_ls]
    with multiprocessing.Pool(processes=9) as pool:
        re = pool.starmap(para_cal, para_ls)
    re_dict = {}
    merge_re_dict = {}
    time = datetime(2001, 5, 1)
    for time, result in tqdm.tqdm(re):
        re_dict[time] = result
        # merge_re_dict = merge_dicts_with_lists(merge_re_dict, result)
    json_path = r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script\C_Time_Series_Processing\A_Analysis\B3_VR_Analysis_By_Pixel\J_Further_Processing\RF3_Ref_And_Processing_Files\A_VR_STATISTIC.json"
    # merge_json_path = r"./Merge_Data.json"
    with open(json_path, 'w') as f:
        json.dump(re_dict, f, indent=4)
    # with open(merge_json_path, 'w') as f:
    #     json.dump(merge_re_dict, f, indent=4)