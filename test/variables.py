from dataclasses import dataclass

@dataclass(frozen=True)
class Params:
    numgen: int = 100
    numCouples: int = 50
    mutationProbability: float = 0.01
    numAttributes: int = 20
    MIN_LIM: int = 1
    MAX_LIM: int = 9
    mu: int = 9
    sd: int = 1

    @property
    def limit(self) -> float:
        return self.mutationProbability * self.numgen

#Constantes originales
DEFAULT_PARAMS = Params()
