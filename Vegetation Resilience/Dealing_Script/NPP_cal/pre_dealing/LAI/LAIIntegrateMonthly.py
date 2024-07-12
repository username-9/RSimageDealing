import os

import numpy as np
from osgeo import gdal, gdalconst

from UtilitiesForDealingImage.ReadMain import raster_read, read_band_scale_offset
from UtilitiesForDealingImage.UtilityFunction import month_of_day_in_year, start_and_end_day_of_month, integrate_monthly
from UtilitiesForDealingImage.WriteMain import raster_write

if __name__ == "__main__":
    work_path = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LAI\LAI_MOSAIC_OUTPUT"
    os.chdir(work_path)
    file_list = os.listdir()
    for file in file_list:
        if not file.endswith(".tif"):
            file_list.remove(file)
    file_index_dict, weight_index_dict = integrate_monthly(file_list, 0, 4,
                                                           4, 7)
    ds = raster_read(file_list[0])
    height = ds.RasterYSize
    width = ds.RasterXSize
    projection = ds.GetProjection()
    geo_trans = ds.GetGeoTransform()
    scale, offset = read_band_scale_offset(ds)
    integrate_array = np.zeros((height, width))
    del ds
    output_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LAI\LAI_INTEGRATE_OUTPUT"
    for key, value in file_index_dict.items():
        for i in value:
            raster_data = raster_read(file_list[i])
            raster_array = raster_data.ReadAsArray()
            weight = weight_index_dict[key][value.index(i)]
            integrate_array += raster_array*weight
            del raster_data
        weight_array = np.array(weight_index_dict[key])
        output_path = os.path.join(output_dir, key+".tif")
        raster_write(output_path, integrate_array, projection, geo_trans, scale=scale,
                     offset=offset, data_type=gdalconst.GDT_UInt16)
