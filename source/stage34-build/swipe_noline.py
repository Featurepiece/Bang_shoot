import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
a="for(const [w,a] of [[10,0.12],[5,0.22],[2,0.95]]){ctx.globalAlpha=a*(0.55+0.45*p);ctx.lineWidth=w;ctx.beginPath();ctx.moveTo(0,yb);ctx.lineTo(W,yb);ctx.stroke();}\n  "
assert s.count(a)==1,s.count(a)
s=s.replace(a,"")
open(P,'w').write(s);print('OK')
