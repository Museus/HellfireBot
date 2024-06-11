import discord

import files
import parsing

rarity_graph_colors = ['#7D7D7D', '#0083F3', '#9500F6', '#FF1C10', '#FFD511']
rarity_embed_colors = [0xFFFFFF, 0x0083F3, 0x9500F6, 0xFF1C10, 0xFFD511, 0xD1FF18]
# god_colors = {'zeus': 0xFCF75B, 'poseidon': 0x4AC4FB, 'athena': 0xF8C741, 'aphrodite': 0xFB91FC, 'artemis': 0xD2FC61,
#               'ares': 0xFB2A2D, 'dionysus': 0xD111DE, 'demeter': 0xECFBFC, 'apollo': 0xFF914F, 'hestia': 0x7B1635,
#               'hermes': 0xFBF7A7, 'bouldy': 0x3D4E46, 'duos': 0xD1FF18, 'hades': 0x9500F6, 'chaos': 0x8783CF,
#               'charon': 0x5500B9, 'keepsake': 0x465B75}
god_colors = {
    'aphrodite': 0xF767E9, 'apollo': 0xFEBF00, 'demeter': 0x99C9FE,
    'hephaestus': 0xA67430, 'hera': 0x00C6FD, 'hestia': 0xFF8E00,
    'poseidon': 0x59D5FE, 'zeus': 0xFFF254, 'duo': 0xD1FF18,
    'arachne': 0xC7F080, 'artemis': 0xD2FC61, 'chaos': 0x8783CF,
    'circe': 0xF2502E, 'echo': 0x8E8C7D, 'hades': 0x770D0A,
    'hermes': 0xFBF7A7, 'icarus': 0xAD9641, 'medea': 0x456B48,
    'selene': 0xB0FFFB, 'keepsake': 0x465B75, 'arcana': 0xCFCABA,
    'bouldy': 0x3D4E46
}
god_icons = {
    'aphrodite': 'thumb/1/10/Aphrodite_Boons.png/60px-Aphrodite_Boons.png',
    'apollo': 'thumb/5/55/Apollo_Boons.png/60px-Apollo_Boons.png',
    'demeter': 'thumb/2/27/Demeter_Boons.png/60px-Demeter_Boons.png',
    'hephaestus': 'thumb/1/13/Hephaestus_Boons.png/60px-Hephaestus_Boons.png',
    'hera': 'thumb/2/25/Hera_Boons.png/60px-Hera_Boons.png',
    'hestia': 'thumb/2/21/Hestia_Boons.png/60px-Hestia_Boons.png',
    'poseidon': 'thumb/4/4e/Poseidon_Boons.png/60px-Poseidon_Boons.png',
    'zeus': 'thumb/3/34/Zeus_Boons.png/60px-Zeus_Boons.png',
    'duo': '1027126357597093969',
    'arachne': '1249245758327095346',
    'artemis': 'thumb/2/2d/Artemis_Boons.png/60px-Artemis_Boons.png',
    'chaos': 'thumb/4/41/Chaos_Boons.png/60px-Chaos_Boons.png',
    'charon': '9/9a/Charon-bond-forged.png/revision/latest?cb=20201129185904',
    'circe': '1249245758327095346',
    'echo': '1249245758327095346',
    'hades': '1249245758327095346',
    'hermes': 'thumb/b/bd/Hermes_Boons.png/60px-Hermes_Boons.png',
    'icarus': 'thumb/f/fb/CodexPortrait_Icarus.png/350px-CodexPortrait_Icarus.png',
    'medea': '1249245758327095346',
    'selene': 'thumb/8/88/Selene_Boons.png/60px-Selene_Boons.png',
}
weapon_icons = {
    'staff': 'thumb/0/06/Witch%27s_Staff.png/300px-Witch%27s_Staff.png',
    'blades': '4/4a/Sister_Blades.png',
    'torch': 'thumb/b/b0/Umbral_Flames.png/300px-Umbral_Flames.png',
    'axe': 'thumb/1/1f/Moonstone_Axe.png/300px-Moonstone_Axe.png',
    'skull': 'thumb/8/8f/Argent_Skull_Art.png/300px-Argent_Skull_Art.png'
}
element_icons = {
    'earth': '1242225885390700604',
    'water': '1242225888519520377',
    'air': '1242224825079169165',
    'fire': '1242225886938533888',
    'aether': '1243121873408102471'
}
card_ranks = [
    (0x505858, '1247798358362554420'),
    (0x48DBFF, '1247798360870490204'),
    (0xFF86FF, '1247798359398416394'),
    (0xFF837C, '1248765071379660840')
]
disambig_select = (
    '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣',
    '🇦', '🇧', '🇨', '🇩', '🇪'
)
optout_dm = 'This channel has not opted into HellfireBot\'s commands (needs "h!optin" in the channel topic). ' \
            'However, all commands are usable via direct message.'
unfun_dm = 'This channel has not opted into HellfireBot\'s fun commands (needs "h!fun" in the channel topic). ' \
           'However, all commands are usable via direct message.'


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
    return value


def boon_color(info: {str: str}, rarity: str) -> int:
    if info['type'] == 'legendary':
        return 0xFFD511
    if info['type'] == 'infusion':
        return 0xF849F8
    if info['type'] == 'duo':
        return 0xD1FF18
    if info['god'] in ('arachne', 'charon', 'circe', 'echo', 'hades', 'icarus', 'medea', 'narcissus', 'selene'):
        return god_colors[info['god']]
    return rarity_embed_colors[parsing.rarities[rarity] - 1]


def rarity_rolls(input: [str]) -> [float]:
    def buff_rolls(buffs: [float]) -> None:
        for j in range(len(buffs)):
            rolls[j] += buffs[j]
    rolls = [0.1, 0.12, 0.05, 0.1]
    if 'erebus miniboss' in input:
        rolls = [0.05, 0.12, 0.07, 0.9]
    elif 'tartarus miniboss' in input:
        rolls = [0.2, 0.2, 0.1, 0.9]
    elif 'miniboss' in input:
        rolls = [0.05, 0.12, 0.1, 0.9]
    elif 'tartarus shop' in input:
        rolls = [0.1, 0.12, 0.25, 0.9]
    elif 'hermes' in input:
        rolls = [0.01, 0, 0.03, 0.06]
    if 'chaos favor' in input:
        buff_rolls([r * input.count('chaos favor') for r in [0.1, 0, 0.1, 0.4]])
    if 'yarn of ariadne' in input:
        buff_rolls([0.1, 0, 0.25, 1])
    if 'natural selection' in input:
        buff_rolls([0.1, 0, 0.1, 0.2])
    if 'excellence' in input:
        buff_rolls([0, 0, 0, 0.5])
    if 'divinity' in input:
        buff_rolls([0, 0, 0.2, 0])
    if 'the queen' in input:
        buff_rolls([0, 0.1, 0, 0])
    if 'hermes' in input or 'chaos' in input:
        rolls[1] = 0
    if 'chaos' in input:
        rolls[0] = 0.01875
    return rolls


def capwords(s: str, capall=False) -> str:
    if not s:
        return ''
    if capall:
        return ' '.join((x[0].upper()) + x[1:] for x in s.split(' '))
    return ' '.join((x[0].upper() + x[1:]
                     if x.lower() not in ('of', 'the', 'from', 'to') else x.lower()) for x in s.split(' '))


def to_link(s: str) -> str:
    if not s:
        return ''
    if s.isdigit():
        return f'https://cdn.discordapp.com/emojis/{s}.webp'
    return f'https://hades2.game-vault.net/w/images/{s}'


def channel_status(ctx):
    if isinstance(ctx.channel, discord.DMChannel) or 'h!fun' in ctx.channel.topic:
        return 0
    if 'h!optin' in ctx.channel.topic:
        return 1
    return 2


def suggest_hint(thing, an=False):
    return (f'Did you use an alias for {"an" if an else "a"} {thing} that didn\'t work? Try calling```h!suggest '
            f'<alias> -> <{thing} name>```to let the developer know!')


async def reply(ctx, message='', embed=None, file=None, mention=False):
    return await ctx.reply(message, embed=embed, file=file, mention_author=mention)
