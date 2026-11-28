"""Ejecuta UN agente sobre un issue, en una COPIA del repositorio (nunca en el repositorio real).

Uso (desde la raíz del repositorio o desde agentes/):
    python agentes/correr_issue.py 1                  # reproduce la trayectoria grabada del issue 1
    python agentes/correr_issue.py 1 --interactivo    # usted pega las respuestas de su asistente de IA

El agente trabaja en un directorio temporal, genera la traza (JSONL), el diagrama (.mmd/.png) y el
cambio propuesto (.diff). Quien incorpora el cambio al repositorio es una persona.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import sys
import tempfile

AGENTES = pathlib.Path(__file__).resolve().parent
RAIZ_REPO = AGENTES.parent
sys.path.insert(0, str(AGENTES))

from agente.herramientas import Herramientas          # noqa: E402
from agente.modelos import ModeloGrabado, ModeloInteractivo  # noqa: E402
from agente.nucleo import Agente                      # noqa: E402
from agente.politica import Politica                  # noqa: E402
from agente.protocolo import PROTOCOLO                # noqa: E402
from agente import traza as tz                        # noqa: E402

IGNORAR = shutil.ignore_patterns(".git", "__pycache__", "node_modules", ".pytest_cache", "trazas", "agentes",
                                 "prompts", "docs", ".github", "*.pyc", "*.png")


def preparar_copia() -> pathlib.Path:
    destino = pathlib.Path(tempfile.mkdtemp(prefix="agente-")) / "repo"
    shutil.copytree(RAIZ_REPO, destino, ignore=IGNORAR)
    return destino


def objetivo(issue: int, h: Herramientas) -> str:
    catalogo = "\n".join(f"  - {d}" for d in h.catalogo().values())
    return (f"{PROTOCOLO}\n\nObjetivo: resuelve el issue descrito en issues/ISSUE-{issue:02d}.md. La prueba que "
            f"indica el issue debe pasar y no debes modificar las pruebas.\nHerramientas:\n{catalogo}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("issue", type=int)
    ap.add_argument("--interactivo", action="store_true", help="usar ModeloInteractivo (copiar y pegar con su asistente)")
    ap.add_argument("--trayectoria", help="archivo JSON de decisiones (por defecto trayectorias/issueNN.json)")
    ap.add_argument("--traza", help="nombre base de la traza (por defecto issueNN)")
    args = ap.parse_args()

    nombre = args.traza or f"issue{args.issue:02d}"
    trayectoria = pathlib.Path(args.trayectoria) if args.trayectoria else AGENTES / "trayectorias" / f"issue{args.issue:02d}.json"
    copia = preparar_copia()
    h = Herramientas(copia)
    modelo = ModeloInteractivo(trayectoria) if args.interactivo else ModeloGrabado.desde_archivo(trayectoria)
    agente = Agente("Ejecutor", modelo, h, Politica(max_pasos=12), objetivo(args.issue, h),
                    AGENTES / "trazas" / f"{nombre}.jsonl")
    agente.registrar_preparacion(f"copia del repositorio en {copia}")
    resumen = agente.ejecutar()

    (AGENTES / "trazas" / f"{nombre}-cambio.diff").write_text(h.ver_cambios(), encoding="utf-8")
    print(f"\nRESUMEN DEL AGENTE:\n{resumen}\n")
    tz.main([str(AGENTES / "trazas" / f"{nombre}.jsonl")])
    print(f"Cambio propuesto: agentes/trazas/{nombre}-cambio.diff (revíselo y aplíquelo usted; el agente no fusiona nada)")


if __name__ == "__main__":
    main()
