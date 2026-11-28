# E4 — Herramienta nueva (`mapa_repo`) y memoria de notas

**Herramienta nueva:** `mapa_repo(ruta="src")` devuelve la estructura del código con `ast`: módulos (con la primera línea de su docstring), clases con sus métodos y funciones, con los nombres de sus parámetros. Está documentada en `catalogo()` (qué hace, parámetro y qué devuelve), solo lee (no ejecuta nada), valida la ruta contra el sandbox y su salida está acotada (6000 caracteres; el mapa de `src/` de VotoEPIS ocupa unos 4700).
**Memoria de notas:** `anotar(texto)` y `leer_notas()` guardan hipótesis y archivos revisados en `notas.md` (máx. 300 caracteres por nota y 2000 en total). Las notas no cuentan como parte del cambio propuesto (`ver_cambios`).
Pruebas: [`pruebas_agente/test_herramientas.py`](pruebas_agente/test_herramientas.py).

## Issue 3 resuelto con las herramientas nuevas y con las básicas
Issue: [#3 La elección cierra antes de la hora](../issues/ISSUE-03.md). Causa: `esta_abierta` comparaba `(fecha, hora)` del cierre y descartaba los minutos. Cambio: [diff](trazas/issue03-cambio.diff). Notas del agente: [issue03-notas.md](trazas/issue03-notas.md).

| Ejecución | Pasos | Acciones | Bloqueadas | Rechazadas por el contrato | Contexto final (caracteres) | Herramientas usadas |
|---|---|---|---|---|---|---|
| E2: issue 1, herramientas básicas | 11 | 8 | 1 | 2 | 8457 | leer_archivo ×2, ejecutar_pruebas ×2, buscar ×1, editar_archivo ×1, ver_cambios ×1 |
| Issue 3, herramientas básicas (control) | 8 | 7 | 0 | 0 | 10537 | leer_archivo ×3, buscar ×1, ejecutar_pruebas ×2, editar_archivo ×1 |
| Issue 3, con `mapa_repo` y notas | 9 | 8 | 0 | 0 | 10431 | leer_archivo ×2, mapa_repo ×1, anotar ×1, ejecutar_pruebas ×2, editar_archivo ×1, leer_notas ×1 |

## ¿Necesitó menos pasos o menos contexto?
Con las herramientas nuevas el agente necesitó **+1 paso** (8 → 9) y un contexto **-106 caracteres** (-1.0 %): prácticamente igual. `mapa_repo` evitó la lectura de `estados.py` (el candidato equivocado del control), pero su salida (~4700 caracteres) pesa casi lo mismo que ese archivo, y `anotar` y `leer_notas` añadieron dos pasos. En una tarea corta y un repositorio de 12 módulos las notas no aportan; su valor aparecería en tareas largas, con muchos archivos o con ejecuciones que se reanudan.
**Advertencia:** las decisiones del modelo de estas dos trayectorias las redactó Claude simulando al asistente; el resultado depende de esa simulación y compara issues distintos con una sola muestra. Repita el experimento con su asistente (`--interactivo`) antes de sacar conclusiones.
