# test/evo/matching.py
from typing import List, Tuple, Optional
from collections import deque
import random as _r
from ..variables import Params
from .models import Person
from .lineage import are_related

# --------- Heurística de calidad ----------
def individual_score(genes: List[int]) -> int:
    return sum(genes)

def pair_score(w_genes: List[int], m_genes: List[int]) -> int:
    return sum(w_genes) + sum(m_genes)

# --------- Hopcroft–Karp ----------
def hopcroft_karp(adj: List[List[int]], n_left: int, n_right: int) -> Tuple[dict, List[int]]:
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

# --------- Emparejamiento ----------
def schedule_pairs(men: List[Person], women: List[Person], params: Params) -> List[Tuple[int, int, bool]]:
    """
    Empareja evitando parentesco hasta bisabuelos.
    Heurística “mejores primero”:
      - Para cada hombre, ordena sus aristas (mujeres permitidas) por mayor pair_score.
      - En el post-proceso (unmatched), elige la mejor mujer disponible por score.
    Respeta pivote: últimos 2 hombres se pueden emparejar sin restricción si es necesario.
    Devuelve (idx_hombre, idx_mujer, relajado?).
    """
    n = len(men)

    # Precompute scores
    men_scores   = [individual_score(m["genes"]) for m in men]
    women_scores = [individual_score(w["genes"]) for w in women]

    # Para cada hombre i, construir lista de (j, score_ij) sólo si NO son parientes
    adj_scored: List[List[Tuple[int, int]]] = []
    for i, m in enumerate(men):
        edges_scored = []
        for j, w in enumerate(women):
            if not are_related(m, w):
                s = pair_score(w["genes"], m["genes"])
                edges_scored.append((j, s))
        # Ordenamos por score descendente; desempate aleatorio para diversidad
        _r.shuffle(edges_scored)
        edges_scored.sort(key=lambda t: t[1], reverse=True)
        adj_scored.append(edges_scored)

    # Adyacencia para HK (sólo índices), preservando el orden por score
    adj: List[List[int]] = [[j for (j, _) in edges] for edges in adj_scored]

    matching, unmatched = hopcroft_karp(adj, n, n)

    pairs: List[Tuple[int, int, bool]] = []
    # matching normal
    for i in range(n):
        if i in matching:
            pairs.append((i, matching[i], False))

    # Relaxation pivot: últimos 2 hombres
    last2 = max(0, n - 2)
    allowed_relaxed = set(range(last2, n))
    used_women = set(matching.values())

    # Índice rápido: para un (i), obtener mejor mujer disponible por score
    def best_available_for(i: int, must_avoid_kin: bool) -> Optional[int]:
        if must_avoid_kin:
            # recorrer su lista ya ordenada por score y tomar la primera mujer libre
            for j, _ in adj_scored[i]:
                if j not in used_women:
                    return j
            return None
        else:
            # si podemos romper parentesco (pivote), elegir la mejor disponible por score “global”
            candidates = []
            for j in range(n):
                if j in used_women:
                    continue
                s = men_scores[i] + women_scores[j]
                candidates.append((j, s))
            if not candidates:
                return None
            candidates.sort(key=lambda t: t[1], reverse=True)
            return candidates[0][0]

    # Asignar no emparejados con la mejor opción disponible
    for i in unmatched:
        # primero, intentar mantener la restricción
        j = best_available_for(i, must_avoid_kin=True)
        if j is not None:
            used_women.add(j)
            pairs.append((i, j, False))
            continue

        # si no hay opción y está en zona pivote, permitir relajación
        if i in allowed_relaxed:
            j = best_available_for(i, must_avoid_kin=False)
            if j is not None:
                used_women.add(j)
                pairs.append((i, j, True))
                continue

        # último recurso: forzar relajado con la mejor disponible
        j = best_available_for(i, must_avoid_kin=False)
        if j is not None:
            used_women.add(j)
            pairs.append((i, j, True))

    pairs.sort(key=lambda x: x[0])
    return pairs
