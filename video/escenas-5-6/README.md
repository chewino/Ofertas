# Escenas 5 y 6 — Recibo de luz (Contepequense)

Composición [HyperFrames](https://github.com/heygen-com/hyperframes) vertical (1080×1920, 15 s).
El segundo 0 de esta composición corresponde al **45 s** del video completo.

| Tiempo local | Video completo | Escena | Archivo |
|---|---|---|---|
| 0–9 s  | 45–54 s | 5 · Cómo pagar menos | `compositions/escena-5.html` |
| 9–15 s | 54–60 s | 6 · Participación del público | `compositions/escena-6.html` |
| 0–15 s | 45–60 s | Subtítulos del narrador | `compositions/subtitulos.html` |

## Escena 5 — Cómo pagar menos
1. **0–3 s** · La familia revisa el recibo; una lupa resalta los **412 kWh consumidos**.
2. **3–5.6 s** · Comparación con el bimestre anterior (350 → 412 kWh, **+18 %**).
3. **5.6–9 s** · Se desconectan microondas, calentador y TV; las luces se apagan y el
   contador de consumo baja de 412 a 298 kWh.

## Escena 6 — Participación del público
Logotipo de Contepequense, la pregunta y tres opciones grandes (**A** menos de $300,
**B** $300–$800, **C** más de $800), cada una se resalta cuando el narrador la menciona;
cierra con el globo "¡Te leemos en los comentarios!".

## Uso
```bash
npx hyperframes check                              # lint + validación + layout
npx hyperframes preview                            # vista previa en el navegador
npx hyperframes render -o renders/escenas-5-6.mp4  # exportar MP4
```

GSAP 3.14.2 va incluido en `vendor/` para que la composición funcione sin conexión.

**Pendiente:** la voz del narrador. Los subtítulos están sincronizados con tiempos
estimados; cuando exista el audio, agrégalo como `<audio>` en `index.html` y ajusta los
`data-start` de `compositions/subtitulos.html`.
