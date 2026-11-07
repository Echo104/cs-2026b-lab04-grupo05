"""Caracterización del asistente de reglamento (IA simulada; no se usa red ni claves).

La IA solo responde preguntas sobre el reglamento y NO participa en el conteo de votos.
Se ejecutan sobre la versión `antes` y sobre la versión `despues`.
"""
import importlib

import pytest

from src.votacion.externos import (ClienteLLMFalso, CorreoEnMemoria, ModeloLocalFalso,
                                   RepositorioEnMemoria)

VERSIONES = ["src.votacion.antes.servicio", "src.votacion.servicio"]


@pytest.fixture(params=VERSIONES)
def m(request):
    return importlib.import_module(request.param)


def servicio(m, alfa=None, beta=None):
    return m.ServicioVotacion(RepositorioEnMemoria(), CorreoEnMemoria(), alfa=alfa, beta=beta)


def test_respuesta_valida_del_proveedor_alfa(m):
    texto = servicio(m).consultar_reglamento("¿El voto es secreto?")
    assert "secreto" in texto and len(texto) <= 240


def test_respuesta_valida_del_proveedor_beta(m):
    beta = ModeloLocalFalso()
    texto = servicio(m, beta=beta).consultar_reglamento("¿Quién vota?", proveedor="BETA")
    assert "padrón" in texto and beta.llamadas == 1


def test_bloquea_resultados_parciales(m):
    alfa = ClienteLLMFalso("Según el resultado parcial, la Lista 1 va ganando.")
    with pytest.raises(ValueError, match="no permitida"):
        servicio(m, alfa=alfa).consultar_reglamento("¿Quién gana?")


def test_bloquea_datos_personales(m):
    alfa = ClienteLLMFalso("Escriba a alumno@unsa.edu.pe para consultar.")
    with pytest.raises(ValueError, match="datos personales"):
        servicio(m, alfa=alfa).consultar_reglamento("¿Cómo reclamo?")


def test_trunca_respuestas_largas(m):
    alfa = ClienteLLMFalso("x" * 500)
    texto = servicio(m, alfa=alfa).consultar_reglamento("Explique el reglamento")
    assert len(texto) == 240 and texto.endswith("...")


def test_proveedor_no_soportado(m):
    with pytest.raises(ValueError, match="Proveedor"):
        servicio(m).consultar_reglamento("¿Hola?", proveedor="GAMMA")


def test_la_ia_no_participa_en_el_conteo(m):
    repo = RepositorioEnMemoria()
    s = m.ServicioVotacion(repo, CorreoEnMemoria())
    s.consultar_reglamento("¿El voto es secreto?")
    assert repo.registros == [] and repo.llamadas_registrar == 0
