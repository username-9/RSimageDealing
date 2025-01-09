import os

from UtilitiesForProcessingImage.BasicUtility.ImageProcessing import shape_warp_for_raster
from UtilitiesForProcessingImage.BasicUtility.UtilityFunction import workdir_filelist

if __name__ == "__main__":
    # work_dir = r"D:\Data\VegetationResilienceDealing\SRC\ForestType"
    # filelist = workdir_filelist(work_dir)
    # # clip forest type data
    # shape_file = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    # for file in filelist:
    #     output_file = os.path.join(r"D:\Data\VegetationResilienceDealing\Integrate_Output\FORESTYPE", file)
    #     shape_warp_for_raster(file, shape_file, output_file, cropToCutline=True)
    work_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LUCC(use)\LUCC_CLIP_NEW"
    filelist = workdir_filelist(work_dir)
    # clip forest type data
    shape_file = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    for file in filelist:
        output_file = os.path.join(r"D:\Data\VegetationResilienceDealing\Integrate_Output\LUCC(use)\LUCC_CLIP", file)
        shape_warp_for_raster(file, shape_file, output_file, cropToCutline=True)
