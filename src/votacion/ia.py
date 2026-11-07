"""Componente de IA aislado: STRATEGY + ADAPTER + DECORATOR (caché) + CHAIN OF RESPONSIBILITY.

El asistente solo responde preguntas sobre el reglamento. NO participa en el conteo de votos ni
recibe el repositorio: la salida del modelo es un dato no confiable y se valida en cadena.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

# Texto de ejemplo: reemplácelo por los artículos reales del reglamento electoral de la EPIS.
REGLAMENTO = (
    "Art. 1. El voto es personal, secreto y se emite una sola vez por elección. "
    "Art. 2. Solo votan los estudiantes que figuran en el padrón. "
    "Art. 3. El conteo es automático y puede verificarse de forma independiente."
)


class ProveedorLLM(ABC):
    """STRATEGY: interfaz común de todos los proveedores de modelos de lenguaje."""

    @abstractmethod
    def completar(self, prompt: str) -> str: ...


class AlfaAdapter(ProveedorLLM):
    """ADAPTER del modelo alojado (interfaz `completar`)."""

    def __init__(self, cliente):
        self._cliente = cliente

    def completar(self, prompt):
        return self._cliente.completar(prompt)


class LocalAdapter(ProveedorLLM):
    """ADAPTER del modelo local (interfaz `generate` que devuelve un diccionario)."""

    def __init__(self, modelo, nombre: str = "modelo-local"):
        self._modelo, self._nombre = modelo, nombre

    def completar(self, prompt):
        return self._modelo.generate(self._nombre, prompt)["response"]


class ConCache(ProveedorLLM):
    """DECORATOR: evita pagar dos veces por el mismo prompt."""

    def __init__(self, interno: ProveedorLLM):
        self._interno, self._cache = interno, {}

    def completar(self, prompt):
        if prompt not in self._cache:
            self._cache[prompt] = self._interno.completar(prompt)
        return self._cache[prompt]


class Guardrail(ABC):
    """CHAIN OF RESPONSIBILITY: cada eslabón valida y pasa el texto al siguiente."""

    def __init__(self, siguiente: Guardrail | None = None):
        self._siguiente = siguiente

    def validar(self, texto: str) -> str:
        texto = self._aplicar(texto)
        return self._siguiente.validar(texto) if self._siguiente else texto

    @abstractmethod
    def _aplicar(self, texto: str) -> str: ...


class SinDatosPersonales(Guardrail):
    def _aplicar(self, texto):
        if "@" in texto:
            raise ValueError("Guardrail: la IA incluyó datos personales")
        return texto


class SinAfirmacionesProhibidas(Guardrail):
    PROHIBIDAS = ["resultado parcial", "va ganando", "votó por"]

    def _aplicar(self, texto):
        for frase in self.PROHIBIDAS:
            if frase in texto.lower():
                raise ValueError(f"Guardrail: afirmación no permitida '{frase}'")
        return texto


class LongitudMaxima(Guardrail):
    def __init__(self, maximo: int = 240, siguiente: Guardrail | None = None):
        super().__init__(siguiente)
        self._maximo = maximo

    def _aplicar(self, texto):
        return texto if len(texto) <= self._maximo else texto[: self._maximo - 3] + "..."


class AsistenteReglamento:
    def __init__(self, proveedores: dict[str, ProveedorLLM], guardrails: Guardrail):
        self.proveedores = proveedores
        self._guardrails = guardrails

    def consultar(self, pregunta: str, proveedor: str = "ALFA") -> str:
        if proveedor not in self.proveedores:
            raise ValueError(f"Proveedor no soportado: {proveedor}")
        prompt = f"Responde solo con base en el reglamento: {REGLAMENTO} Pregunta: {pregunta}"
        return self._guardrails.validar(self.proveedores[proveedor].completar(prompt))
