# Toritos — Versión cinematográfica (Contepequense)

Composición [HyperFrames](https://github.com/heygen-com/hyperframes) horizontal 1920×1080 con encuadre de
cine 2.39:1 (43 s), sobre una partitura original estilo tráiler a 90 BPM en re menor (un compás = 2.667 s).
La versión vertical y rítmica para reels está en `../toritos-drone`.

| Tiempo | Música | Imagen y texto |
|---|---|---|
| 0–10.7 s | Dron grave, piano y viento | **Video:** vuelo del dron hacia la iglesia en cámara lenta; "Contepequense presenta"; "Cuando cae la noche, el pueblo se reúne en la plaza." |
| 10.7–21.3 s | Braam, ostinato de cuerdas, tambores | Corte seco en el braam; tomas largas con fundidos cortos; "Y el fuego se vuelve tradición." |
| 21.3–32 s | Clímax: braam en cada compás, subida | Cortes secos; "Fe · Fuego · Fiesta"; **video:** acercamiento rápido al campanario; rampa de zoom y **silencio en negro** |
| 32–43 s | Golpe final, cuerdas y piano | Destello y temblor; título **TORITOS — Una noche en la plaza**; se disuelve al **video** de la plaza con la gente; cierre "¿Tú también estuviste ahí?"; fundido a negro |

Acabado de cine: etalonaje teal & orange, viñeta, grano de película a 24 cuadros/s, destellos cálidos y
temblor contenido en los golpes. Las frases van en la barra inferior, como subtítulos de cine.

## Archivos
- `clips/` — tres fragmentos del video del dron (sin audio), recortados, sin ruido, con el etalonaje y el grano
  ya aplicados con ffmpeg: `vuelo.mp4` (origen 3–11 s, a 0.75× con interpolación de cuadros),
  `campanario.mp4` (origen 21.5–24.2 s, a 2×) y `plaza.mp4` (origen 30–36.6 s). Se colocan en `index.html`
  debajo de la capa de fotos; mientras se ven, `compositions/fotos.html` apaga sus capas de mezcla.
- `compositions/fotos.html` — tomas (`tomas`), etalonaje, grano, destellos y barras.
- `compositions/textos.html` — textos (fuentes Cinzel y Cormorant Garamond, licencia OFL, en `fuentes/`).
- `audio/musica.py` — genera la partitura (`python3 audio/musica.py musica.wav`, requiere numpy y scipy);
  `audio/musica.m4a` es la versión normalizada a -14 LUFS.

## Uso
```bash
npx hyperframes check
npx hyperframes preview
npx hyperframes render -o renders/toritos-cine.mp4
```
