from osgeo import gdal

from tqdm import tqdm

from UtilitiesForProcessingImage.ImageProcessing import resample_image
from UtilitiesForProcessingImage.UtilityFunction import workdir_filelist

if __name__ == "__main__":
    work_path = r"D:\Data\VegetationResilienceDealing\Integrate_Output\LUCC(use)\LUCC_S_CONSTRUCT"
    filelist = workdir_filelist(work_path)
    out_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\REF_NPP\LUCC_RESAMPLE"
    # ref tif
    ref = r"F:\DATA\Vegetation_Resilience_D_DATA_C\REF_NPP\REF_NPP_INTEGRATE\200003.tif"
    gdal.AllRegister()
    ref_ds: gdal.Dataset = gdal.Open(ref)
    width = ref_ds.RasterXSize
    height = ref_ds.RasterYSize
    ref_trans = ref_ds.GetGeoTransform()
    del ref_ds
    try:
        for file in tqdm(filelist):
            in_ds = gdal.Open(file)
            resample_image(in_ds, width, height, output_dir=out_dir,
                           return_ds=False, reproject_method=gdal.GRA_NearestNeighbour,
                           input_file_path=file, reference_transform=ref_trans)
            del in_ds
    except Exception as e:
        print("something went wrong")
        raise