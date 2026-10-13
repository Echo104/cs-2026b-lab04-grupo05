# Historia de usuario crítica — VotoEPIS

```
HU-03: Como estudiante votante, quiero emitir mi voto en secreto para elegir a mis delegados sin que se sepa por quién voté.
```

Requisitos de [drivers.md](../architecture/drivers.md) que cubre: RF-03 (voto secreto, una sola vez) y RF-08 (comprobante de participación). Atributos de calidad: QA-01 (un voto por estudiante), QA-02 (reintento sin duplicar) y QA-03 (p95 ≤ 3 s).

## Criterios de aceptación
- **Dado** un estudiante autenticado que figura en el padrón y no ha participado, y una elección ABIERTA, **cuando** emite su voto por una lista, **entonces** el voto se guarda en la urna sin su identidad, el estudiante queda registrado como participante y recibe un comprobante de participación (en pantalla y por correo).
- **Dado** un estudiante que ya participó en la elección, **cuando** intenta votar otra vez (incluso con dos envíos simultáneos), **entonces** el sistema rechaza el segundo voto y la urna conserva un solo voto suyo.
- **Dado** una elección que no está ABIERTA (aún configurada o ya cerrada), **cuando** un estudiante intenta votar, **entonces** el sistema rechaza el voto y no registra nada.
- **Dado** un fallo transitorio de la base de datos al registrar el voto, **cuando** el sistema reintenta (máximo 3 veces), **entonces** el voto queda registrado una sola vez.
