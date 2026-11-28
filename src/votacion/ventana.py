"""Ventana de votación (RF-07): la elección está abierta entre su apertura y su cierre.

``esta_abierta`` es una función pura que usa el reloj de cierre y la pantalla de votación. La
elección se abre en ``apertura`` (inclusive) y se cierra exactamente en ``cierre`` (exclusive).
"""
from __future__ import annotations

from datetime import datetime


def esta_abierta(apertura: datetime, cierre: datetime, ahora: datetime) -> bool:
    return apertura <= ahora < cierre
