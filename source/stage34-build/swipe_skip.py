import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:60]}')
    s=s.replace(a,b)
# 1) swipe warning: no box outline, a soft tint fading from the midline into the danger half
rep("ctx.globalAlpha=0.3+0.35*p;ctx.lineWidth=1.5;ctx.strokeRect(1,top?1:yb,W-2,yb-2);ctx.restore();}}",
    "const d=70,gy=top?yb-d:yb,gr=ctx.createLinearGradient(0,top?yb:yb,0,top?yb-d:yb+d);gr.addColorStop(0,'rgba(157,255,61,0.32)');gr.addColorStop(1,'rgba(157,255,61,0)');"
    "ctx.globalAlpha=0.45+0.55*p;ctx.fillStyle=gr;ctx.fillRect(0,gy,W,d);ctx.restore();}}")
# 2) skip keys (B / N): clear a tunnel that is still on screen before jumping to the boss
rep("else if(!G.boss&&!G.pre&&!(G.clearT>0)){if(s1On())",
    "else if(!G.boss&&!G.pre&&!(G.clearT>0)){TUN.on=false;if(s1On())",2)
open(P,'w').write(s);print('OK')
# 3) never start the hive tunnel when it could not clear the screen before the boss (e.g. after a skip)
s=open(P).read()
a="if(!HV.tun){HV.tun=true;tunStart();}"
assert s.count(a)==1
s=s.replace(a,"if(!HV.tun){HV.tun=true;if(T<HV.END-28)tunStart();}")
open(P,'w').write(s);print('OK3')
