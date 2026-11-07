import pathlib
import sys

# Permite ejecutar `pytest` desde la raíz del repositorio e importar `src.votacion...`
sys.path.insert(0, str(pathlib.Path(__file__).parent))
