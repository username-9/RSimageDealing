import os
from typing import Any, Generator

import numpy as np
import matplotlib.pyplot as plt
import tqdm
from numpy import ndarray
from osgeo import gdalconst

import UtilitiesForDealingImage
from Image_TCA import acf
from multiprocessing import Process, Pool


def tac_series(series_name: np.ndarray, _time_window: int, lag: int = 1) -> ndarray:
    """
    Calculates the TCA for a series with a time window sliding
    :param series_name: a ndarray series which is 3D numpy array and the 0 axis indicates the time
    :param _time_window: window sliding image
    :param lag: the tca lag parameter
    :return: the array after the calculation (a 3D numpy array)
    """
    _tac_ser = np.zeros(shape=(series_name.shape[0] - _time_window + 1, series_name.shape[1], series_name.shape[2]))
    for i in range(_time_window, series_name.shape[0]):
        acf_series = series_name[i - _time_window:i, :, :]
        for j in range(acf_series.shape[1]):
            for k in range(acf_series.shape[2]):
                dealing_series = acf_series[:, j, k]
                acf_value = acf(dealing_series, lag)
                _tac_ser[i - _time_window, j, k] = acf_value
    return _tac_ser


def main_deal(_block_generator, _block, _time_window):
    _block_array, _x_offset, _y_offset, x, y = next(_block_generator)
    _tac_ser = tac_series(_block_array, _time_window)
    _block.write_by_block(output_file, _tac_ser, _x_offset, _y_offset, write_data_type=gdalconst.GDT_Float32)
    print(f"{os.getpid()} process dealing with block: x: {_x_offset}, y: {_y_offset}, x_size: {x}, y_size: {y}")


if __name__ == '__main__':
    os.chdir(r"C:\Users\PZH\Desktop\output_detrended")
    file_list = os.listdir()
    if os.path.exists(r"..\output_series_tac"):
        pass
    else:
        os.mkdir(r"..\output_series_tac")
    file_path = r"detrended_merge.tif"
    output_file = os.path.join(r"..\output_series_tac", "tac_series.tif")
    time_window = 3
    block = UtilitiesForDealingImage.ImageBlock.ImageBlock(file_path, 300, 300)
    block_generator = block.read_by_generator()
    pro_bar = tqdm.tqdm(range(block.all_num))
    pro_bar.set_description("Dealing by block")
    for i in pro_bar:
        block_array, x_offset, y_offset, x_size, y_size = next(block_generator)
        pro_bar.set_postfix({
            "x_offset": x_offset,
            "y_offset": y_offset,
            "x_size": x_size,
            "y_size": y_size
        })
        tac_ser = tac_series(block_array, time_window)
        block.write_by_block(output_file, tac_ser, x_offset, y_offset, write_data_type=gdalconst.GDT_Float32)

    # Using multiprocess
    # pool = Pool(5)

