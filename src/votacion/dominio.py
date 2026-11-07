"""Dominio del módulo Votación de VotoEPIS (Lab 05) con los patrones del Lab 07.

Los nombres usan snake_case (equivalencia con el camelCase del diagrama, regla C5).
Los puertos (`RepositorioVotacion`, `CanalComprobante`) se implementan en `repositorio.py`
y `canales.py`; el servicio que los coordina vive en `servicio.py`.
"""
from __future__ import annotations

import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from .estados import Configurada, Etapa, etapa_desde_nombre
from .excepciones import (EleccionNoAbierta, ErrorTransitorio, ParticipacionDuplicada,  # noqa: F401
                          TransicionInvalida)

# UUID en producción; los dobles de prueba usan cadenas como identificador.
Identificador = UUID | str


class EstadoEleccion(Enum):
    CONFIGURADA = "CONFIGURADA"
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"
    ESCRUTADA = "ESCRUTADA"
    PUBLICADA = "PUBLICADA"


@dataclass
class Estudiante:
    correo_institucional: str
    id: Identificador = field(default_factory=uuid4)


@dataclass
class Lista:
    nombre: str
    id: Identificador = field(default_factory=uuid4)


@dataclass
class Eleccion:
    """Contexto del patrón STATE: delega cada operación en su etapa actual (`estados.py`)."""

    nombre: str = ""
    apertura: datetime | None = None
    cierre: datetime | None = None
    total_padron: int = 0
    discrepancias: int = 0
    listas: list[Lista] = field(default_factory=list)
    id: Identificador = field(default_factory=uuid4)
    _etapa: Etapa = field(default_factory=Configurada, repr=False, compare=False)

    @property
    def estado(self) -> EstadoEleccion:
        return EstadoEleccion(self._etapa.nombre)

    def cambiar_a(self, etapa: Etapa) -> None:
        self._etapa = etapa

    @classmethod
    def reconstruir(cls, estado: str, **campos) -> Eleccion:
        """Crea una elección ya existente (p. ej., leída de la BD) en el estado indicado."""
        eleccion = cls(**campos)
        eleccion.cambiar_a(etapa_desde_nombre(estado))
        return eleccion

    def configurar(self, nombre: str, apertura: datetime, cierre: datetime, total_padron: int) -> None:
        self.nombre, self.apertura, self.cierre = nombre, apertura, cierre
        self.total_padron = total_padron
        self.cambiar_a(Configurada())

    def agregar_lista(self, lista: Lista) -> None:
        self._etapa.agregar_lista(self, lista)

    def abrir(self) -> None:
        self._etapa.abrir(self)

    def esta_abierta(self, ahora: datetime) -> bool:
        return self._etapa.esta_abierta(self, ahora)

    def verificar_votable(self, ahora: datetime) -> None:
        """Lanza `EleccionNoAbierta` si no se puede votar en este instante."""
        self._etapa.verificar_votable(self, ahora)

    def cerrar(self, ahora: datetime) -> None:
        self._etapa.cerrar(self, ahora)

    def registrar_discrepancia(self) -> None:
        self._etapa.registrar_discrepancia(self)

    def escrutar(self, votos: int, participaciones: int, auditor_coincide: bool) -> None:
        self._etapa.escrutar(self, votos, participaciones, auditor_coincide)

    def publicar(self, acta_firmada: bool) -> None:
        self._etapa.publicar(self, acta_firmada)


@dataclass(frozen=True)
class Comprobante:
    codigo: str
    fecha_hora: datetime


@dataclass
class Participacion:
    estudiante: Estudiante
    eleccion: Eleccion
    fecha_hora: datetime

    def emitir_comprobante(self) -> Comprobante:
        # El código es aleatorio: no se deriva de la lista elegida (R-06).
        return Comprobante(codigo=secrets.token_hex(4).upper(), fecha_hora=self.fecha_hora)


@dataclass
class Voto:
    """Voto en la urna: sin referencia al estudiante y sin marca de tiempo (ADR-002)."""
    eleccion: Eleccion
    lista: Lista
    id: Identificador = field(default_factory=uuid4)


class CanalComprobante(ABC):  # puerto; rol STRATEGY: cómo se entrega el comprobante
    @abstractmethod
    def enviar_comprobante(self, correo: str, comprobante: Comprobante) -> None: ...


class RepositorioVotacion(ABC):  # puerto
    @abstractmethod
    def buscar_eleccion(self, id: Identificador) -> Eleccion: ...

    @abstractmethod
    def buscar_lista(self, id: Identificador, eleccion_id: Identificador) -> Lista: ...

    @abstractmethod
    def buscar_estudiante(self, id: Identificador) -> Estudiante: ...

    @abstractmethod
    def registrar(self, participacion: Participacion, voto: Voto) -> None:
        """Una sola transacción: padron.participacion (UNIQUE) + urna.voto."""
