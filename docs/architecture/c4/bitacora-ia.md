# Bitácora de uso de IA — Modelo C4 (Lab 06) — VotoEPIS

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 19/10 | Claude | Prompt IA 1 adaptado: borrador de `workspace.dsl` desde `inventario.md`, ADR-001 y despliegue.py | 3 personas, 2 sistemas externos, 5 contenedores, 5 componentes, vista dinámica de 6 pasos y despliegue | Se contrastó con las pistas de la Tabla 10 y con los ADR: «Autenticación institucional» se reemplazó por el servidor de correo (ADR-003); el padrón queda sin integración directa (R-05); no hay contenedor de auditoría ni de Nginx (ADR-001). `validar_modelo.py`: 14 de 14 comprobaciones. Ejecutar `structurizr.sh validate` | Corregida |
| 2 | 19/10 | Claude | Revisión de contradicciones entre los Lab 04, 05 y 06 | El diagrama de secuencia del Lab 05 llamaba «PWA» a la web, pero el Lab 04 la describe como web responsive y el ADR-001 no define una PWA | Se corrigió el artefacto equivocado: `secuencia-emitir-voto.puml` ahora dice «Web de votación»; `verificar_consistencia.py` del Lab 05 sigue en OK | Corregida |
| 3 | 19/10 | Claude | Coherencia del nivel 3 con el diseño del Lab 05 | 5 componentes y sus dependencias | `validar_modelo.py`: los 5 componentes son los paquetes de `paquetes.puml` (sin `compartido`); las 7 dependencias son idénticas; sin ciclos; los 6 pasos de la vista dinámica corresponden a relaciones existentes | Aceptada |

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
