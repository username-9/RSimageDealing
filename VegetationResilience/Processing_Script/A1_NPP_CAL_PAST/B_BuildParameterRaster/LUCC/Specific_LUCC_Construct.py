from multiprocessing import Pool

from osgeo import gdal
import os

from tqdm import tqdm

from UtilitiesForProcessingImage.BasicUtility.ReadMain import raster_read
from UtilitiesForProcessingImage.BasicUtility.UtilityFunction import workdir_filelist


def para_slc_cal(file, out_dir, ft_dir, ft_ls: list):
    print(f"---PID: {os.getpid()}---\n---Dealing with {file}---")
    ds = raster_read(file)
    ds_trans = ds.GetGeoTransform()
    ds_proj = ds.GetProjection()
    ds_width = ds.RasterXSize
    ds_height = ds.RasterYSize
    ds_datatype = ds.GetRasterBand(1).DataType
    ds_band_num = ds.RasterCount
    # get LUCC array
    lucc_array = ds.GetRasterBand(1).ReadAsArray()
    del ds
    # get forest type array by count
    year = eval(file[9:13])
    index = int((year - 2000) / 5)
    if index > 3:
        index = 3
    forest_type_ds = raster_read(os.path.join(ft_dir, str(ft_ls[index])))
    forest_type_array = forest_type_ds.GetRasterBand(1).ReadAsArray()
    del forest_type_ds
    # create a new raster to save the explicit forest type
    driver = gdal.GetDriverByName('GTiff')
    output_forest_type_ds = driver.Create(os.path.join(out_dir, file), ds_width, ds_height,
                                          bands=ds_band_num, eType=ds_datatype)
    output_forest_type_ds.SetGeoTransform(ds_trans)
    output_forest_type_ds.SetProjection(ds_proj)
    # iterate LUCC array to specify the explicit forest type
    output_forest_type_array = output_forest_type_ds.GetRasterBand(1).ReadAsArray()
    try:
        for i in tqdm(range(ds_height)):
            for j in range(ds_width):
                lucc = lucc_array[i, j]
                if lucc != 0:
                    if lucc == 1:
                        output_forest_type_array[i, j] = 6
                    elif lucc == 2:
                        forest_type = forest_type_array[i, j]
                        if forest_type == 111:
                            output_forest_type_array[i, j] = 1
                        elif forest_type == 121:
                            output_forest_type_array[i, j] = 2
                        elif forest_type == 112:
                            output_forest_type_array[i, j] = 3
                        elif forest_type == 122:
                            output_forest_type_array[i, j] = 4
                        else:
                            output_forest_type_array[i, j] = 11
                    elif lucc == 3:
                        output_forest_type_array[i, j] = 7
                    elif lucc == 4:
                        output_forest_type_array[i, j] = 5
                    else:
                        output_forest_type_array[i, j] = 8
                else:
                    output_forest_type_array[i, j] = 0
        output_forest_type_ds.WriteArray(output_forest_type_array)
        output_forest_type_ds.FlushCache()
        del output_forest_type_ds
    except Exception as e:
        print(e)
    print("Done")


if __name__ == "__main__":
    # set work and output directories
    work_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LUCC(use)\LUCC_CLIP"
    out_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LUCC(use)\LUCC_S_CONSTRUCT"
    file_ls = workdir_filelist(work_dir)
    # reading basis LUCC from file_ls
    # set a primary num to decide which forest type should be selected
    forest_type_ls_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\FORESTYPE\ForestType_Resample"
    forest_type_ls = os.listdir(forest_type_ls_dir)
    # # single process test
    # for file in tqdm(file_ls):
    #     ds = raster_read(file)
    #     ds_trans = ds.GetGeoTransform()
    #     ds_proj = ds.GetProjection()
    #     ds_width = ds.RasterXSize
    #     ds_height = ds.RasterYSize
    #     ds_datatype = ds.GetRasterBand(1).DataType
    #     ds_band_num = ds.RasterCount
    #     # get LUCC array
    #     lucc_array = ds.GetRasterBand(1).ReadAsArray()
    #     del ds
    #     # get forest type array by count
    #     year = eval(file[9:13])
    #     index = int((year - 2000) / 5)
    #     if index > 3:
    #         index = 3
    #     forest_type_filepath = os.path.join(forest_type_ls_dir, str(forest_type_ls[index]))
    #     forest_type_ds = raster_read(forest_type_filepath)
    #     forest_type_array = forest_type_ds.GetRasterBand(1).ReadAsArray()
    #     del forest_type_ds
    #     # create a new raster to save the explicit forest type
    #     driver = gdal.GetDriverByName('GTiff')
    #     output_forest_type_ds = driver.Create(os.path.join(out_dir, file), ds_width, ds_height,
    #                                           bands=ds_band_num, eType=ds_datatype)
    #     output_forest_type_ds.SetGeoTransform(ds_trans)
    #     output_forest_type_ds.SetProjection(ds_proj)
    #     # iterate LUCC array to specify the explicit forest type
    #     output_forest_type_array = output_forest_type_ds.GetRasterBand(1).ReadAsArray()
    #     for i in range(ds_height):
    #         for j in range(ds_width):

    #             lucc = lucc_array[i, j]
    #             if lucc != 0:
    #                 if lucc == 1:
    #                     output_forest_type_array[i, j] = 6
    #                 elif lucc == 2:
    #                     forest_type = forest_type_array[i, j]
    #                     if forest_type == 111:
    #                         output_forest_type_array[i, j] = 1
    #                     elif forest_type == 121:
    #                         output_forest_type_array[i, j] = 2
    #                     elif forest_type == 112:
    #                         output_forest_type_array[i, j] = 3
    #                     elif forest_type == 122:
    #                         output_forest_type_array[i, j] = 4
    #                     else:
    #                         output_forest_type_array[i, j] = 11
    #                 elif lucc == 3:
    #                     output_forest_type_array[i, j] = 7
    #                 elif lucc == 4:
    #                     output_forest_type_array[i, j] = 5
    #                 else:
    #                     output_forest_type_array[i, j] = 8
    #             else:
    #                 output_forest_type_array[i, j] = 0
    #     output_forest_type_ds.WriteArray(output_forest_type_array)
    #     output_forest_type_ds.FlushCache()
    #     del output_forest_type_ds
    #     print("Done")

    # para cal
    # construct parameter list
    para_ls = [(file_ls[i], out_dir, forest_type_ls_dir, forest_type_ls) for i in range(len(file_ls))]
    with Pool(processes=8) as pool:
        results = pool.starmap(para_slc_cal, para_ls)

    # # single run
    # os.chdir(r"D:\Data\VegetationResilienceDealing\Integrate_Output\LUCC(use)")
    # file = "CLCD_v01_2005_albert.tif"
    # para_slc_cal(file, out_dir, forest_type_ls_dir, forest_type_ls)
    # print("Done")