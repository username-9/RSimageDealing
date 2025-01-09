import numpy as np
import tqdm
from numpy.ma.extras import average
from osgeo import ogr


def point_link_to_fish(point_ds, fish_ds, link_field_name: str = "value"):
    point_datasource = point_ds
    fish_datasource = fish_ds

    point_layer = point_datasource.GetLayer()
    fish_layer = fish_datasource.GetLayer()

    field_exist = False
    for i in range(point_layer.GetLayerDefn().GetFieldCount()):
        field_defn = point_layer.GetLayerDefn().GetFieldDefn(i)
        if field_defn.GetName() == link_field_name:
            field_exist = True
            break
    if not field_exist:
        raise ValueError("no specific field exist in point shape")

    try:
        field_defn = ogr.FieldDefn(link_field_name, ogr.OFTReal)
        fish_layer.CreateField(field_defn)
    except Exception as e:
        print(e)

    for point_feature in tqdm.tqdm(point_layer):
        point_geometry = point_feature.GetGeometryRef()
        x, y, z = point_geometry.GetX(), point_geometry.GetY(), point_geometry.GetZ()
        value = eval(point_feature.GetField(link_field_name))

        for grid_feature in fish_layer:

            if grid_feature.GetGeometryRef().Contains(point_geometry):
                try:
                    exist_value = grid_feature.GetField(link_field_name)
                    if exist_value is None:
                        grid_feature.SetField(link_field_name, value)
                    else:
                        value = np.mean([exist_value, value])
                        grid_feature.SetField(link_field_name, value)
                    break
                except Exception as e:
                    print(e)
                    grid_feature.SetField(link_field_name, value)
                    break


if __name__ == "__main__":
    shp_file = r""
    fish_file = r""
    p_ds = ogr.Open(shp_file, 1)
    f_ds = ogr.Open(fish_file, 1)
    point_link_to_fish(p_ds, f_ds, link_field_name="Entropy")
