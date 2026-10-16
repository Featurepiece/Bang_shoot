# "Datasette Run" - an original C64-style tune, rendered with SID-like limits:
# 3 voices, pulse/saw/triangle/noise, 50 Hz (PAL) frame updates, arpeggio chords, drums sharing voice 3, resonant filter on the bass.
import numpy as np, scipy.signal as ss, wave, sys
SR=44100; FR=50; SPF=SR//FR; SPEED=5           # 5 frames per 16th step -> 150 BPM
def midi(n):
    names={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}; s=1 if '#' in n else 0
    return 12*(int(n[-1])+1)+names[n[0]]+s
def hz(m): return 440*2**((m-69)/12)
CH={'Am':(57,60,64),'F':(53,57,60),'C':(48,52,55),'G':(55,59,62),'E':(52,56,59),'Dm':(50,53,57),'Em':(52,55,59)}
# ---------- the composition ----------
A =[('Am',[('E5',6),('D5',2),('C5',2),('D5',2),('E5',4)]),('F',[('F5',4),('E5',2),('D5',2),('C5',6),('A4',2)]),
    ('C',[('G4',4),('C5',2),('E5',2),('G5',6),('F5',2)]),('G',[('E5',2),('D5',2),('B4',4),('D5',8)]),
    ('Am',[('E5',6),('D5',2),('C5',2),('D5',2),('E5',4)]),('F',[('A5',4),('G5',2),('F5',2),('E5',4),('C5',4)]),
    ('G',[('D5',2),('E5',2),('F5',2),('G5',2),('F5',2),('E5',2),('D5',2),('B4',2)]),('E',[('G#4',4),('B4',4),('E5',8)])]
A2=A[:6]+[('G',[('D5',4),('B4',2),('G4',2),('B4',4),('D5',4)]),('Am',[('A4',12),('-',4)])]
B =[('Dm',[('F5',2),('E5',2),('D5',2),('A4',2),('D5',2),('E5',2),('F5',4)]),('G',[('G5',2),('F5',2),('E5',2),('D5',2),('B4',4),('G4',4)]),
    ('C',[('E5',2),('D5',2),('C5',2),('G4',2),('C5',2),('D5',2),('E5',4)]),('Am',[('A5',6),('G5',2),('E5',8)]),
    ('Dm',[('F5',4),('A5',4),('D6',6),('C6',2)]),('E',[('B5',4),('G#5',4),('E5',4),('D5',2),('B4',2)]),
    ('Am',[('C5',2),('E5',2),('A5',2),('C6',2),('B5',2),('A5',2),('G#5',2),('A5',2)]),('E',[('B4',4),('E5',4),('G#5',4),('B5',4)])]
def arpbar(c):   # lead plays fast chord runs, two octaves up and back
    r=[x+12 for x in CH[c]]; seq=[r[0],r[1],r[2],r[0]+12,r[1]+12,r[2]+12,r[0]+24,r[2]+12]; seq=seq+seq[::-1]
    return (c,[(m,1) for m in seq])
ARP=[arpbar(c) for c in ['Am','F','C','G','Am','F','G','E']]
REST=lambda c:(c,[('-',16)])
# section: (bars, flags)  flags: lead on, bass style, chord arp on, drums style, filter sweep
SONG=[]
def sec(bars,**f):
    for b in bars: SONG.append((b,f))
sec([REST('Am')]*4,arp=False,drums='intro',sweep='open')
sec(A,arp=True,drums='full')
sec(A2,arp=True,drums='full')
sec([REST(c) for c in ['Am','Am','F','G']],arp=False,drums='full',bass='solo',sweep='wah')
sec(ARP,arp=False,drums='full')
sec(B,arp=True,drums='full')
sec(A,arp=True,drums='full')
sec(A2,arp=True,drums='full')
sec([('Am',[('A5',16)]),('Am',[('A5',8),('-',8)])],arp=True,drums='end')
# ---------- per-frame parameter tracks ----------
nb=len(SONG); NF=nb*16*SPEED+FR*2
V=[{'f':np.zeros(NF),'g':np.zeros(NF),'w':['p']*NF,'pw':np.full(NF,0.5)} for _ in range(3)]
def adsr(n,a=1,d=8,s=0.7,r=4,hold=None):
    hold=n-1 if hold is None else hold; e=np.zeros(n+r)
    for i in range(n+r):
        if i<a:e[i]=(i+1)/a
        elif i<hold:e[i]=max(s,1-(1-s)*(i-a)/max(1,d))
        else:e[i]=e[hold-1 if hold>0 else 0]*max(0,1-(i-hold+1)/r)
    return e
fr=0; prev=None
for bi,(bar,f) in enumerate(SONG):
    chord,notes=bar
    # lead (voice 1)
    t=fr
    for n,L in notes:
        nf=L*SPEED
        if n!='-':
            m=midi(n) if isinstance(n,str) else n
            env=adsr(nf,1,10,0.75,3)
            for i in range(nf+3):
                if t+i>=NF:break
                vib=0
                if L>=3 and i>8:vib=0.22*np.sin(2*np.pi*(i-8)/8)          # delayed vibrato
                slide=0
                if prev is not None and L>=2 and i<3:slide=(prev-m)*(1-i/3)  # quick portamento from the last note
                if i<nf or V[0]['g'][t+i]==0:
                    V[0]['f'][t+i]=hz(m+vib+slide);V[0]['g'][t+i]=max(V[0]['g'][t+i],env[i]) if i>=nf else env[i]
            prev=m
        t+=nf
    # bass (voice 2): galloping octaves, or a busy solo
    root=CH[chord][0]-24 if CH[chord][0]>=55 else CH[chord][0]-12
    if f.get('bass')=='solo': pat=[0,12,7,12,0,12,10,12,0,12,7,3,5,7,10,12]; st=[1]*16
    else: pat=[0,None,0,12,0,None,12,0,0,None,0,12,0,12,7,12]; st=[1]*16
    for s in range(16):
        if pat[s] is None:continue
        m=root+pat[s]+(12 if f.get('bass')=='solo' else 0); e=adsr(SPEED,1,3,0.5,2,hold=3)
        for i in range(SPEED):
            k=fr+s*SPEED+i;V[1]['f'][k]=hz(m);V[1]['g'][k]=e[i];V[1]['w'][k]='p';V[1]['pw'][k]=0.32+0.12*np.sin(k/40)
    # voice 3: chord arpeggio at 50 Hz, interrupted by drums
    for k in range(fr,fr+16*SPEED):
        if f.get('arp'):
            c=CH[chord];V[2]['f'][k]=hz(c[(k)%3]);V[2]['g'][k]=0.42;V[2]['w'][k]='p';V[2]['pw'][k]=0.5
    ds=f.get('drums')
    kick=[0,8,10] if ds=='full' else [0,8] if ds in('intro','end') else []
    snare=[4,12] if ds=='full' else [12] if ds=='intro' and bi%2 else []
    hat=[2,6,14] if ds=='full' else []
    if ds=='end' and bi==len(SONG)-1:kick=[0];snare=[];hat=[]
    for s in range(16):
        k0=fr+s*SPEED
        if s in kick:
            for i,(w,fq,g) in enumerate([('n',3000,1.0),('p',180,1.0),('p',120,0.9),('p',85,0.75),('p',62,0.5)]):V[2]['w'][k0+i]=w;V[2]['f'][k0+i]=fq;V[2]['g'][k0+i]=g;V[2]['pw'][k0+i]=0.5
        elif s in snare:
            for i,(w,fq,g) in enumerate([('p',260,0.9),('n',4500,1.0),('n',3800,0.8),('n',3000,0.55),('n',2500,0.3)]):V[2]['w'][k0+i]=w;V[2]['f'][k0+i]=fq;V[2]['g'][k0+i]=g;V[2]['pw'][k0+i]=0.4
        elif s in hat:
            V[2]['w'][k0]='n';V[2]['f'][k0]=9000;V[2]['g'][k0]=0.45
    fr+=16*SPEED
# lead pulse width sweeps slowly (the classic PWM shimmer)
for k in range(NF):V[0]['pw'][k]=0.28+0.18*np.sin(2*np.pi*k/120)
# ---------- render ----------
rng=np.random.default_rng(64);NOISE=rng.uniform(-1,1,1<<16)
out=np.zeros(NF*SPF)
for vi,v in enumerate(V):
    ph=0.0;nph=0.0;buf=np.zeros(NF*SPF);gprev=0
    for k in range(NF):
        g=v['g'][k];fq=v['f'][k]
        if g<=0 and gprev<=0:ph=0;continue
        n=np.arange(1,SPF+1);gg=gprev+(g-gprev)*n/SPF
        if v['w'][k]=='n':                      # SID noise: sample-and-hold at a rate set by the frequency
            idx=(nph+fq*n/SR*1.0).astype(np.int64);seg=NOISE[idx%len(NOISE)];nph+=fq*SPF/SR
        else:
            p=(ph+fq*n/SR)%1.0;seg=np.where(p<v['pw'][k],1.0,-1.0);ph=(ph+fq*SPF/SR)%1.0
        buf[k*SPF:(k+1)*SPF]=seg*gg;gprev=g
    if vi==1:                                   # resonant low-pass on the bass, its cutoff moving like a SID filter sweep
        y=np.zeros_like(buf);zi=np.zeros(2)
        for k in range(NF):
            bar=k//(16*SPEED);f=SONG[min(bar,len(SONG)-1)][1];sw=f.get('sweep')
            if sw=='open':fc=300+2200*min(1,(k%(64*SPEED))/(64*SPEED))
            elif sw=='wah':fc=500+1800*(0.5+0.5*np.sin(2*np.pi*k/(8*SPEED)))
            else:fc=1400+500*np.sin(2*np.pi*k/400)
            b,a=ss.iirpeak(fc,2.2,fs=SR) if False else ss.butter(2,fc/(SR/2))
            b2,a2=ss.iirpeak(fc,3.0,fs=SR)
            seg=buf[k*SPF:(k+1)*SPF];o,zi=ss.lfilter(b,a,seg,zi=zi*1.0) if k else ss.lfilter(b,a,seg,zi=ss.lfilter_zi(b,a)*0)
            y[k*SPF:(k+1)*SPF]=o
        res=ss.lfilter(*ss.iirpeak(900,2.0,fs=SR),y)
        buf=y+0.35*res
    out+=buf*[0.32,0.42,0.30][vi]
out=out[:fr*SPF+SR]                                   # let the last hit ring for a second
fade=np.ones_like(out);fade[-int(0.8*SR):]=np.linspace(1,0,int(0.8*SR))**2;out*=fade
out-=ss.lfilter([1],[1,-0.995],out)*0.005               # remove DC drift
out=ss.lfilter(*ss.butter(1,9000/(SR/2)),out)        # the C64's output was never bright; tame the very top
out/=np.abs(out).max()*1.12
w=wave.open(sys.argv[1],'wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype('<i2').tobytes());w.close()
print('bars',nb,'length',round(len(out)/SR,1),'s')
