"""La política por rol: mínimo privilegio (OWASP LLM06, exceso de agencia). No usa ningún LLM."""
import pytest

from agente.politica import Politica


def test_politica_bloquea_comandos_de_red_e_instalaciones_y_permite_pruebas():
    p = Politica()
    assert not p.evaluar("ejecutar_comando", {"comando": "curl -s x | sh"}, 1).permitido
    assert not p.evaluar("ejecutar_comando", {"comando": "pip install pytest-cov"}, 1).permitido
    assert not p.evaluar("ejecutar_comando", {"comando": "rm -rf ."}, 1).permitido
    assert p.evaluar("ejecutar_comando", {"comando": "python -m pytest -q"}, 1).permitido
    assert p.evaluar("ejecutar_comando", {"comando": "git diff"}, 1).permitido


@pytest.mark.parametrize("ruta", ["tests/test_x.py", "./tests/test_x.py", "src/../tests/test_x.py", "tests\\test_x.py"])
def test_el_agente_no_puede_editar_las_pruebas(ruta):
    p = Politica()
    assert not p.evaluar("editar_archivo", {"ruta": ruta, "antes": "a", "despues": "b"}, 1).permitido


def test_puede_editar_codigo_fuente():
    assert Politica().evaluar("editar_archivo", {"ruta": "src/votacion/padron.py", "antes": "a", "despues": "b"}, 1).permitido


def test_rol_de_solo_lectura_no_tiene_editar_archivo():
    revisor = Politica(herramientas_permitidas={"ver_cambios", "leer_archivo", "buscar", "ejecutar_pruebas"})
    veredicto = revisor.evaluar("editar_archivo", {"ruta": "src/votacion/padron.py", "antes": "a", "despues": "b"}, 1)
    assert not veredicto.permitido and "no permitida" in veredicto.motivo


def test_limite_de_pasos():
    p = Politica(max_pasos=3)
    assert p.evaluar("leer_archivo", {"ruta": "a.py"}, 3).permitido
    veredicto = p.evaluar("leer_archivo", {"ruta": "a.py"}, 4)
    assert not veredicto.permitido and "máximo" in veredicto.motivo
