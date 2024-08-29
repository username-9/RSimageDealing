import os
from multiprocessing import Pool

import numpy as np
from osgeo import gdal

from UtilitiesForDealingImage.UtilityFunction import workdir_filelist


def para_cal(input_file):
    print(f"---PID: {os.getpid()}---\n---Dealing with {input_file}---")
    file_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\Rm_USING_UNIT_PERCENT"
    file_list = os.listdir(file_dir)
    for file in file_list:
        if not file.endswith(".tif"):
            file_list.remove(file)
    index = file_list.index(input_file)

    # GPP directory
    gpp_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\GPP\GPP_INTEGRATE_OUTPUT_MEAN_CLIP"
    gpp_list = os.listdir(gpp_dir)
    for file in gpp_list:
        if not file.endswith(".tif"):
            gpp_list.remove(file)

    # get gpp array and basement construction information
    gpp_path = os.path.join(gpp_dir, gpp_list[index + 1])
    gpp_ds: gdal.Dataset = gdal.Open(gpp_path)  # add one to begin at 2000-02
    gpp_array = gpp_ds.GetRasterBand(1).ReadAsArray()
    gpp_band: gdal.Band = gpp_ds.GetRasterBand(1)
    ds_trans = gpp_ds.GetGeoTransform()
    ds_proj = gpp_ds.GetProjection()
    ds_width = gpp_ds.RasterXSize
    ds_height = gpp_ds.RasterYSize
    ds_band_num = gpp_ds.RasterCount
    del gpp_ds

    # get rm array
    rm_ds = gdal.Open(input_file)
    rm_array = rm_ds.GetRasterBand(1).ReadAsArray()
    del rm_ds

    # construct NPP raster
    output_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\NPP_MEAN_DAY"
    npp_path = os.path.join(output_dir, "npp_" + os.path.basename(input_file)[3:])
    driver = gdal.GetDriverByName('GTiff')
    npp_ds: gdal.Dataset = driver.Create(npp_path, ds_width, ds_height, bands=ds_band_num, eType=gdal.GDT_Float64)
    npp_ds.SetGeoTransform(ds_trans)
    npp_ds.SetProjection(ds_proj)

    # calculate npp array
    gpp_array = gpp_array.astype(np.float64)
    rm_array = rm_array.astype(np.float64)
    rg_array = (gpp_array - rm_array) * 0.25
    npp_array = gpp_array - rm_array - rg_array
    npp_array[npp_array < 0] = 0

    # write in raster
    npp_ds.WriteArray(npp_array)
    npp_ds.FlushCache()
    del npp_ds


if __name__ == "__main__":
    work_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\Rm_USING_UNIT_PERCENT"
    file_ls = workdir_filelist(work_dir)

    with Pool(processes=5) as pool:
        results = pool.map(para_cal, file_ls)

