"""Cut a Gemini pillar out of its white background (also clears enclosed white gaps, e.g. between claws). args: src out side(top|bottom)"""
import sys,numpy as np
from PIL import Image
from scipy import ndimage
src,out,side=sys.argv[1:4]
g=np.asarray(Image.open(src).convert('RGB')).astype(float)
white=g.min(axis=2)>205;lab,n=ndimage.label(white);sizes=ndimage.sum(white,lab,range(1,n+1))
edges=[lab[:,0],lab[:,-1]]+([lab[-1]] if side=='top' else [lab[0]])   # the side it attaches to is cut flat by the frame
bd=set(np.unique(np.concatenate(edges)))-{0}
neutral=(g.max(axis=2)-g.min(axis=2))<30
drop=set(bd)|{i for i in range(1,n+1) if sizes[i-1]>=20 and neutral[lab==i].mean()>0.8}
fg=~np.isin(lab,list(drop));fg=ndimage.binary_opening(fg,iterations=1)
l2,m=ndimage.label(fg);s=ndimage.sum(fg,l2,range(1,m+1));fg=l2==(np.argmax(s)+1)
ys,xs=np.where(fg);x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
a=ndimage.gaussian_filter(fg.astype(float),0.7);edge=ndimage.binary_dilation(~fg,iterations=2)&fg;rgb=g.copy();rgb[edge]*=0.75
im=Image.fromarray(np.dstack([rgb,a*255]).clip(0,255).astype(np.uint8),'RGBA').crop((x0,y0,x1,y1));im.save(out)
print(out,im.size,'ratio',round(im.height/im.width,2))
