import json

import numpy as np
from osgeo import gdal
from tqdm import tqdm

if __name__ == "__main__":
    # set directory and file path
    lucc_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_RESAMPLE\CLCD_v01_2021_albert.tif"
    tac_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_1_LAG\tca_1lag_0905.tif"

    # read raster
    lucc_ds: gdal.Dataset = gdal.Open(lucc_path)
    lucc_array = lucc_ds.GetRasterBand(1).ReadAsArray()
    tac_ds = gdal.Open(tac_path)
    tac_array = tac_ds.GetRasterBand(1).ReadAsArray()
    print(f"lucc projection: {lucc_ds.GetGeoTransform()}")
    print(f"TAC projection: {tac_ds.GetGeoTransform()}")

    # statistic
    class_list = [1, 2, 3, 4, 5, 6, 7, 8, 11]
    all_dict = {}
    statistic_dict = {}
    count_class = None
    for i in tqdm(range(len(class_list))):
        select_arr = np.where(lucc_array==class_list[i], tac_array, 2)
        select_1_arr = select_arr[(select_arr != 2) & (select_arr < 0.7) & (select_arr >= 0.6)]
        if select_1_arr is not None:
            count_class = len(select_1_arr)
        else:
            count_class = 0
        statistic_dict[class_list[i]] = count_class
    all_dict["0.6-0.7"] = statistic_dict
    statistic_dict_1 = {}
    for i in tqdm(range(len(class_list))):
        select_arr = np.where(lucc_array==class_list[i], tac_array, 2)
        select_1_arr = select_arr[(select_arr != 2) & (select_arr < 0.6)]
        if select_1_arr is not None:
            count_class = len(select_1_arr)
        else:
            count_class = 0
        statistic_dict_1[class_list[i]] = count_class
    all_dict["<0.6"] = statistic_dict_1
    statistic_dict_2 = {}
    for i in tqdm(range(len(class_list))):
        select_arr = np.where(lucc_array==class_list[i], tac_array, 2)
        select_1_arr = select_arr[(select_arr != 2) & (select_arr >= 0.7)]
        if select_1_arr is not None:
            count_class = len(select_1_arr)
        else:
            count_class = 0
        statistic_dict_2[class_list[i]] = count_class
    all_dict[">0.7"] = statistic_dict_2
    json.dump(all_dict, open(r"..\Anlysis_JSON\COUNT_TAC_BIGGER_0P6.json", "w"))