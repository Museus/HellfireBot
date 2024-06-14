import re

import files
import misc

rarities = {'common': 1, 'rare': 2, 'epic': 3, 'heroic': 4, 'legendary': 5}


def parse_boon(args):
    if not args:
        return '', '', -1
    args = [s.lower() for s in args]
    rarity = 'common'
    level = 1
    if args[-1].startswith('level') or args[-1].startswith('lvl') or \
            args[-1].startswith('lv') or args[-1].startswith('lv.'):
        args[-1] = ''.join(c for c in args[-1] if c.isdigit())
    if args[-1].isdigit():
        level = int(args[-1])
        args = args[:-1]
        if args and args[-1] in ('level', 'lvl', 'lv', 'lv.'):
            args = args[:-1]
    if args and args[-1] in ('common', 'rare', 'epic', 'heroic'):
        rarity = args[-1]
        args = args[:-1]
    boon_name = misc.fuzzy_boon(args)
    return boon_name, rarity, level


def parse_aspect(args):
    args = [s.lower() for s in args]
    level = 5
    if args[-1].isdigit():
        level = int(args[-1])
        args = args[:-1]
    aspect_name = ' '.join(args)
    if aspect_name in files.aspects_info:
        return [aspect_name], level
    if aspect_name in files.aliases['aspect']:
        return files.aliases['aspect'][aspect_name], level
    return '', level


def parse_hammer(args):
    if not args:
        return '', False
    args = [s.lower() for s in args]
    hammer_name = ' '.join(args)
    if hammer_name in files.aliases['hammer']:
        hammer_name = files.aliases['hammer'][hammer_name]
        if len(hammer_name) > 1:
            return hammer_name, False, False
        hammer_name = hammer_name[0]
    if hammer_name in misc.weapon_icons:
        return [hammer_name], True, False
    if hammer_name in files.hammers_info:
        return [hammer_name], False, False
    if parse_aspect(args)[0]:
        return parse_aspect(args)[0], True, True
    return '', False, False


def parse_god(args):
    args = [s.lower() for s in args]
    god_name = ' '.join(args)
    if god_name in files.god_cores:
        return god_name
    if god_name in files.aliases['core'] and files.aliases['core'][god_name][0] in files.god_cores:
        return files.aliases['core'][god_name][0]
    return ''


def parse_keepsake(args):
    args = [s.lower() for s in args]
    rank = 3
    if args[-1].isdigit():
        rank = int(args[-1])
        args = args[:-1]
    keepsake_name = ' '.join(args)
    if keepsake_name in files.aliases['keepsake']:
        keepsake_name = files.aliases['keepsake'][keepsake_name]
        if len(keepsake_name) > 1:
            return keepsake_name, -1
        keepsake_name = keepsake_name[0]
    if keepsake_name in files.keepsakes_info:
        return [keepsake_name], rank
    return '', rank


def parse_arcana(args):
    args = [s.lower() for s in args]
    level = 3
    if args[-1].isdigit() and len(args) != 1:
        level = int(args[-1])
        args = args[:-1]
    arcana_name = ' '.join(args)
    if arcana_name in files.aliases['arcana']:
        arcana_name = files.aliases['arcana'][arcana_name]
        if len(arcana_name) > 1:
            return arcana_name, -1
        arcana_name = arcana_name[0]
    if arcana_name in files.arcana_info:
        return [arcana_name], level
    return '', level


def parse_enemy(args):
    args = [s.lower() for s in args]
    enemy_name = ' '.join(args)
    if enemy_name in files.enemies_info:
        return enemy_name
    return ''


def parse_stat(stat_line, value, num_parse=True):
    if not stat_line:
        return ''
    while True:
        try:
            replace = re.findall(r'{[^{}]*}', stat_line)[0]
        except IndexError:
            return f'\n▸{stat_line}'
        round_by = 0
        if 'r' in replace:
            r_idx = replace.index('r')
            round_by = int(replace[r_idx + 1])
            replace = replace[:r_idx] + replace[r_idx + 2:]
        if num_parse:
            if len(value) == 2:
                v1 = round(value[0], round_by)
                if int(v1) == v1:
                    v1 = int(v1)
                v2 = round(value[1], round_by)
                if int(v2) == v2:
                    v2 = int(v2)
                new_stat = f'{v1}-{v2}'
            else:
                new_stat = round(value[0], round_by)
                if int(new_stat) == new_stat:
                    new_stat = int(new_stat)
        else:
            new_stat = value[0]
        if '+' in replace:
            new_stat = f'+{new_stat}'
        if '-' in replace:
            new_stat = f'-{new_stat}'
        if '%' in replace:
            new_stat = f'{new_stat}%'
        if 's' in replace:
            new_stat = f'{new_stat} Sec.'
        if 'x' in replace:
            new_stat = f'{new_stat}x'
        new_stat = f'**{new_stat}**'
        if 'e' in replace:
            new_stat += ' **Encounters**'
        elif 'm' in replace:
            new_stat += ' **<:Magick:1250935754461544478>**'
        elif 'a' in replace:
            new_stat += ' **<:Armor:1243126987032363048>**'
        elif 'l' in replace:
            new_stat += ' **<:Life:1241660063513448499>**'
        elif 'h' in replace:
            new_stat += ' **<:Healing:1028193572840816722>**'
        elif 'g' in replace:
            new_stat += ' **<:GoldenCrowns:1250942621044576308>**'
        stat_line = re.sub(r'{[^{}]*}', new_stat, stat_line)


def parse_prereqs(prereqs):
    parsed_prereqs = []
    for category in prereqs:
        parsed_category = []
        if category[0] == 'x':
            parsed_category.append('Ineligible when you have:')
        elif category[0] == 'm':
            parsed_category.append(f'{category[1][0]} Active')
            parsed_prereqs.append(parsed_category)
            continue
        elif len(category[1]) == 1:
            parsed_category.append('The Following:')
        else:
            parsed_category.append(f'{"One" if category[0] == "1" else "Two"} of:')
        for boon in category[1]:
            parsed_category.append(boon)
        parsed_prereqs.append(parsed_category)
    return parsed_prereqs


def parse_modifiers(args):
    input_str = ' '.join(args).lower()
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


def parse_rarity_table(args, rolls):
    if args:
        title = 'Rarity success rates with the following:\n- '
        title += '\n- '.join([misc.capwords(s) for s in args]) + '\n'
    else:
        title = 'Rarity success rates:'
    output = f'+-----------------+------+\n' \
             f'| Legendary       | {rolls[0]:>3}% |\n' \
             f'+-----------------+------+\n' \
             f'| Duo             | {rolls[1]:>3}% |\n' \
             f'+-----------------+------+\n' \
             f'| Epic            | {rolls[2]:>3}% |\n' \
             f'+-----------------+------+\n' \
             f'| Rare            | {rolls[3]:>3}% |\n' \
             f'+-----------------+------+\n' \
             f'| Common/Infusion | 100% |\n' \
             f'+-----------------+------+'
    return f'{title}```\n{output}```'
