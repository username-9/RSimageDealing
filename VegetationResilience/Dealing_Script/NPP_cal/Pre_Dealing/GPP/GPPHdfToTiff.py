import os
from multiprocessing import Pool

from osgeo import gdalconst

from UtilitiesForDealingImage.ImageTransform import hdf_to_tiff


def para_cal(file):
    print(f"---PID: {os.getpid()}---\n---Dealing with {file}---")
    out_dir = r"E:\DATA-PENG\GPP_HDF_to_TIFF_OUTPUT"
    hdf_to_tiff(file, out_dir, 0, data_type=gdalconst.GDT_Float32, hdf_no_value_data=30000)


if __name__ == "__main__":
    # HDF to TIFF
    os.chdir(r"D:\Data\VegetationResilienceDealing\src\MODIS_GPP_BTH_2000_2024_8day")
    file_list = os.listdir()
    output_dir = r"E:\DATA-PENG\GPP_HDF_to_TIFF_OUTPUT"
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
