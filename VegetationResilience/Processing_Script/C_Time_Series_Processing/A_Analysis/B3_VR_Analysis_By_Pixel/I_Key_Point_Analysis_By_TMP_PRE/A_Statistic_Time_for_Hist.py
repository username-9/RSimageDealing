import json
import os
import re

import numpy as np
import tqdm

if __name__ == '__main__':
    # definition and path set
    sta_dict = {}
    npy_dir = r"F:\DATA\DRAW\PIC\3_KEY_POINT_LOCATION"
    out_json_path = r"/VegetationResilience/Processing_Script/C_Time_Series_Processing/A_Analysis/B3_VR_Analysis_By_Pixel/I_Key_Point_Analysis_By_TMP_PRE\Analysis_Json\A_Statistic_by_Time_for_Hist.json"

    # iteration about npy to statistic
    npy_ls = os.listdir(npy_dir)
    npy_ls = [file for file in npy_ls if file.endswith('.npy')]
    for n_path in tqdm.tqdm(npy_ls):
        match = re.findall(r'\d+', n_path)[0]

        n_arr = np.load(os.path.join(npy_dir, n_path))
        time_index = 0
        sta_class_dict = {}
        for i in range(n_arr.shape[0]):
            count = np.nonzero(n_arr[i, :, :])[0].size
            sta_class_dict[time_index] = count
            time_index += 1
        sta_dict[match] = sta_class_dict
    with open(out_json_path, 'w') as f:
        json.dump(sta_dict, f, indent=4)