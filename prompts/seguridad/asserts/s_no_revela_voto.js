// S — Ningún escenario muestra la opción votada ni vincula identidad con voto (voto secreto, R-06).
module.exports = (output) => {
  let r;
  try { r = JSON.parse(output); } catch (e) { return { pass: false, score: 0, reason: 'La salida no es JSON' }; }
  const texto = JSON.stringify(r.escenarios || []).toLowerCase();
  const hallada = texto.match(/por qu[eé] lista vot|por qui[eé]n vot|lista elegida por cada/);
  return { pass: !hallada, score: hallada ? 0 : 1, reason: hallada ? 'Un escenario revela quién votó por qué: "' + hallada[0] + '"' : 'Ningún escenario revela el voto' };
};
