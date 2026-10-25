# Noche de toritos — Vista desde el dron (Contepequense)

Reel vertical [HyperFrames](https://github.com/heygen-com/hyperframes) (1080×1920, 32 s) con fotos aéreas
de la quema de toritos, montado al ritmo de una pista original a **120 BPM** (un tiempo = 0.5 s).

| Tiempo | Música | Imagen |
|---|---|---|
| 0–4 s | Pad, latidos y subida | Plaza en calma con barras de cine; título "Una noche de TORITOS" |
| 4–16 s | **Drop 1** (impacto, bombo, palmas, bajo, arpegio) | Cortes cada tiempo doble, luego en corcheas; "Tradición · Fuego · Fiesta" |
| 16–20 s | Pausa, redoble y subida | Fuegos sobre la iglesia + rampa de velocidad; "El cielo se ilumina" |
| 20–28 s | **Drop 2** (con toms) | Cortes al ritmo; "Nuestra gente · plaza · fiesta" |
| 28–32 s | Impacto final y cola | Se abre a la plaza completa; "¿Tú también estuviste ahí?" |

Efectos: golpe de zoom en cada corte, destellos y sacudida de cámara en los impactos (4, 20 y 28 s),
destello suave en cada compás, desenfoque de movimiento antes de cada drop, luz cálida (light leak) y
etalonaje con contraste y saturación.

## Archivos
- `compositions/fotos.html` — lista de tomas (`tomas`: inicio, duración, foco, zoom) y efectos de cámara.
- `compositions/textos.html` — títulos y palabras sincronizadas.
- `audio/musica.m4a` — pista original (normalizada a -12 LUFS); `audio/musica.py` la regenera
  (`python3 audio/musica.py musica.wav`, requiere numpy y scipy).
- `fotos/pNN.jpg` — fotos usadas, con un ligero aumento de contraste y color.

## Uso
```bash
npx hyperframes check
npx hyperframes preview
npx hyperframes render -o renders/toritos-drone.mp4
```
