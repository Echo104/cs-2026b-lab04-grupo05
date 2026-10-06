# Bitácora de uso de IA — VotoEPIS

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 05/10 | Claude | Prompt 1 adaptado: 3 alternativas de estilo para VotoEPIS (3 developers, 1 mes, un servidor) | Monolito en capas, monolito modular y microservicios; recomendó el monolito modular | Se contrastó cada alternativa con R-01, R-02 y R-03; microservicios excede equipo, plazo y presupuesto | Aceptada |
| 2 | 05/10 | Claude | Prompt 2 (abogado del diablo) sobre el monolito modular | Riesgos: límites entre módulos que se rompen, falla única, correlación voto–votante por registros u orden de inserción, administrador con acceso total a la base de datos | Se incorporaron mitigaciones: import-linter (ADR-001), roles y esquemas separados, urna sin marcas de tiempo (ADR-002). El riesgo del administrador no se elimina y se declara en el ADR-002 | Corregida |
| 3 | 05/10 | Claude | Pesos, puntajes y total ponderado de la matriz | Totales 3,90 / 4,05 / 2,95 | Recalculados con `matriz_grafico.py`: coinciden; los pesos suman 100 %. Se añadió análisis de sensibilidad (la decisión cambia si seguridad baja a 15 % y entrega sube a 35 %) | Aceptada |
| 4 | 05/10 | Claude | Autenticación del votante con correo institucional | Supuso que la universidad ofrece inicio de sesión federado con la cuenta institucional | No hay evidencia de ello en el caso; se eligió código OTP por correo (ADR-003). ☐ Confirmar con la oficina de TI qué mecanismo permite la UNSA | Corregida |
| 5 | 05/10 | Claude | Recibo verificable por votante para la auditoría | Se evaluó como alternativa en el ADR-002 | Permitiría demostrar a un tercero cómo se votó (compra o coerción) y choca con R-06 | Rechazada |
| 6 | 05/10 | Claude | Código Mermaid y Python Diagrams a partir de la matriz y los ADR | `arquitectura.mmd`, `despliegue.py` | Validar `arquitectura.mmd` en mermaid.live y GitHub; ejecutar `despliegue.py` con Graphviz y guardar la imagen en `img/` | Pendiente de verificar |

## Anexo: prompts


### Entrada 1 — Generación de alternativas (Prompt 1 adaptado)
```
Actúa como arquitecto de software senior con experiencia en sistemas para instituciones educativas.
Contexto: plataforma "VotoEPIS" para la elección digital de delegados estudiantiles de la EPIS (UNSA).
Los estudiantes votan una sola vez y en secreto; el comité electoral gestiona el padrón y publica
resultados y acta; un auditor verifica el conteo de forma independiente. ~300 votantes en los primeros 10 minutos.
Restricciones: 3 developers con experiencia en Python/Django y PostgreSQL, un solo servidor de bajo costo,
MVP en 1 mes, protección de datos personales (Ley 29733).
Tarea: propón 3 alternativas de estilo arquitectónico. Para cada una indica fortalezas, debilidades,
riesgos y qué atributos de calidad favorece o penaliza.
Formato: tabla comparativa en Markdown y, al final, tu recomendación justificada.
No inventes APIs ni capacidades de servicios; si no estás seguro, indícalo.
```

### Entrada 2 — Crítica adversarial (Prompt 2)
```
Ahora actúa como "abogado del diablo". Critica duramente la alternativa que recomendaste: ¿qué supuestos
no se cumplen con nuestras restricciones?, ¿qué podría fallar en producción?, ¿qué costo oculto tiene?
Enumera los 5 riesgos más graves y, para cada uno, una táctica arquitectónica de mitigación.
```

### Entrada 3 — Matriz de decisión ponderada
```
Actúa como arquitecto de software revisor.
Contexto: elegimos entre A (monolito en capas), B (monolito modular) y C (microservicios) para VotoEPIS.
Restricciones: los pesos deben sumar exactamente 100 % y cada uno debe justificarse con un driver
(R-01 plazo 1 mes, R-02 equipo de 3, R-03 presupuesto bajo, QA-01 y QA-04 seguridad, QA-02 fiabilidad).
Criterios y pesos propuestos: Seguridad e integridad 30 %, Tiempo de entrega 20 %, Costo operativo 15 %,
Simplicidad operativa 15 %, Fiabilidad 10 %, Modificabilidad 10 %.
Tarea: (1) puntúa A, B y C de 1 a 5 en cada criterio con una justificación de una línea;
(2) calcula el total ponderado mostrando la fórmula Σ(peso × puntaje) paso a paso;
(3) haz un análisis de sensibilidad: ¿qué cambio en los pesos haría ganar a otra alternativa?
Formato: tabla Markdown con los puntajes, luego los cálculos, luego la sensibilidad.
Si un puntaje depende de un supuesto, indícalo.
```

### Entrada 4 — Autenticación del votante
```
Actúa como arquitecto de seguridad con experiencia en sistemas universitarios.
Contexto: en VotoEPIS solo votan los estudiantes del padrón (importado como CSV) y cada uno debe acreditarse
con su correo institucional. No tenemos acceso al sistema académico.
Restricciones: 3 developers con Python/Django, MVP en 1 mes, sin servicios de pago.
Tarea: propón 3 mecanismos de autenticación y compáralos en seguridad, esfuerzo y dependencias externas.
Indica explícitamente cuáles dependen de una aprobación o capacidad de la universidad que yo debería
confirmar. No asumas que la universidad ofrece inicio de sesión federado; si lo supones, dilo.
Formato: tabla comparativa y una recomendación breve.
```

### Entrada 5 — Recibo verificable por votante
```
Actúa como auditor de sistemas de votación.
Contexto: VotoEPIS debe garantizar voto secreto (R-06) y conteo verificable de forma independiente (QA-04).
Un compañero propone darle a cada votante un recibo para comprobar que su voto fue contado.
Tarea: evalúa esa propuesta frente al voto secreto: ¿permite compra o coerción de votos? ¿existe una
variante que permita verificar la inclusión sin revelar la opción votada y que sea viable para 3 developers en 1 mes?
Formato: ventajas, riesgos, y una recomendación (adoptar, rechazar o posponer) con una frase de justificación.
No inventes capacidades de librerías ni protocolos; si no estás seguro, indícalo.
```

### Entrada 6 — Código de diagramas (Mermaid y Python Diagrams)
```
Actúa como arquitecto de software que documenta con Diagram as Code.
Contexto: la arquitectura elegida para VotoEPIS es un monolito modular con 5 módulos (Elección y padrón,
Autenticación, Votación, Conteo y resultados, Auditoría), PostgreSQL con dos esquemas (padron y urna)
con roles distintos, y un servidor de correo externo para enviar códigos OTP.
Tarea 1: genera el código Mermaid (flowchart TB) con mínimo 2 actores, todos los módulos, el almacenamiento
de datos, mínimo 1 servicio externo y la dirección de las dependencias; usa subgraph para agrupar.
Tarea 2: genera un script de Python Diagrams (vista de despliegue) con usuarios, servidor, aplicación,
base de datos, servicio externo y monitoreo; usa Cluster y Edge(label=...), y guarda la imagen en img/.
Formato: dos bloques de código, sin explicaciones largas. Si dudas de que un ícono o clase exista en la
librería diagrams, indícalo en lugar de inventarlo.
```
