import os

from dask import array as dask_array

import numpy as np
from numpy import ndarray
from osgeo import gdalconst

import UtilitiesForProcessingImage
from F_Image_TAC import acf


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

if __name__ == "__main__":
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
    block = UtilitiesForProcessingImage.BasicUtility.ImageBlock.ImageBlock(file_path, 300, 300)
    # arr_size = (block.image_bands - time_window + 1, block.image_height, block.image_width)
    # re_arr = np.ones(arr_size) * 2

    # handle by parallel running
    detrend_array = np.load(r"npp_detrended_0905.npy")
    # block_region = block.get_blocks_region()

    # Using Dask to running as parallel
    # 假设每个时间步有10个数据点，每个空间维度200x200
    dask_arr_detrend = dask_array.from_array(detrend_array, chunks=(block.image_bands, 300, 300))
    del block

    # 使用 map_blocks 并行处理每个块
    result = dask_arr_detrend.map_blocks(tac_series,
                                         _time_window=3,
                                         dtype=np.float32, drop_axis=0)

    # 计算结果
    result_computed = result.compute()
    print(result_computed.shape)

    # save array
    np.save(output_array, result_computed)