# Inventario del modelo C4 — VotoEPIS

Todos los elementos de [workspace.dsl](workspace.dsl) salen de artefactos de los Laboratorios 04 y 05.

## Elementos y su origen
| Elemento | Tipo C4 | Origen |
|----------|---------|--------|
| Estudiante votante, Comité electoral, Auditor | Persona | [drivers.md](../drivers.md) (RF-01 a RF-08, columna Actor) |
| VotoEPIS | Sistema de software | Caso 5 de la guía del Lab 04 |
| Servidor de correo institucional | Sistema externo | [ADR-003](../adr/003-autenticacion-otp-correo.md) y [arquitectura.mmd](../diagramas/arquitectura.mmd) |
| Sistema académico UNSA | Sistema externo | R-05 de drivers.md (el padrón llega como CSV; sin integración directa) |
| Web de votación | Contenedor | [arquitectura.mmd](../diagramas/arquitectura.mmd) (capa de presentación) y [despliegue.py](../diagramas/despliegue.py) |
| API VotoEPIS | Contenedor | [ADR-001](../adr/001-estilo-arquitectonico.md) (monolito modular en Django) y despliegue.py |
| Base de datos del padrón, Base de datos de la urna | Contenedor | [ADR-002](../adr/002-anonimato-del-voto.md) (dos esquemas de PostgreSQL con roles distintos) |
| Monitoreo | Contenedor | despliegue.py (Grafana) |
| Módulos Elección y padrón, Autenticación, Votación, Resultados, Auditoría | Componente (de la API) | [paquetes.puml](../../design/paquetes.puml) (Lab 05) |
| Flujo «emitir un voto» | Vista dinámica | [secuencia-emitir-voto.puml](../../design/secuencia-emitir-voto.puml) (Lab 05) |
| Nginx, Gunicorn, el servidor | Nodos de despliegue (no son contenedores C4) | despliegue.py (Lab 04) |

## Pistas de la guía (Tabla 10) frente al ADR propio
| Pista | Decisión en este modelo | Por qué |
|-------|-------------------------|---------|
| Sistema externo «Autenticación institucional» | Se modela el **servidor de correo** (SMTP); no hay sistema de autenticación externo | ADR-003: el acceso es por código de un solo uso enviado al correo, no por inicio de sesión federado |
| Sistema externo «Padrón del sistema académico» | Sistema externo **sin relación con VotoEPIS**; el comité obtiene el CSV y lo carga | R-05: no hay acceso directo al sistema académico |
| Contenedor «Registro de auditoría» | No se modela como contenedor; la auditoría es el módulo Auditoría de la API, que exporta la urna anonimizada | El ADR-001 no define un almacén separado para la auditoría |
| «Base de datos de votos separada del padrón» | Dos contenedores de base de datos (`padron` y `urna`) sobre **un mismo servidor PostgreSQL** | ADR-002: dos esquemas con roles distintos, no dos servidores |
| Nginx / proxy | Va como parte de un nodo de despliegue, no como contenedor | Es infraestructura, igual que Docker Compose en el ejemplo |

## Supuestos del modelo (confirmar o registrar en un ADR)
- La tecnología de la Web de votación no está fijada en el ADR-001; se indica «aplicación web responsive (navegador)».
- Las elecciones y las listas se guardan en el esquema `padron` (el ADR-002 solo define padrón, participación y urna).
- La relación API → Monitoreo («Envía métricas de salud», HTTP) se tomó de despliegue.py, que dibuja Grafana con una línea punteada; el protocolo no está documentado en ningún ADR.
- Tamaño del servidor («2 vCPU, 4 GB RAM») es un supuesto para el volumen del caso (≈ 300 votantes en 10 minutos).
- No hay todavía una decisión sobre dónde se guarda la constancia de los intentos de doble voto (QA-01).
