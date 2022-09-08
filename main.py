import copy
import os
import random
import discord
import matplotlib.pyplot as plt
from discord.ext import commands

import files
import misc
import pactgen
import parsing
import randommirror
import randompact

client = commands.Bot(command_prefix=['h!', 'H!'], case_insensitive=True)
bouldy = None


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Race Event: 🌽🎉'))
    print(f'{client.user} is online')


@client.command(aliases=['b'])
async def boon(ctx, *args):
    name, rarity, level = parsing.parse_boon(args)
    if not name:
        await reply(ctx, 'idk man as', True)
        return
    info = files.boons_info[name]
    if rarity == 'heroic' and len(info['rarities']) == 3:
        rarity = 'epic'
    if len(info['rarities']) == 1:
        rarity = 'common'
    value = misc.boon_value(info, rarity)
    pom = 0
    if info['levels'][0] != '0':
        level_display = f'Lv. {level}'
    else:
        level_display = 'Unpommable'
        if len(info['levels']) == 2:
            level_display += ', Unpurgeable'
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
        title=f'**{misc.capwords(name)}** ({level_display})',
        description=desc,
        color=misc.boon_color(info, rarity)
    )
    embed.set_thumbnail(url=info['icon'])
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['ps', 'pom', 'poms'])
async def pomscaling(ctx, *args):
    level = 10
    if args[len(args) - 1].isdigit():
        level = int(args[len(args) - 1])
        args = args[0: len(args) - 1]
    name, _, _ = parsing.parse_boon(args)
    if not name:
        await reply(ctx, 'idk man as', True)
        return
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
    plt.ylim(ymin=0)
    plt.grid(linestyle='--')
    plt.savefig('output.png')

    embed = discord.Embed()
    embed.set_author(name=f'Pom scaling for {" ".join([word[0].upper() + word[1:] for word in name.split()])}')

    file = discord.File('output.png', filename='image.png')
    embed.set_image(url='attachment://image.png')
    await ctx.reply(file=file, embed=embed, mention_author=False)
    os.remove('output.png')


@client.command(aliases=['pre', 'pres', 'prereq', 'prereqs', 'prerequisite'])
async def prerequisites(ctx, *args):
    name, _, _ = parsing.parse_boon(args)
    if not name:
        await reply(ctx, 'idk man as', True)
        return
    boon_info = files.boons_info[name]
    embed = discord.Embed(
        title=f'**{misc.capwords(name)}**',
        color=misc.god_colors[boon_info['god']]
    )
    try:
        prereq_info = files.prereq_info[name]
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
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['a'])
async def aspect(ctx, *args):
    name, level = parsing.parse_aspect(args)
    if not name:
        await reply(ctx, 'idk man as', True)
        return
    info = files.aspects_info[name]
    value = [int(info['levels'][level - 1])]
    embed = discord.Embed(
        title=f'**Aspect of {misc.capwords(name)}** (Lv. {level})',
        description=f'{info["desc"]}\n▸{parsing.parse_stat(info["stat"], value)}',
        color=misc.rarity_embed_colors[level - 1]
    )
    embed.set_footer(text=info['flavor'])
    embed.set_thumbnail(url=info['icon'])
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['h', 'hammers'])
async def hammer(ctx, *args):
    name, is_weapon, is_aspect = parsing.parse_hammer(args)
    if not name:
        await reply(ctx, 'idk man as', True)
        return
    embed = discord.Embed()
    if is_weapon:
        desc = ''
        weapon_name = files.aspects_info[name]['weapon'] if is_aspect else name
        for hammer_name in files.hammers_info:
            if files.hammers_info[hammer_name]['weapon'] == weapon_name:
                if is_aspect and hammer_name in files.prereq_info:
                    compatible = True
                    for prereq in files.prereq_info[hammer_name]:
                        if (prereq[0] == 'x' and f'aspect of {name}' in prereq[1]) or \
                                (prereq[0] == '1' and f'aspect of {name}' not in prereq[1]):
                            compatible = False
                            break
                    if not compatible:
                        continue
                desc += f'{misc.capwords(hammer_name)}\n'
        embed.title = f'List of **{misc.capwords(name)}** hammers'
        embed.description = desc.strip()
        embed.set_thumbnail(url=files.aspects_info[name]['icon'] if is_aspect
                            else f'https://cdn.discordapp.com/emojis/{misc.weapon_icons[name]}.webp')
    else:
        info = files.hammers_info[name]
        embed.title = f'**{misc.capwords(name)}** ({misc.capwords(info["weapon"])})'
        embed.description = info['desc']
        if name in files.prereq_info:
            output = parsing.parse_prereqs(files.prereq_info[name])
            for category in output:
                if len(category) == 1:
                    embed.description = f'**{misc.capwords(category[0])}**'
                    continue
                desc = '\n'.join([misc.capwords(b) for b in category[1:]])
                embed.add_field(name=category[0], value=desc, inline=False)
        embed.set_thumbnail(url=info['icon'])
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['g'])
async def god(ctx, *args):
    name = parsing.parse_god(args)
    if not name:
        await reply(ctx, 'idk man as', True)
        return
    if name == 'bouldy':
        god_boons = {'Bouldy': ['Heart of Stone' for _ in files.bouldy_info]}
    else:
        god_boons = {'Core': []}
        for boon_name in files.boons_info:
            if files.boons_info[boon_name]['god'] == name:
                category = files.boons_info[boon_name]['type']
                if category in ['attack', 'special', 'cast', 'flare', 'dash', 'call']:
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
        title=f'List of **{misc.capwords(name)}** boons', color=misc.god_colors[name]
    )
    for category in god_boons:
        if god_boons[category]:
            desc = '\n'.join([misc.capwords(b) for b in god_boons[category]])
            embed.add_field(name=category, value=desc, inline=False)
    embed.set_thumbnail(url=f'https://cdn.discordapp.com/emojis/{misc.god_icons[name]}.webp')
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['boulder', 'rock', '🪨'])
async def bouldy(ctx):
    info = random.choice(files.bouldy_info)
    embed = discord.Embed(
        title='**Heart of Stone**',
        description=f'{info["desc"]}\n▸{parsing.parse_stat(info["stat"], "")}',
        color=misc.god_colors['bouldy']
    )
    embed.set_thumbnail(url=info['icon'])
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['c'])
async def chaos(ctx, *args):
    blessings = []
    curses = []
    for boon_name in files.boons_info:
        info = files.boons_info[boon_name]
        if info['type'] == 'curse':
            curses.append(boon_name)
        elif info['type'] == 'blessing':
            blessings.append(boon_name)
    args = args + ('chaos',)
    await ctx.reply(embed=parsing.parse_random_chaos(blessings, curses, *args), mention_author=False)


@client.command(aliases=['char', 'well'])
async def charon(ctx, *args):
    input = [s.lower() for s in args]
    hourglass = 8 if 'hourglass' in input else 0
    loyalty = 0.8 if 'loyalty' in input else 1
    types = []
    items = []
    for i in [s.lower() for s in args]:
        if i in ['combat', 'health', 'defiance', 'spawning', 'resource', 'miscellaneous']:
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
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['rarity'])
async def rarityrolls(ctx, *args):
    rolls = [int(min(r * 100, 100)) for r in misc.rarity_rolls(*args)]
    await reply(ctx, parsing.parse_rarity_table(args, rolls))


@client.command(aliases=['p'])
async def pact(ctx, *args):
    total_heat = pactgen.pact_gen(args)
    await ctx.reply(f'Total heat: **{total_heat}**', file=discord.File('./temp.png'), mention_author=False)
    os.remove('./temp.png')


@client.command(aliases=['p\'', '\'p', 'p!', '!p', 'pact\'', '\'pact', 'pact!', '!pact', 'np', 'npact', 'negpact'])
async def negatepact(ctx, *args):
    total_heat = pactgen.negate_pact_gen(args)
    await ctx.reply(f'Total heat: **{total_heat}**', file=discord.File('./temp.png'), mention_author=False)
    os.remove('./temp.png')


@client.command(aliases=['rand', 'random', 'randompact', 'rpact', 'rp'])
async def randpact(ctx, total_heat, hell=None):
    total_heat = int(total_heat)
    if total_heat < (5 if hell else 0) or total_heat > (64 if hell else 63):
        await reply(ctx, 'idk man as', True)
        return
    while True:
        random_pact = {'hl': 1, 'lc': 1, 'js': 1, 'cp': 1, 'pl': 1} if hell else {}
        if hell:
            available_pact = copy.deepcopy(pactgen.hell_pact)
            total_heat -= 5
        else:
            available_pact = copy.deepcopy(pactgen.max_pact)
            available_pact.pop('pl')
        if randompact.add_pact(total_heat, available_pact, random_pact):
            break
    total_heat = pactgen.pact_gen([f'{p}{r}' for p, r in random_pact.items()])
    await ctx.reply(f'Total heat: **{total_heat}**', file=discord.File('./temp.png'), mention_author=False)
    os.remove('./temp.png')


@client.command(aliases=['m'])
async def mirror(ctx, *args):
    randommirror.random_mirror(' '.join(args))
    await ctx.reply(file=discord.File('./temp.png'), mention_author=False)
    os.remove('./temp.png')


@client.command(aliases=['mod', 'ce', 'cheatengine', 'gg', 'gameguardian'])
async def modded(ctx):
    await reply(ctx, misc.modpasta())


async def reply(ctx, message, mention=False):
    await ctx.reply(message, mention_author=mention)


# from webserver import keep_alive
# keep_alive()
# TOKEN = os.environ['TOKEN']
from private.config import TOKEN
client.run(TOKEN)
