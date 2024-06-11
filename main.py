import asyncio
import difflib
import os
import re

import discord
from discord.ext import commands

import embeds
import files
import misc
import parsing

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
            await misc.reply(ctx, f'h!{err} does not exist, use h!help to see a list of valid commands', mention=True)
            return
        matches_str = ' or '.join([f'h!{match}' for match in matches])
        await misc.reply(ctx, f'Did you mean {matches_str}?', mention=True)
        return
    if isinstance(err, commands.MissingRequiredArgument):
        await misc.reply(ctx, 'Missing required input. Run h!help <command_name> for more information.', mention=True)
        return
    raise err


@client.event
async def on_ready():
    await client.change_presence()
    for command in files.commands_info:
        for alias in commands.Bot.get_command(client, command).aliases:
            aliases_to_command[alias] = command
    print(f'{client.user} is online')


@client.command(pass_context=True)
async def help(ctx, command_name=None):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed = embeds.help_embed(client, command_name, aliases_to_command)
    await misc.reply(ctx, embed=embed, mention=True)


@client.command(aliases=['i'])
async def invite(ctx):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    await misc.reply(ctx, 'https://discordapp.com/api/oauth2/authorize?scope=bot&client_id=1007141766979387432')


@client.command(aliases=['b'])
async def boon(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed, choices = embeds.boon_embed(args)
    if not embed:
        await misc.reply(ctx, misc.suggest_hint('boon'), mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.boon_embed)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['ps', 'pom', 'poms', 'pscale', 'pscaling'])
async def pomscaling(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed, choices = embeds.pomscaling_embed(args)
    if not embed:
        await misc.reply(ctx, misc.suggest_hint('boon'), mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.pomscaling_embed)
        return
    await misc.reply(ctx, file=discord.File('./output.png'))
    os.remove('./output.png')


@client.command(aliases=['pre', 'pres', 'prereq', 'prereqs', 'prerequisite'])
async def prerequisites(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    if not args:
        text = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        try:
            text = text.embeds[0].title
        except IndexError:
            await misc.reply(ctx, misc.suggest_hint('boon'), mention=True)
            return
        try:
            entity = re.findall(r'\*\*.*\*\*', text)[0]
        except IndexError:
            await misc.reply(ctx, 'idk man as', mention=True)
            return
        args = entity[2:-2].split()
    embed, choices = embeds.prereq_embed(args)
    if not embed:
        await misc.reply(ctx, misc.suggest_hint('boon'), mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.prereq_embed)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['rpre'])
async def eligible(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed = embeds.eligible_embed(args)
    if not embed:
        await misc.reply(ctx, misc.suggest_hint('boon'), mention=True)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['a', 'weapon', 'w'])
async def aspect(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed, choices = embeds.aspect_embed(args)
    if not embed:
        await misc.reply(ctx, misc.suggest_hint('aspect', an=True), mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.aspect_embed)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['h', 'hammers'])
async def hammer(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed, choices = embeds.hammer_embed(args)
    if not embed:
        await misc.reply(ctx, misc.suggest_hint('hammer'), mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.hammer_embed)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['g', 'gods'])
async def god(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed = embeds.god_embed(args)
    if not embed:
        await misc.reply(ctx, misc.suggest_hint('god'), mention=True)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['legendary', 'leg', 'legend', 'yellow'])
async def legendaries(ctx):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    await misc.reply(ctx, embed=embeds.legendaries_embed())


@client.command(aliases=['d', 'def', 'defs', 'defines', 'definition', 'definitions'])
async def define(ctx):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    if not ctx.message.reference:
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    text = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    try:
        text = text.embeds[0].description
    except IndexError:
        text = text.content
    if not isinstance(text, str):
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    embed = embeds.define_embed(text)
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['randomchaos', 'rchaos', 'rc', 'ch', 'chaos'])
async def randchaos(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed = embeds.random_chaos_embed(args)
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['randomcharon', 'rcharon', 'charon', 'char', 'well', 'randomwell', 'randwell', 'rwell'])
async def randcharon(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    await misc.reply(ctx, 'Not yet implemented', mention=True)
    # embed = embeds.random_charon_embed(args)
    # await misc.reply(ctx, embed=embed)


@client.command(aliases=['k', 'keepsakes', 'companion', 'companions'])
async def keepsake(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed, choices = embeds.keepsake_embed(args)
    if not embed:
        await misc.reply(ctx, misc.suggest_hint('keepsake'), mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.keepsake_embed)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['arcanas', 'c', 'card', 'cards', 'tarot', 'tarots'])
async def arcana(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed, choices = embeds.arcana_embed(args)
    if not embed:
        await misc.reply(ctx, misc.suggest_hint('arcana', an=True), mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.arcana_embed)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['e'])
async def enemy(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    await misc.reply(ctx, 'Not yet implemented', mention=True)
    # embed = embeds.enemy_embed(args)
    # if not embed:
    #     await misc.reply(ctx, misc.suggest_hint('enemy', an=True), mention=True)
    #     return
    # await misc.reply(ctx, embed=embed)


@client.command(aliases=['rarity', 'roll', 'rolls', 'rr'])
async def rarityrolls(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    modifiers = parsing.parse_modifiers(args)
    rolls = [int(min(r * 100, 100)) for r in misc.rarity_rolls(modifiers)]
    await misc.reply(ctx, parsing.parse_rarity_table(modifiers, rolls))


@client.command(aliases=['suggestion', 's', 'request'])
async def suggest(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    input = ' '.join([s.lower() for s in args])
    verofire = input.split('->')
    if len(verofire) != 2:
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    channel = client.get_channel(1018409476908392518)
    await channel.send(f'From {ctx.author.mention}:\n```{input}```')


@client.command(aliases=['cred', 'credit', 'credits'])
async def creds(ctx):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed = await embeds.creds_embed(client)
    await misc.reply(ctx, embed=embed)


async def react_edit(ctx, embed, choices, embed_function):
    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in misc.disambig_select
    msg = await misc.reply(ctx, embed=embed)
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
        await misc.reply(ctx, file=discord.File('./output.png'))
        os.remove('output.png')
    else:
        await msg.edit(embed=embed)
    return


# from webserver import keep_alive
# keep_alive()
# TOKEN = os.environ['TOKEN']
from private.config import TOKEN
client.run(TOKEN)
