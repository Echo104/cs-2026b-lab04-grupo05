"""ADAPTER del repositorio externo y DECORATOR de reintentos."""
from __future__ import annotations

from .dominio import (Eleccion, ErrorTransitorio, Estudiante, Identificador, Lista,
                      Participacion, ParticipacionDuplicada, RepositorioVotacion, Voto)
from .externos import ErrorParticipacionDuplicada, RepositorioExterno


class RepositorioAdapter(RepositorioVotacion):
    """Convierte lo que devuelve el repositorio externo (objetos y diccionarios) en
    objetos del dominio, y los errores del proveedor en errores del dominio."""

    def __init__(self, externo: RepositorioExterno):
        self._externo = externo
        # id(objeto de dominio) -> (objeto de dominio, objeto externo del que proviene)
        self._origen: dict[int, tuple[object, object]] = {}

    def _traducido(self, dominio, externo):
        self._origen[id(dominio)] = (dominio, externo)
        return dominio

    def _externo_de(self, dominio):
        return self._origen[id(dominio)][1]

    def buscar_eleccion(self, id: Identificador) -> Eleccion:
        ext = self._externo.buscar_eleccion(id)
        return self._traducido(
            Eleccion.reconstruir(ext.estado, id=ext.id, apertura=ext.apertura, cierre=ext.cierre), ext)

    def buscar_lista(self, id: Identificador, eleccion_id: Identificador) -> Lista:
        ext = self._externo.buscar_lista(id, eleccion_id)
        return self._traducido(Lista(nombre=ext.nombre, id=ext.id), ext)

    def buscar_estudiante(self, id: Identificador) -> Estudiante:
        ext = self._externo.buscar_estudiante(id)
        return self._traducido(Estudiante(ext.correo_institucional, id=ext.id), ext)

    def registrar(self, participacion: Participacion, voto: Voto) -> None:
        # El voto solo lleva elección y lista: nunca la identidad del estudiante.
        try:
            self._externo.registrar(
                {"estudiante": self._externo_de(participacion.estudiante),
                 "eleccion": self._externo_de(participacion.eleccion),
                 "fecha": participacion.fecha_hora},
                {"eleccion": self._externo_de(voto.eleccion),
                 "lista": self._externo_de(voto.lista)})
        except TimeoutError as error:
            raise ErrorTransitorio(str(error)) from error
        except ErrorParticipacionDuplicada as error:
            raise ParticipacionDuplicada(str(error)) from error


class RepositorioConReintentos(RepositorioVotacion):
    """DECORATOR: agrega reintentos a `registrar` sin modificar el repositorio envuelto.

    Solo se reintenta ante `ErrorTransitorio`: reintentar un duplicado o un error de negocio
    podría registrar dos veces o ocultar una falla real."""

    def __init__(self, interno: RepositorioVotacion, intentos: int = 3):
        self._interno, self._intentos = interno, intentos

    def buscar_eleccion(self, id):
        return self._interno.buscar_eleccion(id)

    def buscar_lista(self, id, eleccion_id):
        return self._interno.buscar_lista(id, eleccion_id)

    def buscar_estudiante(self, id):
        return self._interno.buscar_estudiante(id)

    def registrar(self, participacion: Participacion, voto: Voto) -> None:
        for intento in range(1, self._intentos + 1):
            try:
                return self._interno.registrar(participacion, voto)
            except ErrorTransitorio:
                if intento == self._intentos:
                    raise
