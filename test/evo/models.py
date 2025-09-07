# test/evo/models.py
from typing import Dict, Optional, Tuple, List, Set

# Person schema:
# {'id': int, 'genes': list[int], 'gen': int,
#  'parents': (madre_id, padre_id),
#  'grandparents': set[int],          # abuelos (gen - 2)
#  'greatgrandparents': set[int],     # bisabuelos (gen - 3)
#  'relaxed': bool}
Person = Dict[str, object]

def make_person(next_id: int, genes: List[int], gen: int,
                parents: Tuple[Optional[int], Optional[int]] = (None, None),
                gp: Optional[Set[int]] = None,
                ggp: Optional[Set[int]] = None,
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
