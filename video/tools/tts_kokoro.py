"""Sintetiza una frase con Kokoro-82M usando el fonemizador de español latinoamericano.

`hyperframes tts` solo ofrece "es" (pronunciación de España, con θ). Este script usa el mismo
modelo que descarga HyperFrames, pero con espeak "es-419" (seseo). Lo llama tools/narracion.py
con el python del venv que tiene kokoro-onnx y soundfile:

    python tts_kokoro.py "texto" salida.wav --voz ef_dora --velocidad 1.05 --idioma es-419
"""
import argparse
from pathlib import Path

import soundfile as sf
from kokoro_onnx import Kokoro

MODELOS = Path.home() / ".cache" / "hyperframes" / "tts"

p = argparse.ArgumentParser()
p.add_argument("texto")
p.add_argument("salida")
p.add_argument("--voz", default="ef_dora")
p.add_argument("--velocidad", type=float, default=1.0)
p.add_argument("--idioma", default="es-419")
a = p.parse_args()

kokoro = Kokoro(str(MODELOS / "models" / "kokoro-v1.0.onnx"), str(MODELOS / "voices" / "voices-v1.0.bin"))
muestras, frecuencia = kokoro.create(a.texto, voice=a.voz, speed=a.velocidad, lang=a.idioma)
sf.write(a.salida, muestras, frecuencia)
