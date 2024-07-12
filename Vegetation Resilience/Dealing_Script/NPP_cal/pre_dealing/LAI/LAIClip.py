import os

from osgeo import gdal

from UtilitiesForDealingImage.ImageProcessing import shape_warp_for_raster
from UtilitiesForDealingImage.ReadMain import raster_read

if __name__ == "__main__":
    work_path = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LAI\LAI_INTEGRATE_OUTPUT"
    os.chdir(work_path)
    file_list = os.listdir()
    for file in file_list:
        if not file.endswith(".tif"):
            file_list.remove(file)
    shape_path = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    output_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LAI\LAI_BTH_CLIP"
    for file in file_list:
        ds = raster_read(file)
        output_path = os.path.join(output_dir, file)
        shape_warp_for_raster(file, shape_path, output_path)
