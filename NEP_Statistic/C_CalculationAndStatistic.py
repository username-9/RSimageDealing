import json
import os
import numpy as np
import tqdm
from osgeo import gdal

if __name__ == "__main__":
    # set directory and file path
    separate_tiff_dir = r"C:\Users\PZH\Desktop\ProgrammeGuangdong\1029\XianAreaClip"

    # definition
    sta_dict = {}
    separate_tiff_dir_list = os.listdir(separate_tiff_dir)

    # calculation
    for directory in tqdm.tqdm(separate_tiff_dir_list):
        xian_cal_sta_dict = {}
        year_tif_list = os.listdir(os.path.join(separate_tiff_dir, directory))
        year_tif_list = [file for file in year_tif_list if file.endswith('.tif')]
        for tif in year_tif_list:
            arr = gdal.Open(os.path.join(separate_tiff_dir, directory, tif)).ReadAsArray()
            ## NEP we use has 1km * 1km spatial resolution and a ton carbon double-dioxide sum
            carbon_arr = arr[arr > -9990] # avoid error from data type
            carbon_contain = float(np.sum(carbon_arr))
            area = len(carbon_arr)
            name = tif.split('.')[0]
            xian_cal_sta_dict[name] = [carbon_contain, area]
        sta_dict[directory] = xian_cal_sta_dict
    with open(r"C:\Users\PZH\Desktop\ProgrammeGuangdong\1029\Xian_Carbon_STATISTIC.json", 'w', encoding='utf-8') as f:
        json.dump(sta_dict, f, indent=4, ensure_ascii=False)
    # dict_to_xlsx(sta_dict, r"C:\Users\PZH\Desktop\ProgrammeGuangdong\vector_raster\1024\STATISTIC.xlsx")
    print("done")