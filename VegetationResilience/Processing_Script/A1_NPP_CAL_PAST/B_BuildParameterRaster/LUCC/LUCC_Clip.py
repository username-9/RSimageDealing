import multiprocessing
import os
from multiprocessing.pool import Pool

from osgeo import gdal
from tqdm import tqdm

from UtilitiesForProcessingImage.BasicUtility.ImageProcessing import shape_warp_for_raster
from UtilitiesForProcessingImage.BasicUtility.ReadMain import raster_read


def par_function(tif_path, shape_path, out_path):
    print(f"running on {multiprocessing.current_process().pid}")
    print(tif_path)
    shape_warp_for_raster(tif_path, shape_path, out_path, cropToCutline=True)


if __name__ == "__main__":
    work_path = r"D:\Data\VegetationResilienceDealing\SRC\2000_2021CLCD\LUCC"
    os.chdir(work_path)
    file_list = os.listdir()
    for file in file_list:
        if not file.endswith(".tif"):
            file_list.remove(file)
    shape_path = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    output_dir = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LUCC(use)\LUCC_CLIP"
    out_path = []
    for file in file_list:
        ds = raster_read(file)
        out_path.append(os.path.join(output_dir, file))
        # shape_warp_for_raster(file, shape_path, output_path, cropToCutline=True)
    input_ls = [(file_list[i], shape_path, out_path[i]) for i in range(len(file_list))]
    with Pool(processes=7) as pool:
        pool.starmap(par_function, input_ls)
    os.chdir(r"D:\Data\VegetationResilienceDealing\Integrate_Output\LUCC(use)\LUCC_CLIP")
    file_ls = os.listdir(output_dir)
    for file in tqdm(file_ls):
        output_file = os.path.join(output_dir, file)
        output_file_1 = os.path.join(r"D:\Data\VegetationResilienceDealing\Integrate_Output\LUCC(use)\LUCC_CLIP_NEW", file)
        dataset = gdal.Open(output_file, gdal.GA_ReadOnly)
        creation_options = ['COMPRESS=LZW']

        # 使用gdal.Translate()进行复制并设置压缩格式
        # 注意：由于我们指定了相同的文件名作为输入和输出，这将会覆盖原文件
        gdal.Translate(output_file_1, dataset, options=gdal.TranslateOptions(creationOptions=creation_options))
        del dataset


    # tif_path = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LUCC\LUCC_CLIP\CLCD_v01_2005_albert.tif"
    # shape_path = r"D:\Data\VegetationResilienceDealing\SRC\BTH_SHAPE\mask_Dissolve_Dissolve.shp"
    # out_path = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LUCC\LUCC_CLIP\CLCD_v01_2005_albert_1.tif"
    # # shape_warp_for_raster(tif_path, shape_path, out_path)
    # creation_options = ['COMPRESS=LZW']
    # dataset = gdal.Open(out_path, gdal.GA_ReadOnly)
    # gdal.Translate(tif_path, dataset, options=gdal.TranslateOptions(creationOptions=creation_options))
    # del dataset
