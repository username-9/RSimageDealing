import os
import pickle
from datetime import datetime

import numpy as np
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from tqdm import tqdm

from UtilitiesForProcessingImage.ReadMain import raster_to_array


if __name__ == "__main__":
    # direction set
    kp_path = (r"C:\Users\PZH\PycharmProjects\RSimageProcessing\VegetationResilience\Processing_Script"
               r"\Time_Series_Processing\Analysis\VR_Analysis_By_Pixel\VR_Sta_Json\E_Key_Point_Array.npy")
    lucc_dir = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0829_archive\LUCC(use)\LUCC_RESAMPLE"
    t_p_v_arr_path = r"F:\DATA\Vegetation_Resilience_D_DATA_C\0903_archive\TIME_SERIES_HANDLE\CONSTRUCT_ARRAY_TMP_PRE_VR_1010"
    single_num = 1
    class_ls = [single_num]
    plt.rcParams['font.sans-serif'] = ['Calibri']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 1000
    X = None
    y = None

    if not (os.path.exists("./Analysis_Json/D1_X.npy") or os.path.exists("./Analysis_Json/D2_y.npy")):
        # parameter define
        X = []
        y = []

        # construct data
        vtp_ls = os.listdir(t_p_v_arr_path)
        vtp_ls = [file for file in vtp_ls if file.endswith(".npy")]

        kp_arr = np.load(kp_path)
        ori_time = datetime(2001, 5, 1)

        for i in tqdm(range(kp_arr.shape[0])):
            lucc_path = os.path.join(lucc_dir, "CLCD_v01_" + str(ori_time.year) + "_albert.tif")
            ori_time = ori_time + relativedelta(months=1)

            lucc_arr = raster_to_array(lucc_path)
            tpv_arr = np.load(os.path.join(t_p_v_arr_path, vtp_ls[i]))

            for class_num in class_ls:
                all_t_data = (tpv_arr[0, :, :] * (1 - kp_arr[i]))[(lucc_arr == class_num)].flatten() / 10
                all_p_data = (tpv_arr[1, :, :] * (1 - kp_arr[i]))[(lucc_arr == class_num)].flatten() / 10
                arr = np.concatenate((all_t_data[:, np.newaxis], all_p_data[:, np.newaxis]), axis=1)
                X.append(arr)
                y.append(np.zeros((arr.shape[0],)))
                all_t_data = (tpv_arr[0, :, :] * kp_arr[i])[(lucc_arr == class_num)].flatten() / 10
                all_p_data = (tpv_arr[1, :, :] * kp_arr[i])[(lucc_arr == class_num)].flatten() / 10
                arr = np.concatenate((all_t_data[:, np.newaxis], all_p_data[:, np.newaxis]), axis=1)
                X.append(arr)
                y.append(np.ones((arr.shape[0],)))

        X = np.concatenate(X, axis=0)
        y = np.concatenate(y, axis=0)
        y = y[np.all(X, axis=1) != 0]
        X = X[np.all(X, axis=1) != 0]

        np.save("./Analysis_Json/D1_X.npy", X)
        np.save("./Analysis_Json/D2_y.npy", y)
    else:
        X = np.load("./Analysis_Json/D1_X.npy")
        y = np.load("./Analysis_Json/D2_y.npy")


    # construct SVM model
    model = SVC(kernel='linear')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.2f}")

    co = model.coef_
    intercept = model.intercept_
    print(f"Coefficients: {co:.2f}")
    print(f"Intercept: {intercept:.2f}")

    with open(f"./Analysis_Json/E_SVMmodel_{single_num}.pkl", "wb") as file:
        pickle.dump(model, file)

