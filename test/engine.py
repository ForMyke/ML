# test/engine.py  (reemplaza TODO el archivo por esta versión con logs)
from typing import List, Dict, Optional, Tuple
from .variables import Params
from genes.individual import gen_human, check_perfect, mix_humans_verbose

# {'id': int, 'genes': list[int], 'parents': (id,id), 'grandparents': set[id]}
Person = Dict[str, object]

def make_person(next_id: int, genes: list[int],
                parents: Tuple[Optional[int], Optional[int]] = (None, None),
                gp: Optional[set] = None) -> Person:
    return {
        "id": next_id,
        "genes": genes,
        "parents": parents,
        "grandparents": set() if gp is None else set(gp)
    }

def build_initial_population(params: Params) -> Tuple[List[Person], List[Person]]:
    men: List[Person] = []
    women: List[Person] = []
    nid = 0
    for _ in range(params.numCouples):
        women.append(make_person(nid, gen_human(params))); nid += 1
        men.append(make_person(nid, gen_human(params))); nid += 1
    print(f"\n== Generación 0 (población inicial)")
    print(f"Total mujeres: {len(women)} | Total hombres: {len(men)}")
    return men, women

def are_related(a: Person, b: Person) -> bool:
    """True si comparten algún padre o algún abuelo (primos)."""
    pa = set([p for p in a["parents"] if p is not None])
    pb = set([p for p in b["parents"] if p is not None])
    if pa and pb and pa.intersection(pb):
        return True  # hermanos
    ga = a["grandparents"]
    gb = b["grandparents"]
    return bool(ga.intersection(gb))  # primos

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
    """Empareja evitando primos; si faltan 2 parejas, los últimos 4 actúan como pivote.
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
    allowed_relaxed = set(range(n - 2, n))  # índices de hombres n-2 y n-1
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

def mix_and_make_children(pairs: List[Tuple[int, int, bool]],
                          men: List[Person], women: List[Person],
                          params: Params) -> Tuple[List[Person], List[Person], bool]:
    """Genera la siguiente generación preservando linaje y LOGS detallados."""
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

        # Abuelos: unión de padres y abuelos de ambos
        wgp = set([p for p in w["parents"] if p is not None]) | set(w["grandparents"])
        mgp = set([p for p in m["parents"] if p is not None]) | set(m["grandparents"])
        gp = wgp | mgp

        child_w = {"id": next_id, "genes": h1, "parents": (w["id"], m["id"]), "grandparents": set(gp)}; next_id += 1
        child_m = {"id": next_id, "genes": h2, "parents": (w["id"], m["id"]), "grandparents": set(gp)}; next_id += 1

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

    print(f"  Mutaciones totales: hija(s)={total_mut_c1}, hijo(s)={total_mut_c2}")
    return next_men, next_women, perfect

def get_generation(params: Params) -> int:
    generation = 0
    men, women = build_initial_population(params)

    perfect = any(check_perfect(p["genes"], params) for p in men + women)

    while not perfect:
        print(f"\n== Generación {generation + 1}")
        pairs = schedule_pairs(men, women, params)
        men, women, perfect = mix_and_make_children(pairs, men, women, params)
        generation += 1

    print(f"\n>> ¡Individuo perfecto alcanzado en la generación {generation}!")
    return generation
