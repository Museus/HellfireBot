boons_info = {}
bouldy_info = []
aspects_info = {}
core_aliases = {}
misc_aliases = {}
aspect_aliases = {}
god_cores = {'zeus': {}, 'poseidon': {}, 'athena': {}, 'aphrodite': {}, 'artemis': {},
             'ares': {}, 'dionysus': {}, 'demeter': {}, 'hermes': {}, 'duos': None}

for god in god_cores.keys():
    f = open(f'./files/gods/{god}.txt', 'r', encoding='utf8')
    while boon := f.readline().strip():
        type, boon = boon.split(' ', 1)
        if type in ['attack', 'special', 'cast', 'flare', 'dash', 'call', 'status', 'revenge', 'legendary']:
            god_cores[god][type] = boon
        boons_info[boon] = {'god': god, 'type': type, 'desc': f.readline().strip(), 'stat': f.readline().strip(),
                            'rarities': f.readline().strip().split(' '), 'levels': f.readline().strip().split(' '),
                            'icon': f.readline().strip()}
f = open(f'./files/gods/bouldy.txt', 'r', encoding='utf8')
while f.readline():
    bouldy_info.append({'desc': f.readline().strip(), 'stat': f.readline().strip(), 'icon': f.readline().strip()})

f = open(f'./files/aspects.txt', 'r', encoding='utf8')
while aspect := f.readline().strip():
    aspects_info[aspect] = {'desc': f.readline().strip(), 'stat': f.readline().strip(),
                            'levels': f.readline().strip().split(' '), 'flavor': f.readline().strip(),
                            'icon': f.readline().strip()}

f = open('./files/corealiases.txt', 'r', encoding='utf8')
while name := f.readline().strip():
    aliases = f.readline().strip().split(', ')
    if aliases[0]:
        for alias in aliases:
            if alias in core_aliases:
                print(f'duplicate alias: {alias}')
            core_aliases[alias] = name

f = open('./files/boonaliases.txt', 'r', encoding='utf8')
while name := f.readline().strip():
    aliases = f.readline().strip().split(', ')
    if aliases[0]:
        for alias in aliases:
            if alias in misc_aliases:
                print(f'duplicate alias: {alias}')
            misc_aliases[alias] = name

f = open('./files/aspectaliases.txt', 'r', encoding='utf8')
while name := f.readline().strip():
    aliases = f.readline().strip().split(', ')
    if aliases[0]:
        for alias in aliases:
            if alias in aspect_aliases:
                print(f'duplicate alias: {alias}')
            aspect_aliases[alias] = name
