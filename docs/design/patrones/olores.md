# E1 — Olores detectados en VotoEPIS

Revisión de `src/votacion/antes/servicio.py` y de la salida de complejidad
(`docs/design/patrones/radon-antes.txt`). La versión se mantiene ingenua a propósito como línea base.

**Métricas de la línea base:** `emitir_voto` complejidad 8 (B), `consultar_reglamento` 7 (B),
promedio 6,25 y 65 líneas de código (SLOC) en 1 archivo.

| # | Olor observado | Patrón propuesto por la IA | Principio SOLID | Costo / riesgo | Decisión del equipo |
|---|---|---|---|---|---|
| 1 | El estado de la elección se comprueba con condicionales dentro del caso de uso (y las operaciones del dominio repiten esa lógica con `_exigir`) | State | SRP, OCP | Una clase por estado y coordinación de transiciones | **Aceptado**: implementa la máquina de estados del Lab 05 |
| 2 | El servicio conoce las interfaces de cada servicio externo (objetos y diccionarios del repositorio, formato del correo) | Adapter | DIP, ISP | Contratos y adaptadores por servicio | **Aceptado** |
| 3 | El canal de entrega del comprobante está fijo en el servicio; agregar uno obligaría a modificar `emitir_voto` (cambio previsto: RF-08 «pantalla y por correo» y el adaptador intercambiable del ADR-003) | Strategy + Factory (registro) | OCP, DIP | Dos clases e indirección para un único canal hoy | **Aceptado con reserva**: el olor es un cambio previsto, no un `if/elif` actual; si no hubiera cambios previstos, se rechazaría |
| 4 | Bucle de reintentos de persistencia mezclado con el flujo de emitir voto | Decorator | SRP, OCP | Distinguir errores transitorios de errores de negocio | **Aceptado**: se reintenta solo `TimeoutError`, nunca un duplicado |
| 5 | El servicio registra eventos y envía el comprobante a mano; cada interesado nuevo obliga a modificar `emitir_voto` | Observer | OCP, SRP | Orden de eventos y fallos de suscriptores | **Aceptado**: el voto se registra antes de notificar y los eventos no incluyen la lista elegida |
| 6 | `consultar_reglamento` elige proveedor con `if/elif` y mezcla las validaciones de la respuesta del LLM | Strategy + Adapter + Chain of Responsibility | OCP, DIP, SRP | Más clases para una función auxiliar | **Aceptado**: la salida del LLM es un dato no confiable |
| 7 | La misma pregunta al modelo se paga cada vez | Decorator (caché) | OCP | Respuestas obsoletas si cambia el reglamento | **Aceptado** |
| 8 | Validaciones de elegibilidad en secuencia (elección abierta, horario, lista, estudiante) | Chain of Responsibility | SRP | Cuatro clases para validaciones de una línea | **Rechazado por ahora**: son cuatro comprobaciones simples y claras; ver `metricas.md` |
| 9 | El voto como acción auditable | Command | SRP | Un objeto adicional sin necesidad de deshacer ni encolar | **Rechazado**: la auditoría se logra con Observer; no hay cola ni «deshacer» |
| 10 | «El servicio de votación debería ser Singleton» | Singleton | — | Estado global; impide inyectar dobles en las pruebas | **Rechazado**: la inyección de dependencias basta |
| 11 | «Una familia de fábricas (Abstract Factory) para canales y proveedores de IA» | Abstract Factory | — | No hay familias de productos relacionados | **Rechazado**: sería sobreingeniería |

## Prompt IA 1 y verificación humana

Prompt (adaptado a VotoEPIS): «Actúa como revisor de código experto en refactorización (Fowler) y
patrones GoF. Contexto: `antes/servicio.py` y la salida de radon. Tarea: identifica los olores; para
cada uno indica líneas, olor, el patrón GoF que lo resolvería (o "ninguno"), el principio SOLID que
mejora y el costo de aplicarlo. Restricciones: no escribas código todavía; no propongas patrones sin
un olor concreto; no uses Singleton. Formato: tabla Markdown».

Las filas 8 a 11 se rechazan o se posponen porque no eliminan un olor concreto que valga su costo
(«patternitis»). La fila 3 es la más discutible: se acepta solo porque el cambio es previsible y se
documenta como riesgo en el ADR-005.

## Línea base E1

- Flujo ingenuo: `src/votacion/antes/servicio.py`.
- Dobles externos: `src/votacion/externos.py` (repositorio, correo y dos modelos de lenguaje con
  interfaces distintas).
- Pruebas de caracterización: `tests/test_comportamiento.py` y `tests/test_comportamiento_ia.py`.
- Defecto conocido de la versión antes (prueba marcada como xfail): el comprobante tiene un código fijo.
