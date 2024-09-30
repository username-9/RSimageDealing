import os
from multiprocessing import Pool

from tqdm import tqdm

from UtilitiesForProcessingImage.ImageProcessing import image_mosaic


def para_cal(file_ls):
    output_path = r"F:\DATA\LAI\LAI_MOSAICA"
    output_filepath = os.path.join(output_path, f"{file_ls[0][10:17]}.tif")
    image_mosaic(file_ls, output_filepath)


if __name__ == "__main__":
    # env. building
    os.chdir(r"E:\DATA-PENG\LAI_TIFF_ADD")
    file_list = os.listdir()
    file_list_check = file_list.copy()

    # Check  whether the file list is divisible by 4
    # Even though , there also may be error in calculation
    # Make sure, they four are in a group
    for i in range(len(file_list_check)):
        # get the same term in the file name to split group
        file_list_check[i] = file_list_check[i][:17]
    _set = set(file_list_check)
    _dict = {}
    for item in _set:
        _dict.update({item: file_list_check.count(item)})
    dict_new = {}
    del file_list_check
    for key, value in _dict.items():
        if value != 4:
            dict_new[key] = value
    if dict_new != {}:
        sorted_dict = sorted(dict_new.items(), key=lambda x: x[0])
        print(sorted_dict)
        raise ValueError
    else:
        print("num of file list is divisible by 4, but any problem may occur for many reasons. Just be cautious")

    # mosaic
    output_path = r"F:\DATA\LAI\LAI_MOSAICA"
    if os.path.exists(output_path):
        pass
    else:
        os.mkdir(output_path)
    for file in file_list:
        if file.endswith(".tif") is not True:
            file_list.remove(file)
    # for i in tqdm(range(0, int(len(file_list)), 4), position=0, leave=True):
    #     if file_list[i].endswith(".tif"):
    #         deal_list = file_list[i:i + 4]
    #         output_filepath = os.path.join(output_path, f"{file_list[i][10:17]}.tif")
    #         image_mosaic(deal_list, output_filepath)

    # parallel running
    group_ls = []
    for i in (range(0, int(len(file_list)), 4)):
        if file_list[i].endswith(".tif"):
            deal_list = file_list[i:i + 4]
            group_ls.append(deal_list)

    with Pool(processes=10) as pool:
        pool.map(para_cal, group_ls)
