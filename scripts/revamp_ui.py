# -*- coding: utf-8 -*-
"""Часть 1: чистка меню (обложка/треки), новые сложности, убраны схема и описания."""
import re, sys

P='/home/z/my-project/download/balaclava-rave.html'
s=open(P,encoding='utf-8').read()
def rep(old,new,cnt=1):
    global s
    n=s.count(old)
    assert n==cnt, 'COUNT %d != %d for: %r' % (n,cnt,old[:80])
    s=s.replace(old,new)

# --- обложка: тэглайн, убрать coverNote/ctrlLine/schRow ---
rep('<div class="tagline">ЛОНДОН • АНДЕРГРАУНД • БАРАБАННЫЕ МЕЛОДИИ</div>',
    '<div class="tagline">КЛАССИКА • ПУБЛИЧНОЕ ДОСТОЯНИЕ</div>')
rep('''    <div class="coverNote">7 ТРЕКОВ • БЕЗ СЛОВ • 2–3 МИН • НОЧНОЙ КОР / ТЕХНО / ДРАМ-ЭНД-БЕЙС</div>
    <div class="ctrlLine">КЛАВИАТУРА: <b>D F J K</b> (+ <b>→</b> = F, <b>X</b> = J) • ГЕЙМПАД: <b>LB</b> • <b>СТРЕЛКА →</b> • <b>X</b> • <b>RB</b> (+LT RT) • ПАУЗА: <b>ESC / P / START</b> • СЛОЖНОСТИ: 3 / 4 КНОПКИ / ФУЛЛ • КЛАВИШИ МОЖНО ПЕРЕНАЗНАЧИТЬ: <b>⚙</b></div>
    <div class="schRow" id="schRow">
      <span class="schLbl">СХЕМА:</span>
      <button class="schip on" data-s="auto">АВТО</button>
      <button class="schip" data-s="keys">КЛАВИАТУРА</button>
      <button class="schip" data-s="touch">СЕНСОР</button>
      <button class="schip" data-s="pad">ГЕЙМПАД</button>
    </div>
''','')

# --- шапка экрана треков: убрать подсказку ---
rep('''      <div class="barTitle">ВЫБОР ТРЕКА</div>
      <div class="barHint">СИНТЕЗ В БРАУЗЕРЕ<br>БЕЗ СЛОВ • ВЕЧЕРИНКА</div>
''','''      <div class="barTitle">ВЫБОР ТРЕКА</div>
''')

# --- сложности: новые названия уровней ---
rep('''      <button class="schip" data-d="easy">ЛЕГКО • 3 КНОПКИ</button>
      <button class="schip on" data-d="norm">НОРМА • 4 КНОПКИ</button>
      <button class="schip" data-d="fast">ФУЛЛ • СКОРОСТЬ</button>''',
'''      <button class="schip" data-d="easy">ЛЁГКИЙ</button>
      <button class="schip on" data-d="mid">СРЕДНИЙ</button>
      <button class="schip" data-d="hard">СЛОЖНЫЙ</button>''')

# --- состояние: схема, DIFFMETA ---
rep("var scheme=sGet('br_scheme')||'auto';\n",'')
rep('''/* --- сложности, испытания, бонус ×8 --- */
var DIFFV=(function(){var d=sGet('br_diff');return d==='easy'||d==='fast'?d:'norm';})();
var DIFFMETA={
  easy:{name:'ЛЕГКО',nl:3,tapp:1.5,names:['БАС','НОТА','ДРАМ'],keys:['D','F','J']},
  norm:{name:'НОРМА',nl:4,tapp:1.5,names:['БАС','КИК','НОТА','ДРАМ'],keys:['D','F','J','K']},
  fast:{name:'ФУЛЛ',nl:4,tapp:0.8,names:['БАС','КИК','НОТА','ДРАМ'],keys:['D','F','J','K']}
};''',
'''/* --- сложности: 3 уровня на каждом треке, всегда 4 дорожки --- */
var DIFFV=(function(){var d=sGet('br_diff');return (d==='easy'||d==='hard')?d:'mid';})();
var DIFFMETA={
  easy:{name:'ЛЁГКИЙ',tapp:2.1},
  mid:{name:'СРЕДНИЙ',tapp:1.6},
  hard:{name:'СЛОЖНЫЙ',tapp:1.15}
};
var LANE_NAMES=['БАС','КИК','НОТА','ДРАМ'];''')

# --- touchVisible без scheme ---
rep('''function touchVisible(){
  if(tbMode==='on')return true;
  if(tbMode==='off')return false;
  return scheme==='touch'||(scheme==='auto'&&isTouch);
}''',
'''function touchVisible(){
  if(tbMode==='on')return true;
  if(tbMode==='off')return false;
  return isTouch;
}''')

# --- startTrack: фиксированные 4 дорожки ---
rep('''function startTrack(tr){
  var dm=DIFFMETA[DIFFV];
  NL=dm.nl;TAPPV=dm.tapp;KEYLBL=dm.keys;''',
'''function startTrack(tr){
  TAPPV=DIFFMETA[DIFFV].tapp;''')
rep('''  var tb=document.getElementById('tbtns'),h='';
  for(var l=0;l<dm.nl;l++)h+='<button class="tb" data-l="'+l+'" style="--lc:'+laneCol[l]+'"><span>'+dm.names[l]+'</span><i>'+keyName(KB[l])+'</i></button>';
  tb.innerHTML=h;
  KEYLBL=KB.map(keyName).slice(0,dm.nl);''',
'''  var tb=document.getElementById('tbtns'),h='';
  for(var l=0;l<4;l++)h+='<button class="tb" data-l="'+l+'" style="--lc:'+laneCol[l]+'"><span>'+LANE_NAMES[l]+'</span><i>'+keyName(KB[l])+'</i></button>';
  tb.innerHTML=h;
  KEYLBL=KB.map(keyName);''')

# --- buildMenus: длительность, звёзды, синхронизация ---
rep('var dur=88*4*60/tr.bpm;','var dur=trackDur(tr);')
rep("+'★'.repeat(tr.diff)+'","+'★'.repeat(tr.stars)+'")
rep('''  var sr=document.getElementById('schRow');
  sr.querySelectorAll('.schip').forEach(function(c){c.classList.toggle('on',c.dataset.s===scheme);});
''','')

# --- убрать обработчик schRow ---
rep('''document.getElementById('schRow').addEventListener('click',function(e){
  var b=e.target.closest('.schip');if(!b)return;
  scheme=b.dataset.s;
  sSet('br_scheme',scheme);
  document.querySelectorAll('#schRow .schip').forEach(function(c){c.classList.toggle('on',c.dataset.s===scheme);});
});
''','')

# --- CSS: убрать правила удалённых блоков ---
s=re.sub(r'\.coverNote\{[^}]*\}\n','',s)
s=re.sub(r'\.ctrlLine\{[^}]*\}\n','',s)
s=re.sub(r'\.ctrlLine b\{[^}]*\}\n','',s)
s=re.sub(r'\.barHint\{[^}]*\}\n','',s)

open(P,'w',encoding='utf-8').write(s)
print('OK part1, size:',len(s))
