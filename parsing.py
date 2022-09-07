import random
import re

import discord

import files
import misc

rarities = {'common': 1, 'rare': 2, 'epic': 3, 'heroic': 4, 'legendary': 5}


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
    boon_name = misc.fuzzy_boon(input)
    return boon_name, rarity, level


def parse_aspect(input: [str]) -> (str, int):
    input = [s.lower() for s in input]
    level = 5
    if input[len(input) - 1].isdigit():
        level = int(input[len(input) - 1])
        input = input[0: len(input) - 1]
    aspect_name = ' '.join(input)
    if aspect_name in files.aspects_info:
        return aspect_name, level
    if aspect_name in files.aspect_aliases and files.aspect_aliases[aspect_name] in files.aspects_info:
        return files.aspect_aliases[aspect_name], level
    return '', level


def parse_hammer(input: [str]) -> (str, bool):
    input = [s.lower() for s in input]
    hammer_name = ' '.join(input)
    if hammer_name in files.hammer_aliases:
        hammer_name = files.hammer_aliases[hammer_name]
    if hammer_name in misc.weapon_icons:
        return hammer_name, True
    if hammer_name in files.hammers_info:
        return hammer_name, False
    return '', False


def parse_god(input: [str]) -> str:
    input = [s.lower() for s in input]
    god_name = ' '.join(input)
    if god_name in files.god_cores or god_name == 'bouldy':
        return god_name
    if god_name in files.core_aliases and files.core_aliases[god_name] in [*files.god_cores, 'bouldy']:
        return files.core_aliases[god_name]
    return ''


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


def parse_random_chaos(blessings: [str], curses: [str], *args) -> (str, str, int):
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
    bless_desc = parse_stat(bless_info["desc"][0].lower() + bless_info["desc"][1:], bless_value)
    curse_desc = parse_stat(curse_info["desc"][0].lower() + curse_info["desc"][1:], curse_value)
    embed = discord.Embed(
        title=f'**{misc.capwords(curse + " " + bless)}**',
        description=f'For the next {duration}, {curse_desc}\nAfterward, {bless_desc}',
        color=(0xFFD511 if bless_info['type'] == 'legendary' else misc.rarity_embed_colors[rarities[rarity] - 1])
    )
    embed.set_thumbnail(url=bless_info['icon'])
    return embed
