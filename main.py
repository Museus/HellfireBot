import copy
import difflib
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
client.remove_command('help')


@client.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.CommandNotFound):
        err = str(err)
        err = err[err.find(chr(34)) + 1: err.rfind(chr(34))].lower()
        names = set()
        for command in client.commands:
            names.add(command.name)
            for alias in command.aliases:
                names.add(alias)
        matches = difflib.get_close_matches(err, names, n=2)
        if not matches:
            await reply(ctx, f'h!{err} does not exist, use h!help to see a list of valid commands', True)
            return
        matches_str = ' or '.join([f'h!{match}' for match in matches])
        await reply(ctx, f'Did you mean {matches_str}?', True)
        return
    raise err


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Race Event: 🌽🎉'))
    print(f'{client.user} is online')


@client.command(pass_context=True)
async def help(ctx, command_name=None):
    embed = discord.Embed()
    if not command_name:
        embed.set_author(name='Help')
        embed.add_field(name='Commands', value=', '.join(list(files.commands_info.keys())), inline=False)
        embed.add_field(name='Usage', value='h!help <command_name>', inline=False)
        embed.add_field(name='Syntax', value='[parameter]\n-> parameter is optional\n'
                                             '[parameter=value]\n-> if not provided, parameter defaults to value\n'
                                             'parameter...\n-> arbitrary number of parameters accepted')
    elif command_name in files.commands_info:
        embed.set_author(name=f'Help for \'{command_name}\' command')
        embed.add_field(name='Parameters', value=files.commands_info[command_name][0], inline=False)
        embed.add_field(name='Function', value=files.commands_info[command_name][1], inline=False)
        aliases = commands.Bot.get_command(client, command_name).aliases
        if aliases:
            embed.add_field(name='Aliases', value=', '.join(aliases), inline=False)
    else:
        embed.set_author(name='Help')
        embed.add_field(name=command_name, value='Not a valid command, use h!help for a list of commands', inline=False)
    embed.set_thumbnail(url=client.user.avatar_url)
    await ctx.reply(embed=embed)


@client.command(aliases=['i'])
async def invite(ctx):
    await reply(ctx, 'https://discordapp.com/api/oauth2/authorize?scope=bot&client_id=1007141766979387432')


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
    plt.title(f'Pom scaling for {misc.capwords(name)}')
    plt.ylim(ymin=0)
    plt.grid(linestyle='--')
    plt.savefig('output.png')
    await ctx.reply(file=discord.File('output.png'), mention_author=False)
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
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['a', 'weapon', 'w'])
async def aspect(ctx, *args):
    name, level = parsing.parse_aspect(args)
    if not name:
        await reply(ctx, 'idk man as', True)
        return
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
        color=misc.god_colors[name])
    for category in god_boons:
        if god_boons[category]:
            desc = '\n'.join([misc.capwords(b) for b in god_boons[category]])
            embed.add_field(name=category, value=desc)
    embed.set_thumbnail(url=f'https://cdn.discordapp.com/emojis/{misc.god_icons[name]}.webp')
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['d', 'def', 'defs', 'defines', 'definition', 'definitions'])
async def define(ctx):
    if not ctx.message.reference:
        await reply(ctx, 'idk man as', True)
        return
    text = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    try:
        text = text.embeds[0].description
    except IndexError:
        text = text.content
    if not isinstance(text, str):
        await reply(ctx, 'idk man as', True)
        return
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
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['boulder', 'rock', '🪨', '<:bouldy:1014438782755422220>'])
async def bouldy(ctx):
    info = random.choice(files.bouldy_info)
    embed = discord.Embed(
        title='**Heart of Stone**',
        description=f'{info["desc"]}\n▸{parsing.parse_stat(info["stat"], "")}',
        color=misc.god_colors['bouldy']
    )
    embed.set_thumbnail(url=info['icon'])
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['c', 'ch'])
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
    modifiers = parsing.parse_modifiers(args)
    hourglass = 8 if 'bone hourglass' in modifiers else 0
    loyalty = 0.8 if 'loyalty card' in modifiers else 1
    types = []
    items = []
    for i in [s.lower() for s in args]:
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
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['k', 'keepsakes'])
async def keepsake(ctx, *args):
    if args:
        name, rank = parsing.parse_keepsake(args)
        if not name:
            await reply(ctx, 'idk man as', True)
            return
        info = files.keepsakes_info[name]
        rank = min(max(rank, 1), 5 if info['type'] == 'companion' else 3)
        try:
            value = [int(info['ranks'][rank - 1])]
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
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['rarity'])
async def rarityrolls(ctx, *args):
    modifiers = parsing.parse_modifiers(args)
    rolls = [int(min(r * 100, 100)) for r in misc.rarity_rolls(modifiers)]
    await reply(ctx, parsing.parse_rarity_table(modifiers, rolls))


@client.command(aliases=['p'])
async def pact(ctx, *args):
    total_heat = pactgen.pact_gen(str(ctx.message.author.id), args)
    await ctx.reply(f'Total heat: **{total_heat}**', file=discord.File('./temp.png'), mention_author=False)
    os.remove('./temp.png')


@client.command(aliases=['p\'', '\'p', 'p!', '!p', 'pact\'', '\'pact', 'pact!', '!pact', 'np', 'npact', 'negpact'])
async def negatepact(ctx, *args):
    total_heat = pactgen.negate_pact_gen(args)
    await ctx.reply(f'Total heat: **{total_heat}**', file=discord.File('./temp.png'), mention_author=False)
    os.remove('./temp.png')


@client.command(aliases=['r', 'rand', 'random', 'randompact', 'rpact'])
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
    total_heat = pactgen.pact_gen('', [f'{p}{r}' for p, r in random_pact.items()])
    await ctx.reply(f'Total heat: **{total_heat}**', file=discord.File('./temp.png'), mention_author=False)
    os.remove('./temp.png')


@client.command(aliases=['m'])
async def mirror(ctx, *args):
    randommirror.random_mirror(str(ctx.message.author.id), ' '.join(args))
    await ctx.reply(file=discord.File('./temp.png'), mention_author=False)
    os.remove('./temp.png')


@client.command(aliases=['personal', 'gp'])
async def getpersonal(ctx, user: discord.Member = None):
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
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['addp', 'ap'])
async def addpact(ctx, name, *args):
    id = str(ctx.message.author.id)
    if id not in files.personal:
        files.personal[id] = {'mirrors': {}, 'pacts': {}}
    files.personal[id]['pacts'][name] = list(args)
    files.write_personal()
    await reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['addm', 'am'])
async def addmirror(ctx, name, *args):
    mirror_binary = ''.join(args)
    if len(mirror_binary) != 12 or not all(c in '01' for c in mirror_binary):
        await reply(ctx, 'idk man as', True)
        return
    id = str(ctx.message.author.id)
    if id not in files.personal:
        files.personal[id] = {'mirrors': {}, 'pacts': {}}
    files.personal[id]['mirrors'][name] = mirror_binary
    files.write_personal()
    await reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['deletep', 'dp', 'removepact', 'removep', 'rp'])
async def deletepact(ctx, *args):
    name = ' '.join(args)
    id = str(ctx.message.author.id)
    if id not in files.personal or name not in files.personal[id]['pacts']:
        await reply(ctx, 'No pact with matching name', True)
        return
    files.personal[id]['pacts'].pop(name)
    files.write_personal()
    await reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['deletem', 'dm', 'removemirror', 'removem', 'rm'])
async def deletemirror(ctx, *args):
    name = ' '.join(args)
    id = str(ctx.message.author.id)
    if id not in files.personal or name not in files.personal[id]['mirrors']:
        await reply(ctx, 'No mirror with matching name', True)
        return
    files.personal[id]['mirrors'].pop(name)
    files.write_personal()
    await reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['mod', 'ce', 'cheatengine', 'gg', 'gameguardian'])
async def modded(ctx):
    await reply(ctx, misc.mod_pasta)


@client.command(aliases=['suggestion', 's', 'request'])
async def suggest(ctx, *args):
    input = ' '.join([s.lower() for s in args])
    verofire = input.split('->')
    if len(verofire) != 2:
        await reply(ctx, 'idk man as', True)
        return
    channel = client.get_channel(1018409476908392518)
    await channel.send(f'From {ctx.author.mention}:\n```{input}```')


@client.command(aliases=['cred', 'creds', 'credit'])
async def credits(ctx):
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
    await ctx.reply(embed=embed, mention_author=False)


async def reply(ctx, message, mention=False):
    await ctx.reply(message, mention_author=mention)


# from webserver import keep_alive
# keep_alive()
# TOKEN = os.environ['TOKEN']
from private.config import TOKEN

client.run(TOKEN)
