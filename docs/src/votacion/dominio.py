"""Esqueleto del módulo Votación de VotoEPIS (E6), generado con IA desde docs/design/clases.puml.

Los nombres usan snake_case (equivalencia con el camelCase del diagrama, regla C5).
"""
from __future__ import annotations

import logging
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable
from uuid import UUID, uuid4

MAX_INTENTOS = 3
log = logging.getLogger(__name__)


class EstadoEleccion(Enum):
    CONFIGURADA = "CONFIGURADA"
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"
    ESCRUTADA = "ESCRUTADA"
    PUBLICADA = "PUBLICADA"


class TransicionInvalida(Exception):
    """La operación no está permitida en el estado actual o no cumple su guarda."""


class EleccionNoAbierta(Exception):
    """Se intentó votar con la elección fuera de su ventana de votación."""


class ParticipacionDuplicada(Exception):
    """El estudiante ya participó en la elección (restricción UNIQUE del padrón)."""


class ErrorTransitorio(Exception):
    """Fallo temporal de la base de datos; el registro puede reintentarse."""


@dataclass
class Estudiante:
    correo_institucional: str
    id: UUID = field(default_factory=uuid4)


@dataclass
class Lista:
    nombre: str
    id: UUID = field(default_factory=uuid4)


@dataclass
class Eleccion:
    nombre: str = ""
    apertura: datetime | None = None
    cierre: datetime | None = None
    total_padron: int = 0
    estado: EstadoEleccion = EstadoEleccion.CONFIGURADA
    listas: list[Lista] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

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

    def cerrar(self, ahora: datetime) -> None:
        self._exigir(EstadoEleccion.ABIERTA)
        if self.cierre is None or ahora < self.cierre:
            raise TransicionInvalida("Aún no se alcanza la hora de cierre")
        self.estado = EstadoEleccion.CERRADA

    def escrutar(self, votos: int, participaciones: int) -> None:
        self._exigir(EstadoEleccion.CERRADA)
        if votos != participaciones:
            raise TransicionInvalida("Los votos de la urna no coinciden con las participaciones")
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
    id: UUID = field(default_factory=uuid4)


class NotificadorCorreo(ABC):  # puerto
    @abstractmethod
    def enviar_comprobante(self, correo: str, comprobante: Comprobante) -> None: ...


class RepositorioVotacion(ABC):  # puerto
    @abstractmethod
    def buscar_eleccion(self, id: UUID) -> Eleccion: ...

    @abstractmethod
    def buscar_lista(self, id: UUID, eleccion_id: UUID) -> Lista: ...

    @abstractmethod
    def buscar_estudiante(self, id: UUID) -> Estudiante: ...

    @abstractmethod
    def registrar(self, participacion: Participacion, voto: Voto) -> None:
        """Una sola transacción: padron.participacion (UNIQUE) + urna.voto."""


class SmtpAdapter(NotificadorCorreo):  # adaptador
    def enviar_comprobante(self, correo: str, comprobante: Comprobante) -> None:
        raise NotImplementedError("Integrar con el servidor de correo (SMTP)")


class PostgresRepositorioVotacion(RepositorioVotacion):  # adaptador
    def buscar_eleccion(self, id: UUID) -> Eleccion:
        raise NotImplementedError("Integrar con PostgreSQL")

    def buscar_lista(self, id: UUID, eleccion_id: UUID) -> Lista:
        raise NotImplementedError("Integrar con PostgreSQL")

    def buscar_estudiante(self, id: UUID) -> Estudiante:
        raise NotImplementedError("Integrar con PostgreSQL")

    def registrar(self, participacion: Participacion, voto: Voto) -> None:
        raise NotImplementedError("Integrar con PostgreSQL")


class ServicioVotacion:  # servicio de aplicación
    def __init__(self, repositorio: RepositorioVotacion, notificador: NotificadorCorreo,
                 reloj: Callable[[], datetime] = datetime.now) -> None:
        self._repositorio = repositorio
        self._notificador = notificador
        self._reloj = reloj

    def emitir_voto(self, estudiante_id: UUID, eleccion_id: UUID, lista_id: UUID) -> Comprobante:
        eleccion = self._repositorio.buscar_eleccion(eleccion_id)
        ahora = self._reloj()
        if not eleccion.esta_abierta(ahora):
            raise EleccionNoAbierta("La elección no está abierta")
        lista = self._repositorio.buscar_lista(lista_id, eleccion_id)
        estudiante = self._repositorio.buscar_estudiante(estudiante_id)
        participacion = Participacion(estudiante, eleccion, ahora)
        voto = Voto(eleccion, lista)
        self._registrar_con_reintentos(participacion, voto)
        comprobante = participacion.emitir_comprobante()
        self._notificar(estudiante.correo_institucional, comprobante)
        return comprobante

    def _registrar_con_reintentos(self, participacion: Participacion, voto: Voto) -> None:
        for intento in range(1, MAX_INTENTOS + 1):
            try:
                self._repositorio.registrar(participacion, voto)
                return
            except ErrorTransitorio:
                if intento == MAX_INTENTOS:
                    raise

    def _notificar(self, correo: str, comprobante: Comprobante) -> None:
        # En producción se encola como tarea asíncrona; aquí es "mejor esfuerzo" y no bloquea el voto.
        try:
            self._notificador.enviar_comprobante(correo, comprobante)
        except Exception:  # noqa: BLE001 - el voto ya está registrado
            log.warning("No se pudo enviar el comprobante", exc_info=True)
