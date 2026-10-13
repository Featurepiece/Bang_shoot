"""Armour sounds built from real recordings (Kenney Impact Sounds, CC0) plus the game's own Suno explosions.
Light touch only: trim, layer, a little pitch-down for size, peak -6 dBFS. No synth 'finish' (that is what made the last ones flat)."""
import os, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
SR = 44100; K = '../kenney/wav/'
def load(p, rate=1.0):
    sr, x = wavfile.read(p); x = x.astype(float) / 32767
    if rate != 1.0: x = resample_poly(x, 100, int(round(100 * rate)))   # rate<1 = lower and longer
    return x
def k(name, rate=1.0): return load(K + name + '.wav', rate)
def boom(name, dur, rate=1.0): return load(f'ref-Explosion - {name}.wav', rate)[: int(dur * SR)]
def at(x, t, total):
    y = np.zeros(int(total * SR)); i = int(t * SR); n = min(len(x), len(y) - i); y[i:i + n] += x[:n]; return y
def done(parts, total, fade=0.04):
    y = sum(at(x * g, t, total) for x, t, g in parts)
    y = np.tanh(1.3 * y) / np.tanh(1.3)                     # gentle glue, keeps the transient
    f = int(fade * SR); y[-f:] *= np.linspace(1, 0, f)
    return y / np.max(np.abs(y)) * 10 ** (-6 / 20)

S = {
 # ---- clang: Titan's armour taking hits (short, plays often)
 'kc-1': done([(k('impactMetal_heavy_001'), 0, 1)], 0.36),
 'kc-2': done([(k('impactPlate_heavy_001'), 0, 1)], 0.35),
 'kc-3': done([(k('impactMetal_heavy_003'), 0, 1), (k('impactPunch_heavy_002'), 0, 0.8)], 0.42),
 'kc-4': done([(k('impactPlate_heavy_003', 0.85), 0, 1), (k('impactPunch_heavy_000'), 0, 0.7)], 0.5),
 # ---- chunk: a big piece of a boss breaking off
 'kk-1': done([(k('impactMining_000'), 0, 1)], 0.94, 0.08),
 'kk-2': done([(boom('small', 0.8), 0, 0.9), (k('impactPlate_heavy_004'), 0, 1), (k('impactMetal_heavy_001', 0.85), 0.12, 0.8),
               (k('impactMetal_medium_002'), 0.32, 0.45), (k('impactMetal_medium_004'), 0.45, 0.35)], 0.85, 0.1),
 'kk-3': done([(k('impactMining_003'), 0, 1), (k('impactMetal_heavy_000', 0.8), 0, 0.9), (boom('medium', 0.9), 0.05, 0.6)], 1.0, 0.12),
}
os.makedirs('alt', exist_ok=True)
for n, x in S.items():
    wavfile.write(f'alt/{n}-full.wav', SR, (x * 32767).astype(np.int16))
    wavfile.write(f'alt/{n}.wav', SR // 2, (np.clip(resample_poly(x, 1, 2), -1, 1) * 32767).astype(np.int16))
    print(n, f'{len(x)/SR:.2f}s')
