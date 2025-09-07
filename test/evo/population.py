# test/evo/population.py
from typing import List, Tuple
from ..variables import Params
from .models import Person, make_person
from genes.individual import gen_human

def print_population(population: List[Person], gen: int):
    print(f"\n===== GENERACION {gen} (n={len(population)}) =====")
    for p in population:
        madre, padre = p["parents"]
        genes_str = " ".join(str(g) for g in p["genes"])
        r = "relajado" if p.get("relaxed") else "normal"
        print(f"[id={p['id']:5d}] gen={p['gen']:3d}  madre={madre} padre={padre}  ({r})  atributos: {genes_str}")

def build_initial_population(params: Params) -> Tuple[List[Person], List[Person]]:
    """Generación 0: crea numCouples*2 individuos y la imprime."""
    men: List[Person] = []
    women: List[Person] = []
    nid = 0
    for _ in range(params.numCouples):
        # fundadores: sin padres, abuelos, ni bisabuelos
        women.append(make_person(nid, gen_human(params), 0)); nid += 1
        men.append(make_person(nid, gen_human(params), 0)); nid += 1
    print_population(women + men, gen=0)
    return men, women
