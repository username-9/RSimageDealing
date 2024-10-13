import os
from datetime import datetime

import numpy as np
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt

from UtilitiesForProcessingImage.ReadMain import raster_to_array

if __name__ == "__main__":
    # direction set
    kp_path = (r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script"
               r"\Time_Series_Processing\Analysis\VR_Analysis_By_Pixel\VR_Sta_Json\E_Key_Point_Array.npy")
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_RESAMPLE"
    v_t_p_arr_path = r""

    # get data
    kp_arr = np.load(kp_path)
    ori_time = datetime(2001, 5, 1)
    fig, ax = plt.subplots(2, 2, figsize=(20, 20))
    ax_1 = ax[0, 0]
    ax_2 = ax[0, 1]
    ax_3 = ax[1, 0]
    ax_4 = ax[1, 1]

    vtp_ls = os.listdir(v_t_p_arr_path)
    vtp_ls = [file for file in vtp_ls if file.endswith(".npy")]

    # drawing key point
    for i in range(kp_arr.shape[0]):
        lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(ori_time.year) + "_albert.tif")
        ori_time = ori_time + relativedelta(months=1)

        lucc_arr = raster_to_array(lucc_path)
        vtp_arr = np.load(vtp_ls[i])

        for para in map(class_ls, ax):
            class_name = para[0]
            ax_para = para[1]
            ax_para: plt.Axes
            all_t_data = vtp_arr[1][lucc_arr == class_num].flatten()
            all_p_data = vtp_arr[2][lucc_arr == class_num].flatten()
            ax_para.scatter(all_t_data, all_p_data)

    for i in range(kp_arr.shape[0]):
        lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(ori_time.year) + "_albert.tif")
        ori_time = ori_time + relativedelta(months=1)

        lucc_arr = raster_to_array(lucc_path)
        vtp_arr = np.load(vtp_ls[i])
        kp_temp = kp_arr[i]

        for para in map(class_ls, ax):
            class_name = para[0]
            ax_para = para[1]
            ax_para: plt.Axes
            all_t_data = vtp_arr[1][(lucc_arr == class_num) & (kp_arr == 1)].flatten()
            all_p_data = vtp_arr[2][(lucc_arr == class_num) & (kp_arr == 1)].flatten()
            ax_para.scatter(all_t_data, all_p_data, facecolors='red')
