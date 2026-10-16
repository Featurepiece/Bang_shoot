# "Claude does C64" v3 (lead articulation measured from the same player: hard restart, stepped vibrato, linear PWM, octave-flick attacks)
# "Claude does C64" v2 - original tune; sound design from measurements of a real Rob Hubbard SID player:
#  voice 1 lead (pulse, width sweeps, shallow vibrato) | voice 2 drums only, built from shaped noise | voice 3 bass (pulse, 8ths)
#  4-frame step grid at 50 Hz = 187.5 BPM, bass as loud as the lead, no filter, arpeggios only as flourishes
import numpy as np, scipy.signal as ss, wave, sys
SR=44100; FR=50; SPF=SR//FR; SPEED=4
CLK=985248
def midi(n):
    names={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}; return 12*(int(n[-1])+1)+names[n[0]]+(1 if '#' in n else 0)
def hz(m): return 440*2**((m-69)/12)
CH={'Am':(57,60,64),'F':(53,57,60),'C':(48,52,55),'G':(55,59,62),'E':(52,56,59),'Dm':(50,53,57)}
A =[('Am',[('E5',6),('D5',2),('C5',2),('D5',2),('E5',4)]),('F',[('F5',4),('E5',2),('D5',2),('C5',6),('A4',2)]),
    ('C',[('G4',4),('C5',2),('E5',2),('G5',6),('F5',2)]),('G',[('E5',2),('D5',2),('B4',4),('D5',8)]),
    ('Am',[('E5',6),('D5',2),('C5',2),('D5',2),('E5',4)]),('F',[('A5',4),('G5',2),('F5',2),('E5',4),('C5',4)]),
    ('G',[('D5',2),('E5',2),('F5',2),('G5',2),('F5',2),('E5',2),('D5',2),('B4',2)]),('E',[('G#4',4),('B4',4),('arp',8)])]
A2=A[:6]+[('G',[('D5',4),('B4',2),('G4',2),('B4',4),('D5',4)]),('Am',[('A4',8),('arp',8)])]
B =[('Dm',[('F5',2),('E5',2),('D5',2),('A4',2),('D5',2),('E5',2),('F5',4)]),('G',[('G5',2),('F5',2),('E5',2),('D5',2),('B4',4),('G4',4)]),
    ('C',[('E5',2),('D5',2),('C5',2),('G4',2),('C5',2),('D5',2),('E5',4)]),('Am',[('A5',6),('G5',2),('E5',8)]),
    ('Dm',[('F5',4),('A5',4),('D6',6),('C6',2)]),('E',[('B5',4),('G#5',4),('E5',4),('D5',2),('B4',2)]),
    ('Am',[('C5',2),('E5',2),('A5',2),('C6',2),('B5',2),('A5',2),('G#5',2),('A5',2)]),('E',[('B4',4),('E5',4),('arp',8)])]
def runbar(c):
    r=[x+12 for x in CH[c]];seq=[r[0],r[1],r[2],r[0]+12,r[1]+12,r[2]+12,r[0]+24,r[2]+12];seq=seq+seq[::-1];return (c,[(m,1) for m in seq])
RUNS=[runbar(c) for c in ['Am','F','C','G','Am','F','G','E']]
REST=lambda c:(c,[('-',16)])
SONG=[]
def sec(bars,**f):
    for b in bars:SONG.append((b,f))
sec([REST('Am')]*4,drums='intro')
sec(A,drums='full');sec(A2,drums='full');sec(B,drums='full')
sec([REST(c) for c in ['Am','Am','F','G']],drums='full',bass='solo')
sec(RUNS,drums='full');sec(B,drums='full');sec(A,drums='full');sec(A2,drums='full')
sec([('Am',[('A5',16)]),('Am',[('A5',4),('-',12)])],drums='end')
nb=len(SONG);NF=nb*16*SPEED+FR*2
V=[{'f':np.zeros(NF),'g':np.zeros(NF),'w':['p']*NF,'pw':np.full(NF,0.5)} for _ in range(3)]
def env(n,s,dec,rel):     # attack 0, decay to sustain s over dec frames, release over rel frames after the gate
    e=np.zeros(n+rel)
    for i in range(n+rel):e[i]=max(s,1-(1-s)*i/max(1,dec)) if i<n else e[n-1]*max(0,1-(i-n+1)/rel)
    return e
fr=0;prev=None
for bi,(bar,f) in enumerate(SONG):
    chord,notes=bar;t=fr
    for n,L in notes:                                             # ---- voice 1: lead
        nf=L*SPEED
        if n=='arp':                                              # flourish: a fast chord arpeggio at 50 Hz
            c=[x+12 for x in CH[chord]];e=env(nf,0.47,6,3)
            for i in range(nf):
                if t+i<NF:V[0]['f'][t+i]=hz(c[i%3]);V[0]['g'][t+i]=e[i] if i<nf-2 else 0
        elif n!='-':
            m=midi(n) if isinstance(n,str) else n
            gate=max(1,nf-2)                                       # hard restart: gate off for the last 2 frames of every note
            VIB=[-25,-13,0,13,13,0,-13,-25]                        # stepped vibrato in cents, one step per frame, from the first frame
            nidx=globals().setdefault('_nidx',[0]);nidx[0]+=1
            orn='oct' if (L>=4 and nidx[0]%5==0) else 'noise' if (L>=4 and nidx[0]%11==3) else None
            for i in range(nf):
                if t+i>=NF:break
                if i>=gate:V[0]['g'][t+i]=0;continue
                g_=min(1,(i+1)/2)*max(0.47,1-(1-0.47)*i/6)        # quick attack, decay to sustain 6/15
                cents=VIB[i%8] if L>=4 else 0
                mm_=m
                if orn=='oct' and i in(0,2):mm_=m-12               # octave-down flick on the attack
                V[0]['f'][t+i]=hz(mm_+cents/100);V[0]['g'][t+i]=g_
                if orn=='noise' and i==1:V[0]['w'][t+i]='n';V[0]['f'][t+i]=hz(m+1)
            prev=m
        t+=nf
    root=CH[chord][0]-24 if CH[chord][0]>=55 else CH[chord][0]-12   # ---- voice 3: bass in 8ths
    if f.get('bass')=='solo':pat=[(0,1),(12,1),(7,1),(12,1),(10,1),(12,1),(7,1),(3,1),(5,1),(7,1),(10,1),(12,1),(15,1),(12,1),(10,1),(7,1)];sub=1
    else:pat=[(0,2),(12,2),(0,2),(12,2),(0,2),(12,2),(7,2),(12,2)];sub=2
    s=0
    for iv,ln in pat:
        nf=ln*SPEED;m=root+iv+(12 if f.get('bass')=='solo' else 0);e=env(nf-1,0.55,5,2)
        for i in range(nf):
            k=fr+s*SPEED+i;V[2]['f'][k]=hz(m);V[2]['g'][k]=e[i];V[2]['pw'][k]=0.35+0.2*np.sin(k/90)
        s+=ln
    ds=f.get('drums')                                              # ---- voice 2: drums, noise only
    kick=[0,8] if ds in('full','intro','end') else [];snare=[4,12] if ds=='full' else [12] if ds=='intro' and bi%2 else []
    hat=[2,6,10,14] if ds=='full' else []
    if ds=='full' and bi%8==7:hat=[2,6];snare=[4,10,12,13,14,15]       # a snare fill at the end of each 8 bars
    if ds=='end' and bi==len(SONG)-1:kick=[0];snare=[];hat=[]
    for st in range(16):
        k0=fr+st*SPEED
        if st in kick:shape=[(247,1.0),(494,0.95),(247,0.8),(494,0.6),(247,0.4),(494,0.22),(247,0.1)]   # low noise flicking between two pitches
        elif st in snare:shape=[(784,1.0),(784,0.85),(740,0.65),(740,0.45),(700,0.28),(700,0.14)]
        elif st in hat:shape=[(3136,0.55),(3136,0.25)]
        else:continue
        for i,(fq,g) in enumerate(shape):
            if k0+i<NF:V[1]['w'][k0+i]='n';V[1]['f'][k0+i]=fq;V[1]['g'][k0+i]=g
    fr+=16*SPEED
for k in range(NF):
    if k<4*16*SPEED:V[0]['pw'][k]=0.5
    else:q=(k%56)/28;V[0]['pw'][k]=0.06+0.84*(q if q<=1 else 2-q)        # 1/32 per frame up, then down   # square in the intro, sweeping after
rng=np.random.default_rng(64);NOISE=rng.uniform(-1,1,1<<16)
out=np.zeros(NF*SPF)
for vi,v in enumerate(V):
    ph=0.0;nph=0.0;buf=np.zeros(NF*SPF);gp=0
    for k in range(NF):
        g=v['g'][k];fq=v['f'][k]
        if g<=0 and gp<=0:continue
        n=np.arange(1,SPF+1);gg=gp+(g-gp)*n/SPF
        if v['w'][k]=='n':   # SID noise is clocked at about 16x the set frequency
            rate=min(16*fq,SR);idx=(nph+rate*n/SR).astype(np.int64);seg=NOISE[idx%len(NOISE)];nph+=rate*SPF/SR
        else:p=(ph+fq*n/SR)%1.0;seg=np.where(p<v['pw'][k],1.0,-1.0);ph=(ph+fq*SPF/SR)%1.0
        buf[k*SPF:(k+1)*SPF]=seg*gg;gp=g
    out+=buf*[0.30,0.34,0.38][vi]
out=out[:fr*SPF+SR];fd=np.ones_like(out);fd[-int(0.7*SR):]=np.linspace(1,0,int(0.7*SR))**2;out*=fd
out=ss.lfilter(*ss.butter(1,10000/(SR/2)),out);out=ss.lfilter([1,-1],[1,-0.999],out)
out/=np.abs(out).max()*1.12
w=wave.open(sys.argv[1],'wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype('<i2').tobytes());w.close()
print('bars',nb,'length',round(len(out)/SR,1),'s')
