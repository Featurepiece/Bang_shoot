"""Bang Shoot! sound effects, synthesised in code (sfxr-style retro arcade sounds).
Every sound is built from oscillators, noise, envelopes and filters, then given the same
'16-bit arcade' finish: light saturation, 22 kHz sample-and-hold and 12-bit crush, peak -6 dBFS
(matching the existing Suno sounds). Run: python3 synth.py OUTDIR"""
import sys, os, subprocess
import numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt

SR = 44100
rng = np.random.default_rng(7)          # fixed seed: same sounds every run

def t_axis(dur): return np.arange(int(dur * SR)) / SR

def sweep(f0, f1, dur, curve='exp'):
    t = t_axis(dur); k = t / dur
    if curve == 'exp': return f0 * (f1 / f0) ** k
    return f0 + (f1 - f0) * k

def osc(kind, freq, duty=0.5, phase0=0.0):
    """freq: array of Hz per sample. Phase-accumulating oscillator."""
    ph = (np.cumsum(freq) / SR + phase0) % 1.0
    if kind == 'sine': return np.sin(2 * np.pi * ph)
    if kind == 'square': return np.where(ph < duty, 1.0, -1.0)
    if kind == 'saw': return 2 * ph - 1
    if kind == 'tri': return 1 - 4 * np.abs(ph - 0.5)
    raise ValueError(kind)

def noise(n, hold=1):
    """white noise; hold>1 gives grainy sample-and-hold noise like old sound chips"""
    x = rng.uniform(-1, 1, int(np.ceil(n / hold)))
    return np.repeat(x, hold)[:n]

def env(n, attack=0.002, decay=0.1, shape=4.0, hold=0.0):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-5), 0, 1)
    d = np.where(t < attack + hold, 1.0, np.exp(-shape * (t - attack - hold) / max(decay, 1e-5)))
    return a * d

def lp(x, f, order=2):
    return sosfilt(butter(order, min(f, SR / 2 - 100), 'low', fs=SR, output='sos'), x)

def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, min(hi, SR / 2 - 100)], 'band', fs=SR, output='sos'), x)

def sweep_lp(x, f0, f1):
    """one-pole lowpass whose cutoff glides from f0 to f1 (for whooshes)"""
    n = len(x); fc = f0 * (f1 / f0) ** (np.arange(n) / n)
    a = 1 - np.exp(-2 * np.pi * fc / SR); y = np.zeros(n); s = 0.0
    for i in range(n): s += a[i] * (x[i] - s); y[i] = s
    return y

def pad(x, n):
    return np.pad(x, (0, max(0, n - len(x))))[:n]

def mix(*parts):
    n = max(len(p) for p in parts)
    return sum(pad(p, n) for p in parts)

def finish(x, crush_bits=12, hold=2, drive=1.6, fade_ms=4, peak_db=-6.0, top=8500):
    """the shared 'arcade' finish so every sound sits in the same family"""
    x = np.tanh(drive * x) / np.tanh(drive)
    if hold > 1: x = np.repeat(x[::hold], hold)[:len(x)]           # 22 kHz sample-and-hold grit
    q = 2 ** (crush_bits - 1); x = np.round(x * q) / q                 # bit crush
    x = hp(x, 35)                                                       # remove DC / rumble below hearing
    if top: x = lp(x, top, 4)                                           # tame the fizz: the Suno set has almost nothing above 10 kHz
    f = int(fade_ms / 1000 * SR)
    if f: x[-f:] *= np.linspace(1, 0, f)
    pk = np.max(np.abs(x)) or 1.0
    return x / pk * 10 ** (peak_db / 20)

def finish_loop(x, **kw):
    """same finish with no fade; processed over three copies and the middle one kept, so filters have
    settled and the end joins the start without a click"""
    kw['fade_ms'] = 0; n = len(x)
    return finish(np.tile(x, 3), **kw)[n:2 * n]

def circular(events, length):
    """place one-shot sounds at times on a loop, wrapping tails round to the start"""
    n = int(length * SR); y = np.zeros(n)
    for at, s in events:
        i = int(at * SR)
        for k in range(len(s)):
            y[(i + k) % n] += s[k]
    return y

# ------------------------------------------------------------------ the sounds
def hit_pulse():   # short dull thud of an energy bolt hitting metal armour
    d = 0.11; n = int(d * SR)
    body = osc('square', sweep(230, 60, d), duty=0.4) * env(n, 0.001, 0.07)
    thump = osc('sine', sweep(160, 45, d)) * env(n, 0.001, 0.09) * 1.2
    crack = lp(noise(n, 2), 2500) * env(n, 0.0005, 0.018, 5)
    ping = (osc('sine', np.full(n, 1870)) + 0.7 * osc('sine', np.full(n, 2740))) * env(n, 0.0005, 0.035, 5) * 0.18
    return finish(mix(lp(body, 1800) * 0.7, thump, crack * 0.8, ping))

def hit_laser():   # quick electric sizzle of a laser burning a hull
    d = 0.11; n = int(d * SR); t = t_axis(d)
    sizz = bp(noise(n), 2200, 7000) * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 140 * t)))
    zap = osc('saw', sweep(2600, 900, d)) * env(n, 0.0005, 0.05, 4)
    return finish(mix(sizz * env(n, 0.0005, 0.09, 4.5) * 0.8, hp(zap, 600) * 0.55), top=7500)

def hit_wave():    # bright bubbly pop of a sound-wave blast hitting a target
    d = 0.11; n = int(d * SR); t = t_axis(d); k = t / d
    f = 480 + 750 * np.sin(np.pi * np.clip(k * 1.6, 0, 1)) + 70 * np.sin(2 * np.pi * 55 * t)
    pop = osc('tri', f) * env(n, 0.001, 0.08, 4)
    click = hp(noise(n), 3000) * env(n, 0.0003, 0.006, 5) * 0.6
    bub = osc('sine', sweep(900, 1500, d)) * env(n, 0.02, 0.05, 5) * 0.35
    return finish(mix(pop, click, bub), drive=1.3)

def hit_homing():  # small sharp metallic tick of a mini-missile impact
    d = 0.12; n = int(d * SR)
    tick = bp(noise(n), 2500, 7000) * env(n, 0.0003, 0.012, 5)
    chirp = osc('square', sweep(1700, 550, 0.05), duty=0.3) * env(int(0.05 * SR), 0.0005, 0.04, 4)
    boom = osc('sine', sweep(140, 50, d)) * env(n, 0.001, 0.07, 4) * 0.9
    return finish(mix(tick * 1.1, lp(chirp, 4000) * 0.5, boom))

# ---- firing loops: rapid shots at the weapon's real fire rate, seamless when looped
def _shot_pulse(v):
    d = 0.07; n = int(d * SR)
    f = sweep(1150 * v, 260 * v, d)
    return lp(osc('square', f, 0.35), 3500) * env(n, 0.0008, 0.055, 4) + \
        hp(noise(n, 2), 2000) * env(n, 0.0003, 0.01, 5) * 0.5

def fire_pulse():
    rate = 0.085; shots = 24; L = rate * shots
    ev = [(i * rate, _shot_pulse(1 + 0.03 * np.sin(i * 1.7))) for i in range(shots)]
    return finish_loop(circular(ev, L), drive=1.4, top=6000)

def fire_laser():  # continuous beam hum with crackle (frequencies chosen to cycle exactly over the loop)
    L = 2.0; n = int(L * SR); t = np.arange(n) / SR
    f1, f2 = 440.0, 443.5                                   # whole numbers of cycles in 2 s -> seamless
    beam = osc('saw', np.full(n, f1)) + osc('saw', np.full(n, f2)) + 0.5 * osc('square', np.full(n, f1 * 2), 0.3)
    beam = bp(np.tile(beam, 3), 400, 2400)[n:2 * n] * (0.75 + 0.25 * np.sin(2 * np.pi * 14 * t))   # 14 Hz throb, 28 cycles
    pulse = 0.6 + 0.4 * (np.sin(2 * np.pi * (1 / 0.0714) * t) > 0)               # ~14 shots/s, matches 0.07 s rate
    crack = np.zeros(n)
    for _ in range(60):
        i = rng.integers(0, n); k = int(rng.uniform(0.002, 0.006) * SR)
        crack[np.arange(i, i + k) % n] += rng.uniform(-1, 1, k) * np.exp(-np.arange(k) / (k / 3))
    crack = bp(np.tile(crack, 3), 2500, 7000)[n:2 * n]
    return finish_loop(beam * pulse * 0.6 + crack * 0.3, drive=1.5, top=6500)

def _shot_wave():
    d = 0.11; n = int(d * SR); t = t_axis(d)
    f = sweep(280, 640, d) * (1 + 0.18 * np.sin(2 * np.pi * 38 * t))
    return lp(osc('tri', f) + 0.4 * osc('square', f / 2, 0.5), 2600) * env(n, 0.003, 0.09, 3.5)

def fire_wave():
    rate = 0.13; shots = 16; L = rate * shots
    return finish_loop(circular([(i * rate, _shot_wave()) for i in range(shots)], L), drive=1.3)

def _shot_homing(i):
    d = 0.09; n = int(d * SR)
    wh = sweep_lp(noise(n), 700, 3500) * env(n, 0.004, 0.08, 3.5)
    ch = osc('sine', sweep(700 + 40 * (i % 3), 1500, d)) * env(n, 0.002, 0.06, 4) * 0.35
    th = osc('sine', sweep(180, 70, 0.04)) * env(int(0.04 * SR), 0.0005, 0.03, 4) * 0.6
    return mix(hp(wh, 400), ch, th)

def fire_homing():
    rate = 0.085; shots = 24; L = rate * shots
    return finish_loop(circular([(i * rate, _shot_homing(i)) for i in range(shots)], L), drive=1.3, top=6000)

def player_hurt():  # hull struck: harsh metallic clang with an electric zap
    d = 0.32; n = int(d * SR); t = t_axis(d)
    parts = [(523, 0.22, 1.0), (1291, 0.16, 0.7), (1873, 0.12, 0.55), (2741, 0.08, 0.45), (3517, 0.06, 0.3)]
    clang = sum(a * osc('sine', np.full(n, f)) * env(n, 0.0005, dec, 4) for f, dec, a in parts)
    hitn = lp(noise(n, 2), 4000) * env(n, 0.0005, 0.03, 5)
    zapf = 1100 + 500 * np.sign(np.sin(2 * np.pi * 72 * t))
    zap = osc('square', zapf, 0.3) * osc('square', np.full(n, 61.0)) * env(n, 0.001, 0.14, 3)
    thud = osc('sine', sweep(120, 45, d)) * env(n, 0.001, 0.12, 4)
    return finish(mix(clang * 0.55, hitn * 0.8, lp(zap, 3500) * 0.35, thud * 0.9), drive=2.0)

def low_health():   # urgent single cockpit warning beep
    d = 0.2; n = int(d * SR)
    f = np.full(n, 880.0); f[: int(0.012 * SR)] = 1320                 # tiny pitch blip on the front edge
    beep = osc('square', f, 0.25) + 0.35 * osc('square', f / 2, 0.5)
    e = env(n, 0.003, 0.05, 5, hold=0.11)
    return finish(lp(beep, 5000) * e, drive=1.2)

SOUNDS = {
    'hit-pulse': hit_pulse, 'hit-laser': hit_laser, 'hit-wave': hit_wave, 'hit-homing': hit_homing,
    'fire-pulse': fire_pulse, 'fire-laser': fire_laser, 'fire-wave': fire_wave, 'fire-homing': fire_homing,
    'player-hurt': player_hurt, 'low-health': low_health,
}

if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    from scipy.io import wavfile
    for name, fn in SOUNDS.items():
        x = fn(); wav = os.path.join(out, name + '.wav')
        wavfile.write(wav, SR, (x * 32767).astype(np.int16))
        # loops go to OGG-free MP3 with no padding tricks; game loops them with loopStart/loopEnd if needed
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-ac', '1', '-b:a', '112k', os.path.join(out, name + '.mp3')], check=True)
        print(f'{name:12s} {len(x)/SR:5.2f}s  peak {20*np.log10(np.max(np.abs(x))):.1f} dBFS')
