import json

import pandas as pd
from osgeo import gdal
import os
import numpy as np
from tqdm import tqdm

from UtilitiesForProcessingImage.BasicUtility.ImageTransform import coordination_transform
from VegetationResilience.Drawing.Draw_with_raster import class_dict

if __name__ == "__main__":
    # tif_1_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES\tac_s_trend_0929.tif"
    tif_1_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\NPP_TREND\NPP_TREND_0919.tif"
    tif_2_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_1_LAG\tca_1lag_0919.tif"
    lucc_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_ALL_SAME_TYPE\TYPE_SAME_VEGETATION_LUCC.tif"

    dst_proj4 = "+proj=tmerc +lat_0=0 +lon_0=117 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +units=m +no_defs"

    arr_1 = coordination_transform(tif_1_path, target_proj4=dst_proj4, out_tif_path="o1.tif", to_ds=True, resample_algorithm=gdal.GRA_NearestNeighbour).ReadAsArray()
    arr_2 = coordination_transform(tif_2_path, target_proj4=dst_proj4, out_tif_path="o2.tif", to_ds=True, resample_algorithm=gdal.GRA_NearestNeighbour).ReadAsArray()
    lucc_arr = coordination_transform(lucc_path, target_proj4=dst_proj4, resample_algorithm=gdal.GRA_NearestNeighbour
                                      , out_tif_path="o3.tif", to_ds=True).ReadAsArray()

    count_dict = {}

    c_dict = class_dict

    for key, value in tqdm(c_dict.items()):
        temp_dict = {}
        tac_min = 0.3
        # temp_arr_1 = np.zeros(arr_1.shape)
        temp_arr_1 = arr_1[lucc_arr == key]
        temp_arr_2 = arr_2[lucc_arr == key]
        count_num = np.count_nonzero((temp_arr_1 > 0) & (temp_arr_1 < 1) & (temp_arr_2 < tac_min) & (-1 <= temp_arr_2))
        temp_dict[f"Q1: npp>0&&tac<{tac_min}"] = count_num
        count_num = np.count_nonzero((temp_arr_1 < 0) & (temp_arr_1 > -1) & (temp_arr_2 < tac_min) & (-1 <= temp_arr_2))
        temp_dict[f"Q2: npp<0&&tac<{tac_min}"] = count_num
        count_num = np.count_nonzero((temp_arr_1 > 0) & (temp_arr_1 < 1) & (temp_arr_2 >= tac_min) & (1 >= temp_arr_2))
        temp_dict[f"Q3: npp<0&&tac>={tac_min}"] = count_num
        count_num = np.count_nonzero((temp_arr_1 < 0) & (temp_arr_1 > -1) & (temp_arr_2 >= tac_min) & (1 >= temp_arr_2))
        temp_dict[f"Q4: npp>0&&tac>={tac_min}"] = count_num
        count_dict[value] = temp_dict



    # count_num = np.count_nonzero((arr_1 < 0) & (arr_2 < 0.5))
    # count_dict["npp<0&&tac<0.5"] = count_num
    # count_num = np.count_nonzero((arr_1 < 0) & (arr_2 >= 0.5))
    # count_dict["npp<0&&tac>=0.5"] = count_num
    # count_num = np.count_nonzero((arr_1 > 0) & (arr_2 < 0.5))
    # count_dict["npp>0&&tac<0.5"] = count_num
    # count_num = np.count_nonzero((arr_1 > 0) & (arr_2 >= 0.5))
    # count_dict["npp>0&&tac>=0.5"] = count_num

    # count_num = np.count_nonzero((arr_1 < 0))
    # count_dict["npp trend<0"] = count_num
    # count_num = np.count_nonzero((arr_1 >= 0))
    # count_dict["npp trend>=0"] = count_num

    json_path = "RF3_Ref_And_Processing_Files/I9_NPPe0_TACe0.3_Sta_by_LUCC_Near.json"
    with open(json_path, "w") as outfile:
        json.dump(count_dict, outfile, indent=4)
