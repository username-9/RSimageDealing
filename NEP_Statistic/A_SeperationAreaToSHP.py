from osgeo import ogr, gdal

from UtilitiesForProcessingImage.UtilityFunction import separate_vector

if __name__ == "__main__":
    # set directories and file path
    guangdong_xian_polygon = r"C:\Users\PZH\Desktop\ProgrammeGuangdong\广东省保护区数据\Export_Output.shp"
    out_dir = r"C:\Users\PZH\Desktop\ProgrammeGuangdong\vector_raster\1024\ProtectAreaSeparation"

    separate_vector(guangdong_xian_polygon, out_dir, "name")
    print("done")
