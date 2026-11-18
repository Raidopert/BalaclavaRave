# -*- coding: utf-8 -*-
# Создаёт две версии Ритм-Змейки из базового файла:
#   ritm-zmeyka-telefon.html — сенсорное управление, змейка с отступом над пальцем
#   ritm-zmeyka-pk.html      — клавиатура F/J/D/K + геймпад (A/B, LB/RB, стик для змейки)
import io, sys

BASE = '/home/z/my-project/download/ritm-zmeyka.html'
MOB  = '/home/z/my-project/download/ritm-zmeyka-telefon.html'
PK   = '/home/z/my-project/download/ritm-zmeyka-pk.html'

src = io.open(BASE, 'r', encoding='utf-8').read()

def apply(text, pairs, name):
    for i, (old, new) in enumerate(pairs):
        n = text.count(old)
        if n != 1:
            print('FAIL [%s] pattern #%d found %d times:\n%r' % (name, i, n, old[:120]))
            sys.exit(1)
        text = text.replace(old, new, 1)
    print('%s: %d replacements OK' % (name, len(pairs)))
    return text

# ================= МОБИЛЬНАЯ ВЕРСИЯ =================
mob = src

mob = apply(mob, [
# заголовок и подзаголовок
('<title>Ритм-Змейка</title>',
 '<title>Ритм-Змейка • Телефон</title>'),
('<div class="sub">4 кнопки • белая линия • змейка</div>',
 '<div class="sub">Телефон • сенсор • белая линия</div>'),
# убрать строку про клавиатуру
('   <div class="row"><span class="ic">⌨️</span><span>Клавиши: <b>1</b> и <b>2</b> — ноты, <b>Z</b> и <b>X</b> (или ← и →) — барабаны.</span></div>\n',
 ''),
# строка про змейку: подсказка для сенсора
('   <div class="row"><span class="ic">🐍</span><span>Волна — веди пальцем змейку вдоль дорожки, не упусти!</span></div>',
 '   <div class="row"><span class="ic">🐍</span><span>Волна — веди змейку пальцем вдоль дорожки. Голова змейки рисуется <b>чуть выше пальца</b>, чтобы её было видно!</span></div>'),
# голова змейки выше пальца
('  const hx=(w.pid!=null&&w.mx!=null)?w.mx:w.tx, hy=(w.pid!=null&&w.my!=null)?w.my:w.ty;',
 '  const hx=(w.pid!=null&&w.mx!=null)?w.mx:w.tx;\n'
 '  const hy=(w.pid!=null&&w.my!=null)?Math.max(L.band[0]+12,Math.min(L.band[1]-12,w.my-56)):w.ty;'),
# подсказка во время волны
("    ctx.fillStyle='#ffd43b'; ctx.fillText('Веди змейку вдоль волны 👆',L.ox+L.cw/2,L.band[0]+18);",
 "    ctx.fillStyle='#ffd43b'; ctx.fillText('Веди змейку пальцем — голова выше 👆',L.ox+L.cw/2,L.band[0]+18);"),
], 'MOBILE')

# ================= ПК ВЕРСИЯ =================
pk = src

GAMEPAD_BLOCK = u'''/* ================= ГЕЙМПАД ================= */
let padSeen=false, padPt=null;
const padPrev={};
window.addEventListener('gamepadconnected',()=>{padSeen=true;});
function padEdge(gp,i,down,up){
  const p=!!(gp.buttons[i]&&gp.buttons[i].pressed);
  if(p&&!padPrev[i]&&down)down();
  else if(!p&&padPrev[i]&&up)up();
  padPrev[i]=p;
}
function pollPad(dt){
  const gps=navigator.getGamepads?navigator.getGamepads():[];
  const gp=gps&&(gps[0]||gps[1]); if(!gp||!gp.connected)return;
  padSeen=true;
  padEdge(gp,9,()=>{ if(state==='play'){paused?doResume():doPause();} });
  if(state!=='play'||paused)return;
  padEdge(gp,0,()=>{pointers.set(3000,{role:'mel',idx:0});melodyPress(0,3000);},()=>handleUp(3000));
  padEdge(gp,1,()=>{pointers.set(3001,{role:'mel',idx:1});melodyPress(1,3001);},()=>handleUp(3001));
  padEdge(gp,4,()=>drumPress(0));
  padEdge(gp,5,()=>drumPress(1));
  padEdge(gp,14,()=>drumPress(0));
  padEdge(gp,15,()=>drumPress(1));
  const ax=gp.axes[0]||0, ay=gp.axes[1]||0;
  if(Math.hypot(ax,ay)>0.3){
    if(!padPt)padPt={x:L.ox+L.cw/2,y:(L.band[0]+L.band[1])/2};
    padPt.x=Math.max(L.ox+16,Math.min(L.ox+L.cw-16,padPt.x+ax*460*dt));
    padPt.y=Math.max(L.band[0]+6,Math.min(L.band[1]-6,padPt.y+ay*460*dt));
  }
}

/* ================= ЦИКЛ И СОБЫТИЯ ================= */'''

pk = apply(pk, [
# заголовок и подзаголовок
('<title>Ритм-Змейка</title>',
 '<title>Ритм-Змейка • ПК</title>'),
('<div class="sub">4 кнопки • белая линия • змейка</div>',
 '<div class="sub">ПК • клавиатура или геймпад • белая линия</div>'),
# барабаны: убрать телефонное предложение про большие пальцы
('   <div class="row"><span class="ic">🥁</span><span>Барабаны по краям: <b style="color:#74c0fc">БАМ</b> слева, <b style="color:#ffa94d">ЦСС</b> справа. Левый большой палец — БАМ и нота 1, правый — нота 2 и ЦСС. Табличка <b style="color:#b197fc">ВМЕСТЕ! 👐</b> — ударь по обоим барабанам разом!</span></div>',
 '   <div class="row"><span class="ic">🥁</span><span>Барабаны по краям: <b style="color:#74c0fc">БАМ</b> слева, <b style="color:#ffa94d">ЦСС</b> справа. Табличка <b style="color:#b197fc">ВМЕСТЕ! 👐</b> — ударь по обоим барабанам разом (D+K или LB+RB)!</span></div>'),
# волна: мышь или стик
('   <div class="row"><span class="ic">🐍</span><span>Волна — веди пальцем змейку вдоль дорожки, не упусти!</span></div>',
 '   <div class="row"><span class="ic">🐍</span><span>Волна — веди змейку <b>мышью</b> или <b>левым стиком</b> геймпада вдоль дорожки.</span></div>'),
# клавиатура: F J D K + строка про геймпад
('   <div class="row"><span class="ic">⌨️</span><span>Клавиши: <b>1</b> и <b>2</b> — ноты, <b>Z</b> и <b>X</b> (или ← и →) — барабаны.</span></div>',
 '   <div class="row"><span class="ic">⌨️</span><span>Клавиши: <b>F</b> и <b>J</b> — ноты, <b>D</b> и <b>K</b> — барабаны. Длинные ноты — держи клавишу. (Работают и 1/2, Z/X, ←/→.)</span></div>\n'
 '   <div class="row"><span class="ic">🎮</span><span>Геймпад: <b>A/✕</b> — нота 1, <b>B/○</b> — нота 2, <b>LB/RB</b> — барабаны, левый стик — волна, <b>Start</b> — пауза.</span></div>'),
# шире на десктопе
('  const cw=Math.min(W,520); L.cw=cw; L.ox=(W-cw)/2;',
 '  const cw=Math.min(W,660); L.cw=cw; L.ox=(W-cw)/2;'),
# клавиатура: down
("""  if(e.code==='Digit1'){ pointers.set(1000,{role:'mel',idx:0}); melodyPress(0,1000); }
  if(e.code==='Digit2'){ pointers.set(1001,{role:'mel',idx:1}); melodyPress(1,1001); }
  if(e.code==='KeyZ'||e.code==='ArrowLeft'){ pointers.set(2000,{role:'drum',pad:0}); drumPress(0); }
  if(e.code==='KeyX'||e.code==='ArrowRight'){ pointers.set(2001,{role:'drum',pad:1}); drumPress(1); }""",
 """  if(e.code==='KeyF'||e.code==='Digit1'){ pointers.set(1000,{role:'mel',idx:0}); melodyPress(0,1000); }
  if(e.code==='KeyJ'||e.code==='Digit2'){ pointers.set(1001,{role:'mel',idx:1}); melodyPress(1,1001); }
  if(e.code==='KeyD'||e.code==='KeyZ'||e.code==='ArrowLeft'){ pointers.set(2000,{role:'drum',pad:0}); drumPress(0); }
  if(e.code==='KeyK'||e.code==='KeyX'||e.code==='ArrowRight'){ pointers.set(2001,{role:'drum',pad:1}); drumPress(1); }"""),
# клавиатура: up
("""  if(e.code==='Digit1')handleUp(1000);
  if(e.code==='Digit2')handleUp(1001);
  if(e.code==='KeyZ'||e.code==='ArrowLeft')handleUp(2000);
  if(e.code==='KeyX'||e.code==='ArrowRight')handleUp(2001);""",
 """  if(e.code==='KeyF'||e.code==='Digit1')handleUp(1000);
  if(e.code==='KeyJ'||e.code==='Digit2')handleUp(1001);
  if(e.code==='KeyD'||e.code==='KeyZ'||e.code==='ArrowLeft')handleUp(2000);
  if(e.code==='KeyK'||e.code==='KeyX'||e.code==='ArrowRight')handleUp(2001);"""),
# вибрация + геймпад-отдача
("function vibrate(ms){ try{ if(navigator.vibrate) navigator.vibrate(ms); }catch(e){} }",
 "function padRumble(str,dur){ try{ const gp=(navigator.getGamepads&&navigator.getGamepads()||[])[0];\n"
 "  if(gp&&gp.vibrationActuator)gp.vibrationActuator.playEffect('dual-rumble',{duration:dur,strongMagnitude:str,weakMagnitude:str*0.6}); }catch(e){} }\n"
 "function vibrate(ms){ try{ if(navigator.vibrate) navigator.vibrate(ms); }catch(e){} padRumble(Math.min(ms/60,0.9),ms); }"),
# геймпад-блок перед циклом
('/* ================= ЦИКЛ И СОБЫТИЯ ================= */',
 GAMEPAD_BLOCK),
# волна: виртуальный курсор геймпада
("""      if(w.pid!=null){
        const pt=pointers.get(w.pid);
        if(pt){
          w.mx=pt.x; w.my=pt.y;
          const ok=Math.hypot(pt.x-tx,pt.y-ty)<=CFG.waveR;
          if(ok){ w.zoneT=(w.zoneT||0)+dt; addScore(Math.round(120*dt));
            if(!w.lastPluck||now-w.lastPluck>0.22){ w.lastPluck=now;
              const arp=[220,261.63,329.63,392,440,523.25];
              if(AC)tone(arp[wavePluckI++%arp.length],'sine',0.12,0.25,AC.currentTime,0.4); } }
          (w.trail||(w.trail=[])).push({x:pt.x,y:pt.y,ok,t:now});
          if(w.trail.length>80)w.trail.shift();
        } else w.pid=null;
      }""",
 """      let ctrl=null;
      if(w.pid!=null){ const pt=pointers.get(w.pid); if(pt)ctrl={x:pt.x,y:pt.y}; else w.pid=null; }
      if(!ctrl&&padPt)ctrl={x:padPt.x,y:padPt.y};
      if(ctrl){
          w.mx=ctrl.x; w.my=ctrl.y;
          const ok=Math.hypot(ctrl.x-tx,ctrl.y-ty)<=CFG.waveR;
          if(ok){ w.zoneT=(w.zoneT||0)+dt; addScore(Math.round(120*dt));
            if(!w.lastPluck||now-w.lastPluck>0.22){ w.lastPluck=now;
              const arp=[220,261.63,329.63,392,440,523.25];
              if(AC)tone(arp[wavePluckI++%arp.length],'sine',0.12,0.25,AC.currentTime,0.4); } }
          (w.trail||(w.trail=[])).push({x:ctrl.x,y:ctrl.y,ok,t:now});
          if(w.trail.length>80)w.trail.shift();
      }"""),
# при старте волны ставить курсор геймпада на начало дорожки
('      if(w.phase===undefined)w.phase=Math.random()*Math.PI*2;',
 '      if(w.phase===undefined){w.phase=Math.random()*Math.PI*2; if(w.pid==null)padPt={x:tx,y:ty};}'),
# индикатор ввода в HUD
("""  ctx.textAlign='right'; ctx.fillStyle='rgba(255,255,255,0.5)'; ctx.font='600 9px system-ui';
  ctx.fillText('ТОЧНОСТЬ',W-60,16);
  ctx.fillStyle='#fff'; ctx.font='900 18px system-ui'; ctx.fillText(Math.round(acc*100)+'%',W-60,31);""",
 """  ctx.textAlign='right'; ctx.fillStyle='rgba(255,255,255,0.5)'; ctx.font='600 9px system-ui';
  ctx.fillText('ТОЧНОСТЬ',W-60,16);
  ctx.fillStyle='#fff'; ctx.font='900 18px system-ui'; ctx.fillText(Math.round(acc*100)+'%',W-60,31);
  ctx.textAlign='center'; ctx.fillStyle='rgba(255,255,255,0.45)'; ctx.font='600 10px system-ui';
  ctx.fillText(padSeen?'🎮 ГЕЙМПАД':'⌨️ КЛАВИАТУРА: F J D K',L.ox+L.cw/2,50);"""),
], 'PK')

# вызов pollPad в цикле
pk = apply(pk, [
("""  if(state==='play'&&!paused){ now=t/1000-t0Perf; update(dt); }
  draw();""",
 """  if(state==='play'&&!paused){ now=t/1000-t0Perf; update(dt); }
  if(state==='play')pollPad(dt);
  draw();"""),
], 'PK-loop')

io.open(MOB, 'w', encoding='utf-8').write(mob)
io.open(PK, 'w', encoding='utf-8').write(pk)
print('written:', MOB, len(mob), 'bytes;', PK, len(pk), 'bytes')
