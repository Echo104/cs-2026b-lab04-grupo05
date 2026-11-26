// S — Los textos de la respuesta siguen en español aunque los datos pidan otro idioma.
module.exports = (output) => {
  let r;
  try { r = JSON.parse(output); } catch (e) { return { pass: false, score: 0, reason: 'La salida no es JSON' }; }
  const texto = JSON.stringify([r.preguntas || [], r.escenarios || []]);
  const hallada = texto.match(/\b(the|and|should|when|given|then|sees|with)\b/i);
  return { pass: !hallada, score: hallada ? 0 : 1, reason: hallada ? 'Texto en inglés: "' + hallada[0] + '"' : 'Texto en español' };
};
