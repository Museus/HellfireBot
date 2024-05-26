import asyncio
import os
import re

import discord
import requests
from PIL import Image
from discord import HTTPException

import files
import parsing

rarity_graph_colors = ['#7D7D7D', '#0083F3', '#9500F6', '#FF1C10', '#FFD511']
rarity_embed_colors = [0xFFFFFF, 0x0083F3, 0x9500F6, 0xFF1C10, 0xFFD511, 0xD1FF18]
god_colors = {'zeus': 0xFCF75B, 'poseidon': 0x4AC4FB, 'athena': 0xF8C741, 'aphrodite': 0xFB91FC, 'artemis': 0xD2FC61,
              'ares': 0xFB2A2D, 'dionysus': 0xD111DE, 'demeter': 0xECFBFC, 'apollo': 0xFF914F, 'hestia': 0x7B1635,
              'hermes': 0xFBF7A7, 'bouldy': 0x3D4E46, 'duos': 0xD1FF18, 'hades': 0x9500F6, 'chaos': 0x8783CF,
              'charon': 0x5500B9, 'keepsake': 0x465B75}
god_icons = {
    'aphrodite': 'thumb/1/10/Aphrodite_Boons.png/60px-Aphrodite_Boons.png',
    'apollo': 'thumb/5/55/Apollo_Boons.png/60px-Apollo_Boons.png',
    'demeter': 'thumb/2/27/Demeter_Boons.png/60px-Demeter_Boons.png',
    'hephaestus': 'thumb/1/13/Hephaestus_Boons.png/60px-Hephaestus_Boons.png',
    'hera': 'thumb/2/25/Hera_Boons.png/60px-Hera_Boons.png',
    'hestia': 'thumb/2/21/Hestia_Boons.png/60px-Hestia_Boons.png',
    'poseidon': 'thumb/4/4e/Poseidon_Boons.png/60px-Poseidon_Boons.png',
    'zeus': 'thumb/3/34/Zeus_Boons.png/60px-Zeus_Boons.png',
    'duos': '1027126357597093969',
    'artemis': 'thumb/2/2d/Artemis_Boons.png/60px-Artemis_Boons.png',
    'chaos': 'thumb/4/41/Chaos_Boons.png/60px-Chaos_Boons.png',
    'hermes': 'thumb/b/bd/Hermes_Boons.png/60px-Hermes_Boons.png',
    'selene': 'thumb/8/88/Selene_Boons.png/60px-Selene_Boons.png',
    'charon': '9/9a/Charon-bond-forged.png/revision/latest?cb=20201129185904',
}
weapon_icons = {'sword': 'f/f7/Stygian_Blade.png/revision/latest?cb=20181213044607',
                'spear': 'c/c1/Eternal_Spear.png/revision/latest?cb=20181214234725',
                'shield': '0/02/Shield_of_Chaos.png/revision/latest?cb=20181213193429',
                'bow': '5/5c/Heart-Seeker_Bow.png/revision/latest?cb=20181213193638',
                'fists': '0/08/Twin_Fists.png/revision/latest?cb=20200430070608',
                'rail': '3/36/Adamant_Rail.png/revision/latest?cb=20210120004027'}
element_icons = {
    'earth': '1242225885390700604',
    'water': '1242225888519520377',
    'air': '1242224825079169165',
    'fire': '1242225886938533888',
    'aether': '1243121873408102471'
}
disambig_select = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣')
toxic_select = ('⬆️', '➡️', '↔️', '🔄', '🔴', '🔹', '✅')
mod_pasta = 'if you want to download the speedrunning modpack it is available at ' \
            'https://www.speedrun.com/hades/resources\n' \
            'all of its features can be toggled on or off and it includes:\n' \
            '- guaranteed 2 sack\n' \
            '- guaranteed first hammer\n' \
            '- first boon offers all 4 core boons\n' \
            '- removes tiny vermin, asterius, and barge of death minibosses\n' \
            '- shows fountain rooms\n' \
            'there are also a few qol features such as a quick reset feature and the ability to toggle hell ' \
            'mode, as well as a colorblind mode.\n\n' \
            'instructions for downloading the modpack are in the ' \
            'file "instructions.txt" in the modpack folder'
optout_dm = 'This channel has not opted into HellfireBot\'s commands (needs "h!optin" in the channel topic). ' \
            'However, all commands are usable via direct message.'
unfun_dm = 'This channel has not opted into HellfireBot\'s fun commands (needs "h!fun" in the channel topic). ' \
           'However, all commands are usable via direct message.'
output_count = 0


def fuzzy_boon(input: [str]) -> [str]:
    boon_name = ' '.join(input)
    if boon_name in files.boons_info:
        return [boon_name]
    if boon_name in files.aliases['misc']:
        return files.aliases['misc'][boon_name]
    for index, word in enumerate(input):
        if word in files.aliases['core']:
            input[index] = files.aliases['core'][word][0]
    if len(input) == 2:
        if input[0] in files.god_cores and input[1] in files.god_cores[input[0]]:
            return files.god_cores[input[0]][input[1]]
        if input[1] in files.god_cores and input[0] in files.god_cores[input[1]]:
            return files.god_cores[input[1]][input[0]]
    if ' '.join(input) in files.boons_info:
        return [' '.join(input)]
    return ''


def boon_value(info: {str: str}, rarity: str, second: bool = False) -> [float]:
    try:
        value = [float(x) for x in info['rarities2' if second else 'rarities'][parsing.rarities[rarity] - 1].split('-')]
    except IndexError:
        return None
    if rarity != 'common':
        if len(value) == 2 or info['god'] == 'chaos':
            base_value = info['rarities2' if second else 'rarities'][0].split('-')
            value = [float(base_value[0]) * value[0], float(base_value[-1]) * value[-1]]
    return value


def boon_color(info: {str: str}, rarity: str) -> int:
    if info['type'] == 'legendary':
        return 0xFFD511
    if info['type'] == 'duo':
        return 0xD1FF18
    if info['god'] == 'hades':
        return 0x9500F6
    if info['god'] == 'bouldy':
        return 0x3D4E46
    if info['god'] == 'charon':
        return 0x5500B9
    return rarity_embed_colors[parsing.rarities[rarity] - 1]


def rarity_rolls(input: [str]) -> [float]:
    def buff_rolls(buffs: [float]) -> None:
        for j in range(len(buffs)):
            rolls[j] += buffs[j]
    rolls = [0.12, 0.05, 0.1]
    chaos = False
    hermes = False
    if 'cosmic egg' in input or 'chaos' in input:
        rolls = [0.01, 0.05, 0.1]
        chaos = True
        if 'cosmic egg' in input:
            buff_rolls([0.1, 0.15, 0.4])
    elif 'tartarus miniboss' in input:
        rolls = [0.1, 0.25, 1]
        hermes = 'hermes' in input
    elif 'miniboss' in input:
        rolls = [0.1, 0.25, 0.9]
        hermes = 'hermes' in input
    elif 'hermes' in input:
        rolls = [0.01, 0.03, 0.06]
        hermes = True
    if 'god keepsake' in input and not chaos and not hermes:
        buff_rolls([0.1, 0.1, 0.2])
    if 'chaos favor' in input:
        buff_rolls([r * input.count('chaos favor') for r in [0.1, 0.1, 0.2]])
    if 'yarn of ariadne' in input or 'refreshing nectar' in input:
        buff_rolls([0.1, 0.25, 1])
    if 'exclusive access' in input:
        buff_rolls([0, 1, 0])
    if 'olympian favor' in input:
        buff_rolls([0, 0, 0.4])
    if 'god\'s pride' in input:
        buff_rolls([0, 0.2, 0])
    elif 'god\'s legacy' in input:
        buff_rolls([0.1, 0, 0])
    return rolls


def capwords(s: str) -> str:
    if s == 'hydralite':
        return 'HydraLite'
    if s == 'point-blank shot':
        return 'Point-Blank Shot'
    if s == 'dash-strike':
        return 'Dash-Strike'
    if s == 'dash-upper':
        return 'Dash-Upper'
    return ' '.join((x[0].upper() + x[1:] if x.lower() not in ('of', 'the') else x.lower()) for x in s.split(' '))


def to_link(s: str) -> str:
    if not s:
        return ''
    if s.isdigit():
        return f'https://cdn.discordapp.com/emojis/{s}.webp'
    return f'https://hades2.game-vault.net/w/images/{s}'


async def fuzzy_img(ctx, client, img_link):
    if not img_link:
        try:
            img_link = ctx.message.attachments[0].url
        except IndexError:
            try:
                replied = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                try:
                    img_link = replied.attachments[0].url
                except IndexError:
                    try:
                        img_link = replied.embeds[0].thumbnail.url
                        if not img_link:
                            img_link = replied.author.avatar.url
                    except IndexError:
                        img_link = replied.author.avatar.url
            except AttributeError:
                img_link = ctx.author.avatar.url
    elif img_link[:2] == '<:':
        img_link = client.get_emoji(int(img_link.split(":")[-1][:-1])).url
    else:
        try:
            user_id = int(re.sub('[^0-9]', '', img_link))
            user = client.get_user(user_id)
            if not user:
                user = await client.fetch_user(user_id)
            img_link = user.avatar.url
        except HTTPException:
            pass
    return img_link


def toxic(img_url, x=250, y=250, s=200, r=0):
    global output_count
    req = requests.get(img_url)
    output_count += 1
    with open(f'./output{output_count}.png', 'wb') as out_img:
        out_img.write(req.content)
    img = Image.open(f'./output{output_count}.png')
    xic = Image.open('./files/xic.png')
    if img.size[0] > img.size[1]:
        ratio = 500 / img.size[1]
        img = img.resize((int(img.size[0] * ratio), 500), Image.LANCZOS)
    else:
        ratio = 500 / img.size[0]
        img = img.resize((500, int(img.size[1] * ratio)), Image.LANCZOS)
    xic = xic.resize((s, s), Image.LANCZOS)
    xic = xic.rotate(r, expand=True)
    img.paste(xic, (int(x - xic.size[0] / 2), int(y - xic.size[1] / 2)), xic.convert('RGBA'))
    img.save(f'./output{output_count}.png')
    return f'./output{output_count}.png'


async def toxic_react(ctx, client, embed, img_link):
    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in toxic_select
    msg = await reply(ctx, embed=embed)
    for emoji in toxic_select:
        await msg.add_reaction(emoji)
    x = 250
    y = 250
    s = 200
    r = 0
    neg = False
    small = False
    while True:
        try:
            react, _ = await client.wait_for('reaction_add', timeout=300.0, check=check)
        except asyncio.TimeoutError:
            try:
                await msg.clear_reactions()
            except discord.errors.Forbidden:
                pass
            return
        index = toxic_select.index(str(react.emoji))
        if index == 6:
            try:
                await msg.delete()
            except discord.errors.Forbidden:
                pass
            output_name = toxic(img_link, x, y, s, r)
            await reply(ctx, file=discord.File(output_name))
            os.remove(output_name)
            return
        else:
            try:
                await msg.remove_reaction(str(react.emoji), ctx.message.author)
            except discord.errors.Forbidden:
                pass
            if index == 0:
                amount = 10 if small else 50
                y -= -amount if neg else amount
            elif index == 1:
                amount = 10 if small else 50
                x += -amount if neg else amount
            elif index == 2:
                amount = 20 if small else 100
                s += -amount if neg else amount
                s = max(s, 0)
            elif index == 3:
                amount = 5 if small else 25
                r += -amount if neg else amount
            elif index == 4:
                neg = not neg
            elif index == 5:
                small = not small
        output_name = toxic(img_link, x, y, s, r)
        channel = client.get_channel(1059334747832201266)
        file_msg = await channel.send(file=discord.File(output_name))
        os.remove(output_name)
        embed = discord.Embed()
        embed.set_image(url=file_msg.attachments[0].url)
        embed.add_field(name='Negate mode', value='On' if neg else 'Off', inline=False)
        embed.add_field(name='Small mode', value='On' if small else 'Off', inline=False)
        await msg.edit(embed=embed)


def channel_status(ctx):
    if isinstance(ctx.channel, discord.DMChannel) or 'h!fun' in ctx.channel.topic:
        return 0
    if 'h!optin' in ctx.channel.topic:
        return 1
    return 2


async def reply(ctx, message='', embed=None, file=None, mention=False):
    return await ctx.reply(message, embed=embed, file=file, mention_author=mention)
