# Bitácora de uso de IA — Modelo C4 (Lab 06) — VotoEPIS

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 19/10 | Claude | Prompt IA 1 adaptado: borrador de `workspace.dsl` desde `inventario.md`, ADR-001 y despliegue.py | 3 personas, 2 sistemas externos, 5 contenedores, 5 componentes, vista dinámica de 6 pasos y despliegue | Se contrastó con las pistas de la Tabla 10 y con los ADR: «Autenticación institucional» se reemplazó por el servidor de correo (ADR-003); el padrón queda sin integración directa (R-05); no hay contenedor de auditoría ni de Nginx (ADR-001). `validar_modelo.py`: 14 de 14 comprobaciones.  | Corregida |

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
