import os

import openpyxl


if __name__ == "__main__":
    work_dir = r""
    os.chdir(work_dir)
    file_list = os.listdir()
    for file in file_list:
        if not file.endswith(".csv"):
            file_list.remove(file)
    for file in file_list:
        workbook = openpyxl.load_workbook(file)
        worksheet = workbook.active


