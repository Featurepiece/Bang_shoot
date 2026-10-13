"""Split armour clang: a light tick on every hit, a heavy impact about every half second. Five takes of each so repeats vary."""
import numpy as np
from scipy.io import wavfile
from kenney_mix import k, done, SR
S = {}
for i in range(5):
    S[f'tick-{i}'] = done([(k(f'impactMetal_light_00{i}'), 0, 1)], min(0.3, len(k(f'impactMetal_light_00{i}')) / SR), 0.05)
    S[f'heavy-{i}'] = done([(k(f'impactPlate_heavy_00{i}', 0.85), 0, 1), (k(f'impactPunch_heavy_00{(i + 2) % 5}'), 0, 0.75),
                            (k(f'impactMetal_heavy_00{i}', 0.9), 0.0, 0.6)], 0.55, 0.06)
for n, x in S.items():
    wavfile.write(f'alt/{n}-full.wav', SR, (x * 32767).astype(np.int16)); print(n, f'{len(x)/SR:.2f}s')
