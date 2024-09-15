import os
from multiprocessing import Pool

from UtilitiesForProcessingImage.ImageProcessing import shape_warp_for_raster


def para_cal(_file):
    shape_path = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    output_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0831_archive\REF_NPP\NPP_REF\REF_NPP_NASA_CASA_CLIP"

    output_path = os.path.join(output_dir, _file)
    shape_warp_for_raster(_file, shape_path, output_path, cropToCutline=True)


if __name__ == "__main__":
    work_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0831_archive\REF_NPP\NPP_REF\SRC_NASA_CASA\UNZIP"
    os.chdir(work_path)
    file_list = os.listdir()
    file_list = [file for file in file_list if file.endswith(".tif")]
    shape_path = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    output_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0831_archive\REF_NPP\NPP_REF\REF_NPP_NASA_CASA_CLIP"
    # for file in tqdm(file_list):
    #     output_path = os.path.join(output_dir, file)
    #     shape_warp_for_raster(file, shape_path, output_path, cropToCutline=True)
    # parallel running
    with Pool(processes=10) as pool:
        pool.map(para_cal, file_list)