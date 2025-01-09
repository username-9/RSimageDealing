import json
import os

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.font_manager as fm
from osgeo import gdal
import scipy.ndimage as filters
import seaborn as sns
from tqdm import tqdm

class_dict = {
    1 : "常绿针叶林",
    2 : "常绿阔叶林",
    3 : "落叶针叶林",
    4 : "落叶阔叶林",
    5 : "草地",
    6 : "耕地",
    7 : "灌木",
    8 : "居民用地",
    11 : "混交林"
}

if __name__ == "__main__":
    # plt.rcParams["font.size"] = 42
    plt.rcParams['font.sans-serif'] = ["Calibri"]
    # fig, ax = plt.subplots(figsize = (20, 15))
    fig, ax = plt.subplots()
    ax: plt.Axes
    CN_font = 'C:/Windows/Fonts/simhei.ttf'
    prop = fm.FontProperties(fname=CN_font)
    violinData = None
    class_list = [1, 3, 4, 5, 7, 11]
    # get data
    if os.path.exists("./NPY_files/ViolinData.json"):
        with open("./NPY_files/ViolinData.json", "r", encoding="utf-8") as f:
            violinData = json.load(f)
    else:
        tac_1_lag = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\TAC_1_LAG\tca_1lag_0919.tif"
        lucc = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_ALL_SAME_TYPE\TYPE_SAME_VEGETATION_LUCC.tif"

        ds_t1l = gdal.Open(tac_1_lag)
        t1l_array = ds_t1l.GetRasterBand(1).ReadAsArray()
        del ds_t1l

        ds_lucc = gdal.Open(lucc)
        lucc_array = ds_lucc.GetRasterBand(1).ReadAsArray()
        del ds_lucc

        # flatten array to one dimension
        t1l_array = t1l_array.flatten()
        t1l_array = np.abs(t1l_array)
        lucc_array = lucc_array.flatten()

        # get data by lucc
        data_dict = {}
        for i in tqdm(class_list):
            t1l_class_array = t1l_array[(t1l_array != 2) & (lucc_array == i)]
            data_dict[i] = list(t1l_class_array.astype(float))
        with open('./NPY_files/ViolinData.json', 'w') as handle:
            json.dump(data_dict, handle)
        violinData = data_dict

    # violin plot
    label = []
    # colors = ("#228e45", "#007b7a", "#546672", "#f47720", "#f5c75b", "#f16147")
    colors = ("#1a9641", "#a6d96a", "#bacf68", "#d0c466", "#fdae61", "#d7191c")
    for i in class_list:
        label.append(class_dict[i])
    data_list = list(violinData.values())
    sns.violinplot(data=data_list, palette=colors, saturation=0.6)
    plt.xticks(list(range(len(class_list))), labels=label, fontproperties=prop)

    plt.savefig("./NPY_files/D1_ViolinData.png", dpi=600)