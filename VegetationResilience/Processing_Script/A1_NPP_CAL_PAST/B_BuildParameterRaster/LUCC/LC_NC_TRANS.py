import os

from osgeo import gdalconst, gdal
from tqdm import tqdm

from UtilitiesForProcessingImage.BasicUtility.ImageTransform import nc_to_tiff

if __name__ == "__main__":
    work_path = r"D:\Data\VegetationResilienceDealing\SRC\2000_2021CLCD"
    os.chdir(work_path)
    # make file is all end with .nc
    file_list = os.listdir()
    for file in file_list:
        if not file.endswith(".nc"):
            file_list.remove(file)
    # reference geograph transformation
    ds = gdal.Open(r"D:\Data\VegetationResilienceDealing\Integrate_Output\GPP\GPP_BTH_CLIP\200001.tif")
    geo_trans = ds.GetGeoTransform()
    del ds

    # variability list
    variables = ["ENF", "EBF", "DNF", "DBF", "shrub", "c3grass", "c4grass", "c3crop", "c4crop", "nonveg"]
    # transform
    output_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\CLCD\CLCD_TIFF"
    for file in tqdm(file_list):
        # nc_to_tiff(file, output_dir, "tmp", gdalconst.GDT_Int16, into_one=False, scale_all=0.1)
        # nc_to_tiff(file, output_dir, "tmp", gdalconst.GDT_Int16, into_one=False,
        #            scale_all=0.1, reference_geotrans=geo_trans, nodata=-32768)
        for var in variables:
            nc_to_tiff(file, output_dir, var, gdalconst.GDT_Int16, into_one=False,
                       reference_geotrans=geo_trans)
