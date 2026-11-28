"""El bucle del agente como máquina de estados, con herramientas falsas (sin sistema de archivos ni LLM)."""
import json
import pathlib
import tempfile

from agente.modelos import ModeloGrabado
from agente.nucleo import Agente
from agente.politica import Politica


class HerramientasFalsas:
    def catalogo(self):
        return {"leer_archivo": "leer_archivo(ruta)", "romper": "romper()"}

    def leer_archivo(self, ruta):
        return f"contenido de {ruta}"

    def romper(self):
        raise RuntimeError("falla de la herramienta")


def accion(nombre, **args):
    return {"pensamiento": f"uso {nombre}", "accion": nombre, "args": args}


FINAL = {"pensamiento": "listo", "final": "Resuelto"}


def correr(decisiones, politica=None):
    with tempfile.TemporaryDirectory() as carpeta:
        traza = pathlib.Path(carpeta) / "t.jsonl"
        agente = Agente("Ejecutor", ModeloGrabado(decisiones), HerramientasFalsas(), politica or Politica(max_pasos=5),
                        "objetivo de prueba", traza)
        resumen = agente.ejecutar()
        escrita = [json.loads(l) for l in traza.read_text(encoding="utf-8").splitlines()]
    return agente, resumen, escrita


def estados(agente):
    return [e["estado"] for e in agente.eventos]


def test_accion_valida_y_final():
    agente, resumen, escrita = correr([accion("leer_archivo", ruta="a.py"), FINAL])
    assert estados(agente) == ["INICIO", "OBSERVANDO", "FINALIZADO"] and resumen == "Resuelto"
    assert escrita == agente.eventos                                   # la traza JSONL refleja los eventos


def test_decision_invalida_se_rechaza_y_el_agente_se_corrige():
    agente, resumen, _ = correr(["texto libre, no JSON", accion("leer_archivo", ruta="a.py"), FINAL])
    assert estados(agente) == ["INICIO", "CONTRATO_INVALIDO", "OBSERVANDO", "FINALIZADO"]
    assert "ERROR DE CONTRATO" in agente.historial[2]["content"]       # el error vuelve al modelo como observación


def test_herramienta_inventada_no_se_ejecuta():
    agente, _, _ = correr([accion("borrar_todo"), FINAL])
    assert estados(agente)[1] == "CONTRATO_INVALIDO"


def test_accion_denegada_por_la_politica_se_bloquea_y_continua():
    politica = Politica(max_pasos=5, herramientas_permitidas={"romper"})
    agente, _, _ = correr([accion("leer_archivo", ruta="a.py"), FINAL], politica)
    assert estados(agente) == ["INICIO", "BLOQUEADO", "FINALIZADO"]
    assert "BLOQUEADO POR LA POLÍTICA" in agente.historial[2]["content"]


def test_el_error_de_una_herramienta_es_una_observacion():
    agente, _, _ = correr([accion("romper"), FINAL], Politica(max_pasos=5, herramientas_permitidas={"romper"}))
    assert estados(agente) == ["INICIO", "OBSERVANDO", "FINALIZADO"]
    assert agente.eventos[1]["observacion"].startswith("ERROR: RuntimeError")


def test_el_limite_de_pasos_evita_ejecutar_indefinidamente():
    agente, resumen, _ = correr([accion("leer_archivo", ruta="a.py")] * 10, Politica(max_pasos=3))
    assert estados(agente)[-1] == "LIMITE_ALCANZADO"
    assert sum(1 for e in agente.eventos if e["estado"] == "OBSERVANDO") == 3
    assert resumen == "(sin respuesta final)"


def test_sin_mas_decisiones_el_agente_termina():
    agente, _, _ = correr([accion("leer_archivo", ruta="a.py")])
    assert estados(agente)[-1] == "SIN_DECISIONES"


def test_el_contexto_crece_con_cada_observacion():
    agente, _, _ = correr([accion("leer_archivo", ruta="a.py"), accion("leer_archivo", ruta="b.py"), FINAL])
    contextos = [e["contexto"] for e in agente.eventos]
    assert contextos == sorted(contextos) and contextos[-1] > contextos[0]
