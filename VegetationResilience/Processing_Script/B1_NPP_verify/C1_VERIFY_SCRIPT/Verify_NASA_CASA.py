import os

import numpy as np
from osgeo import gdal
from sklearn.metrics import r2_score
from tqdm import tqdm

from VegetationResilience.Drawing.Scatter import scatter


def get_file_ls(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    file_list = os.listdir(directory)
    file_list = [file for file in file_list if file.endswith(".tif")]
    return file_list


def rmse(y_true, y_pred):
    return np.sqrt(((y_true - y_pred) ** 2).mean()), np.sqrt((((y_true - y_pred) / y_true) ** 2).mean())


def mae(y_true, y_pred):
    return np.mean(np.abs(y_true - y_pred))


def mse(y_true, y_pred):
    return ((y_true - y_pred) ** 2).mean()


def function_format(x, a, b):
    return a * x + b


if __name__ == "__main__":
    # set directory
    npp_verify_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0831_archive\REF_NPP\NPP_V\NPP_V_200101_201512_NASA_CASA_1km"
    npp_ref_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0831_archive\REF_NPP\NPP_REF\REF_NPP_NASA_CASA_CLIP"  # REF NPP Clip First
    nparray_name = "../F_VerifyArray/VerifyArray_0903_NASA_CASA.npy"

    # get file
    npp_verify_ls = get_file_ls(npp_verify_dir)
    npp_ref_ls = get_file_ls(npp_ref_dir)

    # get ref value and verify value
    verify_array = []

    if not os.path.exists(nparray_name):
        verify_temp = None
        for npp_v in tqdm(npp_verify_ls, total=len(npp_ref_dir)):
            index = npp_verify_ls.index(npp_v)
            if index >= len(npp_ref_ls):
                break
            npp_r = npp_ref_ls[index]
            # get dataset
            npp_v_ds: gdal.Dataset = gdal.Open(os.path.join(npp_verify_dir, npp_v))
            npp_v_array = npp_v_ds.ReadAsArray()
            del npp_v
            npp_r_ds: gdal.Dataset = gdal.Open(os.path.join(npp_ref_dir, npp_r))
            npp_r_array = npp_r_ds.ReadAsArray()
            del npp_r
            npp_r_array[npp_r_array==(-3.402823e+38)] = 0
            npp_r_one_a = npp_r_array.ravel()
            npp_v_one_a = npp_v_array.ravel() * 1000
            verify_temp = np.column_stack((npp_r_one_a, npp_v_one_a))
            verify_array.append(verify_temp)
        verify_array = np.array(verify_array)
        np.save(nparray_name, verify_array)
    else:
        verify_array = np.load(nparray_name)

    # pre-dealing for data
    static_array = np.concatenate(verify_array, axis=0)
    # filtered_array = static_array[~(np.any(static_array == 0, axis=1))]
    filtered_array = static_array[~(np.any(static_array <= 0, axis=1))]
    # calculate the RMSE
    array_x = filtered_array[:, 0]
    array_y = filtered_array[:, 1]
    rmse, r_rmse = rmse(array_x, array_y)
    mae = mae(array_x, array_y)
    mse = mse(array_x, array_y)
    r_2 = r2_score(array_x, array_y)
    print(f"RMSE: {rmse}\nMAE: {mae}\nMSE: {mse}\nR-2 Score: {r_2}\nRelative RMSE:{r_rmse}")
    # plot scatter
    scatter(array_x, array_y, ee=2, ci=90)