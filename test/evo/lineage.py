# test/evo/lineage.py
from .models import Person

def are_related(a: Person, b: Person) -> bool:
    """
    True si comparten:
      - algún padre (hermanos),
      - o algún abuelo (primos),
      - o algún bisabuelo (primos en segundo grado).
    """
    # Padres
    pa = {p for p in a["parents"] if p is not None}
    pb = {p for p in b["parents"] if p is not None}
    if pa and pb and (pa & pb):
        return True  # hermanos

    # Abuelos
    ga = a.get("grandparents", set())
    gb = b.get("grandparents", set())
    if ga and gb and (ga & gb):
        return True  # primos

    # Bisabuelos
    gga = a.get("greatgrandparents", set())
    ggb = b.get("greatgrandparents", set())
    if gga and ggb and (gga & ggb):
        return True  # primos en segundo grado

    return False
