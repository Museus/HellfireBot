import asyncio
import difflib
import os

import discord
from discord.ext import commands

import arcanagen
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
    if isinstance(err, commands.PrivateMessageOnly):
        await ctx.author.send('This command can only be used in private messages.')
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
@commands.dm_only()
async def invite(ctx):
    await misc.reply(ctx, 'https://discordapp.com/api/oauth2/authorize?scope=bot&client_id=1007734213904183306')


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


@client.command(aliases=['duo', 'double', 'green'])
async def duos(ctx):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    await misc.reply(ctx, embed=embeds.duos_embed())


@client.command(aliases=['d', 'def', 'defs', 'defines', 'definition', 'definitions'])
async def define(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    if ctx.message.reference:
        text = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        try:
            text = text.embeds[0].description
        except IndexError:
            text = text.content
        if not isinstance(text, str):
            await misc.reply(ctx, 'idk man as', mention=True)
            return
    else:
        text = f'**{misc.capwords(" ".join(args))}**'
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


@client.command(aliases=['vows', 'oath', 'oaths', 'pact', 'pacts', 'fear', 'heat', 'v'])
async def vow(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed, choices = embeds.vow_embed(args)
    if not embed:
        await misc.reply(ctx, misc.suggest_hint('vow'), mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.vow_embed)
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
    args = ' '.join(s.lower() for s in args)
    verofire = args.split('->')
    if len(verofire) != 2:
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    channel = client.get_channel(1018409476908392518)
    await channel.send(f'From {ctx.author.mention}:\n```{args}```')
    await misc.reply(ctx, 'Thank you for your contribution!')


@client.command(aliases=['bug', 'bugreport', 'bugs', 'reports'])
async def report(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    args = ' '.join(args)
    channel = client.get_channel(1025559977227714720)
    await channel.send(f'From {ctx.author.mention}:\n```{args}```')
    await misc.reply(ctx, 'Thank you for your contribution!')


@client.command(aliases=[
    'loadout', 'loadouts', 'arcanaloadouts', 'aload', 'arcload', 'arcloadout', 'arcanagen', 'arcgen']
)
async def arcanaloadout(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    if len(args) == 1 and not args[0].isdigit():
        args = args[0]
    total_grasp = arcanagen.arcana_gen(str(ctx.message.author.id), args)
    if total_grasp == -1:
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    await misc.reply(
        ctx, f'Total grasp: **{total_grasp}** <:Grasp:1250935195700563978>', file=discord.File('./temp.png')
    )
    os.remove('./temp.png')


@client.command(aliases=[
    'randomarcana', 'rarcana', 'randomloadout', 'randloadout', 'rloadout',
    'randomcards','randcards', 'rcards', 'randomcard', 'randcard', 'rcard'
])
async def randarcana(ctx, total_grasp=30):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    loadout = arcanagen.rand_arcana(int(total_grasp))
    total_grasp = arcanagen.arcana_gen('', list(map(str, loadout)))
    await misc.reply(
        ctx, f'Total grasp: **{total_grasp}** <:Grasp:1250935195700563978>', file=discord.File('./temp.png')
    )
    os.remove('./temp.png')


@client.command(aliases=['addloadout'])
@commands.dm_only()
async def addarcana(ctx, name, *args):
    binary = ''.join('1' if str(c) in args else '0' for c in range(1, 26))
    uid = str(ctx.message.author.id)
    if uid not in files.saved_arcana['personal']:
        files.saved_arcana['personal'][uid] = {}
    files.saved_arcana['personal'][uid][name] = binary
    files.write_personal()
    total_grasp = arcanagen.arcana_gen(str(ctx.message.author.id), name)
    if total_grasp == -1:
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    await misc.reply(
        ctx, f'Total grasp: **{total_grasp}** <:Grasp:1250935195700563978>', file=discord.File('./temp.png')
    )
    os.remove('./temp.png')


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
        react, _ = await client.wait_for('reaction_add', timeout=30.0, check=check)
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