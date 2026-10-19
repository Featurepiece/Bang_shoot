# v3.1: hive ribs stand on a far ridge (same treatment as the stage 2 crystal spires)
import sys
P=sys.argv[1] if len(sys.argv)>1 else 'test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:80]}')
    s=s.replace(a,b)
rep("else if(th===2){tileAt(BGT[2].ribs,0.35,0);drawRidge(NEAR,1,",
    "else if(th===2){tileAt(BGT[2].ribs,0.35,0);drawRidge(FAR,0.35,'#082210','#9dff3d',0.2+0.35*bp);drawRidge(NEAR,1,")   # the far ridge the ribs grow out of
rep("const GAME_VERSION='2.9';","const GAME_VERSION='3.1';")
open(P,'w').write(s);print('OK')
