import random
from math import ceil, floor
from test.variables import Params

def random_number(params: Params) -> int:
    """Randomización hacia abajo (gauss -> floor)"""
    rnum = random.gauss(params.mu, params.sd)
    rnum = floor(rnum)
    if rnum > params.MAX_LIM:
        rnum = params.MAX_LIM
    if rnum < params.MIN_LIM:
        rnum = params.MIN_LIM
    return rnum

def random_number_mutation(params: Params) -> int:
    """Randomización hacia arriba (gauss -> ceil)"""
    rnum = random.gauss(params.mu, params.sd)
    rnum = ceil(rnum)
    if rnum > params.MAX_LIM:
        rnum = params.MAX_LIM
    if rnum < params.MIN_LIM:
        rnum = params.MIN_LIM
    return rnum
