# -*- coding: utf-8 -*-
"""Мобильные фиксы (iPhone) + геймплей-полировка + стиль (палитра не трогается)."""

P='/home/z/my-project/download/balaclava-rave.html'
s=open(P,encoding='utf-8').read()

def rep(old,new,cnt=1):
    global s
    n=s.count(old)
    assert n==cnt,'COUNT %d != %d: %r'%(n,cnt,old[:70])
    s=s.replace(old,new)

# --- 1) iOS: размер текста, запрет callout на долгом тапе ---
rep("*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}",
    "*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;-webkit-touch-callout:none}")
rep("html,body{height:100%;overflow:hidden;background:var(--bg);color:var(--txt);\n  font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}",
"""html,body{height:100%;overflow:hidden;background:var(--bg);color:var(--txt);
  font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;-webkit-text-size-adjust:100%;text-size-adjust:100%}
button,.tcard,.schip{touch-action:manipulation}""")

# --- 2) safe-area сверху/снизу для PWA-статусбара ---
rep("  overflow-y:auto;overflow-x:hidden;padding:16px;-webkit-overflow-scrolling:touch}",
    "  overflow-y:auto;overflow-x:hidden;padding:calc(16px + env(safe-area-inset-top)) 16px calc(16px + env(safe-area-inset-bottom));-webkit-overflow-scrolling:touch}")

# --- 3) фидбек нажатий (косой скеw сохраняем) ---
rep(".btn:hover{background:#1c1240;box-shadow:0 0 18px rgba(139,92,246,.45)}",
""".btn:hover{background:#1c1240;box-shadow:0 0 18px rgba(139,92,246,.45)}
.btn:active{transform:skew(-6deg) translateY(1px) scale(.985);filter:brightness(1.12)}
.btn.main:active{filter:brightness(1.18)}
.tcard:active{transform:translateX(4px) scale(.995);background:rgba(24,16,48,.85)}
.schip:active{transform:scale(.94)}
/* ---------- НОВЫЙ РЕКОРД ---------- */
.resNew{display:none;margin:8px 0 0;text-align:center;font-weight:900;letter-spacing:.18em;font-size:.9rem;color:#ffd700;
  text-shadow:0 0 14px rgba(255,215,0,.55);animation:recPulse 1.1s ease-in-out infinite}
.resNew.on{display:block}
@keyframes recPulse{0%,100%{opacity:1}50%{opacity:.5;transform:scale(.97)}}""")

# --- 4) плашка рекорда в результатах ---
rep('''      <div class="resScore" id="resScore"></div>
      <div class="resStats" id="resStats"></div>''',
'''      <div class="resScore" id="resScore"></div>
      <div class="resNew" id="resNew">🏆 НОВЫЙ РЕКОРД!</div>
      <div class="resStats" id="resStats"></div>''')

# --- 5) логика рекорда (только если побит настоящий прошлый) ---
rep("  document.getElementById('resScore').textContent=score+' ОЧКОВ';",
"""  document.getElementById('resScore').textContent=score+' ОЧКОВ';
  document.getElementById('resNew').classList.toggle('on',!!prev&&score>prev.score);""")

# --- 6) пауза при сворачивании приложения/вкладки + поворот экрана ---
rep("function doPause(){",
"""document.addEventListener('visibilitychange',function(){
  if(document.hidden&&state==='play'&&!paused)doPause();
});
window.addEventListener('orientationchange',function(){setTimeout(layout,120);});
function doPause(){""")

open(P,'w',encoding='utf-8').write(s)
print('OK mobile polish, size:',len(s))
