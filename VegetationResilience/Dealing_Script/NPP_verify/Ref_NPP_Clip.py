import os
from multiprocessing import Pool

from UtilitiesForDealingImage.ImageProcessing import shape_warp_for_raster


def para_cal(file):
    shape_path = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    output_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\REF_NPP\REF_NPP_CLIP"

    output_path = os.path.join(output_dir, file)
    shape_warp_for_raster(file, shape_path, output_path, cropToCutline=True)


if __name__ == "__main__":
    work_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\REF_NPP\src_NPP"
    os.chdir(work_path)
    file_list = os.listdir()
    for file in file_list:
        if not file.endswith(".tif"):
            file_list.remove(file)
    shape_path = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    output_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\REF_NPP\REF_NPP_CLIP"
    # for file in tqdm(file_list):
    #     output_path = os.path.join(output_dir, file)
    #     shape_warp_for_raster(file, shape_path, output_path, cropToCutline=True)
    # parallel running
    with Pool(processes=10) as pool:
        pool.map(para_cal, file_list)