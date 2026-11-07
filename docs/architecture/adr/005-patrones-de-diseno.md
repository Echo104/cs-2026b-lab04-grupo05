# ADR-005: Patrones de diseño en el módulo Votación

- Estado: Aceptado
- Fecha: 2026-11-03
- Decisores: <integrantes del grupo>

## Contexto
El flujo «emitir voto» (RF-03 y RF-08; escenarios QA-01, QA-02 y QA-03 de [drivers.md](../drivers.md)) tenía
validaciones, reintentos, persistencia, notificación y un asistente de IA coordinados en un solo método
(`emitir_voto`, complejidad 8; `consultar_reglamento`, complejidad 7). Había cambios previstos: un canal de
comprobante adicional (RF-08), un adaptador de autenticación intercambiable (ADR-003) y un asistente de
reglamento que usa un modelo de lenguaje cuya salida no es confiable. Restricciones: voto secreto (R-06,
[ADR-002](002-anonimato-del-voto.md)), MVP en 1 mes con 3 developers (R-01 y R-02) y sin claves de API en el
repositorio.

## Alternativas consideradas
1. Mantener la versión ingenua (`src/votacion/antes/servicio.py`): 65 líneas, complejidad máxima 8; suficiente si no hubiera cambios previstos.
2. Refactorizar hacia patrones, solo donde un olor concreto lo justifica (7 aceptados, 4 rechazados; ver `docs/design/patrones/olores.md`).
3. Una versión con la máxima cantidad de patrones posible (Singleton, Abstract Factory, Command, Chain para cada validación): rechazada por sobreingeniería.

## Decisión
Adoptamos la alternativa 2 con estos patrones, cada uno con su prueba en `tests/test_patrones.py`:
- **Adapter** para el repositorio y el correo externos (`repositorio.py`, `canales.py`) y para los modelos de lenguaje (`ia.py`).
- **Strategy + Factory (registro)** para el canal de comprobante (`CanalComprobante`, `FabricaCanales`) y para el proveedor de IA (`ProveedorLLM`).
- **State** para el ciclo de vida de la elección, según el diagrama del Lab 05 (`estados.py`).
- **Observer** para el comprobante y la auditoría (`eventos.py`); los eventos no incluyen la lista elegida.
- **Decorator** para los reintentos de persistencia (solo ante errores transitorios) y para la caché de la IA.
- **Chain of Responsibility** para los guardrails de la salida de la IA (`ia.py`).

Rechazamos **Singleton**, **Abstract Factory**, **Command** y **Chain of Responsibility para la elegibilidad**
(ver `docs/design/patrones/metricas.md`). La IA no recibe el repositorio ni participa en el conteo.

## Consecuencias
- Positivas: `emitir_voto` pasa de complejidad 8 a 1 y `consultar_reglamento` de 7 a 1; agregar un canal, un proveedor de IA o un suscriptor no obliga a modificar el servicio; la IA se prueba sin red ni claves; las transiciones inválidas de la elección son imposibles por construcción; las pruebas de caracterización pasan sobre ambas versiones y un defecto de la versión antes (comprobante con código fijo) quedó documentado.
- Negativas / riesgos: el código pasa de 65 a 278 líneas (371 con el dominio) y de 1 a 7 archivos; más indirección: el equipo debe conocer los patrones; Strategy + Factory del canal se aplica a un único canal por cambios previstos, no actuales; los eventos pueden filtrar datos si se agregan campos (hay una prueba que lo vigila); el envío del comprobante sigue siendo síncrono dentro del proceso (pendiente moverlo a una tarea asíncrona).
