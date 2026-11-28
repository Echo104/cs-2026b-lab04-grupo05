"""Política de cada agente: qué NO puede hacer (mínimo privilegio, Sección 1.8)."""
from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Decision:
    permitido: bool
    motivo: str = ""


BASICAS = frozenset({"listar_archivos", "leer_archivo", "buscar", "ejecutar_pruebas",
                     "editar_archivo", "ver_cambios", "ejecutar_comando"})
NUEVAS = frozenset({"mapa_repo", "anotar", "leer_notas"})          # E4: herramienta nueva y memoria de notas


@dataclass
class Politica:
    herramientas_permitidas: set = field(default_factory=lambda: set(BASICAS | NUEVAS))
    comandos_permitidos: tuple = (r"^python -m pytest\b", r"^radon cc\b", r"^lint-imports\b", r"^git (status|diff)\b")
    rutas_protegidas: tuple = ("tests/",)   # el agente no puede «arreglar» las pruebas para que pasen
    max_pasos: int = 15
    aprobar_edicion = None                    # función opcional: humano en el circuito (E6)

    def evaluar(self, accion: str, args: dict, paso: int) -> Decision:
        if paso > self.max_pasos:
            return Decision(False, f"Se alcanzó el máximo de {self.max_pasos} pasos")
        if accion not in self.herramientas_permitidas:
            return Decision(False, f"Herramienta no permitida: {accion}")
        if accion == "ejecutar_comando":
            cmd = args.get("comando", "")
            if not isinstance(cmd, str) or not any(re.search(p, cmd) for p in self.comandos_permitidos):
                return Decision(False, f"Comando fuera de la lista permitida: {cmd!r}")
        if accion == "editar_archivo":
            ruta = args.get("ruta", "")
            normal = posixpath.normpath(ruta.replace("\\", "/")).lstrip("/") if isinstance(ruta, str) else ""
            if not normal or normal.startswith(self.rutas_protegidas):
                return Decision(False, f"Ruta protegida: {ruta}")
            if self.aprobar_edicion and not self.aprobar_edicion(args):
                return Decision(False, "El revisor humano rechazó la edición")
        return Decision(True)
