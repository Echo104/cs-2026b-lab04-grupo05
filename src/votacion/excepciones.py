"""Errores del dominio. Heredan de ValueError/TimeoutError para conservar el comportamiento
observable de la versión ingenua (que lanzaba ValueError y TimeoutError)."""


class TransicionInvalida(ValueError):
    """La operación no está permitida en la etapa actual o no cumple su guarda."""


class EleccionNoAbierta(ValueError):
    """Se intentó votar con la elección fuera de su ventana de votación."""


class ParticipacionDuplicada(ValueError):
    """El estudiante ya participó en la elección (restricción UNIQUE del padrón)."""


class ErrorTransitorio(TimeoutError):
    """Fallo temporal de la base de datos; el registro puede reintentarse."""
