import json
import os
from datetime import datetime
from operator import index

import matplotlib
import numpy as np
import scipy
import tqdm
from dateutil.relativedelta import relativedelta
import matplotlib.font_manager as fm
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.proj3d import transform

if __name__ == '__main__':
    plt.rcParams['font.sans-serif'] = ['Calibri']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 1000
    # plt.rcParams['figure.figsize'] = (10, 5)

    json_path = r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script\C_Time_Series_Processing\A_Analysis\B3_VR_Analysis_By_Pixel\J_Further_Processing\RF3_Ref_And_Processing_Files\H4_Statistic_by_Time_for_Hist_e2_2021.json"
    with open(json_path, 'r') as f:
        data_dict = json.load(f)

    # class_dict = {
    #     1: "ENF",
    #     2: "EBF",
    #     3: "DNF",
    #     4: "DBF",
    #     5: "Grass",
    #     6: "Crop",
    #     7: "Shrub",
    #     8: "Urban",
    #     11: "MF"
    # }

    class_dict = {
        1: "常绿针叶林",
        2: "常绿阔叶林",
        3: "落叶针叶林",
        4: "落叶阔叶林",
        5: "草地",
        6: "耕地",
        7: "灌木",
        8: "居民用地",
        11: "混交林"
    }

    fig, ax = plt.subplots(figsize=(20, 9))
    fig: plt.Figure
    ax: plt.Axes
    x_tick = []
    x_pos = []
    total_width = 0.9
    width = total_width / 5
    wid_index = 0
    color_list = ["#629c35", "#d4e6bc", "#a5b55d", "#d4e6bc"]
    # ["#9aa7c1", "#f2a297", "#a5dce9", "#7fcfc2"]
    color_index = 0
    for class_num, value_dict in tqdm.tqdm(data_dict.items()):
        if class_num not in ["1", "4", "11", "5"]:
            continue
        value_dict: dict
        data_x = value_dict.keys()
        if not x_pos:
            x_pos = list(data_x)
            x_pos = [int(float(_) - total_width / 2 + width / 2) for _ in x_pos]
        if not x_tick:
            datatime = datetime(2001, 5, 1)
            relative_month = relativedelta(months=1)
            x_tick = [(datatime + relativedelta(months=int(index))).strftime("%Y%m") for index in data_x]
        data_y = list(value_dict.values())
        x_pos_1 = [_ + width * wid_index for _ in x_pos]
        wid_index += 1
        x_tick = [_[:4] + "-" + _[4:] for _ in x_tick]
        group_elements_num = 5
        group_num = int(len(x_tick) / group_elements_num)
        for i in range(group_num):
            for j in range(group_elements_num - 1):
                x_tick[group_elements_num * i + j + 1] = ""
            leave = len(x_tick) % group_elements_num
            if leave:
                for j in range(leave):
                    x_tick[group_elements_num * group_num + j] = ""
            # x_tick[6*i] = ""
        if wid_index == 2:
            ax.bar(x_pos_1, data_y, width=width, label=class_dict[eval(class_num)], tick_label=x_tick, color=color_list[color_index])
        else:
            ax.bar(x_pos_1, data_y, width=width, label=class_dict[eval(class_num)], color=color_list[color_index])
        ax.tick_params(axis='x', which='major', labelsize=16, rotation=90)
        ax.tick_params(axis='y', which='major', labelsize=16)

        # drawing the line
        y_smooth = scipy.ndimage.gaussian_filter(np.array(data_y), sigma=0.1)
        ax.plot(np.array(x_pos_1), y_smooth, linewidth=0.5, color=color_list[color_index])
        color_index = color_index + 1
    CN_font = 'C:/Windows/Fonts/simhei.ttf'
    prop = fm.FontProperties(fname=CN_font, size=25)
    fig.legend(loc=(0.15, 0.61), prop=prop)
    fig.savefig("RF3_Ref_And_Processing_Files/B8_Time_Statistic_e2_Bar_Tick_Modify_test_class.png")