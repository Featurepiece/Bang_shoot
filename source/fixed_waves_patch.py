# Every stage plays the same each time (per difficulty): stage content is chosen with seeded random numbers.
#  - one-off events (each wave, tunnel shape, hazard, hive walls) get a seed from stage|difficulty|event|count
#  - ongoing choices (tunnel waves, gate swarms, hazard spawns, escorts, serpent path, carriers, stage 5 presses/drips)
#    each draw from their own seeded stream
#  - effects and sounds (particles, explosions, pitch) always use the normal random generator, so they never shift the stage
import sys,re
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
rep("const rnd=(a,b)=>a+Math.random()*(b-a), pick=a=>a[(Math.random()*a.length)|0];",
r'''const rnd=(a,b)=>a+Math.random()*(b-a), pick=a=>a[(Math.random()*a.length)|0];
// ---- fixed stages: seeded random numbers for everything that decides what a stage throws at you ----
const NATIVE_RANDOM=Math.random;
function mulberry(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function hashStr(str){let h=2166136261;for(let i=0;i<str.length;i++){h^=str.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
const RS={key:null,n:{},st:{}};
function rsSync(){const k=G.stage+'|'+(typeof OPT!=='undefined'?OPT.diff:'');if(RS.key!==k){RS.key=k;RS.n={};RS.st={};}return k;}
function withRng(r,fn){const o=Math.random;Math.random=r;try{return fn();}finally{Math.random=o;}}
function seeded(tag,fn){const k=rsSync(),n=RS.n[tag]=(RS.n[tag]||0)+1;return withRng(mulberry(hashStr(k+'|'+tag+'|'+n)),fn);}
function inStream(tag,fn){const k=rsSync();return withRng(RS.st[tag]||(RS.st[tag]=mulberry(hashStr(k+'|'+tag))),fn);}
function nativeRng(f){return function(){const o=Math.random;Math.random=NATIVE_RANDOM;try{return f.apply(this,arguments);}finally{Math.random=o;}};}''')
# effects and sounds never draw from the stage's numbers
rep("let DF={fire:1,spd:1,hp:1,spawn:1};",
    "let DF={fire:1,spd:1,hp:1,spawn:1};\nP=nativeRng(P);explode=nativeRng(explode);sx=nativeRng(sx);samp=nativeRng(samp);tone=nativeRng(tone);noiseHit=nativeRng(noiseHit);say=nativeRng(say);rumble=nativeRng(rumble);")
# a new game starts every stage's numbers afresh
rep("function newGame(noMusic){","function newGame(noMusic){RS.key=null;")
def wrapfn(name,args,body):
    global s
    a=f"function {name}({args}){{"
    assert s.count(a)==1,(name,s.count(a))
    s=s.replace(a,f"function {name}({args}){{return {body};}}\nfunction {name}_({args}){{")
wrapfn('introWave','',"seeded('w',introWave_)")
wrapfn('tunStart','',"seeded('tun',tunStart_)")
wrapfn('hvWallsStart','T',"seeded('walls',()=>hvWallsStart_(T))")
wrapfn('startHazard','',"seeded('hz',startHazard_)")
wrapfn('hazardTick','dt',"inStream('hzt',()=>hazardTick_(dt))")
wrapfn('serpPick','e',"inStream('serp',()=>serpPick_(e))")
wrapfn('carryTick','',"inStream('carry',carryTick_)")
wrapfn('gateTick','dt,T',"inStream('gate',()=>gateTick_(dt,T))")
wrapfn('tunnelUpdate','dt',"inStream('tunw',()=>tunnelUpdate_(dt))")
rep("G.hazT=rnd(13,19);","G.hazT=inStream('hzgap',()=>rnd(13,19));")
rep("G.hazT=rnd(11,16);","G.hazT=inStream('hzgap',()=>rnd(11,16));")
rep("FL.pressT=rnd(4.2,6);","FL.pressT=inStream('press',()=>rnd(4.2,6));")
rep("FL.dripT=rnd(1.5,2.3);","FL.dripT=inStream('drip',()=>rnd(1.5,2.3));")
rep("for(let i=0;i<3;i++){const x=rnd(40,W-20);later(","for(let i=0;i<3;i++){const x=inStream('drip',()=>rnd(40,W-20));later(")
# mid-boss escorts: wrap each escort block
cnt=0
for m in list(re.finditer(re.escape("if(G.escT<=0){G.escT=rnd(4,5.5);"),s))[::-1]:
    st=m.end();depth=1;i=st
    while depth:
        c=s[i]
        if c=='{':depth+=1
        elif c=='}':depth-=1
        i+=1
    inner=s[m.start()+len("if(G.escT<=0){"):i-1]
    s=s[:m.start()]+"if(G.escT<=0){inStream('esc',()=>{"+inner+"});}"+s[i:];cnt+=1
assert cnt==3,cnt
# hunter rolls are decided when the enemy is made (inside the wave's numbers), not later
rep("  if(e.huntRoll===undefined)e.huntRoll=Math.random()<DFN.huntChance;","  if(e.huntRoll===undefined)e.huntRoll=(e.hr!==undefined?e.hr:Math.random())<DFN.huntChance;")
rep("const e=Object.assign({type,x,y,hp,max:hp,","const e=Object.assign({hr:Math.random(),type,x,y,hp,max:hp,")
open(P,'w').write(s);print('OK')
# fixed timeline: waves arrive on their own schedule; clearing the screen no longer pulls the next wave forward
s=open(P).read()
import re as _re
s,k=_re.subn(r"if\(G\.emptyT>0\.(5|6)\)\{","if(EARLY_WAVES&&G.emptyT>0.\\1){",s)
assert k==5,k
s=s.replace("const NATIVE_RANDOM=Math.random;","const NATIVE_RANDOM=Math.random,EARLY_WAVES=false;   // true: an empty screen calls the next wave early (makes stages vary with kill speed)",1)
open(P,'w').write(s);print('OK2')
