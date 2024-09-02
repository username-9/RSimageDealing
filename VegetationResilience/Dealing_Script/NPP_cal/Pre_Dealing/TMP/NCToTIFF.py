import os

from osgeo import gdalconst, gdal
from tqdm import tqdm

from UtilitiesForDealingImage.ImageTransform import nc_to_tiff

if __name__ == "__main__":
    work_path = r"D:\Data\VegetationResilienceDealing\SRC\TMP"
    os.chdir(work_path)
    # make file is all end with .nc
    file_list = os.listdir()
    for file in file_list:
        if not file.endswith(".nc"):
            file_list.remove(file)
    # reference geograph transformation
    ds = gdal.Open(r"D:\Data\VegetationResilienceDealing\SRC\REF\TMP\tmp_Layer2.tif")
    geo_trans = ds.GetGeoTransform()
    del ds
    # transform
    output_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\TMP"
    for file in tqdm(file_list):
        # nc_to_tiff(file, output_dir, "tmp", gdalconst.GDT_Int16, into_one=False, scale_all=0.1)
        nc_to_tiff(file, output_dir, "tmp", gdalconst.GDT_Int16, into_one=False,
                   scale_all=0.1, reference_geotrans=geo_trans, nodata=-32768)
