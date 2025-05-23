import os
from datetime import datetime

import numpy as np
import tqdm
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt

from UtilitiesForProcessingImage.BasicUtility.ReadMain import raster_to_array

if __name__ == "__main__":
    # direction set
    kp_path = (r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script"
               r"\Time_Series_Processing\Analysis\VR_Analysis_By_Pixel\VR_Sta_Json\E_Key_Point_Array.npy")
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_RESAMPLE"
    t_p_v_arr_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\CONSTRUCT_ARRAY_TMP_PRE_VR_1010"
    class_ls = [1]
    plt.rcParams['font.sans-serif'] = ['Calibri']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 1000

    # get data
    kp_arr = np.load(kp_path)
    ori_time = datetime(2001, 5, 1)
    fig, ax = plt.subplots(1, len(class_ls), figsize=(10 * len(class_ls), 10))

    vtp_ls = os.listdir(t_p_v_arr_path)
    vtp_ls = [file for file in vtp_ls if file.endswith(".npy")]

    # drawing key point
    print("Drawing all point")
    for i in tqdm.tqdm(range(kp_arr.shape[0])):
        lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(ori_time.year) + "_albert.tif")
        ori_time = ori_time + relativedelta(months=1)

        lucc_arr = raster_to_array(lucc_path)
        vtp_arr = np.load(os.path.join(t_p_v_arr_path, vtp_ls[i]))

        for para in zip(class_ls, ax):
            class_num = para[0]
            ax_para = para[1]
            ax_para: plt.Axes
            x = vtp_arr[0, :, :][lucc_arr == class_num]
            all_t_data = vtp_arr[0, :, :][lucc_arr == class_num].flatten() / 10
            all_p_data = vtp_arr[1, :, :][lucc_arr == class_num].flatten() / 10
            ax_para.scatter(all_t_data, all_p_data)

    print("Drawing key points")
    ori_time = datetime(2001, 5, 1)
    for i in tqdm.tqdm(range(kp_arr.shape[0])):
        lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(ori_time.year) + "_albert.tif")
        ori_time = ori_time + relativedelta(months=1)

        lucc_arr = raster_to_array(lucc_path)
        vtp_arr = np.load(os.path.join(t_p_v_arr_path, vtp_ls[i]))
        kp_temp = kp_arr[i]

        for para in zip(class_ls, ax):
            class_num = para[0]
            ax_para = para[1]
            ax_para: plt.Axes
            all_t_data = vtp_arr[0, :, :][(lucc_arr == class_num) & (kp_temp == 1)].flatten() / 10
            all_p_data = vtp_arr[1, :, :][(lucc_arr == class_num) & (kp_temp == 1)].flatten() / 10
            ax_para.scatter(all_t_data, all_p_data, facecolors='red')

    fig: plt.Figure
    fig.savefig("./Analysis_Json/C1_Tmp_Pre_Sta_Scatter_1.png")
