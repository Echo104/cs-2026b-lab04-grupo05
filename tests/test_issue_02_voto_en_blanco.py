"""Issue #2 (RF-04): el voto en blanco se cuenta como voto válido."""
from src.votacion.escrutinio import contar


def test_issue_02_el_voto_en_blanco_no_cuenta_como_valido():
    resultado = contar(["L1", "L1", "L2", None])
    assert resultado == {"por_lista": {"L1": 2, "L2": 1}, "en_blanco": 1, "validos": 3, "total": 4}


def test_cuenta_los_votos_de_cada_lista():
    resultado = contar(["L1", "L2", "L1"])
    assert resultado["por_lista"] == {"L1": 2, "L2": 1} and resultado["validos"] == 3


def test_urna_vacia():
    assert contar([])["total"] == 0
