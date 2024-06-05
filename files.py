boons_info = {}
legendary_info = []
charon_info = {}
aspects_info = {}
hammers_info = {}
keepsakes_info = {}
prereqs_info = {}
definitions_info = {}
enemies_info = {}
aliases = {'core': {}, 'misc': {}, 'aspect': {}, 'hammer': {}, 'keepsake': {}, 'modifier': {}}
god_cores = {
    'aphrodite': {}, 'apollo': {}, 'demeter': {},
    'hephaestus': {}, 'hera': {}, 'hestia': {},
    'poseidon': {}, 'zeus': {}, 'duos': {},
    'artemis': {}, 'hermes': {}
}
commands_info = {}

for god in god_cores:
    with open(f'./files/gods/{god}.txt', 'r', encoding='utf8') as f:
        while boon := f.readline().strip():
            type, boon = boon.split(' ', 1)
            has_prereq = type not in ('attack', 'special', 'cast', 'sprint', 'gain', 't1', 'revenge', 'prime')
            if type[0] == 'x':
                type = type[1:]
            if type not in ('infusion', 'duo'):
                *boon, element = boon.split(' ')
                boon = ' '.join(boon)
            if type in ('attack', 'special', 'cast', 'sprint', 'gain', 'revenge', 'prime', 'infusion', 'legendary'):
                if type == 'legendary':
                    legendary_info.append(boon)
                if type not in god_cores[god]:
                    god_cores[god][type] = []
                god_cores[god][type].append(boon)
            description = f.readline().strip()
            stat = f.readline().strip()
            rarities = f.readline().strip().split(' ')
            levels = f.readline().strip().split(' ')
            next_line = f.readline().strip()
            stat2 = None
            rarities2 = None
            levels2 = None
            if ': ' in next_line:
                stat2 = next_line
                rarities2 = f.readline().strip().split(' ')
                levels2 = f.readline().strip().split(' ')
                icon = f.readline().strip()
            else:
                icon = next_line
            boons_info[boon] = {
                'god': god, 'type': type, 'desc': description, 'stat': stat,
                'rarities': rarities, 'levels': levels, 'icon': icon
            }
            if stat2:
                boons_info[boon]['stat2'] = stat2
                boons_info[boon]['rarities2'] = rarities2
                boons_info[boon]['levels2'] = levels2
            if has_prereq:
                prereqs = f.readline().strip().split('; ')
                prereq_list = []
                for prereq in prereqs:
                    prereq_list.append((prereq[0], prereq[2: -1].split(', ')))
                prereqs_info[boon] = prereq_list
            if god == 'charon':
                boons_info[boon]['cost'] = f.readline().strip()
            if type == 'duo':
                boons_info[boon]['element'] = 'aether'
            elif type != 'infusion':
                boons_info[boon]['element'] = element

with open('./files/gods/misc.txt', 'r', encoding='utf8') as f:
    while boon := f.readline().strip():
        god, type, boon = boon.split(' ', 2)
        has_prereq = False
        if type[0] == 'x':
            has_prereq = True
            type = type[1:]
        description = f.readline().strip()
        stat = f.readline().strip()
        rarities = f.readline().strip().split(' ')
        levels = f.readline().strip().split(' ')
        next_line = f.readline().strip()
        stat2 = None
        rarities2 = None
        levels2 = None
        if ': ' in next_line:
            stat2 = next_line
            rarities2 = f.readline().strip().split(' ')
            levels2 = f.readline().strip().split(' ')
            icon = f.readline().strip()
        else:
            icon = next_line
        boons_info[boon] = {
            'god': god, 'type': type, 'desc': description, 'stat': stat,
            'rarities': rarities, 'levels': levels, 'icon': icon
        }
        if stat2:
            boons_info[boon]['stat2'] = stat2
            boons_info[boon]['rarities2'] = rarities2
            boons_info[boon]['levels2'] = levels2
        if has_prereq:
            prereqs = f.readline().strip().split('; ')
            prereq_list = []
            for prereq in prereqs:
                prereq_list.append((prereq[0], prereq[2: -1].split(', ')))
            prereqs_info[boon] = prereq_list

with open('./files/aspects.txt', 'r', encoding='utf8') as f:
    while aspect := f.readline().strip():
        weapon, aspect = aspect.split(' ', 1)
        aspects_info[aspect] = {
            'weapon': weapon, 'desc': f.readline().strip(), 'stat': f.readline().strip(),
            'levels': f.readline().strip().split(' '), 'flavor': f.readline().strip(),
            'icon': f.readline().strip()
        }

# for weapon in misc.weapon_icons:
#     with open(f'./files/hammers/{weapon}.txt', 'r', encoding='utf8') as f:
#         while hammer := f.readline().strip():
#             has_prereq = False
#             if hammer[0] == 'x':
#                 has_prereq = True
#                 hammer = hammer[1:]
#             hammers_info[hammer] = {'weapon': weapon, 'desc': f.readline().strip(), 'icon': f.readline().strip()}
#             if has_prereq:
#                 prereqs = f.readline().strip().split('; ')
#                 prereq_list = []
#                 for prereq in prereqs:
#                     prereq_list.append((prereq[0], prereq[2: -1].split(', ')))
#                 prereqs_info[hammer] = prereq_list

with open('./files/keepsakes.txt', 'r', encoding='utf8') as f:
    while keepsake := f.readline().strip():
        type, keepsake = keepsake.split(' ', 1)
        keepsakes_info[keepsake] = {
            'type': type, 'desc': f.readline().strip(), 'ranks': f.readline().strip().split(' '),
            'giver': f.readline().strip(), 'icon': f.readline().strip()
        }
        for suffix in ('', ' keepsake', 's keepsake', '\' keepsake', '\'s keepsake'):
            aliases['keepsake'][keepsakes_info[keepsake]['giver'].lower() + suffix] = [keepsake]

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
