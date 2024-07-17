import json

import misc

boons_info = {}
legendary_info = []
duo_info = {
    'aphrodite': [], 'apollo': [], 'demeter': [], 'hephaestus': [],
    'hera': [], 'hestia': [], 'poseidon': [], 'zeus': []
}
charon_info = {}
aspects_info = {}
hammers_info = {}
keepsakes_info = {}
arcana_info = {}
vows_info = {}
prereqs_info = {}
definitions_info = {}
enemies_info = {}
aliases = {
    'core': {}, 'misc': {}, 'aspect': {}, 'hammer': {},
    'keepsake': {}, 'arcana': {}, 'vow': {}, 'modifier': {}
}
god_cores = {
    'aphrodite': {}, 'apollo': {}, 'demeter': {},
    'hephaestus': {}, 'hera': {}, 'hestia': {},
    'poseidon': {}, 'zeus': {}, 'arachne': {},
    'artemis': {}, 'chaos': {}, 'charon': {},
    'circe': {}, 'echo': {}, 'hades': {},
    'hermes': {}, 'icarus': {}, 'medea': {},
    'narcissus': {}, 'selene': {}, 'path of stars': {}
}
global_arcana = {}
commands_info = {}
saved_arcana = {}
saved_oaths = {}

for god in god_cores:
    with open(f'./files/gods/{"".join(god.split())}.txt', 'r', encoding='utf8') as f:
        god_cores[god]['category'] = f.readline().strip()
        while boon := f.readline().strip():
            _type, boon = boon.split(' ', 1)
            has_prereq = _type not in (
                'attack', 'special', 'cast', 'sprint', 'gain', 'hex', 't1', 'revenge', 'prime',
                'blessing', 'curse', 'survival', 'combat', 'resource', 'miscellaneous'
            )
            if _type[0] == 'x':
                _type = _type[1:]
            *boon, element = boon.split()
            boon = ' '.join(boon)
            if _type in ('attack', 'special', 'cast', 'sprint', 'gain',
                         'revenge', 'prime', 'status', 'infusion', 'legendary', 'duo'):
                if _type == 'legendary':
                    legendary_info.append(boon)
                elif _type == 'duo':
                    duo_info[god].append(boon)
                if _type not in god_cores[god]:
                    god_cores[god][_type] = []
                god_cores[god][_type].append(boon)
            description = f.readline().strip()
            stat = f.readline().strip()
            rarities = f.readline().split()
            levels = f.readline().split()
            icon = f.readline().strip()
            if boon in boons_info:
                boons_info[boon]['god'] = (boons_info[boon]['god'], god)
                boons_info[boon] = boons_info.pop(boon)
                if _type == 'duo':
                    if god + ' duo' not in aliases['misc']:
                        aliases['misc'][god + ' duo'] = []
                    aliases['misc'][god + ' duo'].append(boon)
                    aliases['misc'][' '.join(boons_info[boon]['god'])] = [boon]
                    aliases['misc'][' '.join(boons_info[boon]['god']) + ' duo'] = [boon]
                    aliases['misc']['duo ' + ' '.join(boons_info[boon]['god'])] = [boon]
                    aliases['misc'][' '.join(boons_info[boon]['god'][::-1])] = [boon]
                    aliases['misc'][' '.join(boons_info[boon]['god'][::-1]) + ' duo'] = [boon]
                    aliases['misc']['duo ' + ' '.join(boons_info[boon]['god'][::-1])] = [boon]
                else:
                    if god not in aliases['misc']:
                        aliases['misc'][god] = []
                    aliases['misc'][god].append(boon)
                f.readline()
                continue
            boons_info[boon] = {
                'god': god, 'type': _type, 'desc': description, 'stat': stat,
                'rarities': rarities, 'levels': levels, 'icon': icon
            }
            if has_prereq:
                prereqs = f.readline().strip().split('; ')
                prereq_list = []
                for prereq in prereqs:
                    prereq_list.append((prereq[0], prereq[2: -1].split(', ')))
                prereqs_info[boon] = prereq_list
            if god == 'charon':
                boons_info[boon]['cost'] = f.readline().strip()
            if element != 'none':
                boons_info[boon]['element'] = element
            if _type == 'duo':
                if god + ' duo' not in aliases['misc']:
                    aliases['misc'][god + ' duo'] = []
                aliases['misc'][god + ' duo'].append(boon)
            else:
                if god not in aliases['misc']:
                    aliases['misc'][god] = []
                aliases['misc'][god].append(boon)


with open('./files/aspects.txt', 'r', encoding='utf8') as f:
    while aspect := f.readline().strip():
        weapon, aspect = aspect.split(' ', 1)
        aspects_info[aspect] = {
            'weapon': weapon, 'desc': f.readline().strip(), 'stat': f.readline().strip(),
            'levels': f.readline().split(), 'flavor': f.readline().strip(),
            'icon': f.readline().strip()
        }

for weapon in misc.weapon_icons:
    with open(f'./files/hammers/{weapon}.txt', 'r', encoding='utf8') as f:
        while hammer := f.readline().strip():
            _type, hammer = hammer.split(' ', 1)
            has_prereq = False
            if hammer[0] == 'x':
                has_prereq = True
                hammer = hammer[1:]
            hammers_info[hammer] = {
                'type': _type, 'weapon': weapon, 'desc': f.readline().strip(), 'icon': f.readline().strip()
            }
            if has_prereq:
                prereqs = f.readline().strip().split('; ')
                prereq_list = []
                for prereq in prereqs:
                    prereq_list.append((prereq[0], prereq[2: -1].split(', ')))
                prereqs_info[hammer] = prereq_list

with open('./files/keepsakes.txt', 'r', encoding='utf8') as f:
    while keepsake := f.readline().strip():
        _type, keepsake = keepsake.split(' ', 1)
        keepsakes_info[keepsake] = {
            'type': _type, 'desc': f.readline().strip(), 'ranks': f.readline().split(),
            'giver': f.readline().strip(), 'icon': f.readline().strip()
        }
        for suffix in ('', ' keepsake', 's keepsake', '\' keepsake', '\'s keepsake'):
            aliases['keepsake'][keepsakes_info[keepsake]['giver'].lower() + suffix] = [keepsake]

with open('./files/arcana.txt', 'r', encoding='utf8') as f:
    counter = 1
    while card := f.readline().strip():
        grasp, card = card.split(' ', 1)
        grasp = int(grasp)
        arcana_info[card] = {
            'grasp': grasp, 'desc': f.readline().strip(), 'levels': f.readline().split(),
            'flavor': f.readline().strip(), 'icon': f.readline().strip()
        }
        if grasp == 0:
            arcana_info[card]['awakening'] = f.readline().strip()
        aliases['arcana'][str(counter)] = [card]
        counter += 1

with open('./files/vows.txt', 'r', encoding='utf8') as f:
    while vow := f.readline().strip():
        vows_info[vow] = {
            'desc': f.readline().strip(), 'ranks': f.readline().split(), 'fears': f.readline().split(),
            'flavor': f.readline().strip(), 'icon': f.readline().strip()
        }
        aliases['vow'][vow.split()[-1]] = [vow]
        aliases['vow'][' '.join(vow.split()[-2:])] = [vow]

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
        if ', ' in definition:
            definition, alias_list = definition.split(', ', 1)
            alias_list = alias_list.split(', ')
            for alias in alias_list:
                aliases['definition'][alias] = definition
        definitions_info[definition] = f.readline().strip()

with open('./files/help.txt', 'r', encoding='utf8') as f:
    while command := f.readline().strip():
        command, parameters = command.split(' ', 1)
        commands_info[command] = {
            'params': ', '.join(parameters.split()), 'desc': f.readline().strip(),
            'icon': f.readline().strip()
        }

with open('./files/enemies.txt', 'r', encoding='utf8') as f:
    while enemy := f.readline().strip():
        print(enemy)
        healths, attacks = f.readline().strip().rsplit(' ', 1)
        healths = healths.split(' ')
        attacks_info = []
        for i in range(int(attacks)):
            attacks_info.append((f.readline().strip(), f.readline().strip()))
        enemies_info[enemy] = {
            'health': healths[0], 'armor': healths[1], 'attacks': attacks_info,
            'elite': f.readline().strip(), 'location': f.readline().strip(),
            'icon': f.readline().strip()
        }


def read_personal():
    global saved_arcana
    with open('./files/arcana/loadouts.json', 'r', encoding='utf8') as fp:
        saved_arcana = json.loads(fp.read())


def write_personal():
    global saved_arcana
    with open('./files/arcana/loadouts.json', 'w', encoding='utf8') as fp:
        fp.write(json.dumps(saved_arcana, indent=4))


read_personal()
