import sys,subprocess,numpy as np,soundfile as sf
src,A,B,out=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-ar','48000','tmp.wav'],check=True)
y,sr=sf.read('tmp.wav')
def env(x):k=int(sr*0.004);return np.convolve(np.abs(x.mean(1)),np.ones(k)/k,'same')
a0=int(A*sr);seg=env(y[a0:a0+int(1.6*sr)]);best=None
for d in range(-int(0.03*sr),int(0.03*sr),8):
    b0=int(B*sr)+d;s=env(y[b0:b0+len(seg)]);c=np.dot(seg-seg.mean(),s-s.mean())/(np.std(seg)*np.std(s)*len(seg))
    if best is None or c>best[0]:best=(c,d)
b0=int(B*sr)+best[1];pre=int(0.012*sr);xf=int(0.025*sr);ca=a0-pre;cb=b0-pre
t=np.linspace(0,np.pi/2,xf)[:,None]
o=np.concatenate([y[:ca],y[ca:ca+xf]*np.cos(t)+y[cb:cb+xf]*np.sin(t),y[cb+xf:]])
sf.write('cut.wav',o,sr);print('match',round(best[0],3),'shift ms',round(best[1]/sr*1000,1),'removed',round((cb-ca)/sr,3),'new len',round(len(o)/sr,2))
open(out+'.removed','w').write(str((cb-ca)/sr))
