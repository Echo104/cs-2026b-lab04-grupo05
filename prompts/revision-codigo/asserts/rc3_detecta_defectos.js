// RC3 (aserción clave) — Sin falsos "todo está bien": cada defecto esperado (regla y rango de líneas,
// variable `esperado`, p. ej. "S1@5-5;S6@5-5") aparece como hallazgo y el veredicto es "con_hallazgos".
module.exports = (output, context) => {
  const esperado = String(context.vars.esperado || '').split(';').filter(Boolean);
  if (esperado.length === 0) return { pass: true, score: 1, reason: 'No aplica: el código es correcto' };
  let r;
  try { r = JSON.parse(output); } catch (e) { return { pass: false, score: 0, reason: 'La salida no es JSON' }; }
  const hallazgos = r.hallazgos || [];
  const faltan = esperado.filter((e) => {
    const [regla, rango] = e.split('@');
    const [desde, hasta] = rango.split('-').map(Number);
    return !hallazgos.some((h) => h.regla === regla && h.linea >= desde && h.linea <= hasta);
  });
  const ok = faltan.length === 0 && r.veredicto === 'con_hallazgos';
  return { pass: ok, score: ok ? 1 : 0, reason: ok ? 'Detecta todos los defectos esperados' : 'No detecta: ' + (faltan.join(', ') || 'veredicto incorrecto') };
};
