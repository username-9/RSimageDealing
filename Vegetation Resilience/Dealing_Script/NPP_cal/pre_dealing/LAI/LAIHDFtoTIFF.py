import os

from osgeo import gdalconst

from UtilitiesForDealingImage.ImageTransform import hdf_to_tiff

if __name__ == "__main__":
    # HDF to TIFF
    os.chdir(r"D:\Data\VegetationResilienceDealing\SRC\MODIS_LAI_BTH_2000_2024_8day")
    file_list = os.listdir()
    output_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LAI\LAI_HDF_to_TIFF_OUTPUT"
    if os.path.exists(output_dir):
        pass
    else:
        os.mkdir(output_dir)
    # transform to tiff
    for file in file_list:
        if file.endswith(".hdf"):
            hdf_to_tiff(file, output_dir, 1, data_type=gdalconst.GDT_UInt16)
