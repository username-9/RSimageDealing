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
    for i in range(_time_window, series_name.shape[0]+1):
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
def para_cal(_block_region, _shared_nparray, _shared_nparray_re):
    print(f"PID {os.getpid()} Handling {_block_region}")
    x_offset, y_offset, x_size, y_size = _block_region
    ser_arr = _shared_nparray[:, y_offset:y_offset + y_size, x_offset:x_offset + x_size]
    _time_window = 3
    tac_ser = tac_series(ser_arr, _time_window)
    _shared_nparray_re[:, y_offset:y_offset + y_size, x_offset:x_offset + x_size] = tac_ser


if __name__ == '__main__':
    os.chdir(r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\DETREND")
    file_list = os.listdir()
    out_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES"
    if os.path.exists(out_dir):
        pass
    else:
        os.mkdir(out_dir)
    file_path = r"detrended_0905.tif"
    output_file = os.path.join(out_dir, "tac_series_0905.tif")
    output_array = os.path.join(out_dir, "tac_series_0905_test.npy")
    time_window = 3
    block = UtilitiesForProcessingImage.ImageBlock.ImageBlock(file_path, 200, 200)
    arr_size = (block.image_bands-time_window+1, block.image_height, block.image_width)
    re_arr = np.ones(arr_size) * 2
    # handle by block
    block_generator = block.read_by_generator()
    pro_bar = tqdm.tqdm(range(block.all_num), position=0, leave=True)
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
        re_arr[:, y_offset:y_offset + y_size, x_offset:x_offset + x_size] = tac_ser
        block.write_by_block(output_file, tac_ser, x_offset, y_offset, write_data_type=gdalconst.GDT_Float32)

    # # handle by parallel running
    # detrend_array = np.load(r"npp_detrended_0903.npy")
    # block_region = block.get_blocks_region()
    # del block

    # # construct trend shared array
    # shared_array_base = Array('f', detrend_array.size)
    # shared_nparray = np.frombuffer(shared_array_base.get_obj(), dtype=np.float32)
    # shared_nparray = shared_nparray.reshape(detrend_array.shape)
    # np.copyto(shared_nparray, detrend_array)
    # # construct result shared array
    # re_shape = (detrend_array.shape[0]-time_window+1, detrend_array.shape[1], detrend_array.shape[2])
    # re_size = (detrend_array.shape[0]-time_window+1) * detrend_array.shape[1] * detrend_array.shape[2]
    # re_array = np.ones(re_shape) * 2 # use 2 as invaluable data
    # shared_array_base_re = Array('f', re_size)
    # shared_nparray_re = np.frombuffer(shared_array_base_re.get_obj(), dtype=np.float32)
    # shared_nparray_re = shared_nparray_re.reshape(re_shape)
    # np.copyto(shared_nparray_re, re_array)

    # # parallel running using dask
    # dask_arr_detrend = dask_array.from_array(detrend_array)
    # dask_arr_re = dask_array.from_array(re_arr)
    # delayed_tasks = [dask.delayed(para_cal)(region, dask_arr_detrend, dask_arr_re) for region in block_region]
    # dask.compute(*delayed_tasks)

    # save array
    np.save(output_array, re_arr)
