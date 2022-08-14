import files

rarity_graph_colors = ['#7D7D7D', '#0083F3', '#9500F6', '#FF1C10', '#FFD511']
rarity_embed_colors = [0xFFFFFF, 0x0083F3, 0x9500F6, 0xFF1C10, 0xFFD511, 0xD1FF18, 0x8FFF18]
god_colors = {'zeus': 0xfcf75b, 'poseidon': 0x4ac4fb, 'athena': 0xf8c741, 'aphrodite': 0xfb91fc, 'artemis': 0xd2fc61,
              'ares': 0xfb2a2d, 'dionysus': 0xd111de, 'demeter': 0xecfbfc, 'hermes': 0xfbf7a7}
god_icons = {'zeus': 'https://cdn.discordapp.com/emojis/1007940434129064019.webp?size=96&quality=lossless',
             'poseidon': 'https://cdn.discordapp.com/emojis/1007940611850125393.webp?size=96&quality=lossless',
             'athena': 'https://cdn.discordapp.com/emojis/1007940470627893338.webp?size=96&quality=lossless',
             'aphrodite': 'https://cdn.discordapp.com/emojis/1007940684231217173.webp?size=96&quality=lossless',
             'artemis': 'https://cdn.discordapp.com/emojis/1007940543403262033.webp?size=96&quality=lossless',
              'ares': 'https://cdn.discordapp.com/emojis/1007940354873507880.webp?size=96&quality=lossless',
             'dionysus': 'https://cdn.discordapp.com/emojis/1007940646373425182.webp?size=96&quality=lossless',
             'demeter': 'https://cdn.discordapp.com/emojis/1007940575674241055.webp?size=96&quality=lossless',
             'hermes': 'https://cdn.discordapp.com/emojis/1007940503179898990.webp?size=96&quality=lossless'}


def fuzzy_boon(input: [str]) -> str:
    boon_name = ' '.join(input)
    if boon_name in files.boons_info:
        return boon_name
    if boon_name in files.misc_aliases and files.misc_aliases[boon_name] in files.boons_info:
        return files.misc_aliases[boon_name]
    for index, word in enumerate(input):
        if word in files.core_aliases:
            input[index] = files.core_aliases[word]
    if len(input) >= 2:
        if input[0] in files.god_cores.keys() and input[1] in files.god_cores[input[0]].keys():
            return files.god_cores[input[0]][input[1]]
        if input[1] in files.god_cores.keys() and input[0] in files.god_cores[input[1]].keys():
            return files.god_cores[input[1]][input[0]]
    if ' '.join(input) in files.boons_info:
        return ' '.join(input)
    return ''


def adjust_boon_type(info: {}, boon_name: str, rarity: str, level: int) -> (str, str, int):
    if info['type'] in ['legendary', 'duo']:
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
