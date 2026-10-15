"""Stage 1 backgrounds: the alien fleet in the distance (gates and ring) and the giant hull (full power), each fading in with its section.
Open space returns at the Warning so the Mothership is fought against the dark sky."""
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__));BG=os.path.join(HERE,'..','bg')
path=sys.argv[1];src=open(path,encoding='utf-8').read()
def rep(old,new,count=1):
    global src
    n=src.count(old)
    if n!=count: sys.exit(f'FAIL ({n}x, wanted {count}x): {old[:100]}')
    src=src.replace(old,new)
u1=open(os.path.join(BG,'bg1.datauri')).read();u2=open(os.path.join(BG,'bg2.datauri')).read()
rep("""function drawBG(){""","""// stage 1 backdrops (Gemini): 1 = the alien fleet in the distance (loops), 2 = flying low over a giant hull (perspective, so it barely moves)
const S1BG={a:new Image(),b:new Image(),w1:0,w2:0};S1BG.a.src='"""+u1+"""';S1BG.b.src='"""+u2+"""';
function s1Backdrop(){
  let t=0;if(s1On()&&G.state==='play'&&!G.pre&&!G.boss){const T=s1Clock();t=T>=S1.FULL?2:T>=S1.GATE?1:0;}
  const k=Math.min(1,fdt/2);S1BG.w1+=((t===1?1:0)-S1BG.w1)*k*3;S1BG.w2+=((t===2?1:0)-S1BG.w2)*k*3;   // about 2 s cross-fade
  if(S1BG.w1<0.003&&S1BG.w2<0.003)return 0;
  ctx.imageSmoothingEnabled=true;
  if(S1BG.w1>0.003&&S1BG.a.complete&&S1BG.a.naturalWidth){const w=S1BG.a.naturalWidth/2,x=-mod(G.scroll*0.12,w);ctx.globalAlpha=S1BG.w1;ctx.drawImage(S1BG.a,x,0,w,H);ctx.drawImage(S1BG.a,x+w,0,w,H);}
  if(S1BG.w2>0.003&&S1BG.b.complete&&S1BG.b.naturalWidth){const w=S1BG.b.naturalWidth/2,x=-Math.min(w-W,mod(G.scroll*0.03,w-W));ctx.globalAlpha=S1BG.w2;ctx.drawImage(S1BG.b,x,0,w,H);}
  ctx.globalAlpha=1;return Math.min(1,S1BG.w1+S1BG.w2);}
function drawBG(){""")
rep("""  ctx.fillStyle=skyFor(th);ctx.fillRect(-30,-30,W+60,H+60);""","""  ctx.fillStyle=skyFor(th);ctx.fillRect(-30,-30,W+60,H+60);
  const bgw=th===0?s1Backdrop():0;""")
rep("""    ctx.globalAlpha=0.92;ctx.drawImage(PLANET,mod(W*0.6-G.scroll*0.03,W+240)-120,18,130,130);ctx.globalAlpha=1;
    ctx.globalAlpha=0.75;ctx.drawImage(BGT[0].wrecks[0],mod(W*0.15-G.scroll*0.07,W+400)-200,62);ctx.drawImage(BGT[0].wrecks[1],mod(W*0.85-G.scroll*0.1,W+500)-250,98,120,31);ctx.globalAlpha=1;""",
"""    ctx.globalAlpha=0.92*(1-bgw);ctx.drawImage(PLANET,mod(W*0.6-G.scroll*0.03,W+240)-120,18,130,130);ctx.globalAlpha=1;
    ctx.globalAlpha=0.75*(1-bgw);ctx.drawImage(BGT[0].wrecks[0],mod(W*0.15-G.scroll*0.07,W+400)-200,62);ctx.drawImage(BGT[0].wrecks[1],mod(W*0.85-G.scroll*0.1,W+500)-250,98,120,31);ctx.globalAlpha=1;""")
rep("""  if(th===0){tileAt(BGT[0].city,0.35,0,0.9+0.1*bp);""","""  if(th===0){if(bgw<0.99)tileAt(BGT[0].city,0.35,0,(0.9+0.1*bp)*(1-bgw));""")
open(path,'w',encoding='utf-8').write(src);print('OK')
