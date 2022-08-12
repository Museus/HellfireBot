import discord
import os
from discord.ext import commands
import matplotlib.pyplot as plt
import string

from private.config import TOKEN
import misc

# from webserver import keep_alive

client = commands.Bot(command_prefix=['h!'], case_insensitive=True)

boons_info = {}
f = open('./booninfo.txt', 'r', encoding='utf8')
while boon := f.readline().strip():
    type, boon = boon.split(' ', 1)
    boons_info[boon] = {'type': type, 'desc': f.readline().strip(), 'stat': f.readline().strip(),
                        'rarities': f.readline().strip().split(' '), 'levels': f.readline().strip().split(' '),
                        'icon': f.readline()}


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Race Event: 🌽🎉'))
    print(f'{client.user} is online')


@client.command(aliases=['b'])
async def boon(ctx, *args) -> None:
    name, rarity, level = misc.parse_boon(args)
    info = boons_info[name.lower()]
    if rarity == 'heroic' and len(info['rarities']) == 3:
        rarity = 'epic'
    value = info['rarities'][misc.rarities[rarity] - 1]
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
    embed = discord.Embed(
        title=f'**{string.capwords(name)}** ({level_display})',
        description=f'{info["desc"]}\n▸{misc.parse_stat(info["stat"], value)}')
    if info['type'] in ['legendary', 'duo']:
        embed.title = f'**{string.capwords(name)}**'
    if info['type'] in ['legendary']:
        embed.color = 0xFFD511
    elif info['type'] in ['duo']:
        embed.color = 0xD1FF18
    else:
        embed.color = misc.rarity_colors[misc.rarities[rarity] - 1]
    embed.set_thumbnail(url=info['icon'])
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['ps'])
async def pomscaling(ctx, *args) -> None:
    def color_int_str(color_int: int) -> str:
        color = hex(color_int)
        return f'#{color.split("x")[1]:0>6}'
    level = 10
    if args[len(args) - 1].isdigit():
        level = int(args[len(args) - 1])
        args = args[0: len(args) - 1]
    name, _, _ = misc.parse_boon(args)
    info = boons_info[name.lower()]
    values = info['rarities'].copy()
    for rarity, value in enumerate(values):
        if '-' in value:
            value = value.split('-')
            values[rarity] = (float(info['rarities'][0]) * float(value[0]) + float(info['rarities'][0]) * float(value[1])) / 2
        else:
            values[rarity] = float(value)
    pom = 0
    rarity_damages = []
    for i in range(len(values)):
        rarity_damages.append([])
    for i in range(level):
        pom = min(pom, len(info['levels']) - 1)
        for rarity, value in enumerate(values):
            rarity_damages[rarity].append(value)
            values[rarity] += float(info['levels'][pom])
        pom += 1
    plt.clf()
    for rarity, damages in enumerate(rarity_damages):
        plt.plot(list(range(1, level + 1)), damages, color=color_int_str(misc.rarity_colors[rarity]))
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


async def reply(ctx, message, mention=False):
    await ctx.reply(message, mention_author=mention)


# keep_alive()
client.run(TOKEN)
