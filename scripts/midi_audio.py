# -*- coding: utf-8 -*-
"""Часть A: кнопки импорта в редакторе + хранение/воспроизведение аудио трека."""

P='/home/z/my-project/download/balaclava-rave.html'
s=open(P,encoding='utf-8').read()

def rep(old,new,cnt=1):
    global s
    n=s.count(old)
    assert n==cnt,'COUNT %d != %d: %r'%(n,cnt,old[:70])
    s=s.replace(old,new)

# --- 1) кнопки импорта файлов ---
rep('''        <button id="edExport" class="btn ghost">📄 В ТЕКСТ</button>''',
'''        <button id="edMidi" class="btn">🎼 ИЗ MIDI</button>
        <button id="edAudio" class="btn">🎙 ИЗ АУДИО</button>
        <input type="file" id="edMidiFile" accept=".mid,.midi,audio/midi" class="hidden">
        <input type="file" id="edAudioFile" accept="audio/*" class="hidden">
        <button id="edExport" class="btn ghost">📄 В ТЕКСТ</button>''')

# --- 2) подсказка ---
rep('<div class="edHelp">mel: [доля, длина, midi]',
'''<div class="edHelp">Или загрузи файл: 🎼 MIDI (.mid) — точные ноты, бас и барабаны; 🎙 аудио (MP3/WAV/OGG) — программа сама найдёт ноты и темп (FFT).<br>mel: [доля, длина, midi]''')

# --- 3) normTrack: длинные треки + флаг аудио + стабильный id ---
rep("function slugId(name){return 'c_'+String(name).toLowerCase().replace(/[^a-zа-яё0-9]+/gi,'-').replace(/^-+|-+$/g,'').slice(0,20);}",
"function slugId(name,audio){var sl=String(name).toLowerCase().replace(/[^a-zа-яё0-9]+/gi,'-').replace(/^-+|-+$/g,'').slice(0,20);return (audio?'a_':'c_')+sl;}")
rep("var LB=Math.max(4,Math.min(64,Math.round(+t.loopBeats||16)));",
    "var LB=Math.max(4,Math.min(2048,Math.round(+t.loopBeats||16)));")
rep("return {id:slugId(t.name),name:String(t.name).slice(0,26),tag:'СВОЙ',",
    "return {id:slugId(t.name,!!t.audio),audio:!!t.audio,name:String(t.name).slice(0,26),tag:'СВОЙ',")

# --- 4) хранилище аудио + плеер (после var acStart=0) ---
rep('var acStart=0;',
'''var acStart=0;
/* ---------- АУДИО-ТРЕК: IndexedDB + воспроизведение ---------- */
function idbPut(k,v,cb){
  try{var rq=indexedDB.open('brave',1);
  rq.onupgradeneeded=function(){try{rq.result.createObjectStore('f');}catch(e){}};
  rq.onsuccess=function(){var db=rq.result;
    try{var tx=db.transaction('f','readwrite');tx.objectStore('f').put(v,k);
    tx.oncomplete=function(){cb&&cb(true);};tx.onerror=function(){cb&&cb(false);}&&cb&&cb(false);}
    catch(e){cb&&cb(false);}};
  rq.onerror=function(){cb&&cb(false);};}catch(e){cb&&cb(false);}
}
function idbGet(k,cb){
  try{var rq=indexedDB.open('brave',1);
  rq.onupgradeneeded=function(){try{rq.result.createObjectStore('f');}catch(e){}};
  rq.onsuccess=function(){var db=rq.result;
    try{var g=db.transaction('f').objectStore('f').get(k);
    g.onsuccess=function(){cb(g.result);};g.onerror=function(){cb(null);};}
    catch(e){cb(null);}};
  rq.onerror=function(){cb(null);};}catch(e){cb(null);}
}
var AUDSRC=null;
function stopTrackAudio(){if(AUDSRC){try{AUDSRC.stop();}catch(e){}AUDSRC=null;}}
function loadTrackAudio(tr){
  stopTrackAudio();
  if(!tr.audio)return;
  idbGet('bra_'+tr.id,function(ab){
    if(!ab||!AC)return;
    try{
      AC.decodeAudioData(ab).then(function(b){
        tr._audio=b;
        if(state==='play'&&TRK===tr&&!paused&&!AUDSRC){
          var src=AC.createBufferSource();src.buffer=b;
          var g=AC.createGain();g.gain.value=0.92;
          src.connect(g);g.connect(AC.destination);
          src.start(Math.max(AC.currentTime,acStart),Math.max(0,AC.currentTime-acStart));
          AUDSRC=src;
        }
      }).catch(function(){});
    }catch(e){}
  });
}''')

# --- 5) запустить загрузку аудио при старте трека ---
rep('  acStart=AC?AC.currentTime+2.2:0;\n  var tb=document.getElementById(\'tbtns\'),h=\'\';',
'''  acStart=AC?AC.currentTime+2.2:0;
  if(TRK.audio)loadTrackAudio(TRK);
  var tb=document.getElementById('tbtns'),h='';''')

# --- 6) синтез-аккомпанемент молчит, когда играет настоящий звук ---
rep('''function schedTick(){
  if(!AC)return;''',
'''function schedTick(){
  if(!AC)return;
  if(TRK&&TRK._audio){EVid=EV.length;return;}''')

# --- 7) стоп аудио на выходе и финише ---
rep('''function finish(){''',
'''function finish(){
  stopTrackAudio();''')
rep("state='menu';document.getElementById('tbtns').classList.remove('on');var back=ED_RETURN;",
    "state='menu';stopTrackAudio();document.getElementById('tbtns').classList.remove('on');var back=ED_RETURN;")
rep("function(){document.getElementById('pauseOv').classList.remove('on');if(AC)AC.resume();if(TRK)startTrack(TRK);});",
    "function(){document.getElementById('pauseOv').classList.remove('on');stopTrackAudio();if(AC)AC.resume();if(TRK)startTrack(TRK);});")

open(P,'w',encoding='utf-8').write(s)
print('OK wiring, size:',len(s))
