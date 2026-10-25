# Partitura original estilo tráiler: 90 BPM, re menor (Dm–Bb–Gm–A), 16 compases (43 s)
#   compases 0–3   intro: dron grave, piano y viento
#   compases 4–7   construcción: "braam", ostinato de cuerdas, tambores graves
#   compases 8–11  clímax: braams en cada compás, tambores completos, subida
#   compases 12–15 golpe final (32 s), cuerdas sostenidas y piano de cierre
# Uso: python3 musica.py salida.wav   (requiere numpy y scipy)
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 44100
DUR = 43.0
N = int(SR * DUR)
BEAT = 60 / 90
BAR = 4 * BEAT
rng = np.random.default_rng(11)


def bus():
    return np.zeros((N, 2))


def t_(sec):
    return np.arange(int(sec * SR)) / SR


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def put(b, x, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    x = x[: N - i]
    b[i : i + len(x), 0] += x * gain * np.sqrt(1 - pan)
    b[i : i + len(x), 1] += x * gain * np.sqrt(1 + pan)


def saw(f, t, det=0.0):
    ph = f * (1 + det) * t
    return 2 * (ph - np.floor(ph + 0.5))


ROOT = {"D": 73.42, "Bb": 58.27, "G": 49.00, "A": 55.00}
CHORDS = [("D", [0, 3, 7]), ("Bb", [0, 4, 7]), ("G", [0, 3, 7]), ("A", [0, 4, 7])]


def chord(bar):
    n, ints = CHORDS[bar % 4]
    return ROOT[n], ints


# ---------- instrumentos ----------
def piano(f, sec=3.0):
    t = t_(sec)
    x = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.6 + k * 0.9)) for k, a in ((1, 1), (2, 0.45), (3, 0.2), (4, 0.08)))
    return x * np.minimum(1, t / 0.004)


def string_note(f, sec, att=0.02):
    t = t_(sec)
    x = sum(saw(f, t, d) for d in (-0.004, 0, 0.005)) / 3
    x = filt(x, "low", 2200)
    env = np.minimum(1, t / att) * (0.55 + 0.45 * np.exp(-t * 6)) * np.minimum(1, (sec - t) / 0.03)
    return x * env


def string_pad(root, ints, sec, bright=1400, att=0.8):
    t = t_(sec)
    x = np.zeros(len(t))
    for st in ints + [12]:
        f = root * 4 * 2 ** (st / 12)
        for d in (-0.005, 0, 0.006):
            x += saw(f, t, d)
    x = filt(x / 12, "low", bright)
    return x * np.minimum(1, t / att) * np.minimum(1, (sec - t) / 0.6)


def drone(sec):
    t = t_(sec)
    f = ROOT["D"] / 2
    x = np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 2 * t)
    x += filt(sum(saw(f * 2, t, d) for d in (-0.003, 0.004)), "low", 220) * 0.6
    return x * (0.8 + 0.2 * np.sin(2 * np.pi * 0.15 * t))


def wind(sec):
    t = t_(sec)
    n = filt(rng.standard_normal(len(t)), "band", [250, 900])
    return n * (0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * t + 1)) * np.minimum(1, t / 2)


def taiko(f0=62, big=False):
    t = t_(1.4 if big else 0.9)
    f = f0 * (1 + 0.8 * np.exp(-t * 25))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (2.5 if big else 4.5))
    skin = filt(rng.standard_normal(len(t)), "low", 900) * np.exp(-t * 22) * 0.6
    return np.tanh((body + skin) * 1.8)


def frame_hit():
    t = t_(0.5)
    n = filt(rng.standard_normal(len(t)), "band", [500, 3500])
    return n * np.exp(-t * 16) + np.sin(2 * np.pi * 210 * t) * np.exp(-t * 18) * 0.4


def braam(root, ints, sec=2.6, big=False):
    t = t_(sec)
    x = np.zeros(len(t))
    for st in ints[:2] + [12]:
        f = root * 2 ** (st / 12)
        for d in np.linspace(-0.012, 0.012, 7):
            x += saw(f, t, d)
    x /= 21
    # filtro que se abre y se cierra (en bloques para simular el barrido)
    out = np.zeros(len(t))
    blk = 2048
    for i in range(0, len(t), blk):
        p = i / len(t)
        fc = 220 + (1700 if big else 1200) * np.exp(-((p - 0.12) ** 2) / 0.02)
        seg = x[max(0, i - 512) : i + blk]
        y = filt(seg, "low", fc)
        out[i : i + blk] = y[-len(x[i : i + blk]) :]
    sub = np.sin(2 * np.pi * root / 2 * t) * 0.7
    env = np.minimum(1, t / 0.04) * np.exp(-t * (0.7 if big else 1.1))
    return np.tanh((out * 2.2 + sub) * env * 1.4)


def hit():
    t = t_(4.0)
    f = 28 + 60 * np.exp(-t * 5)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 0.9)
    crack = filt(rng.standard_normal(len(t)), "low", 3000) * np.exp(-t * 7)
    return np.tanh(boom * 2 + crack * 0.8)


def swell(sec):
    t = t_(sec)
    p = t / sec
    n = filt(rng.standard_normal(len(t)), "high", 3000)
    return n * p ** 3


def riser(sec):
    t = t_(sec)
    p = t / sec
    n = rng.standard_normal(len(t))
    x = filt(n, "band", [400, 2000]) * (1 - p) + filt(n, "band", [2500, 9000]) * p
    tone = sum(np.sin(2 * np.pi * np.cumsum(f0 * 2 ** (p * 2)) / SR) for f0 in (110, 165))
    return (x * 0.6 + tone * 0.15) * p ** 2.5


# ---------- arreglo ----------
drums, orch, fx, soft = bus(), bus(), bus(), bus()

put(soft, drone(DUR), 0, 0.25)
put(soft, wind(12), 0, 0.12)

# Intro: piano solo, una nota por tiempo y medio
mel = [("D", 0), ("A", 0), ("F", 0), ("E", 0), ("D", 0), ("C", 0), ("Bb", -12), ("A", -12)]
SEMI = {"D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "Bb": 10, "C": 12}
for k, (n, o) in enumerate(mel):
    f = 293.66 * 2 ** ((SEMI[n] - 2 + o) / 12)
    put(soft, piano(f), k * BAR / 2, 0.35, pan=0.2 if k % 2 else -0.2)
for bar in (2, 3):
    r, ints = chord(bar)
    put(orch, string_pad(r, ints, BAR + 0.5, 900, 1.5), bar * BAR, 0.25)
put(fx, swell(2.5), 4 * BAR - 2.5, 0.35)

# Construcción
for bar in range(4, 8):
    t0 = bar * BAR
    r, ints = chord(bar)
    if bar == 4:
        put(fx, braam(r, ints, big=True), t0, 0.8)
        put(drums, taiko(55, big=True), t0, 0.9)
    put(orch, string_pad(r, ints, BAR + 0.4, 1100), t0, 0.28)
    pat = [0, 7, 12, 7]
    for e in range(8):
        f = r * 2 * 2 ** ((ints[0] + pat[e % 4]) / 12)
        put(orch, string_note(f, BEAT / 2 * 0.9), t0 + e * BEAT / 2, 0.16 + 0.05 * (bar - 4), pan=-0.3)
    for b in (0, 2):
        put(drums, taiko(62), t0 + b * BEAT, 0.7)
    if bar == 7:
        for e in range(4):
            put(drums, taiko(70 + e * 6), t0 + 3 * BEAT + e * BEAT / 4, 0.4 + e * 0.1, pan=0.3 if e % 2 else -0.3)

# Clímax
for bar in range(8, 12):
    t0 = bar * BAR
    r, ints = chord(bar)
    put(fx, braam(r, ints, big=bar == 8), t0, 0.75)
    put(orch, string_pad(r, ints, BAR + 0.4, 1800), t0, 0.32)
    pat = [0, 7, 12, 7, 15 if ints[1] == 3 else 16, 12, 7, 12]
    for e in range(8):
        f = r * 2 * 2 ** ((ints[0] + pat[e]) / 12)
        put(orch, string_note(f, BEAT / 2 * 0.9), t0 + e * BEAT / 2, 0.24, pan=-0.3)
        put(orch, string_note(f * 2, BEAT / 2 * 0.9), t0 + e * BEAT / 2, 0.1, pan=0.4)
    for b, g in ((0, 1.0), (1.5, 0.6), (2, 0.85), (3, 0.7), (3.5, 0.6)):
        put(drums, taiko(58 if b in (0, 2) else 74), t0 + b * BEAT, g, pan=0.0 if b in (0, 2) else 0.35)
    for b in (1, 3):
        put(drums, frame_hit(), t0 + b * BEAT, 0.35, pan=-0.25)
put(fx, riser(3.2), 12 * BAR - 3.5, 0.6)
put(fx, swell(2.0), 12 * BAR - 2.3, 0.4)

# Golpe final y cierre
T = 12 * BAR  # 32 s
r, ints = chord(0)
put(fx, hit(), T, 1.0)
put(fx, braam(r, ints, sec=4.0, big=True), T, 0.9)
put(drums, taiko(48, big=True), T, 1.0)
put(orch, string_pad(r, ints, DUR - T - 0.2, 1500, 1.2), T + 0.3, 0.4)
for k, (n, o) in enumerate([("A", 0), ("F", 0), ("E", 0), ("D", 0)]):
    f = 293.66 * 2 ** ((SEMI[n] - 2 + o) / 12)
    put(soft, piano(f, 4), T + 2.0 + k * BEAT * 1.5, 0.3)

# ---------- mezcla ----------
# Silencio dramático justo antes del golpe final
gap = np.ones(N)
a, b = int((T - 0.35) * SR), int(T * SR)
gap[a:b] = 0.0
gap[a - 1000 : a] = np.linspace(1, 0, 1000)
for buf in (drums, orch, fx):
    buf *= gap[:, None]

irt = t_(3.5)
ir = np.stack([rng.standard_normal(len(irt)) for _ in range(2)], 1) * np.exp(-irt * 1.9)[:, None]
ir = np.stack([filt(ir[:, c], "low", 6000) for c in range(2)], 1)
ir /= np.sqrt((ir ** 2).sum(0))
send = drums * 0.35 + orch * 0.45 + fx * 0.4 + soft * 0.6
wet = np.stack([fftconvolve(send[:, c], ir[:, c])[:N] for c in range(2)], 1)

mix = drums + orch + fx + soft + wet * 0.55
mix = np.tanh(mix * 1.05)
mix /= np.abs(mix).max() / 0.89
fade = np.ones(N)
nf = int(1.5 * SR)
fade[-nf:] = np.linspace(1, 0, nf) ** 2
mix *= fade[:, None]
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
print("ok", sys.argv[1])
