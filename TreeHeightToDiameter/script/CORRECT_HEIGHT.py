import os

import numpy as np
from osgeo import gdal, ogr

import TreeFunction
from UtilitiesForProcessingImage.BasicUtility.ImageProcessing import shape_warp_for_raster
from UtilitiesForProcessingImage.BasicUtility.UtilityFunction import fix_vector_error
from UtilitiesForProcessingImage.BasicUtility.WriteMain import array_to_raster


# Function to mask a raster based on a shapefile attribute filter
def mask_raster(raster_path, shapefile_path, output_path, attribute_filter, fix_vector: bool = False):
    # try to fix vector
    if fix_vector:
        fix_vector_error(shapefile_path, os.path.join(os.path.dirname(shapefile_path)) + "fix_shape.shp")

    # Open raster dataset
    # raster_ds = gdal.Open(raster_path, gdal.GA_ReadOnly)
    # if raster_ds is None:
    #     raise ValueError(f"Unable to open raster dataset: {raster_path}")

    # # Get raster dimensions and geotransform
    # cols = raster_ds.RasterXSize
    # rows = raster_ds.RasterYSize
    # geotransform = raster_ds.GetGeoTransform()
    # projection = raster_ds.GetProjection()

    # Create output raster dataset
    driver = gdal.GetDriverByName('GTiff')
    # out_ds = driver.Create(output_path, cols, rows, 1, gdal.GDT_Float32)
    # out_ds.SetGeoTransform(geotransform)
    # out_ds.SetProjection(projection)


    # Open shapefile and select features based on attribute filter
    shape_ds: ogr.DataSource = ogr.Open(shapefile_path)
    if shape_ds is None:
        raise ValueError(f"Unable to open shapefile: {shapefile_path}")

    layer = shape_ds.GetLayer()
    layer.SetAttributeFilter(attribute_filter)
    spatialRef = layer.GetSpatialRef()

    # Create a memory layer to hold the selected features
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.CreateDataSource(r'.\REF\data.shp')
    shp_layer = ds.CreateLayer('layer', geom_type=ogr.wkbPolygon, srs=spatialRef)

    # Copy selected features to memory layer
    for feature in layer:
        shp_layer.CreateFeature(feature.Clone())
    ds.FlushCache()
    shape_ds.Destroy()
    ds.Destroy()

    # Create a mask band from the selected features
    # mask_band = out_ds.GetRasterBand(1)
    # mask_band.SetNoDataValue(0)

    # Apply mask to the raster
    shape_warp_for_raster(raster_path, r'.\REF\data.shp', output_path, cropToCutline=False)

    # Close datasets
    # del out_ds
    # del raster_ds
    # del shape_ds


# Example usage and processing loop
if __name__ == "__main__":
    H_raster_path = r"C:\Users\PZH\Desktop\res_tcl_data\栅格\res_xz_ndsm1.tif"
    F_raster_path = r"C:\Users\PZH\Desktop\res_tcl_data\栅格\res_xz_zbfgd1.tif"
    Slope_raster_path = r"C:\Users\PZH\Desktop\res_tcl_data\栅格\res_xz_slope1.tif"
    shape_path = r"C:\Users\PZH\Desktop\res_tcl_data\矢量\fix.shp"

    dealing_dict = {
        (180000, 190000, 220000, 260000, 261000, 262000, 290000): TreeFunction.SongLei,
        (310000, 320000, 330000, 340000, 350000, 360000, 390000): TreeFunction.ShanLei,
        (530000, 535000, 540000, 761000, 590000, 630000): TreeFunction.YangShu,
        (440000, 410000, 711000, 801000, 710000, 804000, 580000,
         480000, 490000, 620000, 819000, 849000): TreeFunction.ZhangShu,
        (701000, 702000, 703000, 704000, 705000, 706000, 707000,
         709000, 749000, 769000, 755000, 799000): TreeFunction.GuoShuLei
    }

    # Loop through each species defined in dealing_dict
    for key, species in dealing_dict.items():
        attribute_filter = " OR ".join([f'"YOU_SHI_SZ"' + '=' + f"'{spe_num}'" for spe_num in key])

        # Mask and process each raster dataset
        # Mask H_raster
        print(f"[{species.__name__}]")
        output_H_array_path = rf"C:\Users\PZH\Desktop\江苏项目\数据处理\output\masked_H_raster_{species.__name__}.tif"
        mask_raster(H_raster_path, shape_path, output_H_array_path, attribute_filter)

        # Read masked H_raster and perform further processing
        H_ds: gdal.Dataset = gdal.Open(output_H_array_path, gdal.GA_ReadOnly)
        geotrans = H_ds.GetGeoTransform()
        projection = H_ds.GetProjection()
        H_array = H_ds.ReadAsArray()
        del H_ds  # Close H_ds

        # Mask F_raster
        output_F_array_path = rf"C:\Users\PZH\Desktop\江苏项目\数据处理\output\masked_F_raster_{species.__name__}.tif"
        mask_raster(F_raster_path, shape_path, output_F_array_path, attribute_filter)

        # Read masked F_raster and perform further processing
        F_ds: gdal.Dataset = gdal.Open(output_F_array_path, gdal.GA_ReadOnly)
        F_arr = F_ds.ReadAsArray()
        del F_ds  # Close F_ds

        # Mask Slope_raster
        output_Slope_array_path = rf"C:\Users\PZH\Desktop\江苏项目\数据处理\output\masked_Slope_raster_{species.__name__}.tif"
        mask_raster(Slope_raster_path, shape_path, output_Slope_array_path, attribute_filter)

        # Read masked Slope_raster and perform further processing
        Slope_ds = gdal.Open(output_Slope_array_path, gdal.GA_ReadOnly)
        Slope_arr = Slope_ds.ReadAsArray()
        del Slope_ds  # Close Slope_ds

        # Additional processing steps as per your requirements
        Slope_arr = np.cos(Slope_arr / 180 * np.pi)
        result_carbon = species.calculate_area_carbon(F_arr, Slope_arr, H_array)
        output_path_1 = rf"C:\Users\PZH\Desktop\江苏项目\数据处理\cal_output\cal_raster_{species.__name__}.tif"
        array_to_raster(result_carbon, output_path_1, geotrans, projection, data_type=gdal.GDT_Float32)

