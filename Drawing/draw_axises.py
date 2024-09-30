import matplotlib.pyplot as plt
import matplotlib.image as mpimg

if __name__ == "__main__":
    # 加载图片
    # 注意：这里假设你已经有一张名为'example.jpg'的图片在你的工作目录中
    img = mpimg.imread(r"F:\DATA\DRAW\PIC\color_map.png")

    # 使用plt.imshow()显示图片
    # 这里不直接使用plt.imshow(img)是因为我们想要对axes有更多的控制
    fig, ax = plt.subplots(figsize=(20, 20))  # 创建一个figure和axes
    ax.imshow(img)  # 在axes上显示图片
    ax: plt.Axes
    # ax.spines['bottom'].set_visible(False)

    # 隐藏坐标轴上的刻度标签（如果你想要保留它们，可以省略这一步）
    # ax.set_xticks([])
    # ax.set_yticks([])

    # 如果你想要添加坐标轴和刻度标签（尽管这通常用于图像分析，而不是简单显示）
    # 你可以这样设置
    x_list: list= [item for item in range(99, img.shape[0]-100, 100)]
    x_list.insert(0, 0)
    x_list.append(1000)

    ax.set_xticks(x_list)  # 假设每100个像素设置一个刻度
    y_list: list = [item for item in range(99, img.shape[0]-100, 100)]
    y_list.insert(0, 0)
    y_list.append(1000)
    ax.set_yticks(y_list)

    labels = ["-0.025", "-0.02", "-0.015", "-0.01", "-0.005", "0", "0.001", "0.005", "0.01", "0.02", "0.03"]
    ax.set_xticklabels(labels)
    y_lable = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    y_lable.reverse()
    ax.set_yticklabels(y_lable)

    ax.tick_params(labelsize=36)
    ax.tick_params(axis='x', pad=20)
    ax.tick_params(axis='y', pad=20)

    # 获取x轴的刻度位置
    xticks = x_list

    # for tick in xticks:
    #     ax.axvline(x=tick, ymin=-0.02, ymax=0.02, color='k', linestyle='-', linewidth=1)

    # for i, tick in enumerate(xticks):
    #     # 计算y位置（这里我们假设在图片顶部的某个固定偏移量）
    #     y_offset = -10  # 这个值可能需要根据你的图片和布局进行调整
    #     ax.text(tick, y_offset, labels[i], horizontalalignment='center', verticalalignment='bottom', fontsize=30,
    #             color='k')

    # ax.twiny()

    # ax.set_xlabel('Ecological green area')
    # ax.set_ylabel('Proportion of urban area')

    # 添加格网
    # ax.grid(True)

    # 显示图片
    fig: plt.Figure
    fig.savefig(r"F:\DATA\DRAW\PIC\1_NPP_TAC_ANLYSIS\ColorMapWithAxies_0919.png")
    # plt.show()
