// RC4 — Sin falsos positivos: si el código es correcto (esperado vacío), aprueba y no inventa hallazgos.
module.exports = (output, context) => {
  if (String(context.vars.esperado || '').trim() !== '') return { pass: true, score: 1, reason: 'No aplica: el código tiene defectos' };
  let r;
  try { r = JSON.parse(output); } catch (e) { return { pass: false, score: 0, reason: 'La salida no es JSON' }; }
  const ok = r.veredicto === 'aprobado' && (r.hallazgos || []).length === 0;
  return { pass: ok, score: ok ? 1 : 0, reason: ok ? 'Aprueba el código correcto' : 'Inventa ' + (r.hallazgos || []).length + ' hallazgo(s)' };
};
