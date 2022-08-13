import re

boons_info = {}
aspects_info = {}
rarities = {'common': 1, 'rare': 2, 'epic': 3, 'heroic': 4}
rarity_graph_colors = ['#7D7D7D', '#0083F3', '#9500F6', '#FF1C10', '#FFD511']
rarity_embed_colors = [0xFFFFFF, 0x0083F3, 0x9500F6, 0xFF1C10, 0xFFD511, 0xD1FF18, 0x8FFF18]

god_cores = {'zeus': {}, 'poseidon': {}, 'athena': {}, 'aphrodite': {}, 'artemis': {},
             'ares': {}, 'dionysus': {}, 'demeter': {}, 'hermes': {}, 'duos': None}
core_aliases = {}
misc_aliases = {}
aspect_aliases = {}

for god in god_cores.keys():
    f = open(f'files/{god}.txt', 'r', encoding='utf8')
    while boon := f.readline().strip():
        type, boon = boon.split(' ', 1)
        if type in ['attack', 'special', 'cast', 'flare', 'dash', 'call', 'status', 'revenge', 'legendary']:
            god_cores[god][type] = boon
        boons_info[boon] = {'type': type, 'desc': f.readline().strip(), 'stat': f.readline().strip(),
                            'rarities': f.readline().strip().split(' '), 'levels': f.readline().strip().split(' '),
                            'icon': f.readline().strip()}

f = open(f'files/aspects.txt', 'r', encoding='utf8')
while aspect := f.readline().strip():
    aspects_info[aspect] = {'desc': f.readline().strip(), 'stat': f.readline().strip(),
                            'levels': f.readline().strip().split(' '), 'flavor': f.readline().strip(),
                            'icon': f.readline().strip()}

f = open('files/corealiases.txt', 'r', encoding='utf8')
while name := f.readline().strip():
    aliases = f.readline().strip().split(', ')
    if aliases[0]:
        for alias in aliases:
            if alias in core_aliases:
                print(f'duplicate alias: {alias}')
            core_aliases[alias] = name

f = open('files/boonaliases.txt', 'r', encoding='utf8')
while name := f.readline().strip():
    aliases = f.readline().strip().split(', ')
    if aliases[0]:
        for alias in aliases:
            if alias in misc_aliases:
                print(f'duplicate alias: {alias}')
            misc_aliases[alias] = name

f = open('files/aspectaliases.txt', 'r', encoding='utf8')
while name := f.readline().strip():
    aliases = f.readline().strip().split(', ')
    if aliases[0]:
        for alias in aliases:
            if alias in aspect_aliases:
                print(f'duplicate alias: {alias}')
            aspect_aliases[alias] = name


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
    boon_name = fuzzy_boon(input)
    return boon_name, rarity, level


def parse_aspect(input: [str]) -> (str, int):
    input = [s.lower() for s in input]
    level = 5
    if input[len(input) - 1].isdigit():
        level = int(input[len(input) - 1])
        input = input[0: len(input) - 1]
    aspect_name = ' '.join(input)
    if aspect_name in aspects_info:
        return aspect_name, level
    if aspect_name in aspect_aliases and aspect_aliases[aspect_name] in aspects_info:
        return aspect_aliases[aspect_name], level
    return '', level


def fuzzy_boon(input: [str]) -> str:
    boon_name = ' '.join(input)
    if boon_name in boons_info:
        return boon_name
    if boon_name in misc_aliases and misc_aliases[boon_name] in boons_info:
        return misc_aliases[boon_name]
    for index, word in enumerate(input):
        if word in core_aliases:
            input[index] = core_aliases[word]
    if len(input) >= 2:
        if input[0] in god_cores.keys() and input[1] in god_cores[input[0]].keys():
            return god_cores[input[0]][input[1]]
        if input[1] in god_cores.keys() and input[0] in god_cores[input[1]].keys():
            return god_cores[input[1]][input[0]]
    if ' '.join(input) in boons_info:
        return ' '.join(input)
    return ''


def adjust_boon_type(info: {}, boon_name: str, rarity: str, level: int) -> (str, str, int):
    if info['type'] in ['legendary', 'duo']:
        output = f'**{info["type"].upper()}** {boon_name.upper()}\n'
        rarity = 'common'
        level = 1
    else:
        if len(info['rarities']) == 3 and rarity == 'heroic':
            rarity = 'epic'
        if info['levels'][0] == '0':
            output = f'**{rarity.upper()}** {boon_name.upper()}\n'
            level = 1
        else:
            output = f'**{rarity.upper()}** {boon_name.upper()} LV.{level}\n'
    return output, rarity, level


def parse_stat(stat_line: str, value: [float]) -> str:
    try:
        replace = re.findall(r'{.*}', stat_line)[0]
    except IndexError:
        return stat_line
    rounded = 's' not in replace and 'x' not in replace
    if len(value) == 2:
        value = f'{int(value[0] + 0.5)} - {int(value[1] + 0.5)}' if rounded \
            else f'{round(value[0], 2)} - {round(value[1], 2)}'
    else:
        value = int(value[0] + 0.5) if rounded else round(value[0], 2)
    if '+' in replace:
        value = f'+{value}'
    if '-' in replace:
        value = f'-{value}'
    if '%' in replace:
        value = f'{value}%'
    if 's' in replace:
        value = f'{value} Sec.'
    if 'x' in replace:
        value = f'{value}x'
    stat = re.sub(r'{.*}', f'**{value}**', stat_line)
    return stat
