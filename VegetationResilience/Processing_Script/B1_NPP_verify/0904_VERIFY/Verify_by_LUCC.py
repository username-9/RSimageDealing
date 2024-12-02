import os

import numpy as np
from osgeo import gdal
from sklearn.metrics import r2_score
from tqdm import tqdm

from VegetationResilience.Processing_Script.B1_NPP_verify.C1_VERIFY_SCRIPT.Verify import get_file_ls, rmse, mae, mse
from VegetationResilience.Drawing.Scatter import scatter

if __name__ == "__main__":
    # set directory
    npp_verify_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\NPP\NPP_DAILY_VERIFY\V_RESAMPLE"
    npp_ref_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0831_archive\REF_NPP\NPP_REF\REF_NPP_INTEGRATE_MuSyq"  # REF NPP Clip First
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_RESAMPLE"

    # output_dir = r""

    # get file
    npp_verify_ls = get_file_ls(npp_verify_dir)
    npp_ref_ls = get_file_ls(npp_ref_dir)

    # get ref value and verify value
    verify_array = []
    class_num = 11
    npy_path = rf"/VegetationResilience/Processing_Script\NPP_verify\VerifyArray\{class_num}_16_VerifyArray.npy"
    if not os.path.exists(npy_path):
        verify_temp = None
        for npp_v in tqdm(npp_verify_ls, total=len(npp_ref_dir)):
            year = npp_v[4:8]
            lucc_file_name = "CLCD_v01_"+f"{year}"+"_albert.tif"
            lucc_ds = gdal.Open(os.path.join(lucc_dir, lucc_file_name), gdal.GA_ReadOnly)
            lucc_array = lucc_ds.GetRasterBand(1).ReadAsArray()
            # construct mask array
            lucc_array[~(lucc_array == class_num)] = 0
            lucc_array[lucc_array == class_num] = 1

            index = npp_verify_ls.index(npp_v)
            if index >= len(npp_ref_ls):
                break
            npp_r = npp_ref_ls[index]
            print(f"year {year}, NPP-V {npp_v}, NPP-R {npp_r}")
            # get dataset
            npp_v_ds: gdal.Dataset = gdal.Open(os.path.join(npp_verify_dir, npp_v))
            npp_v_array = npp_v_ds.ReadAsArray()
            del npp_v
            npp_v_array = npp_v_array * lucc_array
            npp_r_ds: gdal.Dataset = gdal.Open(os.path.join(npp_ref_dir, npp_r))
            npp_r_array = npp_r_ds.ReadAsArray()
            del npp_r
            npp_r_array = npp_r_array * lucc_array
            npp_r_one_a = npp_r_array.ravel()
            npp_v_one_a = npp_v_array.ravel()
            verify_temp = np.column_stack((npp_r_one_a, npp_v_one_a))
            verify_array.append(verify_temp)
        verify_array = np.array(verify_array)
        np.save(npy_path, verify_array)
    else:
        verify_array = np.load(npy_path)
    # pre-dealing for data
    static_array = np.concatenate(verify_array, axis=0)
    filtered_array = static_array[~(np.any(static_array==0, axis=1))]
    if filtered_array is not None:
        # calculate the RMSE
        array_x = filtered_array[:, 0] / 100
        array_y = filtered_array[:, 1] * 1000
        rmse, r_rmse = rmse(array_x, array_y)
        mae = mae(array_x, array_y)
        mse = mse(array_x, array_y)
        r_2 = r2_score(array_x, array_y)
        print(f"RMSE: {rmse}\nMAE: {mae}\nMSE: {mse}\nR-2 Score: {r_2}\nRelative RMSE:{r_rmse}")
        # plot scatter
        scatter(array_x, array_y, ee=2, ci=90,
                file_dir=r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\NPP\NPP_DAILY_VERIFY",
                file_name=f"{class_num}_NPP_M_VERIFY.png",
                r_2=r_2,
                rmse=rmse)
    else:
        print(f"There is no class {class_num}")