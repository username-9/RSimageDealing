import multiprocessing
import os
from multiprocessing import Pool

from fontTools.ttx import process
from numba.cuda.simulator.cudadrv.driver import driver
from osgeo import gdal, gdalconst
from sklearn import linear_model

import numpy as np
from statsmodels.sandbox.distributions.mv_normal import np_pi
from tqdm import tqdm

from UtilitiesForDealingImage.ImageBlock import ImageBlock


def linear_detrend(ser: np.ndarray) -> tuple[np.ndarray, any, any]:
    if ser.ndim != 1:
        ser = ser.flatten()
    x = np.arange(len(ser)).reshape(-1, 1)
    model = linear_model.LinearRegression().fit(x, ser)
    trend_components = model.predict(x)
    detrend_ser = ser - trend_components
    co_effect = model.coef_
    intercept = model.intercept_
    return detrend_ser, co_effect, intercept


def season_detrend(ser: np.ndarray) -> np.ndarray:
    array_max = ser.max()
    array_min = ser.min()
    ser = (ser - array_min) / (array_max - array_min)
    return ser


def para_cal_season(arr, index):
    print(f"PID {os.getpid()} Dealing {index}")
    series_a = npp_detrended[index, :, :]
    arr[index, :, :] = season_detrend(series_a)


def para_cal_linear(_i, _j, _merge_array, _npp_detrended):
    print(f"PID {os.getpid()} Dealing i {_i} j {_j}")
    npp_array = _merge_array[:, _i, _j]
    # npp_array = npp_array.reshape(1, -1)
    out_ser, effect, interception = linear_detrend(npp_array)
    _npp_detrended[:, _i, _j] = out_ser.flatten()


if __name__ == '__main__':
    os.chdir(r"F:\DATA\Vegetation_Resilience_D_DATA_C\0831_archive\NPP\NPP_MONTHLY")
    file_list = os.listdir()
    out_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0831_archive\TIME_SERIES_HANDLE\DETREND"
    if os.path.exists(out_dir):
        pass
    else:
        os.mkdir(out_dir)
    for file in file_list:
        if file.endswith(".tif") is not True:
            file_list.remove(file)
    # block = ImageBlock(file_list[0], 500, 500)
    # region = block.get_blocks_region()
    # process_bar = tqdm(region, total=block.all_num, dynamic_ncols=True, position=0, leave=True)
    # process_bar.set_description("Block size and location: ")
    # for x_pos, y_pos, x_size, y_size in process_bar:
    #     process_bar.set_postfix({
    #         "x_pos": str(x_pos),
    #         "y_pos": str(y_pos),
    #         "x_size": str(x_size),
    #         "y_size": str(y_size)
    #     })
    #     try:
    #         array_list = []
    #         for file in file_list:
    #             ds = gdal.Open(file)
    #             block_array = ds.ReadAsArray(x_pos, y_pos, x_size, y_size)
    #             array_list.append(block_array)
    #         merge_array = np.array(array_list)
    #         npp_detrended = np.zeros((len(file_list), merge_array.shape[1], merge_array.shape[2]))
    #         del ds
    #         for i in range(merge_array.shape[1]):
    #             for j in range(merge_array.shape[2]):
    #                 npp_array = merge_array[:, i, j]
    #                 # npp_array = npp_array.reshape(1, -1)
    #                 out_ser, effect, interception = linear_detrend(npp_array)
    #                 npp_detrended[:, i, j] = out_ser.flatten()
    #         for i in range(merge_array.shape[0]):
    #             series_a = npp_detrended[i, :, :]
    #             npp_detrended[i, :, :] = season_detrend(series_a)
    #             output_file = os.path.join(out_dir, file_list[i])
    #             x = npp_detrended[i, :, :]
    #             block.write_by_block(output_file, x, x_pos, y_pos, write_data_type=gdalconst.GDT_Float32)
    #     except Exception as e:
    #         raise Exception(e)
    try:
        ds = gdal.Open(file_list[0], gdal.GA_ReadOnly)
        trans = ds.GetGeoTransform()
        proj = ds.GetProjection()
        del ds
        merge_array = None
        npp_detrended = None
        if not os.path.exists(os.path.join(out_dir, "npp_detrended.npy")):
            array_list = []

            for file in tqdm(file_list):
                ds = gdal.Open(file)
                block_array = ds.ReadAsArray()
                array_list.append(block_array)
                del ds
            merge_array = np.array(array_list)
            npp_detrended = np.zeros((len(file_list), merge_array.shape[1], merge_array.shape[2]))
            for i in tqdm(range(merge_array.shape[1])):
                for j in range(merge_array.shape[2]):
                    npp_array = merge_array[:, i, j]
                    # npp_array = npp_array.reshape(1, -1)
                    out_ser, effect, interception = linear_detrend(npp_array)
                    npp_detrended[:, i, j] = out_ser.flatten()
            # with Pool(processes=4) as p:
            #     para_ls_1 = [(i, j, merge_array, npp_detrended) for i in range(merge_array.shape[1]) for j in range(merge_array.shape[2])]
            #     p.starmap(para_cal_linear, para_ls_1)
            for i in tqdm(range(merge_array.shape[0])):
                series_a = npp_detrended[i, :, :]
                npp_detrended[i, :, :] = season_detrend(series_a)
            np.save(os.path.join(out_dir, "npp_detrended.npy"), npp_detrended)
            # with Pool(processes=8) as pool:
            #     para_ls_2 = [(npp_detrended, i) for i in range(merge_array.shape[0])]
            #     pool.starmap(para_cal_season, para_ls_2)
        else:
            npp_detrended = np.load(os.path.join(out_dir, "npp_detrended.npy"))
        output_file = os.path.join(out_dir, "detrended.tif")
        driver: gdal.Driver = gdal.GetDriverByName('GTiff')
        ds_detrend: gdal.Dataset = driver.Create(output_file, int(npp_detrended.shape[2]),
                                                 int(npp_detrended.shape[1]), bands=npp_detrended.shape[0],
                                                 eType=gdal.GDT_Float32)
        ds_detrend.WriteArray(npp_detrended)
        ds_detrend.SetProjection(proj)
        ds_detrend.SetGeoTransform(trans)
        ds_detrend.FlushCache()
        del ds_detrend

    except Exception as e:
        raise Exception(e)
