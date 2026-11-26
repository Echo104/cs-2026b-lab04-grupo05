// RC2 — El veredicto es coherente con los hallazgos: "aprobado" si y solo si no hay hallazgos.
module.exports = (output) => {
  let r;
  try { r = JSON.parse(output); } catch (e) { return { pass: false, score: 0, reason: 'La salida no es JSON' }; }
  const hallazgos = (r.hallazgos || []).length;
  const ok = (r.veredicto === 'aprobado') === (hallazgos === 0);
  return { pass: ok, score: ok ? 1 : 0, reason: 'veredicto=' + r.veredicto + ', hallazgos=' + hallazgos };
};
