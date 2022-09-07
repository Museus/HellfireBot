import misc

boons_info = {}
bouldy_info = []
aspects_info = {}
hammers_info = {}
prereq_info = {}
core_aliases = {}
misc_aliases = {}
aspect_aliases = {}
hammer_aliases = {}
god_cores = {'zeus': {}, 'poseidon': {}, 'athena': {}, 'aphrodite': {}, 'artemis': {},
             'ares': {}, 'dionysus': {}, 'demeter': {}, 'hermes': {}, 'chaos': {}, 'duos': None}

for god in god_cores:
    f = open(f'./files/gods/{god}.txt', 'r', encoding='utf8')
    while boon := f.readline().strip():
        type, boon = boon.split(' ', 1)
        has_prereq = type not in ['attack', 'special', 'cast', 'flare', 'dash', 'call', 'revenge', 't1', 'misc', 'blessing', 'curse']
        if type[0] == 'x':
            type = type[1:]
        if type in ['attack', 'special', 'cast', 'flare', 'dash', 'call', 'status', 'revenge', 'legendary']:
            god_cores[god][type] = boon
        boons_info[boon] = {'god': god, 'type': type, 'desc': f.readline().strip(), 'stat': f.readline().strip(),
                            'rarities': f.readline().strip().split(' '), 'levels': f.readline().strip().split(' '),
                            'icon': f.readline().strip()}
        if has_prereq:
            prereqs = f.readline().strip().split('; ')
            prereq_list = []
            for prereq in prereqs:
                prereq_list.append((prereq[0], prereq[2: -1].split(', ')))
            prereq_info[boon] = prereq_list
        if type == 'call':
            boons_info[boon]['maxcall'] = f.readline().strip()
    f.close()

f = open(f'./files/gods/misc.txt', 'r', encoding='utf8')
while boon := f.readline().strip():
    god, type, boon = boon.split(' ', 2)
    has_prereq = False
    if type[0] == 'x':
        has_prereq = True
        type = type[1:]
    boons_info[boon] = {'god': god, 'type': type, 'desc': f.readline().strip(), 'stat': f.readline().strip(),
                        'rarities': f.readline().strip().split(' '), 'levels': f.readline().strip().split(' '),
                        'icon': f.readline().strip()}
    if has_prereq:
        prereqs = f.readline().strip().split('; ')
        prereq_list = []
        for prereq in prereqs:
            prereq_list.append((prereq[0], prereq[2: -1].split(', ')))
        prereq_info[boon] = prereq_list
    if type == 'call':
        boons_info[boon]['maxcall'] = f.readline().strip()
f.close()

f = open(f'./files/gods/bouldy.txt', 'r', encoding='utf8')
while f.readline():
    bouldy_info.append({'desc': f.readline().strip(), 'stat': f.readline().strip(), 'icon': f.readline().strip()})
f.close()

f = open(f'./files/aspects.txt', 'r', encoding='utf8')
while aspect := f.readline().strip():
    aspects_info[aspect] = {'desc': f.readline().strip(), 'stat': f.readline().strip(),
                            'levels': f.readline().strip().split(' '), 'flavor': f.readline().strip(),
                            'icon': f.readline().strip()}
f.close()

f = open('./files/corealiases.txt', 'r', encoding='utf8')
while name := f.readline().strip():
    aliases = f.readline().strip().split(', ')
    if aliases[0]:
        for alias in aliases:
            if alias in core_aliases:
                print(f'duplicate alias: {alias}')
            core_aliases[alias] = name
f.close()

f = open('./files/boonaliases.txt', 'r', encoding='utf8')
while name := f.readline().strip():
    aliases = f.readline().strip().split(', ')
    if aliases[0]:
        for alias in aliases:
            if alias in misc_aliases:
                print(f'duplicate alias: {alias}')
            misc_aliases[alias] = name
f.close()

f = open('./files/aspectaliases.txt', 'r', encoding='utf8')
while name := f.readline().strip():
    aliases = f.readline().strip().split(', ')
    if aliases[0]:
        for alias in aliases:
            if alias in aspect_aliases:
                print(f'duplicate alias: {alias}')
            aspect_aliases[alias] = name
f.close()

f = open('./files/hammeraliases.txt', 'r', encoding='utf8')
while name := f.readline().strip():
    aliases = f.readline().strip().split(', ')
    if aliases[0]:
        for alias in aliases:
            if alias in hammer_aliases:
                print(f'duplicate alias: {alias}')
            hammer_aliases[alias] = name
f.close()

for weapon in misc.weapon_icons:
    f = open(f'./files/hammers/{weapon}.txt', 'r', encoding='utf8')
    while hammer := f.readline().strip():
        has_prereq = False
        if hammer[0] == 'x':
            has_prereq = True
            hammer = hammer[1:]
        hammers_info[hammer] = {'weapon': weapon, 'desc': f.readline().strip(), 'icon': f.readline().strip()}
        if has_prereq:
            prereqs = f.readline().strip().split('; ')
            prereq_list = []
            for prereq in prereqs:
                prereq_list.append((prereq[0], prereq[2: -1].split(', ')))
            prereq_info[hammer] = prereq_list
    f.close()
