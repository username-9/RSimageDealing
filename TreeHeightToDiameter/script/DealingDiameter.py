from osgeo import ogr

from TreeHeightToDiameter.script import TreeFunction
from TreeHeightToDiameter.script.TreeFunction import find_carbon_coefficient, get_co_table
from UtilitiesForProcessingImage.ReadMain import vector_read
from UtilitiesForProcessingImage.VectorProcess import find_attribution

if __name__ == '__main__':
    trees = {
        (180000, 190000, 220000, 260000, 261000, 262000, 290000): TreeFunction.SongLei,
        (310000, 320000, 330000, 340000, 350000, 360000, 390000): TreeFunction.ShanLei,
        # (410000, 711000, 801000, 710000, 804000, 580000, 480000, 490000, 620000, 819000, 849000): TreeFunction.LiLei,
        (530000, 535000, 540000, 761000, 590000, 630000): TreeFunction.YangShu,
        (440000, 410000, 711000, 801000, 710000, 804000, 580000,
         480000, 490000, 620000, 819000, 849000): TreeFunction.ZhangShu,
        # (350000, ): TreeFunction.BaiLei,
        (701000, 702000, 703000, 704000, 705000, 706000, 707000,
         709000, 749000, 769000, 755000, 799000): TreeFunction.GuoShuLei
    }
    file_path = r"C:\Users\PZH\Desktop\江苏项目\节点结果\三区单木碳储量-算\tsq_109m_tree.shp"
    datasource = vector_read(file_path, 1)
    # find_condition = f"YOU_SHI_SZ = {i}"
    # layer = find_attribution(datasource, find_condition)
    layer = find_attribution(datasource)
    defn = layer.GetLayerDefn()


    def check_field_exist(field_name_to_check):
        # 遍历图层的字段定义，检查字段是否存在
        field_exists = False
        for i in range(defn.GetFieldCount()):
            field_defn = defn.GetFieldDefn(i)
            if field_defn.GetName() == field_name_to_check:
                field_exists = True
                break
        return field_exists

    xj_field = "xj_0724"
    if not check_field_exist(xj_field):
        print("the field may not exist")
        print(f"create field <{xj_field}>")
        field_name = ogr.FieldDefn(xj_field, ogr.OFTReal)
        if layer.CreateField(field_name) != 0:
            raise Exception(f"Failed to create field {field_name}")
    tcl_field = "tcl_0724"
    if not check_field_exist(tcl_field):
        print("the field may not exist")
        print(f"create field <{tcl_field}>")
        field_name = ogr.FieldDefn(tcl_field, ogr.OFTReal)
        if layer.CreateField(field_name) != 0:
            raise Exception(f"Failed to create field {field_name}")
    feature: ogr.Feature = layer.GetNextFeature()
    index = 0
    co_table = get_co_table(r"C:\Users\PZH\Desktop\江苏项目\数据处理\数据处理参考\江苏三区样地生物量与碳储量.xlsx")
    while feature is not None:
        index += 1
        print(f"feature {index}")
        species = feature.GetField("YOU_SHI_SZ")
        get_height = feature.GetField("Tree_heigh")
        cal_function = None
        co_tuple = None
        for i in trees.keys():
            if eval(species) in i:
                cal_function = trees[i]
                num = eval(str(species)[:4])
                co = find_carbon_coefficient(co_table, num)
                tmp = 0
                while co is None:
                    num = i[tmp]
                    num = eval(str(num)[:4])
                    co = find_carbon_coefficient(co_table, num)
                    tmp += 1
                co_tuple = co
                break
        if cal_function is None:
            print(f"{index} feature -- {species} no matching trees")
        else:
            if get_height is not None:
                tree = cal_function(get_height)
                tree.calculate_dia()
                xj = tree.diameter
                try:
                    feature.SetField(xj_field, xj)
                except Exception as e:
                    print(e)
                if xj is not None:
                    tcl = cal_function.calculate_carbon(tree, co_tuple[0], co_tuple[1],
                                                        co_tuple[2], co_tuple[3], co_tuple[4])
                    try:
                        feature.SetField(tcl_field, tcl)
                    except Exception as e:
                        print(e)
        layer.SetFeature(feature)
        feature = layer.GetNextFeature()
    # feature.Destroy()
    datasource.Destroy()
