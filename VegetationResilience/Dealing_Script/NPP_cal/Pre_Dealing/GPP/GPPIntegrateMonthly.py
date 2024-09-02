import calendar
import os

import numpy as np
from osgeo import gdal, gdalconst
from tqdm import tqdm

from UtilitiesForDealingImage.ReadMain import raster_read, read_band_scale_offset
from UtilitiesForDealingImage.UtilityFunction import month_of_day_in_year, start_and_end_day_of_month, integrate_monthly
from UtilitiesForDealingImage.WriteMain import raster_write

if __name__ == "__main__":
    work_path = r"E:\DATA-PENG\GPP_MOSAIC_OUTPUT"
    os.chdir(work_path)
    file_list = os.listdir()
    for file in file_list:
        if not file.endswith(".tif"):
            file_list.remove(file)
    file_index_dict, weight_index_dict = integrate_monthly(file_list, 1, 5,
                                                           5, 8)
    ds = raster_read(file_list[0])
    height = ds.RasterYSize
    width = ds.RasterXSize
    projection = ds.GetProjection()
    geo_trans = ds.GetGeoTransform()
    # scale, offset = read_band_scale_offset(ds)
    del ds
    output_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\GPP\GPP_INTEGRATE_OUTPUT_MEAN_0830"
    for key, value in tqdm(file_index_dict.items()):
        integrate_array = np.zeros((height, width))
        for i in value:
            raster_data = raster_read(file_list[i])
            raster_array = raster_data.ReadAsArray()
            weight = weight_index_dict[key][value.index(i)]
            # GPP scale = 0.0001
            integrate_array += raster_array * 0.0001 * weight
            del raster_data
        year = int(key[:4])
        month = int(key[4:6])
        _, day_of_month = calendar.monthrange(year, month)
        integrate_array = integrate_array / day_of_month
        weight_array = np.array(weight_index_dict[key])
        output_path = os.path.join(output_dir, key+".tif")
        raster_write(output_path, integrate_array, projection, geo_trans, data_type=gdalconst.GDT_Float32)
