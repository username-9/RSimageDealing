import matplotlib.pyplot as plt
import matplotlib.image as mpimg

if __name__ == "__main__":
    # 加载图片
    # 注意：这里假设你已经有一张名为'example.jpg'的图片在你的工作目录中
    img = mpimg.imread(r"C:\Users\PZH\Desktop\drawing\MEM\output\color_map_output_mirror.png")

    # 使用plt.imshow()显示图片
    # 这里不直接使用plt.imshow(img)是因为我们想要对axes有更多的控制
    fig, ax = plt.subplots(figsize=(20, 20))  # 创建一个figure和axes
    ax.imshow(img)  # 在axes上显示图片

    # ax.spines['bottom'].set_visible(False)

    # 隐藏坐标轴上的刻度标签（如果你想要保留它们，可以省略这一步）
    # ax.set_xticks([])
    # ax.set_yticks([])

    # 如果你想要添加坐标轴和刻度标签（尽管这通常用于图像分析，而不是简单显示）
    # 你可以这样设置
    ax.set_xticks(range(99, img.shape[0]-100, 100))  # 假设每100个像素设置一个刻度
    ax.set_yticks(range(99, img.shape[0]-100, 100))

    labels = ["3", "8", "13", "19", "26", "35", "47", "63", "80"]
    # ax.set_xticklabels(labels)
    ax.set_yticklabels([1, 3, 5, 7, 10, 15, 20, 25, 30])

    ax.tick_params(labelsize=50)

    # 获取x轴的刻度位置
    xticks = range(99, img.shape[1]-100, 100)

    # for tick in xticks:
    #     ax.axvline(x=tick, ymin=-0.02, ymax=0.02, color='k', linestyle='-', linewidth=1)

    for i, tick in enumerate(xticks):
        # 计算y位置（这里我们假设在图片顶部的某个固定偏移量）
        y_offset = -10  # 这个值可能需要根据你的图片和布局进行调整
        ax.text(tick, y_offset, labels[i], horizontalalignment='center', verticalalignment='bottom', fontsize=50,
                color='k')

    # ax.twiny()

    # ax.set_xlabel('Ecological green area')
    # ax.set_ylabel('Proportion of urban area')

    # 添加格网
    # ax.grid(True)

    # 显示图片
    plt.show()
