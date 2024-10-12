import json
import os
import statistics

import numpy as np
from scipy.stats import stats
from tqdm import tqdm

if __name__ == "__main__":
    # get every time value and each lucc VR values
    json_lucc = r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script\Time_Series_Processing\Analysis\VR_Analysis_By_Pixel\VR_Sta_Json\C_Merge_Bin_Data_LUCC.json"
    out_npy_dir = (r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script"
                    r"\Time_Series_Processing\Analysis\VR_Analysis_By_Pixel\VR_Sta_Json")
    with open(json_lucc, "r") as f:
        vr_lucc_dict = json.load(f)

    width = 31 + 24 + 1
    height = 42 + 1
    class_ls = [1, 2, 3, 4, 5, 6, 7, 11]
    construct_arr = np.ones((len(class_ls), height, width)) * 2
    p_arr = np.zeros((len(class_ls), height, width))
    for key, value in tqdm(vr_lucc_dict.items()):
        key = eval(key)
        x_pos = key[0] + 24
        y_pos = int(key[1] / 10)
        for i in range(len(class_ls)):
            if not value[str(class_ls[i])]:
                construct_arr[i, y_pos, x_pos] = 2
            else:
                sta_data = value[str(class_ls[i])]
                mean_data = statistics.mean(sta_data)
                construct_arr[i, y_pos, x_pos] = mean_data
                t_stat, p_value = stats.ttest_1samp(sta_data, 0)
                if p_value < 0.05:
                    p_arr[i, y_pos, x_pos] = 1
    np.save(os.path.join(out_npy_dir, "D_p_arr_1010.npy"), p_arr)
    np.save(os.path.join(out_npy_dir, "D_construct_arr_1010.npy"), construct_arr)