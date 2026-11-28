"""El contrato estructurado de cada decisión (Koenigstein, 2026, cap. 5). No usa ningún LLM."""
import pytest

from agente.contrato import validar_decision

H = {"leer_archivo", "buscar", "ejecutar_pruebas", "editar_archivo"}


@pytest.mark.parametrize("d, esperado", [
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": {"ruta": "a.py"}}, True),
    ({"pensamiento": "listo", "final": "Resuelto"}, True),
    ({"pensamiento": "sin args", "accion": "ejecutar_pruebas"}, True),
    ({"accion": "leer_archivo"}, False),                                                  # sin pensamiento
    ({"pensamiento": "x", "accion": "borrar_todo"}, False),                               # herramienta inventada
    ({"pensamiento": "x", "accion": "leer_archivo", "final": "y"}, False),                # ambas formas
    ("leer_archivo(a.py)", False),                                                        # texto libre, no JSON
    # --- decisiones inválidas propias (vistas en E2 o previsibles en VotoEPIS) ---
    ({"pensamiento": "x", "accion": "leer_archivo", "args": "src/votacion/padron.py"}, False),   # args como texto
    ({"pensamiento": "x", "accion": "leer_archivo", "args": ["src/votacion/padron.py"]}, False),  # args como lista
    ({"pensamiento": "x", "accion": ""}, False),                                          # acción vacía
    ({"pensamiento": "x", "accion": None}, False),                                        # acción nula
    ({"pensamiento": "x", "accion": "buscar", "args": {"patron": "a"}, "confianza": 0.9}, False),  # campo de más
    ({"pensamiento": "x", "final": "ok", "estado": "RESUELTO"}, False),                   # campo de más en «final»
    ({"pensamiento": "   ", "accion": "buscar"}, False),                                  # pensamiento en blanco
    ({"pensamiento": "x", "final": 42}, False),                                           # final que no es texto
    ({"pensamiento": "x", "final": "  "}, False),                                         # final vacío
    ({}, False),                                                                          # objeto vacío
    (None, False),                                                                        # nada
])
def test_contrato(d, esperado):
    assert validar_decision(d, H)[0] is esperado


def test_el_rechazo_explica_el_motivo_para_que_el_modelo_se_corrija():
    ok, motivo = validar_decision({"pensamiento": "x", "accion": "borrar_todo"}, H)
    assert not ok and "borrar_todo" in motivo
