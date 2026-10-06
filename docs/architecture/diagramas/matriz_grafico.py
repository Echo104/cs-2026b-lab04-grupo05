"""Calcula los totales ponderados de matriz-decision.md y genera el gráfico (E2, opcional).
Ejecución: python matriz_grafico.py  ->  img/matriz-decision.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
criterios = ["Seguridad e\nintegridad (30%)", "Tiempo de\nentrega (20%)", "Costo\noperativo (15%)",
             "Simplicidad\noperativa (15%)", "Fiabilidad (10%)", "Modificabilidad\n(10%)"]
pesos = [0.30, 0.20, 0.15, 0.15, 0.10, 0.10]
assert abs(sum(pesos) - 1) < 1e-9, "Los pesos deben sumar 100 %"
alternativas = {
    "Monolito en capas":  ([3, 5, 5, 5, 3, 2], "#9E9E9E"),
    "Monolito modular":   ([4, 4, 5, 4, 3, 4], "#2E7D32"),
    "Microservicios":     ([4, 2, 2, 1, 4, 5], "#2B4F9E"),
}
totales = {n: round(sum(p * s for p, s in zip(pesos, v)), 2) for n, (v, _) in alternativas.items()}
print(totales)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.6, 1]})
ancho = 0.26
for i, (n, (v, c)) in enumerate(alternativas.items()):
    ax1.bar([x + (i - 1) * ancho for x in range(len(criterios))], v, ancho, label=n, color=c)
ax1.set_xticks(range(len(criterios))); ax1.set_xticklabels(criterios, fontsize=8)
ax1.set_ylabel("Puntaje (1-5)"); ax1.set_ylim(0, 5.5); ax1.set_title("Puntaje por criterio"); ax1.legend(fontsize=8, ncol=3)
nombres = list(totales)[::-1]
ax2.barh(nombres, [totales[n] for n in nombres], color=[alternativas[n][1] for n in nombres])
for y, n in enumerate(nombres):
    ax2.text(totales[n] + 0.05, y, f"{totales[n]:.2f}".replace(".", ","), va="center", fontweight="bold")
ax2.set_xlim(0, 5); ax2.set_title("Puntaje ponderado total")
for a in (ax1, ax2):
    a.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "img", "matriz-decision.png"), dpi=150)
