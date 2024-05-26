import asyncio
import copy
import difflib
import math
import os
import random

import discord
from discord.ext import commands
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
        await misc.reply(ctx, 'idk man as', mention=True)
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
        await misc.reply(ctx, 'idk man as', mention=True)
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
    embed, choices = embeds.prereq_embed(args)
    if not embed:
        await misc.reply(ctx, 'idk man as', mention=True)
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
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['a', 'weapon', 'w'])
async def aspect(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed, choices = embeds.aspect_embed(args)
    if not embed:
        await misc.reply(ctx, 'idk man as', mention=True)
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
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.hammer_embed)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['g'])
async def god(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed = embeds.god_embed(args)
    if not embed:
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['legendary', 'leg', 'legend', 'yellow'])
async def legendaries(ctx):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    await misc.reply(ctx, embed=embeds.legendaries_embed())


@client.command(aliases=['bp'])
async def benefitspackage(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed = embeds.bpperk_embed(args)
    if not embed:
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    await misc.reply(ctx, embed=embed)


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


@client.command(aliases=['randomchaos', 'rchaos', 'c', 'ch', 'chaos'])
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
    embed = embeds.random_charon_embed(args)
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['k', 'keepsakes', 'companion', 'companions'])
async def keepsake(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed, choices = embeds.keepsake_embed(args)
    if not embed:
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    if choices:
        await react_edit(ctx, embed, choices, embeds.keepsake_embed)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['e'])
async def enemy(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed = embeds.enemy_embed(args)
    if not embed:
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['rarity', 'roll', 'rolls'])
async def rarityrolls(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    modifiers = parsing.parse_modifiers(args)
    rolls = [int(min(r * 100, 100)) for r in misc.rarity_rolls(modifiers)]
    await misc.reply(ctx, parsing.parse_rarity_table(modifiers, rolls))


@client.command(aliases=['p'])
async def pact(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    total_heat = pactgen.pact_gen(str(ctx.message.author.id), args)
    await misc.reply(ctx, f'Total heat: **{total_heat}**', file=discord.File('./temp.png'))
    os.remove('./temp.png')


@client.command(aliases=['r', 'rand', 'random', 'randompact', 'rpact'])
async def randpact(ctx, total_heat, hell=None):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    total_heat = int(total_heat)
    if total_heat < (5 if hell else 0) or total_heat > (64 if hell else 63):
        await misc.reply(ctx, 'idk man as', True)
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
    await misc.reply(ctx, f'Total heat: **{total_heat}**', file=discord.File('./temp.png'))
    os.remove('./temp.png')


@client.command(aliases=['m'])
async def mirror(ctx, *args):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    randommirror.random_mirror(str(ctx.message.author.id), ' '.join(args))
    await misc.reply(ctx, file=discord.File('./temp.png'))
    os.remove('./temp.png')


@client.command(aliases=['personal', 'gp'])
async def getpersonal(ctx, user: discord.Member = None):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    embed = embeds.getpersonal_embed(ctx, user)
    await misc.reply(ctx, embed=embed)


@client.command(aliases=['addp', 'ap'])
@commands.dm_only()
async def addpact(ctx, name, *args):
    id = str(ctx.message.author.id)
    if id not in files.personal:
        files.personal[id] = {'mirrors': {}, 'pacts': {}}
    files.personal[id]['pacts'][name] = list(args)
    files.write_personal()
    await misc.reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['addm', 'am'])
@commands.dm_only()
async def addmirror(ctx, name, *args):
    mirror_binary = ''.join(args)
    if len(mirror_binary) != 12 or not all(c in '01' for c in mirror_binary):
        await misc.reply(ctx, 'idk man as', mention=True)
        return
    id = str(ctx.message.author.id)
    if id not in files.personal:
        files.personal[id] = {'mirrors': {}, 'pacts': {}}
    files.personal[id]['mirrors'][name] = mirror_binary
    files.write_personal()
    await misc.reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['deletep', 'dp', 'removepact', 'removep', 'rp'])
@commands.dm_only()
async def deletepact(ctx, *args):
    name = ' '.join(args)
    id = str(ctx.message.author.id)
    if id not in files.personal or name not in files.personal[id]['pacts']:
        await misc.reply(ctx, 'No pact with matching name', mention=True)
        return
    files.personal[id]['pacts'].pop(name)
    files.write_personal()
    await misc.reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['deletem', 'dm', 'removemirror', 'removem', 'rm'])
@commands.dm_only()
async def deletemirror(ctx, *args):
    name = ' '.join(args)
    id = str(ctx.message.author.id)
    if id not in files.personal or name not in files.personal[id]['mirrors']:
        await misc.reply(ctx, 'No mirror with matching name', mention=True)
        return
    files.personal[id]['mirrors'].pop(name)
    files.write_personal()
    await misc.reply(ctx, 'special only rama is unaruably')


@client.command(aliases=['mod', 'ce', 'cheatengine', 'gg', 'gameguardian'])
async def modded(ctx):
    if misc.channel_status(ctx) > 1:
        await ctx.author.send(misc.optout_dm)
        return
    await misc.reply(ctx, misc.mod_pasta)


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


@client.command(aliases=['aphro', 'edttoaamo'])
async def aphrodite(ctx, num=None):
    def edttoaamo(n):
        if n > 1:
            return f'Enough. Drop the topic of "{edttoaamo(n - 1)}" and move on.'
        return 'Enough. Drop the topic of Aphrodite and move on.'
    if misc.channel_status(ctx) > 0:
        await ctx.author.send(misc.unfun_dm)
        return
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
            await misc.reply(ctx, embed=embed)
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
            await misc.reply(ctx, file=discord.File('./output.png'))
            os.remove('./output.png')
    else:
        await misc.reply(ctx, edttoaamo(int(num)))


@client.command(aliases=['xic'])
async def toxic(ctx, img_link=None):
    if misc.channel_status(ctx) > 0:
        await ctx.author.send(misc.unfun_dm)
        return
    img_link = await misc.fuzzy_img(ctx, client, img_link)
    output_name = misc.toxic(img_link)
    channel = client.get_channel(1059334747832201266)
    msg = await channel.send(file=discord.File(output_name))
    os.remove(output_name)
    embed = discord.Embed()
    embed.set_image(url=msg.attachments[0].url)
    embed.add_field(name='Negate mode', value='Off', inline=False)
    embed.add_field(name='Small mode', value='Off', inline=False)
    await misc.toxic_react(ctx, client, embed, img_link)


@client.command(aliases=['fc'])
async def firecredits(ctx, diff, *users: discord.Member):
    server_name = ctx.guild.name
    if (server_name == 'BTD6 Index' or server_name == 'hadestest') and ctx.message.author.id == 279126808455151628:
        reply_fc = False
        replied = None
        if not users:
            replied = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            user = ctx.guild.get_member(replied.author.id)
            if not user:
                user = await ctx.guild.fetch_member(replied.author.id)
            users = [user]
            reply_fc = True
        fc_roles = [str(2 ** x) for x in range(0, 10)]
        diff = int(diff)
        output = {}
        max_display = -1
        for user in users:
            old_fc = 0
            for role in user.roles:
                if role.name in fc_roles:
                    old_fc += int(role.name)
            new_fc = min(max(old_fc + diff, 1), 1023)
            new_roles = []
            temp = new_fc
            for i in range(9, -1, -1):
                if 2 ** i <= temp:
                    temp -= 2 ** i
                    new_roles.append(i)
            to_remove = []
            for role in user.roles:
                if role.name in fc_roles:
                    old_index = fc_roles.index(role.name)
                    if old_index not in new_roles:
                        to_remove.append(role)
                    else:
                        new_roles.remove(old_index)
            await user.remove_roles(*to_remove)
            to_add = []
            for index in new_roles:
                new_role = discord.utils.get(ctx.message.guild.roles, name=str(2 ** index))
                to_add.append(new_role)
            await user.add_roles(*to_add)
            output[user.display_name] = '{:<2} → {:<2}'.format(old_fc, new_fc)
            if len(user.display_name) > max_display:
                max_display = len(user.display_name)
        output_str = '```'
        output_str += '\n'.join(map(lambda x: '{name:>{width}}\'s firecredit score: {res}'
                                    .format(name=x, width=max_display, res=output[x]), output))
        output_str += '```'
        if not reply_fc:
            await misc.reply(ctx, output_str)
        else:
            await ctx.message.delete()
            await ctx.send(output_str, reference=replied, mention_author=False)


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
