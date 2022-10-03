from random import random
from PIL import Image

import files

pixel_offsets = [0, 40, 74, 108, 149, 187, 224, 263, 299, 338, 374, 413, 447]
green = Image.open('./files/mirrors/green.png')


def random_mirror(id: str, input: str) -> None:
    base = Image.open('./files/mirrors/red.png')
    if id in files.personal and input in files.personal[id]['mirrors']:
        for i, flip in enumerate(files.personal[id]['mirrors'][input]):
            if flip == '1':
                base.paste(green.crop((0, pixel_offsets[i], 397, pixel_offsets[i + 1])), (0, pixel_offsets[i]))
    elif len(input) == 12 and all(c in '01' for c in input):
        for i, flip in enumerate(input):
            if flip == '1':
                base.paste(green.crop((0, pixel_offsets[i], 397, pixel_offsets[i + 1])), (0, pixel_offsets[i]))
    else:
        for i in range(1, len(pixel_offsets)):
            if random() < 0.5:
                base.paste(green.crop((0, pixel_offsets[i - 1], 397, pixel_offsets[i])), (0, pixel_offsets[i - 1]))
    base.save('temp.png')
