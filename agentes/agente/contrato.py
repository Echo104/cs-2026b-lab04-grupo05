"""Contrato estructurado de cada decisión del modelo (Koenigstein, 2026, cap. 5)."""
from __future__ import annotations


def validar_decision(d, herramientas_conocidas) -> tuple[bool, str]:
    """Devuelve (True, "") si la decisión cumple el protocolo; si no, (False, motivo)."""
    if not isinstance(d, dict):
        return False, "la decisión debe ser un objeto JSON"
    if not isinstance(d.get("pensamiento"), str) or not d["pensamiento"].strip():
        return False, "falta 'pensamiento' (texto no vacío)"
    if ("final" in d) == ("accion" in d):
        return False, "debe incluir 'accion' o 'final', pero no ambos"
    if "final" in d:
        extra = set(d) - {"pensamiento", "final"}
        if extra:
            return False, f"campos no permitidos: {sorted(extra)}"
        return (True, "") if isinstance(d["final"], str) and d["final"].strip() else (False, "'final' debe ser texto no vacío")
    if d["accion"] not in herramientas_conocidas:
        return False, f"herramienta desconocida: {d['accion']!r}"
    if not isinstance(d.get("args", {}), dict):
        return False, "'args' debe ser un objeto JSON"
    extra = set(d) - {"pensamiento", "accion", "args"}
    return (False, f"campos no permitidos: {sorted(extra)}") if extra else (True, "")
