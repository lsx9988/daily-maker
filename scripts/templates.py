# -*- coding: utf-8 -*-
"""本地已测可用的单文件 HTML 成品模板库。

每个工具都是自包含页面（内联 CSS/JS/SVG，无外部依赖、可离线打开）。
成品代码由本地模板保证可用；LLM 只写配套说明文档，不直接生成成品代码，
避免出现跑不起来的页面。新增工具在此加一个 render_* 函数并在 TEMPLATES 登记。
"""
import html


def _esc(v):
    return html.escape(str(v if v is not None else ""), quote=True)


def _shell(title, date, issue, body, script=""):
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(title)}</title>
<style>
:root{{--accent:#4f6b9a}}
*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;background:#f7f7f5;color:#1a1b1c;font-family:-apple-system,'Segoe UI','Microsoft YaHei',sans-serif;line-height:1.6}}
.wrap{{max-width:760px;margin:0 auto;padding:24px 16px}}
.top{{display:flex;justify-content:space-between;align-items:center;font-size:13px;color:#5f6670;margin-bottom:14px}}
.top a{{color:#4f6b9a;text-decoration:none}}
h1{{font-size:22px;margin:0 0 4px}}
.sub{{font-size:13px;color:#5f6670;margin-bottom:18px}}
.card{{background:#fff;border-radius:10px;padding:18px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
button{{font:inherit;border:1px solid var(--accent);background:var(--accent);color:#fff;border-radius:8px;padding:8px 14px;cursor:pointer}}
button.ghost{{background:#fff;color:var(--accent)}}
input,select,textarea{{font:inherit;padding:8px 10px;border:1px solid #d8dbe0;border-radius:8px;width:100%}}
textarea{{min-height:120px;resize:vertical}}
.row{{display:flex;gap:10px;flex-wrap:wrap;align-items:center}}
.muted{{color:#8a9099;font-size:12px}}
.big{{font-size:40px;font-weight:700;text-align:center;margin:10px 0}}
</style></head><body><div class="wrap">
<div class="top"><span>第 {issue} 期 · {date}</span><a href="index.html">← 返回说明</a></div>
<h1>{_esc(title)}</h1>
<div class="sub">本地单文件工具，离线可用，不上传数据。</div>
{body}
</div>
<script>
function mulberry32(a){{return function(){{a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}}}
{script}
</script></body></html>"""


def _hsl(h, s, l):
    return f"hsl({h:.0f} {s:.0f}% {l:.0f}%)"


def render_color_palette(p):
    body = """
<div class="card">
  <div class="row" style="margin-bottom:12px"><button id="regen">换一组配色</button><span class="muted">点击色块复制 HEX</span></div>
  <div id="palette" style="display:flex;gap:10px;flex-wrap:wrap"></div>
  <div id="gradient" style="height:48px;border-radius:8px;margin-top:14px"></div>
</div>"""
    script = """
const rng=mulberry32(SEED);
function hex(h,s,l){const c=(x)=>Math.round(x*255).toString(16).padStart(2,'0');return '#'+c(l)+c(0)+c(0);}
function hslToHex(h,s,l){s/=100;l/=105;const a=s*Math.min(l,1-l);const f=n=>{const k=(n+h/30)%12;const color=l-a*Math.max(-1,Math.min(k-3,Math.min(9-k,1)));return Math.round(color*255).toString(16).padStart(2,'0')};return '#'+f(0)+f(8)+f(4);}
function draw(){
  const base=rng()*360;const box=document.getElementById('palette');box.innerHTML='';const cols=[];
  for(let i=0;i<5;i++){const h=(base+i*36+rng()*18)%360;const col=hslToHex(h,65,58);cols.push(col);
    const d=document.createElement('div');d.style.cssText='flex:1 1 100px;height:120px;border-radius:10px;background:'+col+';display:flex;align-items:flex-end;justify-content:center;padding:8px;cursor:pointer;color:#fff;font-size:12px';
    d.textContent=col;d.onclick=()=>copy(col);box.appendChild(d);}
  document.getElementById('gradient').style.background=`linear-gradient(90deg,${cols[0]},${cols[2]},${cols[4]})`;
}
function copy(t){navigator.clipboard?navigator.clipboard.writeText(t).then(()=>alert('已复制 '+t)):prompt('复制色值',t);}
document.getElementById('regen').onclick=draw;draw();""".replace("SEED", str(p["seed"]))
    return _shell(p["title"], p["date"], p["issue"], body, script)


def render_gradient(p):
    body = """
<div class="card">
  <div class="row" style="margin-bottom:12px"><button id="regen">换一组渐变</button><button class="ghost" id="copy">复制 CSS</button></div>
  <div id="preview" style="height:220px;border-radius:10px"></div>
  <textarea id="css" readonly style="margin-top:12px"></textarea>
</div>"""
    script = """
const rng=mulberry32(SEED);let css='';
function hsl(h,s,l){return `hsl(${h} ${s}% ${l}%)`;}
function draw(){const a=rng()*360,b=(a+60+rng()*160)%360;const ang=Math.floor(rng()*360);
  css=`linear-gradient(${ang}deg, ${hsl(a,70,55)}, ${hsl(b,70,55)})`;
  document.getElementById('preview').style.background=css;
  document.getElementById('css').value='background: '+css+';';}
document.getElementById('regen').onclick=draw;
document.getElementById('copy').onclick=()=>{navigator.clipboard?navigator.clipboard.writeText(css):prompt('复制 CSS',css);};
draw();""".replace("SEED", str(p["seed"]))
    return _shell(p["title"], p["date"], p["issue"], body, script)


def render_text_tools(p):
    body = """
<div class="card">
  <textarea id="in" placeholder="在此粘贴或输入文本…"></textarea>
  <div class="row" style="margin:12px 0">
    <button data-op="upper">大写</button><button data-op="lower">小写</button>
    <button data-op="trim">去首尾空格</button><button data-op="dedup">行去重排序</button>
    <button data-op="space">压缩多余空格</button><button class="ghost" id="clear">清空</button>
  </div>
  <div class="muted" id="stat"></div>
  <textarea id="out" readonly style="margin-top:10px" placeholder="结果显示在这里"></textarea>
</div>"""
    script = """
const inp=document.getElementById('in'),out=document.getElementById('out'),stat=document.getElementById('stat');
function refresh(){const t=inp.value;const lines=t.split('\\n');
  stat.textContent=`字符 ${t.length} · 行数 ${lines.length} · 单词 ${(t.match(/\\S+/g)||[]).length}`;}
function apply(op){let t=inp.value;
  if(op==='upper')t=t.toUpperCase();else if(op==='lower')t=t.toLowerCase();
  else if(op==='trim')t=t.split('\\n').map(x=>x.trim()).join('\\n');
  else if(op==='dedup')t=[...new Set(t.split('\\n').map(x=>x.trim()).filter(Boolean))].sort().join('\\n');
  else if(op==='space')t=t.replace(/[ \\t]+/g,' ').replace(/\\s+$/,'');
  out.value=t;refresh();}
document.querySelectorAll('[data-op]').forEach(b=>b.onclick=()=>apply(b.dataset.op));
document.getElementById('clear').onclick=()=>{inp.value='';out.value='';refresh();};
inp.oninput=refresh;refresh();"""
    return _shell(p["title"], p["date"], p["issue"], body, script)


def render_unit_converter(p):
    body = """
<div class="card">
  <div class="row">
    <input type="number" id="val" value="1" step="any">
    <select id="from"></select>
  </div>
  <div id="results" style="margin-top:14px"></div>
</div>"""
    script = """
const UNITS={mm:1,cm:10,m:1000,km:1000000,inch:25.4,ft:304.8,yd:914.4};
const names={mm:'毫米',cm:'厘米',m:'米',km:'千米',inch:'英寸',ft:'英尺',yd:'码'};
const sel=document.getElementById('from');Object.keys(UNITS).forEach(u=>{const o=document.createElement('option');o.value=u;o.textContent=names[u];sel.appendChild(o);});
function conv(){const v=parseFloat(document.getElementById('val').value)||0;const f=sel.value;const mm=v*UNITS[f];const box=document.getElementById('results');box.innerHTML='';
  Object.keys(UNITS).forEach(u=>{if(u===f)return;const r=document.createElement('div');r.style.cssText='padding:6px 0;border-bottom:1px solid #eee';r.textContent=`${names[u]}：${(mm/UNITS[u]).toFixed(4)}`;box.appendChild(r);});}
document.getElementById('val').oninput=conv;sel.onchange=conv;conv();"""
    return _shell(p["title"], p["date"], p["issue"], body, script)


def render_timestamp(p):
    body = """
<div class="card">
  <div class="row"><input type="datetime-local" id="dt"><button id="toTs">转时间戳</button></div>
  <div class="row" style="margin-top:12px"><input type="number" id="ts" placeholder="Unix 秒"><button id="toDt">转日期</button></div>
  <div id="out" class="muted" style="margin-top:12px"></div>
</div>"""
    script = """
const out=document.getElementById('out');
document.getElementById('toTs').onclick=()=>{const v=document.getElementById('dt').value;if(!v)return;const t=Math.floor(new Date(v).getTime()/1000);out.textContent='Unix 秒：'+t+'　毫秒：'+t*1000;};
document.getElementById('toDt').onclick=()=>{const v=parseInt(document.getElementById('ts').value);if(!v)return;const d=new Date(v*(String(v).length>10?1:1000));out.textContent='本地时间：'+d.toLocaleString('zh-CN');};
const now=Math.floor(Date.now()/1000);document.getElementById('ts').placeholder='Unix 秒（如 '+now+'）';"""
    return _shell(p["title"], p["date"], p["issue"], body, script)


def render_timer(p):
    body = """
<div class="card">
  <div class="row"><input type="number" id="min" value="5" min="1" style="max-width:120px"> 分钟</div>
  <div class="big" id="clock">05:00</div>
  <div class="row" style="justify-content:center">
    <button id="start">开始</button><button class="ghost" id="pause">暂停</button><button class="ghost" id="reset">重置</button>
  </div>
</div>"""
    script = """
let left=0,timer=null;const clock=document.getElementById('clock');
function fmt(s){const m=Math.floor(s/60),x=s%60;return String(m).padStart(2,'0')+':'+String(x).padStart(2,'0');}
function setMin(){left=Math.max(1,parseInt(document.getElementById('min').value)||1)*60;clock.textContent=fmt(left);}
document.getElementById('start').onclick=()=>{if(timer)return;if(left<=0)setMin();timer=setInterval(()=>{left--;clock.textContent=fmt(left);if(left<=0){clearInterval(timer);timer=null;alert('时间到！');}},1000);};
document.getElementById('pause').onclick=()=>{clearInterval(timer);timer=null;};
document.getElementById('reset').onclick=()=>{clearInterval(timer);timer=null;setMin();};
setMin();"""
    return _shell(p["title"], p["date"], p["issue"], body, script)


def render_decision(p):
    items = p.get("items") or ["早上喝豆浆", "中午吃米饭", "晚上散步", "周末整理桌面"]
    opts = "\n".join(items[:12])
    body = f"""
<div class="card">
  <textarea id="list" placeholder="每行一个候选项">{_esc(opts)}</textarea>
  <div class="row" style="margin:12px 0">
    <button id="pick">随机抽一个</button><button id="coin">抛硬币</button><button id="dice">掷骰子</button>
  </div>
  <div class="big" id="result">?</div>
</div>"""
    script = """
const res=document.getElementById('result');
document.getElementById('pick').onclick=()=>{const arr=document.getElementById('list').value.split('\\n').map(x=>x.trim()).filter(Boolean);if(!arr.length)return alert('先填候选项');res.textContent=arr[Math.floor(Math.random()*arr.length)];};
document.getElementById('coin').onclick=()=>res.textContent=Math.random()<0.5?'正面':'反面';
document.getElementById('dice').onclick=()=>res.textContent=(1+Math.floor(Math.random()*6))+' 点';"""
    return _shell(p["title"], p["date"], p["issue"], body, script)


def render_checklist(p):
    items = p.get("items") or ["准备工具", "核对材料", "按步骤操作", "检查成品"]
    rows = "".join(
        f'<label style="display:block;padding:8px 0;border-bottom:1px solid #eee"><input type="checkbox" class="ck" style="width:auto"> {_esc(x)}</label>'
        for x in items[:20]
    )
    body = f"""
<div class="card">
  <div class="muted" id="prog"></div>
  <div id="list">{rows}</div>
</div>"""
    script = """
const boxes=[...document.querySelectorAll('.ck')];const prog=document.getElementById('prog');
function upd(){const done=boxes.filter(b=>b.checked).length;prog.textContent=`已完成 ${done}/${boxes.length}`;}
boxes.forEach(b=>b.onchange=upd);upd();"""
    return _shell(p["title"], p["date"], p["issue"], body, script)


def render_counter(p):
    body = """
<div class="card">
  <div class="big" id="n">0</div>
  <div class="row" style="justify-content:center">
    <button id="dec">−</button><button id="inc">＋</button><button class="ghost" id="zero">清零</button>
  </div>
</div>"""
    script = """
let n=0;const el=document.getElementById('n');
document.getElementById('inc').onclick=()=>{n++;el.textContent=n;};
document.getElementById('dec').onclick=()=>{n--;el.textContent=n;};
document.getElementById('zero').onclick=()=>{n=0;el.textContent=n;};"""
    return _shell(p["title"], p["date"], p["issue"], body, script)


def render_generative_art(p):
    variant = p["seed"] % 3
    body = f"""
<div class="card">
  <div class="row" style="margin-bottom:12px"><button id="regen">换一张</button><span class="muted">种子 #{p['seed']} · 变体 {variant+1}</span></div>
  <svg id="art" viewBox="0 0 600 360" style="width:100%;height:auto;border-radius:10px;background:#111"></svg>
</div>"""
    script = """
const rng=mulberry32(SEED);const svg=document.getElementById('art');const NS='http://www.w3.org/2000/svg';
function el(t,a){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);return e;}
function draw(){svg.innerHTML='';const v=VARIANT;const hue=rng()*360;
  if(v===0){for(let i=0;i<24;i++){const y=20+i*14;const pts=[];for(let x=0;x<=600;x+=20)pts.push(x+','+(y+Math.sin((x/60)+i+rng()*2)*10));svg.appendChild(el('polyline',{points:pts.join(' '),fill:'none',stroke:`hsl(${(hue+i*8)%360} 70% 65%)`,strokeWidth:2}));}}
  else if(v===1){for(let r=150;r>10;r-=14){svg.appendChild(el('circle',{cx:300,cy:180,r:r,fill:'none',stroke:`hsl(${(hue+r)%360} 70% 60%)`,strokeWidth:3,opacity:.8}));}}
  else{for(let i=0;i<160;i++){svg.appendChild(el('circle',{cx:rng()*600,cy:rng()*360,r:rng()*33+2,fill:`hsl(${(hue+rng()*60)%360} 70% ${50+rng()*30}%)`,opacity:.8}));}}
}
document.getElementById('regen').onclick=draw;draw();""".replace("SEED", str(p["seed"])).replace("VARIANT", str(variant))
    return _shell(p["title"], p["date"], p["issue"], body, script)


TEMPLATES = {
    "color-palette": render_color_palette,
    "gradient": render_gradient,
    "text-tools": render_text_tools,
    "unit-converter": render_unit_converter,
    "timestamp": render_timestamp,
    "timer": render_timer,
    "decision": render_decision,
    "checklist": render_checklist,
    "counter": render_counter,
    "generative-art": render_generative_art,
}


def render_app(tool_type, params):
    """按 tool_type 生成成品 HTML；未知类型回退计数器。"""
    fn = TEMPLATES.get(tool_type, render_counter)
    return fn(params)
