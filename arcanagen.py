from PIL import Image

import files


def arcana_gen(args: [str]) -> int:
    if ' '.join(args) in files.global_arcana['arcana']:
        bitstring = files.global_arcana['arcana'][' '.join(args)]
        args = [i for i in range(1, 26) if bitstring[i - 1] == '1']
    else:
        args = list(map(int, args))

    base = Image.open('./files/arcana/base.png')
    total_grasp = 0

    for i in range(1, 26):
        if i in args:
            x = 0 if i % 5 == 1 else ((i - 1) % 5) * 148 + 6
            y = 0 if i <= 5 else (i - 1) // 5 * 190 + 3
            base.paste(Image.open(f'./files/arcana/{i}.png'), (x, y))
            total_grasp += list(files.arcana_info.values())[i - 1]['grasp']
    base.save('./temp.png')
    return total_grasp
