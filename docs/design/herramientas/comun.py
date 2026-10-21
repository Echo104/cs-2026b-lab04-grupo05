"""Utilidades para leer los diagramas de diseño (PlantUML/Mermaid) y el código Python."""
import ast
import re
from pathlib import Path

DESIGN = Path(__file__).resolve().parents[1]
SRC = DESIGN.parents[1] / "src" / "votacion" / "dominio.py"


def snake(nombre: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", nombre).lower()


def leer_clases_puml(ruta: Path = DESIGN / "clases.puml") -> dict:
    """Devuelve {clase: {"tipo","estereotipo","attrs":[...],"ops":[...],"valores":[...]}}."""
    clases, actual = {}, None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(class|enum|interface)\s+(\w+)(?:\s+<<(\w+)>>)?\s*(\{)?\s*$", linea)
        if m:
            actual = m.group(2)
            clases[actual] = {"tipo": m.group(1), "estereotipo": m.group(3),
                              "attrs": [], "ops": [], "valores": []}
            if not m.group(4):
                actual = None
            continue
        if actual is None:
            continue
        if linea.strip() == "}":
            actual = None
            continue
        op = re.match(r"^\s*[-+#~]\s+(\w+)\((.*)\):\s*(.+)$", linea)
        at = re.match(r"^\s*[-+#~]\s+(\w+):\s*(.+)$", linea)
        if op:
            clases[actual]["ops"].append(op.group(1))
        elif at:
            clases[actual]["attrs"].append(at.group(1))
        elif linea.strip() and clases[actual]["tipo"] == "enum":
            clases[actual]["valores"].append(linea.strip())
    return clases


def leer_codigo(ruta: Path = SRC) -> dict:
    """Ingeniería inversa mínima con ast: {clase: {"tipo","bases","attrs","ops","valores"}}."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    salida = {}
    for nodo in arbol.body:
        if not isinstance(nodo, ast.ClassDef):
            continue
        bases = [ast.unparse(b) for b in nodo.bases]
        tipo = "enum" if "Enum" in bases else "interface" if "ABC" in bases else \
            "excepcion" if any(b.endswith("Exception") for b in bases) else "class"
        info = {"tipo": tipo, "bases": bases, "attrs": [], "ops": [], "valores": []}
        for it in nodo.body:
            if isinstance(it, ast.AnnAssign) and isinstance(it.target, ast.Name):
                info["attrs"].append(it.target.id)
            elif isinstance(it, ast.Assign) and tipo == "enum":
                info["valores"] += [t.id for t in it.targets if isinstance(t, ast.Name)]
            elif isinstance(it, ast.FunctionDef):
                if it.name == "__init__":
                    for a in it.args.args[1:]:
                        info["attrs"].append("_" + a.arg)  # atributos privados del servicio
                else:
                    info["ops"].append(it.name)
        salida[nodo.name] = info
    return salida
