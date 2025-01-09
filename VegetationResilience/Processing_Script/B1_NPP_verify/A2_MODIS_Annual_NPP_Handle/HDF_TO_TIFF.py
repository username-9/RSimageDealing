import os
from multiprocessing import Pool

from osgeo import gdalconst

from UtilitiesForProcessingImage.BasicUtility.ImageTransform import hdf_to_tiff


def para_cal(file):
    print(f"---PID: {os.getpid()}---\n---Dealing with {file}---")
    out_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\REF_NPP\REF_NPP_ANNUAL\HDF_TO_TIFF"
    hdf_to_tiff(file, out_dir, 1, data_type=gdalconst.GDT_Float32, hdf_no_value_data=30000)


if __name__ == "__main__":
    # HDF to TIFF
    os.chdir(r"D:\Data\VegetationResilienceDealing\SRC\MODIS_NPP_BTH_2001_2024_annul")
    file_list = os.listdir()
    output_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\REF_NPP\REF_NPP_ANNUAL\HDF_TO_TIFF"
    if os.path.exists(output_dir):
        pass
    else:
        os.mkdir(output_dir)
    # transform to tiff
    for file in file_list:
        if not file.endswith(".hdf"):
            file_list.remove(file)
    with Pool(processes=20) as pool:
        results = pool.map(para_cal, file_list)