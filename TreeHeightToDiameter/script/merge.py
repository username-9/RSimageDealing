import os

from UtilitiesForDealingImage.UtilityFunction import merge_tiff_files


if __name__ == '__main__':
    try:
        os.chdir(r"C:\Users\PZH\Desktop\江苏项目\数据处理\cal_output")
    except Exception as e:
        print(e)
    file_list = os.listdir()
    for i in file_list:
        if not i.endswith(".tif"):
            file_list.remove(i)
    output_file = r"..\output_cal_raster.tif"
    merge_tiff_files(file_list, output_file)
