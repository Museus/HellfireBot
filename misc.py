import re

rarities = {'common': 1, 'rare': 2, 'epic': 3, 'heroic': 4}


def parse_boon(input: [str]) -> (str, str, int):
    input = [s.lower() for s in input]
    rarity = 'common'
    level = 1
    if input[len(input) - 1].isdigit():
        level = int(input[len(input) - 1])
        input = input[0: len(input) - 1]
    if input[len(input) - 1] in rarities.keys():
        rarity = input[len(input) - 1]
        input = input[0: len(input) - 1]
    name = ' '.join(input)
    return name, rarity, level


def adjust_boon_type(info: {}, name: str, rarity: str, level: int) -> (str, str, int):
    if info['type'] in ['legendary', 'duo']:
        output = f'**{info["type"].upper()}** {name.upper()}\n'
        rarity = 'common'
        level = 1
    else:
        if len(info['rarities']) == 3 and rarity == 'heroic':
            rarity = 'epic'
        if info['levels'][0] == '0':
            output = f'**{rarity.upper()}** {name.upper()}\n'
            level = 1
        else:
            output = f'**{rarity.upper()}** {name.upper()} LV.{level}\n'
    return output, rarity, level


def parse_stat(stat_line: str, value: [float]) -> str:
    replace = re.findall(r'{.*}', stat_line)[0]
    rounded = 's' not in replace and 'x' not in replace
    if len(value) == 2:
        value = f'{int(value[0] + 0.5)} - {int(value[1] + 0.5)}' if rounded else f'{value[0]} - {value[1]}'
    else:
        value = int(value[0] + 0.5) if rounded else value[0]
    if '+' in replace:
        value = f'+{value}'
    if '%' in replace:
        value = f'{value}%'
    if 's' in replace:
        value = f'{value} Sec'
    if 'x' in replace:
        value = f'{value}x'
    stat = re.sub(r'{.*}', f'**{value}**', stat_line)
    return stat
