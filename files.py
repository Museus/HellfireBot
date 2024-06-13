import json

import misc

boons_info = {}
legendary_info = []
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
    'poseidon': {}, 'zeus': {}, 'duo': {},
    'arachne': {}, 'artemis': {}, 'chaos': {},
    'charon': {}, 'circe': {}, 'echo': {},
    'hades': {}, 'hermes': {}, 'icarus': {},
    'medea': {}, 'narcissus': {}, 'selene': {},
    'bouldy': {}
}
global_arcana = {}
commands_info = {}

for god in god_cores:
    with open(f'./files/gods/{god}.txt', 'r', encoding='utf8') as f:
        god_cores[god]['category'] = f.readline().strip()
        while boon := f.readline().strip():
            type, boon = boon.split(' ', 1)
            has_prereq = type not in (
                'attack', 'special', 'cast', 'sprint', 'gain', 't1', 'revenge', 'prime',
                'blessing', 'curse', 'survival', 'combat', 'resource', 'miscellaneous'
            )
            if type[0] == 'x':
                type = type[1:]
            *boon, element = boon.split(' ')
            boon = ' '.join(boon)
            if type in ('attack', 'special', 'cast', 'sprint', 'gain', 'revenge', 'prime', 'status', 'infusion', 'legendary'):
                if type == 'legendary':
                    legendary_info.append(boon)
                if type not in god_cores[god]:
                    god_cores[god][type] = []
                god_cores[god][type].append(boon)
            description = f.readline().strip()
            stat = f.readline().strip()
            rarities = f.readline().strip().split(' ')
            levels = f.readline().strip().split(' ')
            icon = f.readline().strip()
            boons_info[boon] = {
                'god': god, 'type': type, 'desc': description, 'stat': stat,
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
            if god not in aliases['misc']:
                aliases['misc'][god] = []
            aliases['misc'][god].append(boon)

# for boon in boons_info:
#     print(boon)

with open('./files/aspects.txt', 'r', encoding='utf8') as f:
    while aspect := f.readline().strip():
        weapon, aspect = aspect.split(' ', 1)
        aspects_info[aspect] = {
            'weapon': weapon, 'desc': f.readline().strip(), 'stat': f.readline().strip(),
            'levels': f.readline().strip().split(' '), 'flavor': f.readline().strip(),
            'icon': f.readline().strip()
        }

for weapon in misc.weapon_icons:
    with open(f'./files/hammers/{weapon}.txt', 'r', encoding='utf8') as f:
        while hammer := f.readline().strip():
            type, hammer = hammer.split(' ', 1)
            has_prereq = False
            if hammer[0] == 'x':
                has_prereq = True
                hammer = hammer[1:]
            hammers_info[hammer] = {
                'type': type, 'weapon': weapon, 'desc': f.readline().strip(), 'icon': f.readline().strip()
            }
            if has_prereq:
                prereqs = f.readline().strip().split('; ')
                prereq_list = []
                for prereq in prereqs:
                    prereq_list.append((prereq[0], prereq[2: -1].split(', ')))
                prereqs_info[hammer] = prereq_list

with open('./files/keepsakes.txt', 'r', encoding='utf8') as f:
    while keepsake := f.readline().strip():
        type, keepsake = keepsake.split(' ', 1)
        keepsakes_info[keepsake] = {
            'type': type, 'desc': f.readline().strip(), 'ranks': f.readline().strip().split(' '),
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
            'grasp': grasp, 'desc': f.readline().strip(), 'levels': f.readline().strip().split(' '),
            'flavor': f.readline().strip(), 'icon': f.readline().strip()
        }
        if grasp == 0:
            arcana_info[card]['awakening'] = f.readline().strip()
        aliases['arcana'][str(counter)] = [card]
        counter += 1

with open('./files/vows.txt', 'r', encoding='utf8') as f:
    while vow := f.readline().strip():
        vows_info[vow] = {
            'desc': f.readline().strip(), 'ranks': f.readline().strip().split(' '), 'fears': f.readline().strip(),
            'flavor': f.readline().strip(), 'icon': f.readline().strip()
        }
        aliases['vow'][vow.split()[-1]] = [vow]

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
            'params': ', '.join(parameters.split(' ')), 'desc': f.readline().strip(),
            'icon': f.readline().strip()
        }

with open('./files/enemies.txt', 'r', encoding='utf8') as f:
    while enemy := f.readline().strip():
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

with open('./files/arcana/global.json', 'r', encoding='utf8') as f:
    global_arcana = json.loads(f.read())
