import json

import pandas as pd
from osgeo import gdal
import os
import numpy as np

from VegetationResilience.Drawing.Draw_with_raster import class_dict

if __name__ == "__main__":
    # tif_1_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES\tac_s_trend_0929.tif"
    tif_1_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\NPP_TREND\NPP_TREND_0919.tif"
    lucc_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_ALL_SAME_TYPE\TYPE_SAME_VEGETATION_LUCC.tif"

    arr_1 = gdal.Open(tif_1_path).ReadAsArray()
    lucc_arr = gdal.Open(lucc_path).ReadAsArray()

    count_dict = {}

    c_dict = class_dict

    for key, value in c_dict.items():
        temp_dict = {}
        tac_min = 0.3
        # temp_arr_1 = np.zeros(arr_1.shape)
        temp_arr_1 = arr_1[lucc_arr == key]
        count_num = np.count_nonzero(temp_arr_1 > 0)
        temp_dict["TACs Trend>0"] = count_num
        count_num = np.count_nonzero(temp_arr_1 < 0)
        temp_dict["TACs Trend<0"] = count_num
        count_dict[value] = temp_dict




    # count_num = np.count_nonzero((arr_1 < 0))
    # count_dict["npp trend<0"] = count_num
    # count_num = np.count_nonzero((arr_1 >= 0))
    # count_dict["npp trend>=0"] = count_num

    json_path = "RF3_Ref_And_Processing_Files/I6_TACsCritic0_Sta_by_LUCC.json"
    with open(json_path, "w") as outfile:
        json.dump(count_dict, outfile, indent=4)
