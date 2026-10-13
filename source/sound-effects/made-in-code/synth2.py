"""The rest of the Bang Shoot! sound set, same toolkit and finish as synth.py."""
import numpy as np
from synth import (SR, rng, t_axis, sweep, osc, noise, env, lp, hp, bp, sweep_lp, pad, mix,
                   finish, finish_loop, circular)

def N(d): return int(d * SR)
def at(x, t, total):
    """place sound x starting at t seconds inside a buffer of `total` seconds"""
    y = np.zeros(N(total)); i = N(t); k = min(len(x), len(y) - i); y[i:i + k] += x[:k]; return y
def partials(n, fs, decs, amps):
    return sum(a * osc('sine', np.full(n, float(f))) * env(n, 0.0005, d, 4) for f, d, a in zip(fs, decs, amps))

# ---------------- weapons and pickups
def charge_loop():      # steady charging hum; the game raises its pitch as the charge builds
    L = 2.0; n = N(L); t = np.arange(n) / SR
    x = osc('saw', np.full(n, 110.0)) + osc('saw', np.full(n, 110.5)) + 0.5 * osc('square', np.full(n, 220.0), 0.3)
    x = lp(np.tile(x, 3), 1400)[n:2 * n] * (0.8 + 0.2 * np.sin(2 * np.pi * 16 * t))
    sh = bp(np.tile(noise(n), 3), 2000, 5000)[n:2 * n] * 0.12
    return finish_loop(x * 0.6 + sh, drive=1.4, top=6000)

def charge_release():   # massive piercing beam blast with a deep boom
    d = 0.8; n = N(d)
    blast = sweep_lp(noise(n), 8000, 300) * env(n, 0.002, 0.6, 3.5)
    beam = osc('saw', sweep(700, 60, d)) * env(n, 0.002, 0.45, 3)
    sub = osc('sine', sweep(95, 32, d)) * env(n, 0.002, 0.7, 3) * 1.4
    return finish(mix(blast, lp(beam, 3500) * 0.6, sub), drive=2.2)

def weapon_swap():      # mechanical click-clack with a rising chirp
    d = 0.22
    click = lambda: hp(noise(N(0.008)), 2500) * env(N(0.008), 0.0002, 0.006, 5)
    chirp = osc('square', sweep(520, 1040, 0.08), 0.3) * env(N(0.08), 0.001, 0.07, 3)
    return finish(mix(at(click(), 0, d), at(click() * 0.8, 0.055, d), at(lp(chirp, 5000) * 0.5, 0.07, d)))

def missile_launch():   # small missile: ignition thump and a short whoosh
    d = 0.3; n = N(d)
    wh = hp(sweep_lp(noise(n), 600, 3500), 300) * env(n, 0.01, 0.22, 3)
    th = osc('sine', sweep(170, 60, 0.06)) * env(N(0.06), 0.0005, 0.05, 4)
    return finish(mix(wh, th * 0.8), top=7000)

def bomb_drop():        # descending whistle of a falling bomb
    d = 0.5; n = N(d); t = t_axis(d)
    f = sweep(1800, 520, d) * (1 + 0.012 * np.sin(2 * np.pi * 9 * t))
    w = osc('sine', f) + 0.25 * osc('tri', f * 2)
    return finish(w * env(n, 0.02, 0.45, 1.5) + hp(noise(n), 4000) * env(n, 0.02, 0.4, 2) * 0.05, drive=1.1)

# ---------------- enemies
def enemy_missile():    # heavy enemy missile: low rumble and ignition
    d = 0.4; n = N(d)
    rum = osc('saw', sweep(95, 60, d)) * env(n, 0.003, 0.3, 3)
    ign = sweep_lp(noise(n), 400, 2200) * env(n, 0.003, 0.3, 3)
    return finish(mix(lp(rum, 900) * 0.8, ign, osc('sine', sweep(600, 200, 0.08)) * env(N(0.08), 0.001, 0.06, 4) * 0.3), drive=1.8)

def armour_chip():      # chunk of armour breaking off: crunch and clang
    d = 0.3; n = N(d)
    crunch = lp(noise(n, 3), 3200) * env(n, 0.0005, 0.08, 4)
    clang = partials(n, [310, 733, 1151, 1690], [0.2, 0.15, 0.1, 0.07], [1, .6, .45, .3])
    return finish(mix(crunch, clang * 0.5), drive=1.8)

def armour_clang():     # bullet ricocheting off thick armour: bright ping
    d = 0.16; n = N(d)
    bend = sweep(1, 0.94, d)
    ping = sum(a * osc('sine', f * bend) * env(n, 0.0005, dd, 4) for f, dd, a in [(1500, .12, 1), (2380, .09, .6), (3310, .06, .4)])
    return finish(ping + hp(noise(n), 4000) * env(n, 0.0003, 0.005, 5) * 0.5, drive=1.2)

def cloaker():          # ship shimmering into view: rising phase sweep
    d = 0.42; n = N(d); t = t_axis(d)
    f = sweep(380, 1400, d)
    x = (osc('sine', f) + osc('sine', f * 1.012)) * (0.6 + 0.4 * np.sin(2 * np.pi * 32 * t))
    air = bp(noise(n), 3000, 7000) * 0.15
    return finish((x * 0.6 + air) * env(n, 0.15, 0.25, 3, hold=0.02), drive=1.2)

def dive():             # fighter diving: descending engine roar
    d = 0.42; n = N(d)
    eng = osc('saw', sweep(520, 140, d)) + osc('saw', sweep(525, 141, d))
    rush = sweep_lp(noise(n), 3000, 600) * 0.6
    return finish(mix(lp(eng, 2500) * 0.5, rush) * env(n, 0.02, 0.38, 2.5), drive=1.6)

def kamikaze():         # drone revving then rushing forward
    d = 0.42; n = N(d); t = t_axis(d)
    buzz = osc('square', sweep(170, 300, d), 0.4) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 42 * t)))
    rush = hp(sweep_lp(noise(n), 500, 4000), 300) * np.clip((t - 0.2) / 0.1, 0, 1)
    return finish(mix(lp(buzz, 2200) * 0.6, rush * 0.7) * env(n, 0.01, 0.4, 2), drive=1.7)

def crystal_shot():     # crystal turret: glassy ringing zing
    d = 0.22; n = N(d)
    zing = osc('tri', sweep(2000, 950, 0.12)) * env(N(0.12), 0.0005, 0.1, 4)
    ring = partials(n, [2400, 3610, 5070], [0.18, 0.14, 0.1], [.5, .35, .25])
    return finish(mix(zing, ring), drive=1.1, top=9000)

def spit():             # acid spit: wet gurgle and splat
    d = 0.3; n = N(d)
    f = sweep(200, 90, d) * (1 + 0.35 * np.repeat(rng.uniform(-1, 1, n // 400 + 1), 400)[:n])
    gur = osc('sine', f) * env(n, 0.005, 0.22, 3)
    splat = lp(noise(n), 1500) * env(n, 0.001, 0.05, 4)
    return finish(mix(gur, splat * 0.7), drive=1.6)

def egg_burst():        # egg sac bursting: wet squelch and crack
    d = 0.42; n = N(d)
    sq = lp(noise(n), 900) * np.repeat(rng.uniform(0.3, 1, n // 300 + 1), 300)[:n] * env(n, 0.002, 0.3, 3)
    crack = hp(noise(N(0.02)), 2500) * env(N(0.02), 0.0003, 0.015, 5)
    thump = osc('sine', sweep(130, 50, 0.15)) * env(N(0.15), 0.001, 0.12, 4)
    return finish(mix(sq, crack * 0.6, thump), drive=1.8)

def carrier_launch():   # hangar bay launching a drone: thunk and whoosh
    d = 0.32; n = N(d)
    thunk = mix(osc('sine', sweep(130, 55, 0.08)) * env(N(0.08), 0.0005, 0.07, 4), lp(noise(N(0.04)), 1200) * env(N(0.04), 0.0005, 0.03, 4))
    wh = hp(sweep_lp(noise(n), 800, 3000), 400) * env(n, 0.03, 0.25, 3)
    return finish(mix(thunk, at(wh * 0.6, 0.03, d)), drive=1.5)

def crystal_fall():     # falling crystal: glassy whistling drop
    d = 0.42; n = N(d)
    f = sweep(1900, 880, d)
    x = osc('tri', f) + 0.3 * osc('sine', f * 2.01)
    return finish(x * env(n, 0.01, 0.38, 2) + partials(n, [3200, 4700], [.2, .15], [.15, .1]), drive=1.1, top=9000)

# ---------------- bosses and warnings
def boss_tell():        # giant ship powering up: ominous rising charge
    d = 0.8; n = N(d); t = t_axis(d)
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(sweep(6, 26, d)) / SR)
    x = osc('saw', sweep(80, 330, d)) + osc('saw', sweep(81, 333, d))
    x = sweep_lp(x, 300, 3200) * trem
    sub = osc('sine', sweep(45, 90, d)) * 0.8
    return finish((x * 0.6 + sub) * env(n, 0.2, 0.05, 3, hold=0.55), drive=1.6)

def boss_launch():      # small ships released from a mothership: clank and whoosh
    d = 0.4; n = N(d)
    clank = mix(partials(N(0.15), [420, 980], [.1, .07], [1, .5]), lp(noise(N(0.02)), 2500) * env(N(0.02), 0.0003, 0.015, 4))
    wh = hp(sweep_lp(noise(n), 600, 4000), 300) * env(n, 0.05, 0.3, 3)
    return finish(mix(clank * 0.7, at(wh * 0.7, 0.02, d)), drive=1.5)

def crystal_break():    # crystal shield shattering
    d = 0.45; n = N(d); y = np.zeros(n)
    for _ in range(22):
        s = rng.uniform(0, 0.25); f = rng.uniform(2200, 6500); k = N(rng.uniform(0.04, 0.12))
        y += at(osc('sine', np.full(k, f)) * env(k, 0.0003, k / SR, 5) * rng.uniform(0.2, 0.6), s, d)
    crack = hp(noise(N(0.03)), 3000) * env(N(0.03), 0.0003, 0.025, 5)
    return finish(mix(y, crack * 0.8), drive=1.2, top=9000)

def new_enemy():        # two-note alert chime
    d = 0.42
    note = lambda f: (osc('tri', np.full(N(0.25), f)) + 0.4 * osc('sine', np.full(N(0.25), f * 2))) * env(N(0.25), 0.002, 0.22, 4)
    return finish(mix(at(note(660), 0, d), at(note(990), 0.12, d)), drive=1.1)

def _beep(f, d, duty=0.5):
    n = N(d); return lp(osc('square', np.full(n, f), duty), 4500) * env(n, 0.002, 0.03, 5, hold=d - 0.035)

def rear_warning():     # three fast urgent beeps
    d = 0.6; return finish(sum(at(_beep(520, 0.1, 0.3), i * 0.2, d) for i in range(3)))

def tunnel_warning():   # two-tone caution alert
    d = 0.75; return finish(mix(at(_beep(587, 0.22, 0.4), 0, d), at(_beep(392, 0.3, 0.4), 0.3, d)))

def miniboss_arrive():  # heavy warship arriving: deep descending horn
    d = 1.0; n = N(d)
    horn = osc('saw', sweep(220, 105, d)) + osc('saw', sweep(222, 106, d)) + osc('saw', sweep(110, 52, d))
    return finish(lp(horn, 1300) * env(n, 0.08, 0.3, 3, hold=0.55) * 0.6 + osc('sine', sweep(55, 30, d)) * env(n, 0.05, 0.6, 2), drive=1.8)

def miniboss_rage():    # machine overheating into a rage
    d = 0.8; n = N(d); t = t_axis(d)
    x = osc('saw', sweep(85, 230, d)) * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 26 * t)))
    grind = bp(noise(n), 400, 2000) * 0.4
    return finish((lp(x, 2500) + grind) * env(n, 0.05, 0.3, 3, hold=0.4), drive=2.4)

# ---------------- stage 5, the Robot Base
def door_alarm():       # industrial klaxon, four blasts
    d = 1.3; n = N(0.24)
    blast = lambda: lp(osc('saw', np.full(n, 330.0)) + osc('saw', np.full(n, 333.0)) + osc('square', np.full(n, 440.0), 0.5) * 0.5, 1800) * env(n, 0.01, 0.03, 5, hold=0.19)
    return finish(sum(at(blast(), i * 0.32, d) for i in range(4)), drive=1.8)

def door_blast():       # huge blast door blown open: explosion and tearing metal
    d = 1.5; n = N(d)
    boom = sweep_lp(noise(n), 5000, 150) * env(n, 0.002, 1.2, 3)
    sub = osc('sine', sweep(80, 28, d)) * env(n, 0.003, 1.1, 2.5) * 1.3
    tear = osc('saw', sweep(900, 260, 0.6) * (1 + 0.04 * np.sin(2 * np.pi * 37 * t_axis(0.6)))) * env(N(0.6), 0.02, 0.55, 3)
    return finish(mix(boom, sub, at(bp(tear, 400, 2500) * 0.35, 0.05, d)), drive=2.2)

def foundry_alarm():    # factory siren wailing, low and menacing
    d = 1.5; n = N(d); t = t_axis(d)
    f = 300 + 260 * np.sin(np.pi * t / d) ** 2
    x = osc('saw', f) + osc('saw', f * 1.005)
    return finish(lp(x, 1600) * env(n, 0.15, 0.25, 3, hold=1.05) * 0.6, drive=1.5)

def press_warning():    # two warning beeps before the press slams
    d = 0.4; return finish(mix(at(_beep(880, 0.08, 0.25), 0, d), at(_beep(880, 0.08, 0.25), 0.25, d)))

def press_slam():       # giant hydraulic press: massive impact and hiss
    d = 0.65; n = N(d)
    sub = osc('sine', sweep(85, 30, d)) * env(n, 0.001, 0.4, 3) * 1.4
    hit = lp(noise(n), 1600) * env(n, 0.0005, 0.12, 4)
    clang = partials(n, [212, 531, 877], [.3, .2, .12], [1, .5, .3]) * 0.5
    hiss = hp(noise(n), 3000) * env(n, 0.08, 0.35, 3) * 0.18
    return finish(mix(sub, hit, clang, at(hiss, 0.1, d)), drive=2.2)

def zap_charge():       # electric magnet charging: rising crackle
    d = 0.85; n = N(d); t = t_axis(d)
    hum = osc('saw', sweep(180, 900, d)) * 0.4
    dens = (t / d) ** 2
    crack = hp(noise(n), 2500) * (rng.uniform(0, 1, n) < 0.02 + 0.25 * dens) * 0.9
    return finish((lp(hum, 3000) + lp(crack, 7000)) * env(n, 0.05, 0.05, 3, hold=0.72), drive=1.6)

def zap_fire():         # lightning bolt discharge: loud crack and buzz
    d = 0.85; n = N(d); t = t_axis(d)
    gate = np.repeat(rng.uniform(0, 1, n // 220 + 1) > 0.35, 220)[:n]
    crack = hp(noise(n), 1200) * gate * env(n, 0.0005, 0.6, 3)
    buzz = osc('square', np.full(n, 60.0)) * osc('square', np.full(n, 1100.0), 0.3) * env(n, 0.005, 0.7, 2.5) * 0.4
    thump = osc('sine', sweep(110, 40, 0.2)) * env(N(0.2), 0.0005, 0.18, 4)
    return finish(mix(crack, lp(buzz, 3500), thump), drive=2.2)

def titan_build():      # assembly line: servo whirr and clunk
    d = 0.5; n = N(d); t = t_axis(d)
    f = 200 + 220 * np.sin(np.pi * np.clip(t / 0.36, 0, 1))
    whirr = lp(osc('saw', f) + osc('square', f * 1.5, 0.3) * 0.4, 1800) * env(n, 0.03, 0.05, 3, hold=0.3)
    clunk = mix(osc('sine', sweep(120, 50, 0.12)) * env(N(0.12), 0.0005, 0.1, 4), lp(noise(N(0.03)), 2000) * env(N(0.03), 0.0005, 0.02, 4))
    return finish(mix(pad(whirr, n) * 0.5, at(clunk, 0.36, d)), drive=1.7)

# ---------------- menus and ending
def menu_move():
    n = N(0.05); return finish(osc('square', np.full(n, 660.0), 0.25) * env(n, 0.001, 0.04, 5), drive=1.1, peak_db=-9)

def menu_select():
    d = 0.18
    note = lambda f: osc('square', np.full(N(0.09), f), 0.25) * env(N(0.09), 0.001, 0.08, 4)
    return finish(mix(at(note(880), 0, d), at(note(1320), 0.06, d)), drive=1.1, peak_db=-8)

def text_tick():
    n = N(0.04); return finish(osc('tri', np.full(n, 1250.0)) * env(n, 0.0005, 0.02, 5) + hp(noise(n), 3000) * env(n, 0.0002, 0.004, 5) * 0.5, drive=1.0, peak_db=-12)

def firework():         # firework burst with crackle
    d = 1.1; n = N(d)
    boom = sweep_lp(noise(n), 3500, 200) * env(n, 0.002, 0.45, 3)
    cr = np.zeros(n)
    for _ in range(70):
        s = rng.uniform(0.12, 0.95); k = N(0.004)
        cr += at(hp(noise(k), 2500) * rng.uniform(0.2, 0.7), s, d)
    return finish(mix(boom, cr * env(n, 0.1, 0.8, 1.5)), drive=1.5)

def hyperdrive():       # jump to hyperspace: huge rising whoosh
    d = 1.3; n = N(d)
    wh = sweep_lp(noise(n), 500, 7000)
    saw = osc('saw', sweep(140, 1400, d)) + osc('saw', sweep(141, 1410, d))
    return finish((wh + lp(saw, 4000) * 0.35) * env(n, 0.6, 0.12, 4, hold=0.55), drive=1.6)

SOUNDS2 = {
    'charge-loop': charge_loop, 'charge-release': charge_release, 'weapon-swap': weapon_swap,
    'missile-launch': missile_launch, 'bomb-drop': bomb_drop,
    'enemy-missile': enemy_missile, 'armour-chip': armour_chip, 'armour-clang': armour_clang, 'cloaker': cloaker,
    'dive': dive, 'kamikaze': kamikaze, 'crystal-shot': crystal_shot, 'spit': spit, 'egg-burst': egg_burst,
    'carrier-launch': carrier_launch, 'crystal-fall': crystal_fall,
    'boss-tell': boss_tell, 'boss-launch': boss_launch, 'crystal-break': crystal_break, 'new-enemy': new_enemy,
    'rear-warning': rear_warning, 'tunnel-warning': tunnel_warning, 'miniboss-arrive': miniboss_arrive, 'miniboss-rage': miniboss_rage,
    'door-alarm': door_alarm, 'door-blast': door_blast, 'foundry-alarm': foundry_alarm, 'press-warning': press_warning,
    'press-slam': press_slam, 'zap-charge': zap_charge, 'zap-fire': zap_fire, 'titan-build': titan_build,
    'menu-move': menu_move, 'menu-select': menu_select, 'text-tick': text_tick, 'firework': firework, 'hyperdrive': hyperdrive,
}
