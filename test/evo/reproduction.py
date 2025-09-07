# test/evo/reproduction.py
from typing import List, Tuple
from ..variables import Params
from .models import Person, make_person
from .lineage import are_related
from .population import print_population
from genes.individual import mix_humans_verbose, check_perfect

def mix_and_make_children(pairs: List[Tuple[int, int, bool]],
                          men: List[Person], women: List[Person],
                          params: Params) -> Tuple[List[Person], List[Person], bool]:
    """
    Genera la siguiente generación preservando linaje (hasta bisabuelos) y LOGS detallados.
    ACELERACIÓN: si un atributo del hijo está marcado como mutado por mix_humans_verbose,
                 lo forzamos a params.MAX_LIM (mutación direccional hacia el óptimo).
    """
    perfect = False
    next_women: List[Person] = []
    next_men: List[Person] = []
    next_id = max([p["id"] for p in men + women]) + 1 if (men or women) else 0

    total_mut_c1 = total_mut_c2 = 0

    print("  Parejas formadas (Hombre x Mujer) [* = relajado/pivote]:")
    for mi, wj, rel in pairs:
        m = men[mi]
        w = women[wj]
        h1, h2, ev = mix_humans_verbose(w["genes"], m["genes"], params)  # 1º hija, 2º hijo

        # === ACELERACIÓN: dirigir mutaciones a MAX ===
        for e in ev:
            i = e["attr"]
            if e["mut_child1"]:
                h1[i] = params.MAX_LIM
            if e["mut_child2"]:
                h2[i] = params.MAX_LIM

        # Conjuntos útiles de los padres
        w_parents = {p for p in w["parents"] if p is not None}
        m_parents = {p for p in m["parents"] if p is not None}
        w_grand   = set(w.get("grandparents", set()))
        m_grand   = set(m.get("grandparents", set()))

        # Linaje para los hijos:
        child_gp  = w_parents | m_parents          # abuelos del hijo
        child_ggp = w_grand  | m_grand            # bisabuelos del hijo

        # Generación del hijo: siguiente respecto a sus padres
        child_gen = max(w["gen"], m["gen"]) + 1

        # ¿Los padres son parientes? (informativo, útil con RELAX)
        parents_related = are_related(m, w)

        # Hijos
        child_w = make_person(next_id, h1, child_gen, parents=(w["id"], m["id"]),
                              gp=child_gp, ggp=child_ggp, relaxed=rel); next_id += 1
        child_m = make_person(next_id, h2, child_gen, parents=(w["id"], m["id"]),
                              gp=child_gp, ggp=child_ggp, relaxed=rel); next_id += 1
        child_w["parents_related"] = parents_related
        child_m["parents_related"] = parents_related

        # Conteos de mutaciones por hijo (tras dirección)
        mut_idx_1 = [e["attr"] for e in ev if e["mut_child1"]]
        mut_idx_2 = [e["attr"] for e in ev if e["mut_child2"]]
        total_mut_c1 += len(mut_idx_1)
        total_mut_c2 += len(mut_idx_2)

        flag = "*" if rel else " "
        print(f"    {flag} H{m['id']} x M{w['id']}  ->  HijM{child_w['id']} / HijH{child_m['id']}"
              f" | mut(H1)={len(mut_idx_1)} {mut_idx_1}  mut(H2)={len(mut_idx_2)} {mut_idx_2}")

        perfect = perfect or check_perfect(child_w["genes"], params) or check_perfect(child_m["genes"], params)
        next_women.append(child_w)
        next_men.append(child_m)

    # Imprime la población de la nueva generación
    if next_women and next_men:
        print_population(next_women + next_men, gen=next_women[0]["gen"])
    print(f"  Mutaciones totales: hija(s)={total_mut_c1}, hijo(s)={total_mut_c2}")

    return next_men, next_women, perfect
