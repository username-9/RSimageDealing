import os
from datetime import datetime, timedelta
import numpy as np
import tqdm
from dateutil.relativedelta import relativedelta
from numpy import ndarray
from osgeo import ogr, gdal, gdal_array, osr
from tqdm.contrib.logging import tqdm_logging_redirect


def month_of_day_in_year(_year: int, _day: int) -> int:
    """
    get the month of the day in the year
    :param _year: the certain year
    :param _day: the certain day
    :return: the month in where the day is
    """
    # 使用datetime模块创建表示该年第一天的datetime对象
    start_of_year = datetime(_year, 1, 1)
    # 使用timedelta找到表示给定日期的datetime对象
    # 注意：timedelta的days参数需要是整数，但这里day_of_year已经是整数
    target_date = start_of_year + timedelta(days=_day - 1)
    # 返回月份的名称
    return target_date.month


def start_and_end_day_of_month(_year: int, _month: int) -> tuple[int, int] or None:
    """
    get the start and end date of the month in a certain year
    :param _year: the certain year
    :param _month: the certain month
    :return: the start and end date of the month
    """
    # 创建该月第一天的datetime对象
    first_day_of_month = datetime(_year, _month, 1)
    # 获取该月第一天是该年的第几天
    first_day_of_year = first_day_of_month.timetuple().tm_yday

    # 为了找到该月最后一天，我们可以先找到下一个月的第一天，然后减去一天
    # 注意月份是循环的，所以我们需要特别处理12月
    if _month == 12:
        next_month_first_day = datetime(_year + 1, 1, 1)
    else:
        next_month_first_day = datetime(_year, _month + 1, 1)

        # 该月最后一天的datetime对象
    last_day_of_month = next_month_first_day - timedelta(days=1)
    # 获取该月最后一天是该年的第几天
    last_day_of_year = last_day_of_month.timetuple().tm_yday

    return first_day_of_year, last_day_of_year


def integrate_monthly(_file_list: list, str_year_start: int, str_year_end: int,
                      str_day_start: int, str_day_end: int, file_format: str = "GTIFF") -> tuple[dict, dict]:
    """
    #integrate img into one
    #be cautious that the function needs to set year and day from the name of file
    :param file_format: which kind of file in the file list
    :param str_day_end: the index of file name string where the year begin
    :param str_year_end: the index of file name string where the year in end in range()
    :param str_year_start: the index of file name string where the year at begin
    :param str_day_start: the index of file name string where the day in end
    :param _file_list: img file name list
    :return: dict the period containing in the month, and their weights
    """
    # get the iterate index from file list
    integrate_index_dict = {}
    weight_dict = {}
    for file in _file_list:
        if not file.endswith('.tif'):
            raise ValueError from BaseException
    for filename in _file_list:
        year = int(filename[str_year_start:str_year_end])
        day = int(filename[str_day_start:str_day_end])
        month = month_of_day_in_year(year, day)
        year_month_str = str(year) + str(month).zfill(2)
        integrate_index_dict.setdefault(year_month_str, []).append(_file_list.index(filename))
        # get start and end day of the month
        start_day, end_day = start_and_end_day_of_month(year, month)
        # check the period whether in the month and set weight
        # if day != start_day and (day - 8) < start_day:
        #     integrate_index_dict.setdefault(year_month_str, []).insert(0, _file_list.index(filename) - 1)
        #     weight_last = (start_day - (day - 8)) / 8
        #     weight_dict.setdefault(year_month_str, []).insert(0, weight_last)
        #     weight_this = (day - start_day) / 8
        #     weight_dict.setdefault(year_month_str, []).append(weight_this)
        # elif (day - 8 > start_day) and ((end_day - (day + 7)) < end_day):
        #     weight_dict.setdefault(year_month_str, []).append(1)
        # elif (day + 7) > end_day:
        #     weight_this = (end_day - day) / 8
        #     weight_dict.setdefault(year_month_str, []).append(weight_this)
        # else:
        #     weight_dict.setdefault(year_month_str, []).append(1)
        if start_day <= day <= end_day:
            if (_file_list.index(filename) != 0) and (day - 8 < start_day):
                # Handle start of month case
                integrate_index_dict.setdefault(year_month_str, []).insert(0, _file_list.index(filename) - 1)
                weight_this = (day - start_day) / 8
                weight_dict.setdefault(year_month_str, []).append(weight_this)
                weight_dict.setdefault(year_month_str, []).append(1)
            elif day + 7 > end_day:
                # Handle end of month case
                weight_this = (end_day - day + 1) / 8
                weight_dict.setdefault(year_month_str, []).append(weight_this)
            else:
                # Handle mid-month case
                weight_dict.setdefault(year_month_str, []).append(1)
    return integrate_index_dict, weight_dict


def rename_files_by_month(_folder_path: str, start_date: datetime, end_date: datetime):
    # 确保路径是存在的
    if not os.path.exists(_folder_path):
        print(f"The folder {_folder_path} does not exist.")
        return
    # 获取期间月份数
    start_year = start_date.year
    start_month = start_date.month
    end_year = end_date.year
    end_month = end_date.month
    # Calculate the difference in months
    months = (end_year - start_year) * 12 + (end_month - start_month) + 1
    dt = start_date.date()
    # 遍历文件夹中的所有文件
    file_list = os.listdir(_folder_path)
    if len(file_list) == months:
        for filename in file_list:
            file_path = os.path.join(_folder_path, filename)
            # 确保是文件而非文件夹
            if os.path.isfile(file_path):
                # 格式化新的文件名，这里假设不需要处理同一个月内的多个文件
                new_filename = f"{dt.year}-{str(dt.month).zfill(3)}.{filename.split('.')[-1]}"
                new_file_path = os.path.join(_folder_path, new_filename)
                # 重命名文件
                os.rename(file_path, new_file_path)
                print(f"Renamed {filename} to {new_filename}")
            dt += relativedelta(months=1)
    else:
        print("the number of months doesn't match file number")


def check_field_exist(field_name_to_check: str, _layer: ogr.Layer) -> bool:
    """
    check if field exists
    :param field_name_to_check: the field to check
    :param _layer: the layer
    :return: True or False
    """
    # 遍历图层的字段定义，检查字段是否存在
    defn = _layer.GetLayerDefn()
    field_exists = False
    for i in range(defn.GetFieldCount()):
        field_defn = defn.GetFieldDefn(i)
        if field_defn.GetName() == field_name_to_check:
            field_exists = True
            break
    return field_exists


def merge_tiff_files(input_files: list, output_path: str):
    """
    Merge multiple TIFF files by selecting the maximum pixel value for each cell.
    Support 1 band TIFF.

    Parameters:
    - input_files (list): List of input TIFF file paths to merge.
    - output_path (str): Output path for the merged TIFF file.
    """
    # Open the first input file to get the reference information
    first_dataset = gdal.Open(input_files[0], gdal.GA_ReadOnly)
    if first_dataset is None:
        print(f"Failed to open {input_files[0]}")
        return False
    # Get geo_transform, projection, and band information
    geo_transform = first_dataset.GetGeoTransform()
    projection = first_dataset.GetProjection()
    band = first_dataset.GetRasterBand(1)
    # Determine the output data type
    output_datatype = band.DataType
    # Create output dataset
    driver = gdal.GetDriverByName("GTiff")
    if driver is None:
        print("GDAL driver for GTiff (GeoTIFF) is not available.")
        return False
    # Ensure output file has .tif extension
    if not output_path.lower().endswith('.tif'):
        output_path += '.tif'

    output_dataset = driver.Create(output_path,
                                   band.XSize,
                                   band.YSize,
                                   1,  # Single band for output
                                   gdal.GDT_Float32)

    if output_dataset is None:
        print(f"Failed to create output file {output_path}")
        return False

    output_dataset.SetGeoTransform(geo_transform)
    output_dataset.SetProjection(projection)

    # Initialize output array with minimum possible value for datatype
    output_array = np.full((band.YSize, band.XSize), 0,
                           dtype=gdal_array.GDALTypeCodeToNumericTypeCode(output_datatype))
    # Loop through input files and merge by selecting maximum value
    for input_file in input_files:
        input_dataset = gdal.Open(input_file, gdal.GA_ReadOnly)
        if input_dataset is None:
            raise EOFError(f"Failed to open {input_file}")

        input_band = input_dataset.GetRasterBand(1)

        # Read input data as numpy array
        input_array = input_band.ReadAsArray()
        input_array = np.nan_to_num(input_array, nan=0)
        # Update output array to select maximum value for each cell
        output_array = np.maximum(output_array, input_array).copy()

        # Close the input dataset
        input_dataset = None

    # Write output array to output band
    output_band = output_dataset.GetRasterBand(1)
    output_band.WriteArray(output_array, 0, 0)

    # Set nodata value if available
    nodata_value = band.GetNoDataValue()
    if nodata_value is not None:
        output_band.SetNoDataValue(nodata_value)
    del first_dataset

    # Close the output dataset
    output_dataset = None

    print(f"Merged TIFF file saved as {output_path}")
    return True


def fix_vector_error(input_shp, output_shp):
    # 打开原始矢量数据源
    inputDataSource = ogr.Open(input_shp, 0)
    if inputDataSource is None:
        print(f"Failed to open input file: {input_shp}")
        return

    # 获取原始图层
    layer = inputDataSource.GetLayer()

    # 获取原始图层的CRS和字段定义
    srs = layer.GetSpatialRef()
    layer_defn = layer.GetLayerDefn()

    # 创建输出数据源
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(output_shp):
        driver.DeleteDataSource(output_shp)
    outputDataSource = driver.CreateDataSource(output_shp)
    if outputDataSource is None:
        print(f"Failed to create output file: {output_shp}")
        inputDataSource.Destroy()
        return

    # 创建新图层，并设置CRS和字段定义
    outputLayer = outputDataSource.CreateLayer(layer.GetName(), srs, layer_defn.GetGeomType())
    for i in range(layer_defn.GetFieldCount()):
        field_defn = layer_defn.GetFieldDefn(i)
        outputLayer.CreateField(field_defn)

    # 复制特征
    feature = None
    while True:
        feature = layer.GetNextFeature()
        if feature is None:
            break

        geom = feature.GetGeometryRef()
        if not geom.IsValid():
            # 尝试修复几何体
            try_geom = geom.Buffer(0)  # 使用零缓冲尝试修复
            if try_geom.IsValid():
                geom = try_geom

                # 创建新特征并设置几何和字段
        new_feature = ogr.Feature(outputLayer.GetLayerDefn())
        new_feature.SetGeometry(geom)
        for i in range(feature.GetFieldCount()):
            new_feature.SetField(feature.GetFieldDefnRef(i).GetName(), feature.GetField(i))

        # 创建特征到输出图层
        outputLayer.CreateFeature(new_feature)
        new_feature = None

        # 清理资源
    outputDataSource.Destroy()
    inputDataSource.Destroy()
    print("Fix done")


def workdir_filelist(path, file_format: str = ".tif"):
    """
    set work directory and get all files with specific extension
    :param path: work directory
    :param file_format: specific extension
    :return: file list needed
    """
    if os.path.exists(path):
        os.chdir(path)
        files = os.listdir(path)
        files = [file for file in files if file.endswith(".tif")]
        return files
    else:
        raise OSError(f"Path {path} does not exist")


def merge_arrays_with_coords(arrays: ndarray or list[ndarray], coords: tuple[int, int] or list[tuple[int, int]],
                             target_array: ndarray = None) -> ndarray or None:
    """
    合并多个多维NumPy数组，根据提供的左上角坐标放置每个数组。

    :param target_array: 当希望将单个数组嵌入进某个目标数组时，提供目标数组以匹配
    :param coords: (list of tuple tuple): 每个数组的左上角坐标列表，格式为 (y, x)
    :param arrays: (list of ndarray or ndarray), 要合并的数组列表

    :return: ndarray or None 合并后的数组或仅对目标数组进行操作
    """
    # 检查 arrays 是否为列表
    if not isinstance(arrays, list):
        if arrays.ndim != 3:
            raise ValueError("Arrays must have 3 dimensions")
        if target_array is None:
            raise TypeError("target array must be set")
        else:
            if not isinstance(coords, tuple):
                raise TypeError("coords must be a tuple in this way")
            else:
                y = coords[0]
                x = coords[1]
                target_array[:, y:y + arrays.shape[1], x:x + arrays.shape[2]] = arrays
    else:
        # 检查 arrays 列表是否包含 NumPy 数组
        if arrays[0].ndim != 3:
            raise ValueError("Arrays must have 3 dimensions")
        if not all(isinstance(array, np.ndarray) for array in arrays):
            raise TypeError("arrays 列表中的每个元素都必须是 NumPy 数组")
            # 检查 coords 是否为坐标列表
        if not all(isinstance(coord, tuple) and len(coord) == 2 and all(isinstance(c, int) for c in coord) for coord in
                   coords):
            raise TypeError("coords 必须是包含 (y, x) 坐标的元组列表")

            # 检查 arrays 和 coords 的长度是否匹配
        if len(arrays) != len(coords):
            raise ValueError("arrays 和 coords 的长度必须匹配")

        # 获取每个数组的形状，以确定输出数组的总大小
        max_height = max(coord[1] + array.shape[1] for coord, array in zip(coords, arrays))
        max_width = max(coord[2] + array.shape[2] for coord, array in zip(coords, arrays))

        # 创建一个空白数组来容纳所有输入的数组
        merged_array = np.zeros((arrays[0].shape[0], max_height, max_width), dtype=arrays[0].dtype)

        # 使用 scipy.ndimage.paste 将每个数组放置在相应的位置
        for array, (y, x) in zip(arrays, coords):
            merged_array[: y:y + array.shape[1], x:x + array.shape[2]] = array
        return merged_array


def separate_vector(shp_file_path, output_dir, field_for_name, vector_class='ESRI Shapefile', encoding='utf-8'):
    os.environ['SHAPE_ENCODING'] = encoding
    # gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
    # gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")
    ogr.RegisterAll()
    # open vector file
    driver = ogr.GetDriverByName(vector_class)
    datasource = driver.Open(shp_file_path, 0)
    datasource: ogr.DataSource
    if not datasource:
        raise Exception("Failed to open datasource")

    # layer
    layer = datasource.GetLayer()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    used_names = set()

    # iterate features in layer
    for feature in tqdm.tqdm(layer):
        try:
            field_value = feature.GetField(field_for_name)
        except ValueError as e:
            print(f"wrong in get field value")
            raise e
        base_name = field_value if field_value else "unknown"
        name_counter = 0

        output_path = None
        while f"{base_name}_{name_counter}.shp" in used_names:
            name_counter += 1

        used_names.add(f"{base_name}_{name_counter}.shp")

        if name_counter == 0:
            output_path = os.path.join(output_dir, f"{base_name}.shp")
        else:
            output_path = os.path.join(output_dir, f"{base_name}_{name_counter}.shp")
        # create new shp files
        out_driver = ogr.GetDriverByName(vector_class)
        if os.path.exists(output_path):
            out_driver.DeleteDataSource(output_path)
        # out_driver.CreateDataSource(output_path)
        ## get data source
        out_data_source = out_driver.CreateDataSource(output_path)
        # # get spatial reference system
        out_srs = osr.SpatialReference()
        out_srs.ImportFromWkt(layer.GetSpatialRef().ExportToWkt())
        ## get layer waiting for edit
        out_layer = out_data_source.CreateLayer(os.path.basename(output_path).split('.')[0], out_srs,
                                                ogr.wkbPolygon)
        ## get layer
        layer_defn = layer.GetLayerDefn()
        for i in range(layer_defn.GetFieldCount()):
            field_defn = layer_defn.GetFieldDefn(i)
            # if field_defn.GetName() != field_for_name:
            out_layer.CreateField(field_defn)

        ## create output feature
        out_feature = ogr.Feature(out_layer.GetLayerDefn())
        for i in range(layer_defn.GetFieldCount()):
            field_defn = layer_defn.GetFieldDefn(i)
            out_feature.SetField(field_defn.GetName(), feature.GetField(field_defn.GetName()))

        # set geometry
        out_feature.SetGeometry(feature.GetGeometryRef().Clone())

        out_layer.CreateFeature(out_feature)
        out_feature = None

    data_source = None
    out_data_source = None


if __name__ == '__main__':
    # folder_path = r"D:\Data\VegetationResilienceDealing\Integrate_Output\PRE\PRE_BTH_CLIP_OUTPUT"
    # start_data = datetime(2000, 1, 1)
    # end_data = datetime(2021, 12, 31)
    # rename_files_by_month(folder_path, start_data, end_data)
    fix_vector_error(r"C:\Users\PZH\Desktop\res_tcl_data\矢量\大丰林地一张图_select01_pro120_select_all_yssz_dis.shp",
                     r"C:\Users\PZH\Desktop\res_tcl_data\矢量\fix.shp")
