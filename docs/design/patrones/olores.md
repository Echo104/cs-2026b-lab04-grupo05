# E1 — Olores detectados en VotoEPIS

Revisión de `src/votacion/antes/servicio.py` y de la salida de `radon cc -s -a`.
La implementación se mantiene ingenua a propósito como línea base para comparar
el refactor. Las líneas pueden variar si el archivo se modifica.

| Olor observado | Patrón propuesto | Principio SOLID | Costo / riesgo | Decisión del equipo |
|---|---|---|---|---|
| Validación de estado y ventana horaria dentro del caso de uso | State (para el ciclo de vida; guardas temporales aparte) | SRP, OCP | Más clases y coordinación de transiciones | Aceptado para modelar transiciones de elección; la ventana horaria seguirá siendo una guarda explícita |
| Reintentos de persistencia mezclados con el flujo de emitir voto | Decorator o política de reintentos inyectable | SRP, OCP | Hay que distinguir errores transitorios de errores de negocio | Aceptado; solo se reintentarán errores transitorios, nunca duplicados |
| Persistencia y envío de correo son dependencias con responsabilidades diferentes | Adapter / puertos separados | DIP, SRP | Requiere contratos y adaptadores por servicio | Aceptado; `externos.py` declara interfaces diferentes para repositorio y correo |
| Auditoría y notificación se coordinan directamente dentro del servicio | Observer | OCP, DIP | Orden de eventos y fallos de suscriptores deben definirse | Aceptado para desacoplar consumidores; el registro del voto debe ocurrir antes de notificar |
| Los parámetros primitivos no expresan la intención de emitir un voto | Command | SRP, OCP | Un objeto adicional y posible sobreestructura para un flujo pequeño | Aceptado si la orden se necesita auditar/reintentar como unidad |
| Se propuso usar Singleton para garantizar un único servicio de votación | Singleton | — | Estado global, pruebas acopladas y dependencias difíciles de sustituir | **Rechazado**: la unicidad no está demostrada como requisito; la inyección de dependencias permite dobles de prueba y configuración explícita |

## Resultado del Prompt IA 1 y verificación humana

Prompt utilizado (adaptado al caso VotoEPIS): «Actúa como revisor experto en
refactorización y patrones GoF. Revisa `antes/servicio.py` y la salida de Radon.
Identifica olores concretos, patrón propuesto o ninguno, principio SOLID, costo
de aplicación. No escribas código, no propongas patrones sin olor concreto y no
uses Singleton».

La IA puede sugerir patrones, pero el equipo decide según el flujo de emisión de
voto y los requisitos de privacidad. Se rechaza Singleton por el estado global y
porque dificulta sustituir servicios externos durante las pruebas.

## Línea base E1

- Flujo ingenuo: `src/votacion/antes/servicio.py`.
- Dobles externos: `src/votacion/externos.py`.
- Pruebas de caracterización: `tests/test_comportamiento.py`.
- Salida de complejidad: `docs/design/patrones/radon-antes.txt`.
