"""Flujo ingenuo de emisión de voto y asistente de reglamento (línea base de E1)."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from ..externos import ClienteLLMFalso, ModeloLocalFalso

MAX_INTENTOS = 3
# Texto simulado
REGLAMENTO = (
    "Art. 1. El voto es personal, secreto y se emite una sola vez por elección. "
    "Art. 2. Solo votan los estudiantes que figuran en el padrón. "
    "Art. 3. El conteo es automático y puede verificarse de forma independiente."
)
PROHIBIDAS = ["resultado parcial", "va ganando", "votó por"]


class ServicioVotacion:
    def __init__(self, repositorio: Any, notificador: Any, alfa: Any = None, beta: Any = None):
        self.repositorio = repositorio
        self.notificador = notificador
        self.alfa = alfa or ClienteLLMFalso()
        self.beta = beta or ModeloLocalFalso()
        self.eventos: list[str] = []

    def emitir_voto(self, estudiante_id: str, eleccion_id: str, lista_id: str,
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

        # Simplificación de la versión ingenua: el código del comprobante es fijo.
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

    def consultar_reglamento(self, pregunta: str, proveedor: str = "ALFA") -> str:
        prompt = f"Responde solo con base en el reglamento: {REGLAMENTO} Pregunta: {pregunta}"
        if proveedor == "ALFA":
            texto = self.alfa.completar(prompt)
        elif proveedor == "BETA":
            texto = self.beta.generate("modelo-local", prompt)["response"]
        else:
            raise ValueError(f"Proveedor no soportado: {proveedor}")
        if "@" in texto:
            raise ValueError("Guardrail: la IA incluyó datos personales")
        for frase in PROHIBIDAS:
            if frase in texto.lower():
                raise ValueError(f"Guardrail: afirmación no permitida '{frase}'")
        if len(texto) > 240:
            texto = texto[:237] + "..."
        return texto
