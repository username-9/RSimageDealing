import math
import multiprocessing

import numpy as np
import tqdm
from osgeo import gdal, gdalconst
from sklearn.linear_model import LinearRegression

import UtilitiesForProcessingImage.BasicUtility.ImageBlock


def para_cal_s_trend(arr, x_pos, y_pos, x_size, y_size):
    height = arr.shape[1]
    width = arr.shape[2]
    s_trend_array = np.ones((height, width), np.float32)
    for i in tqdm.tqdm(range(height)):
        for j in range(width):
            data_array = np.abs(arr[:, i, j])
            tolerance = 1e-1
            if np.all(np.abs(data_array - 2) < tolerance):
                continue
            model = LinearRegression()
            x = np.arange(1, data_array.shape[0] + 1).reshape(-1, 1)
            model.fit(x, data_array)
            slope = model.coef_[0]
            s_trend_array[i, j] = slope
    return s_trend_array, x_pos, y_pos, x_size, y_size


if __name__ == "__main__":
    # set directory and file path
    lucc_dir = r""
    tac_series = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES\tac_series_0913.tif"

    # read array from raster
    tac_s_ds = gdal.Open(tac_series)
    tac_s_array = tac_s_ds.ReadAsArray()
    ref_trans = tac_s_ds.GetGeoTransform()
    ref_proj = tac_s_ds.GetProjection()
    data_type = tac_s_ds.GetRasterBand(1).DataType
    del tac_s_ds

    # get linear trend from TAC series
    output_trend_raster = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES\tac_s_trend_0929.tif"
    block = UtilitiesForProcessingImage.BasicUtility.ImageBlock.ImageBlock(tac_series, 300, 300)
    region_gene = block.read_by_generator()
    region_array = block.get_list_of_block_array(20, region_gene)

    arr_size = (block.image_height, block.image_width)
    re_arr = np.ones(arr_size) * 2

    pro_bar = tqdm.tqdm(range(math.ceil(block.all_num / 20)), position=0, leave=True)
    pro_bar.set_description("Dealing by block")
    for i in pro_bar:
        para_list = next(region_array)
        with multiprocessing.Pool(processes=6) as pool:
            result = pool.starmap(para_cal_s_trend, para_list)
        for re in tqdm.tqdm(result, position=1, leave=False):
            temp_arr, x_offset, y_offset, x_size, y_size = re
            re_arr[y_offset:y_offset + y_size, x_offset:x_offset + x_size] = temp_arr
            block.write_by_block(output_trend_raster, temp_arr, x_offset, y_offset, write_data_type=gdalconst.GDT_Float32)