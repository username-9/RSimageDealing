import math
import os
from typing import Generator, Callable

import numpy as np
import psutil
from osgeo import gdal

from UtilitiesForDealingImage.ReadMain import read_band_scale_offset
from UtilitiesForDealingImage.WriteMain import set_band_scale_offset


def memory_usage():
    """
    calculate available RAM and process RAM 计算可用内存
    :return: available RAM and process RAM 计算进程内存
    """
    mem_available = psutil.virtual_memory().available >> 20  # 可用内存
    mem_process = psutil.Process(os.getpid()).memory_info().rss >> 20  # 进程内存
    return mem_process, mem_available


def pre_cal_for_block(width, height, bands):
    """
    calculate the number of block with the available ram
    :param width: image width
    :param height: image height
    :param bands: bands of image
    :return: the number of block, block height and the rest of height given the available ram and process ram
    """
    # 计算分块数据
    # return: 分块个数，每块行数，剩余行数
    p, a = memory_usage()
    bl = (a - 2000) / (width * height * bands >> 20)
    if bl > 3:
        block_num = 1
    else:
        block_num = math.ceil(bl) + 4

    bl_height = int(height / block_num)
    mod_height = height % block_num

    return block_num, bl_height, mod_height


class ImageBlock:
    def __init__(self, image_file_path: str, block_x_size: int, block_y_size: int):
        """
        initialize function
        :param image_file_path: image file path
        :param block_x_size: --> block x size
        :param block_y_size: // block y size
        """
        self.block_array = None
        self.block_x_size = block_x_size
        self.block_y_size = block_y_size
        self.block_region: list = []
        self.proj = None
        self.image: str = image_file_path
        self.geo_transform = None
        self.ds = gdal.Open(self.image, gdal.GA_ReadOnly)
        self.image_width = self.ds.RasterXSize
        self.image_height = self.ds.RasterYSize
        self.image_bands = self.ds.RasterCount
        self.geo_transform = self.ds.GetGeoTransform()
        self.proj = self.ds.GetProjection()
        scale, offset = read_band_scale_offset(self.ds)
        self.scale = scale
        self.offset = offset
        self.all_num: int = 1
        self.block_num_x: int = 1
        self.block_num_y: int = 1
        self.remain_x: int = 0
        self.remain_y: int = 0
        del self.ds
        if block_x_size > self.image_width or block_y_size > self.image_height:
            if block_x_size > self.image_width and block_y_size < self.image_height:
                raise ValueError("x-size needs to be smaller than image height")
            if block_x_size < self.image_width and block_y_size > self.image_height:
                raise ValueError("y-size needs to be smaller than image width")
            raise ValueError("Block-size needs to be smaller than image")
        else:
            self.block_num_x = int(self.image_width / block_x_size)
            self.block_num_y = int(self.image_height / block_y_size)
            self.remaining_x = self.image_width - self.block_num_x * block_x_size
            self.remaining_y = self.image_height - self.block_num_y * block_y_size
            self.all_num = self.block_num_x * self.block_num_y
            if self.remaining_x != 0:
                self.all_num += self.block_num_y
                if self.remaining_y != 0:
                    self.all_num += self.block_num_x + 1

    def read_by_block_given_ram(self, function: Callable) -> list:
        """
        given blocking by height (without the width)
        :return: block array
        """
        # num of block, line num of block, the rest of line num of block
        bl_size, bl_each, bl_mod = pre_cal_for_block(self.image_width, self.image_height, self.image_bands)
        # get the origin location and number of line of block 提取分块区域位置(起点,行数)
        self.block_region = [(bs * bl_each, 0, bl_each, self.image_width) for bs in range(bl_size)]
        if bl_mod != 0:
            self.block_region.append((bl_size * bl_each, 0, bl_mod, self.image_width))
        if function is not None:
            self.ds = gdal.Open(self.image, gdal.GA_ReadOnly)
            # apply the function in block 分块计算
            for x_pos, y_pos, x_size, y_size in self.block_region:
                print(f'start height pos:{x_pos}, end height pos:{x_pos + x_size - 1}')
                self.block_array = self.ds.ReadAsArray(0, x_pos, self.image_width, x_size)
                function(self.block_array)
            del self.ds
        return self.block_region

    def get_blocks_region(self, function: Callable[[np.ndarray], None] = None) -> list:
        """
        read raster by specified size
        :param function: function using for goal calculation (option)
        :return: a list of block information (origin point x, origin point y, x-size, y-size)
        """
        # get the number and remain of the blocks
        block_x_size = self.block_x_size
        block_y_size = self.block_y_size
        block_num_x = self.block_num_x
        block_num_y = self.block_num_y
        remaining_x = self.remaining_x
        remaining_y = self.remaining_y
        self.block_region = [(i * block_x_size, j * block_y_size, block_x_size, block_y_size)
                             for j in range(block_num_y)
                             for i in range(block_num_x)]
        if remaining_y != 0:
            for i in range(block_num_x):
                self.block_region.append(
                    (i * block_x_size, block_num_y * block_y_size, block_x_size, remaining_y))
            if remaining_x != 0:
                for i in range(block_num_y):
                    self.block_region.append(
                        (block_num_x * block_x_size, i * block_y_size, remaining_x, block_y_size))
                self.block_region.append(
                    (block_num_x * block_x_size, block_num_y * block_y_size, remaining_x, remaining_y))
                if function is not None:
                    self.ds = gdal.Open(self.image, gdal.GA_ReadOnly)
                    for x_pos, y_pos, x_size, y_size in self.block_region:
                        try:
                            print(
                                f'the block region is x = {x_pos}, y = {y_pos}, the size is x = {x_size}, y = {y_size}')
                            self.block_array = self.ds.ReadAsArray(x_pos, y_pos, x_size, y_size)
                            function(self.block_array)
                        except Exception as e:
                            print(f"{e}\nSomething error happened in reading")
                    del self.ds
        return self.block_region

    def read_by_generator(self) -> Generator:
        """
        read by a generator which can save the RAM
        :return: a generator about block location and size
        """
        block_x_size = self.block_x_size
        block_y_size = self.block_y_size
        block_num_x = self.block_num_x
        block_num_y = self.block_num_y
        remaining_x = self.remaining_x
        remaining_y = self.remaining_y
        self.ds = gdal.Open(self.image, gdal.GA_ReadOnly)
        for i in range(block_num_y):
            for j in range(block_num_x):
                self.block_array = self.ds.ReadAsArray(j * block_x_size, i * block_y_size, block_x_size, block_y_size)
                yield self.block_array, j * block_x_size, i * block_y_size, block_x_size, block_y_size
        if remaining_y != 0:
            for i in range(block_num_x):
                self.block_array = self.ds.ReadAsArray(i * block_x_size, block_num_y * block_y_size, block_x_size,
                                                       remaining_y)
                yield self.block_array, i * block_x_size, block_num_y * block_y_size, block_x_size, remaining_y
            if remaining_x != 0:
                for i in range(block_num_y):
                    self.block_array = self.ds.ReadAsArray(block_num_x * block_x_size, i * block_y_size, remaining_x,
                                                           block_y_size)
                    yield self.block_array, block_num_x * block_x_size, i * block_y_size, remaining_x, block_y_size
                    self.block_array = self.ds.ReadAsArray(block_num_x * block_x_size,
                                                           block_num_y * block_y_size, remaining_x, remaining_y)
                    yield (self.block_array, block_num_x * block_x_size,
                           block_num_y * block_y_size, remaining_x, remaining_y)
        del self.ds

    def write_by_block(self, output_file_path, arr: np.ndarray, x_pos, y_pos, write_file_type="GTiff",
                       write_data_type=None):
        """
        write raster by specified size
        :param output_file_path: output file path
        :param arr: array
        :param x_pos:
        :param y_pos:
        :param write_file_type:
        :param write_data_type:
        :return:
        """
        driver = gdal.GetDriverByName(write_file_type)
        if os.path.exists(output_file_path):
            out_ds = gdal.Open(output_file_path, gdal.GA_Update)
        else:
            if write_data_type is None:
                out_ds: gdal.Dataset = driver.Create(output_file_path, self.image_width,
                                                     self.image_height, bands=arr.shape[0])
            else:
                out_ds: gdal.Dataset = driver.Create(output_file_path, self.image_width,
                                                     self.image_height, eType=write_data_type, bands=arr.shape[0])
            out_ds.SetGeoTransform(self.geo_transform)
            out_ds.SetProjection(self.proj)
            set_band_scale_offset(out_ds, self.scale, self.offset)
        out_ds.WriteArray(arr, x_pos, y_pos)
        out_ds.FlushCache()
        del out_ds
        return "write done"