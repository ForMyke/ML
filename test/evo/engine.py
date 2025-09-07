# test/evo/engine.py
from ..variables import Params
from .population import build_initial_population, print_population
from .matching import schedule_pairs
from .reproduction import mix_and_make_children
from genes.individual import check_perfect

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
