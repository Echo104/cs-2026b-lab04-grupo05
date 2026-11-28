"""Issue #1 (RF-03): se puede votar dos veces cambiando las mayúsculas del correo."""
import pytest

from src.votacion.excepciones import ParticipacionDuplicada
from src.votacion.padron import Padron

CORREO = "alumno@unsa.edu.pe"


def test_issue_01_no_permite_votar_dos_veces_cambiando_mayusculas():
    padron = Padron([CORREO])
    padron.registrar_participacion(CORREO)
    with pytest.raises(ParticipacionDuplicada):
        padron.registrar_participacion("ALUMNO@unsa.edu.pe")
    assert padron.total_participantes() == 1


def test_otro_estudiante_si_puede_participar():
    padron = Padron([CORREO, "otra@unsa.edu.pe"])
    padron.registrar_participacion(CORREO)
    padron.registrar_participacion("otra@unsa.edu.pe")
    assert padron.total_participantes() == 2


def test_correo_fuera_del_padron_se_rechaza():
    with pytest.raises(ValueError):
        Padron([CORREO]).registrar_participacion("intruso@gmail.com")
