import json
from cProfile import label

import matplotlib.pyplot as plt
import numpy as np
from numba import int64

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(20, 20))
    fig: plt.Figure
    ax: plt.Axes

    # load data
    with open(
            r"/VegetationResilience/Processing_Script/Time_Series_Processing/Anlysis/Analysis_JSON\COUNT_TAC_BIGGER_0P6.json",
              'r') as f:
        data_dict = json.load(f)
    bigger_p_seven = data_dict[">0.7"]
    bigger_p_six = data_dict["0.6-0.7"]
    small_p_six = data_dict["<0.6"]
    pop_list = ["2", "8", "6"]
    bigger_p_seven = {k: v for k, v in bigger_p_seven.items() if k not in pop_list}
    bigger_p_six = {k: v for k, v in bigger_p_six.items() if k not in pop_list}
    small_p_six = {k: v for k, v in small_p_six.items() if k not in pop_list}
    bigger_p_six_ls = np.array(list(bigger_p_six.values())).astype(np.int64)
    bigger_p_six_ls = bigger_p_six_ls * 500 * 500 / 10000000000
    small_p_six_ls = np.array(list(small_p_six.values())).astype(np.int64)
    small_p_six_ls = small_p_six_ls * 500 * 500 / 10000000000
    bigger_p_seven_ls = np.array(list(bigger_p_seven.values())).astype(np.int64)
    bigger_p_seven_ls = bigger_p_seven_ls * 500 * 500 / 10000000000
    print(bigger_p_six_ls, small_p_six_ls)
    x = np.arange(len(bigger_p_six_ls))
    labels = ["ENF", "DNF", "DBF", "Grass", "Shrub", "MF"]
    ax.bar(x, small_p_six_ls, label="TAC$<$0.6", fc="#16a085", tick_label=labels)
    ax.bar(x, bigger_p_six_ls, bottom=small_p_six_ls, label=r"0.6$\geq$TAC$<$0.7", fc="#e67e22")
    ax.bar(x, bigger_p_seven_ls, bottom=small_p_six_ls+bigger_p_six_ls, label=r"TAC$\geq$0.7", fc="#c0392b")
    ax.legend(fontsize=30)
    ax.tick_params(labelsize=50)
    plt.show()
    fig.savefig(r"F:\DATA\DRAW\PIC\1_NPP_TAC_ANLYSIS\bar.png")