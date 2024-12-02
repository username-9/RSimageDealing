import shutil

import tqdm
from osgeo import gdal
import os
import numpy as np


if __name__ == "__main__":
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\A2_LUCC_DILATE"
    # lucc_same_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_ALL_SAME_TYPE\TYPE_SAME_LUCC.tif"
    lucc_same_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_ALL_SAME_TYPE\TYPE_SAME_VEGETATION_LUCC.tif"
    dst_dir = lucc_dir+"_copy_1126"

    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)

    try:
        shutil.copytree(lucc_dir, dst_dir)
    except Exception as e:
        print(e)

    lucc_ls = [file for file in os.listdir(dst_dir) if file.endswith('.tif')]

    lucc_same_arr = gdal.Open(lucc_same_path).ReadAsArray().astype(np.int8)
    lucc_same_arr[lucc_same_arr != 0] = 1

    for file in tqdm.tqdm(lucc_ls):
        ds = gdal.Open(os.path.join(dst_dir, file), gdal.GA_Update)
        arr = ds.ReadAsArray().astype(np.int8)
        arr_new = arr * lucc_same_arr
        ds.WriteArray(arr_new)
        ds.FlushCache()
        del ds

    print("Done")



