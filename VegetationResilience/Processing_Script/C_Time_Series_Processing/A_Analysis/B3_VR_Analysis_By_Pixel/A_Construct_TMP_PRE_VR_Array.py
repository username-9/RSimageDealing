import datetime
import multiprocessing
import  os

import numpy as np
from osgeo import gdal
from dateutil.relativedelta import relativedelta


def para_cal(_vr_arr, year, month):
    # set directory
    tmp_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\TMP\TMP_BTH_RESAMPLE"
    pre_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\PRE\PRE_RESAMPLE_OUTPUT"
    out_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\CONSTRUCT_ARRAY_TMP_PRE_VR_1010"

    # get file path mainly by VR path
    tmp_path = os.path.join(tmp_dir, f"{year}-"+f"{month}".zfill(3)+".tif")
    if not os.path.exists(tmp_path):
        raise ValueError (f"no tmp file {tmp_path}")
    pre_path = os.path.join(pre_dir, f"{year}-"+f"{month}".zfill(3)+".tif")
    if not os.path.exists(pre_path):
        raise ValueError (f"no pre file {pre_path}")

    # get tmp and pre array
    tmp_ds = gdal.Open(tmp_path)
    tmp_array = tmp_ds.GetRasterBand(1).ReadAsArray()
    del tmp_ds
    pre_ds = gdal.Open(pre_path)
    pre_array = pre_ds.GetRasterBand(1).ReadAsArray()
    del pre_ds

    # construct 3 dimension array
    re_arr = np.stack([tmp_array, pre_array, _vr_arr], axis=0)
    out_path = os.path.join(out_dir, f"{year}-"+f"{month}".zfill(3)+".npy")
    np.save(out_path, re_arr)


if __name__ == "__main__":
    vr_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES\tac_series_0919_3w.tif"
    vr_ds = gdal.Open(vr_path)
    vr_array = vr_ds.ReadAsArray()
    del vr_ds
    time = datetime.datetime(2001, 5, 1)
    para_ls = []
    for i in range(vr_array.shape[0]):
        para_ls.append((vr_array[i, :, :], time.year, time.month))
        time = time + relativedelta(months=1)
        
    del vr_array
    with multiprocessing.Pool(processes=5) as pool:
        pool.starmap(para_cal, para_ls)
    print("done")