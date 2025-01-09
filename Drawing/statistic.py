import multiprocessing
from multiprocessing import Pool

from tqdm import tqdm

from UtilitiesForProcessingImage.BasicUtility.ReadMain import raster_read

from UtilitiesForProcessingImage.BasicUtility import ImageBlock


def drawing_by_block(dataset_1, dataset_2, location):
    print(f"running on {multiprocessing.current_process().pid}")
    print(location)
    op_x, op_y, x_size, y_size = location

    dataset_1 = raster_read(dataset_1)
    dataset_2 = raster_read(dataset_2)

    factor_1_arr = dataset_1.ReadAsArray(op_x, op_y, x_size, y_size)
    factor_2_arr = dataset_2.ReadAsArray(op_x, op_y, x_size, y_size)

    del dataset_1
    del dataset_2

    q1 = 0
    q2 = 0
    q3 = 0
    q4 = 0
    for i in range(factor_1_arr.shape[0]):
        for j in range(factor_1_arr.shape[1]):
            x_loc = None
            y_loc = None
            if 1 < factor_1_arr[i, j] <= 300:
                x_loc = 1
            if factor_1_arr[i, j] > 300:
                x_loc = 2
            if 0 <= factor_2_arr[i, j] <= 10:
                y_loc = 1
            if factor_2_arr[i, j] > 10:
                y_loc = 2
            if x_loc is not None and y_loc is not None:
                if (1, 1) == (x_loc, y_loc):
                    q2 += 1
                if (2, 1) == (x_loc, y_loc):
                    q1 += 1
                if (1, 2) == (x_loc, y_loc):
                    q3 += 1
                if (2, 2) == (x_loc, y_loc):
                    q4 += 1
    return q1, q2, q3, q4


if __name__ == "__main__":
    raster_1 = r"D:\Drawing\2018_unframents.tif"
    raster_2 = r"D:\Drawing\2018_USMpop.tif"
    # raster_1 = r"C:\Users\PZH\Desktop\drawing\MEM\2007_unfragments_sin_1Lha_1_origin.tif"
    # raster_2 = r"C:\Users\PZH\Desktop\drawing\MEM\2007_BTH_USMpop_raster_origin.tif"
    ds_1 = raster_read(raster_1)

    region_list = ImageBlock.ImageBlock(raster_1, 3000, 3000).get_blocks_region()
    region_list_1 = [[raster_1, raster_2, item] for item in region_list]
    del region_list

    with Pool(processes=10) as pool:
        results = pool.starmap(drawing_by_block, region_list_1)

    del ds_1

    sum_q1 = 0
    sum_q2 = 0
    sum_q3 = 0
    sum_q4 = 0

    for result in tqdm(results):
        q1, q2, q3, q4 = result
        sum_q1 += q1
        sum_q2 += q2
        sum_q3 += q3
        sum_q4 += q4

    sum_q1 = sum_q1*100
    sum_q2 = sum_q2*100
    sum_q3 = sum_q3*100
    sum_q4 = sum_q4*100

    print(f"Q1: {sum_q1}\nQ2: {sum_q2}\nQ3: {sum_q3}\nQ4: {sum_q4}")
