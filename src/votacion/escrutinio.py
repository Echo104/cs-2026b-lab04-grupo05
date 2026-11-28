"""Conteo de votos al cierre de la elección (RF-04).

``contar`` recibe el identificador de lista de cada voto de la urna (``None`` = voto en blanco)
y devuelve un diccionario con:
  - ``por_lista``: votos de cada lista (sin incluir los votos en blanco),
  - ``en_blanco``: cantidad de votos en blanco,
  - ``validos``: votos que cuentan para una lista,
  - ``total``: todos los votos de la urna.
"""
from __future__ import annotations

from collections.abc import Iterable

BLANCO = "BLANCO"


def contar(votos: Iterable[str | None]) -> dict:
    por_lista: dict[str, int] = {}
    total = 0
    for voto in votos:
        clave = BLANCO if voto is None else voto
        por_lista[clave] = por_lista.get(clave, 0) + 1
        total += 1
    return {"por_lista": por_lista, "validos": sum(por_lista.values()), "total": total}
