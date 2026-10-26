# Toritos — Versión con banda (Contepequense)

Versión movida 1920×1080 (42 s) sobre una pieza original **estilo banda sinaloense** a 130 BPM en Fa mayor
(ritmo de polka; un tiempo = 0.4615 s). Mezcla las fotos con tres fragmentos del video del dron a 2×.

| Tiempos (s) | Música | Imagen y texto |
|---|---|---|
| 0–3.7 | Fanfarria de trompetas y redoble | **Video:** vuelo del dron; "¡Noche de toritos! · Con todo y banda" |
| 3.7–18.5 | Parte A: tuba, armonías a contratiempo, trompetas en terceras, clarinetes, tambora y tarola | Corte cada 2 tiempos con golpe de zoom; "¡Ajúa!", "¡Pura tradición!" |
| 18.5–22.2 | Break de tambora y tarola | **Video:** acercamiento a la iglesia; "¡Que se prenda la plaza!" |
| 22.2–36.9 | Parte B, más aguda | Cortes cada 2 tiempos y cada tiempo; **video** de la gente; "¡Ahí viene el torito!", "¡Todo el pueblo!", "¡Que siga la fiesta!" |
| 36.9–42 | Final de banda: "ta-ta-ta… ¡TAAAN!" | Un corte por golpe; "¿Estuviste ahí? ¡Cuéntanos en los comentarios!" |

Efectos: pulso de la imagen en cada tiempo, destellos cada 4 tiempos, sacudida en los golpes grandes y
papel picado meciéndose con el ritmo.

## Archivos
- `compositions/fotos.html` — se genera con `python3 herramientas/generar_fotos.py compositions/fotos.html herramientas/fotos.plantilla.html`;
  para cambiar tomas, edita la lista `T` de `herramientas/generar_fotos.py` (tiempos musicales) y vuelve a generar.
- `compositions/textos.html` — papel picado, título y gritos.
- `clips/` — fragmentos del video del dron a 2× con color festivo: `vuelo.mp4` (origen 0–7.5 s),
  `iglesia.mp4` (origen 12–19.5 s) y `gente.mp4` (origen 30–33.8 s).
- `audio/musica.py` — genera la música (`python3 audio/musica.py musica.wav`, requiere numpy y scipy);
  `audio/musica.m4a` es la versión normalizada a -13 LUFS.

## Uso
```bash
npx hyperframes check
npx hyperframes preview
npx hyperframes render -o renders/toritos-banda.mp4
```
