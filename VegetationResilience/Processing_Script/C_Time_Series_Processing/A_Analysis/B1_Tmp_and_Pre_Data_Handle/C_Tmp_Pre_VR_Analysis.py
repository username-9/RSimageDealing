import json
import os

import tqdm
from sklearn.metrics import r2_score

from VegetationResilience.Processing_Script.C_Time_Series_Processing.A_Analysis.B1_Tmp_and_Pre_Data_Handle.B_Get_Sta_Data import \
    get_dict_data
from scipy.stats import spearmanr

from VegetationResilience.Processing_Script.C_Time_Series_Processing.A_Analysis.B1_Tmp_and_Pre_Data_Handle.F_scatter import \
    scatter

if __name__ == "__main__":
    one_json = "../F_Analysis_JSON/C4_OUTPUT_S_LUCC_PRE_DATA.json"
    two_json = "../F_Analysis_JSON/C3_OUTPUT_S_LUCC_PRE_COUNT.json"
    file_json = r"/VegetationResilience/Processing_Script/C_Time_Series_Processing\Analysis\Analysis_JSON\A_OUTPUT_S_LUCC_STA_1010.json"
    vr_json = r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Drawing\NPY_files\OUTPUT_STA_AVG_LS_1010.json"
    with open(vr_json, "r") as f:
        vr_sta_dict = json.load(f)
    tmp_sta_dict, _, _, _= get_dict_data(one_json, two_json, file_json)
    for key, value in tqdm.tqdm(vr_sta_dict.items()):
        y = value
        x = tmp_sta_dict[key][len(tmp_sta_dict[key]) - len(y):]
        corr, p_value = spearmanr(x, y)
        filename = f"{key}_Pre_scatter.png"
        filedir = r"F:\DATA\DRAW\PIC\2_TACS_TMP_PRE_RELATION"
        scatter(x, y, ee=2, file_name=filename, r_2=corr, rmse=p_value, file_dir=filedir)