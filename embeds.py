import random
import discord
from discord.ext import commands
from matplotlib import pyplot as plt

import files
import misc
import parsing


def random_chaos_embed(input: [str]) -> discord.embeds.Embed:
    blessings = []
    curses = []
    for boon_name in files.boons_info:
        info = files.boons_info[boon_name]
        if info['type'] == 'curse':
            curses.append(boon_name)
        elif info['type'] == 'blessing':
            blessings.append(boon_name)
    modifiers = parsing.parse_modifiers((*input, 'chaos'))
    rarity_rolls = misc.rarity_rolls(modifiers)
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
    bless_desc = parsing.parse_stat(bless_info['desc'][0].lower() + bless_info['desc'][1:], bless_value)
    curse_desc = parsing.parse_stat(curse_info['desc'][0].lower() + curse_info['desc'][1:], curse_value)
    embed = discord.Embed(
        title=f'**{misc.capwords(curse + " " + bless)}**',
        description=f'For the next {duration}, {curse_desc}\nAfterward, {bless_desc}',
        color=0xFFD511 if bless_info['type'] == 'legendary' else misc.rarity_embed_colors[parsing.rarities[rarity] - 1]
    )
    embed.set_thumbnail(url=bless_info['icon'])
    return embed


def random_charon_embed(input: [str]):
    modifiers = parsing.parse_modifiers(input)
    hourglass = 8 if 'bone hourglass' in modifiers else 0
    loyalty = 0.8 if 'loyalty card' in modifiers else 1
    types = []
    items = []
    for i in [s.lower() for s in input]:
        if i in ('combat', 'health', 'defiance', 'spawning', 'resource', 'miscellaneous'):
            types.append(i)
    for item_name in files.boons_info:
        if files.boons_info[item_name]['god'] == 'charon':
            if types and files.boons_info[item_name]['type'] not in types:
                continue
            items.append(item_name)
    item = random.choice(items)
    item_info = files.boons_info[item]
    desc = f'{item_info["desc"]}\n▸' \
           f'{parsing.parse_stat(item_info["stat"], [float(item_info["rarities"][0]) + hourglass])}'
    cost = item_info['cost'].split(' ')
    cost[-2] = '-'.join([str(int(int(g) * loyalty)) for g in cost[-2].replace('%', '').split('-')]) \
               + ('%' if '=' in cost else '')
    desc += f'\n▸Cost: **{" ".join(cost)}**'
    embed = discord.Embed(
        title=f'**{misc.capwords(item)}**',
        description=desc,
        color=0x5500B9
    )
    embed.set_thumbnail(url=item_info['icon'])
    return embed


def boon_embed(input: [str]):
    name, rarity, level = parsing.parse_boon(input)
    if not name:
        return None, ''
    if len(name) > 1:
        desc = ''
        for index, alias in enumerate(name):
            desc += f'{misc.disambig_select[index]} {misc.capwords(alias)}\n'
        embed = discord.Embed(
            title='Alias conflict',
            description=desc
        )
        return embed, name
    else:
        name = name[0]
    info = files.boons_info[name]
    if rarity == 'heroic' and len(info['rarities']) == 3:
        rarity = 'epic'
    if len(info['rarities']) == 1:
        rarity = 'common'
    value = misc.boon_value(info, rarity)
    pom = 0
    unpommable = False
    unpurgeable = False
    title = f'**{misc.capwords(name)}**'
    if info['levels'][0] != '0':
        title += f' (Lv. {level})'
    else:
        unpommable = True
        if len(info['levels']) == 2:
            unpurgeable = True
    while level > 1:
        pom = min(pom, len(info['levels']) - 1)
        value[0] += float(info['levels'][pom])
        if len(value) == 2:
            value[1] += float(info['levels'][pom])
        level -= 1
        pom += 1
    desc = parsing.parse_stat(info["desc"], value)
    desc += f'\n▸{parsing.parse_stat(info["stat"], value)}' if info['god'] != 'chaos' or info['type'] == 'curse' else ''
    desc += f'\n▸{info["maxcall"]}' if info['type'] == 'call' else ''
    desc += f'\n▸Cost: **{info["cost"]}**' if info['god'] == 'charon' else ''
    embed = discord.Embed(
        title=title,
        description=desc,
        color=misc.boon_color(info, rarity)
    )
    if unpommable:
        embed.set_footer(text='Unpommable' + ', Unpurgeable' if unpurgeable else '')
    embed.set_thumbnail(url=info['icon'])
    return embed, ''


def pomscaling_embed(input: [str]):
    level = 10
    if input[-1].isdigit():
        level = int(input[-1])
        input = input[: -1]
    name, _, _ = parsing.parse_boon(input)
    if not name:
        return None, ''
    if len(name) > 1:
        desc = ''
        for index, alias in enumerate(name):
            desc += f'{misc.disambig_select[index]} {misc.capwords(alias)}\n'
        embed = discord.Embed(
            title='Alias conflict',
            description=desc
        )
        return embed, name
    else:
        name = name[0]
    info = files.boons_info[name]
    values = info['rarities'].copy()
    for rarity, value in enumerate(values):
        if '-' in value:
            value = value.split('-')
            values[rarity] = [float(info['rarities'][0]) * float(v) for v in value]
        else:
            values[rarity] = [float(value)]
    pom = 0
    rarity_damages = []
    for i in range(len(values)):
        rarity_damages.append([])
    for i in range(level):
        pom = min(pom, len(info['levels']) - 1)
        for rarity, value in enumerate(values):
            rarity_damages[rarity].append(value)
            new_value = values[rarity].copy()
            new_value[0] += float(info['levels'][pom])
            if len(values[rarity]) == 2:
                new_value[1] += float(info['levels'][pom])
            values[rarity] = new_value
        pom += 1
    plt.clf()
    level_axis = list(range(1, level + 1))
    for rarity, damages in enumerate(rarity_damages):
        lower = [d[0] for d in damages]
        plt.plot(level_axis, lower, color=misc.rarity_graph_colors[rarity])
        if len(damages[0]) == 2:
            upper = [d[1] for d in damages]
            plt.plot(level_axis, upper, color=misc.rarity_graph_colors[rarity])
            plt.fill_between(list(range(1, level + 1)), lower, upper, color=misc.rarity_graph_colors[rarity], alpha=0.5)
    plt.xlabel('Level')
    plt.ylabel(info['stat'].split(':')[0])
    plt.title(f'Pom scaling for {misc.capwords(name)}')
    plt.ylim(ymin=0)
    plt.grid(linestyle='--')
    plt.savefig('output.png')
    return 'output.png', ''


def prereq_embed(input: [str]):
    name, _, _ = parsing.parse_boon(input)
    if not name:
        return None, ''
    if len(name) > 1:
        desc = ''
        for index, alias in enumerate(name):
            desc += f'{misc.disambig_select[index]} {misc.capwords(alias)}\n'
        embed = discord.Embed(
            title='Alias conflict',
            description=desc
        )
        return embed, name
    else:
        name = name[0]
    boon_info = files.boons_info[name]
    embed = discord.Embed(
        title=f'**{misc.capwords(name)}**',
        color=misc.god_colors[boon_info['god']]
    )
    try:
        prereq_info = files.prereqs_info[name]
        output = parsing.parse_prereqs(prereq_info)
        for category in output:
            if len(category) == 1:
                embed.description = f'**{misc.capwords(category[0])}**'
                continue
            desc = '\n'.join([misc.capwords(b) for b in category[1:]])
            embed.add_field(name=category[0], value=desc, inline=False)
    except KeyError:
        embed.description = '(None in particular)'
    embed.set_thumbnail(url=boon_info['icon'])
    return embed, ''


def aspect_embed(input: [str]):
    name, level = parsing.parse_aspect(input)
    if not name:
        return None
    name = name[0]
    level = min(max(level, 1), 5)
    info = files.aspects_info[name]
    value = [int(info['levels'][level - 1])]
    embed = discord.Embed(
        title=f'**Aspect of {misc.capwords(name)}** (Lv. {level})',
        description=f'{info["desc"]}\n▸{parsing.parse_stat(info["stat"], value)}',
        color=misc.rarity_embed_colors[level - 1]
    )
    embed.set_footer(text=info['flavor'])
    embed.set_thumbnail(url=info['icon'])
    return embed


def hammer_embed(input: [str]):
    name, is_weapon, is_aspect = parsing.parse_hammer(input)
    if not name:
        return None, ''
    if len(name) > 1:
        desc = ''
        for index, alias in enumerate(name):
            desc += f'{misc.disambig_select[index]} {misc.capwords(alias)}\n'
        embed = discord.Embed(
            title='Alias conflict',
            description=desc
        )
        return embed, name
    else:
        name = name[0]
    embed = discord.Embed()
    if is_weapon:
        desc = ''
        weapon_name = files.aspects_info[name]['weapon'] if is_aspect else name
        for hammer_name in files.hammers_info:
            if files.hammers_info[hammer_name]['weapon'] == weapon_name:
                if is_aspect and hammer_name in files.prereqs_info:
                    compatible = True
                    for prereq in files.prereqs_info[hammer_name]:
                        if (prereq[0] == 'x' and f'aspect of {name}' in prereq[1]) or \
                                (prereq[0] == '1' and f'aspect of {name}' not in prereq[1]):
                            compatible = False
                            break
                    if not compatible:
                        continue
                desc += f'{misc.capwords(hammer_name)}\n'
        embed.title = f'List of **{misc.capwords(name)}** hammers'
        embed.description = desc.strip()
        embed.set_thumbnail(url=files.aspects_info[name]['icon'] if is_aspect else
        f'https://cdn.discordapp.com/emojis/{misc.weapon_icons[name]}.webp')
    else:
        info = files.hammers_info[name]
        embed.title = f'**{misc.capwords(name)}** ({misc.capwords(info["weapon"])})'
        embed.description = info['desc']
        if name in files.prereqs_info:
            output = parsing.parse_prereqs(files.prereqs_info[name])
            for category in output:
                if len(category) == 1:
                    embed.description = f'**{misc.capwords(category[0])}**'
                    continue
                desc = '\n'.join([misc.capwords(b) for b in category[1:]])
                embed.add_field(name=category[0], value=desc, inline=False)
        embed.set_thumbnail(url=info['icon'])
    return embed, ''


def god_embed(input: [str]):
    name = parsing.parse_god(input)
    if not name:
        return None
    if name == 'bouldy':
        god_boons = {'Bouldy': ['Heart of Stone' for _ in files.bouldy_info]}
    else:
        god_boons = {'Core': []}
        for boon_name in files.boons_info:
            if files.boons_info[boon_name]['god'] == name:
                category = files.boons_info[boon_name]['type']
                if category in ('attack', 'special', 'cast', 'flare', 'dash', 'call'):
                    god_boons['Core'].append(boon_name)
                else:
                    if len(category) == 2 and category[0] == 't':
                        category = 'Tier ' + category[1]
                    else:
                        category = category.capitalize()
                    if category not in god_boons:
                        god_boons[category] = []
                    god_boons[category].append(boon_name)
    embed = discord.Embed(
        title=f'List of **{misc.capwords(name)}** boons',
        color=misc.god_colors[name]
    )
    for category in god_boons:
        if god_boons[category]:
            desc = '\n'.join([misc.capwords(b) for b in god_boons[category]])
            embed.add_field(name=category, value=desc)
    embed.set_thumbnail(url=f'https://cdn.discordapp.com/emojis/{misc.god_icons[name]}.webp')
    return embed


def define_embed(text: str):
    used = set()
    for definition in files.definitions_info:
        if misc.capwords(definition) in text and definition not in used:
            used.add(definition)
            text = text.replace(misc.capwords(definition), '')
    for definition in files.aliases['definition']:
        if misc.capwords(definition) in text and files.aliases['definition'][definition] not in used:
            used.add(files.aliases['definition'][definition])
            text = text.replace(misc.capwords(definition), '')
    embed = discord.Embed(
        title=f'List of **Definitions**'
    )
    for definition in used:
        embed.add_field(name=misc.capwords(definition), value=files.definitions_info[definition], inline=False)
    return embed


def keepsake_embed(input: [str]):
    if input:
        name, rank = parsing.parse_keepsake(input)
        if not name:
            return None, ''
        if len(name) > 1:
            desc = ''
            for index, alias in enumerate(name):
                desc += f'{misc.disambig_select[index]} {misc.capwords(alias)}\n'
            embed = discord.Embed(
                title='Alias conflict',
                description=desc
            )
            return embed, name
        else:
            name = name[0]
        info = files.keepsakes_info[name]
        rank = min(max(rank, 1), 5 if info['type'] == 'companion' else 3)
        try:
            value = [float(info['ranks'][rank - 1])]
        except IndexError:
            value = []
        embed = discord.Embed(
            title=f'**{misc.capwords(name)}**',
            description=f'{parsing.parse_stat(info["desc"], value)}',
            color=misc.rarity_embed_colors[rank - 1]
        )
        if info['type'] == 'companion':
            footer = f'From {misc.capwords(info["bond"][0])}, {info["flavor"]}'
        else:
            footer = f'From {misc.capwords(info["bond"][0])}; ' \
                     f'you share {info["bond"][1]} {misc.capwords(info["bond"][2])} Bond' \
                     f'\n\n{info["flavor"]}'
        embed.set_footer(text=footer)
        embed.set_thumbnail(url=info['icon'])
    else:
        keepsakes = {}
        for keepsake_name in files.keepsakes_info:
            category = files.keepsakes_info[keepsake_name]['type'].capitalize()
            if category not in keepsakes:
                keepsakes[category] = []
            keepsakes[category].append(keepsake_name)
        embed = discord.Embed(title='List of **Keepsakes**', color=misc.god_colors['keepsake'])
        for category in keepsakes:
            desc = '\n'.join([misc.capwords(b) for b in keepsakes[category]])
            embed.add_field(name=category, value=desc)
        embed.set_thumbnail(url=f'https://cdn.discordapp.com/emojis/{misc.god_icons["keepsake"]}.webp')
    return embed, ''


def getpersonal_embed(ctx, user):
    id = str(user.id) if user else str(ctx.message.author.id)
    embed = discord.Embed(
        title='Personal pact and mirror presets'
    )
    embed.set_footer(text=f'Requested by {ctx.message.author.name}', icon_url=ctx.message.author.avatar_url)
    if id in files.personal:
        if files.personal[id]['pacts']:
            pacts = ''
            for pact_name in files.personal[id]['pacts']:
                pacts += f'{pact_name}: {" ".join(files.personal[id]["pacts"][pact_name])}\n'
            embed.add_field(name='Pacts', value=pacts, inline=False)
        if files.personal[id]['mirrors']:
            mirrors = ''
            for mirror_name in files.personal[id]['mirrors']:
                mirrors += f'{mirror_name}: {files.personal[id]["mirrors"][mirror_name]}\n'
            embed.add_field(name='Mirrors', value=mirrors, inline=False)
    return embed


def help_embed(client, command_name, aliases_to_command):
    embed = discord.Embed()
    if not command_name:
        embed.set_author(name='Help')
        embed.add_field(name='Commands', value=', '.join(list(files.commands_info.keys())), inline=False)
        embed.add_field(name='Usage', value='h!help <command_name>', inline=False)
        embed.add_field(name='Syntax', value='[parameter]\n-> parameter is optional\n'
                                             '[parameter=value]\n-> if not provided, parameter defaults to value\n'
                                             'parameter...\n-> arbitrary number of parameters accepted')
    else:
        if command_name in aliases_to_command:
            command_name = aliases_to_command[command_name]
        if command_name in files.commands_info:
            embed.set_author(name=f'Help for \'{command_name}\' command')
            embed.add_field(name='Parameters', value=files.commands_info[command_name][0], inline=False)
            embed.add_field(name='Function', value=files.commands_info[command_name][1], inline=False)
            aliases = commands.Bot.get_command(client, command_name).aliases
            if aliases:
                embed.add_field(name='Aliases', value=', '.join(aliases), inline=False)
        else:
            embed.set_author(name='Help')
            embed.add_field(name=command_name, value='Not a valid command, use h!help for a list of commands')
    embed.set_thumbnail(url=client.user.avatar_url)
    return embed


async def creds_embed(client):
    credits_channel = client.get_channel(1008232170751533106)
    if not credits_channel:
        credits_channel = await client.fetch_channel(1008232170751533106)
    messages = await credits_channel.history(limit=200).flatten()
    messages = [message.content.split('\n', 1) for message in messages]
    messages.reverse()
    embed = discord.Embed(
        title='Special thanks to'
    )
    for message in messages:
        user = client.get_user(message[0][2: -1])
        if not user:
            user = await client.fetch_user(message[0][2: -1])
        embed.add_field(name=user.name, value=message[1], inline=False)
    return embed
