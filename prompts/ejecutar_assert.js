// Ejecuta aserciones JavaScript de promptfoo (archivos file://...) FUERA de promptfoo.
// Lo usa evaluar_local.py para repetir la evaluación sin red. Entrada (stdin): lista JSON de
// {archivo, output, vars}. Salida (stdout): lista JSON de {pass, score, reason}.
const fs = require('fs');

const trabajos = JSON.parse(fs.readFileSync(0, 'utf8'));
const resultados = trabajos.map((t) => {
  try {
    const fn = require(t.archivo);
    const r = fn(t.output, { vars: t.vars, config: {} });
    if (typeof r === 'boolean') return { pass: r, score: r ? 1 : 0, reason: '' };
    if (typeof r === 'number') return { pass: r > 0, score: r, reason: '' };
    return { pass: !!r.pass, score: r.score, reason: r.reason || '' };
  } catch (e) {
    return { pass: false, score: 0, reason: 'Error en la aserción: ' + e.message };
  }
});
process.stdout.write(JSON.stringify(resultados));
