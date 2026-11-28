"""El «cerebro» intercambiable del agente (STRATEGY, como el proveedor de LLM del Lab 07)."""
from __future__ import annotations

import json
import pathlib
from abc import ABC, abstractmethod


class TrayectoriaAgotada(Exception):
    """El modelo grabado no tiene más decisiones."""


class Modelo(ABC):
    @abstractmethod
    def decidir(self, historial: list[dict]):
        """Devuelve la siguiente decisión (un dict, o texto si el modelo no siguió el protocolo)."""


class ModeloGrabado(Modelo):
    """Reproduce una trayectoria ya grabada (clase, pruebas, integración continua)."""

    def __init__(self, decisiones: list):
        self._decisiones, self._i = list(decisiones), 0

    @classmethod
    def desde_archivo(cls, ruta) -> "ModeloGrabado":
        return cls(json.loads(pathlib.Path(ruta).read_text(encoding="utf-8")))

    def decidir(self, historial):
        if self._i >= len(self._decisiones):
            raise TrayectoriaAgotada("la trayectoria grabada no tiene más decisiones")
        decision = self._decisiones[self._i]
        self._i += 1
        return decision


class ModeloInteractivo(Modelo):
    """Practicar sin clave de API: se copia el contexto al asistente y se pega su respuesta.

    Cada respuesta pegada se guarda TAL CUAL en ``archivo_trayectoria``; no se corrige a mano: si
    el asistente responde con texto libre o inventa una herramienta, el contrato lo rechaza.
    """

    def __init__(self, archivo_trayectoria, entrada=input, salida=print):
        self._archivo, self._entrada, self._salida = pathlib.Path(archivo_trayectoria), entrada, salida
        self._grabadas: list = []

    def decidir(self, historial):
        self._salida("\n" + "=" * 70 + "\nCOPIA ESTE CONTEXTO A TU ASISTENTE DE IA:\n" + "=" * 70)
        for mensaje in historial:
            self._salida(f"[{mensaje['role']}]\n{mensaje['content']}\n")
        self._salida("=" * 70 + "\nPEGA SU RESPUESTA y termina con una línea vacía:")
        lineas = []
        while True:
            linea = self._entrada()
            if linea.strip() == "" and lineas:
                break
            lineas.append(linea)
        texto = "\n".join(lineas).strip()
        try:
            decision = json.loads(texto)
        except json.JSONDecodeError:
            decision = texto                       # texto libre: lo rechazará el contrato
        self._grabadas.append(decision)
        self._archivo.parent.mkdir(parents=True, exist_ok=True)
        self._archivo.write_text(json.dumps(self._grabadas, ensure_ascii=False, indent=2), encoding="utf-8")
        return decision
