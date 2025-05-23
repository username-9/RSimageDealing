"""
File format transformation
1 HDF to TIFF
2 NC to TIFF
3 Separate multi-band raster to single band raster
4 Transform coordination for datasource
"""

import os

import numpy as np
from osgeo import gdal, osr
import netCDF4 as nc
from tqdm import tqdm

from UtilitiesForProcessingImage.BasicUtility.ReadMain import hdf_read, read_band_scale_offset
from UtilitiesForProcessingImage.BasicUtility.WriteMain import array_to_raster
from UtilitiesForProcessingImage.BasicUtility.ImageProcessing import set_nodata


def hdf_to_tiff(input_file_path: str, output_file_dir: str,
                sub_datasets_num: int, data_type, hdf_no_value_data=None, tif_no_value_data=None) -> None:
    """
    transform the hdf file to tiff file in a list of batch
    :param tif_no_value_data: set no value data for tiff file
    :param hdf_no_value_data: hdf file no value data
    :param input_file_path: hdf file path
    :param output_file_dir: output tiff file path
    :param sub_datasets_num: the index of sub-dataset in dataset
    :param data_type: the data type which is using when writing the array to tiff file
    :return: None
    """
    hdf_layer = hdf_read(input_file_path)
    if type(hdf_layer) != list:
        sub_data = hdf_layer
    else:
        sub_data = gdal.Open(hdf_layer[sub_datasets_num][0])

    geo_transform = sub_data.GetGeoTransform()
    print(f"geograph transform information: {geo_transform}")
    projection = sub_data.GetProjection()
    print(f"geographic referencing projection: {projection}")
    try:
        scale, offset = read_band_scale_offset(sub_data)
        array = sub_data.ReadAsArray(buf_type=data_type)
        output_file_path = os.path.join(output_file_dir, f"{input_file_path[:-3]}_layer_{sub_datasets_num + 1}.tif")
        if hdf_no_value_data is not None:
            if tif_no_value_data is None:
                array[array > hdf_no_value_data] = 0
            else:
                array[array == hdf_no_value_data] = tif_no_value_data
        array_to_raster(array, output_file_path, geo_transform,
                        projection, data_type=data_type, scale=scale, offset=offset)
        print("transform done")
    except ValueError as e:
        print(f"Error reading band scale offset: {e}")
    finally:
        del sub_data, hdf_layer


def nc_to_tiff(input_file_path: str, output_file_dir: str,
               output_variable: str, datatype: gdal.gdalconst,
               output_srs=None, into_one: bool = True,
               scale: list = None, offset: list = None,
               scale_all: float = 1, nc_datatype=int,
               reference_geotrans=None, nodata=None) -> None:
    """
    Transform nc format to the tif format
    :param nodata: (optional) set nodata
    :param reference_geotrans: (optional) set a geograph transformation by reference
    :param nc_datatype: the datatype in nc datatype
    :param input_file_path: .nc file path
    :param output_file_dir: directory in where put output files
    :param output_variable: which variable of nc needs to be extracted
    :param datatype: the datatype of output tif image
    :param output_srs: the SRS(spatial reference system) in which WGS 84 (EPSG 4326) is default
    :param into_one: whether put all bands into one tif image
    :param scale:  a list contained scales of all bands
    :param offset: a list contained offsets of all bands
    :param scale_all: if you want to set the same scale to all bands ,put a single number in
    :return: None
    """
    nc_data = nc.Dataset(input_file_path)
    dimensions = nc_data.dimensions
    lon_dim = None
    lat_dim = None
    for key in dimensions.keys():
        if key == "longitude":
            lon_dim = key
        elif key == "latitude":
            lat_dim = key
        elif key == "lon":
            lon_dim = key
        elif key == "lat":
            lat_dim = key
    lon = nc_data.variables[lon_dim][:]
    lat = nc_data.variables[lat_dim][:]
    nc_arr = np.array(nc_data.variables[output_variable]).astype(nc_datatype)
    # check the order of data
    if lat[0] < lat[-1]:
        nc_arr = nc_arr[:, :, -1]
        print("fix latitude order")
    # nc_arr = nc_arr * 0.1
    # img location
    geo_trans = None
    if reference_geotrans is not None:
        geo_trans = reference_geotrans
    else:
        lon_min, lon_max, lat_min, lat_max = lon.min(), lon.max(), lat.min(), lat.max()
        # calculate spatial resolution
        lon_resolution = (lon_max - lon_min) / (len(lon) - 1)
        lat_resolution = (lat_max - lat_min) / (len(lat) - 1)
        # set geology transform
        geo_trans = [lon_min, lon_resolution, 0, lat_max, 0, -lat_resolution]
    # set SRS
    srs = osr.SpatialReference()
    # WGS 84 coordination system
    srs.ImportFromEPSG(4326)
    if output_srs is None:
        output_srs = srs.ExportToWkt()
    # set scale and offset
    # if scale is None:
    #     scale = [1 for i in range(nc_arr.shape[0])]
    if scale_all is not None:
        scale = [scale_all for i in range(nc_arr.shape[0])]
    # if offset is None:
    #     offset = [0 for i in range(nc_arr.shape[0])]
    # put all bands in a whole tif or divide them
    if into_one:
        output_path = os.path.join(output_file_dir, f"{input_file_path[:-3]}_{output_variable}.tif")
        array_to_raster(nc_arr, output_path, geo_trans, output_srs, data_type=datatype,
                        scale=scale, offset=offset)
    else:
        for i in range(nc_arr.shape[0]):
            arr = nc_arr[i, :, :]
            output_path = os.path.join(output_file_dir, f"{input_file_path[:-3]}_{output_variable}"
                                       + str(i + 1).zfill(3) + ".tif")
            if scale is not None and offset is not None:
                array_to_raster(arr, output_path, geo_trans, output_srs, data_type=datatype, scale=[scale[i]],
                                offset=[offset[i]])
            elif scale is None and offset is not None:
                array_to_raster(arr, output_path, geo_trans, output_srs, data_type=datatype, offset=[offset[i]])
            elif offset is None and scale is not None:
                array_to_raster(arr, output_path, geo_trans, output_srs, data_type=datatype, scale=[scale[i]])
            else:
                array_to_raster(arr, output_path, geo_trans, output_srs, data_type=datatype)
            if nodata is not None:
                ds = gdal.Open(output_path, gdal.GA_Update)
                set_nodata(ds, nodata)
                del ds


def multiply_bands_to_band_raster(ds: gdal.Dataset, output_file_dir: str, axis = 0):
    arr = ds.GetRasterBand(1).ReadAsArray()
    ds_trans = ds.GetGeoTransform()
    ds_proj = ds.GetProjection()
    ds_width = ds.RasterXSize
    ds_height = ds.RasterYSize
    ds_datatype = ds.GetRasterBand(1).DataType
    for i in tqdm(range(arr.shape[axis])):
        out_path = os.path.join(output_file_dir, f"Band{i+1}.tif")
        driver = gdal.GetDriverByName('GTiff')
        band_ds: gdal.Dataset = driver.Create(out_path, ds_width, ds_height, bands=1,
                                               eType=ds_datatype)
        band_ds.SetGeoTransform(ds_trans)
        band_ds.SetProjection(ds_proj)
        band_array = None
        if axis == 0:
            band_array = arr[i, :, :]
        else:
            raise ValueError
        band_ds.WriteArray(band_array)
        band_ds.FlushCache()
        del band_ds


def coordination_transform(ds_path: str, target_wkt: str = None, target_proj4: str = None,
                           out_tif_path: str = 'temp.tif', resample_algorithm: int = gdal.GRA_Bilinear,
                           x_res = None, y_res = None, to_ds:bool = False):
    # set target projection
    target_srs = osr.SpatialReference()
    if target_wkt is not None:
        target_srs.ImportFromWkt(target_wkt)
    elif target_proj4 is not None:
        target_srs.ImportFromProj4(target_proj4)
    else:
        raise ValueError("No target projection defined.")

    # processing
    gdal.Warp(out_tif_path, ds_path, options=gdal.WarpOptions(dstSRS=target_srs,
                                                              format='GTiff',
                                                              xRes=x_res,
                                                              yRes=y_res,
                                                              resampleAlg=resample_algorithm))

    # clear
    if to_ds:
        dst_ds = gdal.Open(out_tif_path)
        return dst_ds


