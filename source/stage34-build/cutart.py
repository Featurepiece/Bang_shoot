import numpy as np,json,base64,io
from PIL import Image
from scipy import ndimage
U='/root/.claude/uploads/ae8d7b5e-3457-5a66-9a7e-d466f5b48944/'
def cut(p,open_edges=('t','b','l','r'),keep_largest=True,gaps=True,thr=205):
    g=np.asarray(Image.open(p).convert('RGB')).astype(float);w=g.min(2)>thr;lab,n=ndimage.label(w)
    E={'t':lab[0],'b':lab[-1],'l':lab[:,0],'r':lab[:,-1]};bd=set(np.unique(np.concatenate([E[k] for k in open_edges])))-{0}
    drop=set(bd)
    if gaps:
        sz=ndimage.sum(w,lab,range(1,n+1));neu=(g.max(2)-g.min(2))<30
        for i in range(1,n+1):
            if i not in bd and sz[i-1]>=40 and neu[lab==i].mean()>0.85:drop.add(i)
    fg=~np.isin(lab,list(drop));fg=ndimage.binary_opening(fg,iterations=1)
    if keep_largest:
        l2,m=ndimage.label(fg);s=ndimage.sum(fg,l2,range(1,m+1));fg=l2==(np.argmax(s)+1)
    ys,xs=np.where(fg);box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    a=ndimage.gaussian_filter(fg.astype(float),0.7);edge=ndimage.binary_dilation(~fg,iterations=2)&fg;rgb=g.copy();rgb[edge]*=0.75
    return Image.fromarray(np.dstack([rgb,a*255]).clip(0,255).astype(np.uint8),'RGBA').crop(box),box,g
out={}
def save(k,im,w):
    h=round(im.height*w/im.width);r=im.resize((w,h),Image.LANCZOS);b=io.BytesIO();r.save(b,'WEBP',quality=88,method=6)
    out[k]={'uri':'data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode(),'w':w,'h':h};r.save('art/'+k+'.png');return r
# hive wall (top edge is flat: open everywhere)
wall,box,g=cut(U+'0a3045fe-image.jpg',open_edges=('b','l','r'))
wall=wall.crop((2,0,wall.width-2,wall.height))
W2=save('wall',wall,320)
a=np.asarray(W2)[:,:,3]>128;prof=[int(np.where(a[:,x])[0].max()) if a[:,x].any() else 0 for x in range(a.shape[1])];out['wall']['prof']=prof
# pods
for k,f in [('podC','1c295966-image.jpg'),('podO','2b066a85-image.jpg')]:
    im,box,g=cut(U+f);im=im.crop((0,0,im.width,im.height-int(im.height*0.0)))
    # drop the grey bar Gemini drew under the pods: rows that are mostly neutral grey at the bottom
    arr=np.asarray(im).astype(int);rows=[y for y in range(arr.shape[0]) if ((arr[y,:,3]>128)&(np.abs(arr[y,:,0]-arr[y,:,2])<15)&(arr[y,:,1]<120)).mean()>0.5]
    if rows:im=im.crop((0,0,im.width,min(rows)))
    save(k,im,120)
# serpent
head,box,g=cut(U+'b4985a8f-image.jpg');save('head',head,180);hbox=box
# glowing frame aligned: scale 1/0.99, shift x-1,y+5 at full size, then crop with the head's box
gm=Image.open(U+'dae436a0-image.jpg').convert('RGB');W0,H0=gm.size;gs=gm.resize((round(W0/0.99),round(H0/0.99)),Image.LANCZOS)
canvas=Image.new('RGB',(W0,H0),'white');canvas.paste(gs,(-1-round((gs.width-W0)/2),5-round((gs.height-H0)/2)));canvas.save('glow_aligned.jpg')
gl,box2,_=cut('glow_aligned.jpg');print('head box',hbox,'glow box',box2)
glc=Image.open('glow_aligned.jpg').convert('RGBA')
hm=np.asarray(head)[:,:,3]
gimg=np.asarray(glc.crop(hbox)).copy();gimg[:,:,3]=hm;save('headG',Image.fromarray(gimg,'RGBA'),180)
seg,box,g=cut(U+'1b630475-image.jpg');save('seg',seg,110)
# engine block (flat top)
eng,box,g=cut(U+'cd72eb7c-image.jpg');E2=save('engine',eng,220)
e=np.asarray(E2).astype(int);H2=e.shape[0];band=e[int(H2*0.8):,:]
orange=(band[:,:,0]>200)&(band[:,:,1]>90)&(band[:,:,1]<200)&(band[:,:,2]<120)&(band[:,:,3]>128)
cols=np.where(orange.sum(0)>2)[0];lab,n=ndimage.label(np.isin(np.arange(e.shape[1]),cols));noz=[float(np.mean(np.where(lab==i)[0]))/e.shape[1] for i in range(1,n+1)]
out['engine']['noz']=[round(x,3) for x in noz if True];print('nozzles',out['engine']['noz'])
# turret row
tr,box,g=cut(U+'69143d6d-image.jpg');T2=save('trow',tr,280)
t=np.asarray(T2)[:,:,3]>128;top=[int(np.where(t[:,x])[0].min()) if t[:,x].any() else 999 for x in range(t.shape[1])]
deck=int(np.median(top[int(len(top)*0.45):int(len(top)*0.55)]))
domes=np.array(top)<np.percentile(top,30);lab,n=ndimage.label(domes);out['trow']['domes']=[round(float(np.mean(np.where(lab==i)[0]))/t.shape[1],3) for i in range(1,n+1)]
out['trow']['deck']=round(min(top[int(len(top)*0.48):int(len(top)*0.52)])/t.shape[0],3);print('domes',out['trow']['domes'])
# reactor
rc,box,g=cut(U+'b3860f2f-image.jpg');R2=save('reactor',rc,240)
r=np.asarray(R2).astype(int);b=(r[:,:,0]>240)&(r[:,:,1]>200)&(r[:,:,3]>128);ys,xs=np.where(b);out['reactor']['core']=[round(xs.mean()/r.shape[1],3),round(ys.mean()/r.shape[0],3),round((xs.max()-xs.min())/r.shape[1]/2,3)];print('core',out['reactor']['core'])
json.dump(out,open('art34.json','w'))
for k,v in out.items():print(k,v['w'],v['h'],len(v['uri'])//1024,'KB')
