"""Núcleo del agente: el bucle ReAct como máquina de estados (Figura 5 de la guía; ver
``diseno/estados.puml``). Cada transición queda registrada en una traza JSONL."""
from __future__ import annotations

import json
import pathlib
import time

from .contrato import validar_decision
from .modelos import TrayectoriaAgotada


class Agente:
    def __init__(self, nombre, modelo, herramientas, politica, objetivo, traza_archivo):
        self.nombre, self.modelo, self.h, self.politica = nombre, modelo, herramientas, politica
        self.traza_archivo = pathlib.Path(traza_archivo)
        self.historial = [{"role": "user", "content": objetivo}]        # memoria de corto plazo
        self.eventos: list[dict] = []                                  # traza
        self._t0 = time.perf_counter()

    def contexto(self) -> int:
        """Caracteres acumulados en el historial (cada llamada al modelo los vuelve a enviar)."""
        return sum(len(m["content"]) for m in self.historial)

    def _registrar(self, **campos) -> None:
        self.eventos.append({"agente": self.nombre, "t": round(time.perf_counter() - self._t0, 3),
                             "contexto": self.contexto(), **campos})

    def registrar_preparacion(self, texto: str) -> None:
        """Estado PREPARANDO_SANDBOX: la copia aislada del repositorio ya está lista."""
        self._registrar(tipo="sandbox", estado="PREPARANDO_SANDBOX", texto=texto)

    def ejecutar(self) -> str:
        self._t0 = time.perf_counter()
        self._registrar(tipo="objetivo", estado="INICIO", texto=self.historial[0]["content"][:300])
        conocidas = set(self.h.catalogo())
        for paso in range(1, self.politica.max_pasos + 2):
            try:
                d = self.modelo.decidir(self.historial)                  # DECIDIENDO
            except TrayectoriaAgotada as e:
                self._registrar(tipo="final", estado="SIN_DECISIONES", paso=paso, texto=str(e))
                break
            self.historial.append({"role": "assistant",
                                   "content": d if isinstance(d, str) else json.dumps(d, ensure_ascii=False)})
            ok, motivo = validar_decision(d, conocidas)                  # VALIDANDO_CONTRATO
            if not ok:
                obs = f"ERROR DE CONTRATO: {motivo}. Responda solo con el JSON del protocolo."
                self._registrar(tipo="accion", estado="CONTRATO_INVALIDO", paso=paso, pensamiento=str(d)[:200],
                                accion="(ninguna)", args={}, observacion=obs, bloqueada=True)
            elif "final" in d:
                self._registrar(tipo="final", estado="FINALIZADO", paso=paso,
                                pensamiento=d["pensamiento"], texto=d["final"])
                break
            else:
                accion, args = d["accion"], d.get("args", {})
                veredicto = self.politica.evaluar(accion, args, paso)    # EVALUANDO_POLITICA
                if veredicto.permitido:
                    try:
                        obs = str(getattr(self.h, accion)(**args))       # EJECUTANDO
                    except Exception as e:                               # el error también es una observación
                        obs = f"ERROR: {type(e).__name__}: {e}"
                    self.historial.append({"role": "user", "content": f"Observación: {obs}"})  # OBSERVANDO
                    self._registrar(tipo="accion", estado="OBSERVANDO", paso=paso, pensamiento=d["pensamiento"],
                                    accion=accion, args=args, observacion=obs[:600], bloqueada=False)
                    continue
                obs = f"BLOQUEADO POR LA POLÍTICA: {veredicto.motivo}"
                limite = "máximo" in veredicto.motivo
                self._registrar(tipo="accion", estado="LIMITE_ALCANZADO" if limite else "BLOQUEADO", paso=paso,
                                pensamiento=d["pensamiento"], accion=accion, args=args, observacion=obs, bloqueada=True)
                if limite:
                    break
            self.historial.append({"role": "user", "content": f"Observación: {obs}"})  # -> DECIDIENDO
        self.traza_archivo.parent.mkdir(parents=True, exist_ok=True)
        with open(self.traza_archivo, "w", encoding="utf-8") as f:
            for e in self.eventos:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        return self.eventos[-1].get("texto", "(sin respuesta final)")
