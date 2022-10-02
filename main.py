import asyncio
import copy
import difflib
import os
import random

import discord
from discord.ext import commands

import embeds
import files
import misc
import pactgen
import parsing
import randommirror
import randompact

client = commands.Bot(command_prefix=['h!', 'H!'], case_insensitive=True)
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
            await reply(ctx, f'h!{err} does not exist, use h!help to see a list of valid commands', True)
            return
        matches_str = ' or '.join([f'h!{match}' for match in matches])
        await reply(ctx, f'Did you mean {matches_str}?', True)
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
    await ctx.reply(embed=embed)


@client.command(aliases=['i'])
async def invite(ctx):
    await reply(ctx, 'https://discordapp.com/api/oauth2/authorize?scope=bot&client_id=1007141766979387432')


@client.command(aliases=['b'])
async def boon(ctx, *args):
    embed, choices = embeds.boon_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.boon_embed)
        return
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['ps', 'pom', 'poms'])
async def pomscaling(ctx, *args):
    embed, choices = embeds.pomscaling_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.pomscaling_embed)
        return
    await ctx.reply(file=discord.File('./output.png'), mention_author=False)
    os.remove('./output.png')


@client.command(aliases=['pre', 'pres', 'prereq', 'prereqs', 'prerequisite'])
async def prerequisites(ctx, *args):
    embed, choices = embeds.prereq_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.prereq_embed)
        return
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['a', 'weapon', 'w'])
async def aspect(ctx, *args):
    embed = embeds.aspect_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', True)
        return
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['h', 'hammers'])
async def hammer(ctx, *args):
    embed, choices = embeds.hammer_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.hammer_embed)
        return
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['g'])
async def god(ctx, *args):
    embed = embeds.god_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', True)
        return
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
    embed = embeds.define_embed(text)
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
    embed = embeds.random_chaos_embed(args)
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['char', 'well'])
async def charon(ctx, *args):
    embed = embeds.random_charon_embed(args)
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['k', 'keepsakes', 'companion', 'companions'])
async def keepsake(ctx, *args):
    embed, choices = embeds.keepsake_embed(args)
    if not embed:
        await reply(ctx, 'idk man as', True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.keepsake_embed)
        return
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
    embed = embeds.getpersonal_embed(ctx, user)
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


@client.command(aliases=['cred', 'credit', 'credits'])
async def creds(ctx):
    embed = await embeds.creds_embed(client)
    await ctx.reply(embed=embed, mention_author=False)


async def reply(ctx, message, mention=False):
    await ctx.reply(message, mention_author=mention)


async def react_edit(ctx, embed, choices, embed_function):
    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in misc.disambig_select
    msg = await ctx.reply(embed=embed)
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
        await ctx.reply(file=discord.File('./output.png'), mention_author=False)
        os.remove('output.png')
    else:
        await msg.edit(embed=embed)
    return


# from webserver import keep_alive
# keep_alive()
# TOKEN = os.environ['TOKEN']
from private.config import TOKEN

client.run(TOKEN)
