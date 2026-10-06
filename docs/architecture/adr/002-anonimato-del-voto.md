# ADR-002: Separar identidad y voto en dos esquemas de PostgreSQL

- Estado: Aceptado
- Fecha: 2026-10-05
- Decisores: <integrantes del grupo>

## Contexto
El voto debe ser secreto (R-06) y a la vez cada estudiante solo puede votar una vez (QA-01, RF-03). El auditor necesita recontar los votos de forma independiente (QA-04, RF-06). El padrón contiene datos personales protegidos por la Ley 29733 (R-04). Hay que registrar quién participó sin registrar qué votó.

## Alternativas consideradas
1. Una tabla única `voto(estudiante_id, opción)` con restricción UNIQUE: garantiza un voto por estudiante, pero vincula identidad y voto; incumple R-06.
2. Dos esquemas de PostgreSQL con roles distintos: `padron.participacion(estudiante_id, elección_id)` con UNIQUE y `urna.voto(id UUID aleatorio, elección_id, opción)`, sin clave foránea ni marca de tiempo entre ambos, escritos en una sola transacción.
3. Votos cifrados con firma ciega o mixnet (verificabilidad criptográfica de extremo a extremo): mayor garantía, pero fuera del alcance de 3 developers en 1 mes (R-01, R-02).
4. Recibo verificable por votante: se descartó porque permitiría demostrar a un tercero cómo se votó (compra o coerción de votos) y choca con R-06.

## Decisión
Usaremos la alternativa 2. La restricción UNIQUE en `padron.participacion` evita el doble voto aun con envíos simultáneos (QA-01). La urna se exporta barajada, sin identificadores de orden, junto con su huella SHA-256, para el recuento independiente del auditor (QA-04). Se desactiva el registro de consultas SQL con valores y los roles de base de datos solo tienen los permisos de su esquema.

## Consecuencias
- Positivas: el secreto del voto se apoya en el diseño de datos y no solo en la disciplina del código; el doble voto es imposible a nivel de base de datos; el auditor puede recontar con un script simple.
- Negativas / riesgos: un administrador con acceso total al servidor podría intentar correlacionar votos y participantes (orden físico de inserción, registros del sistema); se mitiga con UUID aleatorios, sin marcas de tiempo en la urna, acceso restringido y registrado, pero el riesgo no desaparece. Tampoco hay verificación individual del voto por parte del estudiante. Ambos puntos se declaran en el acta.
