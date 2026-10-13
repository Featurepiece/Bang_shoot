"""Mothership damage stages: three Gemini edits of the hull fade in as its health drops (66%, 33%, 15%)."""
import sys,base64,os
HERE=os.path.dirname(os.path.abspath(__file__));path=sys.argv[1];src=open(path,encoding='utf-8').read()
def rep(old,new,count=1):
    global src
    n=src.count(old)
    if n!=count: sys.exit(f'FAIL ({n}x, wanted {count}x): {old[:100]}')
    src=src.replace(old,new)
u=lambda n:'data:image/webp;base64,'+base64.b64encode(open(os.path.join(HERE,f'stage{n}.webp'),'rb').read()).decode()
rep("""function msImg(e,a){const m=e.tDead||0;if(!m||!a.n)return a.n;a._dv=a._dv||{};if(a._dv[m])return a._dv[m];
  const c=mk(a.n.width,a.n.height),g=c.getContext('2d'),w=c.width,h=c.height;g.drawImage(a.n,0,0);""",
"""// Mothership damage stages (Gemini edits of the original art, aligned to it): battered below 66% health, heavy below 33%, wrecked below 15%
const MSD=['"""+u(1)+"""','"""+u(2)+"""','"""+u(3)+"""'].map(s=>{const o={n:null},im=new Image();im.onload=()=>{const c=mk(im.width,im.height);c.getContext('2d').drawImage(im,0,0);o.n=c;};im.src=s;return o;});
function msStage(e,a){const h=e.max?e.hp/e.max:1,s=e.dying?3:h>0.66?0:h>0.33?1:h>0.15?2:3;if(e.dS!==s){if(s===3&&e.dS!==undefined&&!e.dying){explode(e.x+rnd(-30,30),e.y+rnd(-20,20),2.5,PAL_HOT);shake(0.35);}e.dT=e.dS===undefined?-9:G.t;e.dS=s;}   // 15%: no rage phase here, so the break gets its own blast
  const pick=i=>{for(let j=i;j>0;j--)if(MSD[j-1].n)return msImg(e,a,MSD[j-1].n,j);return msImg(e,a);};
  return {lo:pick(Math.max(0,s-1)),hi:pick(s),f:clamp((G.t-e.dT)/0.8,0,1)};}
function msImg(e,a,base,key){base=base||a.n;const m=e.tDead||0;if(!m||!base)return base;a._dv=a._dv||{};const ck=m+'_'+(key||0);if(a._dv[ck])return a._dv[ck];
  const c=mk(base.width,base.height),g=c.getContext('2d'),w=c.width,h=c.height;g.drawImage(base,0,0);""")
rep("""  return a._dv[m]=c;}""","""  return a._dv[ck]=c;}""")
rep("""function drawMothership(e,a){
  const img=msImg(e,a),""","""function drawMothership(e,a){
  const D=msStage(e,a),img=D.f>0.5?D.hi:D.lo,""")
rep("""  ctx.globalCompositeOperation='source-over';
  ctx.drawImage(img,-dw/2,-dh/2,dw,dh);
  if(e.tDead&&STUMP.ok)""","""  ctx.globalCompositeOperation='source-over';
  ctx.drawImage(D.f<1?D.lo:D.hi,-dw/2,-dh/2,dw,dh);
  if(D.f<1&&D.hi!==D.lo){ctx.globalAlpha=D.f;ctx.drawImage(D.hi,-dw/2,-dh/2,dw,dh);ctx.globalAlpha=1;}   // the new damage burns in over 0.8s
  if(e.tDead&&STUMP.ok)""")
open(path,'w',encoding='utf-8').write(src);print('OK')
