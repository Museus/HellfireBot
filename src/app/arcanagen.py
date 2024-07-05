import random

from PIL import Image

import files

all_grasps = [list(files.arcana_info.values())[i - 1]['grasp'] for i in range(1, 26)]


def add_awakenings(loadout, disabled=None):
    if disabled is None:
        disabled = set()
    grasps = [all_grasps[int(card) - 1] for card in loadout]
    if 25 not in disabled and 1 <= len(loadout) <= 3:
        loadout.append(25)
    if 5 not in disabled and any(c in loadout for c in (4, 9, 10)):
        loadout.append(5)
    if 13 not in disabled and all(g in grasps for g in range(1, 6)):
        loadout.append(13)
    if 20 not in disabled and len(loadout) >= 1 and all(grasps.count(g) <= 2 for g in range(1, 7)):
        loadout.append(20)
    if 21 not in disabled and all(c in loadout for c in (16, 17, 22)):
        loadout.append(21)
    if 24 not in disabled and (
            any(all(c in loadout for c in range(r * 5 + 1, r * 5 + 6)) for r in range(4)) or
            any(all(c in loadout for c in range(r + 1, r + 22, 5)) for r in range(5))):
        loadout.append(24)
    return loadout


def arcana_gen(uid, args):
    if isinstance(args, list) or isinstance(args, tuple):
        loadout = [int(c) for c in args if all_grasps[int(c) - 1] != 0]
        add_awakenings(loadout)
    else:
        if uid in files.saved_arcana['personal'] and args in files.saved_arcana['personal'][uid]:
            bitstring = files.saved_arcana['personal'][uid][args]
        elif args in files.saved_arcana['global']:
            bitstring = files.saved_arcana['global'][args]
        else:
            return -1
        loadout = [i for i in range(1, 26) if bitstring[i - 1] == '1' and all_grasps[i - 1] != 0]
        disabled = set(i for i in range(1, 26) if bitstring[i - 1] == '0' and all_grasps[i - 1] == 0)
        add_awakenings(loadout, disabled)

    base = Image.open('./files/arcana/base.png')
    total_grasp = 0

    for i in range(1, 26):
        if i in loadout:
            x = 0 if i % 5 == 1 else ((i - 1) % 5) * 148 + 6
            y = 0 if i <= 5 else (i - 1) // 5 * 190 + 3
            base.paste(Image.open(f'./files/arcana/{i}.png'), (x, y))
            total_grasp += all_grasps[i - 1]
    base.save('./temp.png')
    return total_grasp


def rand_arcana(total_grasp, loadout=None):
    if loadout is None:
        loadout = []
    possible = []
    for i in range(1, 26):
        if i not in loadout and 0 < all_grasps[i - 1] <= total_grasp:
            possible.append(i)
    if not possible:
        return add_awakenings(loadout)
    card = random.choice(possible)
    loadout.append(card)
    return rand_arcana(total_grasp - all_grasps[card - 1], loadout)
