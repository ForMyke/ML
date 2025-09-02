from typing import List
from .variables import Params
from genes.individual import gen_human, check_perfect, mix_humans

def gen_humans(men: List[list], women: List[list], n: int, params: Params) -> bool:
    """Genera n parejas iniciales; devuelve si se alcanzó un individuo perfecto."""
    perfect = False
    for _ in range(n):
        ha = gen_human(params)
        hb = gen_human(params)
        perfect = perfect or check_perfect(ha, params) or check_perfect(hb, params)
        women.append(ha)
        men.append(hb)
    return perfect

def get_generation(params: Params) -> int:
    women: List[list] = []
    men: List[list] = []
    generation = 1

    perfect = gen_humans(men, women, params.numCouples, params)

    while not perfect:
        nwomen: List[list] = []
        nmen: List[list] = []
        for a, b in zip(men, women):
            nhA, nhB = mix_humans(a, b, params)
            perfect = perfect or check_perfect(nhA, params) or check_perfect(nhB, params)
            nwomen.append(nhA)
            nmen.append(nhB)
        men, women = nmen, nwomen
        generation += 1

    return generation
