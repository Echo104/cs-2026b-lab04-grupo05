# Issue #3: La elección cierra antes de la hora configurada

**Reportado por:** delegados de ciclo (simulacro del 12/11)
**Observado:** con cierre configurado a las 18:30, a las 18:10 la pantalla ya muestra «La votación ya cerró»; se pierden 30 minutos de votación.
**Esperado:** la elección sigue abierta hasta las 18:30 (exclusive) y se cierra exactamente a esa hora (RF-07).
**Prueba que reproduce el error:**
`tests/test_issue_03_cierre_anticipado.py::test_issue_03_sigue_abierta_hasta_la_hora_de_cierre`
