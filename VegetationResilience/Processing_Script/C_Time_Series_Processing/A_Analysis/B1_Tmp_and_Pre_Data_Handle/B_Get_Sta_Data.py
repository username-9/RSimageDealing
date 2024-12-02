import json
import os

import tqdm


def get_dict_data(avg_json, count_json, file_path):
    # get data
    sta_dict: dict = {}
    sta_dict_2 = None
    json_file = file_path
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
            sta_dict[i] = [sta/10 for sta in sta_value] # tmp / 10
            sta_dict_2[i] = sta_value_2
        json.dump(sta_dict, open(avg_json, "w"), indent=4)
        json.dump(sta_dict_2, open(count_json, "w"), indent=4)
    return sta_dict, sta_dict_2, x_ls, x_tick

if __name__ == '__main__':
    one_json = "../F_Analysis_JSON/C2_OUTPUT_S_LUCC_TMP_DATA.json"
    two_json = "../F_Analysis_JSON/C1_OUTPUT_S_LUCC_TMP_COUNT.json"
    file_json = (r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script\Time_Series_Processing\Analysis\Analysis_JSON\B1_OUTPUT_S_LUCC_Tmp_1010.json")
    get_dict_data(one_json, two_json, file_json)