from math import ceil, floor
import random
from typing import List, Tuple
from test.variables import Params
from .randoms import random_number, random_number_mutation

def gen_human(params: Params) -> List[int]:
    """Asignación de atributos"""
    return [random_number(params) for _ in range(params.numAttributes)]

def check_perfect(human: List[int], params: Params) -> bool:
    """Verificación de si el humano es perfecto o no"""
    return all(g == params.MAX_LIM for g in human)

def mix_humans(humanA: List[int], humanB: List[int], params: Params) -> Tuple[List[int], List[int]]:
    """Poder relacionarse (recombinación + posible mutación)"""
    nHuman1, nHuman2 = [], []
    for i in range(params.numAttributes):
        choose = (random.randint(0, params.numgen) % 2 == 0)
        media = (humanA[i] + humanB[i]) / 2
        al1 = random.randint(0, params.numgen) <= params.limit
        al2 = random.randint(0, params.numgen) <= params.limit

        a_val = random_number_mutation(params) if al1 else (ceil(media) if choose else floor(media))
        b_val = random_number_mutation(params) if al2 else (floor(media) if choose else ceil(media))

        if choose:
            nHuman1.append(a_val)
            nHuman2.append(b_val)
        else:
            nHuman1.append(b_val)
            nHuman2.append(a_val)
    return nHuman1, nHuman2
