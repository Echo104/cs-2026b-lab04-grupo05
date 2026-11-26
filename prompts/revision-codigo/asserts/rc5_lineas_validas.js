// RC5 — Toda línea citada existe en el código recibido (1..lineas).
module.exports = (output, context) => {
  let r;
  try { r = JSON.parse(output); } catch (e) { return { pass: false, score: 0, reason: 'La salida no es JSON' }; }
  const maximo = Number(context.vars.lineas);
  const malas = (r.hallazgos || []).filter((h) => !(h.linea >= 1 && h.linea <= maximo));
  return { pass: malas.length === 0, score: malas.length === 0 ? 1 : 0, reason: malas.length ? 'Líneas fuera de rango: ' + malas.map((h) => h.linea) : 'Líneas válidas' };
};
