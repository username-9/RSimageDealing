import os

import numpy as np
import tqdm

from UtilitiesForProcessingImage import ImageBlock
from UtilitiesForProcessingImage.UtilityFunction import merge_arrays_with_coords
from VegetationResilience.Processing_Script.Time_Series_Processing.Analysis.VR_TimeSeries_Anlysis.B_Key_Detrend_Point_Analysis import \
    detect_all_mutational_site


def para_cal(_arr, _x_pos, _y_pos, _x_size, _y_size):
    re_arr = np.zeros((_arr.shape[0], _y_size, _x_size))
    for i in tqdm.tqdm(range(_y_size)):
        for j in range(_x_size):
            h_arr = _arr[:, i, j]
            re_0 = detect_all_mutational_site(h_arr, 0.05)
            for key in re_0:
                re_arr[key, i ,j] = 1
    return re_arr, _x_pos, _y_pos


if __name__ == "__main__":
    # parallel calculation
    # calculate with blocks from the series of tac
    # output raster with location of key point weight * height * time interval (260)
    tac_s_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_SERIES\tac_series_0919_3w.tif"
    blocks = ImageBlock.ImageBlock(tac_s_path, 300, 300)
    def_generator = blocks.read_by_generator()
    re = blocks.parallel_calculation(para_cal, 20, 9, region_generator=def_generator)
    width = blocks.image_width
    height = blocks.image_height
    ndim = blocks.image_bands
    merge_array = np.zeros((ndim, height, width))
    for re_list in re:
        for item in re_list:
            arr, x_pos, y_pos = item
            merge_arrays_with_coords(arr, (y_pos, x_pos), merge_array)
    ndarray_filepath = "./VR_Sta_Json/Key_Point_Array.npy"
    np.save(ndarray_filepath, merge_array)

