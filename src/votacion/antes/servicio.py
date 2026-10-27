from __future__ import annotations

from datetime import datetime
from typing import Any

MAX_INTENTOS = 3


class ServicioAntes:
    def __init__(self, repositorio: Any, notificador: Any):
        self.repositorio = repositorio
        self.notificador = notificador
        self.eventos: list[str] = []

    def emitir(self, estudiante_id: str, eleccion_id: str, lista_id: str,
               ahora: datetime) -> dict:
        eleccion = self.repositorio.buscar_eleccion(eleccion_id)
        if eleccion.estado != "ABIERTA":
            raise ValueError("La elección no está abierta")
        if ahora < eleccion.apertura or ahora >= eleccion.cierre:
            raise ValueError("Fuera del horario de votación")

        lista = self.repositorio.buscar_lista(lista_id, eleccion_id)
        estudiante = self.repositorio.buscar_estudiante(estudiante_id)
        participacion = {
            "estudiante": estudiante,
            "eleccion": eleccion,
            "fecha": ahora,
        }
        # El voto solo guarda elección y lista: no incluye identidad del elector.
        voto = {"eleccion": eleccion, "lista": lista}

        for intento in range(1, MAX_INTENTOS + 1):
            try:
                self.repositorio.registrar(participacion, voto)
                break
            except TimeoutError:
                if intento == MAX_INTENTOS:
                    raise

        comprobante = {"codigo": "TEST-0001", "fecha": ahora}
        try:
            self.notificador.enviar_comprobante(
                estudiante.correo_institucional, comprobante
            )
        except Exception:
            # El voto ya fue registrado: una caída del correo no lo revierte.
            self.eventos.append("notificacion_fallida")

        self.eventos.append("voto_registrado")
        return comprobante
