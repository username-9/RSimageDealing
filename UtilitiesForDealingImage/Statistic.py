from osgeo import gdal
from tqdm import tqdm

from UtilitiesForDealingImage.ReadMain import raster_read, read_band_scale_offset, get_raster_nodata


def raster_average(ds: gdal.Dataset, band: list = None):
    """
    calculate average pixel value of a raster
    :param ds: dataset
    :param band: band to average (optional)
    :return: None
    """
    if band is None:
        band = [0]
    ds_arr = ds.ReadAsArray()
    scale, _ = read_band_scale_offset(ds)
    print(f"scale is {scale}")
    nodata = get_raster_nodata(ds)
    if len(band) == 1 and band[0] == 0:
        count = 0
        sum_carbon = 0
        for j in tqdm(range(ds_arr.shape[0])):
            for k in range(ds_arr.shape[1]):
                x = ds_arr[j, k]
                if x > 0:
                    count += 1
                    sum_carbon += x
        print(f"计数：{count}\n求和：{sum_carbon}\n均值：{sum_carbon / count}")
    else:
        for i in band:
            count = 0
            sum_carbon = 0
            for j in tqdm(range(ds_arr.shape[0])):
                for k in range(ds_arr.shape[1]):
                    x = ds_arr[i, j, k]
                    if x > 0:
                        count += 1
                        sum_carbon += x
            print(f"波段：{i}\n计数：{count}\n求和：{sum_carbon}\n均值：{sum_carbon / count}")
