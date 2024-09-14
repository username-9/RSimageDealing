from osgeo import gdal
from tqdm import tqdm

from UtilitiesForProcessingImage.ImageProcessing import resample_image
from UtilitiesForProcessingImage.UtilityFunction import workdir_filelist

# def para_resample(input_path, output_dir, width, height):
#     try:
#         in_ds = gdal.Open(input_path)
#         if in_ds is None:
#             raise ValueError(f"Failed to open {input_path}")
#
#         resample_image(in_ds, width, height, output_dir=output_dir,
#                        return_ds=False, reproject_method=gdal.GRA_NearestNeighbour, input_file_path=input_path)
#         del in_ds
#     except Exception as a:
#         print(f"Error processing {input_path}: {a}")


if __name__ == "__main__":
    work_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\REF_NPP\NPP_ANNUAL_INTEGRATE"
    filelist = workdir_filelist(work_path)
    out_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\REF_NPP\NPP_ANNUAL_INTEGRATE_RESAMPLE"
    # ref tif
    ref = r"F:\DATA\Vegetation_Resilience_D_DATA_C\REF_NPP\REF_NPP_CLIP\MUSES.NPP.5km.2000001.Global.tif"
    gdal.AllRegister()
    ref_ds: gdal.Dataset = gdal.Open(ref)
    width = ref_ds.RasterXSize
    height = ref_ds.RasterYSize
    ref_trans = ref_ds.GetGeoTransform()
    del ref_ds
    # ls = [(filelist[i], out_dir, width, height) for i in range(len(filelist))]
    # resample_image(*ls)
    try:
        # with Pool(processes=1) as pool:
        #     results = pool.starmap(para_resample, ls)
        for file in tqdm(filelist):
            in_ds = gdal.Open(file)
            resample_image(in_ds, width, height, output_dir=out_dir,
                           return_ds=False, reproject_method=gdal.GRA_Bilinear,
                           input_file_path=file, reference_transform=ref_trans)
            del in_ds
    except Exception as e:
        print("something went wrong")
        raise