# -*- coding: utf-8 -*-
"""PWA-мета + редактор треков (свои треки, прогон, экспорт/импорт) + вариативные лесенки."""

P='/home/z/my-project/download/balaclava-rave.html'
s=open(P,encoding='utf-8').read()

def rep(old,new,cnt=1):
    global s
    n=s.count(old)
    assert n==cnt,'COUNT %d != %d: %r'%(n,cnt,old[:70])
    s=s.replace(old,new)

# --- 1) PWA-мета в head ---
rep('<title>BALACLAVA RAVE — лондонский андеграунд</title>',
'''<title>BALACLAVA RAVE — лондонский андеграунд</title>
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#0b0718">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="icon-192.png">
<link rel="icon" type="image/png" href="icon-192.png">
<script>if('serviceWorker' in navigator&&/^https/.test(location.protocol)){window.addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}</script>''')

# --- 2) CSS: без pull-to-refresh + редактор ---
rep('.screen{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;',
'''.screen{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;
/* ---------- РЕДАКТОР ТРЕКОВ ---------- */
.edWrap{width:min(94%,880px);margin:12px auto 0;display:flex;flex-direction:column;gap:10px;flex:1;min-height:0;padding-bottom:14px}
.edRow{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}
.edMsg{text-align:center;font-weight:800;font-size:.78rem;letter-spacing:.08em;color:#9d8fd0;min-height:1.2em}
.edMsg.ok{color:#a7f3d0}.edMsg.err{color:#fda4af}
#edText{width:100%;flex:1;min-height:200px;background:rgba(14,10,28,.92);border:1px solid var(--line);border-radius:6px;
  color:#e6e0ff;font:600 .76rem/1.45 ui-monospace,Consolas,monospace;padding:12px;resize:none;outline:none}
#edText:focus{border-color:#8b5cf6;box-shadow:0 0 14px rgba(139,92,246,.35)}
.edHelp{font-size:.66rem;color:#7a6fae;text-align:center;letter-spacing:.04em;line-height:1.5}
html,body{overscroll-behavior:none}''')

# --- 3) кнопка редактора на обложке ---
rep('    <button id="btnPlay" class="btn main"><b>▶ ИГРАТЬ</b></button>\n  </section>',
'''    <button id="btnPlay" class="btn main"><b>▶ ИГРАТЬ</b></button>
    <button id="btnEditor" class="btn ghost">🎛 РЕДАКТОР ТРЕКОВ</button>
  </section>''')

# --- 4) экран редактора ---
rep('  <section id="scrRes" class="screen">',
'''  <section id="scrEditor" class="screen">
    <div class="bar"><div class="barTitle">РЕДАКТОР ТРЕКОВ</div></div>
    <div class="edWrap">
      <div class="edRow">
        <button id="edTest" class="btn">▶ ПРОГНАТЬ</button>
        <button id="edSave" class="btn">💾 ДОБАВИТЬ</button>
        <button id="edImport" class="btn ghost">📥 ЗАМЕНИТЬ ВСЁ</button>
        <button id="edExport" class="btn ghost">📄 В ТЕКСТ</button>
        <button id="edClear" class="btn ghost">🗑 СТЕРЕТЬ</button>
        <button id="edBack" class="btn ghost"><b>← НАЗАД</b></button>
      </div>
      <div id="edMsg" class="edMsg">Вставь JSON одного трека или массива треков</div>
      <textarea id="edText" spellcheck="false" placeholder='{"name":"МОЙ ТРЕК","bpm":130,"loopBeats":16,"mel":[[0,1,69],[1,1,72],[2,1,74],[3,1,76],[4,2,72]],"chords":[[0,4,45,[57,60,64]],[4,4,41,[53,57,60]]],"drum":{"k":[0,1,2,3],"s":[1,3]}}'></textarea>
      <div class="edHelp">mel: [доля, длина, midi] • chords: [доля, длина, бас-midi, [ноты]] • drum.k — доли бочки, drum.s — доли малого • egap — прореживание на ЛЁГКОМ • loopBeats — длина круга в долях</div>
    </div>
  </section>
  <section id="scrRes" class="screen">''')

# --- 5) buildMenus: список со своими треками + корректная нумерация ---
rep("  var tl=document.getElementById('trackList');\n  tl.innerHTML='';\n  TRACKS.forEach(function(tr,ix){",
"  var tl=document.getElementById('trackList');\n  tl.innerHTML='';\n  LIST().forEach(function(tr,ix){")
rep("d.innerHTML='<div class=\"tnum\">0'+(ix+1)+'</div><div class=\"tname\">'+tr.name+'</div>'+",
"d.innerHTML='<div class=\"tnum\">'+(ix+1<10?'0':'')+(ix+1)+'</div><div class=\"tname\">'+tr.name+'</div>'+")

# --- 6) выход из тест-прогона возвращает в редактор ---
rep("state='menu';document.getElementById('tbtns').classList.remove('on');buildMenus();showScreen('scrCover');});",
"state='menu';document.getElementById('tbtns').classList.remove('on');var back=ED_RETURN;ED_RETURN=false;buildMenus();showScreen(back?'scrEditor':'scrCover');});")

# --- 7) вариативные лесенки: 5 паттернов + тоны из мелодии ---
rep('''  var pat=[0,1,2,3,2,1,0,1,2];
  picks.forEach(function(pb,pi){
    var t0=pb*4*spb,c=chordAt(tr,pb*4),tones=c[3].concat([c[3][0]+12]);
    CH=CH.filter(function(n){return n.t<t0-1.1*spb-0.01||n.t>t0+5.1*spb+0.01;});
    var pack={i:pi,t0:t0,t1:t0+4*spb,hits:0,done:false,failed:false,bonus:500,notes:[]};
    for(var k=0;k<9;k++){
      var n=mk(pat[k],t0+k*.5*spb,(tr.leadKind||'lead'),[tones[pat[k]]],0.4*spb,1);
      n.snk=pi;CH.push(n);pack.notes.push(n);
    }
    SECF.push({t:t0,txt:'🐍 ИСПЫТАНИЕ'});
    PACKS.push(pack);
  });''',
'''  var PATS=[
    {nm:'🐍 ЗМЕЙКА',sq:[0,1,2,3,2,1,0,1,2]},
    {nm:'🌊 ВОЛНА',sq:[1,2,3,2,1,0,1,2,3]},
    {nm:'⚡ РАЗБЕГ',sq:[0,2,1,3,0,2,1,3,0]},
    {nm:'🌀 ПИЛКА',sq:[0,3,1,2,3,0,2,1,3]},
    {nm:'💧 КАСКАД',sq:[[0],[0,1],[1,2],[2,3],[2,3],[1,2],[0,1],[0],[0,1,2]]}
  ];
  picks.forEach(function(pb,pi){
    var pat=PATS[pi%PATS.length];
    var t0=pb*4*spb;
    /* тоны берём из мелодии рядом с баром — лесенка «поёт» тему трека */
    var tones=[];
    tr.mel.forEach(function(mn){
      if(mn[0]>=pb*4-2&&mn[0]<pb*4+6&&tones.indexOf(mn[2])<0)tones.push(mn[2]);
    });
    if(tones.length<4){var c=chordAt(tr,pb*4);tones=c[3].concat([c[3][0]+12,c[3][1]+12]);}
    CH=CH.filter(function(n){return n.t<t0-1.1*spb-0.01||n.t>t0+5.1*spb+0.01;});
    var pack={i:pi,t0:t0,t1:t0+4*spb,hits:0,done:false,failed:false,bonus:500,notes:[]};
    for(var k=0;k<9;k++){
      var step=pat.sq[k],lanes=Array.isArray(step)?step:[step];
      if(DIFFV==='easy'&&lanes.length>1)lanes=[lanes[0]];
      var tone=tones[(pi*2+k)%tones.length];
      lanes.forEach(function(ln){
        var n=mk(ln,t0+k*.5*spb,(tr.leadKind||'lead'),[tone],0.4*spb,1);
        n.snk=pi;CH.push(n);pack.notes.push(n);
      });
    }
    SECF.push({t:t0,txt:pat.nm});
    PACKS.push(pack);
  });''')

open(P,'w',encoding='utf-8').write(s)
print('OK pwa_editor base, size:',len(s))
