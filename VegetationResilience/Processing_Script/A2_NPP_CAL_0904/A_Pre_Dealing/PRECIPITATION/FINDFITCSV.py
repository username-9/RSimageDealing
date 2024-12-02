import os
import openpyxl


def find_station(space_range: tuple):
    for _file in file_list:
        workbook = openpyxl.load_workbook(_file)
        worksheet = workbook.active


if __name__ == "__main__":
    csv_dir = r""
    os.chdir(csv_dir)
    file_list = os.listdir(csv_dir)
    for file in file_list:
        if not file.endswith(".csv"):
            file_list.remove(file)

    # read CSV and find the fit station
