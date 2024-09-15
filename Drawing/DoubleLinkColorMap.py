import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import hsv_to_rgb
import cartopy.crs as ccrs
import cv2
from osgeo import gdal
from tqdm import tqdm

from UtilitiesForProcessingImage.ReadMain import read_band_scale_offset, raster_read
from UtilitiesForProcessingImage.WriteMain import raster_write


# def double_link_color_map(map_x_data: np.ndarray, map_y_data: np.ndarray, two_dim_color_arr: np.ndarray,
#                           resize: bool = False, block_position: tuple = (0.1, 0.1, 1, 1)):
#     """
#     draw maps with double link color map
#     :param two_dim_color_arr: color block used for legend
#     :param block_position: color legend position
#     :param resize: whether to resize the factor map data
#     :param map_x_data: one of the factor in mapping (should be 2-dimensional array)
#     :param map_y_data: another factor in mapping (should be 2-dimensional array)
#     :param resize: resize the data by map_x_data
#     :return: a matplotlib color map
#     """
#     if resize:
#         map_y_data.resize(map_x_data.shape)
#     if map_x_data.shape == map_y_data.shape:
#         rows, cols, colors = two_dim_color_arr.shape
#         fig: plt.Figure = plt.figure(figsize=(rows, cols))
#         # draw main picture
#         ax_main = fig.add_subplot(projection=ccrs.Mollweide())
#         # ax_main.stock_img()
#         # ax_main.coastlines()
#         # draw legend picture
#         ax_legend = fig.add_axes(
#             (block_position[0], block_position[1], rows * block_position[2], cols * block_position[3]))
#         # ax_legend.imshow(two_dim_color_arr, cmap='viridis')
#         fig.show()
#     else:
#         raise ValueError("the size of data is not equal")


def construct_arr(range_1: list, range_2: list, color_num) -> tuple[np.ndarray, np.ndarray]:
    x_v_arr = np.linspace(start=range_1[0], stop=range_1[1], num=color_num)
    x_v_arr = np.tile(x_v_arr, (color_num, 1))
    y_v_arr = np.linspace(range_2[0], range_2[1], num=color_num)
    y_v_arr = np.tile(y_v_arr, (color_num, 1))
    y_v_arr = y_v_arr.T.copy()
    y_v_arr = np.flip(y_v_arr, axis=0).copy()
    return x_v_arr, y_v_arr


def two_dimensional_color_map(x_Hue: int or float, y_Hue: int  or float,
                              x_Saturability: list[int], y_Saturability: list[int],
                              color_num: int = 5, value: int = 255, color_block_size: int = 50
                              , output_size: tuple = (500, 500), x_v=None, y_v=None) -> np.ndarray:
    """
    draw pictures with two-dimensional color map
    :param y_v: y direction value
    :param x_v: x direction value
    :param output_size: output array size
    :param x_Hue: the Hue of the x dimension of the picture  (direction ——) (0~180)
    :param y_Hue: the Hue of the y dimension of the picture  (direction ||) (0~180)
    :param x_Saturability:  the Saturability of the x dimension of the picture (0~255)
    :param y_Saturability:  the Saturability of the y dimension of the picture (0~255)
    :param color_num: the number of color intervals of the picture
    :param value: the value(HSV) of color (0~255)
    :param color_block_size: the size of each block of color
    :return: a 2-dimensional color map
    """
    # construct Hue array
    x_Hue_arr = x_Hue * np.ones((color_num, color_num))
    y_Hue_arr = y_Hue * np.ones((color_num, color_num))

    # construct Saturability array
    x_S_arr, y_S_arr = construct_arr(x_Saturability, y_Saturability, color_num)

    # construct Value array
    if x_v is None or y_v is None:
        x_v_arr = value * np.ones((color_num, color_num))
        y_v_arr = value * np.ones((color_num, color_num))
    else:
        x_v_arr, y_v_arr = construct_arr(x_v, y_v, color_num)

    # build x-picture
    x_hsv_img = np.zeros((color_num, color_num, 3), dtype=np.uint8)
    x_hsv_img[:, :, 0] = x_Hue_arr
    x_hsv_img[:, :, 1] = x_S_arr
    x_hsv_img[:, :, 2] = x_v_arr
    x_hsv_img = matrix_expand_square(x_hsv_img, color_block_size)
    x_img = cv2.cvtColor(x_hsv_img, cv2.COLOR_HSV2RGB)
    # resized_image = cv2.resize(x_img, (1000, 1000))
    # cv2.imshow('x_image', resized_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # build y-picture
    y_hsv_img = np.zeros((color_num, color_num, 3), dtype=np.uint8)
    y_hsv_img[:, :, 0] = y_Hue_arr
    y_hsv_img[:, :, 1] = y_S_arr
    y_hsv_img[:, :, 2] = y_v_arr
    y_hsv_img = matrix_expand_square(y_hsv_img, color_block_size)
    y_img = cv2.cvtColor(y_hsv_img, cv2.COLOR_HSV2RGB)
    # resized_image = cv2.resize(y_img, (500, 500))
    # color_map = cv2.add(x_img, y_img)
    # img = cv2.resize(color_map, (500, 500))
    # cv2.imshow("img", img)
    # cv2.resizeWindow("img", 500, 500)
    # cv2.waitKey(0)

    # combine color maps
    combine = cv2.addWeighted(cv2.resize(x_img, (output_size[0], output_size[1])), 0.8,
                              cv2.resize(y_img, (output_size[0], output_size[1])), 0.8, 0.5)
    # cv2.imshow("img", combine)
    # cv2.waitKey()
    return combine


def matrix_expand_square(array: np.ndarray, block_size: int) -> np.ndarray:
    """
    expend a 3-dim matrix with square blocks
    :param array: the matrix to be expanded
    :param block_size: the size of each block
    :return: expanded matrix
    """
    rows, cols, colors = array.shape
    new_arr = np.empty((rows * block_size, cols * block_size, colors), dtype=np.uint8)
    for k in range(colors):
        for i in range(rows):
            for j in range(cols):
                new_arr[i * block_size:(i + 1) * block_size, j * block_size:(j + 1) * block_size, k] \
                    = np.full((block_size, block_size), array[i, j, k], dtype=array.dtype)
    return new_arr


def colormap_array(dataset_1: gdal.Dataset, dataset_2: gdal.Dataset,
                   color_array: np.ndarray,
                   classification_list_1: list = None,
                   classification_list_2: list = None, block: int = 100, class_with_list: bool = False,
                   nodata=-1) -> np.ndarray:
    """
    output an array with three bands with linking color map array
    :param nodata: set nodata value for each band
    :param class_with_list: whether giving a list to the classification instead of the point num
    :param block: size of color array block, it can be inferred from the color array(color map 's width divides by color number)
    :param classification_list_2: the second raster classification list defined by own
    :param classification_list_1: the first raster classification list defined by own
    :param dataset_1: the first dataset (direction in color map ——）
    :param dataset_2: the second dataset （direction in color map |)
    :param color_array: the color map array
    :return: map with color link
    """
    factor_1_arr = dataset_1.ReadAsArray()
    factor_2_arr = dataset_2.ReadAsArray()
    factor_1_max, factor_1_min = np.max(factor_1_arr), np.min(factor_1_arr)
    print(f"Dataset-1: max: {factor_1_max}, min: {factor_1_min}")
    factor_2_max, factor_2_min = np.max(factor_2_arr), np.min(factor_2_arr)
    print(f"Dataset-2: max: {factor_2_max}, min: {factor_2_min}")
    out_arr = np.zeros((3, factor_1_arr.shape[0], factor_1_arr.shape[1]), dtype=np.uint8)

    # link map with default classification method
    if classification_list_1 is None and classification_list_2 is None:
        factor_1_norm = (factor_1_arr - factor_1_min) / (factor_1_max - factor_1_min)
        factor_2_norm = (factor_2_arr - factor_2_min) / (factor_2_max - factor_2_min)
        for i in tqdm(range(factor_1_norm.shape[0])):
            for j in range(factor_1_norm.shape[1]):
                x_loc = int(factor_1_norm[i, j] * color_array.shape[1]) - 1
                y_loc = int((1 - factor_2_norm[i, j]) * color_array.shape[0]) - 1
                out_arr[::-1, i, j] = color_array[y_loc, x_loc, :]
    else:
        # get the color classification list by own defined classification method
        if classification_list_1 is not None and classification_list_2 is not None:
            class_num_1 = len(classification_list_1)
            class_num_2 = len(classification_list_2)
            class_range_1 = []
            class_range_2 = []
            if class_with_list:
                if class_num_1 * block == color_array.shape[1] and class_num_2 * block == color_array.shape[0]:
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
                if class_num_1 == (color_array.shape[1] + 1) and class_num_2 == (color_array.shape[0] + 1):
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
                print(f"Using defined range list")
                class_range_2 = classification_list_2
        else:
            raise ValueError(f"the size of classification array can't match the number of color number")
        color_offset = block / 2
        for i in tqdm(range(factor_1_arr.shape[0])):
            for j in range(factor_1_arr.shape[1]):
                x_loc = None
                y_loc = None
                class_num = len(class_range_1)
                for k in range(class_num):
                    fact_1 = factor_1_arr[i, j]
                    if class_range_1[k][0] <= factor_1_arr[i, j] <= class_range_1[k][1]:
                        x_loc = int(((k + 1) / class_num) * color_array.shape[1] - 1 - color_offset)
                        # index in python is begun at 0
                        break
                class_num = len(class_range_2)
                for m in range(class_num):
                    fact_2 = factor_2_arr[i, j]
                    if class_range_2[m][0] <= factor_2_arr[i, j] <= class_range_2[m][1]:
                        y_loc = int(((class_num - m) / class_num) * color_array.shape[0] - 1 - color_offset)
                        break
                if x_loc is None:
                    x_loc = 0
                if y_loc is None:
                    y_loc = 0
                if x_loc == 0 or y_loc == 0:
                    out_arr[::-1, i, j] = np.array([-1, -1, -1]).reshape(3, )
                else:
                    out_arr[::-1, i, j] = color_array[y_loc, x_loc, :]
    return out_arr


def add_grid(img_arr, color_num: int, origin_location: tuple = (0, 0)):
    x_block_size = int(img_arr.shape[1] / color_num)
    y_block_size = int(img_arr.shape[0] / color_num)
    # draw row lines
    for i in range(1, int((img_arr.shape[0]) / (img_arr.shape[0] / color_num) + 1)):
        cv2.line(img_arr, (origin_location[0], i * x_block_size), (img_arr.shape[1], i * x_block_size),
                 (250, 250, 250), 1)
    for i in range(1, int((img_arr.shape[1]) / (img_arr.shape[1] / color_num) + 1)):
        cv2.line(img_arr, (i * y_block_size, origin_location[1]), (i * y_block_size, img_arr.shape[0]),
                 (250, 250, 250), 1)


def image_improve(img):
    # 将RGB图像转换到YCrCb空间中
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
    # 将YCrCb图像通道分离
    channels = cv2.split(ycrcb)
    # 以下代码详细注释见官网：
    # https://docs.opencv.org/4.1.0/d5/daf/tutorial_py_histogram_equalization.html
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(30, 30))
    clahe.apply(channels[0], channels[0])
    cv2.merge(channels, ycrcb)
    cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR, img)
    return img


def improve_saturation(img_arr):
    # 转换到HSV色彩空间
    hsv_image = cv2.cvtColor(img_arr, cv2.COLOR_BGR2HSV)
    # 分离HSV通道
    h, s, v = cv2.split(hsv_image)
    # 增加饱和度，这里乘以1.5，可以根据需要调整
    s = np.clip(s * 1.6, 0, 255).astype(np.uint8)
    # 合并HSV通道
    hsv_image = cv2.merge([h, s, v])
    # 转换回BGR色彩空间
    saturated_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
    return saturated_image


if __name__ == "__main__":
    # read rasters
    raster_1 = r"C:\Users\PZH\Desktop\drawing\MEM\2007_unfragments_sin_1Lha_1_origin.tif"
    raster_2 = r"C:\Users\PZH\Desktop\drawing\MEM\2007_BTH_USMpop_raster_origin.tif"
    ds_1 = raster_read(raster_1)
    ds_2 = raster_read(raster_2)

    # get two-dim color map array
    # color_arr = two_dimensional_color_map(90, 120, [30, 240],
    #                                       [30, 240], color_num=10, color_block_size=30)
    # color_arr = two_dimensional_color_map(60, 130, [70, 255],
    #                                       [70, 255], x_v=[200, 150], y_v=[200, 150],
    #                                       color_num=10, color_block_size=50, output_size=(1000, 1000))
    # # color_arr = two_dimensional_color_map(50, 155, [0, 255],
    # #                                       [0, 255],
    # #                                       color_num=10, color_block_size=30)
    # # color_arr = image_improve(color_arr)
    # color_arr = improve_saturation(color_arr)
    # color_map_path = r"C:\Users\PZH\Desktop\drawing\MEM\output\color_map_2.png"
    # # add grid for color map
    # # add_grid(color_arr, 10)
    # cv2.imwrite(color_map_path, color_arr)
    # cv2.imshow("img", color_arr)
    # cv2.waitKey(0)

    # get the map with color link
    defined_classification__1_list = [[1.005351, 1000.000000], [1000.000001, 3000.000000],
                                      [3000.000001, 6000.000000], [6000.000001, 10000.000000],
                                      [10000.000001, 30000.000000], [30000.000001, 60000.000000],
                                      [60000.000001, 100000.000000], [100000.000001, 150000.000000],
                                      [150000.000001, 300000.000000], [300000.000001, 480143.032509]]
    defined_classification__2_list = [[0.00000, 1.00000], [1.00001, 3.00000],
                                      [3.00001, 5.00000], [5.00001, 7.00000],
                                      [7.00001, 10.00000], [10.00001, 15.00000],
                                      [15.00001, 20.00000], [20.00001, 25.00000],
                                      [25.00001, 30.00000], [30.00001, 55.94670]]

    # color_arr = cv2.imread(r"C:\Users\PZH\Desktop\drawing\MEM\output\color_map_3.png")
    # add_grid(color_arr, 10)
    # color_map_path = r"C:\Users\PZH\Desktop\drawing\MEM\output\color_map_output.png"
    # cv2.imwrite(color_map_path, color_arr)
    # cv2.imshow("img", color_arr)
    # cv2.waitKey(0)

    color_arr = cv2.imread(r"C:\Users\PZH\Desktop\drawing\MEM\output\color_map_output.png")
    cv2.imshow("img", color_arr)
    cv2.waitKey(0)

    out_array = colormap_array(ds_1, ds_2, color_arr, defined_classification__1_list, defined_classification__2_list)
    # write array with reference by raster_1
    ref_geotrans = ds_1.GetGeoTransform()
    ref_srs = ds_1.GetProjection()
    del ds_1
    del ds_2
    output_path = r"C:\Users\PZH\Desktop\drawing\MEM\output0716\output_map_2007.tif"
    raster_write(output_path, out_array, projection=ref_srs,
                 geo_transform=ref_geotrans, data_type=gdal.GDT_UInt16)
