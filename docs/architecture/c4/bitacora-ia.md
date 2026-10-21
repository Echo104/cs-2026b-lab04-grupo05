# Bitácora de uso de IA — Modelo C4 (Lab 06) — VotoEPIS

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 19/10 | Claude | Prompt IA 1 adaptado: borrador de `workspace.dsl` desde `inventario.md`, ADR-001 y despliegue.py | 3 personas, 2 sistemas externos, 5 contenedores, 5 componentes, vista dinámica de 6 pasos y despliegue | Se contrastó con las pistas de la Tabla 10 y con los ADR: «Autenticación institucional» se reemplazó por el servidor de correo (ADR-003); el padrón queda sin integración directa (R-05); no hay contenedor de auditoría ni de Nginx (ADR-001). `validar_modelo.py`: 14 de 14 comprobaciones.  | Corregida |
| 2 | 19/10 | Claude | Revisión de contradicciones entre los Lab 04, 05 y 06 | El diagrama de secuencia del Lab 05 llamaba «PWA» a la web, pero el Lab 04 la describe como web responsive y el ADR-001 no define una PWA | Se corrigió el artefacto equivocado: `secuencia-emitir-voto.puml` ahora dice «Web de votación»; `verificar_consistencia.py` del Lab 05 sigue en OK | Corregida |
| 3 | 19/10 | Claude | Coherencia del nivel 3 con el diseño del Lab 05 | 5 componentes y sus dependencias | `validar_modelo.py`: los 5 componentes son los paquetes de `paquetes.puml` (sin `compartido`); las 7 dependencias son idénticas; sin ciclos; los 6 pasos de la vista dinámica corresponden a relaciones existentes | Aceptada |
| 4 | 19/10 | Claude | Revisión de etiquetas con la lista C4 | La flecha API → Monitoreo decía «Expone métricas de salud» | La flecha va de la API al monitoreo, así que «Expone» no coincidía con la dirección; se cambió a «Envía métricas de salud». El protocolo HTTP sigue siendo un supuesto | Corregida |
| 5 | 19/10 | Claude | Prompt IA 3: explicación para el público no técnico | Un texto para el comité electoral | 101 palabras (máximo 120); cada afirmación se contrastó con el modelo (correo para códigos y comprobantes, padrón en archivo, auditor que recuenta, el voto registrado no se pierde si falla el correo) | Aceptada |
| 6 | 19/10 | Claude | Prompt IA 2: auditor C4 sobre las cinco vistas | Hallazgos sobre contexto, contenedores y despliegue | - | Pendiente de verificar |

## Anexo: prompts

### Entrada 1 — Borrador del modelo (Prompt IA 1 adaptado)
```
Actúa como arquitecto de software experto en el modelo C4 y en Structurizr DSL.
Contexto: [pegar inventario.md, ADR-001, ADR-002, ADR-003 y despliegue.py de VotoEPIS].
Tarea: escribe un workspace de Structurizr DSL con personas, el sistema, sus contenedores (con tecnología),
los componentes del contenedor API, los sistemas externos (con la etiqueta "Externo") y relaciones con
descripción y protocolo. Incluye las vistas systemContext, container, component, dynamic (emitir un voto)
y deployment (entorno "Producción").
Restricciones: usa SOLO las tecnologías de los ADR; no confundas contenedor C4 con contenedor Docker;
la autenticación es por código enviado al correo (ADR-003), no por inicio de sesión federado; el padrón
llega como CSV, sin integración con el sistema académico (R-05); usa !identifiers hierarchical.
Formato: solo el código DSL.
```

### Entrada 2 — Contradicciones entre laboratorios
```
Actúa como revisor de consistencia. Te paso los artefactos de VotoEPIS de los Laboratorios 04, 05 y 06:
[pegar arquitectura.mmd, ADR-001, secuencia-emitir-voto.puml y workspace.dsl].
Tarea: lista las contradicciones entre ellos (nombres de elementos, tecnologías, responsabilidades) y, para
cada una, indica cuál artefacto debería corregirse y por qué.
Formato: tabla (contradicción, artefactos involucrados, artefacto a corregir, justificación).
No inventes contradicciones; si no hay, dilo.
```

### Entrada 3 — Coherencia con el Lab 05
```
Actúa como revisor de arquitectura. Te paso el workspace.dsl de VotoEPIS y el paquetes.puml del Laboratorio 05:
[pegar ambos archivos].
Tarea: verifica que (1) los componentes de la API sean exactamente los paquetes de paquetes.puml, (2) las
dependencias entre componentes sean las mismas y no formen ciclos, y (3) cada paso de la vista dynamic
corresponda a una relación ya definida en el modelo.
Formato: tabla (regla, resultado, evidencia). No reescribas los archivos; si algo cumple, indícalo.
```

### Entrada 4 — Etiquetas y direcciones de las relaciones
```
Actúa como revisor de diagramas C4. Te paso las relaciones de workspace.dsl: [pegar la sección de relaciones].
Tarea: para cada relación verifica que la etiqueta describa la intención desde el elemento de origen hacia el
de destino y que tenga protocolo cuando conecta contenedores o sistemas externos.
Formato: solo las relaciones con problema, en tabla (relación, problema, etiqueta sugerida).
```

### Entrada 5 — Explicación para público no técnico (Prompt IA 3)
```
Explica el siguiente diagrama de contexto al comité electoral de la EPIS, que no es técnico, en máximo 120
palabras: qué hace el sistema, quién lo usa y de qué servicios externos depende. Evita la jerga técnica.
[pegar la vista de contexto]
```

### Entrada 6 — Auditor C4 (Prompt IA 2)
```
Actúa como revisor de diagramas de arquitectura. Evalúa estas vistas exportadas de un modelo C4
[pegar los .puml o adjuntar las imágenes] con la lista de revisión de c4model.com: generales, elementos y
relaciones. Responde en una tabla (vista, pregunta de la lista, cumple sí/no, evidencia, corrección sugerida).
No inventes problemas: si algo cumple, indícalo.
```
