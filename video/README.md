# Video del recibo de luz (Contepequense)

Video vertical 1080×1920 de 60 s hecho con [HyperFrames](https://github.com/heygen-com/hyperframes).

- `index.html` — video completo (0–60 s): monta las seis escenas sin duplicarlas.
- `escenas-1-4/` — escenas 1 a 4 (0–45 s), también se pueden previsualizar por separado.
- `escenas-5-6/` — escenas 5 y 6 (45–60 s), también se pueden previsualizar por separado.

```bash
cd video
npx hyperframes check
npx hyperframes render -o renders/recibo-de-luz-completo.mp4
```

**Pendiente:** la voz del narrador (los subtítulos tienen tiempos estimados) y el
archivo del logotipo real de Contepequense (el actual es provisional).
