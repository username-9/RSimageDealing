import json
import math

import numpy as np
from numpy import ndarray
from scipy import stats
import scipy.ndimage as filters

from VegetationResilience.Drawing.Line import get_line_data


def bg_algorithm(series: ndarray, p : float):
    """
    detect the transformation point by Bernaola Galvan algorithm
    :param series:  a one dim array to be analyzed
    :param p: the probability of making a mistake
    :return: mutational site index
    """
    pass

def slide_window_detection_by_standard_deviation(data, window_size, significance_threshold=3.0):
    if window_size < 2:
        raise ValueError("Window width must bigger than or equal to 2")

    n = len(data)
    std_devs = np.zeros(n - window_size + 1)

    # calculate standard deviation
    for i in range(n - window_size + 1):
        window = data[i:i + window_size]
        std_devs[i] = np.std(window)

        # find the index of drastic change of standard deviation
    change_points = []
    for i in range(1, len(std_devs) - 1):
        if np.abs(std_devs[i] - std_devs[i - 1]) > significance_threshold * np.mean([std_devs[i], std_devs[i - 1]]) or \
                np.abs(std_devs[i] - std_devs[i + 1]) > significance_threshold * np.mean(
            [std_devs[i], std_devs[i + 1]]):
            change_points.append(i + window_size // 2)  # 将突变点定位到窗口中心

    return change_points


def calculate_derivative(data, index):
    if index < 0 or index >= len(data) - 1:
        raise IndexError("Index out of bounds for calculating derivative.")

    # 前向差分
    forward_difference = data[index + 1] - data[index]

    # 后向差分
    backward_difference = data[index] - data[index - 1]

    # 中心差分（如果索引不是列表的第一个或最后一个元素）
    if 0 < index < len(data) - 1:
        central_difference = (data[index + 1] - data[index - 1]) / 2
    else:
        central_difference = None  # 或者可以选择使用前向或后向差分

    return forward_difference


def detection_by_bg_t_test(data, alpha=0.05, judgment: bool= False):
    """
    detect the mutational point by Bernaola Galvan algorithm
    :param judgment: whether judging for trend
    :param data: one dim array to be analyzed
    :param alpha: significance level for mutation detection
    :return: index of mutational site(1~N-2), at the same time, it is (1~N-2) in data index
    """
    # split series with iterate
    t_series = []
    for i in range(1, len(data) - 1):
        one_side_data = data[:i]
        the_other_data = data[i+1:]
        # get mean and standard deviation
        osd_mean = np.mean(one_side_data)
        tod_mean = np.mean(the_other_data)
        osd_std = np.std(one_side_data)
        tod_std = np.std(the_other_data)
        osd_count = len(one_side_data)
        tod_count = len(the_other_data)

        sd_i = math.sqrt(((osd_count - 1) * osd_std + (tod_count - 1) * tod_std) /
                       (osd_count + tod_count - 2)) * math.sqrt(1 / osd_count + 1 / tod_count)
        t_i = abs(osd_mean - tod_mean) / sd_i
        t_series.append(t_i)
    t_max = max(enumerate(t_series), key=lambda x: x[1])
    p_value = 2 * stats.t.sf(abs(t_max[1]), (len(data) - 2))
    if p_value < alpha:
        if judgment:
            trend = calculate_derivative(data, t_max[0])
            return t_max[0], trend
        else:
            return t_max[0]


def detect_all_mutational_site(arr, alpha, judgment: bool = False) -> list:
    """
    using BG algorithm to detect all mutational site
    :param judgment: whether judging for trend
    :param arr: array(must be 1 dimension) to be analyzed
    :param alpha: probability of making a mistake
    :return: a list containing index of all mutational sites
    """
    if arr.ndim != 1:
        raise ValueError("arr must be one dimensional")
    mutational_sites = []
    re = detection_by_bg_t_test(arr, alpha, judgment)
    check = True
    arr_list = []
    if re is not None:
        mutational_sites.append(re)
        if judgment:
            re = re[0]
        arr_list.append(arr[:re+1])
        arr_list.append(arr[re+1:])
    else:
        check = False
    while check:
        arr_list_check = arr_list
        if arr_list_check != arr_list:
            arr_list = arr_list_check
        for index, arr_test in enumerate(arr_list):
            re = detection_by_bg_t_test(arr_test, alpha, judgment=judgment)
            if re is not None:
                trend = None
                if judgment:
                    trend = re[1]
                    re = re[0]
                devi = 0
                if index != 0:
                    for k in range(index):
                        devi += len(arr_list[k])
                if judgment:
                    mutational_sites.append((re + 1 + devi, trend))
                else:
                    mutational_sites.append(re + 1 + devi)
                side_1 = arr_test[:re + 1]
                side_2 = arr_test[re + 1:]
                arr_list_check.pop(index)
                arr_list_check.insert(index, side_2)
                arr_list_check.insert(index, side_1)
        if arr_list_check == arr_list:
            check = False
    return mutational_sites


if __name__ == '__main__':
    sta_dict, sta_dict_2, x_ls, x_tick = get_line_data()
    draw_class_ls = [1, 3, 4, 5, 6, 7, 11]
    mutational_site_dict = {}
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
    for i in draw_class_ls:
        data_y = sta_dict[str(i)]
        # data_y_smooth = filters.gaussian_filter(data_y, 3)
        # m_s = detect_all_mutational_site(data_y, 0.5)
        m_s = slide_window_detection_by_standard_deviation(data_y, window_size=3, significance_threshold=3)
        mutational_site_dict[i] = m_s
    json.dump(mutational_site_dict, open(r'../F_Analysis_JSON/mutational_site_dict.json', 'w'))

