# Bitácora de uso de IA — VotoEPIS

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 05/10 | Claude | Prompt 1 adaptado: 3 alternativas de estilo para VotoEPIS (3 developers, 1 mes, un servidor) | Monolito en capas, monolito modular y microservicios; recomendó el monolito modular | Se contrastó cada alternativa con R-01, R-02 y R-03; microservicios excede equipo, plazo y presupuesto | Aceptada |
| 2 | 05/10 | Claude | Prompt 2 (abogado del diablo) sobre el monolito modular | Riesgos: límites entre módulos que se rompen, falla única, correlación voto–votante por registros u orden de inserción, administrador con acceso total a la base de datos | Se incorporaron mitigaciones: import-linter (ADR-001), roles y esquemas separados, urna sin marcas de tiempo (ADR-002). El riesgo del administrador no se elimina y se declara en el ADR-002 | Corregida |
| 3 | 05/10 | Claude | Pesos, puntajes y total ponderado de la matriz | Totales 3,90 / 4,05 / 2,95 | Recalculados con `matriz_grafico.py`: coinciden; los pesos suman 100 %. Se añadió análisis de sensibilidad (la decisión cambia si seguridad baja a 15 % y entrega sube a 35 %) | Aceptada |
| 4 | 05/10 | Claude | Autenticación del votante con correo institucional | Supuso que la universidad ofrece inicio de sesión federado con la cuenta institucional | No hay evidencia de ello en el caso; se eligió código OTP por correo (ADR-003). ☐ Confirmar con la oficina de TI qué mecanismo permite la UNSA | Corregida |
| 5 | 05/10 | Claude | Recibo verificable por votante para la auditoría | Se evaluó como alternativa en el ADR-002 | Permitiría demostrar a un tercero cómo se votó (compra o coerción) y choca con R-06 | Rechazada |
| 6 | 05/10 | Claude | Código Mermaid y Python Diagrams a partir de la matriz y los ADR | `arquitectura.mmd`, `despliegue.py` | Validar `arquitectura.mmd` en mermaid.live y GitHub; ejecutar `despliegue.py` con Graphviz y guardar la imagen en `img/` | Pendiente de verificar |

