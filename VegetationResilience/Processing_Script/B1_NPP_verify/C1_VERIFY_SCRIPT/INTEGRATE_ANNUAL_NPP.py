import os

from osgeo import gdal
from tqdm import tqdm

from UtilitiesForProcessingImage.BasicUtility.UtilityFunction import workdir_filelist

if __name__ == "__main__":
    work_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\NPP\NPP_MONTHLY"
    out_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\NPP\NPP_ANNUAL"
    file_ls = workdir_filelist(work_dir)

    # get reference information
    in_ds = gdal.Open(file_ls[0], gdal.GA_ReadOnly)
    ds_trans = in_ds.GetGeoTransform()
    ds_proj = in_ds.GetProjection()
    ds_width = in_ds.RasterXSize
    ds_height = in_ds.RasterYSize
    ds_band_num = in_ds.RasterCount

    # get the file list dict for integrate
    integrate_dict = {}
    for file in file_ls:
        year = file[4:8]
        integrate_dict.setdefault(year, []).append(file)
    for year, file_list in tqdm(integrate_dict.items()):
        integrate_array = None
        out_path = os.path.join(out_dir, year + ".tif")
        for file in file_list:
            ds = gdal.Open(file)
            ds_array = ds.GetRasterBand(1).ReadAsArray()
            if integrate_array is None:
                integrate_array = ds_array
            else:
                integrate_array += ds_array
        # create output raster
        driver = gdal.GetDriverByName('GTiff')
        npp_a_ds: gdal.Dataset = driver.Create(out_path, ds_width, ds_height, bands=ds_band_num, eType=gdal.GDT_Float32)
        npp_a_ds.SetGeoTransform(ds_trans)
        npp_a_ds.SetProjection(ds_proj)
        npp_a_ds.GetRasterBand(1).WriteArray(integrate_array)
        npp_a_ds.FlushCache()
        del npp_a_ds
    print("Done")