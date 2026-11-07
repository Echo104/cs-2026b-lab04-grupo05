"""OBSERVER: el servicio publica hechos y los interesados se suscriben, sin que el servicio los conozca.

Los datos del evento `voto_registrado` NUNCA incluyen la lista elegida (secreto del voto, R-06).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .dominio import CanalComprobante


class Suscriptor(ABC):
    @abstractmethod
    def actualizar(self, evento: str, datos: dict) -> None: ...


class PublicadorEventos:
    def __init__(self) -> None:
        self._suscriptores: dict[str, list[Suscriptor]] = {}
        self.fallos: list[tuple[str, str, str]] = []   # (evento, suscriptor, error)

    def suscribir(self, evento: str, suscriptor: Suscriptor) -> None:
        self._suscriptores.setdefault(evento, []).append(suscriptor)

    def publicar(self, evento: str, datos: dict) -> None:
        for suscriptor in list(self._suscriptores.get(evento, [])):
            try:
                suscriptor.actualizar(evento, datos)
            except Exception as error:  # un suscriptor defectuoso no afecta a los demás ni al voto
                self.fallos.append((evento, type(suscriptor).__name__, str(error)))


class NotificadorComprobante(Suscriptor):
    """Entrega el comprobante por el canal elegido; si falla, publica `notificacion_fallida`."""

    def __init__(self, canal: CanalComprobante, publicador: PublicadorEventos):
        self._canal, self._publicador = canal, publicador

    def actualizar(self, evento, datos):
        try:
            self._canal.enviar_comprobante(datos["correo"], datos["comprobante"])
        except Exception:
            self._publicador.publicar("notificacion_fallida", {"eleccion_id": datos["eleccion_id"]})


class RegistroEventos(Suscriptor):
    """Bitácora de auditoría: guarda solo el nombre del evento (sin identidad del estudiante)."""

    def __init__(self, bandeja: list[str]):
        self._bandeja = bandeja

    def actualizar(self, evento, datos):
        self._bandeja.append(evento)
