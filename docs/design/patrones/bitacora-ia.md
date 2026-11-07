# Bitácora de uso de IA — Patrones de diseño (Lab 07) — VotoEPIS


| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 03/11 | Claude | Prompt IA 1 (detector de olores) sobre `antes/servicio.py` | 11 olores con patrón, principio SOLID y costo | Se contrastó con la lectura del código y con la complejidad (8 y 7). Se rechazaron Singleton, Abstract Factory, Command y Chain para la elegibilidad por no eliminar un olor concreto; Strategy + Factory se aceptó con reserva (cambio previsto, un solo canal hoy).  | 7 aceptados (1 con reserva), 4 rechazados |
| 2 | 03/11 | Claude | Prompt IA 2: aplicar solo Strategy + Adapter + Factory | `canales.py`, `repositorio.py` (adaptador), `FabricaCanales` y `servicio.py` | Las pruebas de caracterización pasan sobre `antes` y `despues` (la suite de esta etapa: 42 pasan y 1 xfail). La prueba `test_comprobantes_distintos_entre_participaciones` falla en `antes` (xfail): todos los comprobantes tienen el mismo código; `despues` genera códigos distintos.  | Corregida (defecto de `antes` detectado por una prueba) |
| 3 | 03/11 | Claude | Refactor de estados: State desde `estados-eleccion.mmd` | `estados.py` con una etapa por estado y `Eleccion` delegando | 8 transiciones inválidas y 6 guardas verificadas por prueba. En la revisión se halló que una prueba de guardas tenía un parámetro sin usar y no verificaba nada; se reemplazó por pruebas reales | Corregida |
| 4 | 03/11 | Claude | Observer y Decorator para notificaciones y reintentos | `eventos.py` y `RepositorioConReintentos` | Se reintenta solo ante `ErrorTransitorio` y nunca un duplicado (prueba); los eventos no incluyen la lista elegida (prueba de privacidad); un suscriptor defectuoso no anula el voto (prueba) | Aceptada |
| 5 | 03/11 | Claude | Aislar la IA: Strategy + Adapter + Decorator (caché) + Chain | `ia.py` con dos adaptadores, caché y tres guardrails | LLM simulado con respuestas válidas e inválidas; los guardrails bloquean datos personales, resultados parciales y textos largos; la IA no recibe el repositorio (prueba). Los mismos casos pasan sobre `antes` y `despues` | Aceptada |
| 6 | 03/11 | Claude | Diagramas PlantUML por patrón y actualización de `clases.puml` | 5 diagramas de patrones, una secuencia y `clases.puml` actualizado | `verificar_consistencia.py` (Lab 05): C1 8 de 8, C2, C3 y C4 en OK.| Aceptada (pendiente render) |

## Anexo: prompts

Todos siguen la estructura RCRTF. Péguenles el contexto (código, pruebas y ADR) si usan una conversación nueva.

### Entrada 1 — Detector de olores (Prompt IA 1)
```
Actúa como revisor de código experto en refactorización (Fowler) y patrones GoF.
Contexto: [pegar src/votacion/antes/servicio.py y la salida de radon].
Tarea: identifica los olores de código. Para cada uno indica: líneas, olor, el patrón GoF que lo
resolvería (o "ninguno" si no se justifica), el principio SOLID que mejora y el COSTO de aplicarlo.
Restricciones: no escribas código todavía; no propongas patrones sin un olor concreto; no uses Singleton.
Formato: tabla Markdown.
```

### Entrada 2 — Strategy + Adapter + Factory (Prompt IA 2)
```
Aplica ÚNICAMENTE el patrón [Strategy + Adapter + Factory] al siguiente código [pegar antes/servicio.py],
para el canal de entrega del comprobante y la traducción de los servicios externos [pegar externos.py].
Reglas: (1) no cambies el comportamiento observable; las pruebas [pegar test_comportamiento.py] deben
seguir pasando; (2) no introduzcas Singleton ni estado global; (3) no agregues patrones que no te pedí;
(4) el canal debe validarse antes de registrar el voto; (5) muestra los archivos completos y explica en
3 líneas qué olor elimina.
```

### Entrada 3 — State
```
Aplica ÚNICAMENTE el patrón State a la clase Eleccion [pegar dominio.py] siguiendo esta máquina de estados
[pegar estados-eleccion.mmd]. Reglas: una clase base que prohíba todas las transiciones y una subclase por
estado que redefina solo las permitidas; ninguna clase de estado debe preguntar por el nombre de otro
estado; conserva la API pública y los mensajes de error. Muestra los archivos completos.
```

### Entrada 4 — Observer y Decorator
```
Aplica ÚNICAMENTE Observer y Decorator a este servicio [pegar servicio.py]. Observer: el evento
"voto_registrado" debe notificar el comprobante y registrar la auditoría; sus datos NO deben incluir la lista
elegida (el voto es secreto). Decorator: extrae los reintentos de persistencia; reintenta solo ante
TimeoutError, nunca ante un duplicado. No cambies el comportamiento observable [pegar las pruebas].
```

### Entrada 5 — IA aislada
```
Implementa un asistente que responde preguntas sobre el reglamento electoral detrás de una interfaz
ProveedorLLM con dos adaptadores (interfaces distintas: [pegar externos.py]), un Decorator de caché y una
cadena de guardrails (datos personales, afirmaciones prohibidas como resultados parciales, longitud
máxima). Restricciones: la IA NO recibe el repositorio ni participa en el conteo; no uses claves de API;
las pruebas usan modelos simulados. Muestra los archivos completos.
```

### Entrada 6 — Diagramas por patrón
```
Genera un diagrama de clases PlantUML por cada patrón aplicado en este código [pegar los archivos],
con los estereotipos del rol (<<Strategy>>, <<Adapter>>, <<Factory>>, <<State>>, <<Observer>>,
<<Decorator>>, <<Handler>>) y multiplicidades en las asociaciones, y una secuencia de emitir_voto().
No agregues clases que no existan en el código; si dudas de un nombre, indícalo en un comentario.
```
