"""Padrón y participación (RF-03): un estudiante solo puede participar una vez por elección.

El padrón llega como archivo CSV con correos institucionales (en minúsculas). Este módulo lleva
la cuenta de quién ya participó. NO guarda ni conoce la lista elegida (el voto es secreto, ADR-002).
"""
from __future__ import annotations

from collections.abc import Iterable

from .excepciones import ParticipacionDuplicada


class Padron:
    def __init__(self, correos: Iterable[str]):
        self._habilitados = {c.lower() for c in correos}
        self._participaron: set[str] = set()

    def figura(self, correo: str) -> bool:
        return correo.lower() in self._habilitados

    def registrar_participacion(self, correo: str) -> None:
        """Marca que el estudiante ya participó; lanza ``ParticipacionDuplicada`` si lo repite."""
        if correo.lower() not in self._habilitados:
            raise ValueError("El correo no figura en el padrón")
        if correo in self._participaron:
            raise ParticipacionDuplicada(f"{correo} ya participó en la elección")
        self._participaron.add(correo)

    def total_participantes(self) -> int:
        return len(self._participaron)
