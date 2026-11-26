import re
from pathlib import Path

RAIZ = Path(__file__).parent


def _normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()


def _renderizar(plantilla: str, variables: dict) -> str:
    return re.sub(r"\{\{\s*(\w+)\s*\}\}", lambda m: str(variables.get(m.group(1), m.group(0))), plantilla)


def _version(prompt: str, context: dict, tarea: Path, plantillas: Path) -> str | None:
    etiqueta = ((context or {}).get("prompt") or {}).get("label")
    if etiqueta and (tarea / "grabaciones" / etiqueta).is_dir():
        return etiqueta
    variables = (context or {}).get("vars") or {}
    for archivo in sorted(plantillas.glob("v*.txt")):
        if _normalizar(_renderizar(archivo.read_text(encoding="utf-8"), variables)) == _normalizar(prompt):
            return archivo.stem
    return None


def call_api(prompt, options, context):
    config = (options or {}).get("config") or {}
    tarea = config.get("tarea", "criterios")
    # Las plantillas pueden estar en otra carpeta (p. ej. seguridad/ reutiliza criterios/).
    plantillas = RAIZ / config.get("plantillas", tarea)
    version = _version(prompt, context, RAIZ / tarea, plantillas)
    caso = ((context or {}).get("vars") or {}).get("id")
    if not version or not caso:
        return {"error": f"No se pudo identificar la versión ({version}) o el caso ({caso})"}
    ruta = RAIZ / tarea / "grabaciones" / version / f"{caso}.txt"
    if not ruta.exists():
        return {"error": f"Falta la grabación {ruta.relative_to(RAIZ)}"}
    return {"output": ruta.read_text(encoding="utf-8")}
