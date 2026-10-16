"""Gate pillars: new angular tower art (the old rounded columns read as rude). One picture; the floor towers are the same art flipped.
Taller towers repeat the widest armour block below the cap instead of stretching the picture."""
import sys,re,os
p=sys.argv[1];s=open(p,encoding='utf-8').read();uri=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'tower.uri')).read()
m=re.search(r"const PIL=\{ceil:new Image\(\),floor:new Image\(\)\};PIL\.ceil\.src='[^']+';PIL\.floor\.src='[^']+';",s);assert m
s=s[:m.start()]+"const PIL={tower:new Image()};PIL.tower.src='"+uri+"';   // angular gate tower (Gemini); floor towers are flipped\nconst TOW={cap:80/655,band0:80/655,band1:170/655};"+s[m.end():]
a=s.index("function drawPillar(img,x,tipY,top){");b=s.index("function drawGates(){")
s=s[:a]+r"""function drawPillar(img,x,tipY,top){
  if(!img.complete||!img.naturalWidth)return;const iw=img.naturalWidth,ih=img.naturalHeight,w=GATE_W,k=w/iw,nat=ih*k;
  ctx.save();if(!top){ctx.translate(0,H);ctx.scale(1,-1);tipY=H-tipY;}
  const L=tipY+6;
  if(L<=nat)ctx.drawImage(img,x-w/2,tipY-nat,w,nat);
  else{const b0=ih*TOW.band0,b1=ih*TOW.band1,lowH=(ih-b1)*k,bandH=(b1-b0)*k,capH=b0*k;
    let y=tipY-lowH;ctx.drawImage(img,0,b1,iw,ih-b1,x-w/2,y,w,lowH+0.5);
    while(y-capH>-6){y-=bandH;ctx.drawImage(img,0,b0,iw,b1-b0,x-w/2,y,w,bandH+0.5);}
    ctx.drawImage(img,0,0,iw,b0,x-w/2,y-capH,w,capH+0.5);}
  ctx.restore();}
"""+s[b:]
for a_,b_ in [("drawPillar(PIL.ceil,x,g.top+4,true);drawPillar(PIL.floor,x,g.bot-4,false);","drawPillar(PIL.tower,x,g.top+4,true);drawPillar(PIL.tower,x,g.bot-4,false);")]:
    assert s.count(a_)==1,a_;s=s.replace(a_,b_)
open(p,'w',encoding='utf-8').write(s);print('OK')
