# ADR-003: Autenticar con un código de un solo uso enviado al correo institucional

- Estado: Aceptado
- Fecha: 2026-10-05
- Decisores: <integrantes del grupo>

## Contexto
Solo pueden votar los estudiantes del padrón (RF-02) y cada uno debe poder acreditarse con su identidad institucional (R-05). No hay acceso al sistema académico (R-05) y el equipo tiene 1 mes y poca experiencia en seguridad de identidad (R-01, R-02). Un acceso suplantado permitiría votar por otra persona, lo que afecta QA-01.

## Alternativas consideradas
1. Inicio de sesión federado (OAuth 2.0 / OIDC) con la cuenta institucional: la mejor opción si la universidad lo habilita, pero depende de una aprobación externa que no tenemos confirmada.
2. Usuario y contraseña propios: obliga a almacenar y proteger contraseñas y aumenta la superficie de ataque.
3. Código de un solo uso (OTP) enviado al correo institucional, verificado contra el padrón.

## Decisión
Usaremos la alternativa 3: el estudiante ingresa su correo, el sistema verifica que figura en el padrón y envía un código de 6 dígitos que vence a los 10 minutos, con máximo 5 intentos y un límite de solicitudes por correo. El envío se encapsula en un adaptador para poder migrar a OAuth/OIDC (alternativa 1) sin tocar los demás módulos.

## Consecuencias
- Positivas: no se guardan contraseñas; reutiliza una identidad institucional existente; el adaptador permite cambiar el mecanismo (R-02, modificabilidad).
- Negativas / riesgos: depende de que el servidor de correo entregue los códigos a tiempo (se probará con la carga de QA-03) y de la seguridad del buzón del estudiante; si un buzón está comprometido, se puede suplantar a ese votante. Se debe confirmar con la oficina de TI que los correos institucionales reciben mensajes del servidor elegido.
