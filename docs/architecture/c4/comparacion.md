# Comparación (E4 y E6)

## E4. Secuencia UML frente a vista dinámica C4
La secuencia UML de [secuencia-emitir-voto.puml](../../design/secuencia-emitir-voto.puml) muestra el detalle de las operaciones (`estaAbierta(ahora)`, `registrar(participacion, voto)`), los mensajes de retorno, las ramas de error (elección cerrada, participación duplicada), el reintento de hasta 3 veces y el envío asíncrono del comprobante. La vista dinámica `EmitirVoto` solo numera 6 llamadas entre componentes, contenedores y sistemas externos, sin retornos, ramas ni parámetros. En cambio, es la única que muestra a la vez la base del padrón, la urna y el servidor de correo como elementos del sistema, y que el módulo Votación consulta primero la sesión (paso 2); la secuencia da por hecho que el identificador del estudiante ya llega. La secuencia sirve a quien implementa o prueba el flujo; la vista dinámica, al equipo técnico, al docente y a quien necesita entender quién colabora con quién sin leer el código.

## E6. Diagrama escrito a mano frente a modelo exportado
| Aspecto | Escrito a mano ([contexto-manual.puml](contexto-manual.puml)) | Modelo exportado ([workspace.dsl](workspace.dsl)) |
|---------|-----------------------------------------------------------------|----------------------------------------------------|
| Tamaño | 20 líneas para 1 vista | 138 líneas para las 5 vistas (más estilos) |
| Errores encontrados | macros mal escritas , flechas sin etiqueta, etc | Un validador local halló 0 identificadores inexistentes; la revisión de etiquetas halló 1 flecha cuya etiqueta no coincidía con su dirección (API → Monitoreo). |
| Si cambia el nombre de «VotoEPIS» | Hay que editar 2 lugares del diagrama de contexto, y los mismos nombres en cada diagrama que se dibuje aparte | Se edita el nombre del sistema una vez en el DSL y se vuelven a exportar las vistas |
| Si cambia el nombre del contenedor «API VotoEPIS» | No aparece en el diagrama de contexto, pero habría que corregirlo a mano en cada diagrama que lo muestre | Se edita 1 vez en el DSL; el contenedor aparece en 4 de las 5 vistas (contenedores, componentes, dinámica y despliegue) y todas se actualizan |

Conclusión: para un solo diagrama simple, escribirlo a mano es rápido; con varias vistas del mismo modelo, un modelo único evita inconsistencias entre ellas.
