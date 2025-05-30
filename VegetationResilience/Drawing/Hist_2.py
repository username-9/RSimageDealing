import numpy as np
from matplotlib import pyplot as plt
import matplotlib.font_manager as fm
from osgeo import gdal
import scipy.ndimage as filters


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
    plt.rcParams["font.size"] = 42
    fm.findSystemFonts()
    plt.rcParams['font.sans-serif'] = ["Calibri"]
    fig, ax = plt.subplots(figsize = (20, 15))
    ax: plt.Axes
    CN_font = 'C:/Windows/Fonts/simhei.ttf'
    prop = fm.FontProperties(fname=CN_font)
    # get data
    # npp_trend = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\NPP_TREND\NPP_TREND.tif"
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
    class_list = [1, 3, 4, 5, 7, 11]
    for i in class_list:
        t1l_class_array = t1l_array[(t1l_array != 2) & (lucc_array == i)]
        # np.save(rf".\NPY_files\t1l_{i}.npy", t1l_class_array)

        t1l_class_hist, t1l_class_bin_edge = np.histogram(t1l_class_array, density=True, bins=100)
        t1l_x = [(t1l_class_bin_edge[i] + t1l_class_bin_edge[i + 1]) / 2 for i in range(len(t1l_class_bin_edge) - 1)]

        color_list = ["#f55f17", "#71a300", "#68e50f", "#706500", "#95a5a6", "#3498db", "#34495e", "#f39c12"]
        face_color_list = ["#d95012", "#5c7f00", "#55b20c", "#574d00", "#7d8c8d", "#297bba", "#263642", "#d5850b"]

        hist_class_t1l = filters.gaussian_filter(t1l_class_hist, 5)

        ax.plot(t1l_x, hist_class_t1l, color=color_list[class_list.index(i)], label=f'{class_dict[i]}',
                linewidth=5)
        # ax.plot(t1l_x, t1l_hist, color="red")

        ax.fill_between(t1l_x, 0, hist_class_t1l, facecolor=face_color_list[class_list.index(i)], alpha=0.2)

    # nt_hist, nt_bin_edge = np.histogram(nt_array, density=True, bins=100)
    # t1l_hist, t1l_bin_edge = np.histogram(t1l_array, density=True, bins=100)

    # np.save(r".\NPY_files\nt_hist.npy", nt_hist)
    # np.save(r".\NPY_files\nt_bin_edge.npy", nt_bin_edge)
    # np.save(r".\NPY_files\nt_hist_t1.npy", t1l_hist)
    # np.save(r".\NPY_files\nt_bin_edge.npy", t1l_bin_edge)

    # hist_nt = filters.gaussian_filter(nt_hist, 1)
    # hist_t1l = filters.gaussian_filter(t1l_hist, 1)

    # nt_x = [(nt_bin_edge[i]+nt_bin_edge[i+1]) / 2 for i in range(len(nt_bin_edge)-1)]
    # t1l_x = [(t1l_bin_edge[i]+t1l_bin_edge[i+1]) / 2 for i in range(len(t1l_bin_edge)-1)]

    # ax.plot(nt_x, nt_hist, color='blue')
    # # ax.plot(t1l_x, t1l_hist, color="red")
    #
    # ax.fill_between(nt_x, 0, nt_hist, facecolor='skyblue', alpha=0.2)
    # ax.fill_between(t1l_x, 0, t1l_hist, facecolor='red', alpha=0.2)

    ax.legend(loc='upper right', fontsize=42, prop=prop)
    ax.set_xlabel("TAC lag 1 month")
    ax.set_ylabel("Probability Density")
    ax.set_ylim(0)
    ax.set_xlim(0)
    fig.savefig(r".\NPY_files\t1l_hist_1226.png")



