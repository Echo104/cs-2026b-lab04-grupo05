import pathlib
import sys

# Permite `python -m pytest agentes/pruebas_agente` desde la raíz del repositorio e importar `agente`.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
