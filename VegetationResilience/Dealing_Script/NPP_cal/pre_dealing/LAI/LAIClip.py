import os
from multiprocessing import Pool

from osgeo import gdal
from tqdm import tqdm

from UtilitiesForDealingImage.ImageProcessing import shape_warp_for_raster
from UtilitiesForDealingImage.ReadMain import raster_read


def para_cal(file):
    shape_path = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    output_dir = r"F:\DATA\LAI\LAI_BTH_CLIP"

    output_path = os.path.join(output_dir, file)
    shape_warp_for_raster(file, shape_path, output_path, cropToCutline=True)

if __name__ == "__main__":
    work_path = r"F:\DATA\LAI\LAI_INTEGRATE_OUTPUT"
    os.chdir(work_path)
    file_list = os.listdir()
    for file in file_list:
        if not file.endswith(".tif"):
            file_list.remove(file)
    shape_path = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    output_dir = r"F:\DATA\LAI\LAI_BTH_CLIP"
    # for file in tqdm(file_list):
    #     ds = raster_read(file)
    #     output_path = os.path.join(output_dir, file)
    #     shape_warp_for_raster(file, shape_path, output_path)

    # parallel running
    with Pool(processes=5) as pool:
        pool.map(para_cal, file_list)
