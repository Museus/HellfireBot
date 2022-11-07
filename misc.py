import files
import parsing

rarity_graph_colors = ['#7D7D7D', '#0083F3', '#9500F6', '#FF1C10', '#FFD511']
rarity_embed_colors = [0xFFFFFF, 0x0083F3, 0x9500F6, 0xFF1C10, 0xFFD511, 0xD1FF18]
god_colors = {'zeus': 0xFCF75B, 'poseidon': 0x4AC4FB, 'athena': 0xF8C741, 'aphrodite': 0xFB91FC, 'artemis': 0xD2FC61,
              'ares': 0xFB2A2D, 'dionysus': 0xD111DE, 'demeter': 0xECFBFC, 'apollo': 0xFF914F, 'hestia': 0x7B1635,
              'hermes': 0xFBF7A7, 'bouldy': 0x3D4E46, 'duos': 0xD1FF18, 'hades': 0x9500F6, 'chaos': 0x8783CF,
              'charon': 0x5500B9, 'keepsake': 0x465B75}
god_icons = {'zeus': 'f/f4/Zeus-bond-forged.png/revision/latest?cb=20201129190802',
             'poseidon': '6/6d/Poseidon-bond-forged.png/revision/latest?cb=20201129190617',
             'athena': '1/15/Athena-bond-forged.png/revision/latest?cb=20201129185736',
             'aphrodite': '8/85/Aphrodite-bond-icon.png/revision/latest?cb=20201129185343',
             'artemis': '8/89/Artemis-bond-forged.png/revision/latest?cb=20201129185707',
             'ares': '7/7e/Ares-bond-icon.png/revision/latest?cb=20201129185523',
             'dionysus': '8/81/Dionysus-bond-forged.png/revision/latest?cb=20201129190028',
             'demeter': '0/04/Demeter-bond-forged.png/revision/latest?cb=20201129190001',
             'hermes': 'f/fd/Hermes-bond-forged.png/revision/latest?cb=20201129190309',
             'bouldy': '1014438782755422220', 'duos': '1027126357597093969',
             'chaos': '7/7a/Chaos-bond-forged.png/revision/latest?cb=20201129185835',
             'charon': '9/9a/Charon-bond-forged.png/revision/latest?cb=20201129185904',
             'apollo': 'Apollo/Apollo/ApolloBadge_max.png?raw=true',
             'hestia': 'Hestia/Hestia/HestiaBadge_max.PNG?raw=true'}
weapon_icons = {'sword': 'f/f7/Stygian_Blade.png/revision/latest?cb=20181213044607',
                'spear': 'c/c1/Eternal_Spear.png/revision/latest?cb=20181214234725',
                'shield': '0/02/Shield_of_Chaos.png/revision/latest?cb=20181213193429',
                'bow': '5/5c/Heart-Seeker_Bow.png/revision/latest?cb=20181213193638',
                'fists': '0/08/Twin_Fists.png/revision/latest?cb=20200430070608',
                'rail': '3/36/Adamant_Rail.png/revision/latest?cb=20210120004027'}
disambig_select = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣')
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
    if s[1] == '/':
        return f'https://static.wikia.nocookie.net/hades_gamepedia_en/images/{s}'
    return f'https://github.com/AlexKage69/OlympusExtra/blob/AssetsLab/AssetsLab/PackMe/{s}'
