"""VERSIÓN DESPUÉS (E2): puertos y adaptadores, estrategia de canal y fábrica.

Quedan pendientes los reintentos y la notificación en línea (E4) y el asistente de IA (E5).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .canales import CorreoAdapter, FabricaCanales
from .dominio import ErrorTransitorio, Identificador, Participacion, Voto
from .repositorio import RepositorioAdapter

MAX_INTENTOS = 3


class ServicioVotacion:
    def __init__(self, repositorio: Any, notificador: Any, alfa: Any = None, beta: Any = None,
                 fabrica: FabricaCanales | None = None, canal: str = "CORREO"):
        self.eventos: list[str] = []
        self.fabrica = fabrica or FabricaCanales()
        self.fabrica.registrar("CORREO", lambda: CorreoAdapter(notificador))
        self._canal = self.fabrica.crear(canal)          # el canal se valida ANTES de operar
        self._repositorio = RepositorioAdapter(repositorio)

    def emitir_voto(self, estudiante_id: Identificador, eleccion_id: Identificador,
                    lista_id: Identificador, ahora: datetime) -> dict:
        eleccion = self._repositorio.buscar_eleccion(eleccion_id)
        eleccion.verificar_votable(ahora)
        lista = self._repositorio.buscar_lista(lista_id, eleccion_id)
        estudiante = self._repositorio.buscar_estudiante(estudiante_id)
        participacion = Participacion(estudiante, eleccion, ahora)
        voto = Voto(eleccion, lista)

        for intento in range(1, MAX_INTENTOS + 1):
            try:
                self._repositorio.registrar(participacion, voto)
                break
            except ErrorTransitorio:
                if intento == MAX_INTENTOS:
                    raise

        comprobante = participacion.emitir_comprobante()
        try:
            self._canal.enviar_comprobante(estudiante.correo_institucional, comprobante)
        except Exception:
            self.eventos.append("notificacion_fallida")
        self.eventos.append("voto_registrado")
        return {"codigo": comprobante.codigo, "fecha": comprobante.fecha_hora}
