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

    re_arr = None

    #create specific tiff
    output_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_ALL_SAME_TYPE\TYPE_SAME_VEGETATION_LUCC.tif"
    driver:gdal.Driver = gdal.GetDriverByName('GTiff')
    re_ds = driver.CreateCopy(output_path, init_ds)
    del init_ds

    # judgement
    for file in tqdm.tqdm(lucc_file_ls[1:]):
        temp_arr = gdal.Open(file).ReadAsArray()
        if re_arr is None:
            # re_arr = (merge_arr == temp_arr) # get the same lucc
            re_arr = ((merge_arr != 0) & (merge_arr != 6) & (merge_arr != 8)) & ((temp_arr != 0) & (temp_arr != 6) & (temp_arr != 8))
        else:
            # re_arr = (merge_arr == temp_arr) & re_arr # get the same lucc
            re_arr = ((temp_arr != 0) & (temp_arr != 6) & (temp_arr != 8)) & re_arr

    re_arr = merge_arr * re_arr

    # write
    re_ds.WriteArray(re_arr)
    re_ds.FlushCache()
    del re_ds
