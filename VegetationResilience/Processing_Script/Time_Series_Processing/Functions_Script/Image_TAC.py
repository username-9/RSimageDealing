import os

import numpy as np
import tqdm
from osgeo import gdal, gdalconst

import UtilitiesForProcessingImage
from UtilitiesForProcessingImage import ImageBlock
from UtilitiesForProcessingImage.ImageProcessing import set_nodata


def acf(value_time: np.ndarray, lag: int, time_interval: int = 1) -> any:
    """
    calculates ACF for given year and lag
    :param time_interval:
    :param value_time: the series by year
    :param lag: the interval of TAC analysis
    :return: the ACF series with length (len(year) - lag)
    """
    if value_time.ndim != 1:
        raise ValueError('y must be 1-dimensional')
    # ta = np.zeros((lag, 1))
    n_max = np.max(value_time)
    n_min = np.min(value_time)
    tca_sum = 0
    if n_max != 0 or n_min != 0:
        cross_sum = np.zeros((value_time.shape[0] - lag, 1))
        series_mean = np.mean(value_time)
        for t in range(lag, value_time.shape[0], time_interval):
            cross_sum[t-lag] = (value_time[t] - series_mean) * (value_time[t - lag] - series_mean)
        denominator = np.dot((value_time - series_mean).T, (value_time - series_mean))
        if denominator == 0:
            tca_sum = 0
        else:
            tca_sum = (np.sum(cross_sum, axis=0) / denominator)[0]
    else:
        tca_sum = 2
    return tca_sum


def acf_all_lag(value_time: np.ndarray, num_lag: int) -> np.ndarray:
    """
    calculates ACF for all lag(from 1 to num_lag)
    :param num_lag: the number of lag
    :param value_time: the series by year
    :return: a list containing auto-correlations of all the lag
    """
    tca_all_lag = []
    for lag_index in range(num_lag):
        tca_all_lag.append(acf(value_time, lag_index + 1))
    tca_all_lag = np.array(tca_all_lag)
    return tca_all_lag


if __name__ == '__main__':
    os.chdir(r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\DETREND")
    file_list = os.listdir()
    out_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_1_LAG"
    if os.path.exists(out_dir):
        pass
    else:
        os.mkdir(out_dir)
    # for file in file_list:
    #     if file.endswith(".tif") is not True:
    #         file_list.remove(file)
    output_file = os.path.join(out_dir, "tca_1lag_0905.tif")
    detrend_file = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\DETREND\detrended_0905.tif"
    block = ImageBlock.ImageBlock(detrend_file, 300, 300)
    block.scale = [1]
    block.offset = [0]
    region = block.get_blocks_region()
    lag_all = 1
    process_bar = tqdm.tqdm(region, total=block.all_num, dynamic_ncols=True, position=0, leave=True)
    process_bar.set_description("Block size and location: ")
    for x_pos, y_pos, x_size, y_size in process_bar:
        process_bar.set_postfix({
            "x_pos": str(x_pos),
            "y_pos": str(y_pos),
            "x_size": str(x_size),
            "y_size": str(y_size)
        })
        try:
            # print(
            #     f'the block region is x = {x_pos}, y = {y_pos}, the size is x = {x_size}, y = {y_size}')
            # array_list = []
            # for file in file_list:
            #     ds = gdal.Open(file)
            #     block_array = ds.ReadAsArray(x_pos, y_pos, x_size, y_size)
            #     array_list.append(block_array)
            # merge_array = np.array(array_list)
            array_list = []
            merge_ds: gdal.Dataset = gdal.Open(detrend_file)
            for i in tqdm.tqdm(range(merge_ds.RasterCount), position=1, leave=False):
                array_list.append(merge_ds.GetRasterBand(i+1).ReadAsArray(x_pos, y_pos, x_size, y_size))
            del merge_ds
            merge_array = np.array(array_list)
            npp_tac = np.zeros((lag_all, merge_array.shape[1], merge_array.shape[2]))
            for i in range(merge_array.shape[1]):
                for j in range(merge_array.shape[2]):
                    npp_array = merge_array[:, i, j]
                    # npp_array = npp_array.reshape(1, -1)
                    tca = acf_all_lag(npp_array, lag_all)
                    tca.resize((lag_all, 1, 1))
                    npp_tac[:, i, j] = tca[:, 0, 0]
            # del ds
            block.write_by_block(output_file, npp_tac, x_pos, y_pos, write_data_type=gdalconst.GDT_Float32)
        except Exception as e:
            raise Exception(e)
    # ds = gdal.Open(r"..\output_TCA\tac.tif", gdal.GA_Update)
    # set_nodata(ds, 0)
    # del ds
