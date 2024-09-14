import multiprocessing
import os
import re

from osgeo import gdal
from tqdm import tqdm

from UtilitiesForProcessingImage.ImageProcessing import shape_warp_for_raster


def para_cal(raster, out_dir, _year):
    # check output dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    ds = gdal.Open(raster)
    no_data = ds.GetRasterBand(1).GetNoDataValue()
    del ds

    # directory set
    clip_shp = r"F:\DATA\ChinaAdminDivisonSHP-24.02.06\1. Country\country.shp"

    # clip raster
    out_path = os.path.join(out_dir, str(os.path.basename(raster)).replace('Global', 'China'))
    if not os.path.exists(out_path):
        shape_warp_for_raster(raster, clip_shp, out_path, srs=None, cropToCutline=True, nodata=no_data)



if __name__ == "__main__":
    # set directory and file path
    p_work_dir = r"F:\DATA\EAR5\GLOBAL_OUTPUT"
    output_folder = r"F:\DATA\EAR5\CHINA_CLIP"

    # construct path list dealing with
    for work_dir in tqdm(os.listdir(p_work_dir), position=0, leave=True):
        out_dir = os.path.join(output_folder, work_dir)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        handle_dict = {}
        work_dir = os.path.join(p_work_dir, work_dir)
        for dir in os.listdir(work_dir):
            tmp_path = []
            year = re.findall(r'\d{4}$', dir)
            if len(year) != 1:
                raise ValueError("String matching error, check pattern for RE")
            year = year[0]
            file_ls = os.listdir(os.path.join(work_dir, dir))
            file_ls = [file for file in file_ls if file.endswith(".tif")]
            for file in file_ls:
                tmp_path.append(os.path.join(work_dir, dir, file))
            handle_dict[year] = tmp_path

        # processing
        for key, value in tqdm(handle_dict.items(), position=1, leave=False):
            output_dir = os.path.join(out_dir, key)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            para_ls = [(temp_file, output_dir, key) for temp_file in value]
            with multiprocessing.Pool(processes=6) as pool:
                pool.starmap(para_cal, para_ls)


    print("Done")