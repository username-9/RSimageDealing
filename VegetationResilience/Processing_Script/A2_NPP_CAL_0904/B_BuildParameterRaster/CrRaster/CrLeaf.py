import os
from multiprocessing import Pool

from osgeo import gdal
from tqdm import tqdm

from UtilitiesForProcessingImage.BasicUtility.UtilityFunction import workdir_filelist
from VegetationResilience.Processing_Script.A1_NPP_CAL_PAST.B_BuildParameterRaster.SLARaster.SLARaster import get_specific_lucc_dict


def para_cal(input_file_path, output_file_dir, ref_dictionary):
    print(f"---PID: {os.getpid()}---\n---Dealing with {input_file_path}---")
    # read ds
    in_ds = gdal.Open(input_file_path, gdal.GA_ReadOnly)
    lucc_array = in_ds.GetRasterBand(1).ReadAsArray()
    lucc_array_temp = lucc_array.astype(float)
    lucc_array = lucc_array_temp
    ds_trans = in_ds.GetGeoTransform()
    ds_proj = in_ds.GetProjection()
    ds_width = in_ds.RasterXSize
    ds_height = in_ds.RasterYSize
    ds_band_num = in_ds.RasterCount
    del in_ds
    # create empty y raster
    Crleaf_path = os.path.join(output_file_dir, "Crleaf_" + os.path.basename(input_file_path)[9:13] + ".tif")
    driver = gdal.GetDriverByName('GTiff')
    Crleaf_ds: gdal.Dataset = driver.Create(Crleaf_path, ds_width, ds_height, bands=ds_band_num, eType=gdal.GDT_Float32)
    Crleaf_ds.SetGeoTransform(ds_trans)
    Crleaf_ds.SetProjection(ds_proj)
    sla_array = Crleaf_ds.GetRasterBand(1).ReadAsArray()
    # get reference parameter
    ref_s_dict = {}
    for i in range(8):
        if i == 7:
            ref_s_dict[str(i + 1)] = ref_dictionary[str(11)]["10"]
        else:
            ref_s_dict[str(i + 1)] = ref_dictionary[str(i + 1)]["10"]
    # exchange and iteration(make sure all the index is right in your master optimising the speed)
    ref_ls = list(ref_s_dict.values())
    for i in tqdm(range(len(ref_ls))):
        if ref_ls[i] not in {1, 2, 3, 4, 5, 6, 7, 11}:
            # if lucc code is 11 make it equal to the right index
            if i == 7:
                lucc_array[lucc_array == 11] = ref_ls[7]
            else:
                lucc_array[lucc_array == i + 1] = ref_ls[i]
        else:
            for j in range(lucc_array.shape[1]):
                for k in range(lucc_array.shape[0]):
                    if lucc_array[k][j] == 11:
                        lucc_array[k][j] = ref_ls[i]
                    if lucc_array[k][j] == i + 1:
                        lucc_array[k][j] = ref_ls[i]
    lucc_array[lucc_array == 8] = 0
    Crleaf_ds.WriteArray(lucc_array)
    Crleaf_ds.FlushCache()
    del Crleaf_ds
    print("r leaf raster done")


if __name__ == "__main__":
    ref_dict = get_specific_lucc_dict()

    # get specific LUCC file list
    work_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_RESAMPLE"
    file_ls = workdir_filelist(work_dir)

    out_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\PARAMETER\Rleaf"
    para_ls = [(file_ls[i], out_dir, ref_dict) for i in range(len(file_ls))]
    with Pool(processes=8) as pool:
        results = pool.starmap(para_cal, para_ls)
