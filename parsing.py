import re

import files
import misc

rarities = {'common': 1, 'rare': 2, 'epic': 3, 'heroic': 4, 'legendary': 5}


def parse_boon(input: [str]) -> (str, str, int):
    if not input:
        return '', '', -1
    input = [s.lower() for s in input]
    rarity = 'common'
    level = 1
    if input[-1].startswith('level') or input[-1].startswith('lvl') or \
            input[-1].startswith('lv') or input[-1].startswith('lv.'):
        input[-1] = ''.join(c for c in input[-1] if c.isdigit())
    if input[-1].isdigit():
        level = int(input[-1])
        input = input[:-1]
        if input and input[-1] in ('level', 'lvl', 'lv', 'lv.'):
            input = input[:-1]
    if input and input[-1] in ('common', 'rare', 'epic', 'heroic'):
        rarity = input[-1]
        input = input[:-1]
    boon_name = misc.fuzzy_boon(input)
    return boon_name, rarity, level


def parse_aspect(input: [str]) -> (str, int):
    input = [s.lower() for s in input]
    level = 5
    if input[-1].isdigit():
        level = int(input[-1])
        input = input[:-1]
    aspect_name = ' '.join(input)
    if aspect_name in files.aspects_info:
        return [aspect_name], level
    if aspect_name in files.aliases['aspect']:
        return files.aliases['aspect'][aspect_name], level
    return '', level


def parse_hammer(input: [str]) -> (str, bool, bool):
    if not input:
        return '', False
    input = [s.lower() for s in input]
    hammer_name = ' '.join(input)
    if hammer_name in files.aliases['hammer']:
        hammer_name = files.aliases['hammer'][hammer_name]
        if len(hammer_name) > 1:
            return hammer_name, False, False
        hammer_name = hammer_name[0]
    if hammer_name in misc.weapon_icons:
        return [hammer_name], True, False
    if hammer_name in files.hammers_info:
        return [hammer_name], False, False
    if parse_aspect(input)[0]:
        return parse_aspect(input)[0], True, True
    return '', False, False


def parse_god(input: [str]) -> str:
    input = [s.lower() for s in input]
    god_name = ' '.join(input)
    if god_name in files.god_cores:
        return god_name
    if god_name in files.aliases['core'] and files.aliases['core'][god_name][0] in files.god_cores:
        return files.aliases['core'][god_name][0]
    return ''


def parse_keepsake(input: [str]) -> (str, int, bool):
    input = [s.lower() for s in input]
    rank = 3
    if input[-1].isdigit():
        rank = int(input[-1])
        input = input[:-1]
    keepsake_name = ' '.join(input)
    if keepsake_name in files.aliases['keepsake']:
        keepsake_name = files.aliases['keepsake'][keepsake_name]
        if len(keepsake_name) > 1:
            return keepsake_name, -1
        keepsake_name = keepsake_name[0]
    if keepsake_name in files.keepsakes_info:
        return [keepsake_name], rank
    return '', rank


def parse_enemy(input: [str]) -> str:
    input = [s.lower() for s in input]
    enemy_name = ' '.join(input)
    if enemy_name in files.enemies_info:
        return enemy_name
    return ''


def parse_stat(stat_line: str, value: [float], rounded=True) -> str:
    try:
        replace = re.findall(r'{.*}', stat_line)[0]
    except IndexError:
        return f'\n▸{stat_line}' if stat_line else ''
    rounded = rounded and 's' not in replace and 'x' not in replace
    round_by = 0 if rounded else 1
    if len(value) == 2:
        v1 = round(value[0], round_by)
        if int(v1) == v1:
            v1 = int(v1)
        v2 = round(value[1], round_by)
        if int(v2) == v2:
            v2 = int(v2)
        value = f'{v1} - {v2}'
    else:
        value = round(value[0], round_by)
        if int(value) == value:
            value = int(value)
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
    if 'e' in replace:
        value = f'{value} Encounters'
    if 'c' in replace:
        value = f'{value} Chambers'
    if 'm' in replace:
        value = f'{value}<:Magick:1241635310387990568>'
    stat = re.sub(r'{.*}', f'**{value}**', stat_line)
    return f'\n▸ {stat}'


def parse_prereqs(prereqs: [(str, [str])]) -> [[str]]:
    parsed_prereqs = []
    for category in prereqs:
        parsed_category = []
        if category[0] == 'x':
            parsed_category.append('Incompatible with:')
        elif category[0] == 'm':
            parsed_category.append(f'{category[1][0]} Active')
            parsed_prereqs.append(parsed_category)
            continue
        elif len(category[1]) == 1:
            parsed_category.append('The Following:')
        else:
            parsed_category.append(f'{"One" if category[0] == "1" else "Two"} of the Following:')
        for boon in category[1]:
            parsed_category.append(boon)
        parsed_prereqs.append(parsed_category)
    return parsed_prereqs


def parse_modifiers(input: [str]) -> [str]:
    input_str = ' '.join(input).lower()
    output = []
    while True:
        h = []
        for modifier in files.aliases['modifier']:
            if modifier in input_str:
                h.append(modifier)
        if not h:
            break
        next_modifier = max(h, key=lambda x: x.count(' '))
        input_str = input_str.replace(next_modifier, '', 1)
        alias = files.aliases['modifier'][next_modifier][0]
        if alias == 'chaos favor' or alias not in output:
            output.append(alias)
    return output


def parse_rarity_table(input: [str], rolls: [int]) -> (str, str):
    title = 'Rarity success rates with the following:\n- '
    title += '\n- '.join([misc.capwords(s) for s in input])
    output = f'+---------------+------+\n' \
             f'| Legendary/Duo | {rolls[0]:>3}% |\n' \
             f'+---------------+------+\n' \
             f'| Epic          | {rolls[1]:>3}% |\n' \
             f'+---------------+------+\n' \
             f'| Rare          | {rolls[2]:>3}% |\n' \
             f'+---------------+------+\n' \
             f'| Common        | 100% |\n' \
             f'+---------------+------+'
    return f'{title}```\n{output}```'
