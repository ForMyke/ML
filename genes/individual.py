from math import ceil, floor
import random
from typing import List, Tuple
from test.variables import Params
from .randoms import random_number, random_number_mutation

"""Asignación de atributos"""
def gen_human(params: Params) -> List[int]:
    return [random_number(params) for _ in range(params.numAttributes)]

"""Verificación de si el humano es perfecto o no"""
def check_perfect(human: List[int], params: Params) -> bool:
    return all(g == params.MAX_LIM for g in human)


def mix_humans_verbose(humanA: List[int], humanB: List[int], params: Params):
    nHuman1: List[int] = []
    nHuman2: List[int] = []
    events = []

    k = min(2, int(round(params.mutationProbability * params.numAttributes)))

    # Selecciona k genes distintos para mutar en cada hijo
    mut_positions_child1 = set(random.sample(range(params.numAttributes), min(k, params.numAttributes)))
    mut_positions_child2 = set(random.sample(range(params.numAttributes), min(k, params.numAttributes)))

    for i in range(params.numAttributes):
        choose = random.randint(0, 1) == 0  
        media = (humanA[i] + humanB[i]) / 2

        # Mutaciones obligatorias en las posiciones seleccionadas
        mut1 = i in mut_positions_child1
        mut2 = i in mut_positions_child2

        a_val = random_number_mutation(params) if mut1 else (ceil(media) if choose else floor(media))
        b_val = random_number_mutation(params) if mut2 else (floor(media) if choose else ceil(media))

        if choose:
            c1, c2 = a_val, b_val
            ev1_mut, ev2_mut = mut1, mut2
        else:
            c1, c2 = b_val, a_val
            ev1_mut, ev2_mut = mut2, mut1

        nHuman1.append(c1)
        nHuman2.append(c2)
        events.append({
            "attr": i,
            "parents": (humanA[i], humanB[i]),
            "avg": media,
            "chooseAfirst": choose,
            "child1": c1,
            "child2": c2,
            "mut_child1": ev1_mut,
            "mut_child2": ev2_mut
        })
    return nHuman1, nHuman2, events
