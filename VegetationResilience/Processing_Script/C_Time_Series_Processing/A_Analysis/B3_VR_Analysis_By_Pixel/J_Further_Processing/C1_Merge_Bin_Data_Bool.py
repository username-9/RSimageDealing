import json

from tqdm import tqdm

from VegetationResilience.Processing_Script.C_Time_Series_Processing.A_Analysis.B3_VR_Analysis_By_Pixel.C2_Get_VR_Sta_Array_Via_TMP_PRE_Scale_LUCC import \
    merge_dicts_with_lists

if __name__ == "__main__":
    json_path = "RF3_Ref_And_Processing_Files/A_VR_STATISTIC.json"
    with open(json_path, "r") as json_file:
        data = json.load(json_file)
    re_dict = {}
    for _, value_0 in tqdm(data.items()):
        for key, value in value_0.items():
            if not key in re_dict:
                re_dict[key] = value
            else:
                re_dict[key] = merge_dicts_with_lists(re_dict[key], value)

    out_json_path = "RF3_Ref_And_Processing_Files/B_Merge_Bin_Data_LUCC.json"
    with open(out_json_path, "w") as json_file:
        json.dump(re_dict, json_file)