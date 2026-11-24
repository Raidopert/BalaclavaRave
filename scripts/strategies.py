# -*- coding: utf-8 -*-
"""Стратегии (стили игры): КЛАССИКА / СНАЙПЕР / ПОТОК / РИСК — окна, очки, комбо."""

P='/home/z/my-project/download/balaclava-rave.html'
s=open(P,encoding='utf-8').read()

def rep(old,new,cnt=1):
    global s
    n=s.count(old)
    assert n==cnt,'COUNT %d != %d: %r'%(n,cnt,old[:70])
    s=s.replace(old,new)

# --- 1) UI: строка стратегий под сложностью ---
rep('''    </div>
    <div id="trackList"></div>''',
'''    </div>
    <div class="schRow" id="styleRow">
      <span class="schLbl">СТРАТЕГИЯ:</span>
      <button class="schip on" data-s="classic" title="Стандартные правила">КЛАССИКА</button>
      <button class="schip" data-s="sniper" title="Узкие окна попадания, очки ×1.5">СНАЙПЕР</button>
      <button class="schip" data-s="flow" title="Широкие окна, МИМО не рвёт комбо, очки ×0.75">ПОТОК</button>
      <button class="schip" data-s="risk" title="МИМО −200 очков, комбо растёт быстрее">РИСК</button>
    </div>
    <div id="trackList"></div>''')

# --- 2) метаданные стратегий + производные окна ---
rep("""  easy:{name:'ЛЁГКИЙ',tapp:2.1},
  mid:{name:'СРЕДНИЙ',tapp:1.6},
  hard:{name:'СЛОЖНЫЙ',tapp:1.15}
};""",
"""  easy:{name:'ЛЁГКИЙ',tapp:2.1},
  mid:{name:'СРЕДНИЙ',tapp:1.6},
  hard:{name:'СЛОЖНЫЙ',tapp:1.15}
};
/* --- стратегии: модификаторы риска/награды (wm=окна, pm=очки, cap/step=множитель,
       nobreak=МИМО не рвёт комбо, penalty=штраф очков за МИМО) --- */
var STYLMETA={
  classic:{name:'КЛАССИКА',wm:1,pm:1,cap:8,step:8,nobreak:false,penalty:0},
  sniper:{name:'СНАЙПЕР',wm:0.6,pm:1.5,cap:8,step:8,nobreak:false,penalty:0},
  flow:{name:'ПОТОК',wm:1.35,pm:0.75,cap:6,step:8,nobreak:true,penalty:0},
  risk:{name:'РИСК',wm:1,pm:1.2,cap:14,step:6,nobreak:false,penalty:200}
};
var STYLEV=(function(){var d=sGet('br_style');return (d&&STYLMETA[d])?d:'classic';})();
var SPERF=PERF,SGOOD=GOOD;
function styleSync(){var st=STYLMETA[STYLEV];SPERF=PERF*st.wm;SGOOD=GOOD*st.wm;}
styleSync();""")

# --- 3) рекорды отдельно на каждую стратегию ---
rep("var key='br_best_'+TRK.id+'_'+DIFFV,prev=null;",
    "var key='br_best_'+TRK.id+'_'+DIFFV+'_'+STYLEV,prev=null;")
rep("try{best=JSON.parse(sGet('br_best_'+tr.id+'_'+DIFFV)||'null');}catch(e){}",
    "try{best=JSON.parse(sGet('br_best_'+tr.id+'_'+DIFFV+'_'+STYLEV)||'null');}catch(e){}")

# --- 4) окна попадания: живые SPERF/SGOOD ---
rep("    if(n.t>now+GOOD)break;",
    "    if(n.t>now+SGOOD)break;")
rep("if(best>=0&&bd<=GOOD)hitNote(best,bd);",
    "if(best>=0&&bd<=SGOOD)hitNote(best,bd);")
rep("n.judged=true;n.hit=true;n.perf=dt<=PERF;",
    "n.judged=true;n.hit=true;n.perf=dt<=SPERF;")

# --- 5) очки и множитель по стратегии ---
rep("score+=Math.round((n.perf?100:55)*mult);",
    "score+=Math.round((n.perf?100:55)*mult*STYLMETA[STYLEV].pm);")
rep("mult=1+Math.min(7,Math.floor(combo/8)*0.5);",
    "mult=1+Math.min(STYLMETA[STYLEV].cap-1,Math.floor(combo/STYLMETA[STYLEV].step)*0.5);")

# --- 6) МИМО: поведение по стратегии ---
rep("      n.judged=true;n.miss=true;missCnt++;judgedCnt++;combo=0;mult=1;applauseFired=false;",
"""      n.judged=true;n.miss=true;missCnt++;judgedCnt++;applauseFired=false;
      var stm=STYLMETA[STYLEV];
      if(stm.nobreak){combo=Math.floor(combo/2);mult=Math.max(1,mult*0.6);}
      else{combo=0;mult=1;}
      if(stm.penalty){score=Math.max(0,score-stm.penalty);addFloat(laneXOf(n.lane)+LW/2,lineY-58,'−'+stm.penalty,'#ff5c8a');}""")

# --- 7) синк окон на старте трека ---
rep("  TAPPV=DIFFMETA[DIFFV].tapp;",
    "  TAPPV=DIFFMETA[DIFFV].tapp;\n  styleSync();")

# --- 8) строка стратегии в результатах ---
rep("'<div>ФУЛЛ КОМБО <b>'+(fc?'+3000':'—')+'</b></div>';",
    "'<div>ФУЛЛ КОМБО <b>'+(fc?'+3000':'—')+'</b></div><div>СТРАТЕГИЯ <b>'+STYLMETA[STYLEV].name+'</b></div>';")

# --- 9) синк чипов в buildMenus + клики ---
rep("""  document.querySelectorAll('#diffRow .schip').forEach(function(c){c.classList.toggle('on',c.dataset.d===DIFFV);});
}
/* ====================== ВВОД ====================== */""",
"""  document.querySelectorAll('#diffRow .schip').forEach(function(c){c.classList.toggle('on',c.dataset.d===DIFFV);});
  document.querySelectorAll('#styleRow .schip').forEach(function(c){c.classList.toggle('on',c.dataset.s===STYLEV);});
}
/* ====================== ВВОД ====================== */""")

rep("/* ====================== ВВОД ====================== */",
"""document.querySelectorAll('#styleRow .schip').forEach(function(c){c.addEventListener('click',function(){
  STYLEV=c.dataset.s;sSet('br_style',STYLEV);styleSync();
  document.querySelectorAll('#styleRow .schip').forEach(function(x){x.classList.toggle('on',x===c);});
  buildMenus();
});});
/* ====================== ВВОД ====================== */""")

open(P,'w',encoding='utf-8').write(s)
print('OK strategies, size:',len(s))
