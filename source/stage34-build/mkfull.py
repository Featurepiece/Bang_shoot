# Full, unedited Jukebox versions: whole original, gain to -16.3 LUFS (limiter only if the gain would clip), 192 kbps
import subprocess,re,json
S='source/music/'
M={'title':'title - Bang Shoot','stage1':'stage1 - E Minor Assault','stage3h':'stage3 - Arcade Climax','stage4d':'stage4 - Full Power (alternative)',
   'stage2':'stage2 - Arcade Rush','stage5':'stage5 - Final Battle','boss1':'boss1 - Mothership','boss2':'boss2 - Crystal Queen','boss3':'boss3 - Hive Mother',
   'boss4':'boss4 - Dreadnought','boss':'final boss - Final Boss Rush','ending':'ending - Victory Arpeggio','secret':'secret - Secret song',
   'stage':'stage1 - Pixel Blaster','stage3':'stage3 - Pixelata Space','stage4':'stage4 - Hammer Press','uhive':'stage3 - Insectoid Arpeggio',
   'ub1':'stage4 - Battleship Assault','ub2':'stage4 - Battleship Assault 2'}
def meas(f):
    o=subprocess.run(['ffmpeg','-nostats','-i',f,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
    I=float(re.findall(r'I:\s+(-?[\d.]+) LUFS',o)[-1]);pk=float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS',o)[-1]);return I,pk
out={}
for k,n in M.items():
    src=S+n+'.mp3';I,pk=meas(src);g=-16.3-I;af=f'volume={g:.2f}dB'+(',alimiter=limit=0.9:level=false' if pk+g>-1 else '')
    subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-af',af,'-c:a','libmp3lame','-b:a','192k','-map_metadata','-1',f'music/full/{k}.mp3'],check=True)
    d=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'music/full/{k}.mp3'],capture_output=True,text=True).stdout)
    out[k]=round(d,2);print(f'{k:8s} {n:38s} {I:6.1f} LUFS -> -16.3 (gain {g:+.1f} dB{", limited" if pk+g>-1 else ""})  {d:6.1f} s')
json.dump(out,open('/tmp/claude-0/-home-claude-bang-shoot/ae8d7b5e-3457-5a66-9a7e-d466f5b48944/scratchpad/s34/full_durs.json','w'))
