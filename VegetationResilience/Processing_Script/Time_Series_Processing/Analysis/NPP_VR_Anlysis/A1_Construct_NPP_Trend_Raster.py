import os

import numpy as np
from osgeo import gdal

if __name__ == "__main__":
    # read ds
    ref_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\NPP\NPP_MONTHLY\npp_2000-003.tif"
    output_file_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\NPP_TREND"
    ref_ds = gdal.Open(ref_path, gdal.GA_ReadOnly)
    ds_trans = ref_ds.GetGeoTransform()
    ds_proj = ref_ds.GetProjection()
    ds_width = ref_ds.RasterXSize
    ds_height = ref_ds.RasterYSize
    ds_band_num = ref_ds.RasterCount
    del ref_ds
    # create empty SLA raster
    npp_t_path = os.path.join(output_file_dir, "NPP_TREND_0919" + ".tif")
    driver = gdal.GetDriverByName('GTiff')
    npp_t_ds: gdal.Dataset = driver.Create(npp_t_path, ds_width, ds_height, bands=ds_band_num, eType=gdal.GDT_Float32)
    npp_t_ds.SetGeoTransform(ds_trans)
    npp_t_ds.SetProjection(ds_proj)
    # get trend array
    n_array_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\DETREND\npp_interception_0919.npy"
    trend_array = np.load(n_array_path)
    npp_t_ds.WriteArray(trend_array)
    npp_t_ds.FlushCache()
    del npp_t_ds