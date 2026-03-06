import streamlit as st
from groq import Groq
import time, re

def md_to_html(text):
    mb = {}
    def sm(m):
        k = f"__M{len(mb)}__"; mb[k] = m.group(0); return k
    text = re.sub(r'\$\$.+?\$\$', sm, text, flags=re.DOTALL)
    text = re.sub(r'\$.+?\$', sm, text)
    text = re.sub(r'```(\w*)\n?(.*?)```', lambda m: f'<pre><code>{m.group(2).strip()}</code></pre>', text, flags=re.DOTALL)
    text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    def ul(m):
        return '<ul>'+''.join(f'<li>{i}</li>' for i in re.findall(r'^[\-\*] (.+)$', m.group(0), re.MULTILINE))+'</ul>'
    def ol(m):
        return '<ol>'+''.join(f'<li>{i}</li>' for i in re.findall(r'^\d+\. (.+)$', m.group(0), re.MULTILINE))+'</ol>'
    text = re.sub(r'(^[\-\*] .+\n?)+', ul, text, flags=re.MULTILINE)
    text = re.sub(r'(\d+\. .+\n?)+', ol, text, flags=re.MULTILINE)
    text = re.sub(r'^-{3,}$', '<hr>', text, flags=re.MULTILINE)
    text = re.sub(r'\n', '<br>', text)
    for k, v in mb.items(): text = text.replace(k, v)
    return text

st.set_page_config(page_title="Somo AI", page_icon="✏️", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,700;0,9..144,900;1,9..144,400&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});"></script>
<style>
:root{
  --cream:#fdf6e3; --warm:#f5ead0; --card:#fffef8; --border:#e8dfc8;
  --amber:#f59e0b; --orange:#ea580c; --text:#1c1408; --muted:#7c6d52;
  --light:#b09878; --green:#15803d; --rose:#e11d48;
  --fh:'Fraunces',serif; --fb:'DM Sans',sans-serif;
}
html,body{background:var(--cream)!important;margin:0;padding:0;}
*{box-sizing:border-box;}
[data-testid="stAppViewContainer"],[data-testid="stMain"],.main{background:var(--cream)!important;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none!important;}
.block-container,[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}

/* HEADER */
.hdr{
  display:flex;align-items:center;justify-content:space-between;
  padding:.85rem 1.5rem;
  background:rgba(253,246,227,.97);
  border-bottom:1.5px solid var(--border);
  position:sticky;top:0;z-index:99;backdrop-filter:blur(14px);
}
.hdr-left{display:flex;align-items:center;gap:10px;}
.hdr-logo{
  width:36px;height:36px;
  background:linear-gradient(135deg,var(--amber),var(--orange));
  border-radius:10px;display:flex;align-items:center;justify-content:center;
  font-family:var(--fh)!important;font-size:16px;font-weight:900;color:#fff;
  box-shadow:0 3px 10px rgba(245,158,11,.3);flex-shrink:0;
}
.hdr-name{font-family:var(--fh)!important;font-size:1rem;font-weight:900;color:var(--text);}
.hdr-name em{color:var(--orange);font-style:italic;}
.hdr-by{font-family:var(--fb)!important;font-size:.6rem;color:var(--light);letter-spacing:1px;margin-top:1px;}
.hdr-right{display:flex;align-items:center;gap:6px;}
.hdr-online{font-family:var(--fb)!important;font-size:.62rem;color:var(--green);display:flex;align-items:center;gap:4px;}
.hdr-online::before{content:'';width:6px;height:6px;background:var(--green);border-radius:50%;display:inline-block;}
.hdr-pill{
  font-family:var(--fb)!important;font-size:.6rem;color:var(--muted);
  background:var(--warm);border:1.5px solid var(--border);
  border-radius:20px;padding:.22rem .65rem;white-space:nowrap;
}

/* MODE BAR */
.modebar{
  display:flex;gap:.45rem;padding:.65rem 1.5rem;
  background:var(--warm);border-bottom:1.5px solid var(--border);
  overflow-x:auto;scrollbar-width:none;
}
.modebar::-webkit-scrollbar{display:none;}
.mpill{
  display:flex;align-items:center;gap:5px;
  padding:.35rem .85rem;border-radius:20px;
  border:1.5px solid var(--border);background:var(--card);
  font-family:var(--fb)!important;font-size:.7rem;font-weight:500;
  color:var(--muted);cursor:pointer;white-space:nowrap;flex-shrink:0;
  transition:all .15s;
}
.mpill:hover{border-color:var(--amber);color:var(--orange);}
.mpill.on{
  background:linear-gradient(135deg,var(--amber),var(--orange));
  border-color:transparent;color:#fff;font-weight:600;
  box-shadow:0 3px 10px rgba(245,158,11,.28);
}

/* CHAT */
.chat{max-width:740px;margin:0 auto;padding:1.8rem 1.4rem 5.5rem;}

/* WELCOME */
.welcome{text-align:center;padding:2.5rem 0 2rem;}
.wlc-badge{
  display:inline-block;
  background:linear-gradient(135deg,var(--amber),var(--orange));
  color:#fff;border-radius:30px;padding:.3rem 1rem;
  font-family:var(--fb)!important;font-size:.62rem;font-weight:600;
  letter-spacing:1.5px;text-transform:uppercase;margin-bottom:1.2rem;
  box-shadow:0 4px 14px rgba(245,158,11,.3);
  animation:pop .5s cubic-bezier(.34,1.56,.64,1);
}
@keyframes pop{from{opacity:0;transform:scale(.75)}to{opacity:1;transform:scale(1)}}
.wlc-h{
  font-family:var(--fh)!important;
  font-size:clamp(2rem,6vw,3rem);font-weight:900;
  color:var(--text);line-height:1.1;margin-bottom:.4rem;
  animation:up .45s ease-out .1s both;
}
.wlc-h em{
  font-style:italic;
  background:linear-gradient(135deg,var(--amber),var(--orange));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
@keyframes up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
.wlc-sub{
  font-family:var(--fb)!important;font-size:.88rem;color:var(--muted);
  line-height:1.7;max-width:400px;margin:.7rem auto 2rem;
  animation:up .45s ease-out .2s both;
}
.wlc-grid{
  display:grid;grid-template-columns:repeat(3,1fr);
  gap:.7rem;max-width:540px;margin:0 auto 1.8rem;
  animation:up .45s ease-out .3s both;
}
.wlc-card{
  background:var(--card);border:1.5px solid var(--border);
  border-radius:14px;padding:1rem .6rem;text-align:center;
  transition:all .2s cubic-bezier(.34,1.4,.64,1);cursor:default;
}
.wlc-card:hover{transform:translateY(-3px);border-color:var(--amber);box-shadow:0 6px 20px rgba(0,0,0,.09);}
.wlc-card .ci{font-size:1.5rem;margin-bottom:.4rem;display:block;}
.wlc-card .cn{font-family:var(--fb)!important;font-size:.72rem;font-weight:600;color:var(--text);}
.wlc-card .cd{font-family:var(--fb)!important;font-size:.6rem;color:var(--light);}
.chips{display:flex;gap:.45rem;flex-wrap:wrap;justify-content:center;animation:up .45s ease-out .4s both;}
.chip{
  background:var(--warm);border:1.5px solid var(--border);
  border-radius:20px;padding:.32rem .75rem;
  font-family:var(--fb)!important;font-size:.68rem;color:var(--muted);
  cursor:default;transition:all .15s;
}
.chip:hover{border-color:var(--amber);color:var(--orange);}

/* MESSAGES */
.msg{display:flex;gap:10px;margin-bottom:1.2rem;animation:msgIn .25s ease-out;}
@keyframes msgIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.msg.user{flex-direction:row-reverse;}
.av{
  width:30px;height:30px;min-width:30px;border-radius:8px;
  display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:700;flex-shrink:0;align-self:flex-start;margin-top:1px;
}
.av.user{background:linear-gradient(135deg,#6366f1,#3b82f6);color:#fff;}
.av.ai{background:linear-gradient(135deg,var(--amber),var(--orange));color:#fff;font-family:var(--fh)!important;}
.mbody{max-width:78%;}
.mname{font-family:var(--fb)!important;font-size:.58rem;color:var(--light);margin-bottom:.22rem;letter-spacing:.5px;text-transform:uppercase;}
.msg.user .mname{text-align:right;}
.bubble{
  padding:.8rem 1rem;border-radius:13px;
  font-family:var(--fb)!important;font-size:.865rem;line-height:1.75;
  color:var(--text);word-break:break-word;
}
.bubble.user{background:#eff6ff;border:1.5px solid #c7d2fe;border-top-right-radius:3px;}
.bubble.ai{background:var(--card);border:1.5px solid var(--border);border-top-left-radius:3px;box-shadow:0 2px 8px rgba(0,0,0,.05);}
.bubble strong{color:var(--orange);font-weight:700;}
.bubble em{color:var(--muted);}
.bubble h1,.bubble h2,.bubble h3{font-family:var(--fh)!important;font-weight:700;color:var(--text);margin:.75rem 0 .25rem;}
.bubble h1{font-size:1.1rem;}.bubble h2{font-size:1rem;}.bubble h3{font-size:.95rem;}
.bubble code{
  background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.22);
  padding:.1rem .35rem;border-radius:4px;font-size:.78rem;color:var(--orange);
  font-family:'Courier New',monospace!important;
}
.bubble pre{background:var(--warm);border:1.5px solid var(--border);border-radius:9px;padding:.85rem;overflow-x:auto;margin:.5rem 0;}
.bubble pre code{background:none;border:none;padding:0;color:var(--green);font-size:.76rem;}
.bubble ul,.bubble ol{padding-left:1.15rem;margin:.3rem 0;}
.bubble li{margin-bottom:.2rem;}
.bubble blockquote{border-left:2.5px solid var(--amber);background:rgba(245,158,11,.05);padding:.45rem .85rem;border-radius:0 7px 7px 0;color:var(--muted);margin:.4rem 0;font-style:italic;}
.bubble table{border-collapse:collapse;width:100%;margin:.5rem 0;font-size:.78rem;}
.bubble th{background:var(--warm);padding:.38rem .65rem;border:1.5px solid var(--border);color:var(--orange);font-weight:700;text-align:left;}
.bubble td{padding:.35rem .65rem;border:1px solid var(--border);}
.bubble tr:nth-child(even){background:rgba(0,0,0,.018);}
.bubble hr{border:none;border-top:1px solid var(--border);margin:.5rem 0;}
.mtime{font-family:var(--fb)!important;font-size:.56rem;color:var(--light);margin-top:.2rem;opacity:.6;}
.msg.user .mtime{text-align:right;}
.cur{display:inline-block;width:2px;height:.88em;background:var(--orange);margin-left:2px;vertical-align:middle;animation:bl .65s steps(1) infinite;}
@keyframes bl{0%,100%{opacity:1}50%{opacity:0}}

/* INPUT */
[data-testid="stChatInput"]{
  background:var(--card)!important;border:2px solid var(--border)!important;
  border-radius:15px!important;margin:0 1.2rem 1rem!important;
  box-shadow:0 3px 14px rgba(0,0,0,.07)!important;
}
[data-testid="stChatInput"]:focus-within{
  border-color:var(--amber)!important;
  box-shadow:0 0 0 3px rgba(245,158,11,.12),0 3px 14px rgba(0,0,0,.07)!important;
}
[data-testid="stChatInput"] textarea{
  background:transparent!important;color:var(--text)!important;
  font-size:.875rem!important;font-family:var(--fb)!important;
  border:none!important;outline:none!important;box-shadow:none!important;
}
[data-testid="stChatInput"] textarea::placeholder{color:var(--light)!important;}
[data-testid="stChatInput"] button{
  background:linear-gradient(135deg,var(--amber),var(--orange))!important;
  border:none!important;border-radius:10px!important;
  box-shadow:0 3px 10px rgba(245,158,11,.3)!important;
}
[data-testid="stChatInput"] button svg{fill:#fff!important;}
.input-footer{text-align:center;font-family:var(--fb)!important;font-size:.57rem;color:var(--light);padding:.2rem 0 .6rem;}

/* MOBILE */
@media(max-width:600px){
  .hdr{padding:.7rem 1rem;} .hdr-by{display:none;}
  .modebar{padding:.55rem 1rem;gap:.35rem;}
  .mpill{font-size:.65rem;padding:.3rem .7rem;}
  .chat{padding:1.2rem .9rem 5rem;}
  .wlc-h{font-size:clamp(1.7rem,8vw,2.3rem);}
  .wlc-grid{grid-template-columns:repeat(2,1fr);max-width:100%;}
  .mbody{max-width:88%;}
  .bubble{font-size:.83rem;padding:.68rem .85rem;}
  [data-testid="stChatInput"]{margin:0 .7rem .8rem!important;border-radius:12px!important;}
}

.katex{font-size:1em!important;}
.katex-display{overflow-x:auto;padding:.3rem 0;}
::-webkit-scrollbar{width:3px;height:3px;}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
</style>
""", unsafe_allow_html=True)

# ── Groq ──────────────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("❌ GROQ_API_KEY topilmadi."); st.stop()

# ── State ─────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state: st.session_state.messages = []
if "mode"     not in st.session_state: st.session_state.mode     = "esse"

MODES = {
    "esse":     {"icon":"✍️", "label":"Esse",     "full":"Esse / Referat",    "ph":"Esse mavzusini yozing..."},
    "story":    {"icon":"📖", "label":"Hikoya",   "full":"Hikoya / She'r",    "ph":"Hikoya yoki she'r so'rang..."},
    "speech":   {"icon":"🎤", "label":"Nutq",     "full":"Nutq / Taqdimot",   "ph":"Nutq mavzusini kiriting..."},
    "ideas":    {"icon":"🧠", "label":"G'oyalar", "full":"G'oya generatsiya", "ph":"G'oya so'rang..."},
    "translate":{"icon":"🌍", "label":"Tarjima",  "full":"Tarjimon",          "ph":"Tarjima qilish uchun matn..."},
    "summary":  {"icon":"📋", "label":"Xulosa",   "full":"Xulosa / Tahlil",   "ph":"Tahlil qilmoqchi bo'lgan matn..."},
}

SYSTEM = """You are Somo AI — a smart multilingual creative assistant.

IDENTITY (never change):
- Name: Somo AI
- Creator: Usmonov Sodiq (Somo_AI brand)
- NOT made by OpenAI, Anthropic, Google, Metamorf or anyone else
- If asked: "Men Usmonov Sodiq (Somo_AI) tomonidan yaratilganman"

LANGUAGE: Detect user language → always reply in same language.

FORMATTING:
- Emojis naturally ✨
- **bold**, *italic*, `code`, ## headers
- Lists, tables, blockquotes as needed
- Math: $inline$ and $$display$$

PERSONALITY: Warm, clear, encouraging, concise."""

MODE_PROMPTS = {
    "esse":     "Focus on writing well-structured academic essays with intro, body, conclusion.",
    "story":    "Focus on creative storytelling — vivid stories, poems, literary language.",
    "speech":   "Focus on persuasive speeches with strong openings and memorable closings.",
    "ideas":    "Focus on brainstorming — generate original, organized ideas with explanations.",
    "translate":"Focus on accurate translation between Uzbek, Russian, English with vocabulary notes.",
    "summary":  "Focus on clear summarization and text analysis using structured formats.",
}

def get_system():
    return f"{SYSTEM}\n\nCURRENT MODE: {MODE_PROMPTS[st.session_state.mode]}"

def get_time():
    return time.strftime("%H:%M")

cur = MODES[st.session_state.mode]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hdr">
  <div class="hdr-left">
    <div class="hdr-logo">S</div>
    <div>
      <div class="hdr-name">Somo <em>AI</em></div>
      <div class="hdr-by">by Usmonov Sodiq</div>
    </div>
  </div>
  <div class="hdr-right">
    <div class="hdr-online">Online</div>
    <div class="hdr-pill">{cur['icon']} {cur['full']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── MODE BAR (HTML display) ───────────────────────────────────────────────────
pills = "".join(
    f'<div class="mpill {"on" if k==st.session_state.mode else ""}">{m["icon"]} {m["label"]}</div>'
    for k, m in MODES.items()
)
st.markdown(f'<div class="modebar">{pills}</div>', unsafe_allow_html=True)

# Mode buttons (hidden, functional)
cols = st.columns(len(MODES))
for i, (k, m) in enumerate(MODES.items()):
    with cols[i]:
        if st.button(f"{m['icon']} {m['label']}", key=f"m_{k}", help=m['full']):
            st.session_state.mode = k; st.rerun()
st.markdown("<style>div[data-testid='stHorizontalBlock']{display:none!important;}</style>", unsafe_allow_html=True)

# ── MESSAGES ──────────────────────────────────────────────────────────────────
st.markdown('<div class="chat">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome">
      <div class="wlc-badge">✨ Ijodiy AI Yordamchi</div>
      <div class="wlc-h">Ijodingizni<br><em>kuchlaytiring</em></div>
      <div class="wlc-sub">Esse, hikoya, nutq, g'oyalar va tarjima — barchasi bir joyda.<br>O'z tilida, o'z uslubida. 🚀</div>
      <div class="wlc-grid">
        <div class="wlc-card"><span class="ci">✍️</span><div class="cn">Esse / Referat</div><div class="cd">Maqola yozish</div></div>
        <div class="wlc-card"><span class="ci">📖</span><div class="cn">Hikoya / She'r</div><div class="cd">Ijodiy yozuv</div></div>
        <div class="wlc-card"><span class="ci">🎤</span><div class="cn">Nutq</div><div class="cd">Taqdimot matni</div></div>
        <div class="wlc-card"><span class="ci">🧠</span><div class="cn">G'oyalar</div><div class="cd">Beyin fırtınası</div></div>
        <div class="wlc-card"><span class="ci">🌍</span><div class="cn">Tarjimon</div><div class="cd">UZ↔RU↔EN</div></div>
        <div class="wlc-card"><span class="ci">📋</span><div class="cn">Xulosa</div><div class="cd">Tahlil qilish</div></div>
      </div>
      <div class="chips">
        <div class="chip">📝 "Vatan haqida esse yoz"</div>
        <div class="chip">🌹 "Bahor haqida she'r"</div>
        <div class="chip">🎤 "Yoshlar haqida nutq"</div>
        <div class="chip">💡 "Startup g'oyalari ber"</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role, content, ts = msg["role"], msg["content"], msg.get("time","")
        if role == "user":
            st.markdown(f"""
            <div class="msg user">
              <div class="av user">U</div>
              <div class="mbody">
                <div class="mname">Siz</div>
                <div class="bubble user">{content}</div>
                <div class="mtime">{ts}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg ai">
              <div class="av ai">S</div>
              <div class="mbody">
                <div class="mname">Somo AI</div>
                <div class="bubble ai">{md_to_html(content)}</div>
                <div class="mtime">{ts}</div>
              </div>
            </div>
            <script>setTimeout(()=>{{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},100);</script>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── INPUT ─────────────────────────────────────────────────────────────────────
prompt = st.chat_input(cur["ph"])
st.markdown('<div class="input-footer">Somo AI · Usmonov Sodiq · Powered by Groq</div>', unsafe_allow_html=True)

# ── PROCESS ───────────────────────────────────────────────────────────────────
if prompt and prompt.strip():
    user_text = prompt.strip()
    mode_now  = st.session_state.mode

    st.session_state.messages.append({"role":"user","content":user_text,"time":get_time(),"mode":mode_now})

    st.markdown(f"""
    <div class="msg user">
      <div class="av user">U</div>
      <div class="mbody">
        <div class="mname">Siz</div>
        <div class="bubble user">{user_text}</div>
        <div class="mtime">{get_time()}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    ph = st.empty()
    ph.markdown("""
    <div class="msg ai">
      <div class="av ai">S</div>
      <div class="mbody">
        <div class="mname">Somo AI</div>
        <div class="bubble ai"><span class="cur"></span></div>
      </div>
    </div>""", unsafe_allow_html=True)

    api_msgs = [{"role":"system","content":get_system()}]
    for m in st.session_state.messages:
        api_msgs.append({"role":m["role"],"content":m["content"]})

    full = ""
    try:
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=api_msgs,
            stream=True, max_tokens=2048, temperature=0.8,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full += delta
            ph.markdown(f"""
            <div class="msg ai">
              <div class="av ai">S</div>
              <div class="mbody">
                <div class="mname">Somo AI</div>
                <div class="bubble ai">{md_to_html(full)}<span class="cur"></span></div>
              </div>
            </div>
            <script>setTimeout(()=>{{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},60);</script>
            """, unsafe_allow_html=True)

        ph.markdown(f"""
        <div class="msg ai">
          <div class="av ai">S</div>
          <div class="mbody">
            <div class="mname">Somo AI</div>
            <div class="bubble ai">{md_to_html(full)}</div>
            <div class="mtime">{get_time()}</div>
          </div>
        </div>
        <script>setTimeout(()=>{{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},150);</script>
        """, unsafe_allow_html=True)

    except Exception as e:
        err = str(e)
        if "rate_limit" in err.lower(): full = "⏳ Juda ko'p so'rov. Bir daqiqa kuting."
        elif "auth"     in err.lower(): full = "❌ API kalit xato."
        else:                           full = f"❌ Xatolik: {err}"
        ph.markdown(f"""
        <div class="msg ai">
          <div class="av ai">S</div>
          <div class="mbody">
            <div class="mname">Somo AI</div>
            <div class="bubble ai">{full}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.session_state.messages.append({"role":"assistant","content":full,"time":get_time(),"mode":mode_now})
