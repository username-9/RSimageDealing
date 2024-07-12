import os
import typing

from osgeo import gdal, gdalconst

from UtilitiesForDealingImage.ReadMain import raster_read, read_band_scale_offset
from UtilitiesForDealingImage.WriteMain import raster_write


def shape_warp_for_raster(raster: str, input_shape: str, out_raster,
                          open_type: str = gdal.GA_ReadOnly, srs="EPSG:4326", cropToCutline: bool = False) -> None:
    """
    To clip raster with a specific shape
    :param cropToCutline: whether keep the size of the input raster
    :param srs: spatial reference system (default EPSG:4326)
    :param raster: file path of raster to be clipped
    :param input_shape: file path of the specific shape
    :param out_raster: path with file name of output raster
    :param open_type: gdal dataset open type
    :return: None
    """
    src = raster_read(raster, open_type)
    try:
        gdal.Warp(out_raster, src,
                  format="GTiff",
                  cutlineDSName=input_shape,
                  cropToCutline=cropToCutline,
                  dstSRS=srs,
                  dstNodata=0)
    except Exception as e:
        print(f"{e}\nSomething wrong in the wrapping")
    finally:
        del src


def image_mosaic(input_file_path: list[str], output_file_path: str) -> None:
    """
    Mosaic a list of image through the method gdal build vrt which builds a virtual raster
    and here we write it in a real tiff
    :param input_file_path: input file path
    :param output_file_path: output file path
    :return: None
    """
    try:
        vrt = os.path.join(os.path.split(output_file_path)[0], "vrt.tif")
        gdal.BuildVRT(vrt,
                      input_file_path,
                      hideNodata=True)
        vrt_ds = raster_read(vrt)
        scale, offset = read_band_scale_offset(vrt_ds)
        geo_info = vrt_ds.GetGeoTransform()
        proj = vrt_ds.GetProjection()
        if vrt_ds.RasterCount == 1:
            data_type = vrt_ds.GetRasterBand(1).DataType
        else:
            data_type = vrt_ds.GetRasterBand(1).DataType
        vrt_array = vrt_ds.ReadAsArray(buf_type=gdalconst.GDT_Float32)
        raster_write(output_file_path, vrt_array, proj, geo_info,
                     data_type=gdalconst.GDT_Float32, scale=scale, offset=offset)
        # gdal.Translate(vrt, output_file_path, format=output_format)
        os.remove(vrt)
        del vrt, vrt_ds
    except Exception as e:
        print(f"{e}\nSome error in reading image")


def set_nodata(dataset: gdal.Dataset, nodata: int) -> None:
    """
    set nodata for a specific int value in a gdal dataset
    :param dataset: goal gdal dataset
    :param nodata: the specific int value being seen as nodata
    :return: None
    """
    if not isinstance(dataset, gdal.Dataset):
        raise ValueError("dataset must be a GDAL dataset")

    if not isinstance(nodata, int):
        raise ValueError("nodata must be an integer")

    for i in range(dataset.RasterCount):
        band = dataset.GetRasterBand(i + 1)  # GDAL 索引从 1 开始
        try:
            band.SetNoDataValue(nodata)
            print(f"set band {i + 1}  {nodata} as nodata")
        except Exception as e:
            print(f"can not set {nodata} as nodata for {i + 1} ：{e}")


def reproject_image(input_ds: gdal.Dataset, width, height, bands: list = None, datatype=gdalconst.GDT_Float32,
                    reference_projection: str = None, reproject_method: str = gdalconst.GRA_Bilinear) \
        -> gdal.Dataset or typing.Generator:
    input_proj = input_ds.GetProjection()
    driver = gdal.GetDriverByName('GTiff')
    temp_path = r"..\temp.tif"
    if bands is None:
        n_bands = input_ds.RasterCount
        output_ds = driver.Create(temp_path, width, height, n_bands, etype=datatype)
        gdal.ReprojectImage(input_ds, output_ds, input_proj, reference_projection, reproject_method)
        os.remove(temp_path)
        return output_ds
    else:
        n_bands = bands
        output_ds = driver.Create(temp_path, width, height, 1, etype=datatype)
        for i in n_bands:
            input_band = input_ds.GetRasterBand(i + 1)
            gdal.ReprojectImage(input_band, output_ds, input_proj, reference_projection, reproject_method)
            yield output_ds


if __name__ == '__main__':
    # pass
    # # hdf to tiff
    # os.chdir(r"C:\Users\PZH\Desktop\MODIS-NPP-2001-2024")
    # file_list = os.listdir()
    # output_dir = r"..\output_GPP_tif"
    # if os.path.exists(output_dir):
    #     pass
    # else:
    #     os.mkdir(output_dir)
    # # transform to tiff
    # for file in file_list:
    #     if file.endswith(".hdf"):
    #         hdf_to_tiff(file, output_dir, 0, data_type=gdalconst.GDT_Float32)

    # # mosaic
    # os.chdir(r"C:\Users\PZH\Desktop\output_tif")
    # file_list = os.listdir()
    # if os.path.exists(r"..\output_tif"):
    #     pass
    # else:
    #     os.mkdir(r"..\output_tif")
    # for file in file_list:
    #     if file.endswith(".tif") is not True:
    #         file_list.remove(file)
    # for i in range(0, int(len(file_list)), 4):
    #     if file_list[i].endswith(".tif"):
    #         deal_list = file_list[i:i + 4]
    #         output_filepath = os.path.join("..\\output", f"{file_list[i][12:16]}.tif")
    #         image_mosaic(deal_list, output_filepath)

    # clip the image
    # os.chdir("C:\\Users\\PZH\\Desktop\\output\\")
    # file_list = os.listdir()
    # if os.path.exists(r"..\output_Clip"):
    #     pass
    # else:
    #     os.mkdir(r"..\output_Clip")
    # for file in file_list:
    #     if file.endswith(".tif") is not True:
    #         file_list.remove(file)
    # shape_file = r"C:\Users\PZH\Desktop\BTH\mask_Dissolve_Dissolve.shp"
    # for file in file_list:
    #     output_file = os.path.join(r"..\output_Clip", file)
    #     shape_warp_for_raster(file, shape_file, output_file)

    # set nodata
    # os.chdir(r"C:\Users\PZH\Desktop\江苏项目\数据处理\area_out")
    # file_list = os.listdir()
    # for file in file_list:
    #     if not file.endswith(".tif"):
    #         file_list.remove(file)
    # for file in file_list:
    #     ds = gdal.Open(file, gdal.GA_Update)
    #     set_nodata(ds, -9999)
    ds = gdal.Open(r"C:\Users\PZH\Desktop\REF\clip_output.tif", gdal.GA_Update)
    set_nodata(ds, 0)
