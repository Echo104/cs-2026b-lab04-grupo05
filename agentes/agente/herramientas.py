"""Herramientas del agente: pocas, pequeñas y con el alcance mínimo (Tabla 5 de la guía).

Todas las rutas se validan contra el sandbox (la raíz de la COPIA del repositorio) y los
errores vuelven al agente como observaciones.
"""
from __future__ import annotations

import ast
import difflib
import os
import pathlib
import re
import shlex
import subprocess
import sys

EXCLUIDOS = {".git", "__pycache__", "node_modules", ".pytest_cache", "trazas"}
NOTAS = "notas.md"               # memoria de notas (Sección 1.6): vive en la copia del repositorio
MAX_NOTA, MAX_NOTAS_TOTAL = 300, 2000
LIMITE_MAPA = 6000


def _nombres(funcion) -> str:
    """Solo los nombres de los parámetros (sin anotaciones ni valores por defecto): el mapa debe ser corto."""
    a = funcion.args
    nombres = [x.arg for x in a.posonlyargs + a.args + a.kwonlyargs]
    if a.vararg:
        nombres.append("*" + a.vararg.arg)
    if a.kwarg:
        nombres.append("**" + a.kwarg.arg)
    return ", ".join(n for n in nombres if n != "self")
SUFIJOS_TEXTO = {".py", ".md", ".txt", ".toml", ".cfg", ".ini", ".yml", ".yaml", ".json"}


class Herramientas:
    def __init__(self, raiz, habilitadas=None):
        """``habilitadas``: nombres de las herramientas que el modelo puede ver (None = todas)."""
        self.raiz = pathlib.Path(raiz).resolve()
        self._habilitadas = None if habilitadas is None else set(habilitadas)
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
            if archivo.relative_to(self.raiz).as_posix() == NOTAS:
                continue                                   # las notas no son parte del cambio propuesto
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
        todas = {
            "listar_archivos": "listar_archivos(ruta='.'): lista los archivos de texto de una carpeta del repositorio.",
            "leer_archivo": "leer_archivo(ruta): devuelve el contenido de un archivo (máx. 6000 caracteres).",
            "buscar": "buscar(patron, ruta='.'): busca una expresión regular; devuelve 'archivo:línea: texto' (máx. 20).",
            "ejecutar_pruebas": "ejecutar_pruebas(ruta='tests'): ejecuta pytest sobre un archivo, carpeta o 'archivo::prueba'; devuelve el resumen.",
            "editar_archivo": "editar_archivo(ruta, antes, despues): reemplaza un fragmento que debe aparecer EXACTAMENTE una vez.",
            "ver_cambios": "ver_cambios(): devuelve el diff de todo lo modificado desde el inicio de la tarea.",
            "ejecutar_comando": "ejecutar_comando(comando): solo 'python -m pytest', 'radon cc', 'lint-imports' o 'git status/diff'.",
            "mapa_repo": "mapa_repo(ruta='src'): estructura del código (módulos con la primera línea de su docstring, clases con sus métodos y funciones, con los nombres de sus parámetros), obtenida con ast; úsala ANTES de leer archivos completos para ubicar dónde está la lógica.",
            "anotar": "anotar(texto): guarda una nota breve (hipótesis o archivos ya revisados) en notas.md; máx. 300 caracteres por nota.",
            "leer_notas": "leer_notas(): devuelve las notas guardadas en esta tarea.",
        }
        return todas if self._habilitadas is None else {k: v for k, v in todas.items() if k in self._habilitadas}

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

    # ---------------------------------------------------------------- E4: mapa del repositorio y notas
    def mapa_repo(self, ruta: str = "src") -> str:
        base = self._ruta(ruta)
        if not base.exists():
            return f"ERROR: {ruta} no existe"
        archivos = [base] if base.is_file() else sorted(a for a in base.rglob("*.py") if "__pycache__" not in a.parts)
        lineas = []
        for archivo in archivos:
            rel = archivo.relative_to(self.raiz).as_posix()
            try:
                arbol = ast.parse(archivo.read_text(encoding="utf-8"))
            except SyntaxError as e:
                lineas.append(f"{rel}  [ERROR de sintaxis: {e.msg}]")
                continue
            resumen = (ast.get_docstring(arbol) or "").splitlines()
            lineas.append(f"{rel}" + (f"  — {resumen[0][:60]}" if resumen else ""))
            for nodo in arbol.body:
                if isinstance(nodo, ast.ClassDef):
                    metodos = [f"{m.name}({_nombres(m)})" for m in nodo.body
                               if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and not m.name.startswith("__")]
                    lineas.append(f"  class {nodo.name}" + (": " + ", ".join(metodos) if metodos else ""))
                elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    lineas.append(f"  def {nodo.name}({_nombres(nodo)})")
        salida = "\n".join(lineas) or "(sin archivos .py)"
        return salida if len(salida) <= LIMITE_MAPA else salida[:LIMITE_MAPA] + "\n... (recortado: pida una subcarpeta)"

    def anotar(self, texto: str) -> str:
        if not isinstance(texto, str) or not texto.strip():
            return "ERROR: la nota debe ser un texto no vacío"
        if len(texto) > MAX_NOTA:
            return f"ERROR: la nota supera {MAX_NOTA} caracteres"
        archivo = self.raiz / NOTAS
        previo = archivo.read_text(encoding="utf-8") if archivo.exists() else ""
        linea = "- " + " ".join(texto.split()) + "\n"
        if len(previo) + len(linea) > MAX_NOTAS_TOTAL:
            return f"ERROR: las notas superarían {MAX_NOTAS_TOTAL} caracteres; resuma o priorice"
        archivo.write_text(previo + linea, encoding="utf-8")
        return f"OK: nota guardada ({previo.count(chr(10)) + 1} en total)"

    def leer_notas(self) -> str:
        archivo = self.raiz / NOTAS
        return archivo.read_text(encoding="utf-8") if archivo.exists() else "(sin notas)"
