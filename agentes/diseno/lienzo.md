# Lienzo de diseño — sistema agéntico de VotoEPIS (Lab 10)

**Objetivo del sistema:** resolver *issues* del código de VotoEPIS (módulos `padron`, `escrutinio` y `ventana`) con una prueba que los reproduce. El agente **nunca** toca votos ni datos reales: trabaja sobre una copia del repositorio con dobles en memoria, y un humano del grupo aprueba cada cambio (regla de oro del laboratorio: *el agente propone; el contrato y la política filtran; el humano aprueba*).

| # | Decisión de diseño | Elección para VotoEPIS | Justificación |
|---|---|---|---|
| 1 | ¿Agente o flujo de trabajo? | **Agente** para resolver issues; **flujo fijo** para emitir votos y contar la urna. | Para un issue hay que explorar el código y la causa no se conoce de antemano (Sección 1.1). En cambio, emitir un voto y escrutar siguen pasos fijos y verificables (`ServicioVotacion`, Lab 07): ahí un LLM que decide el flujo añadiría riesgo para el voto secreto sin aportar valor. Los issues 2 y 3 son tan acotados (un solo módulo y una función) que también podrían resolverse con un flujo fijo «buscar → editar → probar»; se usa el agente para comparar costos en E4 y E5. |
| 2 | Arquetipo (Sección 1.3) | **ReAct** en E2–E4 (un solo agente); **Planificador-ejecutor + ReAct** y **Reflexión** (crítico) en E5. | Localizar un error es exploración (ReAct). El plan corto del planificador hace el sistema más legible y barato de depurar. La reflexión se justifica en el issue 1 porque el cambio toca la regla de participación única, de alto riesgo para la elección: un error cuesta caro. |
| 3 | Herramientas (Sección 1.5) | `listar_archivos`, `leer_archivo`, `buscar`, `ejecutar_pruebas`, `editar_archivo`, `ver_cambios` y `ejecutar_comando` (solo `python -m pytest`, `radon cc`, `lint-imports`, `git status/diff`). En E4: `mapa_repo`, `anotar` y `leer_notas`. | Lo mínimo para leer, cambiar y verificar. `editar_archivo` exige que el fragmento aparezca una sola vez; no existe «ejecutar cualquier comando», no hay acceso a red, a la base de datos ni a la urna. Todas las rutas se validan contra el sandbox. |
| 4 | Memoria (Sección 1.6) | **Corto plazo** (historial de la tarea) en E2; **notas** (`notas.md`) en E4. | Cada issue es una tarea corta y no hace falta recordar ejecuciones anteriores (sin memoria episódica). Las notas sirven para guardar hipótesis y archivos revisados sin releerlos. Memoria semántica y procedimental (por ejemplo, un `AGENTS.md`) queda para el Lab 12. |
| 5 | Coordinación (Sección 1.7) | **Un solo agente** en E2–E4; **por gestor** (planificador) + **actor-crítico** (ejecutor y revisor de solo lectura) en E5, con máximo 2 rondas. | Parsimonia: empezar con un solo agente y añadir más solo si aporta valor. Separar quién cambia el código de quién lo revisa permite dar permisos distintos (el revisor no tiene `editar_archivo`). Se mide en E5 si compensa el costo. |
| 6 | Rol humano (Sección 1.8) | **Revisor:** el agente actúa y una persona del grupo aprueba el cambio antes de incorporarlo al repositorio. | Primer uso del sistema: la confianza aún es baja. El agente no fusiona nada; en E6 se activa la aprobación de cada edición desde la consola y se define cómo ganaría autonomía. |
| 7 | Control | Contrato JSON de cada decisión; política por rol; **máximo 12 pasos** por agente y **2 rondas**; rutas protegidas (`tests/`); sandbox en una copia del repositorio; traza JSONL de cada transición. | Evita acciones indebidas, bucles y costos sin límite, y el agente no puede «arreglar» las pruebas para que pasen. La traza permite auditar y medir (E7). |

## Tareas del agente (issues)
| Issue | Módulo | RF | Prueba que falla | ¿Flujo o agente? |
|---|---|---|---|---|
| [#1](../../issues/ISSUE-01.md) Se vota dos veces cambiando mayúsculas | `padron.py` | RF-03 | `tests/test_issue_01_voto_doble.py` | Agente con reflexión (riesgo alto) |
| [#2](../../issues/ISSUE-02.md) El voto en blanco cuenta como válido | `escrutinio.py` | RF-04 | `tests/test_issue_02_voto_en_blanco.py` | Admite flujo fijo; se usa para comparar (E5) |
| [#3](../../issues/ISSUE-03.md) La elección cierra antes de la hora | `ventana.py` | RF-07 | `tests/test_issue_03_cierre_anticipado.py` | Admite flujo fijo; se usa con herramientas nuevas (E4) |

## Restricciones propias de VotoEPIS
- **Voto secreto (ADR-002):** ninguna herramienta lee la urna ni datos de estudiantes; los dobles de prueba usan correos ficticios.
- **Datos de prueba ficticios:** el agente no recibe credenciales, claves de API ni datos personales reales.
- **Humano en el circuito:** quien aprueba el cambio es una persona del grupo; el agente no hace `git push` ni abre Pull Requests por su cuenta.
