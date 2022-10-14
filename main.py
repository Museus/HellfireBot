import asyncio
import copy
import difflib
import math
import os
import random

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from matplotlib import pyplot as plt

import embeds
import files
import misc
import pactgen
import parsing
import randommirror
import randompact

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=['h!', 'H!'], case_insensitive=True, intents=intents)
client.remove_command('help')
aliases_to_command = {}


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
            await reply(ctx, f'h!{err} does not exist, use h!help to see a list of valid commands', mention=True)
            return
        matches_str = ' or '.join([f'h!{match}' for match in matches])
        await reply(ctx, f'Did you mean {matches_str}?', mention=True)
        return
    if isinstance(err, commands.MissingRequiredArgument):
        await reply(ctx, 'Missing required input. Run h!help <command_name> for more information.', mention=True)
        return
    raise err


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Race Event: 🌽🎉'))
    for command in files.commands_info:
        for alias in commands.Bot.get_command(client, command).aliases:
            aliases_to_command[alias] = command
    print(f'{client.user} is online')


@client.command(pass_context=True)
async def help(ctx, command_name=None):
    embed = embeds.help_embed(client, command_name, aliases_to_command)
    await reply(ctx, embed=embed, mention=True)


@client.command(aliases=['i'])
async def invite(ctx):
    await reply(ctx, 'https://discordapp.com/api/oauth2/authorize?scope=bot&client_id=1007141766979387432')


@client.command(aliases=['b'])
async def boon(ctx, *args):
    embed, choices = embeds.boon_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.boon_embed)
        return
    await reply(ctx, embed=embed)


@client.command(aliases=['ps', 'pom', 'poms', 'pscale', 'pscaling'])
async def pomscaling(ctx, *args):
    embed, choices = embeds.pomscaling_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.pomscaling_embed)
        return
    await reply(ctx, file=discord.File('./output.png'))
    os.remove('./output.png')


@client.command(aliases=['pre', 'pres', 'prereq', 'prereqs', 'prerequisite'])
async def prerequisites(ctx, *args):
    embed, choices = embeds.prereq_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.prereq_embed)
        return
    await reply(ctx, embed=embed)


@client.command(aliases=['a', 'weapon', 'w'])
async def aspect(ctx, *args):
    embed, choices = embeds.aspect_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.aspect_embed)
        return
    await reply(ctx, embed=embed)


@client.command(aliases=['h', 'hammers'])
async def hammer(ctx, *args):
    embed, choices = embeds.hammer_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.hammer_embed)
        return
    await reply(ctx, embed=embed)


@client.command(aliases=['g'])
async def god(ctx, *args):
    embed = embeds.god_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', mention=True)
        return
    await reply(ctx, embed=embed)


@client.command(aliases=['legendary', 'leg', 'legend', 'yellow'])
async def legendaries(ctx):
    await reply(ctx, embed=embeds.legendaries_embed())


@client.command(aliases=['bp'])
async def benefitspackage(ctx, *args):
    embed = embeds.bpperk_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', mention=True)
        return
    await reply(ctx, embed=embed)


@client.command(aliases=['d', 'def', 'defs', 'defines', 'definition', 'definitions'])
async def define(ctx):
    if not ctx.message.reference:
        await reply(ctx, 'idk man as', mention=True)
        return
    text = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    try:
        text = text.embeds[0].description
    except IndexError:
        text = text.content
    if not isinstance(text, str):
        await reply(ctx, 'idk man as', mention=True)
        return
    embed = embeds.define_embed(text)
    await reply(ctx, embed=embed)


@client.command(aliases=['boulder', 'rock', '🪨', '<:bouldy:1014438782755422220>'])
async def bouldy(ctx):
    info = random.choice(files.bouldy_info)
    embed = discord.Embed(
        title='**Heart of Stone**',
        description=f'{info["desc"]}\n▸{parsing.parse_stat(info["stat"], "")}',
        color=misc.god_colors['bouldy']
    )
    embed.set_thumbnail(url=misc.to_link(info['icon']))
    await reply(ctx, embed=embed)


@client.command(aliases=['randomchaos', 'rchaos', 'c', 'ch', 'chaos'])
async def randchaos(ctx, *args):
    embed = embeds.random_chaos_embed(args)
    await reply(ctx, embed=embed)


@client.command(aliases=['randomcharon', 'rcharon', 'charon', 'char', 'well', 'randomwell', 'randwell', 'rwell'])
async def randcharon(ctx, *args):
    embed = embeds.random_charon_embed(args)
    await reply(ctx, embed=embed)


@client.command(aliases=['k', 'keepsakes', 'companion', 'companions'])
async def keepsake(ctx, *args):
    embed, choices = embeds.keepsake_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.keepsake_embed)
        return
    await reply(ctx, embed=embed)


@client.command(aliases=['rarity', 'roll', 'rolls'])
async def rarityrolls(ctx, *args):
    modifiers = parsing.parse_modifiers(args)
    rolls = [int(min(r * 100, 100)) for r in misc.rarity_rolls(modifiers)]
    await reply(ctx, parsing.parse_rarity_table(modifiers, rolls))


@client.command(aliases=['p'])
async def pact(ctx, *args):
    total_heat = pactgen.pact_gen(str(ctx.message.author.id), args)
    await reply(ctx, f'Total heat: **{total_heat}**', file=discord.File('./temp.png'))
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
    await reply(ctx, f'Total heat: **{total_heat}**', file=discord.File('./temp.png'))
    os.remove('./temp.png')


@client.command(aliases=['m'])
async def mirror(ctx, *args):
    randommirror.random_mirror(str(ctx.message.author.id), ' '.join(args))
    await reply(ctx, file=discord.File('./temp.png'))
    os.remove('./temp.png')


@client.command(aliases=['personal', 'gp'])
async def getpersonal(ctx, user: discord.Member = None):
    embed = embeds.getpersonal_embed(ctx, user)
    await reply(ctx, embed)


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
        await reply(ctx, 'idk man as', mention=True)
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
        await reply(ctx, 'No pact with matching name', mention=True)
        return
    files.personal[id]['pacts'].pop(name)
    files.write_personal()
    await reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['deletem', 'dm', 'removemirror', 'removem', 'rm'])
async def deletemirror(ctx, *args):
    name = ' '.join(args)
    id = str(ctx.message.author.id)
    if id not in files.personal or name not in files.personal[id]['mirrors']:
        await reply(ctx, 'No mirror with matching name', mention=True)
        return
    files.personal[id]['mirrors'].pop(name)
    files.write_personal()
    await reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['addc', 'ac'])
@has_permissions(administrator=True)
async def addchannel(ctx, channel_id):
    guild_id = str(ctx.message.guild.id)
    if guild_id not in files.channels:
        files.channels[guild_id] = []
    if channel_id not in files.channels[guild_id]:
        files.channels[guild_id].append(channel_id)
        files.write_channel()
    await reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['deletec', 'dc', 'removechannel', 'removec', 'rc'])
@has_permissions(administrator=True)
async def deletechannel(ctx, channel_id):
    guild_id = str(ctx.message.guild.id)
    if guild_id not in files.channels or channel_id not in files.channels[guild_id]:
        await reply(ctx, 'idk man as', mention=True)
        return
    files.channels[guild_id].remove(channel_id)
    if not files.channels[guild_id]:
        files.channels.pop(guild_id)
    files.write_channel()
    await reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['mod', 'ce', 'cheatengine', 'gg', 'gameguardian'])
async def modded(ctx):
    await reply(ctx, misc.mod_pasta)


@client.command(aliases=['suggestion', 's', 'request'])
async def suggest(ctx, *args):
    input = ' '.join([s.lower() for s in args])
    verofire = input.split('->')
    if len(verofire) != 2:
        await reply(ctx, 'idk man as', mention=True)
        return
    channel = client.get_channel(1018409476908392518)
    await channel.send(f'From {ctx.author.mention}:\n```{input}```')


@client.command(aliases=['cred', 'credit', 'credits'])
async def creds(ctx):
    embed = await embeds.creds_embed(client)
    await reply(ctx, embed=embed)


@client.command(aliases=['aphro', 'edttoaamo'])
async def aphrodite(ctx, num=None):
    def edttoaamo(n):
        if n > 1:
            return f'Enough. Drop the topic of "{edttoaamo(n - 1)}" and move on.'
        return 'Enough. Drop the topic of Aphrodite and move on.'
    if not num:
        if random.random() < 0:
            embed = discord.Embed(
                title='Drop',
                description='the',
                color=misc.god_colors['aphrodite']
            )
            embed.set_author(name='Enough.')
            embed.add_field(name='topic of', value='Aphrodite')
            embed.set_footer(text='and move on.')
            await reply(ctx, embed=embed)
        else:
            plt.clf()
            x_axis = [x / 2 for x in range(0, 21)]
            y_axis_1 = [10 - math.exp(x - 7.7) for x in x_axis]
            y_axis_2 = [10 - y for y in y_axis_1]
            plt.plot(x_axis, y_axis_1, label='Topic of Aphrodite', color='#FB91FC')
            plt.plot(x_axis, y_axis_2, label='Moving on', color='#000000')
            plt.title('Enough.')
            plt.xlabel('Time')
            plt.ylabel('Relevance')
            plt.xticks([])
            plt.yticks([])
            plt.legend()
            plt.savefig('output.png')
            await reply(ctx, file=discord.File('./output.png'))
    else:
        await reply(ctx, edttoaamo(int(num)))


async def reply(ctx, message='', embed=None, file=None, mention=False):
    try:
        guild_id = str(ctx.message.guild.id)
        if guild_id in files.channels and str(ctx.message.channel.id) not in files.channels[guild_id]:
            return
    except AttributeError:
        pass
    return await ctx.reply(message, embed=embed, file=file, mention_author=mention)


async def react_edit(ctx, embed, choices, embed_function):
    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in misc.disambig_select
    msg = await reply(ctx, embed=embed)
    for i in range(0, len(choices)):
        await msg.add_reaction(misc.disambig_select[i])
    try:
        react, _ = await client.wait_for('reaction_add', timeout=10.0, check=check)
    except asyncio.TimeoutError:
        await msg.clear_reactions()
        return
    embed, _ = embed_function([choices[misc.disambig_select.index(str(react.emoji))]])
    try:
        await msg.clear_reactions()
    except discord.errors.Forbidden:
        pass
    if embed == 'output.png':
        await msg.delete()
        await reply(ctx, file=discord.File('./output.png'))
        os.remove('output.png')
    else:
        await msg.edit(embed=embed)
    return


# from webserver import keep_alive
# keep_alive()
# TOKEN = os.environ['TOKEN']
from private.config import TOKEN
client.run(TOKEN)
