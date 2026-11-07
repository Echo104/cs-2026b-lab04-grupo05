"""VERSIÓN DESPUÉS (E4): adaptadores + strategy/factory + observer + decorator de reintentos.

Pendiente: el asistente de IA aislado (E5).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .canales import CorreoAdapter, FabricaCanales
from .dominio import Identificador, Participacion, Voto
from .eventos import NotificadorComprobante, PublicadorEventos, RegistroEventos
from .repositorio import RepositorioAdapter, RepositorioConReintentos

MAX_INTENTOS = 3


class ServicioVotacion:
    def __init__(self, repositorio: Any, notificador: Any, alfa: Any = None, beta: Any = None,
                 fabrica: FabricaCanales | None = None, canal: str = "CORREO"):
        self.eventos: list[str] = []
        self.fabrica = fabrica or FabricaCanales()
        self.fabrica.registrar("CORREO", lambda: CorreoAdapter(notificador))
        canal_comprobante = self.fabrica.crear(canal)    # el canal se valida ANTES de operar
        self._repositorio = RepositorioConReintentos(RepositorioAdapter(repositorio), MAX_INTENTOS)

        self.publicador = PublicadorEventos()
        self.publicador.suscribir("voto_registrado", NotificadorComprobante(canal_comprobante, self.publicador))
        self.publicador.suscribir("voto_registrado", RegistroEventos(self.eventos))
        self.publicador.suscribir("notificacion_fallida", RegistroEventos(self.eventos))

    def emitir_voto(self, estudiante_id: Identificador, eleccion_id: Identificador,
                    lista_id: Identificador, ahora: datetime) -> dict:
        eleccion = self._repositorio.buscar_eleccion(eleccion_id)
        eleccion.verificar_votable(ahora)
        lista = self._repositorio.buscar_lista(lista_id, eleccion_id)
        estudiante = self._repositorio.buscar_estudiante(estudiante_id)
        participacion = Participacion(estudiante, eleccion, ahora)

        self._repositorio.registrar(participacion, Voto(eleccion, lista))

        comprobante = participacion.emitir_comprobante()
        self.publicador.publicar("voto_registrado", {
            "correo": estudiante.correo_institucional,
            "comprobante": comprobante,
            "eleccion_id": eleccion.id,        # sin lista ni otros datos que revelen el voto
        })
        return {"codigo": comprobante.codigo, "fecha": comprobante.fecha_hora}
