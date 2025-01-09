import os
from datetime import datetime

import numpy as np
import tqdm
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
import matplotlib.colors as colors

from UtilitiesForProcessingImage.BasicUtility.ReadMain import raster_to_array
from VegetationResilience.Drawing.Scatter_Dot_Density import scatter_with_density


def get_all_k_point_data(single_class_num, class_trend = 1):
    # direction set
    # kp_path = r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script\C_Time_Series_Processing\A_Analysis\B3_VR_Analysis_By_Pixel\J_Further_Processing\RF2_Ref_And_Processing_Files\C_DETECT_KEY_POINT.npy"
    kp_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\B4_KP_1221\C_DETECT_KEY_POINT.npy"
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\A4_LUCC_DILATE_EXCEPT_LUCC_CHANGE"
    t_p_v_arr_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\CONSTRUCT_ARRAY_TMP_PRE_VR_1010"
    single_num = single_class_num
    class_ls = [single_num]
    plt.rcParams['font.sans-serif'] = ['Calibri']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 1000
    X = None

    if not (os.path.exists(f"RF3_Ref_And_Processing_Files/G1_KP_X_{single_num}_trend_{class_trend}_1221.npy")):
        # parameter define
        X = []

        # construct data
        vtp_ls = os.listdir(t_p_v_arr_path)
        vtp_ls = [file for file in vtp_ls if file.endswith(".npy")]

        kp_arr = np.load(kp_path)
        ori_time = datetime(2001, 5, 1)

        for i in tqdm.tqdm(range(kp_arr.shape[0])):
            lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(ori_time.year) + "_albert.tif")
            ori_time = ori_time + relativedelta(months=1)

            lucc_arr = raster_to_array(lucc_path)
            tpv_arr = np.load(os.path.join(t_p_v_arr_path, vtp_ls[i]))
            kp_temp = kp_arr[i]

            for class_num in class_ls:
                all_t_data = tpv_arr[0, :, :][(lucc_arr == class_num) & (kp_temp == class_trend)].flatten() / 10
                all_p_data = tpv_arr[1, :, :][(lucc_arr == class_num) & (kp_temp == class_trend)].flatten() / 10
                arr = np.concatenate((all_t_data[:, np.newaxis], all_p_data[:, np.newaxis]), axis=1)
                X.append(arr)

        X = np.concatenate(X, axis=0)
        # X = X[np.all(X, axis=1) != 0]

        np.save(f"RF3_Ref_And_Processing_Files/G1_KP_X_{single_num}_trend_{class_trend}_1221.npy", X)
    else:
        X = np.load(f"RF3_Ref_And_Processing_Files/G1_KP_X_{single_num}_trend_{class_trend}_1221.npy")
    return X

def main_process(single_num):
    # direction set
    # kp_path = r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script\C_Time_Series_Processing\A_Analysis\B3_VR_Analysis_By_Pixel\J_Further_Processing\RF2_Ref_And_Processing_Files\C_DETECT_KEY_POINT.npy"
    kp_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\B4_KP_1221\C_DETECT_KEY_POINT.npy"
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\1101_archive\A4_LUCC_DILATE_EXCEPT_LUCC_CHANGE"
    t_p_v_arr_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\CONSTRUCT_ARRAY_TMP_PRE_VR_1010"
    single_num = single_num
    class_ls = [single_num]
    plt.rcParams['font.sans-serif'] = ['Calibri']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 1000

    # get data
    kp_arr = np.load(kp_path)
    ori_time = datetime(2001, 5, 1)
    fig, ax = plt.subplots(1, len(class_ls), figsize=(10 * len(class_ls), 10))
    if len(class_ls) == 1:
        ax = [ax]

    vtp_ls = os.listdir(t_p_v_arr_path)
    vtp_ls = [file for file in vtp_ls if file.endswith(".npy")]

    X = get_all_k_point_data(single_num)

    all_k_t_data = X[:, 0]
    all_k_p_data = X[:, 1]

    # degree = 5
    # coefficients = np.polyfit(all_k_t_data, all_k_p_data, degree)
    # print(coefficients)
    # polynomial = Polynomial(coefficients)

    # def model_func(x, a, b):
    #     # return a * x ** 2 + b * x + c
    #     return a * np.exp(b * x)

    # def model_func_1(x, a, c):
    #     return a * x ** 2 + c
        # return a * np.exp(b * x)

    def model_func(x, a, b):
        return a * np.exp(b * x)

    # 使用curve_fit进行非线性回归
    if not ((list(all_k_p_data) == []) or (list(all_k_t_data) == [])):
        # x , y 数据都不为空的话->
        # params, covariance = curve_fit(model_func_1, all_k_t_data, all_k_p_data)
        params, covariance = curve_fit(model_func, all_k_t_data, all_k_p_data)

        # 获取拟合参数
        # a_fit, c_fit = params
        a_fit, b_fit = params
        print(params)
        x_fit = np.linspace(min(all_k_t_data), max(all_k_t_data), 100)
        # y_fit = polynomial(x_fit)
        # y_fit = model_func_1(x_fit, a_fit, c_fit)

        y_fit = model_func(x_fit, a_fit, b_fit)
        y_pred = model_func(all_k_t_data, a_fit, b_fit)
        # y_pred = model_func_1(all_k_t_data, a_fit, c_fit)

        r2 = r2_score(all_k_p_data, y_pred)
        print(r2)

        x_list = np.linspace(min(all_k_p_data), max(all_k_p_data), 100)
        y_list = np.linspace(min(all_k_p_data), max(all_k_p_data), 100)

        cdict = {
            'red': ((0.0, 1.0, 1.0),  # 白色
                    (1.0, 0.8, 1.0)),  # 纯的低饱和度红色（仅红色分量有值）
            'green': ((0.0, 0.0, 1.0),  # 白色（绿色分量为 0）
                      (1.0, 0.0, 1.0)),  # 低饱和度红色（绿色分量仍然为 0）
            'blue': ((0.0, 0.0, 1.0),  # 白色（蓝色分量为 0）
                     (1.0, 0.0, 1.0))  # 低饱和度红色（蓝色分量仍然为 0）
        }

        # 创建颜色映射
        cmap = colors.LinearSegmentedColormap('my_cmap', cdict)

        _, _, xmesh, ymesh, zmesh, colormap = scatter_with_density(all_k_t_data, all_k_p_data, x_fit, y_list)
        # ax[0].contourf(xmesh, ymesh, zmesh, cmap=cmap)

        # drawing key point
        print("Drawing all point")
        for i in tqdm.tqdm(range(kp_arr.shape[0])):
            lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(ori_time.year) + "_albert.tif")
            ori_time = ori_time + relativedelta(months=1)

            lucc_arr = raster_to_array(lucc_path)
            tpv_arr = np.load(os.path.join(t_p_v_arr_path, vtp_ls[i]))

            for para in zip(class_ls, ax):
                class_num = para[0]
                ax_para = para[1]
                ax_para: plt.Axes
                all_t_data = tpv_arr[0, :, :][lucc_arr == class_num].flatten() / 10
                all_p_data = tpv_arr[1, :, :][lucc_arr == class_num].flatten() / 10
                ax_para.scatter(all_t_data, all_p_data, s=1, c='gray', alpha=0.1, edgecolors='none')

        cs = ax[0].contour(xmesh, ymesh, zmesh, cmap=cmap, linewidths=0.75)

        print("Drawing key points")
        ori_time = datetime(2001, 5, 1)
        for i in tqdm.tqdm(range(kp_arr.shape[0])):
            lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(ori_time.year) + "_albert.tif")
            ori_time = ori_time + relativedelta(months=1)

            lucc_arr = raster_to_array(lucc_path)
            tpv_arr = np.load(os.path.join(t_p_v_arr_path, vtp_ls[i]))
            kp_temp = kp_arr[i]

            for para in zip(class_ls, ax):
                class_num = para[0]
                ax_para = para[1]
                ax_para: plt.Axes
                all_t_data = tpv_arr[0, :, :][(lucc_arr == class_num) & (kp_temp == 1)].flatten() / 10
                all_p_data = tpv_arr[1, :, :][(lucc_arr == class_num) & (kp_temp == 1)].flatten() / 10
                ax_para.scatter(all_t_data, all_p_data, facecolors='#d62447', s=8, edgecolors='none')
                # all_t_data = tpv_arr[0, :, :][(lucc_arr == class_num) & (kp_temp == 2)].flatten() / 10
                # all_p_data = tpv_arr[1, :, :][(lucc_arr == class_num) & (kp_temp == 2)].flatten() / 10
                # ax_para.scatter(all_t_data, all_p_data, facecolors='blue', s=8, edgecolors='none')
        ax[0].tick_params(axis='both', which='major', labelsize=18)
        ax[0].plot(x_fit, y_fit, label=f'Result of nonlinear fitting', color='#308cc5', linewidth=2)
        ax[0].text(0.05, 0.8, rf'$y = {a_fit:.2f} \cdot e^{{{b_fit:.2f} \cdot x}}$' + '\n' + rf'$R^2: {r2:.2f}$',
                   fontsize=20, transform=ax[0].transAxes, ha='left', va='center')
        # ax[0].text(0.05, 0.8, rf"$y = {a_fit:.2f}x^{2}+{c_fit:.2f}$" + '\n' + rf'$R^2: {r2:.2f}$',
        #            fontsize=20, transform=ax[0].transAxes, ha='left', va='center')
    else:
        print("Drawing all point")
        for i in tqdm.tqdm(range(kp_arr.shape[0])):
            lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(ori_time.year) + "_albert.tif")
            ori_time = ori_time + relativedelta(months=1)

            lucc_arr = raster_to_array(lucc_path)
            tpv_arr = np.load(os.path.join(t_p_v_arr_path, vtp_ls[i]))

            for para in zip(class_ls, ax):
                class_num = para[0]
                ax_para = para[1]
                ax_para: plt.Axes
                all_t_data = tpv_arr[0, :, :][lucc_arr == class_num].flatten() / 10
                all_p_data = tpv_arr[1, :, :][lucc_arr == class_num].flatten() / 10
                ax_para.scatter(all_t_data, all_p_data, s=1, c='gray', alpha=0.1, edgecolors='none')
        print("Drawing key points")
        ori_time = datetime(2001, 5, 1)
        for i in tqdm.tqdm(range(kp_arr.shape[0])):
            lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(ori_time.year) + "_albert.tif")
            ori_time = ori_time + relativedelta(months=1)

            lucc_arr = raster_to_array(lucc_path)
            tpv_arr = np.load(os.path.join(t_p_v_arr_path, vtp_ls[i]))
            kp_temp = kp_arr[i]

            for para in zip(class_ls, ax):
                class_num = para[0]
                ax_para = para[1]
                ax_para: plt.Axes
                all_t_data = tpv_arr[0, :, :][(lucc_arr == class_num) & (kp_temp == 2)].flatten() / 10
                all_p_data = tpv_arr[1, :, :][(lucc_arr == class_num) & (kp_temp == 2)].flatten() / 10
                ax_para.scatter(all_t_data, all_p_data, facecolors='blue', s=8, edgecolors='none')
        ax[0].tick_params(axis='both', which='major', labelsize=18)
    # ax[0].legend(fontsize=20)
    # cbar = fig.colorbar(cs)
    plt.ylim(bottom=0)
    plt.xlabel("Temperature ($^\circ$C)", fontsize=20)
    plt.ylabel("Precipitation (mm)", fontsize=20)
    fig: plt.Figure
    fig.savefig(f"RF3_Ref_And_Processing_Files/I_PIC/A2_Tmp_Pre_Sta_Scatter_{single_num}_density_fit_1227.png")


if __name__ == "__main__":
    for i in [1, 4, 5, 11]:
        main_process(i)

