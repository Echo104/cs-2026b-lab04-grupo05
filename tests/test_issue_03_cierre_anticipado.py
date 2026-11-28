"""Issue #3 (RF-07): la elección cierra antes de la hora configurada."""
from datetime import datetime

from src.votacion.ventana import esta_abierta

APERTURA = datetime(2026, 11, 20, 8, 0)
CIERRE = datetime(2026, 11, 20, 18, 30)


def test_issue_03_sigue_abierta_hasta_la_hora_de_cierre():
    assert esta_abierta(APERTURA, CIERRE, datetime(2026, 11, 20, 18, 10)) is True
    assert esta_abierta(APERTURA, CIERRE, datetime(2026, 11, 20, 18, 29)) is True


def test_se_cierra_exactamente_a_la_hora():
    assert esta_abierta(APERTURA, CIERRE, datetime(2026, 11, 20, 18, 30)) is False


def test_no_esta_abierta_antes_de_la_apertura():
    assert esta_abierta(APERTURA, CIERRE, datetime(2026, 11, 20, 7, 59)) is False
    assert esta_abierta(APERTURA, CIERRE, datetime(2026, 11, 20, 12, 0)) is True
