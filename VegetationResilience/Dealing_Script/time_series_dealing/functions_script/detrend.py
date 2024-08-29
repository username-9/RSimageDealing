import os

from osgeo import gdal, gdalconst
from sklearn import linear_model

import numpy as np
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


if __name__ == '__main__':
    os.chdir(r"C:\Users\PZH\Desktop\output_Clip")
    file_list = os.listdir()
    if os.path.exists(r"..\output_detrended"):
        pass
    else:
        os.mkdir(r"..\output_detrended")
    for file in file_list:
        if file.endswith(".tif") is not True:
            file_list.remove(file)
    block = ImageBlock(file_list[0], 300, 300)
    region = block.get_blocks_region()
    output_file = os.path.join(r"..\output_detrended", "detrended_merge.tif")
    process_bar = tqdm(region, total=block.all_num, dynamic_ncols=True, position=0, leave=True)
    process_bar.set_description("Block size and location: ")
    for x_pos, y_pos, x_size, y_size in process_bar:
        process_bar.set_postfix({
            "x_pos": str(x_pos),
            "y_pos": str(y_pos),
            "x_size": str(x_size),
            "y_size": str(y_size)
        })
        try:
            array_list = []
            for file in file_list:
                ds = gdal.Open(file)
                block_array = ds.ReadAsArray(x_pos, y_pos, x_size, y_size)
                array_list.append(block_array)
            merge_array = np.array(array_list)
            npp_detrended = np.zeros((len(file_list), merge_array.shape[1], merge_array.shape[2]))
            del ds
            for i in range(merge_array.shape[1]):
                for j in range(merge_array.shape[2]):
                    npp_array = merge_array[:, i, j]
                    # npp_array = npp_array.reshape(1, -1)
                    out_ser, effect, interception = linear_detrend(npp_array)
                    npp_detrended[:, i, j] = out_ser.flatten()
            block.write_by_block(output_file, npp_detrended, x_pos, y_pos, write_data_type=gdalconst.GDT_Float32)
        except Exception as e:
            raise Exception(e)
