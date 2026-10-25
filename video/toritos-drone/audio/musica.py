# Pista original sintetizada: 120 BPM, re menor, 32 s (16 compases de 2 s)
# 0–4 intro · 4–16 drop 1 · 16–20 pausa + subida · 20–28 drop 2 · 28–32 impacto final
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 44100
DUR = 32.0
N = int(SR * DUR)
B = 0.5  # duración de un tiempo
rng = np.random.default_rng(7)

def bus():
    return np.zeros((N, 2))

def t_(sec):
    return np.arange(int(sec * SR)) / SR

def filt(x, kind, f):
    sos = butter(2 if kind != "band" else 2, f, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x)

def put(b, x, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    x = x[: N - i]
    l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    b[i : i + len(x), 0] += x * gain * l * 1.414
    b[i : i + len(x), 1] += x * gain * r * 1.414

# ---------- instrumentos ----------
def kick(big=False):
    t = t_(0.6 if big else 0.45)
    f = 44 + 120 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * (4 if big else 7))
    click = filt(rng.standard_normal(len(t)), "high", 2000) * np.exp(-t * 300) * 0.3
    return np.tanh((x + click) * 1.6)

def clap():
    t = t_(0.35)
    n = filt(rng.standard_normal(len(t)), "band", [900, 5000])
    env = np.zeros(len(t))
    for d in (0, 0.011, 0.022):
        i = int(d * SR)
        env[i:] += np.exp(-np.arange(len(t) - i) / SR * (90 if d < 0.02 else 14))
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.5
    return n * env * 0.8 + tone

def hat(open_=False):
    t = t_(0.3 if open_ else 0.06)
    return filt(rng.standard_normal(len(t)), "high", 7500) * np.exp(-t * (14 if open_ else 70))

def tom(f0):
    t = t_(0.4)
    f = f0 * (1 + 0.6 * np.exp(-t * 20))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)

def crash():
    t = t_(2.5)
    n = filt(rng.standard_normal(len(t)), "high", 4000)
    return n * np.exp(-t * 1.8)

def impact():
    t = t_(3.0)
    f = 30 + 70 * np.exp(-t * 6)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.3)
    hit = filt(rng.standard_normal(len(t)), "low", 1800) * np.exp(-t * 5)
    return np.tanh(boom * 1.8 + hit * 0.7)

def riser(sec):
    t = t_(sec)
    p = t / sec
    n = rng.standard_normal(len(t))
    lo = filt(n, "band", [300, 1500])
    hi = filt(n, "band", [2500, 9000])
    x = lo * (1 - p) + hi * p
    f = 180 * 2 ** (p * 3)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    return (x * 0.7 + tone) * p ** 2

def downlifter(sec):
    return riser(sec)[::-1] * 0.8

def saw(f, t, det=0.0):
    ph = (f * (1 + det)) * t
    return 2 * (ph - np.floor(ph + 0.5))

NOTE = {"D": 73.42, "Bb": 58.27, "F": 87.31, "C": 65.41}
CHORDS = [("D", [0, 3, 7]), ("Bb", [0, 4, 7]), ("F", [0, 4, 7]), ("C", [0, 4, 7])]

def pad(root, ints, sec, bright=1200):
    t = t_(sec)
    x = np.zeros(len(t))
    for st in ints:
        f = root * 4 * 2 ** (st / 12)
        for d in (-0.006, 0, 0.007):
            x += saw(f, t, d)
    x = filt(x / 9, "low", bright)
    a = np.minimum(1, t / 0.4) * np.minimum(1, (sec - t) / 0.3)
    return x * a

def bass_note(f, sec):
    t = t_(sec)
    x = saw(f, t) + 0.5 * np.sin(2 * np.pi * f / 2 * t)
    x = filt(x, "low", 380)
    return x * np.exp(-t * 4) * np.minimum(1, t / 0.004)

def pluck(f, sec=0.22):
    t = t_(sec)
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + saw(f, t, 0.004) * 0.5
    return filt(x, "low", 2600) * np.exp(-t * 16)

# ---------- buses ----------
drums, music, fx = bus(), bus(), bus()
kick_times = []

def chord_at(bar):
    name, ints = CHORDS[bar % 4]
    return NOTE[name], ints

def full_bar(bar, extra=False):
    t0 = bar * 2.0
    root, ints = chord_at(bar)
    for b in range(4):
        tb = t0 + b * B
        put(drums, kick(), tb, 0.9); kick_times.append(tb)
        if b in (1, 3):
            put(drums, clap(), tb, 0.55)
        for s in range(4):
            acc = 0.32 if s == 2 else 0.16
            put(drums, hat(), tb + s * B / 4, acc, pan=0.3 if s % 2 else -0.3)
        put(drums, hat(True), tb + B / 2, 0.12, pan=0.2)
        if extra:
            put(drums, tom(110 if b % 2 else 82), tb + 0.375, 0.35, pan=-0.4 if b % 2 else 0.4)
        # bajo en corcheas a contratiempo
        for e in range(2):
            put(music, bass_note(root * (2 if e else 1), 0.24), tb + e * B / 2 + (0.25 if e == 0 else 0), 0.5)
    # arpegio en semicorcheas
    seq = [0, 1, 2, 1, 2, 0, 1, 2]
    for s in range(16):
        st = ints[seq[s % 8]] + (12 if s % 4 == 3 else 0)
        put(music, pluck(root * 8 * 2 ** (st / 12)), t0 + s * B / 4, 0.13, pan=0.35 if s % 2 else -0.35)
    put(music, pad(root, ints, 2.0, 1600), t0, 0.35)

# Intro 0–4
for bar in (0, 1):
    root, ints = chord_at(bar)
    put(music, pad(root, ints, 2.0, 600 + 500 * bar), bar * 2.0, 0.45)
    put(drums, kick(big=True), bar * 2.0, 0.6); kick_times.append(bar * 2.0)
    put(drums, kick(big=True), bar * 2.0 + 0.75, 0.35)
for s in range(8):
    put(drums, hat(), 2.0 + s * 0.25, 0.08 + s * 0.02)
put(fx, riser(3.0), 1.0, 0.55)

# Drop 1 (4–16)
for bar in range(2, 8):
    full_bar(bar)
for tt, f in zip(np.arange(15.0, 16.0, 0.125), np.linspace(140, 70, 8)):
    put(drums, tom(f), tt, 0.5, pan=float(np.sin(tt * 7)) * 0.5)

# Pausa y subida (16–20)
put(fx, downlifter(1.5), 16.0, 0.45)
for bar in (8, 9):
    root, ints = chord_at(bar)
    put(music, pad(root, ints, 2.0, 900), bar * 2.0, 0.55)
    for s in range(16):
        st = ints[[0, 1, 2, 1][s % 4]]
        put(music, pluck(root * 8 * 2 ** (st / 12)), bar * 2.0 + s * 0.125, 0.07)
put(drums, kick(big=True), 16.0, 0.7)
put(drums, kick(big=True), 17.0, 0.5)
roll = list(np.arange(18.0, 19.0, 0.25)) + list(np.arange(19.0, 19.5, 0.125)) + list(np.arange(19.5, 20.0, 0.0625))
for i, tt in enumerate(roll):
    put(drums, clap(), tt, 0.15 + 0.4 * i / len(roll))
put(fx, riser(2.0), 18.0, 0.6)

# Drop 2 (20–28)
for bar in range(10, 14):
    full_bar(bar, extra=True)

# Impactos y platillos
for tt, g in ((4.0, 0.9), (20.0, 1.0), (28.0, 1.0)):
    put(fx, impact(), tt, g)
    put(drums, crash(), tt, 0.35)
put(drums, crash(), 12.0, 0.25)
put(drums, crash(), 24.0, 0.25)

# Cierre 28–32
root, ints = chord_at(0)
put(music, pad(root, ints, 4.0, 1400), 28.0, 0.55)
put(music, bass_note(root, 2.5), 28.0, 0.6)

# ---------- mezcla ----------
# "Pumping": la música se agacha con cada bombo
duck = np.ones(N)
for tt in kick_times:
    i = int(tt * SR)
    seg = np.arange(min(int(0.35 * SR), N - i)) / SR
    duck[i : i + len(seg)] = np.minimum(duck[i : i + len(seg)], 1 - 0.55 * np.exp(-seg * 9))
music *= duck[:, None]

# Reverberación simple por convolución
irt = t_(2.2)
ir = np.stack([rng.standard_normal(len(irt)), rng.standard_normal(len(irt))], 1) * np.exp(-irt * 2.8)[:, None]
ir /= np.sqrt((ir ** 2).sum(0))
send = music * 0.35 + fx * 0.4 + drums * 0.08
wet = np.stack([fftconvolve(send[:, c], ir[:, c])[:N] for c in range(2)], 1)

mix = drums + music + fx + wet * 0.5
mix = np.tanh(mix * 1.1)
mix /= np.abs(mix).max() / 0.89
fade = np.ones(N); nf = int(0.8 * SR); fade[-nf:] = np.linspace(1, 0, nf)
mix *= fade[:, None]
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
print("ok", sys.argv[1])
