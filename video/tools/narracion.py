#!/usr/bin/env python3
"""Genera la narración del video a partir de guion.json.

Para cada frase del guion:
  1. sintetiza la voz con Kokoro-82M, el modelo de `hyperframes tts`, con acento
     latinoamericano (se guarda en caché por texto/voz/velocidad/acento),
  2. mide su duración y la coloca en la línea de tiempo.

Con esos tiempos escribe:
  - audio/narracion.mp3            la narración completa
  - tiempos.js                     window.GUION con el inicio/duración de cada escena y frase
  - compositions/subtitulos.html   los subtítulos sincronizados con la voz
  - index.html                     el video completo con la duración de cada escena

Las escenas leen window.GUION, así que sus animaciones se acomodan solas si cambia el texto
o la voz. Uso (desde video/):

    HYPERFRAMES_PYTHON=/ruta/a/venv/bin/python python3 tools/narracion.py

El venv necesita `pip install kokoro-onnx soundfile`. La primera vez se descarga el modelo
con `npx hyperframes tts` (~300 MB, queda en ~/.cache/hyperframes/tts).
Para usar una grabación propia en lugar de la voz sintética, ver README.md.
"""
import hashlib
import html
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CACHE = RAIZ / "audio" / "frases"
ANCHO, ALTO = 1080, 1920


def duracion(wav: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
        check=True, capture_output=True, text=True,
    ).stdout
    return float(out.strip())


def sintetizar(texto: str, voz: str, velocidad: float, acento: str) -> Path:
    clave = hashlib.sha1(f"{voz}|{velocidad}|{acento}|{texto}".encode()).hexdigest()[:16]
    wav = CACHE / f"{clave}.wav"
    if not wav.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        modelo = Path.home() / ".cache" / "hyperframes" / "tts" / "models" / "kokoro-v1.0.onnx"
        if not modelo.exists():  # la primera vez, deja que HyperFrames descargue el modelo
            subprocess.run(["npx", "-y", "hyperframes@0.8.185", "tts", "hola", "-v", voz, "-o", str(CACHE / "prueba.wav")],
                           check=True, cwd=RAIZ, stdout=subprocess.DEVNULL)
        python = os.environ.get("HYPERFRAMES_PYTHON", sys.executable)
        subprocess.run(
            [python, "-I", str(RAIZ / "tools" / "tts_kokoro.py"), texto, str(wav),
             "--voz", voz, "--velocidad", str(velocidad), "--idioma", acento],
            check=True, stdout=subprocess.DEVNULL,
        )
    return wav


def mezclar(frases: list, salida: Path, total: float) -> None:
    entradas, filtros = [], []
    for i, f in enumerate(frases):
        entradas += ["-i", str(f["wav"])]
        ms = round(f["start"] * 1000)
        filtros.append(f"[{i}:a]adelay={ms}:all=1[a{i}]")
    mezcla = "".join(f"[a{i}]" for i in range(len(frases)))
    filtros.append(f"{mezcla}amix=inputs={len(frases)}:normalize=0,apad,atrim=0:{total:.3f}[out]")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", *entradas, "-filter_complex", ";".join(filtros),
         "-map", "[out]", "-ac", "1", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "128k", str(salida)],
        check=True,
    )


def main() -> None:
    guion = json.loads((RAIZ / "guion.json").read_text(encoding="utf-8"))
    voz, vel, acento = guion["voz"], guion["velocidad"], guion["acento"]
    pausa, pausa_escena = guion["pausa_entre_frases"], guion["pausa_entre_escenas"]

    t = 0.0
    escenas, frases = [], []
    for e in guion["escenas"]:
        inicio = t
        t += 0.4  # deja entrar la escena antes de que hable el narrador
        locales = []
        for f in e["frases"]:
            wav = sintetizar(f["tts"], voz, vel, acento)
            d = duracion(wav)
            frases.append({"wav": wav, "start": t, "end": t + d, "subtitulo": f["subtitulo"]})
            locales.append({"start": round(t - inicio, 3), "end": round(t + d - inicio, 3)})
            print(f"  {e['id']}  {t:6.2f}–{t + d:6.2f}  {f['tts']}", file=sys.stderr)
            t += d + pausa
        t += pausa_escena - pausa
        escenas.append({"id": e["id"], "titulo": e["titulo"], "start": round(inicio, 3), "frases": locales})
    t += guion["cola_final"] - pausa_escena
    total = round(t, 2)
    for i, e in enumerate(escenas):
        fin = escenas[i + 1]["start"] if i + 1 < len(escenas) else total
        e["duracion"] = round(fin - e["start"], 3)

    (RAIZ / "audio").mkdir(exist_ok=True)
    mezclar(frases, RAIZ / "audio" / "narracion.mp3", total)

    datos = {"duracion": total, "escenas": {e["id"]: e for e in escenas}}
    (RAIZ / "tiempos.js").write_text(
        "// Generado por tools/narracion.py a partir de guion.json. No editar a mano.\n"
        f"window.GUION = {json.dumps(datos, ensure_ascii=False, indent=2)};\n",
        encoding="utf-8",
    )
    escribir_subtitulos(frases)
    escribir_index(escenas, total)
    print(f"Duración total: {total:.2f} s", file=sys.stderr)


def escribir_subtitulos(frases: list) -> None:
    cues = [f for f in frases if f["subtitulo"]]
    divs, tiempos = [], []
    for i, f in enumerate(cues, 1):
        ini = round(f["start"] - 0.05, 3)
        dur = round(f["end"] - f["start"] + 0.2, 3)
        divs.append(
            f'    <div id="sub-{i}" class="clip cap" data-start="{ini}" data-duration="{dur}" '
            f'data-track-index="0"><span>{f["subtitulo"]}</span></div>'
        )
        tiempos.append(ini)
    (RAIZ / "compositions" / "subtitulos.html").write_text(f"""<template>
  <!-- Generado por tools/narracion.py a partir de guion.json. No editar a mano. -->
  <style>
    #root {{ position: absolute; inset: 0; font-family: "Montserrat", sans-serif; }}
    #root .cap {{
      position: absolute; left: 70px; right: 70px; top: 1560px;
      color: #fff; text-align: center; font-size: 54px; font-weight: 800; line-height: 1.22;
      text-shadow: 0 4px 0 rgba(0,0,0,.55), 0 0 24px rgba(0,0,0,.45);
    }}
    #root .cap > span {{ display: inline-block; }}
    #root .cap em {{ font-style: normal; color: #ffb703; }}
  </style>

  <div id="root" data-composition-id="subtitulos" data-width="{ANCHO}" data-height="{ALTO}">
{chr(10).join(divs)}
  </div>

  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      {json.dumps(tiempos)}.forEach((t, i) => {{
        tl.fromTo("#sub-" + (i + 1) + " > span", {{ y: 18, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.2, ease: "power2.out" }}, t);
      }});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["subtitulos"] = tl;
    }})();
  </script>
</template>
""", encoding="utf-8")


def escribir_index(escenas: list, total: float) -> None:
    hosts = []
    for e in escenas:
        hosts.append(f"""    <!-- {html.escape(e["titulo"])} -->
    <div id="{e["id"]}" class="capa"
      data-composition-id="{e["id"]}" data-composition-src="compositions/{e["id"]}.html"
      data-start="{e["start"]}" data-duration="{e["duracion"]}" data-track-index="1" data-track-kind="graphics"
      data-width="{ANCHO}" data-height="{ALTO}"></div>
""")
    (RAIZ / "index.html").write_text(f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width={ANCHO}, height={ALTO}" />
  <title>Recibo de luz — Video completo</title>
  <script src="vendor/gsap.min.js"></script>
  <script src="tiempos.js"></script>
  <style>
    html, body {{ margin: 0; padding: 0; width: {ANCHO}px; height: {ALTO}px; overflow: hidden; background: #0f1b3d; }}
    #main {{ position: relative; width: {ANCHO}px; height: {ALTO}px; overflow: hidden; font-family: "Montserrat", sans-serif; }}
    #fondo {{
      position: absolute; inset: 0;
      background: radial-gradient(1200px 900px at 50% 30%, #1a2a5c, #0f1b3d 70%);
    }}
    .capa {{ position: absolute; inset: 0; }}
  </style>
</head>
<body>
  <!--
    Generado por tools/narracion.py a partir de guion.json. No editar a mano.
    Video del recibo de luz (Contepequense), vertical {ANCHO}×{ALTO}, {total:.1f} s.
  -->
  <div id="main" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{ANCHO}" data-height="{ALTO}">
    <div id="fondo"></div>

{"".join(hosts)}
    <div id="subtitulos" class="capa"
      data-composition-id="subtitulos" data-composition-src="compositions/subtitulos.html"
      data-start="0" data-duration="{total}" data-track-index="2" data-track-kind="captions"
      data-width="{ANCHO}" data-height="{ALTO}"></div>

    <audio id="narracion" src="audio/narracion.mp3" data-start="0" data-duration="{total}" data-track-index="3" data-volume="1"></audio>

    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </div>
</body>
</html>
""", encoding="utf-8")


if __name__ == "__main__":
    main()
