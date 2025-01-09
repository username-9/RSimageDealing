from osgeo import gdal
from tqdm import tqdm

from UtilitiesForProcessingImage.BasicUtility.ReadMain import read_band_scale_offset, get_raster_nodata


def raster_average(ds: gdal.Dataset, band: list = None):
    """
    calculate the average pixel value for a raster
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
        _count = 0
        sum_carbon = 0
        for j in tqdm(range(ds_arr.shape[0])):
            for k in range(ds_arr.shape[1]):
                x = ds_arr[j, k]
                if x > 0:
                    _count += 1
                    sum_carbon += x
        print(f"计数：{_count}\n求和：{sum_carbon}\n均值：{sum_carbon / _count}")
    else:
        for i in band:
            _count = 0
            sum_carbon = 0
            for j in tqdm(range(ds_arr.shape[0])):
                for k in range(ds_arr.shape[1]):
                    x = ds_arr[i, j, k]
                    if x > 0:
                        _count += 1
                        sum_carbon += x
            print(f"波段：{i}\n计数：{_count}\n求和：{sum_carbon}\n均值：{sum_carbon / _count}")


def value_count(ds: gdal.Dataset, value_range:list or tuple, range_or_single: bool = True) -> dict:
    """
    statistic value for raster dataset
    :param range_or_single: count for range or disperse values, true is continuous value
    :param ds: dataset of the raster
    :param value_range: split or range of the series to count(True is range)
    :return: a dict with statistic result
    """
    if type(value_range) not in {"list", "tuple"}:
        raise ValueError("value_range must be list or tuple")
    # read raster array
    ds_arr = ds.ReadAsArray()
    # construct result dict
    re_dict = {}
    if range_or_single:
        for i in range(len(value_range)):
            if i == 0:
                ds_count = len(ds_arr[ds_arr<value_range[i]])
                re_dict[f"(,{value_range[i]})"] = ds_count
            elif i == len(value_range) - 1:
                ds_count = len(ds_arr[ds_arr>=value_range[i]])
                re_dict[f"[{value_range[i]}, )"] = ds_count
            else:
                ds_count = len(ds_arr[value_range[i]<=ds_arr<value_range[i+1]])
                re_dict[f"[{value_range[i]}, {value_range[i+1]})"] = ds_count
    else:
        for i in value_range:
            ds_count = len(ds_arr[value_range[i]==ds_arr])
            re_dict[f"{value_range[i]}"] = ds_count
    return re_dict
