"""Canal de entrega del comprobante: STRATEGY + ADAPTER + FACTORY (registro).

`CanalComprobante` (en `dominio.py`) es la interfaz común. Cada servicio externo se
adapta a ella y la fábrica crea el canal elegido por nombre; agregar un canal nuevo
es registrar un creador, no modificar el servicio (abierto/cerrado).
"""
from __future__ import annotations

from collections.abc import Callable

from .dominio import CanalComprobante, Comprobante
from .externos import ServicioCorreoExterno


class CorreoAdapter(CanalComprobante):
    """ADAPTER: traduce el comprobante del dominio al diccionario que espera el SMTP externo."""

    def __init__(self, servicio: ServicioCorreoExterno):
        self._servicio = servicio

    def enviar_comprobante(self, correo: str, comprobante: Comprobante) -> None:
        self._servicio.enviar_comprobante(
            correo, {"codigo": comprobante.codigo, "fecha": comprobante.fecha_hora}
        )


class FabricaCanales:
    """FACTORY (registro): crea el canal adecuado por nombre."""

    def __init__(self) -> None:
        self._creadores: dict[str, Callable[[], CanalComprobante]] = {}

    def registrar(self, canal: str, creador: Callable[[], CanalComprobante]) -> None:
        self._creadores[canal] = creador

    def crear(self, canal: str) -> CanalComprobante:
        if canal not in self._creadores:
            raise ValueError(f"Canal de comprobante no soportado: {canal}")
        return self._creadores[canal]()
