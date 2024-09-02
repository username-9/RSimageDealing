import os

from osgeo import gdal

from UtilitiesForDealingImage.ImageProcessing import shape_warp_for_raster, set_nodata

if __name__ == "__main__":
    # clip the images
    os.chdir("C:\\Users\\PZH\\Desktop\\output\\")
    file_list = os.listdir()
    if os.path.exists(r"..\output_Clip"):
        pass
    else:
        os.mkdir(r"..\output_Clip")
    for file in file_list:
        if file.endswith(".tif") is not True:
            file_list.remove(file)
    shape_file = r"C:\Users\PZH\Desktop\BTH\mask_Dissolve_Dissolve.shp"
    for file in file_list:
        output_file = os.path.join(r"..\output_Clip", file)
        shape_warp_for_raster(file, shape_file, output_file)
    ds = gdal.Open(r"C:\Users\PZH\Desktop\output_detrended\detrended_merge.tif", gdal.GA_Update)
    set_nodata(ds, 0)
