# Issue #2: El voto en blanco se cuenta como voto válido

**Reportado por:** auditor de la elección
**Observado:** con los votos `L1, L1, L2, (blanco)` el escrutinio informa 4 votos válidos y una «lista» llamada BLANCO.
**Esperado:** los votos en blanco se informan aparte (`en_blanco`) y no cuentan como válidos ni como una lista: resultado `{"por_lista": {"L1": 2, "L2": 1}, "en_blanco": 1, "validos": 3, "total": 4}` (RF-04).
**Prueba que reproduce el error:**
`tests/test_issue_02_voto_en_blanco.py::test_issue_02_el_voto_en_blanco_no_cuenta_como_valido`
