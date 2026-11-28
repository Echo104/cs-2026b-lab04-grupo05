"""Herramientas del agente: sandbox, edición segura, mapa del repositorio (ast) y memoria de notas."""
import pathlib
import tempfile

import pytest

from agente.herramientas import Herramientas

RAIZ_REPO = pathlib.Path(__file__).resolve().parents[2]

MODULO = '''"""Módulo de ejemplo para el mapa."""


class Padron:
    def __init__(self, correos):
        self.correos = correos

    def figura(self, correo: str) -> bool:
        return correo in self.correos


def contar(votos, blancos: bool = False):
    return len(votos)
'''


def repo_temporal(archivos: dict[str, str]):
    carpeta = tempfile.TemporaryDirectory()
    for ruta, texto in archivos.items():
        destino = pathlib.Path(carpeta.name) / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
    return carpeta, Herramientas(carpeta.name)


# ---------------------------------------------------------------- sandbox y edición
def test_las_rutas_fuera_del_sandbox_se_rechazan():
    carpeta, h = repo_temporal({"a.py": "x = 1\n"})
    with carpeta:
        for ruta in ("../secreto.txt", "/etc/passwd"):
            with pytest.raises(PermissionError):
                h.leer_archivo(ruta)
        with pytest.raises(PermissionError):
            h.mapa_repo("..")


def test_editar_exige_que_el_fragmento_aparezca_exactamente_una_vez():
    carpeta, h = repo_temporal({"a.py": "x = 1\nx = 1\ny = 2\n"})
    with carpeta:
        assert h.editar_archivo("a.py", "x = 1", "x = 3").startswith("ERROR: el fragmento aparece 2 veces")
        assert h.editar_archivo("a.py", "z = 9", "z = 0").startswith("ERROR: el fragmento aparece 0 veces")
        assert h.editar_archivo("a.py", "y = 2", "y = 5") == "OK: a.py modificado"
        assert "y = 5" in h.leer_archivo("a.py")


def test_ver_cambios_muestra_el_diff():
    carpeta, h = repo_temporal({"a.py": "x = 1\n"})
    with carpeta:
        assert h.ver_cambios() == "(sin cambios)"
        h.editar_archivo("a.py", "x = 1", "x = 2")
        diff = h.ver_cambios()
        assert "--- a/a.py" in diff and "-x = 1" in diff and "+x = 2" in diff


# ---------------------------------------------------------------- E4: mapa_repo
def test_mapa_repo_lista_clases_funciones_y_firmas():
    carpeta, h = repo_temporal({"src/votacion/padron.py": MODULO})
    with carpeta:
        mapa = h.mapa_repo("src")
        assert "src/votacion/padron.py  — Módulo de ejemplo para el mapa." in mapa
        assert "class Padron: figura(correo)" in mapa
        assert "def contar(votos, blancos)" in mapa
        assert "__init__" not in mapa                      # los métodos especiales no aportan al mapa


def test_mapa_repo_informa_los_errores_de_sintaxis_sin_romperse():
    carpeta, h = repo_temporal({"src/roto.py": "def f(:\n", "src/ok.py": "def g():\n    pass\n"})
    with carpeta:
        mapa = h.mapa_repo("src")
        assert "src/roto.py  [ERROR de sintaxis" in mapa and "def g()" in mapa


def test_mapa_repo_recorta_las_salidas_muy_largas():
    muchos = {f"src/m{i:03d}.py": "def funcion_con_nombre_largo_%d(a, b, c):\n    pass\n" % i for i in range(400)}
    carpeta, h = repo_temporal(muchos)
    with carpeta:
        mapa = h.mapa_repo("src")
        assert len(mapa) < 6100 and "(recortado" in mapa


def test_mapa_repo_de_una_ruta_inexistente():
    carpeta, h = repo_temporal({"a.py": "x = 1\n"})
    with carpeta:
        assert h.mapa_repo("no_existe").startswith("ERROR")


def test_mapa_repo_ubica_la_ventana_de_votacion_en_el_repositorio_real():
    mapa = Herramientas(RAIZ_REPO).mapa_repo("src")
    assert "(recortado" not in mapa, "el mapa del repositorio debe caber completo"
    assert "src/votacion/ventana.py" in mapa and "def esta_abierta(apertura, cierre, ahora)" in mapa


# ---------------------------------------------------------------- E4: memoria de notas
def test_las_notas_se_guardan_y_se_leen():
    carpeta, h = repo_temporal({"a.py": "x = 1\n"})
    with carpeta:
        assert h.leer_notas() == "(sin notas)"
        assert h.anotar("Hipótesis:   ventana.py  compara solo la hora") == "OK: nota guardada (1 en total)"
        assert h.anotar("Archivos revisados: estados.py") == "OK: nota guardada (2 en total)"
        assert h.leer_notas() == "- Hipótesis: ventana.py compara solo la hora\n- Archivos revisados: estados.py\n"


@pytest.mark.parametrize("texto", ["", "   ", None, 42, "x" * 301])
def test_anotar_rechaza_notas_invalidas(texto):
    carpeta, h = repo_temporal({"a.py": "x = 1\n"})
    with carpeta:
        assert h.anotar(texto).startswith("ERROR")
        assert h.leer_notas() == "(sin notas)"


def test_las_notas_tienen_un_tope_total():
    carpeta, h = repo_temporal({"a.py": "x = 1\n"})
    with carpeta:
        resultados = [h.anotar("n" * 290) for _ in range(10)]
        assert resultados[:6] == ["OK: nota guardada (%d en total)" % i for i in range(1, 7)]
        assert resultados[-1].startswith("ERROR: las notas superarían")


def test_las_notas_no_forman_parte_del_cambio_propuesto():
    carpeta, h = repo_temporal({"a.py": "x = 1\n"})
    with carpeta:
        h.anotar("una hipótesis")
        assert h.ver_cambios() == "(sin cambios)"


# ---------------------------------------------------------------- catálogo
def test_el_catalogo_documenta_cada_herramienta():
    catalogo = Herramientas(RAIZ_REPO).catalogo()
    assert {"mapa_repo", "anotar", "leer_notas"} <= set(catalogo)
    for nombre, descripcion in catalogo.items():
        assert descripcion.startswith(nombre + "(") and len(descripcion) > len(nombre) + 10


def test_el_catalogo_puede_ocultar_las_herramientas_nuevas():
    base = {"leer_archivo", "buscar"}
    assert set(Herramientas(RAIZ_REPO, habilitadas=base).catalogo()) == base
