from random import random
from PIL import Image

pixel_offsets = [0, 40, 74, 108, 149, 187, 224, 263, 299, 338, 374, 413, 447]
opt_mirrors = {
    'speedrun': '100000011101',
    'high heat': '101000001101'
}


def random_mirror(input):
    red = Image.open('./files/mirrors/red.png')
    green = Image.open('./files/mirrors/green.png')
    if input in opt_mirrors:
        for i, flip in enumerate(opt_mirrors[input]):
            if flip == '1':
                red.paste(green.crop((0, pixel_offsets[i], 397, pixel_offsets[i + 1])), (0, pixel_offsets[i]))
    else:
        for i in range(1, len(pixel_offsets)):
            if random() < 0.5:
                red.paste(green.crop((0, pixel_offsets[i - 1], 397, pixel_offsets[i])), (0, pixel_offsets[i - 1]))
    red.save('temp.png')
