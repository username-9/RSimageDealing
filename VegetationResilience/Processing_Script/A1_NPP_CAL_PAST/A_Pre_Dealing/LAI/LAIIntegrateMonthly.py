import calendar
import os

import numpy as np
from osgeo import gdalconst
from tqdm import tqdm

from UtilitiesForProcessingImage.BasicUtility.ReadMain import raster_read, read_band_scale_offset
from UtilitiesForProcessingImage.BasicUtility.UtilityFunction import integrate_monthly
from UtilitiesForProcessingImage.BasicUtility.WriteMain import raster_write

if __name__ == "__main__":
    work_path = r"F:\DATA\LAI\LAI_MOSAICA"
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
    del ds
    output_dir = r"F:\DATA\LAI\LAI_INTEGRATE_OUTPUT"
    for key, value in tqdm(file_index_dict.items()):
        integrate_array = np.zeros((height, width))
        for i in value:
            raster_data = raster_read(file_list[i])
            raster_array = raster_data.ReadAsArray()
            weight = weight_index_dict[key][value.index(i)]
            integrate_array += raster_array*weight
            del raster_data
        weight_array = np.array(weight_index_dict[key])
        output_path = os.path.join(output_dir, key+".tif")
        year = int(key[:4])
        month = int(key[4:6])
        _, day_of_month = calendar.monthrange(year, month)
        integrate_array = ((integrate_array * 8) / day_of_month).astype(int)
        raster_write(output_path, integrate_array, projection, geo_trans, scale=scale,
                     offset=offset, data_type=gdalconst.GDT_UInt16)
