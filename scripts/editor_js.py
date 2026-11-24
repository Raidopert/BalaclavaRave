# -*- coding: utf-8 -*-
"""Часть 2: JS редактора — свои треки (localStorage), прогон, импорт/экспорт."""

P='/home/z/my-project/download/balaclava-rave.html'
s=open(P,encoding='utf-8').read()

def rep(old,new,cnt=1):
    global s
    n=s.count(old)
    assert n==cnt,'COUNT %d != %d: %r'%(n,cnt,old[:70])
    s=s.replace(old,new)

rep("""state='menu';document.getElementById('tbtns').classList.remove('on');var back=ED_RETURN;ED_RETURN=false;buildMenus();showScreen(back?'scrEditor':'scrCover');});""",
"""state='menu';document.getElementById('tbtns').classList.remove('on');var back=ED_RETURN;ED_RETURN=false;buildMenus();showScreen(back?'scrEditor':'scrCover');});
/* ---------- РЕДАКТОР: свои треки ---------- */
var ED_RETURN=false;
var CUSTOMS=[];
try{CUSTOMS=JSON.parse(sGet('br_custom')||'[]')||[];}catch(e){CUSTOMS=[];}
function saveCustoms(){sSet('br_custom',JSON.stringify(CUSTOMS));}
function LIST(){return TRACKS.concat(CUSTOMS);}
function slugId(name){return 'c_'+String(name).toLowerCase().replace(/[^a-zа-яё0-9]+/gi,'-').replace(/^-+|-+$/g,'').slice(0,20);}
function normTrack(t){
  var num=function(v){return typeof v==='number'&&isFinite(v);};
  if(!t||typeof t!=='object')return 'объект не найден';
  if(!t.name)return 'нет name';
  if(!Array.isArray(t.mel)||!t.mel.length)return 'нет mel (мелодии)';
  if(!Array.isArray(t.chords)||!t.chords.length)return 'нет chords (аккордов)';
  var LB=Math.max(4,Math.min(64,Math.round(+t.loopBeats||16)));
  for(var j=0;j<t.mel.length;j++){
    var m=t.mel[j];
    if(!Array.isArray(m)||m.length<3||!num(m[0])||!num(m[1])||!num(m[2]))return 'mel['+j+'] — нужен [доля, длина, midi]';
    if(m[0]+m[1]>LB+0.001)return 'mel['+j+'] выходит за loopBeats='+LB;
  }
  for(var c=0;c<t.chords.length;c++){
    var ch=t.chords[c];
    if(!Array.isArray(ch)||ch.length<4||!Array.isArray(ch[3])||!ch[3].length||!num(ch[0])||!num(ch[1])||!num(ch[2])||!ch[3].every(num))return 'chords['+c+'] — нужен [доля, длина, бас, [ноты]]';
  }
  var d=t.drum||{},k=Array.isArray(d.k)&&d.k.every(num)?d.k.slice():[0,1,2,3];
  var sv=Array.isArray(d.s)&&d.s.every(num)?d.s.slice():[1,3];
  return {id:slugId(t.name),name:String(t.name).slice(0,26),tag:'СВОЙ',
    bpm:Math.max(40,Math.min(300,Math.round(+t.bpm||120))),bassKind:t.bassKind||'saw',leadKind:t.leadKind||'lead',
    stars:Math.max(1,Math.min(5,Math.round(+t.stars||3))),loopBeats:LB,egap:Math.max(1,+t.egap||1),
    drum:{k:k,s:sv},mel:t.mel,chords:t.chords};
}
function edParse(limit){
  var v=edTxt.value.trim();
  if(!v)return {ok:false,err:'пусто — вставь JSON'};
  var raw;try{raw=JSON.parse(v);}catch(e){return {ok:false,err:'JSON: '+e.message};}
  var arr=Array.isArray(raw)?raw:[raw];
  if(arr.length>limit)return {ok:false,err:'не больше '+limit+' треков за раз'};
  var out=[];
  for(var i=0;i<arr.length;i++){
    var t=normTrack(arr[i]);
    if(typeof t==='string')return {ok:false,err:'трек #'+(i+1)+': '+t};
    out.push(t);
  }
  return {ok:true,list:out};
}
var edTxt=document.getElementById('edText'),edMsg=document.getElementById('edMsg');
function edSay(txt,ok){edMsg.textContent=txt;edMsg.className='edMsg '+(ok?'ok':'err');}
document.getElementById('btnEditor').addEventListener('click',function(){ED_RETURN=false;edSay('Своих треков: '+CUSTOMS.length+' • вставь JSON трека или массива',true);showScreen('scrEditor');});
document.getElementById('edBack').addEventListener('click',function(){buildMenus();showScreen('scrCover');});
document.getElementById('edTest').addEventListener('click',function(){
  var r=edParse(1);
  if(!r.ok){edSay('ОШИБКА: '+r.err,false);return;}
  ED_RETURN=true;edSay('Прогоняю: '+r.list[0].name+' • «В МЕНЮ» вернёт в редактор',true);
  startTrack(r.list[0]);
});
document.getElementById('edSave').addEventListener('click',function(){
  var r=edParse(50);
  if(!r.ok){edSay('ОШИБКА: '+r.err,false);return;}
  var names={};LIST().forEach(function(t){names[t.name]=1;});
  var add=0;
  r.list.forEach(function(t){if(!names[t.name]){CUSTOMS.push(t);add++;}});
  saveCustoms();buildMenus();
  edSay(add?('ДОБАВЛЕНО '+add+' • всего своих: '+CUSTOMS.length+' — ищи в списке с меткой «СВОЙ»'):'Такое название уже есть — не добавлен',!!add);
});
document.getElementById('edImport').addEventListener('click',function(){
  var r=edParse(50);
  if(!r.ok){edSay('ОШИБКА: '+r.err,false);return;}
  CUSTOMS=r.list;saveCustoms();buildMenus();
  edSay('ЗАМЕНЕНО: своих треков теперь '+CUSTOMS.length,true);
});
document.getElementById('edExport').addEventListener('click',function(){
  if(!CUSTOMS.length){edSay('Своих треков пока нет',false);return;}
  edTxt.value=JSON.stringify(CUSTOMS);edSay('Треки выведены в текст ниже — копируй и храни',true);
});
var edArm=false;
document.getElementById('edClear').addEventListener('click',function(){
  if(!edArm){edArm=true;this.innerHTML='<b>ТОЧНО?</b>';return;}
  edArm=false;this.innerHTML='🗑 СТЕРЕТЬ';CUSTOMS=[];saveCustoms();buildMenus();edSay('Свои треки стёрты',true);
});""")

open(P,'w',encoding='utf-8').write(s)
print('OK editor js, size:',len(s))
