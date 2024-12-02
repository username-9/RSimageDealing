import os

import numpy as np
import cv2
import tqdm
from osgeo import gdal


def array_dilate(array: np.ndarray, value_to_dilate, count):
    """
    [Test Done]
    :param array:
    :param value_to_dilate:
    :param count:
    :return:
    """
    mask = (array == value_to_dilate) * np.ones(array.shape, np.uint8)
    kernel = np.ones((count * 2, count * 2), np.uint8)
    dilated_arr = cv2.dilate(mask, kernel)
    array[dilated_arr.astype(np.bool_)] = value_to_dilate
    return array


def array_erode(array: np.ndarray, value_to_erode, count, fill_value=0):
    mask = (array == value_to_erode) * np.ones(array.shape, np.uint8)
    kernel = np.ones((count * 2, count * 2), np.uint8)
    eroded_arr = cv2.erode(mask, kernel)
    array[eroded_arr.astype(np.bool_)] = fill_value
    return array


if __name__ == '__main__':
    # set directory
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\A2_LUCC_DILATE"
    lucc_ls = os.listdir(lucc_dir)
    lucc_ls = [file for file in lucc_ls if file.endswith(".tif")]
    output_dir = r"/VegetationResilience/Processing_Script/C_Time_Series_Processing\Analysis\VR_Analysis_By_Pixel\Further_Processing\Ref_And_Processing_Files"

    ref_arr = gdal.Open(os.path.join(lucc_dir, lucc_ls[0])).ReadAsArray()
    out_arr = np.ones((len(lucc_ls), ref_arr.shape[0], ref_arr.shape[1]), dtype=np.uint8)
    # processing each lucc
    for index, lucc in tqdm.tqdm(enumerate(lucc_ls)):
        ds = gdal.Open(os.path.join(lucc_dir, lucc), gdal.GA_Update)
        arr = ds.ReadAsArray()
        erode_value_ls = [8, 6]
        for i in erode_value_ls:
            array_dilate(arr, value_to_dilate=i, count=2)
            # array_erode(arr, value_to_erode=i, count=10, fill_value=100)
        out_arr[index] = arr
        ds.WriteArray(arr)
        ds.FlushCache()
        del ds
    np.save(os.path.join(output_dir, "A_Array_Dilate.npy"), out_arr)