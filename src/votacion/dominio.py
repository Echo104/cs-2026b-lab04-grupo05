"""Dominio del módulo Votación de VotoEPIS (Lab 05) preparado para los patrones del Lab 07.

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

# UUID en producción; los dobles de prueba usan cadenas como identificador.
Identificador = UUID | str


class EstadoEleccion(Enum):
    CONFIGURADA = "CONFIGURADA"
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"
    ESCRUTADA = "ESCRUTADA"
    PUBLICADA = "PUBLICADA"


class TransicionInvalida(ValueError):
    """La operación no está permitida en el estado actual o no cumple su guarda."""


class EleccionNoAbierta(ValueError):
    """Se intentó votar con la elección fuera de su ventana de votación."""


class ParticipacionDuplicada(ValueError):
    """El estudiante ya participó en la elección (restricción UNIQUE del padrón)."""


class ErrorTransitorio(TimeoutError):
    """Fallo temporal de la base de datos; el registro puede reintentarse."""


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
    nombre: str = ""
    apertura: datetime | None = None
    cierre: datetime | None = None
    total_padron: int = 0
    discrepancias: int = 0
    estado: EstadoEleccion = EstadoEleccion.CONFIGURADA
    listas: list[Lista] = field(default_factory=list)
    id: Identificador = field(default_factory=uuid4)

    @classmethod
    def reconstruir(cls, estado: str, **campos) -> Eleccion:
        """Crea una elección ya existente (p. ej., leída de la BD) en el estado indicado."""
        eleccion = cls(**campos)
        eleccion.estado = EstadoEleccion(estado)
        return eleccion

    def configurar(self, nombre: str, apertura: datetime, cierre: datetime, total_padron: int) -> None:
        self.nombre, self.apertura, self.cierre = nombre, apertura, cierre
        self.total_padron = total_padron
        self.estado = EstadoEleccion.CONFIGURADA

    def agregar_lista(self, lista: Lista) -> None:
        self._exigir(EstadoEleccion.CONFIGURADA)
        self.listas.append(lista)

    def abrir(self) -> None:
        self._exigir(EstadoEleccion.CONFIGURADA)
        if self.total_padron <= 0 or not self.listas:
            raise TransicionInvalida("Se requiere padrón cargado y al menos una lista")
        self.estado = EstadoEleccion.ABIERTA

    def esta_abierta(self, ahora: datetime) -> bool:
        return (
            self.estado is EstadoEleccion.ABIERTA
            and self.apertura is not None and self.cierre is not None
            and self.apertura <= ahora < self.cierre
        )

    def verificar_votable(self, ahora: datetime) -> None:
        """Lanza `EleccionNoAbierta` si no se puede votar en este instante."""
        if self.estado is not EstadoEleccion.ABIERTA:
            raise EleccionNoAbierta("La elección no está abierta")
        if not self.esta_abierta(ahora):
            raise EleccionNoAbierta("Fuera del horario de votación")

    def cerrar(self, ahora: datetime) -> None:
        self._exigir(EstadoEleccion.ABIERTA)
        if self.cierre is None or ahora < self.cierre:
            raise TransicionInvalida("Aún no se alcanza la hora de cierre")
        self.estado = EstadoEleccion.CERRADA

    def registrar_discrepancia(self) -> None:
        """CERRADA -> CERRADA: los recuentos difieren; la elección no avanza ni se publica el acta."""
        self._exigir(EstadoEleccion.CERRADA)
        self.discrepancias += 1

    def escrutar(self, votos: int, participaciones: int, auditor_coincide: bool) -> None:
        self._exigir(EstadoEleccion.CERRADA)
        if votos != participaciones or not auditor_coincide:
            raise TransicionInvalida("El recuento oficial y el del auditor deben coincidir")
        self.estado = EstadoEleccion.ESCRUTADA

    def publicar(self, acta_firmada: bool) -> None:
        self._exigir(EstadoEleccion.ESCRUTADA)
        if not acta_firmada:
            raise TransicionInvalida("El acta debe estar firmada")
        self.estado = EstadoEleccion.PUBLICADA

    def _exigir(self, esperado: EstadoEleccion) -> None:
        if self.estado is not esperado:
            raise TransicionInvalida(f"Estado {self.estado.value}; se esperaba {esperado.value}")


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
