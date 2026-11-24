# -*- coding: utf-8 -*-
"""Полировка: палитра, кнопки, мобильная адаптация, фон с логотипом, спец-секции."""

P='/home/z/my-project/download/balaclava-rave.html'
s=open(P,encoding='utf-8').read()

def rep(old,new,cnt=1):
    global s
    n=s.count(old)
    assert n==cnt,'COUNT %d != %d: %r'%(n,cnt,old[:70])
    s=s.replace(old,new)

# --- 1) палитра: 4 цвета от тёмно-фиолетового к светло-сиреневому ---
rep("var laneCol=['#7c3aed','#a855f7','#d946ef','#f0abfc'];",
"""var laneCol=['#45129e','#7126d9','#a259f2','#e2ccff'];
function hexA(hex,a){var r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);return 'rgba('+r+','+g+','+b+','+a+')';}""")

# --- 2) стильные тач-кнопки на четверть экрана ---
rep('''#tbtns{position:absolute;left:0;right:0;bottom:0;display:none;gap:6px;padding:8px 8px calc(8px + env(safe-area-inset-bottom));z-index:20}
#tbtns.on{display:flex}
.tb{flex:1;height:clamp(64px,13vh,104px);border-radius:6px;border:2px solid var(--lc,#8b5cf6);
  background:linear-gradient(180deg,rgba(20,12,40,.85),rgba(10,6,22,.9));color:#efeafd;cursor:pointer;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;position:relative}
.tb span{font-weight:900;font-size:clamp(.72rem,2.9vw,.95rem);letter-spacing:.14em}
.tb i{font-style:normal;font-size:.6rem;color:var(--dim);font-weight:800;letter-spacing:.2em}
.tb.hit{background:linear-gradient(180deg,var(--lc,#8b5cf6),rgba(168,85,247,.25));box-shadow:0 0 22px var(--lc,#8b5cf6)}''',
'''#tbtns{position:absolute;left:0;right:0;bottom:0;display:none;gap:8px;padding:10px 10px calc(10px + env(safe-area-inset-bottom));z-index:20;
  background:linear-gradient(180deg,rgba(11,7,24,0),rgba(11,7,24,.8) 36%,#0b0718)}
#tbtns.on{display:flex}
.tb{flex:1;height:clamp(84px,22vh,150px);border-radius:12px;border:2px solid var(--lc,#8b5cf6);color:#f4f0ff;cursor:pointer;
  background:linear-gradient(180deg,var(--lcG,rgba(139,92,246,.22)),rgba(9,5,20,.78) 62%,rgba(6,3,14,.92));
  box-shadow:inset 0 2px 0 rgba(255,255,255,.16),inset 0 -12px 24px rgba(0,0,0,.45),0 0 18px var(--lcS,rgba(139,92,246,.35));
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;position:relative;
  touch-action:manipulation;-webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent;
  transition:transform .05s ease,box-shadow .05s ease,background .05s ease}
.tb span{font-weight:900;font-size:clamp(.74rem,3vw,1rem);letter-spacing:.14em;text-shadow:0 0 8px var(--lcS,transparent)}
.tb i{font-style:normal;font-size:.62rem;color:#cbb8ff;font-weight:800;letter-spacing:.2em;opacity:.85}
.tb.hit{transform:scale(.96);background:linear-gradient(180deg,var(--lc,#8b5cf6),var(--lcG,rgba(168,85,247,.25)) 78%);
  box-shadow:0 0 30px var(--lc,#8b5cf6),inset 0 2px 0 rgba(255,255,255,.3)}''')
rep('#tbtns.on~#btnPauseOv{bottom:calc(132px + env(safe-area-inset-bottom))}',
    '#tbtns.on~#btnPauseOv{bottom:calc(clamp(84px,22vh,150px) + 30px + env(safe-area-inset-bottom))}')

# --- 3) кнопки получают цвет своей дорожки (подложка+свечение) ---
rep("""for(var l=0;l<4;l++)h+='<button class="tb" data-l="'+l+'" style="--lc:'+laneCol[l]+'"><span>'+LANE_NAMES[l]+'</span><i>'+keyName(KB[l])+'</i></button>';""",
"""for(var l=0;l<4;l++)h+='<button class="tb" data-l="'+l+'" style="--lc:'+laneCol[l]+';--lcG:'+hexA(laneCol[l],0.22)+';--lcS:'+hexA(laneCol[l],0.5)+'"><span>'+LANE_NAMES[l]+'</span><i>'+keyName(KB[l])+'</i></button>';""")

# --- 4) линия удара учитывает крупные кнопки ---
rep('var bh=on?Math.min(Math.max(H*0.13,64),104)+16:0;',
    'var bh=on?Math.min(Math.max(H*0.22,84),150)+30:0;')

# --- 5) аккордная скобка в палитре ---
rep("ctx.fillStyle='rgba(217,70,239,0.28)';ctx.fillRect(xa,py-4,xb-xa,h+8);",
    "ctx.fillStyle='rgba(162,89,242,0.30)';ctx.fillRect(xa,py-4,xb-xa,h+8);")
rep("ctx.strokeStyle='rgba(240,171,252,0.55)';ctx.lineWidth=1;ctx.strokeRect(xa,py-4,xb-xa,h+8);",
    "ctx.strokeStyle='rgba(226,204,255,0.55)';ctx.lineWidth=1;ctx.strokeRect(xa,py-4,xb-xa,h+8);")

# --- 6) фон: полосы-дорожки, ритм-линии и приглушённый логотип в игре ---
rep('''function drawBg(){
  var g=ctx.createLinearGradient(0,0,0,H);
  g.addColorStop(0,'#0b0718');g.addColorStop(1,'#050309');
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  var tn=state==='play'?now:performance.now()/1000%997;
  for(var k=0;k<3;k++){
    ctx.strokeStyle='rgba(139,92,246,'+(0.05+k*0.035)+')';
    ctx.lineWidth=1.5;
    var y0=H*(0.16+k*0.3),amp=24+k*16,per=110+k*50,off=(tn*(20+k*14))%per;
    ctx.beginPath();
    var flip=0;
    for(var x=-per;x<W+per;x+=per/2){
      ctx.lineTo(x,y0+(flip?-amp:amp));
      flip=1-flip;
    }
    ctx.stroke();
  }
}''',
'''function drawBg(){
  var g=ctx.createLinearGradient(0,0,0,H);
  g.addColorStop(0,'#0b0718');g.addColorStop(1,'#050309');
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  var tn=state==='play'?now:performance.now()/1000%997;
  for(var k=0;k<3;k++){
    ctx.strokeStyle='rgba(139,92,246,'+(0.05+k*0.035)+')';
    ctx.lineWidth=1.5;
    var y0=H*(0.16+k*0.3),amp=24+k*16,per=110+k*50,off=(tn*(20+k*14))%per;
    ctx.beginPath();
    var flip=0;
    for(var x=-per;x<W+per;x+=per/2){
      ctx.lineTo(x,y0+(flip?-amp:amp));
      flip=1-flip;
    }
    ctx.stroke();
  }
  /* неоновые полосы-дорожки на фоне */
  ctx.fillStyle='rgba(139,92,246,0.045)';
  for(var v=0;v<9;v++)ctx.fillRect(W*(v+0.5)/9-13,0,26,H);
  if(state==='play'&&lineY>0){
    drawLogoDim();
    /* бегущие линии ритма по «дороге» */
    var spb=TRK?60/TRK.bpm:0.5,per2=spb*2;
    var k1=((now%per2)+per2)%per2/per2;
    ctx.strokeStyle='rgba(162,89,242,0.10)';ctx.lineWidth=2;
    for(var r=0;r<4;r++){
      var yl=lineY-((k1+r/4)%1)*(lineY-90);
      ctx.beginPath();ctx.moveTo(W/2-NL*LW/2,yl);ctx.lineTo(W/2+NL*LW/2,yl);ctx.stroke();
    }
  }
}
/* приглушённый логотип BALACLAVA RAVE за дорожками */
function drawLogoDim(){
  var s=Math.min(W*0.46,250),cx=W/2,cy=H*0.26;
  ctx.save();ctx.globalAlpha=0.11;
  var rg=ctx.createRadialGradient(cx,cy,0,cx,cy,s*0.5);
  rg.addColorStop(0,'rgba(139,92,246,0.55)');rg.addColorStop(1,'rgba(139,92,246,0)');
  ctx.fillStyle=rg;ctx.fillRect(cx-s*0.5,cy-s*0.5,s,s);
  ctx.strokeStyle='#8b5cf6';ctx.lineWidth=s*0.055;
  ctx.beginPath();ctx.arc(cx,cy,s*0.42,0,7);ctx.stroke();
  ctx.fillStyle='#1a1030';ctx.strokeStyle='#8b5cf6';ctx.lineWidth=s*0.02;
  ctx.beginPath();ctx.ellipse(cx,cy,s*0.22,s*0.27,0,0,7);ctx.fill();ctx.stroke();
  ctx.strokeStyle='rgba(196,181,253,0.4)';ctx.lineWidth=s*0.008;
  for(var kx=1;kx<4;kx++){
    var ky=cy-s*0.27+kx*s*0.135;
    ctx.beginPath();ctx.moveTo(cx-s*0.2,ky);ctx.lineTo(cx+s*0.2,ky);ctx.stroke();
  }
  ctx.fillStyle='#c4b5fd';ctx.shadowColor='#a855f7';ctx.shadowBlur=s*0.08;
  ctx.beginPath();ctx.ellipse(cx-s*0.09,cy-s*0.03,s*0.055,s*0.032,0,0,7);ctx.fill();
  ctx.beginPath();ctx.ellipse(cx+s*0.09,cy-s*0.03,s*0.055,s*0.032,0,0,7);ctx.fill();
  ctx.shadowBlur=0;
  ctx.strokeStyle='rgba(196,181,253,0.35)';ctx.lineWidth=s*0.012;
  ctx.strokeRect(cx-s*0.075,cy+s*0.08,s*0.15,s*0.09);
  var sw=s*1.06,sh=s*0.17,sy=cy+s*0.58;
  ctx.fillStyle='#0b0712';ctx.strokeStyle='#8b5cf6';ctx.lineWidth=s*0.02;
  ctx.fillRect(cx-sw/2,sy-sh/2,sw,sh);ctx.strokeRect(cx-sw/2,sy-sh/2,sw,sh);
  ctx.fillStyle='#c4b5fd';ctx.textAlign='center';ctx.textBaseline='middle';
  ctx.font='900 '+Math.round(s*0.105)+'px system-ui';
  ctx.fillText('BALACLAVA RAVE',cx,sy+s*0.01);
  ctx.restore();
}''')

# --- 7) спец-бары: перебивки, роллы, соло (до змеек, с метками занятости) ---
rep('''  insertSnakes(tr,spb);
  EV.sort(function(a,b){return a.t-b.t;});''',
'''  /* --- спец-бары: ⚡ перебивки, 🎹 роллы, 🔥 соло --- */
  for(var sb=4;sb<totalBars-2;sb++){
    var kind=sb%8===7?'fill':(sb%12===10?'roll':(sb%16===4?'solo':null));
    if(!kind)continue;
    var st0=sb*4*spb,tonesS=chordAt(tr,sb*4)[3].concat([chordAt(tr,sb*4)[3][0]+12]);
    BARS_BUSY[sb]=1;
    if(kind==='fill'){
      SECF.push({t:st0,txt:'⚡ ПЕРЕБИВКА'});
      CH=CH.filter(function(n){return !(n.lane===3&&n.t>=st0-0.01&&n.t<st0+4*spb-0.01);});
      var frN=DIFFV==='easy'?3:(DIFFV==='hard'?12:6),frSt=DIFFV==='hard'?0.25:(DIFFV==='easy'?1:0.5);
      for(var fr=0;fr<frN;fr++)CH.push(mk(3,st0+(1+fr*frSt)*spb,'snare',[],0,0.55+fr*0.04));
      CH.push(mk(1,st0+3.75*spb,'kick',[],0,1));
    }else if(kind==='roll'){
      SECF.push({t:st0,txt:'🎹 СОЛО-РУЛЛ'});
      CH=CH.filter(function(n){return n.t<st0-0.01||n.t>st0+4*spb+0.01;});
      var seq=(DIFFV==='easy')?[0,1,2,3]:[0,1,2,3,0,1,2,3];
      seq.forEach(function(ln,sk){
        CH.push(mk(ln,st0+sk*(DIFFV==='easy'?1:0.5)*spb,(tr.leadKind||'lead'),[tonesS[ln]],0.4*spb,1));
      });
    }else{
      SECF.push({t:st0,txt:'🔥 ОГНЕННОЕ СОЛО'});
      CH=CH.filter(function(n){return n.t<st0-0.01||n.t>st0+4*spb+0.01;});
      var laneS=Math.floor(sb/16)%4,seq2=(DIFFV==='easy')?[0,2,4,6]:[0,1,2,3,4,5,6,7];
      seq2.forEach(function(sk2){
        CH.push(mk(laneS,st0+sk2*0.5*spb,(tr.leadKind||'lead'),[tonesS[laneS]+(sk2>=6?12:0)],0.4*spb,1));
      });
    }
  }
  insertSnakes(tr,spb);
  EV.sort(function(a,b){return a.t-b.t;});''')

# --- 8) змейки не встают на спец-бары и вплотную после них ---
rep('''  for(var i=0;i<9;i++){
    var b=Math.round(from+(to-from)*i/8);
    if(b>lastBar+1&&b<total-2){picks.push(b);lastBar=b;}
  }''',
'''  function barFree(bb){return !BARS_BUSY[bb]&&!BARS_BUSY[bb+1]&&!BARS_BUSY[bb-1];}
  for(var i=0;i<9;i++){
    var b=Math.round(from+(to-from)*i/8),put=-1;
    for(var d2=0;d2<6;d2++){
      var bb2=b+((d2+1)>>1)*(d2%2?-1:1);
      if(bb2>lastBar+1&&bb2<total-2&&barFree(bb2)){put=bb2;break;}
    }
    if(put>0){picks.push(put);lastBar=put;}
  }''')

open(P,'w',encoding='utf-8').write(s)
print('OK polish, size:',len(s))
