# -*- coding: utf-8 -*-
"""Часть B: парсер MIDI, FFT-анализатор аудио, конвертеры в карту уровня."""

P='/home/z/my-project/download/balaclava-rave.html'
s=open(P,encoding='utf-8').read()

def rep(old,new,cnt=1):
    global s
    n=s.count(old)
    assert n==cnt,'COUNT %d != %d: %r'%(n,cnt,old[:70])
    s=s.replace(old,new)

anchor="""  edArm=false;this.innerHTML='🗑 СТЕРЕТЬ';CUSTOMS=[];saveCustoms();buildMenus();edSay('Свои треки стёрты',true);
});"""

importer=anchor+"""
/* ---------- ИМПОРТ: MIDI (.mid) ---------- */
function parseMIDI(ab){
  var d=new DataView(ab),p=0;
  function u8(){return d.getUint8(p++);}
  function u16(){var v=d.getUint16(p);p+=2;return v;}
  function u32(){var v=d.getUint32(p);p+=4;return v;}
  function vlq(){var v=0,b;do{b=u8();v=(v<<7)|(b&127);}while(b&128);return v;}
  if(d.byteLength<14||u32()!==0x4d546864)throw 'это не MIDI-файл';
  u16();u16();var ntr=u16(),div=u16();
  if(!div||(div&0x8000))throw 'SMPTE MIDI не поддерживается';
  var tempos=[],notes=[],kicks=[],snares=[];
  for(var ti=0;ti<ntr&&p<d.byteLength-8;ti++){
    if(u32()!==0x4d54726b)break;
    var len=u32(),end=Math.min(p+len,d.byteLength),tick=0,run=0;
    while(p<end){
      tick+=vlq();
      var st=u8();
      if(st===0xff){var mt=u8(),ml=vlq();
        if(mt===0x51&&ml===3)tempos.push([tick,(d.getUint8(p)<<16)|(d.getUint8(p+1)<<8)|d.getUint8(p+2)]);
        p+=ml;
      }else if(st===0xf0||st===0xf7){p+=vlq();}
      else{
        if(st&0x80)run=st;else{p--;st=run;}
        var typ=st&240,ch=st&15;
        if(typ===0x90){var pt=u8(),vl=u8();
          if(vl>0){
            if(ch===9){if(pt===35||pt===36)kicks.push(tick);else if(pt===37||pt===38||pt===40)snares.push(tick);}
            else notes.push({on:tick,off:-1,p:pt,ch:ch});
          }else{for(var i=notes.length-1;i>=0;i--){if(notes[i].p===pt&&notes[i].ch===ch&&notes[i].off<0){notes[i].off=tick;break;}}}
        }else if(typ===0x80){var p2=u8();u8();
          for(var i2=notes.length-1;i2>=0;i2--){if(notes[i2].p===p2&&notes[i2].ch===ch&&notes[i2].off<0){notes[i2].off=tick;break;}}}
        else if(typ===0xc0||typ===0xd0){u8();}
        else{u8();u8();}
      }
    }
    p=end;
  }
  tempos.sort(function(a,b){return a[0]-b[0];});
  if(!tempos.length||tempos[0][0]>0)tempos.unshift([0,500000]);
  var bpm=Math.round(60000000/tempos[0][1]);
  function tickSec(t){var sec=0,lt=0,us=tempos[0][1];
    for(var i=0;i<tempos.length;i++){var tt=tempos[i][0];if(tt>=t)break;
      if(tt>lt)sec+=(tt-lt)*(us/1e6)/div;
      lt=tt;us=tempos[i][1];}
    sec+=(t-lt)*(us/1e6)/div;return sec;}
  var maxT=0,out=[];
  notes.forEach(function(n){
    if(n.off<0)n.off=n.on+div;
    var t0=tickSec(n.on),t1=tickSec(n.off);
    if(t1<=t0)t1=t0+0.1;
    out.push({t:t0,d:t1-t0,p:n.p});
    if(t1>maxT)maxT=t1;});
  kicks.forEach(function(t){var q=tickSec(t);if(q>maxT)maxT=q;});
  snares.forEach(function(t){var q=tickSec(t);if(q>maxT)maxT=q;});
  if(!out.length)throw 'в MIDI нет нот';
  return {bpm:bpm,dur:maxT,notes:out,
    kbeats:kicks.map(function(t){return tickSec(t)*bpm/60;}),
    sbeats:snares.map(function(t){return tickSec(t)*bpm/60;})};
}

function midiToTrack(md,fname){
  var q=0.25,bpm=md.bpm,BPS=bpm/60;
  var sorted=md.notes.slice().sort(function(a,b){return a.t-b.t||b.p-a.p;});
  var mel=[];
  sorted.forEach(function(n){
    var last=mel[mel.length-1];
    if(!last||n.t>=last.t+last.d-0.02)mel.push({t:n.t,d:n.d,p:n.p});
    else if(n.p>last.p){last.d=Math.max(0.1,n.t-last.t);mel.push({t:n.t,d:n.d,p:n.p});}
  });
  var melQ=mel.map(function(n){
    return [Math.max(0,Math.round(n.t*BPS/q)*q),Math.max(q,Math.round(n.d*BPS/q)*q),n.p];});
  var totalB=Math.max(8,Math.ceil((md.dur*BPS)/4)*4);
  var LB=Math.max(16,Math.min(2048,totalB));
  melQ=melQ.filter(function(m){return m[0]<LB-0.001&&m[2]>=24&&m[2]<108;})
    .map(function(m){return [m[0],Math.min(m[1],LB-m[0]),m[2]];});
  if(!melQ.length)throw 'не нашёл нот мелодии для карты';
  var chords=[];
  for(var w=0;w<totalB;w+=4){
    var snd=md.notes.filter(function(n){return n.t<w+4&&n.t+n.d>w;});
    if(!snd.length)continue;
    var root=snd[0];for(var i=0;i<snd.length;i++)if(snd[i].p<root.p)root=snd[i];
    var rpc=((root.p%12)+12)%12,pcs=[];
    snd.forEach(function(n){var pc=((n.p%12)+12)%12;if(pcs.indexOf(pc)<0)pcs.push(pc);});
    pcs.sort(function(a,b){return a-b;});
    chords.push([w,4,36+rpc,pcs.slice(0,4).map(function(pc){return 48+rpc+((pc-rpc+12)%12);})]);
  }
  if(!chords.length)chords=[[0,4,45,[57,60,64]]];
  var dk=[],ds=[];
  md.kbeats.forEach(function(b){var m=((Math.round(b*2)/2)%LB+LB)%LB;if(dk.indexOf(m)<0)dk.push(m);});
  md.sbeats.forEach(function(b){var m=((Math.round(b*2)/2)%LB+LB)%LB;if(ds.indexOf(m)<0)ds.push(m);});
  dk.sort(function(a,b){return a-b;});ds.sort(function(a,b){return a-b;});
  if(!dk.length&&!ds.length){dk=[0,1,2,3];ds=[1,3];}
  var nps=melQ.length/Math.max(1,md.dur*BPS);
  var stars=nps>2.2?5:(nps>1.4?4:(nps>0.8?3:(nps>0.4?2:1)));
  return {name:String(fname||'ИМПОРТ MIDI').replace(/\\.[a-z0-9]+$/i,'').toUpperCase().slice(0,26)||'ИМПОРТ MIDI',
    tag:'СВОЙ',bpm:bpm,bassKind:'saw',leadKind:'lead',stars:stars,loopBeats:LB,egap:1,
    drum:{k:dk,s:ds},mel:melQ,chords:chords};
}

/* ---------- ИМПОРТ: АУДИО (MP3/WAV/OGG) — FFT-поиск нот ---------- */
function fftMag(re,im){
  var n=re.length,i,j,bit;
  for(i=1,j=0;i<n;i++){bit=n>>1;for(;j&bit;bit>>=1)j^=bit;j^=bit;
    if(i<j){var tr=re[i];re[i]=re[j];re[j]=tr;var ti=im[i];im[i]=im[j];im[j]=ti;}}
  for(var len=2;len<=n;len<<=1){
    var ang=-2*Math.PI/len,wr=Math.cos(ang),wi=Math.sin(ang),half=len>>1;
    for(i=0;i<n;i+=len){
      var cr=1,ci=0;
      for(var k=0;k<half;k++){
        var ar=re[i+k],ai=im[i+k],br=re[i+k+half],bi=im[i+k+half];
        var vr=br*cr-bi*ci,vi=br*ci+bi*cr;
        re[i+k]=ar+vr;im[i+k]=ai+vi;re[i+k+half]=ar-vr;im[i+k+half]=ai-vi;
        var ncr=cr*wr-ci*wi;ci=cr*wi+ci*wr;cr=ncr;
      }
    }
  }
  var m=new Float32Array(n>>1);
  for(var i3=0;i3<(n>>1);i3++)m[i3]=Math.hypot(re[i3],im[i3]);
  return m;
}
function analyzeAudio(buf,onp){
  var sr0=buf.sampleRate,nch=buf.numberOfChannels,len0=buf.length;
  var mono=new Float32Array(len0);
  for(var c=0;c<nch;c++){var ch=buf.getChannelData(c);for(var i=0;i<len0;i++)mono[i]+=ch[i]/nch;}
  var sr=sr0,data=mono;
  if(sr0>24000){
    var h=Math.floor(sr0/24000),n2=Math.floor(len0/h),d2=new Float32Array(n2);
    for(var i2=0;i2<n2;i2++)d2[i2]=mono[i2*h];
    data=d2;sr=sr0/h;
  }
  var N=2048,hop=512,frames=Math.min(12000,Math.floor((data.length-N)/hop));
  if(frames<20)throw 'файл слишком короткий';
  var win=new Float32Array(N);
  for(var w=0;w<N;w++)win[w]=0.5-0.5*Math.cos(2*Math.PI*w/N);
  var melF=new Float32Array(frames),bassF=new Float32Array(frames),flux=new Float32Array(frames);
  var binLo=Math.ceil(75*N/sr),binHi=Math.min(Math.floor(1400*N/sr),N/2-2);
  var bLo=Math.ceil(45*N/sr),bHi=Math.min(Math.floor(220*N/sr),N/2-2);
  var prev=null;
  for(var f=0;f<frames;f++){
    var re=new Float32Array(N),im=new Float32Array(N),off=f*hop,rm=0;
    for(var s2=0;s2<N;s2++){re[s2]=data[off+s2]*win[s2];rm+=re[s2]*re[s2];}
    rm=Math.sqrt(rm/N);
    var mg=fftMag(re,im),fx=0;
    if(prev)for(var b3=binLo;b3<=binHi;b3++)fx+=Math.max(0,mg[b3]-prev[b3]);
    flux[f]=fx;
    var pk=binLo,pv=-1,avg=0;
    for(var b4=binLo;b4<=binHi;b4++){avg+=mg[b4];if(mg[b4]>pv){pv=mg[b4];pk=b4;}}
    avg/=(binHi-binLo+1);
    if(pv>avg*6&&rm>0.004){
      var y1=mg[pk-1],y2=mg[pk],y3=mg[pk+1],den=(y1-2*y2+y3);
      var dp=Math.abs(den)>1e-9?0.5*(y1-y3)/den:0;
      if(dp>1)dp=1;if(dp<-1)dp=-1;
      melF[f]=69+12*Math.log2((pk+dp)*sr/N/440);
    }else melF[f]=0;
    var pb=bLo,pbv=-1;
    for(var b5=bLo;b5<=bHi;b5++)if(mg[b5]>pbv){pbv=mg[b5];pb=b5;}
    bassF[f]=pbv>avg*2?69+12*Math.log2(pb*sr/N/440):0;
    if(onp&&f%Math.max(1,frames>>5)===0)onp(f/frames);
    prev=mg;
  }
  /* темп: автокорреляция спектрального потока */
  var fps=sr/hop,bestLag=0,bestV=0;
  for(var lag=Math.round(fps*0.32);lag<=Math.round(fps*1.25)&&lag<frames>>1;lag++){
    var v=0;for(var i=0;i<frames-lag;i+=2)v+=flux[i]*flux[i+lag];
    v/=(frames-lag);
    if(v>bestV){bestV=v;bestLag=lag;}
  }
  var bpm=bestLag?Math.round(60/(bestLag/fps)):120;
  while(bpm<85)bpm*=2;
  while(bpm>190)bpm=Math.round(bpm/2);
  /* сегменты нот из высоты тона */
  var beatSec=60/bpm,segs=[],st=-1,acc=0,cnt=0,cur=0;
  for(var i4=0;i4<=frames;i4++){
    var m=i4<frames?melF[i4]:0,ok=i4<frames&&m>0;
    if(ok){
      if(st<0){st=i4;acc=m;cnt=1;cur=m;}
      else if(Math.abs(m-cur)<0.8){acc+=m;cnt++;cur=acc/cnt;}
      else{if(cnt>=3)segs.push([st,i4,cur]);st=i4;acc=m;cnt=1;cur=m;}
    }else if(st>=0){if(cnt>=3)segs.push([st,i4,cur]);st=-1;}
  }
  var merged=[];
  segs.forEach(function(sg){
    var last=merged[merged.length-1];
    if(last&&Math.abs(sg[2]-last[2])<0.5&&(sg[0]-last[1])*hop/sr<0.12){last[1]=sg[1];last[2]=(last[2]+sg[2])/2;}
    else merged.push(sg);
  });
  var q=0.25,melA=merged.map(function(sg){
    var t0=Math.max(0,Math.round(sg[0]*hop/sr/beatSec/q)*q);
    var d0=Math.max(q,Math.round((sg[1]-sg[0])*hop/sr/beatSec/q)*q);
    return [t0,d0,Math.round(sg[2])];
  }).filter(function(m2){return m2[2]>=24&&m2[2]<100;})
    .sort(function(a,b){return a[0]-b[0];}).slice(0,900);
  if(!melA.length)throw 'не услышал нот — попробуй запись с ясной мелодией';
  var totalB=Math.max(8,Math.ceil(frames*hop/sr/beatSec/4)*4);
  var LB=Math.max(16,Math.min(2048,totalB));
  var fpsB=beatSec*fps,chords=[];
  for(var w2=0;w2<totalB;w2+=2){
    var i0=Math.floor(w2*fpsB),i1=Math.min(frames,Math.floor((w2+2)*fpsB));
    var vals=[];
    for(var i5=i0;i5<i1;i5++)if(bassF[i5]>0)vals.push(bassF[i5]);
    var root;
    if(vals.length>2){vals.sort(function(a,b){return a-b;});root=vals[vals.length>>1];}
    else{
      var mIn=melA.filter(function(m3){return m3[0]>=w2&&m3[0]<w2+2;});
      root=mIn.length?mIn[0][2]:57;
    }
    var pc=((Math.round(root)%12)+12)%12,pcs2=[];
    melA.forEach(function(m4){if(m4[0]>=w2&&m4[0]<w2+2){var p5=((m4[2]%12)+12)%12;if(pcs2.indexOf(p5)<0)pcs2.push(p5);}});
    if(!pcs2.length)pcs2=[pc,(pc+4)%12,(pc+7)%12];
    chords.push([w2,2,36+pc,pcs2.slice(0,4).map(function(p6){return 48+pc+((p6-pc+12)%12);})]);
  }
  if(!chords.length)chords=[[0,4,45,[57,60,64]]];
  var nps2=melA.length/Math.max(1,frames*hop/sr);
  return {bpm:bpm,loopBeats:LB,mel:melA,chords:chords,
    stars:nps2>2.2?5:(nps2>1.4?4:(nps2>0.8?3:(nps2>0.4?2:1)))};
}

/* ---------- обработчики загрузки файлов ---------- */
document.getElementById('edMidi').addEventListener('click',function(){document.getElementById('edMidiFile').click();});
document.getElementById('edMidiFile').addEventListener('change',function(){
  var f=this.files[0];this.value='';if(!f)return;
  edSay('Читаю MIDI: '+f.name+'…',true);
  var fr=new FileReader();
  fr.onload=function(){
    try{
      var tr=midiToTrack(parseMIDI(fr.result),f.name);
      edTxt.value=JSON.stringify(tr);
      edSay('MIDI готов: '+tr.name+' • '+tr.bpm+' BPM • '+tr.mel.length+' нот • '+tr.drum.k.length+' бочек. Жми ▶ ПРОГНАТЬ или 💾 ДОБАВИТЬ',true);
    }catch(e){edSay('ОШИБКА MIDI: '+e.message,false);}
  };
  fr.onerror=function(){edSay('Не смог прочитать файл',false);};
  fr.readAsArrayBuffer(f);
});
document.getElementById('edAudio').addEventListener('click',function(){document.getElementById('edAudioFile').click();});
document.getElementById('edAudioFile').addEventListener('change',function(){
  var f=this.files[0];this.value='';if(!f)return;
  edSay('Декодирую аудио: '+f.name+'…',true);
  ensureAudio();
  var fr2=new FileReader();
  fr2.onload=function(){
    var ab=fr2.result;
    if(!AC){edSay('Нет аудио-движка в этом браузере',false);return;}
    AC.decodeAudioData(ab).then(function(buf){
      edSay('Ищу ноты (FFT-анализ)…',true);
      var res=analyzeAudio(buf,function(pr){edSay('Анализ: '+Math.round(pr*100)+'%',true);});
      var base=f.name.replace(/\\.[a-z0-9]+$/i,'');
      var tr={id:slugId(base,true),audio:true,name:(base||'ИЗ АУДИО').toUpperCase().slice(0,26),tag:'СВОЙ',
        bpm:res.bpm,bassKind:'saw',leadKind:'lead',stars:res.stars,loopBeats:res.loopBeats,egap:1,
        drum:{k:[0,2],s:[1,3]},mel:res.mel,chords:res.chords};
      edTxt.value=JSON.stringify(tr);
      idbPut('bra_'+tr.id,ab,function(ok){
        edSay(ok?('Готово: '+tr.bpm+' BPM • '+tr.mel.length+' нот • звук сохранён и будет играть в игре. Жми ▶ или 💾')
          :('Готово: '+tr.bpm+' BPM • '+tr.mel.length+' нот (звук не сохранился — будет синтез). Жми ▶ или 💾'),ok);
      });
    }).catch(function(e){edSay('ОШИБКА аудио: '+((e&&e.message)||'формат не декодировался'),false);});
  };
  fr2.onerror=function(){edSay('Не смог прочитать файл',false);};
  fr2.readAsArrayBuffer(f);
});"""

rep(anchor,importer)
open(P,'w',encoding='utf-8').write(s)
print('OK importer, size:',len(s))
