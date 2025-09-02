from test.engine import get_generation
from test.variables import DEFAULT_PARAMS
import numpy as np

if __name__ == "__main__":
    tests = 1
    gens = np.array([get_generation(DEFAULT_PARAMS) for _ in range(tests)])
    print(f"Generacion...  {int(gens.sum()) // tests}")
