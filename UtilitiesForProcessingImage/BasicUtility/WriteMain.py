import os

import numpy as np
from osgeo import gdal, gdalconst, ogr

from UtilitiesForProcessingImage.BasicUtility.ReadMain import raster_read


def array_to_raster(array: np.ndarray,
                    out_raster_path: str,
                    geo_transform: list,
                    projection=None,
                    file_type: str = "GTiff",
                    data_type: gdalconst = gdalconst.GDT_Float32,
                    scale: list = None,
                    offset: list = None) -> None:
    """
    :param data_type:
    :param scale:
    :param offset:
    :param array:image array
    :param out_raster_path:output raster path
    :param geo_transform:geograph referencing transform
    :param projection:geographic referencing projection
    :param file_type:raster file type
    :param data_type:raster data type
    :param scale: metadata scale
    :param offset: metadata offset
    """
    try:
        driver = gdal.GetDriverByName(file_type)
        if array.ndim == 2:
            band_num = 1
            x_size = array.shape[1]
            y_size = array.shape[0]
        else:
            band_num = array.shape[0]
            x_size = array.shape[2]
            y_size = array.shape[1]
        out_data = driver.Create(out_raster_path, xsize=x_size, ysize=y_size, bands=band_num, eType=data_type)
        out_data.WriteArray(array)
        out_data.FlushCache()
        del out_data
        render_geo = gdal.Open(out_raster_path, gdal.GA_Update)
        set_band_scale_offset(render_geo, scale, offset)
        render_geo.SetGeoTransform(geo_transform)
        render_geo.SetProjection(projection)
        render_geo.FlushCache()
        del render_geo
    except Exception as e:
        raise f"{e}\nSome error in transforming image" from e


def raster_write(file_path, image_array, projection, geo_transform,
                 file_type="GTiff", data_type=None, scale=None, offset=None) -> None:
    """
    write raster using an array
    :param file_path: output raster path
    :param image_array: array to be written
    :param projection: projection reference to be set
    :param geo_transform: geographic referencing transform to be set
    :param file_type: output raster file type
    :param data_type: output raster data type
    :param scale: scale reference to be set
    :param offset: offset reference to be set
    :return: None
    """
    if data_type is not None:
        array_to_raster(image_array, file_path, geo_transform, projection,
                        file_type, data_type=data_type, scale=scale, offset=offset)
    else:
        try:
            array_to_raster(image_array, file_path, geo_transform, projection, file_type,
                            scale=scale, offset=offset)
        except Exception as e:
            print(f"{e}\nMay be no Data_type, please set data_type argument")
    print("write done")


def vector_write():
    pass


def set_band_scale_offset(ds: gdal.Dataset, scale: list = None, offset: list = None, bands: list = None) -> None:
    """
    set scale and offset for gdal.Dataset
    :param ds: gdal dataset
    :param scale: scale reference to be set
    :param offset: offset reference to be set
    :param bands: which bands to be set
    :return: None
    """
    if scale is not None:
        if ds.RasterCount != len(scale):
            scale = [scale[0] for i in range(ds.RasterCount)]
    if offset is not None:
        if ds.RasterCount != len(offset):
            offset = [offset[0] for i in range(ds.RasterCount)]
    if bands is None:
        for i in range(ds.RasterCount):
            band = ds.GetRasterBand(i + 1)
            if scale is not None:
                if scale[i] is not None:
                    band.SetScale(float(scale[i]))
            if offset is not None:
                if offset[i] is not None:
                    band.SetOffset(offset[i])
            del band
    else:
        for i in range(len(bands)):
            band = ds.GetRasterBand(bands[i])
            if scale is not None:
                if scale[i] is not None:
                    band.SetScale(float(scale[i]))
            if offset is not None:
                if offset[i] is not None:
                    band.SetOffset(offset[i])
            del band
    ds.FlushCache()
    print("set scale and offset done")


def save_data_source_to_file(data_source: ogr.DataSource, file_path: str, driver_name: str = 'ESRI Shapefile'):
    # get driver
    driver = ogr.GetDriverByName(driver_name)

    # delete file if it has existed (maybe wrong in processing for it is using)
    if driver.TestCapability(ogr.ODrCDeleteDataSource):
        if os.path.exists(file_path):
            driver.DeleteDataSource(file_path)

    # create new datasource
    new_data_source = driver.CreateDataSource(file_path)

    # get layer from o-datasource
    layer = data_source.GetLayer()
    layer_defn = layer.GetLayerDefn()

    # create new layer in new datasource
    new_layer = new_data_source.CreateLayer(layer.GetName(), layer.GetSpatialRef(), layer.GetGeomType())

    # copy the definition of field
    for i in range(layer_defn.GetFieldCount()):
        field_defn = layer_defn.GetFieldDefn(i)
        new_layer.CreateField(field_defn)

    # copy feature
    feature = layer.GetNextFeature()
    while feature:
        new_feature = ogr.Feature(new_layer.GetLayerDefn())

        # copy geometry
        geom = feature.GetGeometryRef()
        if geom:
            new_geom = geom.Clone()
            new_feature.SetGeometry(new_geom)

        # copy attributions
        for i in range(feature.GetFieldCount()):
            new_feature.SetField(feature.GetFieldDefnRef(i).GetNameRef(), feature.GetFieldAsString(i))

        # add new feature to new layer
        new_layer.CreateFeature(new_feature)

        # clear
        new_feature = None
        feature = layer.GetNextFeature()

    # clear
    new_data_source = None
    data_source = None


if __name__ == "__main__":
    _file_type = "GTiff"
    _file_path = r"C:\Users\Administrator\Downloads\write_prac.TIF"
    test_1 = raster_read(r"C:\Users\Administrator\Downloads\MYDLT1F.20140601.CN.LTN.MAX.V2.TIF")
    _projection = test_1.GetProjection()
    _geo_transform = test_1.GetGeoTransform()
    test_array = test_1.ReadAsArray()
    raster_write(_file_path, test_array, _projection, _geo_transform, _file_type)
    test_1 = raster_read(_file_path)
    del test_1
