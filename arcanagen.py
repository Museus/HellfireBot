from PIL import Image


def arcana_gen(input: [str]) -> int:
    input = list(map(int, input))
    base = Image.open('./files/arcana/base.png')

    for i in range(1, 26):
        if i in input:
            x = 0 if i % 5 == 1 else ((i - 1) % 5) * 148 + 6
            y = 0 if i <= 5 else (i - 1) // 5 * 190 + 3
            base.paste(Image.open(f'./files/arcana/{i}.png'), (x, y))

    base.save('./temp.png')
