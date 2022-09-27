import random
import re

import discord

import files
import misc

rarities = {'common': 1, 'rare': 2, 'epic': 3, 'heroic': 4, 'legendary': 5}


def parse_boon(input: [str]) -> (str, str, int):
    if not input:
        return '', '', -1
    input = [s.lower() for s in input]
    rarity = 'common'
    level = 1
    if input[-1].isdigit():
        level = int(input[-1])
        input = input[:-1]
    if input[-1] in ('common', 'rare', 'epic', 'heroic'):
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
        return aspect_name, level
    if aspect_name in files.aliases['aspect']:
        return files.aliases['aspect'][aspect_name], level
    return '', level


def parse_hammer(input: [str]) -> (str, bool, bool):
    if not input:
        return '', False, False
    input = [s.lower() for s in input]
    hammer_name = ' '.join(input)
    if hammer_name in files.aliases['hammer']:
        hammer_name = files.aliases['hammer'][hammer_name]
    if hammer_name in misc.weapon_icons:
        return hammer_name, True, False
    if hammer_name in files.hammers_info:
        return hammer_name, False, False
    if parse_aspect(input)[0]:
        return parse_aspect(input)[0], True, True
    return '', False, False


def parse_god(input: [str]) -> str:
    input = [s.lower() for s in input]
    god_name = ' '.join(input)
    if god_name in files.god_cores or god_name == 'bouldy':
        return god_name
    if god_name in files.aliases['core'] and files.aliases['core'][god_name] in (*files.god_cores, 'bouldy'):
        return files.aliases['core'][god_name]
    return ''


def parse_keepsake(input: []) -> (str, int):
    input = [s.lower() for s in input]
    rank = 3
    if input[-1].isdigit():
        rank = int(input[-1])
        input = input[:-1]
    keepsake_name = ' '.join(input)
    if keepsake_name in files.keepsakes_info:
        return keepsake_name, rank
    if keepsake_name in files.aliases['keepsake']:
        return files.aliases['keepsake'][keepsake_name], rank
    return '', rank


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
    if 'e' in replace:
        value = f'{value} Encounters'
    if 'c' in replace:
        value = f'{value} Chambers'
    stat = re.sub(r'{.*}', f'**{value}**', stat_line)
    return stat


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


def parse_random_chaos(blessings: [str], curses: [str], *args) -> discord.embeds.Embed:
    rarity_rolls = misc.rarity_rolls(*args)
    if random.random() < rarity_rolls[0]:
        bless = 'defiance'
        rarity = 'common'
    else:
        bless = random.choice(blessings)
        if random.random() < rarity_rolls[1]:
            rarity = 'epic'
        elif random.random() < rarity_rolls[2]:
            rarity = 'rare'
        else:
            rarity = 'common'
    curse = random.choice(curses)
    bless_info = files.boons_info[bless]
    bless_value = misc.boon_value(bless_info, rarity)
    if len(bless_value) == 2:
        bless_value = [random.randint(*[int(v) for v in bless_value])]
    curse_info = files.boons_info[curse]
    curse_value = misc.boon_value(curse_info, 'common')
    if len(curse_value) == 2:
        curse_value = [random.randint(*curse_value)]
    if curse == 'enshrouded':
        duration = f'**{random.choice((4, 5))} Chambers**'
    elif curse == 'roiling':
        duration = f'**{random.choice((3, 4))}** standard **Encounters**'
    else:
        duration = f'**{random.choice((3, 4))} Encounters**'
    bless_desc = parse_stat(bless_info['desc'][0].lower() + bless_info['desc'][1:], bless_value)
    curse_desc = parse_stat(curse_info['desc'][0].lower() + curse_info['desc'][1:], curse_value)
    embed = discord.Embed(
        title=f'**{misc.capwords(curse + " " + bless)}**',
        description=f'For the next {duration}, {curse_desc}\nAfterward, {bless_desc}',
        color=0xFFD511 if bless_info['type'] == 'legendary' else misc.rarity_embed_colors[rarities[rarity] - 1]
    )
    embed.set_thumbnail(url=bless_info['icon'])
    return embed


def parse_modifiers(input: [str]) -> [str]:
    input_str = ' '.join(input)
    output = []
    while True:
        h = []
        for modifier in files.aliases['modifier']:
            if modifier in input_str:
                h.append(modifier)
        if not h:
            break
        next_modifier = max(h, key=lambda x: x.count(' '))
        output.append(files.aliases['modifier'][next_modifier])
        input_str = input_str.replace(next_modifier, '', 1)
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
