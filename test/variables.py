from dataclasses import dataclass

@dataclass(frozen=True)
class Params:
    numgen: int = 100
    numCouples: int = 50
    mutationProbability: float = 0.20
    numAttributes: int = 20
    MIN_LIM: int = 1
    MAX_LIM: int = 9

#Constantes originales
DEFAULT_PARAMS = Params()
