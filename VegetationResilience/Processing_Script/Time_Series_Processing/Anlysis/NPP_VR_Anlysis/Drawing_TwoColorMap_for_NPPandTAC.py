import cv2
from osgeo import gdal

from Drawing.DoubleLinkColorMap import two_dimensional_color_map, improve_saturation, add_grid, colormap_array
from UtilitiesForProcessingImage.ReadMain import raster_read
from UtilitiesForProcessingImage.WriteMain import raster_write

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
    # color_map_path = r"F:\DATA\DRAW\PIC\color_map.png"
    # # add grid for color map
    # add_grid(color_arr, 10)
    # cv2.imwrite(color_map_path, color_arr)
    # cv2.imshow("img", color_arr)
    # cv2.waitKey(0)

    # read rasters
    raster_1 = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\NPP_TREND\NPP_TREND.tif"
    raster_2 = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_1_LAG\tca_1lag_0905.tif"
    ds_1 = raster_read(raster_1)
    ds_2 = raster_read(raster_2)

    color_arr = cv2.imread(r"F:\DATA\DRAW\PIC\color_map.png")

    defined_classification__1_list = [[-0.015, 0.01],[-0.01, 0],
                                      [0.000001, 0.025], [0.025001, 0.027],
                                      [0.027001, 0.03], [0.030001, 0.035],
                                      [0.035001, 0.036], [0.036001, 0.039],
                                      [0.039001, 0.1], [0.10001, 0.13]]
    defined_classification__2_list = [[0.3, 0.6], [0.6001, 0.7],
                                      [0.7001, 0.73], [0.73001, 0.75],
                                      [0.75001, 0.77], [0.77001, 0.79],
                                      [0.79001, 0.80000], [0.80001, 0.9000],
                                      [0.9001, 0.95000], [0.95001, 1]]

    out_array = colormap_array(ds_1, ds_2, color_arr, defined_classification__1_list, defined_classification__2_list)
    # write array with reference by raster_1
    ref_geotrans = ds_1.GetGeoTransform()
    ref_srs = ds_1.GetProjection()
    del ds_1
    del ds_2
    output_path = r"F:\DATA\DRAW\PIC\npp_trend_TAC_map.tif"
    raster_write(output_path, out_array, projection=ref_srs,
                 geo_transform=ref_geotrans, data_type=gdal.GDT_UInt16)