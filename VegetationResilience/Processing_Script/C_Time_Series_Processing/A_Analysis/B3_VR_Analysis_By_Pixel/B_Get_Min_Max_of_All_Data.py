import os

import numpy as np
import tqdm

if __name__ == "__main__":
    # get min and max value of temperature and precipitation
    npy_file_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\CONSTRUCT_ARRAY_TMP_PRE_VR_1010"
    min_tmp_v = 0
    max_tmp_v = 0
    min_pre_v= 4000
    max_pre_v = 0

    file_ls = os.listdir(npy_file_dir)
    file_ls = [file for file in file_ls if file.endswith(".npy")]

    for i in tqdm.tqdm(file_ls):
        ref_npy = np.load(os.path.join(npy_file_dir, i))
        tmp_arr = ref_npy[0, :, :]
        min_tmp_v = min(np.min(tmp_arr), min_tmp_v)
        max_tmp_v = max(np.max(tmp_arr), max_tmp_v)
        del tmp_arr
        pre_arr = ref_npy[1, :, :]
        min_pre_v = min(np.min(pre_arr), min_pre_v)
        max_pre_v = max(np.max(pre_arr), max_pre_v)
        del pre_arr

    print(f"min tmp : {min_tmp_v}\nmax tmp : {max_tmp_v}\nmin pre : {min_pre_v}\nmax pre : {max_pre_v}")