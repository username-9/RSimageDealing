import matplotlib.pyplot as plt


if __name__ == "__main__":
    # get data
    json_file = r""
    with open(json_file, "r") as file:
        data = dict(json.load(file))

    class_ls = []
    sta_dict = {}
    x_ls = list(data.keys())
    for i in class_ls:
        sta_value = []
        for key, value in data.items():
            sta_value.append(value[i])
        sta_dict[i] = sta_value

    # drawing
    fig, ax = plt.subplots()
    draw_class_ls = []
    for i in draw_class_ls:
        ax.plot(x_ls, sta_dict[i], label=i)
