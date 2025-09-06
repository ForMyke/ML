# genes/randoms.py
import random
from test.variables import Params

def random_number(params: Params) -> int:
    """Valor uniforme entero dentro de [MIN_LIM, MAX_LIM]."""
    return random.randint(params.MIN_LIM, params.MAX_LIM)

def random_number_mutation(params: Params) -> int:
    """Valor uniforme entero para mutación dentro de [MIN_LIM, MAX_LIM]."""
    return random.randint(params.MIN_LIM, params.MAX_LIM)
