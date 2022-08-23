import random

import pactgen

heats = {}

for i in range(5):
    heats[f'hl{i + 1}'] = 1
for i in range(4):
    heats[f'lc{i + 1}'] = 1
for i in range(2):
    heats[f'cf{i + 1}'] = 1
for i in range(3):
    heats[f'js{i + 1}'] = 1
for i in range(4):
    heats[f'em{i + 1}'] = i + 1
for i in range(2):
    heats[f'cp{i + 1}'] = 1
for i in range(2):
    heats[f'bp{i + 1}'] = i + 2
heats['mm1'] = 2
heats['uc1'] = 2
for i in range(2):
    heats[f'fo{i + 1}'] = 3
heats['hs1'] = 1
for i in range(4):
    heats[f'ri{i + 1}'] = 2
for i in range(2):
    heats[f'dc{i + 1}'] = 1
for i in range(2):
    heats[f'ap{i + 1}'] = i + 2
for i in range(3):
    heats[f'td{i + 1}'] = i + 1
heats['pl1'] = 1


def add_pact(total_heat: int, available: {str: int}, pact: [str]) -> bool:
    if total_heat == 0:
        return True
    while available:
        random_pact, rank = random.choice(list(available.items()))
        rank = pactgen.max_pact[random_pact] - rank + 1
        heat = heats[f'{random_pact}{rank}']
        if heat <= total_heat:
            available[random_pact] -= 1
            if available[random_pact] == 0:
                available.pop(random_pact)
            pact[random_pact] = rank
            return add_pact(total_heat - heat, available, pact)
        else:
            available.pop(random_pact)
    return False
