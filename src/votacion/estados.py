"""STATE: ciclo de vida de la elección (máquina de estados del Lab 05).

La clase base `Etapa` PROHÍBE todas las operaciones; cada etapa redefine solo las
transiciones permitidas por `docs/design/estados-eleccion.mmd`. Una transición inválida es
imposible por construcción y ninguna etapa pregunta por el nombre de otra.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .excepciones import EleccionNoAbierta, TransicionInvalida

if TYPE_CHECKING:  # solo para anotaciones; evita una importación circular
    from .dominio import Eleccion, Lista


class Etapa:
    nombre = "?"

    def agregar_lista(self, eleccion: Eleccion, lista: Lista) -> None:
        raise TransicionInvalida(f"No se puede agregar una lista en una elección {self.nombre}")

    def abrir(self, eleccion: Eleccion) -> None:
        raise TransicionInvalida(f"No se puede abrir una elección {self.nombre}")

    def esta_abierta(self, eleccion: Eleccion, ahora: datetime) -> bool:
        return False

    def verificar_votable(self, eleccion: Eleccion, ahora: datetime) -> None:
        raise EleccionNoAbierta("La elección no está abierta")

    def cerrar(self, eleccion: Eleccion, ahora: datetime) -> None:
        raise TransicionInvalida(f"No se puede cerrar una elección {self.nombre}")

    def registrar_discrepancia(self, eleccion: Eleccion) -> None:
        raise TransicionInvalida(f"No se puede registrar una discrepancia en una elección {self.nombre}")

    def escrutar(self, eleccion: Eleccion, votos: int, participaciones: int,
                 auditor_coincide: bool) -> None:
        raise TransicionInvalida(f"No se puede escrutar una elección {self.nombre}")

    def publicar(self, eleccion: Eleccion, acta_firmada: bool) -> None:
        raise TransicionInvalida(f"No se puede publicar una elección {self.nombre}")


class Configurada(Etapa):
    nombre = "CONFIGURADA"

    def agregar_lista(self, eleccion, lista):
        eleccion.listas.append(lista)                      # CONFIGURADA -> CONFIGURADA

    def abrir(self, eleccion):
        if eleccion.total_padron <= 0 or not eleccion.listas:
            raise TransicionInvalida("Se requiere padrón cargado y al menos una lista")
        eleccion.cambiar_a(Abierta())


class Abierta(Etapa):
    nombre = "ABIERTA"

    def esta_abierta(self, eleccion, ahora):
        return (eleccion.apertura is not None and eleccion.cierre is not None
                and eleccion.apertura <= ahora < eleccion.cierre)

    def verificar_votable(self, eleccion, ahora):
        if not self.esta_abierta(eleccion, ahora):
            raise EleccionNoAbierta("Fuera del horario de votación")

    def cerrar(self, eleccion, ahora):
        if eleccion.cierre is None or ahora < eleccion.cierre:
            raise TransicionInvalida("Aún no se alcanza la hora de cierre")
        eleccion.cambiar_a(Cerrada())


class Cerrada(Etapa):
    nombre = "CERRADA"

    def registrar_discrepancia(self, eleccion):
        eleccion.discrepancias += 1                        # CERRADA -> CERRADA

    def escrutar(self, eleccion, votos, participaciones, auditor_coincide):
        if votos != participaciones or not auditor_coincide:
            raise TransicionInvalida("El recuento oficial y el del auditor deben coincidir")
        eleccion.cambiar_a(Escrutada())


class Escrutada(Etapa):
    nombre = "ESCRUTADA"

    def publicar(self, eleccion, acta_firmada):
        if not acta_firmada:
            raise TransicionInvalida("El acta debe estar firmada")
        eleccion.cambiar_a(Publicada())


class Publicada(Etapa):
    nombre = "PUBLICADA"                                   # estado final: sin transiciones


_ETAPAS = {etapa.nombre: etapa for etapa in (Configurada, Abierta, Cerrada, Escrutada, Publicada)}


def etapa_desde_nombre(nombre: str) -> Etapa:
    """FACTORY METHOD: crea la etapa que corresponde al nombre del estado."""
    if nombre not in _ETAPAS:
        raise ValueError(f"Estado de elección desconocido: {nombre}")
    return _ETAPAS[nombre]()
