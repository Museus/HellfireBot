import json

import misc

boons_info = {}
bouldy_info = []
legendary_info = []
charon_info = {}
aspects_info = {}
hammers_info = {}
keepsakes_info = {}
prereqs_info = {}
bpperks_info = {}
definitions_info = {}
aliases = {'core': {}, 'misc': {}, 'aspect': {}, 'hammer': {}, 'keepsake': {}, 'modifier': {}}
god_cores = {'zeus': {}, 'poseidon': {}, 'athena': {}, 'aphrodite': {}, 'artemis': {}, 'ares': {},
             'dionysus': {}, 'demeter': {}, 'apollo': {}, 'hermes': {}, 'chaos': {}, 'charon': {}, 'duos': None}
personal = {}
channels = {}
commands_info = {}

for god in god_cores:
    with open(f'./files/gods/{god}.txt', 'r', encoding='utf8') as f:
        while boon := f.readline().strip():
            type, boon = boon.split(' ', 1)
            modded = False
            if type[: 3] == 'mod':
                modded = True
                type = type[3:]
            has_prereq = type not in ('attack', 'special', 'cast', 'dash', 'call',
                                      'revenge', 't1', 'blessing', 'curse', 'combat', 'survival',
                                      'spawning', 'resource', 'miscellaneous')
            if type[0] == 'x':
                type = type[1:]
            if type in ('attack', 'special', 'cast', 'flare', 'dash', 'call', 'status', 'revenge', 'legendary'):
                if type == 'legendary':
                    legendary_info.append(boon)
                if type not in god_cores[god]:
                    god_cores[god][type] = []
                god_cores[god][type].append(boon)
            boons_info[boon] = {'god': god, 'type': type, 'desc': f.readline().strip(), 'stat': f.readline().strip(),
                                'rarities': f.readline().strip().split(' '), 'levels': f.readline().strip().split(' '),
                                'icon': f.readline().strip()}
            if has_prereq:
                prereqs = f.readline().strip().split('; ')
                prereq_list = []
                for prereq in prereqs:
                    prereq_list.append((prereq[0], prereq[2: -1].split(', ')))
                prereqs_info[boon] = prereq_list
            if type == 'call' and god not in ('hermes', 'charon'):
                boons_info[boon]['maxcall'] = f.readline().strip()
            if god == 'charon':
                boons_info[boon]['cost'] = f.readline().strip()
            if modded:
                boons_info[boon]['modded'] = True

with open('./files/gods/misc.txt', 'r', encoding='utf8') as f:
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
            prereqs_info[boon] = prereq_list
        if type == 'call':
            boons_info[boon]['maxcall'] = f.readline().strip()

with open(f'./files/gods/bouldy.txt', 'r', encoding='utf8') as f:
    while f.readline():
        bouldy_info.append({'desc': f.readline().strip(), 'stat': f.readline().strip(), 'icon': f.readline().strip()})

with open('./files/aspects.txt', 'r', encoding='utf8') as f:
    while aspect := f.readline().strip():
        weapon, aspect = aspect.split(' ', 1)
        aspects_info[aspect] = {'weapon': weapon, 'desc': f.readline().strip(), 'stat': f.readline().strip(),
                                'levels': f.readline().strip().split(' '), 'flavor': f.readline().strip(),
                                'icon': f.readline().strip()}

for weapon in misc.weapon_icons:
    with open(f'./files/hammers/{weapon}.txt', 'r', encoding='utf8') as f:
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
                prereqs_info[hammer] = prereq_list

with open('./files/keepsakes.txt', 'r', encoding='utf8') as f:
    while keepsake := f.readline().strip():
        type, keepsake = keepsake.split(' ', 1)
        modded = False
        if type[: 3] == 'mod':
            modded = True
            type = type[3:]
        keepsakes_info[keepsake] = {'type': type, 'desc': f.readline().strip(),
                                    'ranks': f.readline().strip().split(' '),
                                    'bond': f.readline().strip().rsplit(' ', 2), 'flavor': f.readline().strip(),
                                    'icon': f.readline().strip()}
        if modded:
            keepsakes_info[keepsake]['modded'] = True
        if type != 'companion':
            for suffix in ('', ' keepsake', 's keepsake', '\' keepsake', '\'s keepsake'):
                aliases['keepsake'][keepsakes_info[keepsake]['bond'][0].lower() + suffix] = [keepsake]
        else:
            for suffix in (' companion', 's companion', '\' companion',
                           '\'s companion', ' pet', 's pet', '\' pet', '\'s pet'):
                aliases['keepsake'][keepsakes_info[keepsake]['bond'][0].lower() + suffix] = [keepsake]

for category in aliases:
    with open(f'./files/aliases/{category}aliases.txt', 'r', encoding='utf8') as f:
        while name := f.readline().strip():
            alias_list = f.readline().strip().split(', ')
            if alias_list[0]:
                for alias in alias_list:
                    if alias not in aliases[category]:
                        aliases[category][alias] = []
                    aliases[category][alias].append(name)

with open('./files/definitions.txt', 'r', encoding='utf8') as f:
    aliases['definition'] = {}
    while definition := f.readline().strip():
        modded = False
        if definition[: 3] == 'mod':
            modded = True
            definition = definition[3:]
        if ', ' in definition:
            definition, alias_list = definition.split(', ', 1)
            alias_list = alias_list.split(', ')
            for alias in alias_list:
                aliases['definition'][alias] = definition
        if not modded:
            definitions_info[definition] = f.readline().strip()
        else:
            definitions_info[definition] = (f.readline().strip(), 'modded')

with open('./files/benefits_package.txt', 'r', encoding='utf8') as f:
    while perk := f.readline().strip():
        has_prereq = False
        if perk[0] == 'x':
            has_prereq = True
            perk = perk[1:]
        bpperks_info[perk] = {'desc': f.readline().strip(), 'icon': f.readline().strip()}
        if has_prereq:
            bpperks_info[perk]['req'] = f.readline().strip()

with open('./files/help.txt', 'r', encoding='utf8') as f:
    while command := f.readline().strip():
        command, parameters = command.split(' ', 1)
        commands_info[command] = {'params': ', '.join(parameters.split(' ')), 'desc': f.readline().strip(),
                                  'icon': f.readline().strip()}


def read_personal() -> None:
    global personal
    with open('./private/personal.txt', 'r', encoding='utf8') as fp:
        personal = json.loads(fp.read())


def write_personal() -> None:
    global personal
    with open('./private/personal.txt', 'w', encoding='utf8') as fp:
        fp.write(json.dumps(personal))


def read_channel() -> None:
    global channels
    with open('./private/server_channels.txt', 'r', encoding='utf8') as fp:
        channels = json.loads(fp.read())


def write_channel() -> None:
    global channels
    with open('./private/server_channels.txt', 'w', encoding='utf8') as fp:
        fp.write(json.dumps(channels))


read_personal()
read_channel()
