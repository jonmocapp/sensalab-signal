# -*- coding: utf-8 -*-
"""
AUTOPILOT — el motor autónomo local de The Signal. 100% Python, sin n8n.

Corre el pipeline completo (buscar -> acomodar -> redactar -> setear -> reconstruir) y luego
publica (deploy). En bucle o una sola pasada.

  python autopilot.py --once            una pasada y sale  (ideal para el Programador de Tareas)
  python autopilot.py --every 12        corre ya y luego cada 12h (demonio en primer plano)
  python autopilot.py --once --mock     prueba la plomería sin LLM ni publicar

Para dejarlo 100% autónomo en tu PC: registra `python autopilot.py --once` en el Programador de
Tareas de Windows (ver setup_autopilot.ps1) — así corre solo aunque reinicies, sin proceso vivo.
"""
from __future__ import annotations

import argparse
import time
import traceback
from datetime import datetime

import pipeline
import deploy


def cycle(limit: int | None = None, mock: bool = False, publish: bool = True) -> int:
    print(f"\n########## AUTOPILOT :: {datetime.now().strftime('%Y-%m-%d %H:%M')} ##########")
    rc = pipeline.run(mock=mock, limit=limit)
    if rc == 0 and publish and not mock:
        deploy.deploy()
    return rc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="una pasada y salir")
    ap.add_argument("--every", type=float, default=12.0, help="horas entre pasadas (modo bucle)")
    ap.add_argument("--limit", type=int, default=None, help="notas nuevas por pasada")
    ap.add_argument("--mock", action="store_true", help="sin LLM ni publicar (prueba de plomería)")
    ap.add_argument("--no-publish", action="store_true", help="reconstruye pero no publica")
    args = ap.parse_args()
    publish = not args.no_publish

    if args.once:
        return cycle(limit=args.limit, mock=args.mock, publish=publish)

    interval = max(60, int(args.every * 3600))
    print(f"[autopilot] bucle cada {args.every}h ({interval}s). Ctrl+C para parar.")
    while True:
        try:
            cycle(limit=args.limit, mock=args.mock, publish=publish)
        except KeyboardInterrupt:
            print("[autopilot] detenido por el usuario."); return 0
        except Exception:
            traceback.print_exc()
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main() or 0)
