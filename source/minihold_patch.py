# 1) carrier pod a little smaller
# 2) mid-bosses must be killed: on music-locked stages the music loops the mid-boss section (sample-accurate, inside the
#    audio buffer) and the stage clock holds before the next section until the mid-boss is dead; then the music plays on
#    to the section line and the stage carries on in time with it.
import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
rep("const CARRIER={img:new Image(),dw:46,dh:46*640/1131,","const CARRIER={img:new Image(),dw:37,dh:37*640/1131,")
rep("e.hp=e.max=10*hpScale();e.score=1000;e.hw=20;e.hh=10;","e.hp=e.max=10*hpScale();e.score=1000;e.hw=16;e.hh=8;")
# trackPos follows the hold loop while it is active
rep("function trackPos(){\n  if(!M.node)return 0;const t=MUSIC[M.name];let p=M.offset+(A.ctx.currentTime-M.startedAt);",
    "function trackPos(){\n  if(!M.node)return 0;const t=MUSIC[M.name];let p=M.offset+(A.ctx.currentTime-M.startedAt);\n"
    "  if(M.hold&&!M.hold.rel){const h=M.hold;if(p>=h.B)p=h.A+(p-h.A)%(h.B-h.A);return p;}")
rep("  M.node=src;M.gain=g;M.name=name;M.startedAt=now0;","  M.hold=null;M.node=src;M.gain=g;M.name=name;M.startedAt=now0;")
rep("function s1Clock(){",
r'''// hold the stage before the section after a mid-boss until it is dead (cfg: A = mid-boss section start, B = next section)
function miniHold(c,cfg){
  const alive=!!(G.mini&&!G.mini.dead&&!G.mini.leaving),t=MUSIC[cfg.track],playing=!!(M.name===cfg.track&&M.node&&A.ctx);
  if(alive&&playing&&!M.hold&&c>=cfg.A){const p=trackPos();if(p>=cfg.A-0.5&&p<cfg.B){M.offset=p;M.startedAt=A.ctx.currentTime;M.hold={A:cfg.A,B:cfg.B};M.node.loopStart=cfg.A;M.node.loopEnd=cfg.B;}}
  if(!alive&&M.hold&&!M.hold.rel){if(playing){const p=trackPos();M.node.loopStart=t.ls;M.node.loopEnd=t.le;M.offset=p;M.startedAt=A.ctx.currentTime;}M.hold.rel=true;}
  const waiting=alive||!!(M.hold&&M.hold.rel&&playing&&trackPos()<cfg.B-0.1);
  if(M.hold&&M.hold.rel&&!waiting)M.hold=null;
  if(waiting&&c>cfg.B-0.05){G.stageT=Math.min(G.stageT,cfg.B-0.05-cfg.DROP);return cfg.B-0.05;}
  return c;}
function s1Clock(){''')
rep("  if(M.name==='stage1'&&M.node){const p=trackPos();if(p>=(G.s1c||0)-2)c=Math.max(p,g-1.0);}   // follow the music, never more than 1 s behind the game\n  return G.s1c=Math.max(G.s1c||0,c);}",
    "  if(M.name==='stage1'&&M.node){const p=trackPos();if(p>=(G.s1c||0)-2)c=Math.max(p,g-1.0);}   // follow the music, never more than 1 s behind the game\n"
    "  c=miniHold(c,{A:S1.WARDEN,B:S1.GATE,track:'stage1',DROP:S1.DROP});\n  return G.s1c=Math.max(G.s1c||0,c);}")
rep("function sxClock(cfg){const g=cfg.DROP+G.stageT;let c=g;\n  if(M.name===cfg.track&&M.node){const p=trackPos();if(p>=(G.sxc||0)-2)c=Math.max(p,g-1.0);}",
    "function sxClock(cfg){const g=cfg.DROP+G.stageT;let c=g;\n  if(M.name===cfg.track&&M.node){const p=trackPos();if(p>=(G.sxc||0)-2)c=Math.max(p,g-1.0);}\n"
    "  if(cfg===HV)c=miniHold(c,{A:HV.MINI,B:HV.WALLS,track:'stage3h',DROP:HV.DROP});")
open(P,'w').write(s);print('OK')
