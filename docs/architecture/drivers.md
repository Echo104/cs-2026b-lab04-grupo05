# Drivers arquitectónicos — VotoEPIS

Plataforma web para la elección digital de delegados estudiantiles de la EPIS. Actores: estudiante votante, comité electoral y auditor.

> **Supuestos de carga (confirmar con el comité electoral):** padrón de ≈ 1 000 estudiantes; hasta 300 votantes en los primeros 10 minutos tras la apertura; elección abierta un solo día.

## 1. Requisitos funcionales clave
| ID    | Requisito                                                                         | Actor              | Prioridad |
|-------|-----------------------------------------------------------------------------------|--------------------|-----------|
| RF-01 | Cargar y administrar el padrón electoral (importación desde CSV)                  | Comité electoral   | Alta      |
| RF-02 | Autenticarse con el correo institucional y verificar que figura en el padrón      | Estudiante votante | Alta      |
| RF-03 | Emitir un voto secreto, una sola vez por elección                                 | Estudiante votante | Alta      |
| RF-04 | Realizar el conteo automático de votos al cierre de la elección                   | Comité electoral   | Alta      |
| RF-05 | Publicar los resultados y generar el acta de la elección                          | Comité electoral   | Alta      |
| RF-06 | Verificar el conteo de forma independiente (exportar urna anonimizada y huella)   | Auditor            | Alta      |
| RF-07 | Configurar la elección (candidatos o listas, fecha y hora de apertura y cierre)   | Comité electoral   | Media     |
| RF-08 | Mostrar comprobante de participación (sin revelar la opción votada)               | Estudiante votante | Media     |

## 2. Atributos de calidad (ordenados por prioridad)
1. **Seguridad (integridad y confidencialidad)** — atributo crítico: un voto por estudiante, voto secreto y conteo verificable; un solo fallo invalida la elección.
2. **Fiabilidad (disponibilidad y recuperabilidad)** — la ventana de votación es corta y fija; una caída no puede perder votos confirmados ni obligar a repetir la elección.
3. **Rendimiento (eficiencia de desempeño)** — la mayoría vota en los primeros minutos; una respuesta lenta provoca reintentos y envíos duplicados.
4. **Capacidad de interacción** — los votantes no son técnicos y el voto no se puede corregir; la interfaz debe evitar errores al votar.
5. **Modificabilidad** — cada ciclo electoral cambia candidatos, padrón y reglas; el equipo debe adaptarlos sin reescribir módulos.

## 3. Restricciones
| ID   | Tipo         | Restricción                                                                                              |
|------|--------------|----------------------------------------------------------------------------------------------------------|
| R-01 | Plazo        | MVP en producción en 1 mes                                                                               |
| R-02 | Equipo       | 3 developers con experiencia en Python/Django y PostgreSQL; sin experiencia en DevOps ni Kubernetes *(ajustar a los integrantes reales)* |
| R-03 | Presupuesto  | Bajo: un solo servidor (VPS o servidor de la universidad); cualquier servicio de pago debe justificarse  |
| R-04 | Normativa    | Ley 29733 de protección de datos personales: el padrón contiene datos personales y debe minimizarse y protegerse |
| R-05 | Tecnología   | La identidad se valida con el correo institucional contra el padrón; no hay acceso directo al sistema académico (el padrón llega como CSV) |
| R-06 | Dominio      | Voto secreto: ningún registro puede vincular la identidad del estudiante con la opción votada            |

## 4. Escenarios de atributos de calidad
| ID    | Atributo                    | Fuente                       | Estímulo                                                     | Entorno                          | Artefacto                  | Respuesta                                                                                         | Medida                                                      |
|-------|-----------------------------|------------------------------|--------------------------------------------------------------|----------------------------------|----------------------------|---------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| QA-01 | Seguridad (integridad)      | Estudiante autenticado       | Envía dos votos a la vez (doble clic o dos pestañas)         | Elección abierta, operación normal | Módulo Votación          | Registra solo el primer voto, rechaza el resto y deja constancia del intento                      | 0 votos duplicados en 100 pruebas de doble envío simultáneo |
| QA-02 | Fiabilidad                  | Fallo del servidor           | El proceso se reinicia en plena votación                     | Elección abierta, hora pico       | Aplicación y base de datos | El servicio se recupera; los votos confirmados persisten y quien no recibió confirmación puede reintentar sin duplicar | 0 votos confirmados perdidos; recuperación ≤ 5 min          |
| QA-03 | Rendimiento                 | 300 estudiantes              | Emiten su voto en los primeros 10 minutos tras la apertura   | Hora pico, operación normal       | Módulo Votación            | Confirma cada voto y muestra el comprobante de participación                                      | p95 del tiempo de respuesta ≤ 3 s                           |
| QA-04 | Seguridad (auditabilidad)   | Auditor                      | Solicita verificar el conteo tras el cierre                  | Elección cerrada                  | Módulo Auditoría           | Entrega la urna anonimizada, su huella SHA-256 y un script de recuento independiente              | Recuento independiente coincide 100 % con el oficial; ≤ 10 min para 1 000 votos |

> Los tres atributos distintos exigidos son Seguridad (QA-01), Fiabilidad (QA-02) y Rendimiento (QA-03); QA-04 desarrolla la auditabilidad del atributo crítico.
