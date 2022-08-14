import re
from PIL import Image


def pact_gen(input: [str]) -> int:
    input = [s.lower() for s in input]
    hell_mode = False
    total_heat = 0
    base = Image.open('./files/pacts/base.png')
    PL_pact, heat = PL(input)
    if PL_pact:
        total_heat += heat
        base.paste(Image.open(PL_pact), (0, 568))
        hell_mode = True
    HL_pact, heat = HL(input, hell_mode)
    if HL_pact:
        total_heat += heat
        base.paste(Image.open(HL_pact), (0, 0))
    LC_pact, heat = LC(input, hell_mode)
    if LC_pact:
        total_heat += heat
        base.paste(Image.open(LC_pact), (0, 43))
    CF_pact, heat = CF(input)
    if CF_pact:
        total_heat += heat
        base.paste(Image.open(CF_pact), (0, 81))
    JS_pact, heat = JS(input, hell_mode)
    if JS_pact:
        total_heat += heat
        base.paste(Image.open(JS_pact), (0, 118))
    EM_pact, heat = EM(input)
    if EM_pact:
        total_heat += heat
        base.paste(Image.open(EM_pact), (0, 156))
    CP_pact, heat = CP(input, hell_mode)
    if CP_pact:
        total_heat += heat
        base.paste(Image.open(CP_pact), (0, 193))
    BP_pact, heat = BP(input)
    if BP_pact:
        total_heat += heat
        base.paste(Image.open(BP_pact), (0, 231))
    MM_pact, heat = MM(input)
    if MM_pact:
        total_heat += heat
        base.paste(Image.open(MM_pact), (0, 268))
    UC_pact, heat = UC(input)
    if UC_pact:
        total_heat += heat
        base.paste(Image.open(UC_pact), (0, 305))
    FO_pact, heat = FO(input)
    if FO_pact:
        total_heat += heat
        base.paste(Image.open(FO_pact), (0, 343))
    HS_pact, heat = HS(input)
    if HS_pact:
        total_heat += heat
        base.paste(Image.open(HS_pact), (0, 381))
    RI_pact, heat = RI(input)
    if RI_pact:
        total_heat += heat
        base.paste(Image.open(RI_pact), (0, 418))
    DC_pact, heat = DC(input)
    if DC_pact:
        total_heat += heat
        base.paste(Image.open(DC_pact), (0, 456))
    AP_pact, heat = AP(input)
    if AP_pact:
        total_heat += heat
        base.paste(Image.open(AP_pact), (0, 493))
    TD_pact, heat = TD(input)
    if TD_pact:
        total_heat += heat
        base.paste(Image.open(TD_pact), (0, 531))
    base.save('temp.png')
    return total_heat


def HL(input: [str], hell_mode) -> (str, int):
    pact = 'hl'
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return (f'./files/pacts/{pact.upper()}/1.png', 1) if hell_mode else ('', 0)
    rank = min(int(temp[0].split(pact)[1]), 5)
    if rank <= 0:
        return (f'./files/pacts/{pact.upper()}/1.png', 1) if hell_mode else ('', 0)
    return f'./files/pacts/{pact.upper()}/{rank}.png', rank


def LC(input: [str], hell_mode) -> (str, int):
    pact = 'lc'
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return (f'./files/pacts/{pact.upper()}/1.png', 1) if hell_mode else ('', 0)
    rank = min(int(temp[0].split(pact)[1]), 4)
    if rank <= 0:
        return (f'./files/pacts/{pact.upper()}/1.png', 1) if hell_mode else ('', 0)
    return f'./files/pacts/{pact.upper()}/{rank}.png', rank


def CF(input: [str]) -> (str, int):
    pact = 'cf'
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = min(int(temp[0].split(pact)[1]), 2)
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/{rank}.png', rank


def JS(input: [str], hell_mode) -> (str, int):
    pact = 'js'
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return (f'./files/pacts/{pact.upper()}/1.png', 1) if hell_mode else ('', 0)
    rank = min(int(temp[0].split(pact)[1]), 3)
    if rank <= 0:
        return (f'./files/pacts/{pact.upper()}/1.png', 1) if hell_mode else ('', 0)
    return f'./files/pacts/{pact.upper()}/{rank}.png', rank


def EM(input: [str]) -> (str, int):
    pact = 'em'
    heat = (1, 3, 6, 10)
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = min(int(temp[0].split(pact)[1]), 4)
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/{rank}.png', heat[rank - 1]


def CP(input: [str], hell_mode) -> (str, int):
    pact = 'cp'
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return (f'./files/pacts/{pact.upper()}/1.png', 1) if hell_mode else ('', 0)
    rank = min(int(temp[0].split(pact)[1]), 2)
    if rank <= 0:
        return (f'./files/pacts/{pact.upper()}/1.png', 1) if hell_mode else ('', 0)
    return f'./files/pacts/{pact.upper()}/{rank}.png', rank


def BP(input: [str]) -> (str, int):
    pact = 'bp'
    heat = (2, 5)
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = min(int(temp[0].split(pact)[1]), 2)
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/{rank}.png', heat[rank - 1]


def MM(input: [str]) -> (str, int):
    pact = 'mm'
    if pact in input:
        return f'./files/pacts/{pact.upper()}/1.png', 2
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = int(temp[0].split(pact)[1])
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/1.png', 2


def UC(input: [str]) -> (str, int):
    pact = 'uc'
    if pact in input:
        return f'./files/pacts/{pact.upper()}/1.png', 2
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = int(temp[0].split(pact)[1])
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/1.png', 2


def FO(input: [str]) -> (str, int):
    pact = 'fo'
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = min(int(temp[0].split(pact)[1]), 2)
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/{rank}.png', rank * 3


def HS(input: [str]) -> (str, int):
    pact = 'hs'
    if pact in input:
        return f'./files/pacts/{pact.upper()}/1.png', 1
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = int(temp[0].split(pact)[1])
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/1.png', 1


def RI(input: [str]) -> (str, int):
    pact = 'ri'
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = min(int(temp[0].split(pact)[1]), 4)
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/{rank}.png', rank * 2


def DC(input: [str]) -> (str, int):
    pact = 'dc'
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = min(int(temp[0].split(pact)[1]), 2)
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/{rank}.png', rank


def AP(input: [str]) -> (str, int):
    pact = 'ap'
    heat = (2, 5)
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = min(int(temp[0].split(pact)[1]), 2)
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/{rank}.png', heat[rank - 1]


def TD(input: [str]) -> (str, int):
    pact = 'td'
    heat = (1, 3, 6)
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = min(int(temp[0].split(pact)[1]), 3)
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/{rank}.png', heat[rank - 1]


def PL(input: [str]) -> (str, int):
    pact = 'pl'
    if pact in input:
        return f'./files/pacts/{pact.upper()}/1.png', 1
    r = re.compile(f'{pact}\d')
    temp = list(filter(r.match, input))
    if not temp:
        return '', 0
    rank = int(temp[0].split(pact)[1])
    if rank <= 0:
        return '', 0
    return f'./files/pacts/{pact.upper()}/1.png', 1
