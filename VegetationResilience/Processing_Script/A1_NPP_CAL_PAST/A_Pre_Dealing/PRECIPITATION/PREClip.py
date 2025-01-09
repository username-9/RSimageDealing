import os

from tqdm import tqdm

from UtilitiesForProcessingImage.BasicUtility.ImageProcessing import shape_warp_for_raster
from UtilitiesForProcessingImage.BasicUtility.ReadMain import raster_read

if __name__ == "__main__":
    work_path = r"D:\Data\VegetationResilienceDealing\Integrate_Output\PRE\PRE_TRANSFORM_OUTPUT"
    os.chdir(work_path)
    file_list = os.listdir()
    for file in file_list:
        if not file.endswith(".tif"):
            file_list.remove(file)
    shape_path = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    output_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\PRE\PRE_BTH_CLIP_OUTPUT"
    for file in tqdm(file_list):
        ds = raster_read(file)
        output_path = os.path.join(output_dir, file)
        shape_warp_for_raster(file, shape_path, output_path)