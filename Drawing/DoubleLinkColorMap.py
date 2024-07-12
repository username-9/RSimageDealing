import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import hsv_to_rgb
import cartopy.crs as ccrs
import cv2
from osgeo import gdal
from tqdm import tqdm

from UtilitiesForDealingImage.ReadMain import read_band_scale_offset, raster_read
from UtilitiesForDealingImage.WriteMain import raster_write


def double_link_color_map(map_x_data: np.ndarray, map_y_data: np.ndarray, two_dim_color_arr: np.ndarray,
                          resize: bool = False, block_position: tuple = (0.1, 0.1, 1, 1)):
    """
    draw maps with double link color map
    :param two_dim_color_arr: color block used for legend
    :param block_position: color legend position
    :param resize: whether to resize the factor map data
    :param map_x_data: one of the factor in mapping (should be 2-dimensional array)
    :param map_y_data: another factor in mapping (should be 2-dimensional array)
    :param resize: resize the data by map_x_data
    :return: a matplotlib color map
    """
    if resize:
        map_y_data.resize(map_x_data.shape)
    if map_x_data.shape == map_y_data.shape:
        rows, cols, colors = two_dim_color_arr.shape
        fig: plt.Figure = plt.figure(figsize=(rows, cols))
        # draw main picture
        ax_main = fig.add_subplot(projection=ccrs.Mollweide())
        # ax_main.stock_img()
        # ax_main.coastlines()
        # draw legend picture
        ax_legend = fig.add_axes(
            (block_position[0], block_position[1], rows * block_position[2], cols * block_position[3]))
        # ax_legend.imshow(two_dim_color_arr, cmap='viridis')
        fig.show()
    else:
        raise ValueError("the size of data is not equal")


def construct_arr(range_1: list, range_2: list, color_num) -> tuple[np.ndarray, np.ndarray]:
    x_v_arr = np.linspace(start=range_1[0], stop=range_1[1], num=color_num)
    x_v_arr = np.tile(x_v_arr, (color_num, 1))
    y_v_arr = np.linspace(range_2[0], range_2[1], num=color_num)
    y_v_arr = np.tile(y_v_arr, (color_num, 1))
    y_v_arr = y_v_arr.T.copy()
    y_v_arr = np.flip(y_v_arr, axis=0).copy()
    return x_v_arr, y_v_arr


def two_dimensional_color_map(x_Hue: int, y_Hue: int,
                              x_Saturability: list[int], y_Saturability: list[int],
                              color_num: int = 5, value: int = 255, color_block_size: int = 1
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
    :param value: the value of color (0~255)
    :param color_block_size: the size of each block of color
    :return: a 2-dimensional color map
    """
    # construct Hue array
    x_Hue_arr = x_Hue * np.ones((color_num, color_num))
    y_Hue_arr = y_Hue * np.ones((color_num, color_num))
    # construct Saturability array
    x_S_arr, y_S_arr = construct_arr(x_Saturability, y_Saturability, color_num)
    # x_S_arr = np.linspace(start=x_Saturability[0], stop=x_Saturability[1], num=color_num)
    # x_S_arr = np.tile(x_S_arr, (color_num, 1))
    # y_S_arr = np.linspace(y_Saturability[0], y_Saturability[1], num=color_num)
    # y_S_arr = np.tile(y_S_arr, (color_num, 1))
    # y_S_arr = y_S_arr.T.copy()
    # y_S_arr = np.flip(y_S_arr, axis=0).copy()
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


def colormap_array(dataset_1: gdal.Dataset, dataset_2: gdal.Dataset, color_array: np.ndarray) -> np.ndarray:
    """
    output an array with three bands with linking color map array
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
    factor_1_norm = (factor_1_arr - factor_1_min) / (factor_1_max - factor_1_min)
    factor_2_norm = (factor_2_arr - factor_2_min) / (factor_2_max - factor_2_min)
    out_arr = np.zeros((3, factor_1_norm.shape[0], factor_1_norm.shape[1]), dtype=np.uint8)
    for i in tqdm(range(factor_1_norm.shape[0])):
        for j in range(factor_1_norm.shape[1]):
            x_loc = int(factor_1_norm[i, j] * color_array.shape[1] - 1)
            y_loc = int(factor_2_norm[i, j] * color_array.shape[0]) - 1
            out_arr[::-1, i, j] = color_array[y_loc, x_loc, :]
    return out_arr


def add_grid(img_arr, color_num: int, origin_location: tuple = (0, 0)):
    x_block_size = int(img_arr.shape[1] / color_num)
    y_block_size = int(img_arr.shape[0] / color_num)
    # draw row lines
    for i in range(1, int((img_arr.shape[0]) / (img_arr.shape[0] / color_num) + 1)):
        cv2.line(color_arr, (origin_location[0], i * x_block_size), (img_arr.shape[1], i * x_block_size),
                 (250, 250, 250), 1)
    for i in range(1, int((img_arr.shape[1]) / (img_arr.shape[1] / color_num) + 1)):
        cv2.line(color_arr, (i * y_block_size, origin_location[1]), (i * y_block_size, img_arr.shape[0]),
                 (250, 250, 250), 1)


if __name__ == "__main__":
    # read rasters
    # raster_1 = r"D:\Data\VegetationResilienceDealing\Integrate_Output\GPP\GPP_BTH_CLIP\200003.tif"
    # raster_2 = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LAI\LAI_BTH_CLIP\200003.tif"
    # ds_1 = raster_read(raster_1)
    # ds_2 = raster_read(raster_2)
    # get two-dim color map array
    # color_arr = two_dimensional_color_map(90, 120, [30, 240],
    #                                       [30, 240], color_num=10, color_block_size=30)
    color_arr = two_dimensional_color_map(60, 127, [70, 255],
                                          [70, 255],  x_v=[200, 150], y_v=[200, 150],
                                          color_num=10, color_block_size=30, output_size=(1000, 1000))
    # color_arr = two_dimensional_color_map(50, 155, [0, 255],
    #                                       [0, 255],
    #                                       color_num=10, color_block_size=30)
    color_map_path = r"C:\Users\PZH\Desktop\REF\color_map_1.png"
    # add grid for color map
    add_grid(color_arr, 10)
    cv2.imwrite(color_map_path, color_arr)
    cv2.imshow("img", color_arr)
    cv2.waitKey(0)
    # # get the map with color link
    # out_array = colormap_array(ds_1, ds_2, color_arr)
    # # write array with reference by raster_1
    # ref_geotrans = ds_1.GetGeoTransform()
    # ref_srs = ds_1.GetProjection()
    # del ds_1
    # del ds_2
    # output_path = r"C:\Users\PZH\Desktop\REF\output_map.tif"
    # raster_write(output_path, out_array, projection=ref_srs,
    #              geo_transform=ref_geotrans, data_type=gdal.GDT_UInt16)
