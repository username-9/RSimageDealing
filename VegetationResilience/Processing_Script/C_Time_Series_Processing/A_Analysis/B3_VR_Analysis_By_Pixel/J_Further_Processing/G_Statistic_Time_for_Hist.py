import json
import os
import re

import numpy as np
import tqdm

if __name__ == '__main__':
    # definition and path set
    sta_dict = {}
    npy_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\B4_KEY_POINT_LOCATION_EXCEPT_LUCC_CHANGE"
    out_json_path = "RF3_Ref_And_Processing_Files/H4_Statistic_by_Time_for_Hist_e2_2021.json"

    # iteration about npy to statistic
    npy_ls = os.listdir(npy_dir)
    npy_ls = [file for file in npy_ls if file.endswith('.npy')]
    for n_path in tqdm.tqdm(npy_ls):
        match = re.findall(r'\d+', n_path)[0]

        n_arr = np.load(os.path.join(npy_dir, n_path))
        time_index = 0
        sta_class_dict = {}
        for i in range(n_arr.shape[0]):
            # count = np.count_nonzero(n_arr[i, :, :] == 1)
            count = np.count_nonzero(n_arr[i, :, :] == 2)
            sta_class_dict[time_index] = count
            time_index += 1
        sta_dict[match] = sta_class_dict
    with open(out_json_path, 'w') as f:
        json.dump(sta_dict, f, indent=4)