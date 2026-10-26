# Pieza original estilo banda sinaloense: 130 BPM, Fa mayor, ritmo de polka (2/4)
#   tiempos 0–8    intro: fanfarria de trompetas y redoble de tarola
#   tiempos 8–40   parte A: tuba en el tiempo, armonías a contratiempo, trompetas en terceras, clarinetes
#   tiempos 40–48  break: tambora y tarola con la tuba caminando
#   tiempos 48–80  parte B, más aguda
#   tiempos 80–88  final de banda: "ta-ta-ta… ¡TAAAN!"
# Uso: python3 musica.py salida.wav   (requiere numpy y scipy)
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 44100
DUR = 42.0
N = int(SR * DUR)
B = 60 / 130  # un tiempo
rng = np.random.default_rng(5)


def bus():
    return np.zeros((N, 2))


def t_(sec):
    return np.arange(max(1, int(sec * SR))) / SR


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def put(b, x, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N or i < 0:
        return
    x = x[: N - i]
    b[i : i + len(x), 0] += x * gain * np.sqrt(1 - pan)
    b[i : i + len(x), 1] += x * gain * np.sqrt(1 + pan)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def saw(ph):
    return 2 * (ph - np.floor(ph + 0.5))


# ---------- instrumentos ----------
def metal(m, sec, bright=1.0):
    """Trompeta/trombón: diente de sierra con 'golpe' de brillo al ataque y vibrato tardío."""
    t = t_(sec)
    f = hz(m) * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.25))
    ph = np.cumsum(f) / SR
    x = saw(ph) + 0.5 * saw(ph * 1.003)
    claro = filt(x, "low", 4200 * bright)
    oscuro = filt(x, "low", 1300 * bright)
    e_br = np.exp(-t * 9)
    x = claro * (0.35 + 0.65 * e_br) + oscuro * (0.65 - 0.65 * e_br)
    env = np.minimum(1, t / 0.012) * np.minimum(1, (sec - t) / 0.025) * (0.85 + 0.15 * np.exp(-t * 6))
    return x * env


def clarinete(m, sec):
    t = t_(sec)
    f = hz(m) * (1 + 0.005 * np.sin(2 * np.pi * 6.2 * t))
    ph = np.cumsum(f) / SR
    x = np.sign(np.sin(2 * np.pi * ph)) * 0.6 + np.sin(2 * np.pi * ph * 3) * 0.2
    x = filt(x, "low", 3000)
    env = np.minimum(1, t / 0.02) * np.minimum(1, (sec - t) / 0.03)
    return x * env


def tuba(m, sec):
    t = t_(sec)
    ph = hz(m) * t
    x = saw(ph) * 0.7 + np.sin(2 * np.pi * ph) * 0.8
    x = filt(x, "low", 520)
    env = np.minimum(1, t / 0.015) * np.exp(-t * 2.2) * np.minimum(1, (sec - t) / 0.03)
    return x * env


def armonia(ms, sec=0.17):
    """'Pa' de las armonías (saxores/trombones) a contratiempo."""
    return sum(metal(m, sec, 0.7) for m in ms) / len(ms)


def tambora(fuerte=True):
    t = t_(0.5)
    f = 52 + 70 * np.exp(-t * 28)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (6 if fuerte else 9))
    skin = filt(rng.standard_normal(len(t)), "low", 1500) * np.exp(-t * 35) * 0.5
    return np.tanh((body + skin) * 1.7)


def platillo(abierto=False):
    t = t_(0.9 if abierto else 0.16)
    n = filt(rng.standard_normal(len(t)), "high", 5200)
    return n * np.exp(-t * (4 if abierto else 26))


def tarola(g=1.0):
    t = t_(0.22)
    n = filt(rng.standard_normal(len(t)), "band", [1200, 7500]) * np.exp(-t * 24)
    return (n + np.sin(2 * np.pi * 230 * t) * np.exp(-t * 30) * 0.5) * g


# ---------- armonía ----------
F, C7, BB = (53, [65, 69, 72]), (48, [64, 67, 70]), (46, [62, 65, 70])  # (raíz de tuba, voces de armonía)
PROG_A = [F, F, C7, C7, C7, C7, F, F, F, F, BB, BB, C7, C7, F, F]
PROG_B = [BB, BB, F, F, C7, C7, F, F, BB, BB, F, F, C7, C7, F, F]

# Melodías: (duración en tiempos, nota MIDI o None)
e, q, h = 0.5, 1.0, 2.0
MEL_A = [(e,72),(e,69),(e,72),(e,69), (q,77),(e,76),(e,74), (e,72),(e,70),(e,67),(e,70), (q,76),(e,74),(e,72),
         (e,70),(e,67),(e,64),(e,67), (q,72),(e,70),(e,69), (e,69),(e,72),(e,77),(e,81), (h,77),
         (e,72),(e,69),(e,72),(e,69), (q,77),(e,79),(e,81), (q,82),(e,81),(e,79), (e,77),(e,74),(e,70),(e,74),
         (e,72),(e,76),(e,79),(e,82), (q,81),(e,79),(e,76), (e,77),(e,69),(e,72),(e,69), (q,77),(q,None)]
MEL_B = [(e,74),(e,77),(e,74),(e,77), (q,82),(e,81),(e,79), (e,81),(e,77),(e,72),(e,77), (h,81),
         (e,79),(e,76),(e,72),(e,76), (q,79),(e,77),(e,76), (e,77),(e,81),(e,84),(e,81), (h,77),
         (e,74),(e,77),(e,74),(e,77), (q,82),(e,84),(e,86), (e,84),(e,81),(e,77),(e,81), (h,84),
         (e,82),(e,79),(e,76),(e,79), (q,84),(e,82),(e,79), (e,81),(e,77),(e,72),(e,69), (q,77),(q,None)]
FANFARRIA = [(e,72),(e,72),(e,72),(e,72), (q,77),(e,76),(e,77), (q,79),(q,81), (h,84)]

ESCALA = [65, 67, 69, 70, 72, 74, 76]  # Fa mayor


def tercera_abajo(m):
    """Segunda voz de trompeta: dos grados abajo en la escala de Fa (tercera diatónica)."""
    grados = sorted({x + 12 * o for x in ESCALA for o in (-2, -1, 0, 1, 2)})
    i = max(j for j, g in enumerate(grados) if g <= m)
    return grados[i - 2] if grados[i] == m else grados[i - 1]


metales, ritmo, bajo = bus(), bus(), bus()


def melodia(mel, t0, gain=1.0):
    t = t0
    for d, m in mel:
        if m is not None:
            dur = d * B * (0.82 if d < 1 else 0.92)
            put(metales, metal(m, dur), t, 0.42 * gain, pan=-0.25)
            put(metales, metal(tercera_abajo(m), dur), t, 0.32 * gain, pan=0.25)
            put(metales, clarinete(m + 12, dur), t, 0.12 * gain, pan=0.45)
        t += d * B


def acompanamiento(prog, t0, octava_tuba=0):
    for k, (raiz, voces) in enumerate(prog):
        for tb in range(2):  # compás de 2/4
            t = t0 + (2 * k + tb) * B
            nota = raiz + octava_tuba + (0 if tb == 0 else 7)
            put(bajo, tuba(nota, B * 0.8), t, 0.75)
            put(metales, armonia(voces), t + B / 2, 0.22, pan=0.1)
            put(ritmo, tambora(tb == 0), t, 0.85 if tb == 0 else 0.6)
            put(ritmo, platillo(), t + B / 2, 0.32, pan=0.35)
            put(ritmo, tarola(0.35), t + B / 2, 1.0, pan=-0.2)
            if k % 8 == 7 and tb == 1:  # remate de tarola al final de cada frase
                for r in range(4):
                    put(ritmo, tarola(0.25 + 0.1 * r), t + r * B / 4, 1.0, pan=-0.2)


def redoble(t0, beats, g0=0.15, g1=0.6):
    n = int(beats * 8)
    for i in range(n):
        put(ritmo, tarola(g0 + (g1 - g0) * i / n), t0 + i * B / 8, 1.0, pan=-0.2)


# Intro: fanfarria + redoble
melodia(FANFARRIA, 0.0, 1.1)
redoble(4 * B, 4, 0.1, 0.7)
put(ritmo, tambora(), 0, 0.9)
put(ritmo, platillo(True), 0, 0.4)

# Parte A
T_A = 8 * B
put(ritmo, platillo(True), T_A, 0.6)
acompanamiento(PROG_A, T_A)
melodia(MEL_A, T_A)

# Break: tambora y tarola solas, tuba caminando, golpes de metales en el último compás
T_BR = 40 * B
for k in range(8):
    t = T_BR + k * B
    put(ritmo, tambora(k % 2 == 0), t, 0.9)
    put(ritmo, platillo(), t + B / 2, 0.35, pan=0.35)
    put(bajo, tuba([41, 43, 45, 46, 48, 50, 52, 53][k], B * 0.8), t, 0.8)
redoble(T_BR + 4 * B, 2, 0.15, 0.5)
for k, d in enumerate([0, 0.5, 1.0]):
    put(metales, armonia([72, 76, 79], 0.2), T_BR + 6 * B + d * B, 0.6)
redoble(T_BR + 7 * B, 1, 0.3, 0.8)

# Parte B
T_B = 48 * B
put(ritmo, platillo(True), T_B, 0.6)
acompanamiento(PROG_B, T_B)
melodia(MEL_B, T_B, 1.05)

# Final de banda: dos golpes de C7, golpe largo de Fa con redoble y "pa" final
T_F = 80 * B
for d in (0, 0.5, 1.0):
    put(metales, armonia([64, 70, 76, 79], 0.2), T_F + d * B, 0.75)
    put(ritmo, tambora(), T_F + d * B, 0.8)
    put(bajo, tuba(48, 0.2), T_F + d * B, 0.8)
put(metales, sum(metal(m, 3 * B) for m in (65, 69, 72, 77, 81)) / 5, T_F + 2 * B, 0.9)
put(bajo, tuba(41, 3 * B), T_F + 2 * B, 0.9)
put(ritmo, platillo(True), T_F + 2 * B, 0.7)
redoble(T_F + 2 * B, 3, 0.2, 0.7)
put(metales, armonia([65, 69, 72, 77], 0.22), T_F + 5 * B, 1.0)
put(bajo, tuba(41, 0.25), T_F + 5 * B, 1.0)
put(ritmo, tambora(), T_F + 5 * B, 1.0)
put(ritmo, platillo(True), T_F + 5 * B, 0.8)

# ---------- mezcla (plaza abierta: poca reverberación) ----------
irt = t_(1.2)
ir = np.stack([rng.standard_normal(len(irt)) for _ in range(2)], 1) * np.exp(-irt * 4.5)[:, None]
ir /= np.sqrt((ir ** 2).sum(0))
send = metales * 0.35 + ritmo * 0.15 + bajo * 0.05
wet = np.stack([fftconvolve(send[:, c], ir[:, c])[:N] for c in range(2)], 1)
mix = metales * 1.0 + ritmo * 0.9 + bajo * 1.0 + wet * 0.35
mix = np.tanh(mix * 1.2)
mix /= np.abs(mix).max() / 0.89
fade = np.ones(N)
nf = int(0.5 * SR)
fade[-nf:] = np.linspace(1, 0, nf)
mix *= fade[:, None]
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
print("ok", sys.argv[1], "fin del último golpe:", round(T_F + 5 * B, 2), "s")
