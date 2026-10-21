# Revisión con la lista oficial del modelo C4 (E7)

## 1. Lista de revisión
| Grupo | Pregunta | ¿Cumple? | Evidencia |
|-------|----------|----------|-----------|
| General | ¿Cada vista tiene título, tipo y alcance? | Sí (5 de 5) | Cada vista tiene clave y descripción en el DSL; la CLI agrega el tipo y el alcance al título («Container View: VotoEPIS») |
| General | ¿Tiene leyenda? | Sí | La exportación a C4-PlantUML suele incluirla; verificar en las cinco imágenes |
| Elementos | ¿Cada elemento tiene nombre, tipo, descripción y, si corresponde, tecnología? | Sí | 16 de 16 elementos con descripción; 5 de 5 contenedores y 5 de 5 componentes con tecnología |
| Elementos | ¿Se entienden acrónimos, colores, formas y bordes? | Parcial | Hay estilos para persona, externo (gris), base de datos (cilindro) y navegador; las siglas SMTP, REST, SQL, TCP y CSV no se explican en ninguna leyenda. |
| Relaciones | ¿Cada flecha tiene etiqueta con su intención? | Sí | 33 de 33 relaciones con descripción, en verbo («Registra la participación», «Envía el comprobante») |
| Relaciones | ¿La etiqueta coincide con la dirección de la flecha? | Sí, tras una corrección | Se revisaron las 33. La flecha API → Monitoreo decía «Expone métricas de salud» (la API no es quien recibe); se cambió a «Envía métricas de salud» |
| Relaciones | ¿Se indica la tecnología o el protocolo? | Sí | Todas las relaciones entre contenedores, componentes→contenedor y hacia externos tienen protocolo (HTTPS, SQL/TCP, SMTP, HTTP). Las de persona → sistema y componente → componente no lo llevan, igual que en el ejemplo |
| Relaciones | ¿Se entienden los estilos de línea y las puntas de flecha? | Sí | Depende del render |

## 2. Hallazgos de la IA (Prompt IA 2)

| Vista | Hallazgo | Verificación del equipo |
|-------|----------|-------------------------|
| Contexto | «Faltan las tecnologías de las relaciones con las personas» | **Falso positivo esperado:** el nivel 1 no las exige y las relaciones persona → sistema describen la intención |
| Contenedores | «Los contenedores `padron` y `urna` son dos cajas, pero hay un solo servidor PostgreSQL» | Hallazgo válido de interpretación: son dos contenedores lógicos (ADR-002, dos esquemas con roles distintos) sobre un mismo servidor, que el despliegue deja ver | 
| Contenedores | «La relación API → Monitoreo usa HTTP, pero ningún ADR la documenta» | Cierto: sale de despliegue.py; el protocolo es un supuesto | 
| Despliegue | «El tamaño del servidor (2 vCPU, 4 GB) no está justificado» | Cierto: es un supuesto para ≈ 300 votantes en 10 minutos | 
