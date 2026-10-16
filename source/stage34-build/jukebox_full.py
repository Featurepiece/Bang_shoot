# Jukebox plays the full, unedited version of every track (music/full/<key>.mp3, level-matched, loaded on demand),
# once through, then moves on to the next track. The game keeps its trimmed, looping edits.
import sys,json
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
D=json.load(open('/tmp/claude-0/-home-claude-bang-shoot/ae8d7b5e-3457-5a66-9a7e-d466f5b48944/scratchpad/s34/full_durs.json'))
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
durs=','.join(f"{k}:{v}" for k,v in D.items())
rep("function stageTrack(n){",
    "// Jukebox: full, unedited versions (key 'f_'+track), played once through\n"
    f"const FULL_DUR={{{durs}}};\n"
    "for(const k in FULL_DUR)MUSIC['f_'+k]={src:'music/full/'+k+'.mp3',ls:0,le:FULL_DUR[k],once:true,lazy:true,buf:null};\n"
    "function jbKey(k){return MUSIC['f_'+k]?'f_'+k:k;}\n"
    "function stageTrack(n){")
# play / stop the full version
rep("      else{if(MENU.playing===it.k&&M.node&&M.name===it.k){musicOff(0.6);MENU.playing='none';}\n        else{if(A.ctx)stopMusic(0.3);playMusic(it.k,0,0.2);MENU.playing=it.k;if(!MUSIC[it.k].buf){loadTrack(it.k);flash('Loading...');}}}}",
    "      else jbPlay(it.k);}")
rep("function jukeItems(){",
    "function jbPlay(k){const f=jbKey(k);if(MENU.playing===f&&M.node&&M.name===f){musicOff(0.6);MENU.playing='none';return;}\n"
    "  if(A.ctx)stopMusic(0.3);playMusic(f,0,0.2);MENU.playing=f;if(!MUSIC[f].buf){loadTrack(f);flash('Loading...');}}\n"
    "// when a full version reaches its end, the next track starts (the list stops after the last one)\n"
    "function jbAdvance(){if(!M.node||!M.name||!M.name.startsWith('f_')||!A.ctx)return;const t=MUSIC[M.name];if(!t.buf)return;\n"
    "  if(M.offset+(A.ctx.currentTime-M.startedAt)<t.buf.duration-0.05)return;\n"
    "  const it=jukeItems(),i=it.findIndex(x=>jbKey(x.k)===M.name);let j=i+1;while(j<it.length&&it[j].k==='hdr')j++;\n"
    "  if(i<0||j>=it.length||it[j].k==='back'){musicOff(0.2);MENU.playing='none';return;}MENU.playing=null;jbPlay(it[j].k);}\n"
    "function jukeItems(){")
# highlight and now-playing use the full key; caption under the heading
rep("  heading(MENU.sync?'Lyric sync':'Jukebox',16);\n  if(MENU.sync){drawSync();return;}",
    "  heading(MENU.sync?'Lyric sync':'Jukebox',16);\n  if(MENU.sync){drawSync();return;}\n  jbAdvance();ctx.globalAlpha=0.75;centerText('Full, unedited versions',31,8,'#8d7fc0');ctx.globalAlpha=1;")
rep("on=i===MENU.sel,pl_=MENU.playing===it.k&&M.name===it.k&&M.node;\n    if(it.k==='hdr')",
    "on=i===MENU.sel,pl_=MENU.playing===jbKey(it.k)&&M.name===jbKey(it.k)&&M.node;\n    if(it.k==='hdr')")
rep("const nm=M.name==='secret'?'Secret song':(TRACKS.find(x=>x.k===M.name)||{}).n||M.name;",
    "const bk=M.name.replace(/^f_/,''),nm=bk==='secret'?'Secret song':(TRACKS.find(x=>x.k===bk)||{}).n||bk;")
rep("txt('Now playing',260,170,'#b9a8e8');","txt(M.name.startsWith('f_')?'Now playing - full version':'Now playing',260,170,'#b9a8e8');")
open(P,'w').write(s);print('OK')
