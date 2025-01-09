import calendar
import os
from multiprocessing import Pool

import numpy as np
from osgeo import gdal

from UtilitiesForProcessingImage.BasicUtility.UtilityFunction import workdir_filelist


def para_cal(input_file):
    print(f"---PID: {os.getpid()}---\n---Dealing with {input_file}---")
    file_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\Rm\Rm_DAILY_ParaChange"
    file_list = os.listdir(file_dir)
    file_list = [file for file in file_list if file.endswith(".tif")]
    index = file_list.index(input_file)

    # GPP directory
    gpp_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0831_archive\GPP\GPP_INTEGRATE_OUTPUT_MEAN_0830_CLIP"

    gpp_list = os.listdir(gpp_dir)
    gpp_list = [file for file in gpp_list if file.endswith(".tif")]
    print(f"gpp file : {gpp_list[index + 1]}\nRm file : {input_file}")

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
    output_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\NPP\NPP_MONTHLY"
    npp_path = os.path.join(output_dir, "npp_" + os.path.basename(input_file)[3:])
    driver = gdal.GetDriverByName('GTiff')
    npp_ds: gdal.Dataset = driver.Create(npp_path, ds_width, ds_height, bands=ds_band_num, eType=gdal.GDT_Float64)
    npp_ds.SetGeoTransform(ds_trans)
    npp_ds.SetProjection(ds_proj)

    # calculate npp array
    # gpp_array = gpp_array * 0.0001 # scale has been handled
    rm_array = rm_array.astype(np.float64)
    # gpp_array = gpp_array # Gpp Modify Factor
    rg_array = (gpp_array - rm_array) * 0.25
    npp_array = gpp_array - rm_array - rg_array
    year = eval(input_file[3:7])
    month = int(input_file[8:11])
    _, day_of_month = calendar.monthrange(year, month)
    npp_array = npp_array * day_of_month
    # np.save(os.path.join(output_dir, "npp_" + os.path.basename(input_file)[:-4] + ".npy"), npp_array)
    npp_array[npp_array < 0] = 0

    # write in raster
    npp_ds.WriteArray(npp_array)
    npp_ds.FlushCache()
    del npp_ds


if __name__ == "__main__":
    work_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\Rm\Rm_DAILY_ParaChange"
    file_ls = workdir_filelist(work_dir)

    with Pool(processes=10) as pool:
        results = pool.map(para_cal, file_ls)

