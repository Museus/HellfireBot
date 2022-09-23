import files
import parsing

rarity_graph_colors = ['#7D7D7D', '#0083F3', '#9500F6', '#FF1C10', '#FFD511']
rarity_embed_colors = [0xFFFFFF, 0x0083F3, 0x9500F6, 0xFF1C10, 0xFFD511, 0xD1FF18]
god_colors = {'zeus': 0xFCF75B, 'poseidon': 0x4AC4FB, 'athena': 0xF8C741, 'aphrodite': 0xFB91FC,
              'artemis': 0xD2FC61, 'ares': 0xFB2A2D, 'dionysus': 0xD111DE, 'demeter': 0xECFBFC,
              'hermes': 0xFBF7A7, 'bouldy': 0x3D4E46, 'duos': 0xD1FF18, 'hades': 0x9500F6,
              'chaos': 0x8783CF, 'charon': 0x5500B9, 'keepsake': 0x465B75}
god_icons = {'zeus': '1007940434129064019', 'poseidon': '1007940611850125393', 'athena': '1007940470627893338',
             'aphrodite': '1007940684231217173', 'artemis': '1007940543403262033', 'ares': '1007940354873507880',
             'dionysus': '1007940646373425182', 'demeter': '1007940575674241055', 'hermes': '1007940503179898990',
             'bouldy': '1014438782755422220', 'chaos': '1015394974088573038', 'charon': '1017340791011676170',
             'keepsake': '1018053070921412618'}
weapon_icons = {'sword': '1016977627485057034', 'spear': '1016977626201587763', 'shield': '1016977625081712660',
                'bow': '1016977619956277279', 'fists': '1016977621705314315', 'rail': '1016977623349469204'}
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


def fuzzy_boon(input: [str]) -> str:
    boon_name = ' '.join(input)
    if boon_name in files.boons_info:
        return boon_name
    if boon_name in files.aliases['misc'] and files.aliases['misc'][boon_name] in files.boons_info:
        return files.aliases['misc'][boon_name]
    for index, word in enumerate(input):
        if word in files.aliases['core']:
            input[index] = files.aliases['core'][word]
    if len(input) == 2:
        if input[0] in files.god_cores.keys() and input[1] in files.god_cores[input[0]].keys():
            return files.god_cores[input[0]][input[1]]
        if input[1] in files.god_cores.keys() and input[0] in files.god_cores[input[1]].keys():
            return files.god_cores[input[1]][input[0]]
    if ' '.join(input) in files.boons_info:
        return ' '.join(input)
    return ''


def adjust_boon_type(info: {}, boon_name: str, rarity: str, level: int) -> (str, str, int):
    if info['type'] in ('legendary', 'duo'):
        output = f'**{info["type"].upper()}** {boon_name.upper()}\n'
        rarity = 'common'
        level = 1
    else:
        if len(info['rarities']) == 3 and rarity == 'heroic':
            rarity = 'epic'
        if info['levels'][0] == '0':
            output = f'**{rarity.upper()}** {boon_name.upper()}\n'
            level = 1
        else:
            output = f'**{rarity.upper()}** {boon_name.upper()} LV.{level}\n'
    return output, rarity, level


def boon_value(info: {str: str}, rarity: str) -> [float]:
    value = [float(x) for x in info['rarities'][parsing.rarities[rarity] - 1].split('-')]
    if rarity != 'common':
        if len(value) == 2 or info['god'] == 'chaos':
            base_value = info['rarities'][0].split('-')
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
        for i in range(len(buffs)):
            rolls[i] += buffs[i]

    rolls = [0.12, 0.05, 0.1]
    chaos = False
    hermes = False
    if 'cosmic egg' or 'chaos' in input:
        rolls = [0.01, 0.05, 0.1]
        chaos = True
        if 'cosmic egg' in input:
            buff_rolls([0.1, 0.15, 0.4])
    elif 'miniboss' in input:
        rolls = [0.1, 0.25, 1]
    elif 'hermes' in input:
        rolls = [0.01, 0.03, 0.06]
        hermes = True
    if 'god keepsake' in input and not chaos and not hermes:
        buff_rolls([0.1, 0.1, 0.2])
    if 'olympian favor' in input:
        buff_rolls([0.1, 0.1, 0.2])
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
    return ' '.join((x[0].upper() + x[1:] if x.lower() not in ('of', 'the') else x.lower()) for x in s.split(' '))
