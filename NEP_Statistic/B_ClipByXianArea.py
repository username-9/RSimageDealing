import os

import tqdm
from osgeo import gdal

from UtilitiesForProcessingImage.ImageProcessing import shape_warp_for_raster

if __name__ == "__main__":
    # set directories and file path
    shp_file_dir = r"C:\Users\PZH\Desktop\GuangDong1030\CarbonStatistic\ProcessingFiles\A_GuangdongXianAreaSeparation"
    tiff_file_dir = r"C:\Users\PZH\Desktop\ProgrammeGuangdong\data\郭建晓大论文数据资料\2_过程数据产品及最终成果数据\5_NEP及趋势分析\NEP2000-2020"
    output_dir = r"C:\Users\PZH\Desktop\ProgrammeGuangdong\1029\XianAreaClip"

    # processing
    ## get all the shape file paths
    shp_file_list = os.listdir(shp_file_dir)
    shp_file_list = [file for file in shp_file_list if file.endswith(".shp")]

    ## get all the tiff file paths
    tiff_file_list = os.listdir(tiff_file_dir)
    tiff_file_list = [file for file in tiff_file_list if file.endswith(".tif")]

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)


    # iterate tiff file
    for tif in tqdm.tqdm(tiff_file_list):
        # iterate shape file
        year = tif[3:7]
        if not os.path.exists(os.path.join(output_dir, year)):
            os.makedirs(os.path.join(output_dir, year))
        for shp in shp_file_list:
            print(shp)
            out_path = os.path.join(output_dir, year, shp.split(".shp")[0]+".tif")
            shape_warp_for_raster(os.path.join(tiff_file_dir, tif), os.path.join(shp_file_dir, shp), out_path, cropToCutline=True, nodata=-9999)

