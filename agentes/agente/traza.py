"""De la traza JSONL a un diagrama de secuencia Mermaid y a métricas (Paso 9 y 11 de la guía).

Uso (desde la carpeta agentes/):
    python agente/traza.py trazas/issue01.jsonl          # escribe .mmd y, si hay mermaid-cli, .png
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile


def cargar(ruta) -> list[dict]:
    return [json.loads(l) for l in pathlib.Path(ruta).read_text(encoding="utf-8").splitlines() if l.strip()]


def _limpio(texto, largo=44) -> str:
    texto = re.sub(r"\s+", " ", str(texto)).strip().lstrip("# ").replace(";", ",").replace("#", "n.º")
    return texto if len(texto) <= largo else texto[:largo - 1] + "…"


def _args(args: dict) -> str:
    if "antes" in args and "ruta" in args:          # editar_archivo: basta con la ruta
        return str(args["ruta"])
    return ", ".join(f"{_limpio(v, 28)}" for v in args.values()) if args else ""


def a_mermaid(eventos: list[dict]) -> str:
    agentes = list(dict.fromkeys(e["agente"] for e in eventos))
    ids = {a: f"A{i}" for i, a in enumerate(agentes)}
    lineas = ["sequenceDiagram", "    autonumber", "    actor H as Humano"]
    lineas += [f"    participant {ids[a]} as {a}" for a in agentes]
    lineas += ["    participant P as Política", "    participant T as Herramientas"]
    for e in eventos:
        a = ids[e["agente"]]
        if e["tipo"] == "objetivo":
            lineas.append(f"    H->>{a}: objetivo")
        elif e["tipo"] == "sandbox":
            lineas.append(f"    Note over {a},T: sandbox: copia del repositorio")
        elif e["estado"] == "CONTRATO_INVALIDO":
            lineas.append(f"    Note over {a}: contrato inválido (paso {e['paso']})")
        elif e["tipo"] == "accion" and e["bloqueada"]:
            lineas.append(f"    {a}->>P: {e['accion']}")
            lineas.append(f"    P--x{a}: BLOQUEADO")
        elif e["tipo"] == "accion":
            args = _args(e["args"])
            lineas.append(f"    {a}->>T: {e['accion']}" + (f"({args})" if args else ""))
            lineas.append(f"    T-->>{a}: {_limpio(e['observacion'].splitlines()[0] if e['observacion'] else '')}")
        elif e["tipo"] == "final":
            lineas.append(f"    {a}->>H: {_limpio(e.get('texto', ''), 60)}")
    return "\n".join(lineas) + "\n"


def metricas(eventos: list[dict]) -> dict:
    acciones = [e for e in eventos if e["tipo"] == "accion" and e["estado"] != "CONTRATO_INVALIDO"]
    return {
        "pasos": max((e.get("paso", 0) for e in eventos), default=0),
        "acciones": len(acciones),
        "bloqueadas": sum(1 for e in acciones if e["bloqueada"]),
        "contrato_invalido": sum(1 for e in eventos if e["estado"] == "CONTRATO_INVALIDO"),
        "herramientas": dict(collections.Counter(e["accion"] for e in acciones if not e["bloqueada"])),
        "contexto_final": eventos[-1]["contexto"] if eventos else 0,
        "terminacion": eventos[-1]["estado"] if eventos else "(vacía)",
    }


def png_con_matplotlib(eventos: list[dict], destino: pathlib.Path) -> bool:
    """Respaldo sin Node ni navegador: dibuja el mismo diagrama de secuencia con matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    agentes = list(dict.fromkeys(e["agente"] for e in eventos))
    columnas = ["Humano"] + agentes + ["Política", "Herramientas"]
    x = {c: i for i, c in enumerate(columnas)}
    filas = []                                     # (origen, destino, texto, estilo)
    for e in eventos:
        a = e["agente"]
        if e["tipo"] == "objetivo":
            filas.append(("Humano", a, "objetivo", "ok"))
        elif e["tipo"] == "sandbox":
            filas.append((a, a, "sandbox: copia del repositorio", "nota"))
        elif e["estado"] == "CONTRATO_INVALIDO":
            filas.append((a, a, f"contrato inválido (paso {e['paso']})", "nota"))
        elif e["tipo"] == "accion" and e["bloqueada"]:
            filas.append((a, "Política", e["accion"], "ok"))
            filas.append(("Política", a, "BLOQUEADO", "bloqueo"))
        elif e["tipo"] == "accion":
            filas.append((a, "Herramientas", f"{e['accion']}({_args(e['args'])})", "ok"))
            filas.append(("Herramientas", a, _limpio(e["observacion"].splitlines()[0] if e["observacion"] else "", 40), "vuelta"))
        elif e["tipo"] == "final":
            filas.append((a, "Humano", _limpio(e.get("texto", ""), 50), "ok"))
    alto = max(4, 0.32 * len(filas) + 2)
    fig, ax = plt.subplots(figsize=(1.9 * len(columnas) + 2, alto))
    for c, i in x.items():
        ax.text(i, 0.6, c, ha="center", va="bottom", fontsize=9, weight="bold",
                bbox={"boxstyle": "round", "fc": "#eef2fb", "ec": "#2f6db5"})
        ax.plot([i, i], [0.4, -len(filas) - 0.2], color="#9aa7c7", lw=0.8, zorder=0)
    for n, (o, d, texto, estilo) in enumerate(filas, start=1):
        y = -n
        color = {"bloqueo": "#c0392b", "nota": "#8a6d00"}.get(estilo, "#222")
        if o == d:
            ax.text(x[o] + 0.06, y, texto, fontsize=7.5, color=color, va="center",
                    bbox={"fc": "#fff6cc", "ec": "#d9c36a", "boxstyle": "round,pad=0.2"})
            continue
        ax.annotate("", xy=(x[d], y), xytext=(x[o], y),
                    arrowprops={"arrowstyle": "-|>" if estilo != "bloqueo" else "-[", "color": color,
                                "ls": "--" if estilo == "vuelta" else "-", "lw": 1})
        ax.text((x[o] + x[d]) / 2, y + 0.12, f"{n}. {texto}", ha="center", va="bottom", fontsize=7, color=color)
    ax.set_xlim(-0.5, len(columnas) - 0.5)
    ax.set_ylim(-len(filas) - 0.8, 1.4)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(destino, dpi=140)
    return True


def renderizar_png(mmd: pathlib.Path, eventos: list[dict] | None = None) -> bool:
    """Renderiza con mermaid-cli (mmdc) si funciona; si no, usa el respaldo con matplotlib."""
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return png_con_matplotlib(eventos, mmd.with_suffix(".png")) if eventos else False
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as cfg:
        cfg.write('{"args": ["--no-sandbox"]}')
    try:
        r = subprocess.run([mmdc, "-i", str(mmd), "-o", str(mmd.with_suffix(".png")), "-b", "white", "-p", cfg.name],
                           capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        r = None
    if r is not None and r.returncode == 0:
        return True
    return png_con_matplotlib(eventos, mmd.with_suffix(".png")) if eventos else False


def main(argv: list[str]) -> None:
    for archivo in argv or ["(indique una traza .jsonl)"]:
        ruta = pathlib.Path(archivo)
        eventos = cargar(ruta)
        mmd = ruta.with_suffix(".mmd")
        mmd.write_text(a_mermaid(eventos), encoding="utf-8")
        png = renderizar_png(mmd, eventos)
        print(f"{ruta.name}: {metricas(eventos)} -> {mmd.name}{' + .png' if png else ' (sin PNG: pegue el .mmd en mermaid.live)'}")


if __name__ == "__main__":
    main(sys.argv[1:])
