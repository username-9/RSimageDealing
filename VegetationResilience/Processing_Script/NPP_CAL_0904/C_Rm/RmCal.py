import calendar
import os
from multiprocessing import Pool

import numpy as np
from matplotlib.pyplot import pause
from osgeo import gdal
from tqdm import tqdm

from UtilitiesForProcessingImage.UtilityFunction import workdir_filelist


def get_year_para_array(directory, year_i):
    x_list = os.listdir(directory)
    x_list = [file for file in x_list if file.endswith(".tif")]
    x_ds = gdal.Open(os.path.join(directory, x_list[year_i]))
    x_array = x_ds.GetRasterBand(1).ReadAsArray()
    del x_ds
    return x_array


def para_cal(file_path):
    # ref_dict = get_specific_lucc_dict()
    # set directory
    out_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\Rm\Rm_DAILY_ParaChange"

    lai_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0831_archive\LAI\LAI_BTH_CLIP"

    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_RESAMPLE"
    sla_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\PARAMETER\SLA"
    y_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\PARAMETER\Y"
    r_leaf_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\PARAMETER\Rleaf"
    r_stem_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\PARAMETER\Rstem"
    r_root_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\PARAMETER\Rroot"

    # get geograph reference
    ref_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0831_archive\GPP\GPP_BTH_CLIP\200003.tif"
    ref_ds = gdal.Open(ref_path, gdal.GA_ReadOnly)
    ds_trans = ref_ds.GetGeoTransform()
    ds_proj = ref_ds.GetProjection()
    ds_width = ref_ds.RasterXSize
    ds_height = ref_ds.RasterYSize
    ds_band_num = ref_ds.RasterCount
    del ref_ds

    # iterate temperature file for calculating month by month
    tmp_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\TMP\TMP_BTH_RESAMPLE"
    tmp_list = os.listdir(tmp_dir)
    tmp_list = [tmp for tmp in tmp_list if tmp.endswith(".tif")]
    i = tmp_list.index(file_path)
    year_index = int((1 + (i + 1)) / 12) - 1
    # get lai and temperature array
    lai_list = os.listdir(lai_dir)
    lai_list = [lai for lai in lai_list if lai.endswith(".tif")]
    lai_ds = gdal.Open(os.path.join(lai_dir, lai_list[i]))
    lai_array = lai_ds.GetRasterBand(1).ReadAsArray()
    lai_array = lai_array * 0.1  # LAI scale
    del lai_ds

    tmp_ds = gdal.Open(os.path.join(tmp_dir, file_path), gdal.GA_ReadOnly)
    tmp_array = tmp_ds.GetRasterBand(1).ReadAsArray()
    del tmp_ds
    tmp_array = tmp_array * 0.1

    # get SLA and parameter array
    # SLA array
    sla_array = get_year_para_array(sla_dir, year_index)
    # get y array
    y_array = get_year_para_array(y_dir, year_index)
    # get r leaf array
    r_leaf_array = get_year_para_array(r_leaf_dir, year_index)
    # get r stem array
    r_stem_array = get_year_para_array(r_stem_dir, year_index)
    # get r root array
    r_root_array = get_year_para_array(r_root_dir, year_index)
    # get lucc
    lucc_array = get_year_para_array(lucc_dir, year_index)
    # create empty Rm array
    rm_array = np.zeros(lucc_array.shape, dtype=np.float32)
    # create Rm raster
    rm_path = os.path.join(out_dir, "rm_" + os.path.basename(file_path)[:-4] + ".tif")
    driver = gdal.GetDriverByName('GTiff')
    rm_ds: gdal.Dataset = driver.Create(rm_path, ds_width, ds_height, bands=ds_band_num, eType=gdal.GDT_Float32)
    rm_ds.SetGeoTransform(ds_trans)
    rm_ds.SetProjection(ds_proj)

    # calculation for Rm
    year = eval(file_path[:4])
    month = int(file_path[5:8])
    _, day_of_month = calendar.monthrange(year, month)
    for i in tqdm(range(ds_height)):
        for j in range(ds_width):
            class_num = int(lucc_array[i, j])
            # print(class_num)
            if class_num == 5:
                pass
            if class_num in {1, 2, 3, 4, 5, 6, 7, 11}:
                sla = sla_array[i, j]
                if sla == 0:
                    rm_array[i, j] = 0
                else:
                    m1 = lai_array[i, j] / sla
                    m2 = m1 / (1 + y_array[i, j])
                    m3 = m2 * y_array[i, j]
                    # there's another algorithm to exchange 2
                    temp_co = 2 ** ((tmp_array[i, j] - 20) / 10)
                    r1 = m1 * r_leaf_array[i, j] * temp_co
                    r2 = m2 * r_stem_array[i, j] * temp_co
                    r3 = m3 * r_root_array[i, j] * temp_co
                    rm_array[i, j] = r1 + r2 + r3
            else:
                sla = sla_array[i, j]
                if sla == 0:
                    rm_array[i, j] = 0
                else:
                    lai = lai_array[i, j]
                    tmp = tmp_array[i, j]
                    rm = (lai / sla) * 0.5 * (2 ** ((tmp - 20) / 10))
                    rm_array[i, j] = rm
    # rm_array = rm_array * day_of_month
    rm_ds.WriteArray(rm_array)
    rm_ds.FlushCache()
    del rm_ds


if __name__ == "__main__":
    tmp_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\TMP\TMP_BTH_RESAMPLE"
    tmp_file_ls = workdir_filelist(tmp_dir)
    with Pool(processes=10) as pool:
        results = pool.map(para_cal, tmp_file_ls)
