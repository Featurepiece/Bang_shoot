# v3.3: tunnels are the same every play and on every difficulty, and each stage has its own shape;
# the ground line is fixed too (it was randomised on page load, which nudged the tunnel entrance/exit floor)
import sys
P=sys.argv[1] if len(sys.argv)>1 else 'test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:80]}')
    s=s.replace(a,b)
rep("const L=960,FAR={base:62,w:[[20,2,rnd(0,TAU)],[10,5,rnd(0,TAU)],[5,11,rnd(0,TAU)],[2,23,rnd(0,TAU)]]},\n  NEAR={base:26,w:[[12,3,rnd(0,TAU)],[7,8,rnd(0,TAU)],[3,17,rnd(0,TAU)],[1.5,41,rnd(0,TAU)]]};",
    "const L=960,FAR={base:62,w:[[20,2,1.3],[10,5,4.1],[5,11,2.7],[2,23,5.6]]},   // fixed hills: the same ground every play\n  NEAR={base:26,w:[[12,3,3.4],[7,8,0.9],[3,17,5.0],[1.5,41,2.2]]};")
rep("TUN.X1=TUN.X0+TUN_LEN;TUN.ph=rnd(0,TAU);",
    "TUN.X1=TUN.X0+TUN_LEN;TUN.ph=TUN_SHAPE[G.stage]!==undefined?TUN_SHAPE[G.stage]:rnd(0,TAU);")
rep("function tunStart(){return seeded('tun',tunStart_);}",
    "const TUN_SHAPE={1:0.2,2:5.2,3:1.8};   // each stage's own tunnel, the same on every play and every difficulty (only the width changes with difficulty)\nfunction tunStart(){return seeded('tun',tunStart_);}")
rep("const GAME_VERSION='3.1';","const GAME_VERSION='3.3';")
open(P,'w').write(s);print('OK')
