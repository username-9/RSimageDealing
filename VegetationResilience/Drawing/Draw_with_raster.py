import os
from cProfile import label

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgba

class_dict = {
    1: "ENF",
    2: "EBF",
    3: "DNF",
    4: "DBF",
    5: "Grass",
    6: "Crop",
    7: "Shrub",
    8: "Urban",
    11: "MF"
}

if __name__ == "__main__":
    npy_path = "../Processing_Script/C_Time_Series_Processing/A_Analysis/B3_VR_Analysis_By_Pixel/J_Further_Processing/RF3_Ref_And_Processing_Files/E1_construct_arr_1126.npy"
    p_path = r"../Processing_Script/C_Time_Series_Processing\A_Analysis\B3_VR_Analysis_By_Pixel\J_Further_Processing\RF3_Ref_And_Processing_Files\E2_p_arr_1126.npy"
    v_path = r"../Processing_Script/C_Time_Series_Processing\A_Analysis\B3_VR_Analysis_By_Pixel\J_Further_Processing\RF3_Ref_And_Processing_Files\E3_variance_1220.npy"

    # vr_arr = np.abs(np.load(npy_path))
    # vr_arr[vr_arr.astype(int) == 2] = np.nan
    # vmin = np.nanmin(vr_arr)
    # vmax = np.nanmax(vr_arr)
    # p_arr = np.load(p_path)
    v_arr = np.load(v_path)
    v_arr[v_arr.astype(int) == 2] = np.nan
    vmin = np.nanmin(v_arr)
    vmax = np.nanmax(v_arr)

    x_tick = [str(num) for num in range(-24, 32)]
    for i in range(len(x_tick)):
        if (i % 4) == 0:
            pass
        elif i == 0:
            pass
        else:
            x_tick[i] = ""
    y_tick = [str(num) for num in range(0, 421, 10)]
    for i in range(len(y_tick)):
        if (i % 5) == 0:
            pass
        elif i == 0:
            pass
        else:
            y_tick[i] = ""
    y_tick = y_tick[::-1]

    plt.rcParams["font.family"] = "Calibri"
    plt.rcParams["font.size"] = 30

    # set own color bar
    # 定义深抹茶色和红色的RGB值
    dark_matcha = [0.46, 0.54, 0.34]  # 深抹茶色的RGB值，可以根据需要调整
    nice_red = [0.94, 0.16, 0.16]  # 好看的红色的RGB值，可以根据需要调整

    # 创建一个字典来定义颜色映射的段数据
    # cdict = {
    #     'red': [(0.0, 0.0, 0.0),  # 0.0时红色为0（实际上是深抹茶色的红色分量）
    #             (0.5, dark_matcha[0], dark_matcha[0]),  # 中间点的红色分量，调整为抹茶色
    #             (1.0, nice_red[0], nice_red[0])],  # 1.0时红色为红色值
    #     'green': [(0.0, dark_matcha[1], dark_matcha[1]),  # 0.0时绿色为抹茶色的绿色分量
    #               (0.5, 0.7, 0.7),  # 中间点的绿色分量，调整为过渡色（这里选择了一个较为中性的绿色）
    #               (1.0, 0.0, 0.0)],  # 1.0时绿色为0（红色没有绿色分量）
    #     'blue': [(0.0, dark_matcha[2], dark_matcha[2]),  # 0.0时蓝色为抹茶色的蓝色分量
    #              (0.5, 0.7, 0.7),  # 中间点的蓝色分量，调整为过渡色（与绿色分量相同以保持色调和谐）
    #              (1.0, 0.0, 0.0)]  # 1.0时蓝色为0（红色没有蓝色分量）
    # }

    # cdict = {
    #     'red': [(0.0, dark_matcha[0], dark_matcha[0]),  # 0.0时红色为深抹茶色的红色分量
    #             (0.5, 1.0, 1.0),  # 中间点的红色分量，调整为黄色
    #             (1.0, nice_red[0], nice_red[0])],  # 1.0时红色为红色值
    #     'green': [(0.0, dark_matcha[1], dark_matcha[1]),  # 0.0时绿色为深抹茶色的绿色分量
    #               (0.5, 1.0, 1.0),  # 中间点的绿色分量，调整为黄色
    #               (1.0, 0.0, 0.0)],  # 1.0时绿色为0（红色没有绿色分量）
    #     'blue': [(0.0, dark_matcha[2], dark_matcha[2]),  # 0.0时蓝色为深抹茶色的蓝色分量
    #              (0.5, 0.0, 0.0),  # 中间点的蓝色分量，调整为黄色（没有蓝色分量）
    #              (1.0, 0.0, 0.0)]  # 1.0时蓝色为0（红色没有蓝色分量）
    # }

    # dark_research_green = (0.2, 0.3, 0.1)  # 较深的、不饱和的绿色，作为起始颜色
    # neutral_yellow = (0.7, 0.7, 0.5)  # 中性的、不饱和的黄色，作为中间颜色
    # muted_red = (0.6, 0.2, 0.2)
    # cdict = {
    #     'red': [(0.0, dark_research_green[0], dark_research_green[0]),  # 起始点为较深的绿色，红色分量为0
    #             (0.5, neutral_yellow[0], neutral_yellow[0]),  # 中间点为中性黄色，红色分量适中
    #             (1.0, muted_red[0], muted_red[0])],  # 结束点为较暗的红色
    #     'green': [(0.0, dark_research_green[1], dark_research_green[1]),  # 起始点为较深的绿色
    #               (0.5, neutral_yellow[1], neutral_yellow[1]),  # 中间点为中性黄色
    #               (1.0, 0.0, 0.0)],  # 结束点绿色分量为0
    #     'blue': [(0.0, dark_research_green[2], dark_research_green[2]),  # 起始点为较深的绿色，蓝色分量较低
    #              (0.5, neutral_yellow[2], neutral_yellow[2]),  # 中间点为中性黄色，蓝色分量较低
    #              (1.0, 0.0, 0.0)]  # 结束点蓝色分量为0
    # }

    light_research_green = (0.4, 0.5, 0.3)  # 较浅的、不饱和的绿色，作为起始颜色
    research_yellow = (0.9, 0.9, 0.7)  # 柔和的、不饱和的黄色，作为中间颜色
    soft_red = (0.8, 0.3, 0.3)  # 柔和的、不饱和的红色，但对比度适中，作为结束颜色

    # cdict = {
    #     'red': [(0.0, light_research_green[0], light_research_green[0]),  # 起始点为较浅的绿色，红色分量为0
    #             (0.5, research_yellow[0], research_yellow[0]),  # 中间点为柔和黄色，红色分量适中
    #             (1.0, soft_red[0], soft_red[0])],  # 结束点为柔和的红色，但对比度适中
    #     'green': [(0.0, light_research_green[1], light_research_green[1]),  # 起始点为较浅的绿色
    #               (0.5, research_yellow[1], research_yellow[1]),  # 中间点为柔和黄色
    #               (1.0, 0.0, 0.0)],  # 结束点绿色分量为0
    #     'blue': [(0.0, light_research_green[2], light_research_green[2]),  # 起始点为较浅的绿色，蓝色分量较低
    #              (0.5, research_yellow[2], research_yellow[2]),  # 中间点为柔和黄色，蓝色分量较低
    #              (1.0, 0.0, 0.0)]  # 结束点蓝色分量为0
    # }

    # cdict = {
    #     'red': (
    #         (0.0, 0.842, 0.842),  # (x, y0, y1) at start of red channel
    #         (1.0, 0.0588, 0.0588)  # (x, y0, y1) at end of red channel
    #     ),
    #     'green': (
    #         (0.0, 0.212, 0.212),  # (x, y0, y1) at start of green channel
    #         (1.0, 0.4667, 0.4667)  # (x, y0, y1) at end of green channel
    #     ),
    #     'blue': (
    #         (0.0, 0.208, 0.208),  # (x, y0, y1) at start of blue channel
    #         (1.0, 0.098, 0.098)  # (x, y0, y1) at end of blue channel
    #     )
    # }

    # 定义颜色
    red = '#A51C36'
    green = '#84BA42'
    middle = '#F5EBAE'

    # 将颜色从十六进制转换为RGBA格式
    red_rgba = to_rgba(red)
    green_rgba = to_rgba(green)

    # 创建一个线性渐变的颜色映射
    cmap = LinearSegmentedColormap.from_list('green_to_red', [green_rgba, middle, red_rgba])

    # 创建自定义颜色映射
    # cmap_name = 'dark_matcha_to_nice_red'
    # cmap = LinearSegmentedColormap(cmap_name, cdict)

    # fig, ax = plt.subplots(figsize=(16, 16))
    # fig: plt.Figure
    # ax: plt.Axes
    #
    # im = ax.imshow(vr_arr[0], cmap=cmap, aspect='equal')
    # ax.set_xticks([num for num in range(0, len(x_tick), 2)])
    # ax.set_yticks([num for num in range(0, len(y_tick))])
    # ax.set_xticklabels([x_tick[i] for i in range(0, len(x_tick), 2)], fontsize=15)
    # ax.set_yticklabels(y_tick, fontsize=15)
    # # fig.colorbar(im, ax=ax)
    # # ax.tick_params(labelsize=10)
    # # fig.show()
    # out_dir = r"F:\DATA\DRAW\F_PIC\2_TACS_TMP_PRE_RELATIOIN"
    # out_path = os.path.join(out_dir, "T_P_V_1.png")
    # fig.savefig(out_path)

    class_ls = [1, 2, 3, 4, 5, 6, 7, 11]
    # class_ls = [1]
    for i in range(len(class_ls)):
        fig, ax = plt.subplots(figsize=(16, 16))
        fig: plt.Figure
        ax: plt.Axes

        # im = ax.imshow(vr_arr[i], cmap=cmap, aspect='equal')
        # im = ax.imshow(vr_arr[i, ::-1, :], cmap=cmap, aspect='equal', vmin=vmin, vmax=vmax)

        im = ax.imshow(v_arr[i, ::-1, :], cmap=cmap, aspect='equal', vmin=vmin, vmax=vmax)

        ax.set_xticks([num for num in range(0, len(x_tick))])
        ax.set_yticks([num for num in range(0, len(y_tick))])
        ax.set_xticklabels([x_tick[i] for i in range(0, len(x_tick))], fontsize=30)
        ax.set_yticklabels(y_tick, fontsize=30)
        ax.set_xlabel("Temperature ($^\circ$C)", labelpad=15, fontweight='bold')
        ax.set_ylabel("Precipitation (mm)", labelpad=15, fontweight='bold')
        title = class_dict[class_ls[i]]
        ax.text(0.08, 0.935, title, ha='center', va='center', transform=ax.transAxes, fontsize=45)
        # ax.set_title(title, pad=20, fontweight='bold', fontsize= 30)
        # fig.colorbar(im, ax=ax)
        # ax.tick_params(labelsize=10)
        # fig.show()



        out_dir = r"../Processing_Script/C_Time_Series_Processing\A_Analysis\B3_VR_Analysis_By_Pixel\J_Further_Processing\RF3_Ref_And_Processing_Files\A3_TPV_PIC"
        out_path = os.path.join(out_dir, f"T_P_V_variance_{title}.png")
        fig.savefig(out_path)