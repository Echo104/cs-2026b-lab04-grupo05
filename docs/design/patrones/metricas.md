# E6 — Métricas y trade-off del refactor

Mediciones sobre el flujo «emitir voto» y el asistente de reglamento. Las cifras salen de
`radon-antes.txt` y `radon-despues.txt`.

## Complejidad ciclomática (radon cc)
| Bloque | Antes | Después |
|--------|-------|---------|
| `emitir_voto()` | 8 (B) | 1 (A) |
| `consultar_reglamento()` | 7 (B) | 1 (A) |
| Clase `ServicioVotacion` | 7 (B) | 3 (A) |
| Mayor complejidad en el módulo | 8 (B) | 5 (A, `ServicioVotacion.__init__`) |
| Promedio por bloque | 6,25 (B) — 4 bloques | 1,62 (A) — 116 bloques |

## Tamaño (SLOC) y costo de cambio
| Medida | Antes | Después |
|--------|-------|---------|
| Líneas de código del flujo (sin el dominio del Lab 05) | 65 (1 archivo) | 278 (7 archivos) |
| Líneas incluyendo `dominio.py` | 65 | 371 (8 archivos) |
| Métodos a modificar para agregar un canal de comprobante | 1 (`emitir_voto`) | 0 (se registra en la fábrica) |
| Métodos a modificar para agregar un proveedor de IA | 1 (`consultar_reglamento`) | 0 (se agrega al diccionario de proveedores) |
| Métodos a modificar para agregar un suscriptor (p. ej., otra auditoría) | 1 (`emitir_voto`) | 0 (se suscribe) |

## Pruebas
La suite completa (caracterización sobre `antes` y `despues`, pruebas de patrones y de IA) tiene 84 pruebas que pasan en el entorno donde se
generó este material, más 1 `xfail` que documenta un defecto de la versión antes (comprobante con código fijo). Ejecute `pytest -v` para confirmarlo en su equipo.

## Análisis del trade-off (¿qué ganamos, qué costó y cuándo bastaba la versión antes?)
Ganamos que `emitir_voto` pasó de 8 a 1 y que agregar un canal, un proveedor de IA o un interesado ya no
obliga a modificar el servicio; además, la IA quedó aislada (sin acceso al repositorio ni al conteo) y se
prueba sin red ni claves. También salió a la luz un defecto de la versión antes: todos los comprobantes
tenían el mismo código. Costó pasar de 65 a 278 líneas, de 1 a 7 archivos y aprender cinco patrones. Un
dato honesto: la versión antes tenía complejidad máxima 8, por debajo del umbral de 10, así que no era
«inmanejable». La versión antes habría bastado si VotoEPIS tuviera un único canal de comprobante, un solo
proveedor de IA y ningún interesado adicional previsto. Los patrones se justifican por los cambios
previstos (RF-08, ADR-003 y el asistente de reglamento), no por sí mismos; la fila 3 de `olores.md`
(Strategy + Factory) es la más discutible porque hoy existe un solo canal.

## Patrones que decidimos NO aplicar
- **Singleton** (servicio de votación único): introduce estado global y dificulta inyectar dobles en las pruebas.
- **Abstract Factory** (familias de canales y proveedores): no hay familias de productos relacionados; sería sobreingeniería.
- **Command** (voto como objeto): no hay cola, «deshacer» ni reenvío; la auditoría ya se logra con Observer.
- **Chain of Responsibility para la elegibilidad:** son cuatro comprobaciones de una línea (estado, horario, lista,
  estudiante); cuatro clases las harían menos legibles. Sí se aplica Chain a los guardrails de la IA, donde las
  reglas se combinan y se espera agregar más.
