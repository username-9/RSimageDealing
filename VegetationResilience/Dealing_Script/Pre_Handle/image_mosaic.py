import os

from UtilitiesForDealingImage.ImageProcessing import image_mosaic

if __name__ == "__main__":
    pass
    # mosaic
    # os.chdir(r"C:\Users\PZH\Desktop\output_tif")
    # file_list = os.listdir()
    # if os.path.exists(r"..\output_tif"):
    #     pass
    # else:
    #     os.mkdir(r"..\output_tif")
    # for file in file_list:
    #     if file.endswith(".tif") is not True:
    #         file_list.remove(file)
    # for i in range(0, int(len(file_list)), 4):
    #     if file_list[i].endswith(".tif"):
    #         deal_list = file_list[i:i + 4]
    #         output_filepath = os.path.join("..\\output", f"{file_list[i][12:16]}.tif")
    #         image_mosaic(deal_list, output_filepath)
