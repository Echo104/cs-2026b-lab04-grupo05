"""Servicios externos SIMULADOS de VotoEPIS (no requieren red ni claves de API).

Representan dependencias de terceros: sus interfaces son deliberadamente distintas
entre sí, como ocurre en la realidad (repositorio, correo y dos modelos de lenguaje).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from types import SimpleNamespace
from typing import Any


class ErrorParticipacionDuplicada(ValueError):
    """Error que lanza la base de datos simulada ante una segunda participación."""


class RepositorioExterno(ABC):
    """Puerto de persistencia: acceso a elección, lista, estudiante y registro."""

    @abstractmethod
    def buscar_eleccion(self, eleccion_id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def buscar_lista(self, lista_id: str, eleccion_id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def buscar_estudiante(self, estudiante_id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def registrar(self, participacion: dict, voto: dict) -> None:
        raise NotImplementedError


class ServicioCorreoExterno(ABC):
    """Puerto de notificación: entrega un comprobante, no persiste votos."""

    @abstractmethod
    def enviar_comprobante(self, correo: str, comprobante: dict) -> None:
        raise NotImplementedError


@dataclass
class RepositorioEnMemoria(RepositorioExterno):
    """Simula una BD y permite inyectar fallas transitorias para probar reintentos."""

    fallas_transitorias: int = 0
    eleccion: Any = field(default_factory=lambda: SimpleNamespace(
        id="eleccion-1",
        estado="ABIERTA",
        apertura=datetime(2026, 1, 1),
        cierre=datetime(2027, 1, 1),
    ))
    lista: Any = field(default_factory=lambda: SimpleNamespace(id="lista-1", nombre="Lista 1"))
    estudiante: Any = field(default_factory=lambda: SimpleNamespace(
        id="estudiante-1", correo_institucional="alumno@unsa.edu.pe"
    ))
    llamadas_registrar: int = 0
    registros: list[tuple[dict, dict]] = field(default_factory=list)
    participaciones: set[tuple[str, str]] = field(default_factory=set)

    def buscar_eleccion(self, eleccion_id: str) -> Any:
        if eleccion_id != "eleccion-1":
            raise LookupError("Elección no encontrada")
        return self.eleccion

    def buscar_lista(self, lista_id: str, eleccion_id: str) -> Any:
        if eleccion_id != "eleccion-1" or lista_id != "lista-1":
            raise LookupError("La lista no pertenece a la elección")
        return self.lista

    def buscar_estudiante(self, estudiante_id: str) -> Any:
        if estudiante_id != "estudiante-1":
            raise LookupError("Estudiante no encontrado")
        return self.estudiante

    def registrar(self, participacion: dict, voto: dict) -> None:
        self.llamadas_registrar += 1
        if self.fallas_transitorias > 0:
            self.fallas_transitorias -= 1
            raise TimeoutError("Tiempo de espera agotado al registrar")
        clave = (participacion["estudiante"].id, participacion["eleccion"].id)
        if clave in self.participaciones:
            raise ErrorParticipacionDuplicada("Participación duplicada")
        self.participaciones.add(clave)
        self.registros.append((participacion, voto))


@dataclass
class CorreoEnMemoria(ServicioCorreoExterno):
    """Simula SMTP y permite provocar una falla de envío."""

    fallar: bool = False
    enviados: list[tuple[str, dict]] = field(default_factory=list)

    def enviar_comprobante(self, correo: str, comprobante: dict) -> None:
        if self.fallar:
            raise RuntimeError("Servicio SMTP no disponible")
        self.enviados.append((correo, comprobante))


class ClienteLLMFalso:
    """Simula un modelo de lenguaje alojado (interfaz `completar`)."""

    RESPUESTA_POR_DEFECTO = "El voto es personal, secreto y se emite una sola vez por elección (Art. 1)."

    def __init__(self, respuesta: str | None = None):
        self.respuesta = respuesta
        self.llamadas = 0

    def completar(self, prompt: str) -> str:
        self.llamadas += 1
        return self.respuesta if self.respuesta is not None else self.RESPUESTA_POR_DEFECTO


class ModeloLocalFalso:
    """Simula un modelo local con OTRA interfaz (`generate` devuelve un diccionario)."""

    def __init__(self, respuesta: str | None = None):
        self.respuesta = respuesta
        self.llamadas = 0

    def generate(self, model: str, text: str) -> dict:
        self.llamadas += 1
        texto = self.respuesta if self.respuesta is not None else (
            "Solo votan los estudiantes del padrón y el voto es secreto (Art. 2)."
        )
        return {"model": model, "response": texto}
