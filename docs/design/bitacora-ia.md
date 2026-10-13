# Bitácora de uso de IA — Diseño UML (Lab 05) — VotoEPIS


| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 13/10 | Claude | Prompt IA 1 adaptado: diagrama de clases de HU-03 con ADR-001 y ADR-002 | 12 clases: entidades, enumeración, 2 puertos con sus adaptadores y un servicio; `Voto` sin enlace al estudiante | Contrastado con ADR-001 (puertos y adaptadores) y ADR-002 (sin clave foránea ni marca de tiempo en la urna); multiplicidades con `verificar_consistencia.py` (C3) | Aceptada |
| 2 | 13/10 | Claude | Diagrama de secuencia de «emitir voto» | 8 líneas de vida, `alt` anidado, `loop` de reintentos, mensaje asíncrono para el comprobante | `verificar_consistencia.py`: 8 de 8 mensajes son operaciones de su clase (C1). ☐ Renderizar en plantuml.com y comprobar que no hay errores de sintaxis | Aceptada (pendiente render) |
| 3 | 13/10 | Claude | Máquina de estados de `Eleccion` en Mermaid | 5 estados, 6 transiciones y 4 guardas | `verificar_consistencia.py`: transiciones = operaciones de `Eleccion` y estados = enumeración (C2); 12 pruebas unitarias, una por transición. ☐ Validar en mermaid.live | Aceptada (pendiente validación) |
| 4 | 13/10 | Claude | Prompt IA 2 adaptado: esqueleto en Python desde `clases.puml` | `src/votacion/dominio.py` con dataclasses, ABC, adaptadores con `NotImplementedError` y lógica mínima | Se ejecutaron las 12 pruebas: pasan. Se comparó con el código por ingeniería inversa: 7 diferencias en `round-trip.md`; el envío asíncrono quedó síncrono (pendiente). ☐ Ejecutar `pyreverse` real | Aceptada con diferencias documentadas |
| 5 | 13/10 | Claude | Prompt IA 3 adaptado: auditor de consistencia sobre los cinco diagramas | Hallazgos C1 a C4; el más relevante: ESCRUTADA sin salida si el auditor reporta discrepancia | Hallazgo real, pendiente de decisión del grupo; el hallazgo `Voto` sin asociación a `Estudiante` se espera como falso positivo (R-06). ☐ Repetir con su asistente | Pendiente de decisión |
| 6 | 13/10 | Claude | Diagramas de actividades (escrutinio y acta) y de paquetes | 3 particiones, 3 decisiones y fork/join; 6 paquetes del ADR-001 | C4 con script: 12 dependencias sin ciclos. ☐ Renderizar; ☐ validar el flujo con un compañero que actúe como comité electoral | Aceptada (pendiente validación) |

## Anexo: prompts

### Entrada 1 — Diagrama de clases (Prompt IA 1 adaptado)
```
Actúa como diseñador de software orientado a objetos. Contexto: módulos Elección y Votación de VotoEPIS,
un monolito modular (ADR-001: puertos y adaptadores para integraciones externas; ADR-002: el voto no debe
poder vincularse con el estudiante: sin clave foránea ni marca de tiempo en la urna).
Historia y criterios: [pegar historia.md].
Tarea: genera un diagrama de clases en PlantUML con atributos tipados, operaciones, multiplicidades,
una enumeración para el estado de la elección y una interfaz (puerto) para cada servicio externo.
Formato: solo el código PlantUML. No agregues clases que no se deriven de la historia; si asumes algo,
indícalo en un comentario.
```

### Entrada 2 — Diagrama de secuencia
```
Actúa como diseñador de software. Contexto: el diagrama de clases [pegar clases.puml] y la historia
[pegar historia.md] de VotoEPIS.
Tarea: genera en PlantUML el diagrama de secuencia de "emitir voto" con 5 o más líneas de vida, un fragmento
alt para éxito y error, un loop u opt, al menos un mensaje asíncrono (->>) y los mensajes de retorno.
Restricción: cada mensaje dirigido a un objeto debe ser una operación de su clase en el diagrama de clases;
si necesitas una operación nueva, indícalo en un comentario en lugar de inventarla.
Formato: solo el código PlantUML.
```

### Entrada 3 — Máquina de estados
```
Actúa como diseñador de software. Contexto: la clase Eleccion de [pegar clases.puml] con la enumeración
EstadoEleccion (CONFIGURADA, ABIERTA, CERRADA, ESCRUTADA, PUBLICADA).
Tarea: escribe en Mermaid (stateDiagram-v2) su máquina de estados con estado inicial y final, transiciones
nombradas con operaciones de la clase y 2 o más guardas entre corchetes.
Restricción: no agregues estados que no estén en la enumeración; si una transición no tiene operación, dilo.
Formato: solo el código Mermaid.
```

### Entrada 4 — Ingeniería directa (Prompt IA 2 adaptado)
```
Genera el esqueleto en Python 3.10 (dataclasses y type hints) del siguiente diagrama de clases.
Respeta exactamente los nombres de clases, atributos y operaciones (en snake_case), las enumeraciones,
las interfaces como clases abstractas (ABC) y las multiplicidades. Implementa solo la lógica mínima de las
operaciones de Eleccion y del servicio; los adaptadores deben lanzar NotImplementedError.
No guardes en Voto ninguna referencia al estudiante ni una marca de tiempo. [pegar clases.puml]
```

### Entrada 5 — Auditor de consistencia (Prompt IA 3 adaptado)
```
Actúa como revisor de diseño. Te paso cinco diagramas UML de VotoEPIS en PlantUML/Mermaid:
[pegar clases.puml, secuencia-emitir-voto.puml, estados-eleccion.mmd, actividades-escrutinio-acta.puml, paquetes.puml].
Verifica estas reglas y responde en una tabla (regla, elemento, problema, corrección sugerida):
C1 cada mensaje de secuencia es una operación de la clase receptora; C2 cada transición de estados corresponde
a una operación de la clase; C3 multiplicidades coherentes con los criterios de aceptación; C4 paquetes sin ciclos
y conformes al ADR-001; C5 nombres consistentes. Revisa también que el diagrama de actividades no contradiga el
de estados. No reescribas los diagramas; solo reporta hallazgos y cita la línea.
```

### Entrada 6 — Diagramas de actividades y de paquetes
```
Actúa como analista de procesos y diseñador de software. Contexto: VotoEPIS; proceso "Escrutinio y firma del
acta" con tres actores (comité electoral, sistema y auditor) y los módulos del ADR-001: Elección y padrón,
Autenticación, Votación, Resultados y Auditoría.
Tarea 1: diagrama de actividades en PlantUML con 3 o más particiones, 2 o más decisiones y un fork/join.
Tarea 2: diagrama de paquetes en PlantUML con un paquete por módulo, dependencias etiquetadas con la clase o
el puerto usado y una nota con la regla de dependencias; sin dependencias cíclicas.
Formato: dos bloques de código PlantUML, sin explicaciones largas.
```
