## 1. Revisión con IA (Prompt IA 3)

| Regla | Hallazgo | Verificación del equipo | Estado |
|-------|----------|-------------------------|--------|
| C2 / entre diagramas | En [actividades-escrutinio-acta.puml](actividades-escrutinio-acta.puml) la elección pasa a ESCRUTADA antes del recuento del auditor. Si el auditor reporta una discrepancia, la elección queda en ESCRUTADA y el diagrama de estados no tiene una transición para revertirla o anularla | Es un hallazgo real: la guarda de `publicar()` solo exige acta firmada, y el acta no se firma si hay discrepancia, así que no se publica. Pero el estado queda sin salida | Corregido |
| C3 | Voto no está asociado a Participacion ni a Estudiante: «relación faltante» | Falso positivo confirmado: la ausencia de esta asociación es deliberada, conforme a R-06 y ADR-002. Relacionar directamente Voto con Estudiante permitiría identificar por quién votó cada estudiante, comprometiendo el secreto del voto. | Descartado: falso positivo justificado |
| C1 | `VotoController` y `Web de votación` reciben mensajes pero no existen en el diagrama de clases | La regla C1 se aplica a las clases del dominio y de los puertos; controlador y web pertenecen a la capa de presentación, fuera del alcance de la historia | Aceptado como limitación |
| C4 | `votacion` depende de `autenticacion` | Permitido por ADR-001 solo para el identificador de sesión; la dependencia está etiquetada así | Verificado |
