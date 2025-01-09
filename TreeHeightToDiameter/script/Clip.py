from UtilitiesForProcessingImage.BasicUtility.ImageProcessing import shape_warp_for_raster
from UtilitiesForProcessingImage.BasicUtility.ReadMain import raster_read

if __name__ == "__main__":
    file = r"C:\Users\PZH\Desktop\江苏项目\数据处理\output_cal_raster.tif"
    shape_path = r"C:\Users\PZH\Desktop\res_tcl_data\矢量\大丰林地一张图_select01_pro120_select_all_yssz_dis.shp"
    output_path = r"C:\Users\PZH\Desktop\江苏项目\数据处理\clip.tif"
    ds = raster_read(file)
    shape_warp_for_raster(file, shape_path, output_path)
