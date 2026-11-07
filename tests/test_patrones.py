"""Pruebas que demuestran cada patrón: solo son posibles (o fáciles) gracias a ellos."""
from datetime import datetime

import pytest

from src.votacion.canales import CorreoAdapter, FabricaCanales
from src.votacion.dominio import (CanalComprobante, Comprobante, Eleccion, EstadoEleccion,
                                  Lista)
from src.votacion.estados import (Abierta, Cerrada, Configurada, Escrutada, Publicada,
                                  etapa_desde_nombre)
from src.votacion.excepciones import EleccionNoAbierta, TransicionInvalida
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


# ---------- E3: State ----------
APERTURA, CIERRE = datetime(2026, 10, 20, 8, 0), datetime(2026, 10, 20, 18, 0)


def eleccion_en(etapa):
    e = Eleccion.reconstruir(etapa, apertura=APERTURA, cierre=CIERRE, total_padron=10)
    e.listas.append(Lista("Lista 1"))
    return e


def test_state_recorrido_completo_de_la_maquina_de_estados():
    e = Eleccion()
    e.configurar("Delegados EPIS", APERTURA, CIERRE, total_padron=10)    # [*] -> CONFIGURADA
    e.agregar_lista(Lista("Lista 1"))                                   # CONFIGURADA -> CONFIGURADA
    e.abrir()
    assert e.estado is EstadoEleccion.ABIERTA
    e.cerrar(CIERRE)
    assert e.estado is EstadoEleccion.CERRADA
    e.registrar_discrepancia()                                          # CERRADA -> CERRADA
    assert e.estado is EstadoEleccion.CERRADA and e.discrepancias == 1
    e.escrutar(5, 5, auditor_coincide=True)
    assert e.estado is EstadoEleccion.ESCRUTADA
    e.publicar(acta_firmada=True)
    assert e.estado is EstadoEleccion.PUBLICADA


@pytest.mark.parametrize(("etapa", "operacion"), [
    ("CONFIGURADA", lambda e: e.cerrar(CIERRE)),
    ("CONFIGURADA", lambda e: e.escrutar(1, 1, True)),
    ("ABIERTA", lambda e: e.abrir()),
    ("ABIERTA", lambda e: e.agregar_lista(Lista("Tarde"))),
    ("CERRADA", lambda e: e.publicar(True)),
    ("ESCRUTADA", lambda e: e.registrar_discrepancia()),
    ("PUBLICADA", lambda e: e.abrir()),
    ("PUBLICADA", lambda e: e.publicar(True)),
])
def test_state_impide_transiciones_invalidas(etapa, operacion):
    e = eleccion_en(etapa)
    with pytest.raises(TransicionInvalida):
        operacion(e)
    assert e.estado is EstadoEleccion(etapa)                            # el estado no cambió


@pytest.mark.parametrize(("etapa", "operacion", "mensaje"), [
    ("CONFIGURADA", lambda e: setattr(e, "total_padron", 0) or e.abrir(), "padrón"),
    ("CONFIGURADA", lambda e: setattr(e, "listas", []) or e.abrir(), "lista"),
    ("ABIERTA", lambda e: e.cerrar(CIERRE - (CIERRE - APERTURA) / 2), "hora de cierre"),
    ("CERRADA", lambda e: e.escrutar(5, 4, True), "deben coincidir"),
    ("CERRADA", lambda e: e.escrutar(5, 5, False), "deben coincidir"),
    ("ESCRUTADA", lambda e: e.publicar(False), "acta"),
])
def test_state_las_guardas_impiden_avanzar_de_etapa(etapa, operacion, mensaje):
    e = eleccion_en(etapa)
    with pytest.raises(TransicionInvalida, match=mensaje):
        operacion(e)
    assert e.estado is EstadoEleccion(etapa)


def test_state_solo_la_etapa_abierta_acepta_votos():
    dentro = datetime(2026, 10, 20, 12, 0)
    assert eleccion_en("ABIERTA").esta_abierta(dentro)
    for etapa in ("CONFIGURADA", "CERRADA", "ESCRUTADA", "PUBLICADA"):
        e = eleccion_en(etapa)
        assert not e.esta_abierta(dentro)
        with pytest.raises(EleccionNoAbierta, match="no está abierta"):
            e.verificar_votable(dentro)
    with pytest.raises(EleccionNoAbierta, match="horario"):
        eleccion_en("ABIERTA").verificar_votable(CIERRE)


def test_state_factory_crea_la_etapa_por_nombre_y_rechaza_desconocidas():
    assert [type(etapa_desde_nombre(n)) for n in ("CONFIGURADA", "ABIERTA", "CERRADA", "ESCRUTADA", "PUBLICADA")] == \
        [Configurada, Abierta, Cerrada, Escrutada, Publicada]
    with pytest.raises(ValueError, match="desconocido"):
        etapa_desde_nombre("ANULADA")
