import json
import os

import matplotlib.pyplot as plt
import tqdm
import scipy.ndimage as filters


def get_line_data():
    # get data
    avg_json = r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Drawing\NPY_files\OUTPUT_STA_AVG_LS_1010.json"
    count_json = r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Drawing\NPY_files\OUTPUT_COUNT_LUCC_LS_1010.json"
    sta_dict: dict = {}
    sta_dict_2 = None
    json_file = (r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script"
                 r"\Time_Series_Processing\Analysis\Analysis_JSON\A_OUTPUT_S_LUCC_STA_1010.json")
    with open(json_file, "r") as file:
        data = dict(json.load(file))

    class_ls = [1, 3, 4, 5, 6, 7, 11]
    x_ls = list(data.keys())
    # x_tick = [int(name[5:7]) for name in x_ls]
    x_tick = [x_ls[0]]
    temp = x_ls[0][:4]
    for name in x_ls[1:]:
        if name[:4] != temp:
            x_tick.append(name)
            temp = name[:4]
        else:
            x_tick.append("")
    if os.path.exists(avg_json) and os.path.exists(count_json):
        with open(avg_json, "r") as file:
            sta_dict = json.load(file)
        with open(count_json, "r") as file:
            sta_dict_2 = json.load(file)
    else:
        sta_dict = {}
        sta_dict_2 = {}
        for i in tqdm.tqdm(class_ls):
            sta_value = []
            sta_value_2 = []
            for _, value in data.items():
                value: dict
                sta_value.append(value[str(i)][0])
                sta_value_2.append(value[str(i)][1])
            sta_dict[i] = sta_value
            sta_dict_2[i] = sta_value_2
        json.dump(sta_dict, open(avg_json, "w"), indent=4)
        json.dump(sta_dict_2, open(count_json, "w"), indent=4)
    return sta_dict, sta_dict_2, x_ls, x_tick


if __name__ == "__main__":
    sta_dict, sta_dict_2, x_ls, x_tick = get_line_data()
    # drawing
    fig, ax = plt.subplots(figsize=(30, 12))
    draw_class_ls = [1, 3, 4, 5, 6, 7, 11]
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
    color_ls = ["#d95012", "#5c7f00", "#55b20c", "#574d00", "#7d8c8d", "#297bba", "#263642", "#d5850b"]
    for i in draw_class_ls:
        data_y = sta_dict[str(i)]
        data_y_smooth = filters.gaussian_filter(data_y, 3)
        data_y_smooth = [abs(num) for num in data_y_smooth]
        ax.plot(x_ls, data_y_smooth, label=class_dict[i], color=color_ls[draw_class_ls.index(i)], linewidth=2)
    ax.legend(fontsize="xx-large")
    ax.set_xticks(x_ls)
    ax.set_xticklabels(x_tick)
    ax: plt.Axes
    ax.tick_params(axis='x', rotation=0, labelsize=15)
    ax.tick_params(axis='y', labelsize=20)
    out_path = r"./NPY_files/line_pic.png"
    plt.savefig(out_path)
