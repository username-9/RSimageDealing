import cv2
from osgeo import gdal

from Drawing.DoubleLinkColorMap import colormap_array
from UtilitiesForProcessingImage.BasicUtility.ReadMain import raster_read
from UtilitiesForProcessingImage.BasicUtility.WriteMain import raster_write

if __name__ == "__main__":
    # # get two-dim color map array
    # # color_arr = two_dimensional_color_map(90, 120, [30, 240],
    # #                                       [30, 240], color_num=10, color_block_size=30)
    # color_arr = two_dimensional_color_map(63, 120.5, [70, 255],
    #                                       [70, 234], x_v=[200, 150], y_v=[200, 160],
    #                                       color_num=10, color_block_size=50, output_size=(1000, 1000))
    # # color_arr = two_dimensional_color_map(50, 155, [0, 255],
    # #                                       [0, 255],
    # #                                       color_num=10, color_block_size=30)
    # # color_arr = image_improve(color_arr)
    # color_arr = improve_saturation(color_arr)
    # color_map_path = r"F:\DATA\DRAW\F_PIC\color_map.png"
    # # add grid for color map
    # add_grid(color_arr, 10)
    # cv2.imwrite(color_map_path, color_arr)
    # cv2.imshow("img", color_arr)
    # cv2.waitKey(0)

    # read rasters
    raster_1 = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\NPP_TREND\NPP_TREND_0919.tif"
    raster_2 = r"F:\DATA\DRAW\Vegetation_Resilience\PIC\6_PIC_REPEAT_1126\tac_trend_1202.tif"
    ds_1 = raster_read(raster_1)
    ds_2 = raster_read(raster_2)

    color_arr = cv2.imread(r"F:\DATA\DRAW\Vegetation_Resilience\PIC\1_NPP_TAC_ANLYSIS\color_map_1212.png")

    # past 1115
    # defined_classification__1_list = [[-0.025, -0.020001],[-0.02, -0.0151],
    #                                   [-0.015, -0.01001], [-0.01, -0.005001],
    #                                   [-0.005, 0], [0.0000001, 0.001],
    #                                   [0.0010001, 0.005], [0.0050001, 0.01],
    #                                   [0.0100001, 0.02], [0.0200001, 0.3]]
    # defined_classification__2_list = [[0, 0.1], [0.1001, 0.2],
    #                                   [0.2001, 0.3], [0.30001, 0.4],
    #                                   [0.4001, 0.5], [0.5001, 0.6],
    #                                   [0.6001, 0.70000], [0.70001, 0.8000],
    #                                   [0.8001, 0.9000], [0.9001, 1]]

    # 1115
    defined_classification__1_list = [[-1, -0.0020001],[-0.002, -0.00150001],
                                      [-0.0015, -0.0010001], [-0.001, -0.00050001],
                                      [-0.0005, 0], [0.0000001, 0.0005],
                                      [0.0050001, 0.001], [0.0010001, 0.002],
                                      [0.00200001, 0.004], [0.00400001, 1]]
    defined_classification__2_list = [[-1, -0.00040001], [-0.0004, -0.00030001],
                                      [-0.0003, -0.0002001], [-0.0002, -0.00010001],
                                      [-0.0001, 0], [0, 0.0001],
                                      [0.00010001, 0.0002], [0.00020001, 0.0003],
                                      [0.00030001, 0.0004], [0.0004001, 0.9]]

    out_array = colormap_array(ds_1, ds_2, color_arr, defined_classification__1_list, defined_classification__2_list)
    # write array with reference by raster_1
    ref_geotrans = ds_1.GetGeoTransform()
    ref_srs = ds_1.GetProjection()
    del ds_1
    del ds_2
    output_path = r"F:\DATA\DRAW\Vegetation_Resilience\PIC\6_PIC_REPEAT_1126\TWO_COLOR_MAP\npp_trend_TAC_trend_map_1212_2.tif"
    raster_write(output_path, out_array, projection=ref_srs,
                 geo_transform=ref_geotrans, data_type=gdal.GDT_UInt16)