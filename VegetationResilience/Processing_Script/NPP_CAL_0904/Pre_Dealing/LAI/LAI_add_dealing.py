import os
from multiprocessing import Pool

from osgeo import gdal, gdalconst

from UtilitiesForProcessingImage.UtilityFunction import workdir_filelist


def para_cal(file):
    print(f"---PID: {os.getpid()}---\n---Dealing with {file}---")
    lai_ds = gdal.Open(file)
    ds_trans = lai_ds.GetGeoTransform()
    ds_proj = lai_ds.GetProjection()
    ds_width = lai_ds.RasterXSize
    ds_height = lai_ds.RasterYSize
    ds_band_num = lai_ds.RasterCount
    lai_array = lai_ds.GetRasterBand(1).ReadAsArray()
    del lai_ds
    output_dir = r"E:\DATA-PENG\LAI_TIFF_ADD"
    lai_path = os.path.join(output_dir, file)
    driver = gdal.GetDriverByName('GTiff')
    lai_ds_n: gdal.Dataset = driver.Create(lai_path, ds_width, ds_height, bands=ds_band_num, eType=gdalconst.GDT_UInt16)
    lai_ds_n.SetGeoTransform(ds_trans)
    lai_ds_n.SetProjection(ds_proj)
    lai_array[lai_array > 100] = 0
    lai_ds_n.WriteArray(lai_array)
    lai_ds_n.FlushCache()
    del lai_ds_n


if __name__ == "__main__":
    lai_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LAI\LAI_HDF_to_TIFF_OUTPUT"
    lai_file_ls = workdir_filelist(lai_dir)
    with Pool(processes=10) as pool:
        pool.map(para_cal, lai_file_ls)
