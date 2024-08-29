import os

from osgeo import gdalconst

from UtilitiesForDealingImage.ImageTransform import hdf_to_tiff

if __name__ == "__main__":
    # hdf to tiff
    os.chdir(r"C:\Users\PZH\Desktop\MODIS-NPP-2001-2024")
    file_list = os.listdir()
    output_dir = r"..\output_GPP_tif"
    if os.path.exists(output_dir):
        pass
    else:
        os.mkdir(output_dir)
    # transform to tiff
    for file in file_list:
        if file.endswith(".hdf"):
            hdf_to_tiff(file, output_dir, 0, data_type=gdalconst.GDT_Float32)
