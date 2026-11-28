# Issue #1: Un estudiante puede votar dos veces cambiando las mayúsculas de su correo

**Reportado por:** comité electoral (simulacro del 12/11)
**Observado:** el estudiante `alumno@unsa.edu.pe` participó, volvió a ingresar como `ALUMNO@unsa.edu.pe` y el sistema aceptó una segunda participación (el contador de participantes quedó en 2).
**Esperado:** el correo se compara sin distinguir mayúsculas ni espacios sobrantes; la segunda participación lanza `ParticipacionDuplicada` (RF-03).
**Prueba que reproduce el error:**
`tests/test_issue_01_voto_doble.py::test_issue_01_no_permite_votar_dos_veces_cambiando_mayusculas`
