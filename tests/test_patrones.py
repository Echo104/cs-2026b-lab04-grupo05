"""Pruebas que demuestran cada patrón: solo son posibles (o fáciles) gracias a ellos."""
from datetime import datetime

import pytest

from src.votacion.canales import CorreoAdapter, FabricaCanales
from src.votacion.dominio import CanalComprobante, Comprobante
from src.votacion.externos import CorreoEnMemoria, RepositorioEnMemoria
from src.votacion.servicio import ServicioVotacion

AHORA = datetime(2026, 10, 20, 12, 0)


class BandejaInterna(CanalComprobante):
    """Canal nuevo (hipotético): se agrega SIN modificar el servicio."""

    def __init__(self):
        self.recibidos = []

    def enviar_comprobante(self, correo, comprobante):
        self.recibidos.append((correo, comprobante.codigo))


# ---------- E2: Strategy + Adapter + Factory ----------
def test_open_closed_nuevo_canal_sin_modificar_el_servicio():
    bandeja, correo = BandejaInterna(), CorreoEnMemoria()
    fabrica = FabricaCanales()
    fabrica.registrar("BANDEJA", lambda: bandeja)                    # extensión, no modificación
    servicio = ServicioVotacion(RepositorioEnMemoria(), correo, fabrica=fabrica, canal="BANDEJA")
    comprobante = servicio.emitir_voto("estudiante-1", "eleccion-1", "lista-1", AHORA)
    assert bandeja.recibidos == [("alumno@unsa.edu.pe", comprobante["codigo"])]
    assert correo.enviados == []                                     # el canal por defecto no se usó


def test_adapter_traduce_el_comprobante_a_la_interfaz_del_correo_externo():
    correo = CorreoEnMemoria()
    CorreoAdapter(correo).enviar_comprobante("a@unsa.edu.pe", Comprobante("ABC123", AHORA))
    assert correo.enviados == [("a@unsa.edu.pe", {"codigo": "ABC123", "fecha": AHORA})]


def test_factory_rechaza_un_canal_no_soportado_antes_de_operar():
    repo = RepositorioEnMemoria()
    with pytest.raises(ValueError, match="Canal de comprobante no soportado"):
        ServicioVotacion(repo, CorreoEnMemoria(), canal="SMS")
    assert repo.registros == [] and repo.llamadas_registrar == 0


def test_adapter_del_repositorio_conserva_los_objetos_externos_y_oculta_al_estudiante():
    repo = RepositorioEnMemoria()
    ServicioVotacion(repo, CorreoEnMemoria()).emitir_voto("estudiante-1", "eleccion-1", "lista-1", AHORA)
    participacion, voto = repo.registros[0]
    assert voto["lista"] is repo.lista and participacion["estudiante"] is repo.estudiante
    assert set(voto) == {"eleccion", "lista"}
