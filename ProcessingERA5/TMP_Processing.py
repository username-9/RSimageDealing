import multiprocessing
import os
import re

from osgeo import gdal
from tqdm import tqdm


def para_cal(raster, out_dir, _year):
    # check output dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # read raster and transform array
    ds = gdal.Open(raster)
    array = ds.GetRasterBand(1).ReadAsArray()
    no_data = ds.GetRasterBand(1).GetNoDataValue()
    array[array != no_data] = array[array != no_data] - 273.15
    def_proj = ds.GetProjection()
    def_trans = ds.GetGeoTransform()
    data_type = ds.GetRasterBand(1).DataType
    del ds

    # construct output raster
    month = re.findall(r'\d+(?=\.)', raster)
    if len(month) != 1:
        raise ValueError ("String matching error, check pattern for RE")
    month = month[0]
    out_path = os.path.join(out_dir, "Global_" + _year + '_' + str(month).zfill(2) + "_tem.tif")
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(out_path, array.shape[1], array.shape[0], 1, eType=data_type)
    out_ds.GetRasterBand(1).WriteArray(array)
    out_ds.SetGeoTransform(def_trans)
    out_ds.SetProjection(def_proj)
    out_ds.GetRasterBand(1).SetNoDataValue(no_data)
    out_ds.FlushCache()
    del out_ds


if __name__ == "__main__":
    # set directory and file path
    tmp_folder = r"F:\DATA\EAR5\global_ERA-5\global_2m-tempreature"
    out_dir = r"F:\DATA\EAR5\GLOBAL_OUTPUT\temperature"

    # construct path list dealing with
    handle_dict = {}
    for dir in os.listdir(tmp_folder):
        tmp_path = []
        year = re.findall(r'\d{4}$', dir)
        if len(year) != 1:
            raise ValueError ("String matching error, check pattern for RE")
        year = year[0]
        file_ls = os.listdir(os.path.join(tmp_folder, dir))
        file_ls = [file for file in file_ls if file.endswith(".tif")]
        for file in file_ls:
            tmp_path.append(os.path.join(tmp_folder, dir, file))
        handle_dict[year] = tmp_path

    # processing
    for key, value in tqdm(handle_dict.items()):
        output_dir = os.path.join(out_dir, key)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        para_ls = [(temp_file, output_dir, key) for temp_file in value]
        with multiprocessing.Pool(processes=6) as pool:
            pool.starmap(para_cal, para_ls)

    print("Done")


