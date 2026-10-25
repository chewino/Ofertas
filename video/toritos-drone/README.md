# Noche de toritos — Vista desde el dron (Contepequense)

Reel vertical [HyperFrames](https://github.com/heygen-com/hyperframes) (1080×1920, 31 s) hecho con
12 fotos aéreas de la quema de toritos y los fuegos artificiales en la plaza.

| Tiempo | Contenido | Archivo |
|---|---|---|
| 0–31 s | 12 fotos con paneo lento (Ken Burns) y fundidos de 0.5 s, 2.5 s por foto | `compositions/fotos.html` |
| 0–4.6 s | Logo + título "¡Noche de toritos!" · "Vista desde el dron" | `compositions/textos.html` |
| 5.2 / 8.0 / 20.3 s | Rótulos: "La plaza, llena" · "¡Lluvia de chispas!" · "El cielo se ilumina" | `compositions/textos.html` |
| 27.6–31 s | Cierre: "¿Tú también estuviste ahí?" + "¡Cuéntanos en los comentarios!" | `compositions/textos.html` |

Las fotos (`fotos/01.jpg`–`12.jpg`) llevan un ligero aumento de contraste y saturación. Se
descartaron las tomas movidas o desenfocadas. Para cambiar el encuadre de una foto, ajusta su
valor en `focos` (centro horizontal de la acción, 0–1) en `compositions/fotos.html`.

## Uso
```bash
npx hyperframes check                                # lint + validación + layout
npx hyperframes preview                              # vista previa en el navegador
npx hyperframes render -o renders/toritos-drone.mp4  # exportar MP4
```

**Pendiente:** música. Agrega un `<audio>` en `index.html` con data-start="0" data-duration="31".
