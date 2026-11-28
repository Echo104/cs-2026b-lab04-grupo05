"""Herramientas del agente: pocas, pequeñas y con el alcance mínimo (Tabla 5 de la guía).

Todas las rutas se validan contra el sandbox (la raíz de la COPIA del repositorio) y los
errores vuelven al agente como observaciones.
"""
from __future__ import annotations

import difflib
import os
import pathlib
import re
import shlex
import subprocess
import sys

EXCLUIDOS = {".git", "__pycache__", "node_modules", ".pytest_cache", "trazas"}
SUFIJOS_TEXTO = {".py", ".md", ".txt", ".toml", ".cfg", ".ini", ".yml", ".yaml", ".json"}


class Herramientas:
    def __init__(self, raiz):
        self.raiz = pathlib.Path(raiz).resolve()
        self._base = self._leer_todo()                     # instantánea para ver_cambios

    # ---------------------------------------------------------------- utilidades
    def _ruta(self, ruta: str) -> pathlib.Path:
        p = (self.raiz / ruta).resolve()
        if self.raiz not in p.parents and p != self.raiz:
            raise PermissionError(f"Ruta fuera del sandbox: {ruta}")
        return p

    def _archivos(self):
        for actual, carpetas, nombres in os.walk(self.raiz):
            carpetas[:] = sorted(c for c in carpetas if c not in EXCLUIDOS)
            for nombre in sorted(nombres):
                archivo = pathlib.Path(actual) / nombre
                if archivo.suffix in SUFIJOS_TEXTO:
                    yield archivo

    def _leer_todo(self) -> dict[str, str]:
        base = {}
        for archivo in self._archivos():
            try:
                base[archivo.relative_to(self.raiz).as_posix()] = archivo.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
        return base

    def _correr(self, comando: list[str]) -> str:
        entorno = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            r = subprocess.run(comando, cwd=self.raiz, capture_output=True, text=True, timeout=60, env=entorno)
        except subprocess.TimeoutExpired:
            return "ERROR: el comando superó los 60 segundos"
        salida = (r.stdout + r.stderr).strip()
        return salida[-1500:] if salida else f"(sin salida; código {r.returncode})"

    # ---------------------------------------------------------------- catálogo
    def catalogo(self) -> dict[str, str]:
        """Nombre -> descripción (qué hace, parámetros y qué devuelve). El modelo elige solo con esto."""
        return {
            "listar_archivos": "listar_archivos(ruta='.'): lista los archivos de texto de una carpeta del repositorio.",
            "leer_archivo": "leer_archivo(ruta): devuelve el contenido de un archivo (máx. 6000 caracteres).",
            "buscar": "buscar(patron, ruta='.'): busca una expresión regular; devuelve 'archivo:línea: texto' (máx. 20).",
            "ejecutar_pruebas": "ejecutar_pruebas(ruta='tests'): ejecuta pytest sobre un archivo, carpeta o 'archivo::prueba'; devuelve el resumen.",
            "editar_archivo": "editar_archivo(ruta, antes, despues): reemplaza un fragmento que debe aparecer EXACTAMENTE una vez.",
            "ver_cambios": "ver_cambios(): devuelve el diff de todo lo modificado desde el inicio de la tarea.",
            "ejecutar_comando": "ejecutar_comando(comando): solo 'python -m pytest', 'radon cc', 'lint-imports' o 'git status/diff'.",
        }

    # ---------------------------------------------------------------- herramientas
    def listar_archivos(self, ruta: str = ".") -> str:
        base = self._ruta(ruta)
        if not base.is_dir():
            return f"ERROR: {ruta} no es una carpeta"
        rel = [a.relative_to(self.raiz).as_posix() for a in self._archivos() if base in a.parents]
        return "\n".join(rel[:150]) or "(sin archivos)"

    def leer_archivo(self, ruta: str) -> str:
        p = self._ruta(ruta)
        if not p.is_file():
            return f"ERROR: {ruta} no existe"
        texto = p.read_text(encoding="utf-8")
        return texto if len(texto) <= 6000 else texto[:6000] + "\n... (recortado)"

    def buscar(self, patron: str, ruta: str = ".") -> str:
        try:
            er = re.compile(patron)
        except re.error as e:
            return f"ERROR: expresión regular inválida ({e})"
        base, coincidencias = self._ruta(ruta), []
        for archivo in self._archivos():
            if base != archivo and base not in archivo.parents:
                continue
            for n, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), start=1):
                if er.search(linea):
                    coincidencias.append(f"{archivo.relative_to(self.raiz).as_posix()}:{n}: {linea.strip()[:120]}")
        return "\n".join(coincidencias[:20]) or "(sin coincidencias)"

    def ejecutar_pruebas(self, ruta: str = "tests") -> str:
        objetivo = self._ruta(ruta.split("::")[0])
        relativa = objetivo.relative_to(self.raiz).as_posix()
        if "::" in ruta:
            relativa += "::" + ruta.split("::", 1)[1]
        return self._correr([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", relativa])

    def editar_archivo(self, ruta: str, antes: str, despues: str) -> str:
        p = self._ruta(ruta)
        texto = p.read_text(encoding="utf-8")
        if texto.count(antes) != 1:
            return f"ERROR: el fragmento aparece {texto.count(antes)} veces; debe aparecer exactamente 1"
        p.write_text(texto.replace(antes, despues), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ver_cambios(self) -> str:
        actual, partes = self._leer_todo(), []
        for ruta in sorted(set(self._base) | set(actual)):
            antes, despues = self._base.get(ruta, ""), actual.get(ruta, "")
            if antes != despues:
                partes.extend(difflib.unified_diff(antes.splitlines(keepends=True), despues.splitlines(keepends=True),
                                                   fromfile=f"a/{ruta}", tofile=f"b/{ruta}"))
        return "".join(partes) or "(sin cambios)"

    def ejecutar_comando(self, comando: str) -> str:
        partes = shlex.split(comando)               # sin shell: no hay tuberías ni redirecciones
        if partes and partes[0] == "python":
            partes[0] = sys.executable
        try:
            return self._correr(partes)
        except FileNotFoundError:
            return f"ERROR: FileNotFoundError: comando no instalado en este entorno ({partes[0]})"
