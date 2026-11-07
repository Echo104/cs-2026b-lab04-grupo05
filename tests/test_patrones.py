"""Pruebas que demuestran cada patrón: solo son posibles (o fáciles) gracias a ellos."""
from datetime import datetime

import pytest

from src.votacion.canales import CorreoAdapter, FabricaCanales
from src.votacion.dominio import (CanalComprobante, Comprobante, Eleccion, EstadoEleccion,
                                  Lista, Participacion, Voto)
from src.votacion.estados import (Abierta, Cerrada, Configurada, Escrutada, Publicada,
                                  etapa_desde_nombre)
from src.votacion.eventos import PublicadorEventos, Suscriptor
from src.votacion.excepciones import (EleccionNoAbierta, ErrorTransitorio, ParticipacionDuplicada,
                                       TransicionInvalida)
from src.votacion.repositorio import RepositorioAdapter, RepositorioConReintentos
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


# ---------- E4: Observer ----------
class Espia(Suscriptor):
    def __init__(self):
        self.recibidos = []

    def actualizar(self, evento, datos):
        self.recibidos.append((evento, dict(datos)))


class Defectuoso(Suscriptor):
    def actualizar(self, evento, datos):
        raise RuntimeError("suscriptor roto")


def test_observer_nuevo_suscriptor_sin_tocar_el_servicio():
    servicio = ServicioVotacion(RepositorioEnMemoria(), CorreoEnMemoria())
    espia = Espia()
    servicio.publicador.suscribir("voto_registrado", espia)             # solo suscribir
    servicio.emitir_voto("estudiante-1", "eleccion-1", "lista-1", AHORA)
    assert [evento for evento, _ in espia.recibidos] == ["voto_registrado"]


def test_observer_los_eventos_no_revelan_la_lista_elegida():
    servicio = ServicioVotacion(RepositorioEnMemoria(), CorreoEnMemoria())
    espia = Espia()
    servicio.publicador.suscribir("voto_registrado", espia)
    servicio.emitir_voto("estudiante-1", "eleccion-1", "lista-1", AHORA)
    datos = espia.recibidos[0][1]
    assert set(datos) == {"correo", "comprobante", "eleccion_id"}
    assert "lista-1" not in repr(datos) and "Lista 1" not in repr(datos)


def test_observer_un_suscriptor_defectuoso_no_anula_el_voto_ni_a_los_demas():
    repo = RepositorioEnMemoria()
    servicio = ServicioVotacion(repo, CorreoEnMemoria())
    espia = Espia()
    servicio.publicador.suscribir("voto_registrado", Defectuoso())
    servicio.publicador.suscribir("voto_registrado", espia)
    servicio.emitir_voto("estudiante-1", "eleccion-1", "lista-1", AHORA)
    assert len(repo.registros) == 1 and len(espia.recibidos) == 1
    assert servicio.publicador.fallos == [("voto_registrado", "Defectuoso", "suscriptor roto")]


def test_observer_publicar_sin_suscriptores_no_hace_nada():
    PublicadorEventos().publicar("evento_sin_nadie", {})


# ---------- E4: Decorator ----------
@pytest.mark.parametrize(("fallas", "llamadas"), [(0, 1), (2, 3)])
def test_decorator_reintenta_solo_ante_errores_transitorios(fallas, llamadas):
    externo = RepositorioEnMemoria(fallas_transitorias=fallas)
    servicio = ServicioVotacion(externo, CorreoEnMemoria())
    servicio.emitir_voto("estudiante-1", "eleccion-1", "lista-1", AHORA)
    assert externo.llamadas_registrar == llamadas


def test_decorator_se_agota_tras_los_intentos_configurados():
    externo = RepositorioEnMemoria(fallas_transitorias=10)
    repo = RepositorioConReintentos(RepositorioAdapter(externo), intentos=2)
    eleccion = repo.buscar_eleccion("eleccion-1")
    participacion = _participacion(repo, eleccion)
    with pytest.raises(ErrorTransitorio):
        repo.registrar(participacion, _voto(repo, eleccion))
    assert externo.llamadas_registrar == 2


def test_decorator_no_reintenta_errores_de_negocio_como_el_duplicado():
    externo = RepositorioEnMemoria()
    servicio = ServicioVotacion(externo, CorreoEnMemoria())
    servicio.emitir_voto("estudiante-1", "eleccion-1", "lista-1", AHORA)
    with pytest.raises(ParticipacionDuplicada):
        servicio.emitir_voto("estudiante-1", "eleccion-1", "lista-1", AHORA)
    assert externo.llamadas_registrar == 2                              # 1 por cada intento de voto


def _participacion(repo, eleccion):
    return Participacion(repo.buscar_estudiante("estudiante-1"), eleccion, AHORA)


def _voto(repo, eleccion):
    return Voto(eleccion, repo.buscar_lista("lista-1", "eleccion-1"))
