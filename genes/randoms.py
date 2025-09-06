# genes/randoms.py
import random
from test.variables import Params

def random_number(params: Params) -> int:
    """Usa distribución uniforme para la población inicial."""
    return random.randint(params.MIN_LIM, params.MAX_LIM)

def random_number_mutation(params: Params) -> int:
    """También uniforme para las mutaciones (consistente con la inicial)."""
    return random.randint(params.MIN_LIM, params.MAX_LIM)
