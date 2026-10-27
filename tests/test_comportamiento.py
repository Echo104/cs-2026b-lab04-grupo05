from datetime import datetime

import importlib
import pytest

@pytest.fixture(params=["src.votacion.antes.servicio"])
def m(request):
    return importlib.import_module(request.param)


@pytest.fixture
def entorno():
    from src.votacion.externos import CorreoEnMemoria, RepositorioEnMemoria
    return RepositorioEnMemoria(), CorreoEnMemoria()


AHORA = datetime(2026, 10, 20, 12, 0)


def emitir(m, repo, correo, *, estudiante="estudiante-1",
           eleccion="eleccion-1", lista="lista-1", ahora=AHORA):
    return m.ServicioAntes(repo, correo).emitir(estudiante, eleccion, lista, ahora)


def test_voto_exitoso_guarda_y_devuelve_comprobante(m, entorno):
    repo, correo = entorno
    comprobante = emitir(m, repo, correo)
    assert comprobante == {"codigo": "TEST-0001", "fecha": AHORA}
    assert len(repo.registros) == 1
    assert len(correo.enviados) == 1
    assert repo.registros[0][1]["lista"] is repo.lista


@pytest.mark.parametrize(("fallas", "llamadas"), [(0, 1), (1, 2), (2, 3)])
def test_reintenta_fallas_transitorias_y_finalmente_registra(m, fallas, llamadas):
    from src.votacion.externos import CorreoEnMemoria, RepositorioEnMemoria
    repo, correo = RepositorioEnMemoria(fallas_transitorias=fallas), CorreoEnMemoria()
    emitir(m, repo, correo)
    assert repo.llamadas_registrar == llamadas
    assert len(repo.registros) == 1


def test_agotar_tres_intentos_propaga_timeout(m):
    from src.votacion.externos import CorreoEnMemoria, RepositorioEnMemoria
    repo = RepositorioEnMemoria(fallas_transitorias=3)
    with pytest.raises(TimeoutError, match="agotado"):
        emitir(m, repo, CorreoEnMemoria())
    assert repo.llamadas_registrar == 3
    assert repo.registros == []


def test_eleccion_cerrada_rechaza_antes_de_registrar(m, entorno):
    repo, correo = entorno
    repo.eleccion.estado = "CERRADA"
    with pytest.raises(ValueError, match="no está abierta"):
        emitir(m, repo, correo)
    assert repo.registros == []


@pytest.mark.parametrize("ahora", [
    datetime(2025, 12, 31, 23, 59, 59),
    datetime(2027, 1, 1, 0, 0, 0),
])
def test_limites_de_horario_se_rechazan(m, entorno, ahora):
    repo, correo = entorno
    with pytest.raises(ValueError, match="horario"):
        emitir(m, repo, correo, ahora=ahora)
    assert repo.registros == []


def test_instante_de_apertura_se_acepta(m, entorno):
    repo, correo = entorno
    emitir(m, repo, correo, ahora=repo.eleccion.apertura)
    assert len(repo.registros) == 1


def test_lista_ajena_o_inexistente_se_rechaza(m, entorno):
    repo, correo = entorno
    with pytest.raises(LookupError, match="lista"):
        emitir(m, repo, correo, lista="lista-ajena")
    assert repo.registros == []


def test_estudiante_inexistente_se_rechaza(m, entorno):
    repo, correo = entorno
    with pytest.raises(LookupError, match="Estudiante"):
        emitir(m, repo, correo, estudiante="desconocido")
    assert repo.registros == []


def test_fallo_de_correo_no_revierte_voto_registrado(m, entorno):
    repo, correo = entorno
    correo.fallar = True
    servicio = m.ServicioAntes(repo, correo)
    comprobante = servicio.emitir("estudiante-1", "eleccion-1", "lista-1", AHORA)
    assert len(repo.registros) == 1
    assert comprobante["codigo"] == "TEST-0001"
    assert "notificacion_fallida" in servicio.eventos
    assert "voto_registrado" in servicio.eventos


def test_segundo_voto_del_mismo_estudiante_se_rechaza(m, entorno):
    repo, correo = entorno
    emitir(m, repo, correo)
    with pytest.raises(ValueError, match="duplicada"):
        emitir(m, repo, correo)
    assert len(repo.registros) == 1


def test_voto_no_guarda_identidad_del_estudiante(m, entorno):
    repo, correo = entorno
    emitir(m, repo, correo)
    _, voto = repo.registros[0]
    assert "estudiante" not in voto
    assert "lista" in voto and "eleccion" in voto
