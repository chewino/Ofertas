# Video del recibo de luz (Contepequense)

Video vertical 1080×1920 de ~87 s con narración, hecho con
[HyperFrames](https://github.com/heygen-com/hyperframes).

| Escena | Contenido |
|---|---|
| 1 · El gancho | El recibo llega, "$1,027" cae como rayo; "te explico cómo leerlo y pagar menos". |
| 2 · Las partes del recibo | Cuatro datos: tarifa, periodo (≈ 2 meses), lecturas del medidor y total. |
| 3 · Por qué sube tanto | Lecturas → 412 kWh; escalones de tarifa 1 por bimestre: básico 0–150, intermedio 151–280, excedente más de 280 (más de 3 veces el precio del básico). |
| 4 · Cuidado con la tarifa DAC | Promedio mensual de 12 meses mayor a 250 kWh (tarifa 1; 1A 300, 1B 400, 1C 850) → DAC sin subsidio; para salir hay que bajar el promedio. |
| 5 · Cómo pagar menos | Revisar y comparar kWh, reducir aparatos de alto consumo, apagar luces y desconectar aparatos en espera (≈ 10 % del consumo). |
| 6 · Participación del público | ¿Menos de $300, entre $300 y $800, o más de $800? "¡Te leemos en los comentarios!" |

## Cómo está armado

- `guion.json` — **fuente del guion**: el texto que dice el narrador (`tts`) y el subtítulo de cada frase.
- `tools/narracion.py` — genera la voz frase por frase, mide cuánto dura cada una y escribe:
  `audio/narracion.mp3`, `tiempos.js`, `compositions/subtitulos.html` e `index.html`
  (estos cuatro son generados: no se editan a mano).
- `compositions/escena-*.html` — las animaciones. Leen `window.GUION` (de `tiempos.js`), así que
  cada movimiento ocurre cuando el narrador dice la frase correspondiente, aunque cambie el texto o la voz.
- `vendor/gsap.min.js` — GSAP 3.14.2 local, para trabajar sin conexión.

La voz es sintética: Kokoro-82M (el modelo de `hyperframes tts`), voz `ef_dora`, con pronunciación
de español latinoamericano (`es-419`).

## Cambiar el texto o la voz

```bash
cd video
python3 -m venv .venv && .venv/bin/pip install kokoro-onnx soundfile
# edita guion.json y luego:
HYPERFRAMES_PYTHON=.venv/bin/python python3 tools/narracion.py
npx hyperframes check
npx hyperframes render -o renders/recibo-de-luz.mp4
```

Para usar una grabación propia, reemplaza `audio/narracion.mp3` y ajusta los tiempos de cada frase
en `tiempos.js` (inicio y fin en segundos dentro de su escena) para que coincidan con tu audio.

## Fuentes de los datos

Límites de escalones y de la DAC, y precios de referencia de la tarifa 1 (2026), según notas de
prensa que citan las tablas de CFE: [Uno TV](https://www.unotv.com/nacional/las-tarifas-domesticas-de-cfe-van-de-1-a-4-pesos-por-kwh-en-junio-de-2026/),
[adn40](https://www.adn40.mx/mexico/2025-07-18/que-es-y-quienes-pueden-tener-la-tarifa-dac-la-cfe-para-tener-descuento-en-la-luz),
[Ámbito](https://www.ambito.com/mexico/economia/adios-al-subsidio-cfe-advierte-que-quintuplicara-el-recibo-deluz-miles-mexicanos-previo-aviso-n6274147).
Consumo en espera (≈ 7–11 %): [adn40](https://www.adn40.mx/mexico/consumo-fantasma-el-secreto-del-gasto-energia-invisible-cfe).
Conviene confirmarlos en [cfe.mx](https://www.cfe.mx) antes de publicar; las cifras del recibo
(lecturas, 412 kWh, $1,027) son de ejemplo.

**Pendiente:** el archivo del logotipo real de Contepequense (el actual es provisional).
