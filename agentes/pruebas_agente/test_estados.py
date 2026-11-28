"""Coherencia entre el diagrama diseno/estados.puml, el código del núcleo y las trazas."""
import json
import pathlib
import re

AGENTES = pathlib.Path(__file__).resolve().parents[1]
PUML = (AGENTES / "diseno" / "estados.puml").read_text(encoding="utf-8")
NUCLEO = (AGENTES / "agente" / "nucleo.py").read_text(encoding="utf-8")


def _estados_del_diagrama():
    nombres = set(re.findall(r"^(\w+) -->|--> (\w+)", PUML, flags=re.MULTILINE))
    return {n for par in nombres for n in par if n}


def _snake(nombre):                       # ValidandoContrato -> VALIDANDO_CONTRATO
    return re.sub(r"(?<!^)(?=[A-Z])", "_", nombre).upper()


def test_cada_estado_del_diagrama_existe_en_el_codigo():
    estados = _estados_del_diagrama()
    assert {"PreparandoSandbox", "Decidiendo", "ValidandoContrato", "EvaluandoPolitica", "Ejecutando",
            "Observando", "Finalizado", "LimiteAlcanzado", "SinDecisiones"} <= estados
    faltan = [e for e in estados if _snake(e) not in NUCLEO]
    assert not faltan, f"estados del diagrama que no aparecen en nucleo.py: {faltan}"


def test_cada_estado_de_las_trazas_esta_en_el_diagrama():
    trazas = sorted((AGENTES / "trazas").glob("*.jsonl"))
    assert trazas, "no hay trazas para comprobar"
    for traza in trazas:
        for linea in traza.read_text(encoding="utf-8").splitlines():
            estado = json.loads(linea)["estado"]
            assert estado in {_snake(e) for e in _estados_del_diagrama()} or f"/ {estado}" in PUML, (traza.name, estado)
