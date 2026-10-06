# ADR-001: Adoptar un monolito modular para el MVP de VotoEPIS

- Estado: Aceptado
- Fecha: 2026-10-05
- Decisores: <integrantes del grupo>

## Contexto
VotoEPIS debe estar en producción en 1 mes (R-01), con 3 developers que dominan Python/Django (R-02) y un único servidor de bajo costo (R-03). El atributo crítico es la seguridad: un voto por estudiante (QA-01), voto secreto (R-06) y conteo verificable (QA-04). La carga esperada es baja (QA-03: ≈ 300 votantes en 10 minutos), por lo que la escalabilidad no es el driver dominante. Requisitos relacionados: RF-03, RF-04 y RF-06.

## Alternativas consideradas
1. Monolito en capas (3,90): rápido y simple, pero sin límites internos; el código de votación podría acceder a la identidad del votante, lo que pone en riesgo R-06.
2. Microservicios (2,95): buen aislamiento, pero 4 despliegues, varias bases de datos y un broker exceden la capacidad operativa del equipo y el plazo (R-01, R-02, R-03).
3. Monolito modular (4,05): elegido.

## Decisión
Usaremos un monolito modular en Django con 5 módulos (Elección y padrón, Autenticación, Votación, Resultados, Auditoría). Los módulos se comunican solo mediante interfaces públicas (servicios de aplicación) y el módulo Votación no importa nada del módulo Autenticación salvo el identificador de sesión. Las integraciones externas (correo) se implementan como adaptadores (puertos y adaptadores).

## Consecuencias
- Positivas: un solo despliegue y bajo costo (R-03); entrega en 1 mes (R-01); fronteras claras que protegen el voto secreto; los módulos pueden extraerse como servicios si en el futuro la carga lo exige.
- Negativas / riesgos: el equipo debe respetar los límites entre módulos (se usará import-linter en la CI); una falla grave afecta a todo el sistema (QA-02 se mitiga con reinicio automático y pruebas de recuperación); la diferencia con la alternativa en capas es pequeña (0,15), por lo que la decisión es sensible a los pesos de la matriz.
