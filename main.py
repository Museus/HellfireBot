import discord
import os
from discord.ext import commands
import matplotlib.pyplot as plt

from private.config import TOKEN
import misc

# from webserver import keep_alive

client = commands.Bot(command_prefix=['h!'], case_insensitive=True)

boons_info = {}
f = open('booninfo.txt', 'r', encoding='utf8')
while boon := f.readline().strip():
    type, boon = boon.split(' ', 1)
    boons_info[boon] = {'type': type, 'desc': f.readline().strip(), 'stat': f.readline().strip(),
                        'rarities': f.readline().strip().split(' '), 'levels': f.readline().strip().split(' ')}


@client.event
async def on_ready():
    # await client.change_presence(activity=discord.Game(name='Race Event: 🌽🎉'))
    print(f'{client.user} is online')


@client.command(aliases=['b'])
async def boon(ctx, *args) -> None:
    name, rarity, level = misc.parse_boon(args)
    info = boons_info[name.lower()]
    output, rarity, level = misc.adjust_boon_type(info, name, rarity, level)
    output += f'{info["desc"]}\n'
    value = info['rarities'][misc.rarities[rarity] - 1]
    if '-' in value:
        value = value.split('-')
        value = [float(info['rarities'][0]) * float(v) for v in value]
    else:
        value = [float(value)]
    pom = 0
    while level > 1:
        pom = min(pom, len(info['levels']) - 1)
        value[0] += int(info['levels'][pom])
        if len(value) == 2:
            value[1] += int(info['levels'][pom])
        level -= 1
        pom += 1
    output += f'{misc.parse_stat(info["stat"], value)}'
    await reply(ctx, output)


@client.command(aliases=['ps'])
async def pomscaling(ctx, *args) -> None:
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
            values[rarity] += int(info['levels'][pom])
        pom += 1
    plt.clf()
    for rarity, damages in enumerate(rarity_damages):
        plt.plot(list(range(1, level + 1)), damages, color=misc.rarity_colors[rarity])
    plt.xlabel('Level')
    plt.ylabel(info['stat'].split(':')[0])
    plt.ylim(ymin=0)
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
