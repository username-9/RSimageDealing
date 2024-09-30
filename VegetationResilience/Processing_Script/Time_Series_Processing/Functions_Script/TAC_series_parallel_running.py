import math
import multiprocessing
import os

import numpy as np
import tqdm
from numpy import ndarray
from osgeo import gdalconst

import UtilitiesForProcessingImage
from Image_TAC import acf


def tac_series(series_name: np.ndarray, _time_window: int, lag: int = 1) -> ndarray:
    """
    Calculates the TCA for a series with a time window sliding
    :param series_name: a ndarray series which is 3D numpy array and the 0 axis indicates the time
    :param _time_window: window sliding image
    :param lag: the tca lag parameter
    :return: the array after the calculation (a 3D numpy array)(whose length is (len(year)-time_window+1))
    """
    _tac_ser = np.zeros(shape=(series_name.shape[0] - _time_window + 1, series_name.shape[1], series_name.shape[2]))
    # for i in tqdm.tqdm(range(_time_window, series_name.shape[0]), position=1, leave=False):
    for i in range(_time_window, series_name.shape[0] + 1):
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


# define parallel running function
def para_cal(block_array, x_position, y_position, x_remain, y_remain):
    print(f"PID {os.getpid()} Handling {x_position, y_position ,x_remain, y_remain}")
    _time_window = 3
    tac_ser = tac_series(block_array, _time_window)
    return tac_ser, x_position, y_position, x_remain, y_remain


if __name__ == '__main__':
    os.chdir(r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\DETREND")
    file_list = os.listdir()
    out_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES"
    if os.path.exists(out_dir):
        pass
    else:
        os.mkdir(out_dir)
    file_path = r"detrended_0919.tif"
    output_file = os.path.join(out_dir, "tac_series_0919_3w.tif")
    output_array = os.path.join(out_dir, "tac_series_0919_3w.npy")
    time_window = 3
    parallel_num = 8
    batch_block_num = 20

    # get divide regions
    block = UtilitiesForProcessingImage.ImageBlock.ImageBlock(file_path, 300, 300)
    region_generator = block.read_by_generator()
    region_array = block.get_list_of_block_array(batch_block_num, region_generator)

    # construct result array
    arr_size = (block.image_bands-time_window+1, block.image_height, block.image_width)
    re_arr = np.ones(arr_size) * 2

    # handle by block
    pro_bar = tqdm.tqdm(range(math.ceil(block.all_num / batch_block_num)), position=0, leave=True)
    pro_bar.set_description("Dealing by block")

    for i in pro_bar:
        para_list = next(region_array)
        with multiprocessing.Pool(processes=parallel_num) as pool:
            result = pool.starmap(para_cal, para_list)
        for re in tqdm.tqdm(result, position=1, leave=False):
            temp_arr, x_offset, y_offset, x_size, y_size = re
            re_arr[:, y_offset:y_offset + y_size, x_offset:x_offset + x_size] = temp_arr
            block.write_by_block(output_file, temp_arr, x_offset, y_offset, write_data_type=gdalconst.GDT_Float32)

    # for i in pro_bar:
    #     block_array, x_offset, y_offset, x_size, y_size = next(block_generator)
    #     pro_bar.set_postfix({
    #         "x_offset": x_offset,
    #         "y_offset": y_offset,
    #         "x_size": x_size,
    #         "y_size": y_size
    #     })

    # save array
    np.save(output_array, re_arr)
