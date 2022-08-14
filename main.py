import discord
import os
from discord.ext import commands
import matplotlib.pyplot as plt
import string

import files
import pactgen
import parsing
import misc
from private.config import TOKEN

# from webserver import keep_alive

client = commands.Bot(command_prefix=['h!'], case_insensitive=True)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Race Event: 🌽🎉'))
    print(f'{client.user} is online')


@client.command(aliases=['b'])
async def boon(ctx, *args) -> None:
    name, rarity, level = parsing.parse_boon(args)
    if not name:
        await reply(ctx, 'Invalid input!', True)
        return
    info = files.boons_info[name]
    if rarity == 'heroic' and len(info['rarities']) == 3:
        rarity = 'epic'
    value = info['rarities'][parsing.rarities[rarity] - 1]
    if '-' in value:
        value = value.split('-')
        value = [float(info['rarities'][0]) * float(v) for v in value]
    else:
        value = [float(value)]
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
    if info['type'] in ['legendary']:
        color = 0xFFD511
    elif info['type'] in ['duo']:
        color = 0xD1FF18
    else:
        color = misc.rarity_embed_colors[parsing.rarities[rarity] - 1]
    embed = discord.Embed(
        title=f'**{string.capwords(name)}** ({level_display})',
        description=f'{info["desc"]}\n▸{parsing.parse_stat(info["stat"], value)}',
        color=color
    )
    embed.set_thumbnail(url=info['icon'])
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['ps'])
async def pomscaling(ctx, *args) -> None:
    level = 10
    if args[len(args) - 1].isdigit():
        level = int(args[len(args) - 1])
        args = args[0: len(args) - 1]
    name, _, _ = parsing.parse_boon(args)
    if not name:
        await reply(ctx, 'Invalid input!', True)
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


@client.command(aliases=['a'])
async def aspect(ctx, *args):
    name, level = parsing.parse_aspect(args)
    if not name:
        await reply(ctx, 'Invalid input!', True)
        return
    info = files.aspects_info[name]
    value = [int(info['levels'][level - 1])]
    embed = discord.Embed(
        title=f'**Aspect of {string.capwords(name)}** (Lv. {level})',
        description=f'{info["desc"]}\n▸{parsing.parse_stat(info["stat"], value)}',
        color=misc.rarity_embed_colors[level - 1]
    )
    embed.set_footer(text=info['flavor'])
    embed.set_thumbnail(url=info['icon'])
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['g'])
async def god(ctx, *args):
    name = parsing.parse_god(args)
    if not name:
        await reply(ctx, 'Invalid input!', True)
        return
    god_boons = {'Core': [], 'Tier 1': [], 'Tier 2': [], 'Legendary': []}
    for boon_name in files.boons_info:
        if files.boons_info[boon_name]['god'] == name:
            type = files.boons_info[boon_name]['type']
            if type in ['attack', 'special', 'cast', 'flare', 'dash', 'call']:
                god_boons['Core'].append(boon_name)
            elif type == 't1':
                god_boons['Tier 1'].append(boon_name)
            elif type == 't2':
                god_boons['Tier 2'].append(boon_name)
            elif type == 'status':
                god_boons['Status'] = [boon_name]
            elif type == 'revenge':
                god_boons['Revenge'] = [boon_name]
            elif type == 'legendary':
                god_boons['Legendary'].append(boon_name)
    embed = discord.Embed(
        title=f'List of **{string.capwords(name)}** boons', color=misc.god_colors[name]
    )

    for type in god_boons:
        desc = '\n'.join([string.capwords(b) for b in god_boons[type]])
        embed.add_field(name=type, value=desc, inline=False)
    embed.set_thumbnail(url=misc.god_icons[name])
    await ctx.reply(embed=embed, mention_author=False)


@client.command('p')
async def pact(ctx, *args):
    total_heat = pactgen.pact_gen(args)
    await ctx.reply(f'Total heat: **{total_heat}**', file=discord.File('./temp.png'), mention_author=False)
    os.remove('./temp.png')


async def reply(ctx, message, mention=False):
    await ctx.reply(message, mention_author=mention)


# keep_alive()
client.run(TOKEN)
