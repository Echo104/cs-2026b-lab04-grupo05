# Round-trip (E6): diagrama → código → diagrama

**Ingeniería directa:** `src/votacion/dominio.py` se generó con IA a partir de [clases.puml](clases.puml) (Prompt IA 2, ver [bitácora](bitacora-ia.md)).

**Ingeniería inversa:** `src/classes_votacion.puml` se generó a partir de `src/votacion/dominio.py` usando pyreverse y se generó `src/classes_votacion.png` usando java plantuml.

## Diferencias entre el diagrama de diseño y el diagrama obtenido del código
| # | Diferencia observada | Causa | Acción |
|---|----------------------|-------|--------|
| 1 | Las asociaciones del diseño (`Eleccion`–`Lista`, `Participacion`–`Estudiante`/`Eleccion`, `Voto`–`Eleccion`/`Lista`) aparecen en el código como campos (`listas`, `estudiante`, `eleccion`, `lista`) y sin multiplicidades | El código expresa las relaciones como atributos y no tiene multiplicidades | Mantener el diagrama de diseño. La multiplicidad `1..*` entre `Eleccion` y `Lista` se hace cumplir con una validación en `abrir()` (regla C3) |
| 2 | Cuatro clases del código no están en el diagrama: `TransicionInvalida`, `EleccionNoAbierta`, `ParticipacionDuplicada`, `ErrorTransitorio` | Son el mecanismo del lenguaje para las ramas de error del diagrama de secuencia (`alt` y `loop`) | Documentar la diferencia: el diagrama de clases se mantiene en el nivel del dominio. Si el docente prefiere verlas, agregarlas con el estereotipo `<<excepción>>` |
| 3 | Operaciones y atributos privados del código no modelados: `Eleccion._exigir`, `ServicioVotacion._registrar_con_reintentos`, `_notificar`, `_repositorio`, `_notificador`, `_reloj` | Detalles de implementación; el reloj se inyecta para poder probar con fechas fijas | Documentar. `_registrar_con_reintentos` corresponde al `loop` del diagrama de secuencia |
| 4 | `SmtpAdapter` y `PostgresRepositorioVotacion` muestran en el código las operaciones de la interfaz; en el diseño solo se ven por la realización | En UML la realización implica implementar la interfaz; el código lo repite | Aceptable; se documenta |
| 5 | El envío del comprobante está marcado como asíncrono (`->>`) en la secuencia, pero el código lo invoca de forma síncrona con `try/except` | La herramienta de ingeniería inversa no ve la asincronía; el esqueleto no tiene cola | Pendiente: encolar el envío en la infraestructura (tarea asíncrona) para cumplir QA-03; mientras tanto, se documenta la limitación |
| 6 | Nombres en `snake_case` (`esta_abierta`) frente a `camelCase` en el diagrama (`estaAbierta`) | Convención de Python | Aceptable; se documenta la equivalencia (C5) |
| 7 | Las interfaces (`NotificadorCorreo`, `RepositorioVotacion`) aparecen como clases abstractas (ABC) y no como `interface` | Python implementa interfaces con ABC | Aceptable en Python; se documenta |
