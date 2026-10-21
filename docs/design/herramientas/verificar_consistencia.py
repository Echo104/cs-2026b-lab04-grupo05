"""Verificación automática de las reglas de consistencia C1-C4 (E7).

Ejecución (desde la raíz del repositorio): python docs/design/herramientas/verificar_consistencia.py
C3 (multiplicidades) se comprueba solo de forma sintáctica; su coherencia con el negocio se revisa a mano.
C5 (lenguaje del dominio) también es revisión humana.
"""
import re
import sys
from comun import DESIGN, leer_clases_puml

clases = leer_clases_puml()
ok = True


def informe(regla: str, estado: bool, detalle: str) -> None:
    global ok
    ok &= estado
    print(f"[{'OK ' if estado else 'FALLA'}] {regla}: {detalle}")


# C1: mensajes de la secuencia -> operaciones de la clase receptora
seq = (DESIGN / "secuencia-emitir-voto.puml").read_text(encoding="utf-8")
alias = {m.group(2): m.group(1).split("\\n")[0] for m in re.finditer(r'participant "([^"]+)" as (\w+)', seq)}
revisados, sin_clase, fallos = 0, set(), []
for m in re.finditer(r"^\s*(\w+)\s+(->>?)\s+(\w+)\s*:\s*(\w+)\(", seq, re.M):
    destino, op = alias.get(m.group(3)), m.group(4)
    if destino not in clases:
        sin_clase.add(destino)
        continue
    revisados += 1
    if op not in clases[destino]["ops"]:
        fallos.append(f"{destino}.{op}()")
informe("C1", not fallos, f"{revisados} mensajes verificados contra clases.puml; "
        f"sin operación: {fallos or 'ninguno'}; receptores sin clase (capa de presentación): {sorted(sin_clase)}")

# C2: transiciones de estados -> operaciones de Eleccion y estados = enum
est = (DESIGN / "estados-eleccion.mmd").read_text(encoding="utf-8")
trans = re.findall(r"^\s*(\[\*\]|\w+)\s+-->\s+(\[\*\]|\w+)\s*:\s*(\w+)\(", est, re.M)
sin_op = [f"{o}->{d}: {op}()" for o, d, op in trans if op not in clases["Eleccion"]["ops"]]
informe("C2", not sin_op, f"{len(trans)} transiciones con operación; sin operación en Eleccion: {sin_op or 'ninguna'}")
estados = {x for t in trans for x in t[:2]} - {"[*]"}
enum = set(clases["EstadoEleccion"]["valores"])
informe("C2 (estados = enumeración)", estados == enum, f"diagrama {sorted(estados)} vs enum {sorted(enum)}")
con_salida = {o for o, _, _ in trans if o != "[*]"}
finales = {o for o, d, _ in trans if d == "[*]"}
sin_salida = estados - con_salida
informe("C2 (sin estados sin salida)", sin_salida <= {"PUBLICADA"}, f"sin salida salvo finales: {sorted(sin_salida) or 'ninguno'}")

# C3 (sintáctico): toda asociación/composición con multiplicidad en ambos extremos
cls_txt = (DESIGN / "clases.puml").read_text(encoding="utf-8")
asoc = [l for l in cls_txt.splitlines() if re.search(r'\w+ "[^"]+" (\*--|--|-->) "[^"]+" \w+', l)]
sueltas = [l for l in cls_txt.splitlines()
           if re.match(r"^\w+ (\*--|--|-->) \w+", l)]
informe("C3", not sueltas, f"{len(asoc)} asociaciones con multiplicidad en ambos extremos; sin multiplicidad: {sueltas or 'ninguna'}")

# C4: paquetes sin ciclos
paq = (DESIGN / "paquetes.puml").read_text(encoding="utf-8")
deps = {}
for a, b in re.findall(r"^\s*(\w+)\s+\.\.>\s+(\w+)", paq, re.M):
    deps.setdefault(a, set()).add(b)


def ciclo(nodo, camino, vistos):
    if nodo in camino:
        return camino[camino.index(nodo):] + [nodo]
    if nodo in vistos:
        return None
    vistos.add(nodo)
    for sig in deps.get(nodo, ()):
        c = ciclo(sig, camino + [nodo], vistos)
        if c:
            return c
    return None


vistos, encontrado = set(), None
for n in list(deps):
    encontrado = encontrado or ciclo(n, [], vistos)
informe("C4", encontrado is None, f"{sum(len(v) for v in deps.values())} dependencias entre {len(set(deps) | {x for v in deps.values() for x in v})} paquetes; ciclo: {' -> '.join(encontrado) if encontrado else 'ninguno'}")
sys.exit(0 if ok else 1)
