# Escenas 1 a 4 — Recibo de luz (Contepequense)

Composición [HyperFrames](https://github.com/heygen-com/hyperframes) vertical (1080×1920, 45 s).
Sus tiempos coinciden con los segundos 0–45 del video completo.

| Tiempo | Escena | Archivo |
|---|---|---|
| 0–8 s   | 1 · El gancho | `compositions/escena-1.html` |
| 8–20 s  | 2 · Las partes del recibo | `compositions/escena-2.html` |
| 20–33 s | 3 · Por qué sube tanto | `compositions/escena-3.html` |
| 33–45 s | 4 · Cuidado con la tarifa DAC | `compositions/escena-4.html` |
| 0–45 s  | Subtítulos del narrador | `compositions/subtitulos-1-4.html` |

## Escena 1 — El gancho
El recibo llega por debajo de la puerta; al abrirlo, "$1,027" cae como rayo (destello,
sacudida, cara de susto). Con "Tranquilo…" la cara sonríe y aparece el cronómetro
"¡En menos de 1 minuto!". El logotipo está desde el primer frame (miniatura del video).

## Escena 2 — Las partes del recibo
Se resaltan en orden: **1** el periodo (≈ 2 meses), **2** las lecturas actual y anterior
(con un medidor que avanza de 18,330 a 18,742) y **3** el total a pagar.

## Escena 3 — Por qué sube tanto
La resta 18,742 − 18,330 = **412 kWh**; luego tres escalones (básico, intermedio,
excedente) que se encienden con monedas cada vez más grandes y la etiqueta
"¡Varias veces más caro!".

## Escena 4 — Cuidado con la tarifa DAC
Doce barras del promedio mensual rebasan el "límite de tu tarifa", la aguja del medidor
cae en rojo (DAC), aparece el sello "SIN SUBSIDIO" y el total tachado con una flecha
hacia arriba: "¡Mucho más!".

Las cifras (lecturas, 412 kWh, $1,027) son de ejemplo y coinciden con las de la escena 5.

## Uso
```bash
npx hyperframes check
npx hyperframes preview
npx hyperframes render -o renders/escenas-1-4.mp4
```

**Pendiente:** la voz del narrador; los tiempos de los subtítulos son estimados.
