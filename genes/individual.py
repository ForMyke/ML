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
    """
    Recombinación simple (versión antigua).
    Conservada por compatibilidad, pero aquí las mutaciones siguen probabilísticas.
    """
    nHuman1: List[int] = []
    nHuman2: List[int] = []
    for i in range(params.numAttributes):
        choose = random.randint(0, 1) == 0
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

def mix_humans_verbose(humanA: List[int], humanB: List[int], params: Params):
    """
    Igual que mix_humans pero también devuelve 'events' para auditar.
    Ahora cada hijo muta exactamente 2 genes elegidos al azar.
    """
    nHuman1: List[int] = []
    nHuman2: List[int] = []
    events = []

    # Selecciona 2 genes distintos para mutar en cada hijo
    mut_positions_child1 = random.sample(range(params.numAttributes), 2)
    mut_positions_child2 = random.sample(range(params.numAttributes), 2)

    for i in range(params.numAttributes):
        choose = random.randint(0, 1) == 0  # True => H1 toma ceil(media) salvo mutación
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
