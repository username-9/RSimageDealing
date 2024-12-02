from pickletools import uint4, uint8

import tqdm
from osgeo import gdal
import numpy as np
import os


if __name__ == "__main__":
    # directory
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_RESAMPLE"
    os.chdir(lucc_dir)
    lucc_file_ls = [file for file in os.listdir(lucc_dir) if file.endswith(".tif")]

    # condition judgement
    init_ds:gdal.Dataset = gdal.Open(lucc_file_ls[0])
    init_trans = init_ds.GetGeoTransform()
    init_proj = init_ds.GetProjection()

    merge_arr = init_ds.ReadAsArray()

    re_arr = np.zeros(merge_arr.shape)

    #create specific tiff
    output_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_ALL_SAME_TYPE\TYPE_RANGE_LUCC_12345711.tif"
    driver:gdal.Driver = gdal.GetDriverByName('GTiff')
    re_ds = driver.CreateCopy(output_path, init_ds)
    del init_ds

    # merge
    for file in tqdm.tqdm(lucc_file_ls):
        arr = gdal.Open(file).ReadAsArray()
        arr = arr.astype(np.int64)
        re_arr += ((arr != 0) & (arr != 6) & (arr != 8))


    # write
    re_ds.WriteArray(re_arr.astype(np.int64))
    re_ds.FlushCache()
    del re_ds
