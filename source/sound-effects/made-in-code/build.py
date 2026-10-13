import os, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
from synth import SOUNDS, SR
from synth2 import SOUNDS2
ALL = {**SOUNDS, **SOUNDS2}
os.makedirs('out', exist_ok=True); os.makedirs('game', exist_ok=True)
for name, fn in ALL.items():
    x = fn()
    assert np.isfinite(x).all(), name
    wavfile.write(f'out/{name}.wav', SR, (x * 32767).astype(np.int16))
    # game copy at 22.05 kHz (the sounds are band-limited below 9 kHz, so nothing is lost)
    if name.startswith(('fire-', 'charge-loop')):
        y = x[::2]                                   # straight decimation keeps loop length exact
    else:
        y = resample_poly(x, 1, 2)
    wavfile.write(f'game/{name}.wav', SR // 2, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    s = np.abs(np.fft.rfft(x)); fr = np.fft.rfftfreq(len(x), 1 / SR)
    print(f'{name:16s} {len(x)/SR:5.2f}s  rms {20*np.log10(np.sqrt(np.mean(x**2))):6.1f}  centroid {(s*fr).sum()/s.sum():5.0f} Hz')
