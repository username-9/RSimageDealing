import multiprocessing
import os
from multiprocessing import Pool

import cv2
import numpy as np
from osgeo import gdal
from tqdm import tqdm

from UtilitiesForDealingImage.ReadMain import raster_read, read_band_scale_offset

from UtilitiesForDealingImage import ImageBlock
from UtilitiesForDealingImage.WriteMain import raster_write, set_band_scale_offset


def drawing_by_block(dataset_1, dataset_2, color_arr, location):
    print(f"running on {multiprocessing.current_process().pid}")
    print(location)
    op_x, op_y, x_size, y_size = location

    # classification_list_1 = [[1.005351, 1000.000000], [1000.000001, 3000.000000],
    #                          [3000.000001, 6000.000000], [6000.000001, 10000.000000],
    #                          [10000.000001, 30000.000000], [30000.000001, 60000.000000],
    #                          [60000.000001, 100000.000000], [100000.000001, 150000.000000],
    #                          [150000.000001, 300000.000000], [300000.000001, 480143.032509]]
    classification_list_2 = [[0.00000, 1.00000], [1.00001, 3.00000],
                             [3.00001, 5.00000], [5.00001, 7.00000],
                             [7.00001, 10.00000], [10.00001, 15.00000],
                             [15.00001, 20.00000], [20.00001, 25.00000],
                             [25.00001, 30.00000], [30.00001, 55.94670]]

    classification_list_1 = [[0, 0.03], [0.0300001, 0.08], [0.0800001, 0.13],
                             [0.130001, 0.19], [0.190001, 0.26], [0.260001, 0.35],
                             [0.350001, 0.47], [0.470001, 0.63], [0.630001, 0.8],
                             [0.800001, 2]]

    class_with_list = False

    block = 100

    dataset_1 = raster_read(dataset_1)
    dataset_2 = raster_read(dataset_2)

    factor_1_arr = dataset_1.ReadAsArray(op_x, op_y, x_size, y_size)
    factor_2_arr = dataset_2.ReadAsArray(op_x, op_y, x_size, y_size)

    del dataset_1
    del dataset_2

    factor_1_max, factor_1_min = np.max(factor_1_arr), np.min(factor_1_arr)
    print(f"Dataset-1: max: {factor_1_max}, min: {factor_1_min}")
    factor_2_max, factor_2_min = np.max(factor_2_arr), np.min(factor_2_arr)
    print(f"Dataset-2: max: {factor_2_max}, min: {factor_2_min}")
    out_arr = np.zeros((3, factor_1_arr.shape[0], factor_1_arr.shape[1]), dtype=np.uint8)

    # link map with default classification method
    if classification_list_1 is None and classification_list_2 is None:
        factor_1_norm = (factor_1_arr - factor_1_min) / (factor_1_max - factor_1_min)
        factor_2_norm = (factor_2_arr - factor_2_min) / (factor_2_max - factor_2_min)
        for i in range(factor_1_norm.shape[0]):
            for j in range(factor_1_norm.shape[1]):
                x_loc = int(factor_1_norm[i, j] * color_arr.shape[1]) - 1
                y_loc = int((1 - factor_2_norm[i, j]) * color_arr.shape[0]) - 1
                out_arr[::-1, i, j] = color_arr[y_loc, x_loc, :]
    else:
        # get the color classification list by own defined classification method
        if classification_list_1 is not None and classification_list_2 is not None:
            class_num_1 = len(classification_list_1)
            class_num_2 = len(classification_list_2)
            class_range_1 = []
            class_range_2 = []
            if class_with_list:
                if class_num_1 * block == color_arr.shape[1] and class_num_2 * block == color_arr.shape[0]:
                    print("classification of factor 1 as:")
                    for i in range(class_num_1):
                        if i == 0:
                            print(f"class {1}: min -> {classification_list_1[i]}")
                            class_range_1.append([factor_1_min, classification_list_1[i]])
                        else:
                            print(f"{i + 1}: {classification_list_1[i]} -> {classification_list_1[i + 1]}")
                            class_range_1.append([classification_list_1[i], classification_list_1[i + 1]])
                    print("classification of factor 2 as:")
                    for i in range(class_num_2):
                        if i == 0:
                            print(f"class {1}: min -> {classification_list_2[i]}")
                            class_range_2.append([factor_2_min, classification_list_2[i]])
                        else:
                            print(f"{i + 1}: {classification_list_2[i]} -> {classification_list_2[i + 1]}")
                            class_range_2.append([classification_list_2[i], classification_list_2[i + 1]])
                if class_num_1 == (color_arr.shape[1] + 1) and class_num_2 == (color_arr.shape[0] + 1):
                    print("classification of factor 1 as:")
                    for i in range(class_num_1 - 1):
                        print(f"{i + 1}: {classification_list_1[i]} -> {classification_list_1[i + 1]}")
                        class_range_1.append([classification_list_1[i], classification_list_1[i + 1]])
                    print("classification of factor 2 as:")
                    for i in range(class_num_2 - 1):
                        print(f"{i + 1}: {classification_list_2[i]} -> {classification_list_2[i + 1]}")
                        class_range_2.append([classification_list_2[i], classification_list_2[i + 1]])
            else:
                class_range_1 = classification_list_1
                class_range_2 = classification_list_2
        else:
            raise ValueError(f"the size of classification array can't match the number of color number")
        color_offset = block / 2
        for i in range(factor_1_arr.shape[0]):
            for j in range(factor_1_arr.shape[1]):
                x_loc = None
                y_loc = None
                class_num = len(class_range_1)
                for k in range(class_num):
                    fact_1 = factor_1_arr[i, j]
                    if class_range_1[k][0] <= factor_1_arr[i, j] <= class_range_1[k][1]:
                        x_loc = int(((k + 1) / class_num) * color_arr.shape[1] - 1 - color_offset)
                        # index in python is begun at 0
                        break
                class_num = len(class_range_2)
                for m in range(class_num):
                    fact_2 = factor_2_arr[i, j]
                    if class_range_2[m][0] <= factor_2_arr[i, j] <= class_range_2[m][1]:
                        y_loc = int(((class_num - m) / class_num) * color_arr.shape[0] - 1 - color_offset)
                        break
                if x_loc is None:
                    x_loc = 0
                if y_loc is None:
                    y_loc = 0
                if x_loc == 0 and y_loc == 0:
                    out_arr[::-1, i, j] = np.array([-1, -1, -1]).reshape(3, )
                else:
                    out_arr[::-1, i, j] = color_arr[y_loc, x_loc, :]
    return out_arr, location


if __name__ == "__main__":
    raster_1 = r"D:\Drawing\2018_unframents_1.tif"
    raster_2 = r"D:\Drawing\2018_USMpop.tif"
    # raster_1 = r"C:\Users\PZH\Desktop\drawing\MEM\2007_unfragments_sin_1Lha_1_origin.tif"
    # raster_2 = r"C:\Users\PZH\Desktop\drawing\MEM\2007_BTH_USMpop_raster_origin.tif"
    ds_1 = raster_read(raster_1)

    color_arr = cv2.imread(r"C:\Users\PZH\Desktop\drawing\MEM\output\color_map_output.png")

    region_list = ImageBlock.ImageBlock(raster_1, 3000, 3000).get_blocks_region()
    region_list_1 = [[raster_1, raster_2, color_arr, item] for item in region_list]
    del region_list

    with Pool(processes=7) as pool:
        results = pool.starmap(drawing_by_block, region_list_1)

    output_path = r"D:\Drawing\output\output_map_2018_1.tif"
    # output_path = r"D:\Drawing\output\test.tif"
    ref_geotrans = ds_1.GetGeoTransform()
    ref_srs = ds_1.GetProjection()
    image_width = ds_1.GetRasterBand(1).XSize
    image_height = ds_1.GetRasterBand(1).YSize

    del ds_1

    driver = gdal.GetDriverByName("GTiff")
    print("make sure that the tif is first creat or may be get some error like before")
    for result in tqdm(results):
        arr, loc = result
        op_x, op_y, x_size, y_size = loc
        if os.path.exists(output_path):
            out_ds = gdal.Open(output_path, gdal.GA_Update)
        else:
            out_ds: gdal.Dataset = driver.Create(output_path, image_width,
                                                 image_height, bands=3, eType=gdal.GDT_UInt16)
            out_ds.SetGeoTransform(ref_geotrans)
            out_ds.SetProjection(ref_srs)
        out_ds.WriteArray(arr, op_x, op_y)
        out_ds.FlushCache()
        del out_ds
