import os

from tqdm import tqdm

from UtilitiesForDealingImage.ImageProcessing import image_mosaic


def para_cal():
    pass


if __name__ == "__main__":
    # env. building
    os.chdir(r"E:\DATA-PENG\GPP_HDF_to_TIFF_OUTPUT")
    file_list = os.listdir()
    file_list_check = file_list.copy()

    # Check  whether the file list is divisible by 4
    # Even though , there also may be error in calculation
    # Make sure, they four are in a group
    for i in range(len(file_list_check)):
        file_list_check[i] = file_list_check[i][11:19]
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
    output_path = r"E:\DATA-PENG\GPP_MOSAIC_OUTPUT"
    if os.path.exists(output_path):
        pass
    else:
        os.mkdir(output_path)
    for file in file_list:
        if file.endswith(".tif") is not True:
            file_list.remove(file)
    for i in tqdm(range(0, int(len(file_list)), 4), position=0, leave=True):
        if file_list[i].endswith(".tif"):
            deal_list = file_list[i:i + 4]
            output_filepath = os.path.join(output_path, f"{file_list[i][11:19]}.tif")
            image_mosaic(deal_list, output_filepath)

