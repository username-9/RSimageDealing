import os
from cProfile import label

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

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
    npy_path = (r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script"
                r"\Time_Series_Processing\Anlysis\VR_Analysis_By_Pixel\VR_Sta_Json\construct_arr.npy")
    p_path = (r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script"
              r"\Time_Series_Processing\Anlysis\VR_Analysis_By_Pixel\VR_Sta_Json\p_arr.npy")

    vr_arr = np.abs(np.load(npy_path))
    vr_arr[vr_arr.astype(int) == 2] = np.nan
    p_arr = np.load(p_path)

    x_tick = [str(num) for num in range(-24, 32)]
    y_tick = [str(num) for num in range(0, 421, 10)]
    y_tick = y_tick[::-1]

    plt.rcParams["font.family"] = "Calibri"
    plt.rcParams["font.size"] = 25

    # set own color bar
    # 定义深抹茶色和红色的RGB值
    dark_matcha = [0.46, 0.54, 0.34]  # 深抹茶色的RGB值，可以根据需要调整
    nice_red = [0.94, 0.16, 0.16]  # 好看的红色的RGB值，可以根据需要调整

    # 创建一个字典来定义颜色映射的段数据
    cdict = {
        'red': [(0.0, 0.0, 0.0),  # 0.0时红色为0（实际上是深抹茶色的红色分量）
                (0.5, dark_matcha[0], dark_matcha[0]),  # 中间点的红色分量，调整为抹茶色
                (1.0, nice_red[0], nice_red[0])],  # 1.0时红色为红色值
        'green': [(0.0, dark_matcha[1], dark_matcha[1]),  # 0.0时绿色为抹茶色的绿色分量
                  (0.5, 0.7, 0.7),  # 中间点的绿色分量，调整为过渡色（这里选择了一个较为中性的绿色）
                  (1.0, 0.0, 0.0)],  # 1.0时绿色为0（红色没有绿色分量）
        'blue': [(0.0, dark_matcha[2], dark_matcha[2]),  # 0.0时蓝色为抹茶色的蓝色分量
                 (0.5, 0.7, 0.7),  # 中间点的蓝色分量，调整为过渡色（与绿色分量相同以保持色调和谐）
                 (1.0, 0.0, 0.0)]  # 1.0时蓝色为0（红色没有蓝色分量）
    }

    # 创建自定义颜色映射
    cmap_name = 'dark_matcha_to_nice_red'
    cmap = LinearSegmentedColormap(cmap_name, cdict)

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
    # out_dir = r"F:\DATA\DRAW\PIC\2_TACS_TMP_PRE_RELATIOIN"
    # out_path = os.path.join(out_dir, "T_P_V_1.png")
    # fig.savefig(out_path)

    class_ls = [1, 2, 3, 4, 5, 6, 7, 11]
    for i in range(len(class_ls)):
        fig, ax = plt.subplots(figsize=(16, 16))
        fig: plt.Figure
        ax: plt.Axes

        im = ax.imshow(vr_arr[i], cmap=cmap, aspect='equal')
        ax.set_xticks([num for num in range(0, len(x_tick), 2)])
        ax.set_yticks([num for num in range(0, len(y_tick))])
        ax.set_xticklabels([x_tick[i] for i in range(0, len(x_tick), 2)], fontsize=15)
        ax.set_yticklabels(y_tick, fontsize=15)
        ax.set_xlabel("Temperature ($^\circ$C)", labelpad=15, fontweight='bold')
        ax.set_ylabel("Precipitation (mm)", labelpad=15, fontweight='bold')
        title = class_dict[class_ls[i]]
        ax.text(0.05, 0.05, title, ha='center', va='center', transform=ax.transAxes)
        # ax.set_title(title, pad=20, fontweight='bold', fontsize= 30)
        # fig.colorbar(im, ax=ax)
        # ax.tick_params(labelsize=10)
        # fig.show()
        out_dir = r"F:\DATA\DRAW\PIC\2_TACS_TMP_PRE_RELATIOIN"
        out_path = os.path.join(out_dir, f"T_P_V_{title}.png")
        fig.savefig(out_path)