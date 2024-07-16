from UtilitiesForDealingImage import ImageBlock


if __name__ == "__main__":
    image_path = r""
    image_block = ImageBlock.ImageBlock(image_path, 1000, 1000)
    region_list = image_block.block_region()