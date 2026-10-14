"""Cut a Gemini Mothership edit out of its white background, aligned to the original sprite.
Removes loose debris floating off the hull (the game throws its own moving debris) and white gaps in broken parts,
but keeps bright blast areas near the core."""
import sys,re,base64,io,os,numpy as np
from PIL import Image
from scipy import ndimage
srcimg,out=sys.argv[1],sys.argv[2]
src=open('/home/claude/bang_shoot/test.html').read()
m=re.search(r"\n  boss:\{[^\n]*?src:'data:image/\w+;base64,([A-Za-z0-9+/=]+)'",src)
orig=Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGBA');ow,oh=orig.size
g=np.asarray(Image.open(srcimg).convert('RGB').crop((47,43,1359,724)).resize((ow,oh),Image.LANCZOS)).astype(float)
white=g.min(axis=2)>205;lab,n=ndimage.label(white);sizes=ndimage.sum(white,lab,range(1,n+1))
bd=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
neutral=(g.max(axis=2)-g.min(axis=2))<30
drop=set(bd)
for i in range(1,n+1):
    if i in bd:continue
    r=lab==i;ys,xs=np.where(r);cx,cy=xs.mean()/ow,ys.mean()/oh
    near_core=0.22<cx<0.6 and 0.3<cy<0.7     # the blast in the middle stays solid
    if sizes[i-1]>=25 and neutral[r].mean()>0.8 and not near_core:drop.add(i);print('gap',int(sizes[i-1]),round(cx,2),round(cy,2))
fg=~np.isin(lab,list(drop));fg=ndimage.binary_opening(fg,iterations=1)
# loose debris: pieces not joined to the hull
l2,n2=ndimage.label(fg);s2=ndimage.sum(fg,l2,range(1,n2+1));keep=np.zeros(n2+1,bool)
for i,s in enumerate(s2,1):keep[i]=s>=1500
print('removed loose pieces:',int((~keep[1:]).sum()),'kept',int(keep[1:].sum()))
fg=keep[l2]
a=np.clip(ndimage.gaussian_filter(fg.astype(float),0.7),0,1)
edge=ndimage.binary_dilation(~fg,iterations=2)&fg
rgb=g.copy();rgb[edge]*=0.75
im=Image.fromarray(np.dstack([rgb,a*255]).clip(0,255).astype(np.uint8),'RGBA')
im.save(out+'.png');im.save(out+'.webp',quality=86,method=6);print(os.path.getsize(out+'.webp'))
bg=Image.new('RGBA',(ow,oh),(14,8,24,255));bg.alpha_composite(im);bg.convert('RGB').save(out+'_prev.png')
