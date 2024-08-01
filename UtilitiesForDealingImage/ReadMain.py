from osgeo import gdal, ogr


def raster_read(file_path: str, deal_type: str = gdal.GA_ReadOnly) -> gdal.Dataset:
    """
    read raster with more information ,also can use the origin method of gdal (gdal.Open())
    :param file_path: the raster file path
    :param deal_type: the type of how to read dataset(find in gdal manual)
    :return: gdal.Dataset
    """
    try:
        src = gdal.Open(file_path, deal_type)
        # read prac.
        rows = src.RasterYSize
        cols = src.RasterXSize
        bands = src.RasterCount
        print(f"[{file_path}]\nrows={rows}  column={cols}  bands={bands}")

        # get geo transform info.
        geo_info = src.GetGeoTransform()
        print(f"Geograph information(image to projection): {geo_info}")

        # get geo projection info.
        geo_proj = src.GetProjection()
        print(f"Projection information(projection to geo_coordination): {geo_proj}")

        # # get band information
        # fir_band = src.GetRasterBand(1)
        # the_max = fir_band.GetMaximum()
        # the_min = fir_band.GetMinimum()
        # print(fir_band, the_max, the_min)

        # read as array
        # fir_array = fir_band.ReadAsArray()
        # print(fir_array.shape)

        # show
        # mean = np.mean(fir_array)
        # std = np.std(fir_array)
        # plt.imshow(fir_array,
        #            vmin=mean - std * 2,
        #            vmax=mean + std * 2,
        #            cmap="gray")
        # plt.show()

        # mult_band show
        # ……
        return src
    except Exception as e:
        print(f"{e}\nmay be the driver cannot be used")


def vector_read(file_path: str, operate_type: int = 0, file_type: str = "ESRI Shapefile") -> gdal.ogr.DataSource:
    """
    read vector data
    :param operate_type: 
    :param file_path: vector file path
    :param file_type: type of vector file(default is ESRI Shapefile)
    :return: gdal.Dataset
    """
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
    gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")
    ogr.RegisterAll()
    driver = ogr.GetDriverByName(file_type)
    try:
        src = driver.Open(file_path, operate_type)
        return src
    except Exception as e:
        print(f"{e}\nmay be the driver cannot be used")


def hdf_read(file_path: str, deal_type: str = gdal.GA_ReadOnly) -> gdal.Dataset:
    """
    read HDF file
    :param file_path: the source file path
    :param deal_type: type of gdal.Open
    :return: gdal.Dataset
    """
    try:
        ds = gdal.Open(file_path, deal_type)
        sub_datasets = ds.GetSubDatasets()
        print('Number of sub-datasets: {}'.format(len(sub_datasets)))
        for sd in sub_datasets:
            print('Name: {0}\nDescription:{1}\n'.format(*sd))
        return sub_datasets
    except Exception as e:
        print(f"{e}\nSome wrongs happened in reading hdf")


def read_band_scale_offset(ds: gdal.Dataset, bands: list = None):
    """
    read scale and offset information of dataset
    :param ds: gdal dataset
    :param bands: bands which need to be read
    :return: None
    """
    scale = []
    offset = []
    if bands is None:
        try:
            for i in range(ds.RasterCount):
                ds_band = ds.GetRasterBand(i + 1)
                scale_1 = ds_band.GetScale()
                offset_1 = ds_band.GetOffset()
                scale.append(scale_1)
                offset.append(offset_1)
                del ds_band
            return scale, offset
        except Exception as e:
            print(f"{e}\ngetting all band information is wrong")
    else:
        try:
            for i in bands:
                ds_band = ds.GetRasterBand(i)
                scale_1 = ds_band.GetScale()
                offset_1 = ds_band.GetOffset()
                scale.append(scale_1)
                offset.append(offset_1)
                del ds_band
            return scale, offset
        except Exception as e:
            print(f"{e}\nSome wrongs happened in reading band information")


def get_raster_nodata(ds: gdal.Dataset, bands: list = None):
    nodata = []
    if bands is None:
        try:
            for i in range(ds.RasterCount):
                ds_band: gdal.Band = ds.GetRasterBand(i + 1)
                nodata = ds_band.GetNoDataValue()
                del ds_band
            return nodata
        except Exception as e:
            print(f"{e}\ngetting all band nodata information false")
    else:
        try:
            for i in bands:
                ds_band = ds.GetRasterBand(i)
                nodata = ds_band.GetNoDataValue()
                del ds_band
            return nodata
        except Exception as e:
            print(f"{e}\nSome wrongs happened in getting defined bands information")


if __name__ == '__main__':
    _src = raster_read(r"C:\Users\Administrator\Downloads\MYDLT1F.20140601.CN.LTN.MAX.V2.TIF")
    del _src
