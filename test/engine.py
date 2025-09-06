# test/engine.py
from typing import List, Dict, Optional, Tuple
from .variables import Params
from genes.individual import gen_human, check_perfect, mix_humans_verbose

# {'id': int, 'genes': list[int], 'gen': int,
#  'parents': (madre_id, padre_id),
#  'grandparents': set[int],          # abuelos (gen - 2)
#  'greatgrandparents': set[int],     # bisabuelos (gen - 3)
#  'relaxed': bool}
Person = Dict[str, object]

def make_person(next_id: int, genes: list[int], gen: int,
                parents: Tuple[Optional[int], Optional[int]] = (None, None),
                gp: Optional[set] = None,                     # abuelos
                ggp: Optional[set] = None,                    # bisabuelos
                relaxed: bool = False) -> Person:
    return {
        "id": next_id,
        "genes": genes,
        "gen": gen,  # generación de nacimiento
        "parents": parents,  # (madre, padre)
        "grandparents": set() if gp is None else set(gp),
        "greatgrandparents": set() if ggp is None else set(ggp),
        "relaxed": relaxed,
    }

def print_population(population: List[Person], gen: int):
    print(f"\n===== GENERACION {gen} (n={len(population)}) =====")
    for p in population:
        madre, padre = p["parents"]
        genes_str = " ".join(str(g) for g in p["genes"])
        r = "relajado" if p.get("relaxed") else "normal"
        print(f"[id={p['id']:5d}] gen={p['gen']:3d}  madre={madre} padre={padre}  ({r})  atributos: {genes_str}")

def are_related(a: Person, b: Person) -> bool:
    """
    True si comparten:
      - algún padre (hermanos),
      - o algún abuelo (primos),
      - o algún bisabuelo (primos en segundo grado).
    """
    # Padres
    pa = set([p for p in a["parents"] if p is not None])
    pb = set([p for p in b["parents"] if p is not None])
    if pa and pb and pa.intersection(pb):
        return True  # hermanos

    # Abuelos
    ga = a.get("grandparents", set())
    gb = b.get("grandparents", set())
    if ga and gb and ga.intersection(gb):
        return True  # primos

    # Bisabuelos
    gga = a.get("greatgrandparents", set())
    ggb = b.get("greatgrandparents", set())
    if gga and ggb and gga.intersection(ggb):
        return True  # primos en segundo grado

    return False

def hopcroft_karp(adj: List[List[int]], n_left: int, n_right: int) -> Tuple[dict, List[int]]:
    """Devuelve matching dict L->R y lista de nodos izquierdos no emparejados."""
    from collections import deque
    INF = 10**9
    pairU = [-1] * n_left
    pairV = [-1] * n_right
    dist  = [0]  * n_left

    def bfs() -> bool:
        dq = deque()
        for u in range(n_left):
            if pairU[u] == -1:
                dist[u] = 0
                dq.append(u)
            else:
                dist[u] = INF
        reachable_free = False
        while dq:
            u = dq.popleft()
            for v in adj[u]:
                if pairV[v] != -1 and dist[pairV[v]] == INF:
                    dist[pairV[v]] = dist[u] + 1
                    dq.append(pairV[v])
                if pairV[v] == -1:
                    reachable_free = True
        return reachable_free

    def dfs(u: int) -> bool:
        for v in adj[u]:
            if pairV[v] == -1 or (dist[pairV[v]] == dist[u] + 1 and dfs(pairV[v])):
                pairU[u] = v
                pairV[v] = u
                return True
        dist[u] = INF
        return False

    while bfs():
        for u in range(n_left):
            if pairU[u] == -1:
                dfs(u)

    unmatched = [u for u in range(n_left) if pairU[u] == -1]
    return {u: pairU[u] for u in range(n_left) if pairU[u] != -1}, unmatched

def schedule_pairs(men: List[Person], women: List[Person], params: Params) -> List[Tuple[int, int, bool]]:
    """Empareja evitando parentesco hasta bisabuelos; si faltan 2 parejas, los últimos 4 actúan como pivote.
       Devuelve (idx_hombre, idx_mujer, relajado?)."""
    import random as _r
    n = len(men)
    adj: List[List[int]] = []
    for i, m in enumerate(men):
        edges = [j for j, w in enumerate(women) if not are_related(m, w)]
        _r.shuffle(edges)
        adj.append(edges)

    matching, unmatched = hopcroft_karp(adj, n, n)

    pairs: List[Tuple[int, int, bool]] = []
    # matching “normal”
    for i in range(n):
        if i in matching:
            pairs.append((i, matching[i], False))

    # Relajación: “últimos 4” (2 parejas) pueden mezclarse libremente
    last2 = max(0, n - 2)
    allowed_relaxed = set(range(last2, n))  # índices de hombres n-2 y n-1 (si hay)
    used_women = set(matching.values())

    for i in unmatched:
        candidates = [j for j in range(n) if j not in used_women]
        if not candidates:
            break
        if i in allowed_relaxed:
            j = candidates[0]
            used_women.add(j)
            pairs.append((i, j, True))
        else:
            ok = [j for j in candidates if not are_related(men[i], women[j])]
            if ok:
                j = ok[0]
                used_women.add(j)
                pairs.append((i, j, False))
            else:
                j = candidates[0]
                used_women.add(j)
                pairs.append((i, j, True))  # obligado

    pairs.sort(key=lambda x: x[0])
    return pairs

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

def mix_and_make_children(pairs: List[Tuple[int, int, bool]],
                          men: List[Person], women: List[Person],
                          params: Params) -> Tuple[List[Person], List[Person], bool]:
    """Genera la siguiente generación preservando linaje (hasta bisabuelos) y LOGS detallados."""
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

        # Conjuntos útiles de los padres
        w_parents = set([p for p in w["parents"] if p is not None])
        m_parents = set([p for p in m["parents"] if p is not None])

        w_grand = set(w.get("grandparents", set()))
        m_grand = set(m.get("grandparents", set()))

        # Linaje para los hijos:
        #  - Abuelos del hijo = padres de sus padres (gen-2)
        #  - Bisabuelos del hijo = abuelos de sus padres (gen-3)
        child_gp  = w_parents | m_parents
        child_ggp = w_grand  | m_grand

        # Generación del hijo: siguiente respecto a sus padres
        child_gen = max(w["gen"], m["gen"]) + 1

        # ¿Los padres son parientes? (informativo, útil con RELAX)
        parents_related = are_related(m, w)

        # Hijos
        child_w = make_person(next_id, h1, child_gen, parents=(w["id"], m["id"]), gp=child_gp, ggp=child_ggp, relaxed=rel); next_id += 1
        child_m = make_person(next_id, h2, child_gen, parents=(w["id"], m["id"]), gp=child_gp, ggp=child_ggp, relaxed=rel); next_id += 1
        child_w["parents_related"] = parents_related
        child_m["parents_related"] = parents_related

        # Conteos de mutaciones por hijo
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

def get_generation(params: Params) -> int:
    generation = 0
    men, women = build_initial_population(params)

    # Bucle de generaciones
    while True:
        # ¿Ya hay perfecto en la población actual?
        perfects = [p for p in men + women if check_perfect(p["genes"], params)]
        if perfects:
            indiv = perfects[0]
            print("\n>>> ¡Perfecto encontrado! Detalles del individuo:")
            print_population([indiv], gen=indiv["gen"])

            # Certificado de parentesco
            rflag = "RELAX" if indiv.get("relaxed") else "NORMAL"
            pr = indiv.get("parents_related", False)
            texto_rel = "NO parientes (válido)" if (rflag == "NORMAL" and not pr) else ("PODRÍA ser pariente" if pr or rflag == "RELAX" else "NO parientes")
            print(f">>> Emparejamiento: {rflag}  |  Verificación parentesco: {texto_rel}")

            print(f">>> Generaciones desde fundadores: {generation}")
            print(f">>> Generaciones desde su nacimiento: {generation - indiv['gen']} (nació en gen {indiv['gen']})")
            return generation

        # Avanza a la siguiente generación
        print(f"\n== Generación {generation + 1}")
        pairs = schedule_pairs(men, women, params)
        men, women, _ = mix_and_make_children(pairs, men, women, params)
        generation += 1
