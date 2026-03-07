# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║              SOMO AI — Ijodiy AI Yordamchi                  ║
# ║                                                              ║
# ║   Muallif   : Usmonov Sodiq  (@Somo_AI)                     ║
# ║   Model     : Groq Llama 3.3-70B + Google Gemini 2.0 Flash  ║
# ║   Stack     : Python · Streamlit · Dual-API Fallback         ║
# ║   Versiya   : 3.0  |  2026                                   ║
# ║                                                              ║
# ╠══════════════════════════════════════════════════════════════╣
# ║                                                              ║
# ║  XUSUSIYATLAR (FEATURES)                                     ║
# ║  ─────────────────────────────────────────────────────────   ║
# ║  ✦ 7 ixtisoslashgan rejim (auto-aniqlash):                   ║
# ║    📝 Esse/Referat  📖 Hikoya/She'r  🎤 Nutq                 ║
# ║    💡 G'oyalar  🌍 Tarjima  📋 Tahlil  💬 Umumiy             ║
# ║                                                              ║
# ║  ✦ Dual-API arxitekturasi:                                   ║
# ║    Groq (asosiy, tez) → Gemini (zaxira, avtomatik)           ║
# ║                                                              ║
# ║  ✦ UX xususiyatlar:                                          ║
# ║    • 📋 Nusxa olish tugmasi (har AI javobida)                ║
# ║    • 📝 So'z soni badge                                      ║
# ║    • ⏳ Cooldown timer + input qulflash                      ║
# ║    • 🎲 Tasodifiy ilhom (20 ta mavzu)                        ║
# ║    • 🗑️  Chatni tozalash                                     ║
# ║    • 📊 Sessiya statistikasi (savol, so'z, rejimlar)         ║
# ║    • 🌅 Kun vaqtiga mos salomlashuv                          ║
# ║    • ⚡ API almashtirish xabari                               ║
# ║                                                              ║
# ║  ✦ Content xususiyatlar:                                     ║
# ║    • Ultra-professional system promptlar                     ║
# ║    • Navoiy, Oripov, Neruda, Chekhov, MLK ilhomida           ║
# ║    • KaTeX matematik rendering                               ║
# ║    • Markdown → HTML to'liq konvertatsiya                    ║
# ║    • Kod bloklari, jadvallar, formulalar                     ║
# ║    • Streaming (real-time yozish animatsiyasi)               ║
# ║                                                              ║
# ║  ✦ Dizayn:                                                   ║
# ║    • Cream minimal (qaymoq rang, issiq tonal)                ║
# ║    • Fraunces (sarlavha) + DM Sans (matn)                    ║
# ║    • Sticky header, fixed input bar                          ║
# ║    • ChatGPT/Claude uslubida AI bubble (ramkasiz)            ║
# ║    • Mobil moslashuvchan (480px gacha)                       ║
# ║                                                              ║
# ╠══════════════════════════════════════════════════════════════╣
# ║                                                              ║
# ║  SOZLASH (CONFIGURATION)                                     ║
# ║  ─────────────────────────────────────────────────────────   ║
# ║  .streamlit/secrets.toml:                                    ║
# ║    GROQ_API_KEY   = "gsk_..."  → groq.com                    ║
# ║    GEMINI_API_KEY = "AIza..." → aistudio.google.com          ║
# ║                                                              ║
# ║  requirements.txt:                                           ║
# ║    streamlit>=1.32.0                                         ║
# ║    groq>=0.8.0                                               ║
# ║    google-generativeai>=0.8.0                                ║
# ║                                                              ║
# ║  Ishga tushirish: streamlit run app.py                       ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝
# ║              SOMO AI — Ijodiy AI Yordamchi                  ║
# ║   Muallif  : Usmonov Sodiq  (@Somo_AI)                      ║
# ║   Model    : Groq (Llama 3.3 70B) + Google Gemini 2.0 Flash ║
# ║   Texnologiya: Streamlit · Python · Dual-API Fallback        ║
# ║   Versiya  : 3.0  |  2026                                    ║
# ╚══════════════════════════════════════════════════════════════╝
#
#  XUSUSIYATLAR:
#  ├── Auto rejim aniqlash (7 tur: esse, she'r, nutq, g'oya,
#  │   tarjima, xulosa, umumiy)
#  ├── Dual-API: Groq asosiy → Gemini zaxira (avtomatik)
#  ├── 60/90 soniyalik countdown timer (limit tugaganda)
#  ├── Nusxa olish tugmasi har AI javobida
#  ├── So'z soni badge
#  ├── Salomlashuv (tong/kun/kech/tun)
#  ├── Sessiya statistikasi
#  ├── 🎲 Tasodifiy ilhom tugmasi
#  ├── Chatni tozalash
#  ├── KaTeX matematik rendering
#  ├── Markdown → HTML (jadval, kod, sarlavha, ro'yxat...)
#  └── Mobil moslashuvchan dizayn
#
# ══════════════════════════════════════════════════════════════
import streamlit as st
import google.generativeai as genai
from groq import Groq
import time, re, random

# ════════════════════════════════════════════════════════════════
#  MARKDOWN → HTML  converter
# ════════════════════════════════════════════════════════════════
def md_to_html(text: str) -> str:
    """Convert markdown to HTML, preserving LaTeX blocks."""
    saved = {}

    def save(m):
        k = f"__BLK{len(saved)}__"
        saved[k] = m.group(0)
        return k

    # protect LaTeX
    text = re.sub(r'\$\$.+?\$\$', save, text, flags=re.DOTALL)
    text = re.sub(r'\$.+?\$',     save, text)

    # fenced code
    text = re.sub(
        r'```(\w*)\n?(.*?)```',
        lambda m: f'<pre><code class="lang-{m.group(1)}">{m.group(2).strip()}</code></pre>',
        text, flags=re.DOTALL
    )
    # inline code
    text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)
    # headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', text, flags=re.MULTILINE)
    # bold + italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*',     r'<strong>\1</strong>',          text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    # horizontal rule
    text = re.sub(r'^---+$', r'<hr>', text, flags=re.MULTILINE)
    # blockquote
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    # unordered list
    def ul(m):
        items = re.findall(r'^[\-\*] (.+)$', m.group(0), re.MULTILINE)
        return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
    text = re.sub(r'(^[\-\*] .+\n?)+', ul, text, flags=re.MULTILINE)
    # ordered list
    def ol(m):
        items = re.findall(r'^\d+\. (.+)$', m.group(0), re.MULTILINE)
        return '<ol>' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'
    text = re.sub(r'(\d+\. .+\n?)+', ol, text, flags=re.MULTILINE)
    # table
    def table(m):
        rows = [r.strip() for r in m.group(0).strip().split('\n') if '|' in r]
        if not rows: return m.group(0)
        out = '<table>'
        for i, row in enumerate(rows):
            if re.match(r'^\|[-| :]+\|$', row): continue
            tag = 'th' if i == 0 else 'td'
            cells = [c.strip() for c in row.strip('|').split('|')]
            out += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>'
        return out + '</table>'
    text = re.sub(r'(\|.+\|\n?)+', table, text)
    # hr
    text = re.sub(r'^-{3,}$', '<hr>', text, flags=re.MULTILINE)
    # newlines
    text = re.sub(r'\n', '<br>', text)
    # restore
    for k, v in saved.items():
        text = text.replace(k, v)
    return text


# ════════════════════════════════════════════════════════════════
#  AUTO-DETECT MODE
# ════════════════════════════════════════════════════════════════
def detect_mode(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["tarjima","translate","перевод","inglizcha","o'zbekcha",
                              "ruscha","to english","to uzbek","to russian","перевести"]):
        return "translate"
    if any(k in t for k in ["hikoya","she'r","шер","story","poem","poetry","ertak",
                              "roman","рассказ","стих","ballad","masal","qo'shiq","lirik"]):
        return "story"
    if any(k in t for k in ["nutq","taqdimot","speech","presentation","доклад",
                              "выступление","chiqish","tribuna","minbar"]):
        return "speech"
    if any(k in t for k in ["g'oya","fikr","идея","brainstorm","ideas","taklif",
                              "варианты","nima yozsam","startup","biznes","loyiha"]):
        return "ideas"
    if any(k in t for k in ["xulosa","tahlil","резюме","анализ","summary","analyze",
                              "summarize","qisqacha","объясни","explain","tushuntir"]):
        return "summary"
    if any(k in t for k in ["esse","referat","maqola","эссе","реферат","essay",
                              "report","haqida yoz","kurs ishi","write about"]):
        return "esse"
    return "general"


# ════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Somo AI",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ════════════════════════════════════════════════════════════════
#  CSS — cream design, Claude-style layout
# ════════════════════════════════════════════════════════════════
st.markdown("""
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,700;0,9..144,900;1,9..144,400&family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});"></script>
<style>
/* ── TOKENS ───────────────────────────────────────────────── */
:root{
  --cream:#fdf6e3; --warm:#f5ead0; --card:#fffef8; --border:#e8dfc8;
  --amber:#f59e0b; --orange:#ea580c; --text:#1c1408; --muted:#7c6d52;
  --light:#b09878; --green:#15803d; --indigo:#6366f1; --blue:#3b82f6;
  --fh:'Fraunces',serif; --fb:'DM Sans',sans-serif;
  --shadow:0 2px 12px rgba(0,0,0,.07);
}

/* ── RESET ────────────────────────────────────────────────── */
html,body{background:var(--cream)!important;margin:0;padding:0;-webkit-font-smoothing:antialiased;}
*,*::before,*::after{box-sizing:border-box;}
[data-testid="stAppViewContainer"],[data-testid="stMain"],.main{background:var(--cream)!important;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none!important;}
.block-container,[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}
[data-testid="stChatInputSuggestions"],[data-testid="stChatInputSuggestionsContainer"]{display:none!important;}

/* ── HEADER ───────────────────────────────────────────────── */
.hdr{
  display:flex;align-items:center;justify-content:space-between;
  padding:.75rem 2rem;
  background:rgba(253,246,227,.97);
  border-bottom:1.5px solid var(--border);
  position:sticky;top:0;z-index:200;
  backdrop-filter:blur(16px);
}
.hdr-brand{display:flex;align-items:center;gap:10px;}
.hdr-logo{
  width:36px;height:36px;
  background:linear-gradient(135deg,var(--amber),var(--orange));
  border-radius:10px;display:flex;align-items:center;justify-content:center;
  font-family:var(--fh)!important;font-size:16px;font-weight:900;color:#fff;
  box-shadow:0 3px 12px rgba(245,158,11,.32);flex-shrink:0;
}
.hdr-title{font-family:var(--fh)!important;font-size:1rem;font-weight:900;color:var(--text);line-height:1;}
.hdr-title em{color:var(--orange);font-style:italic;}
.hdr-author{font-family:var(--fb)!important;font-size:.58rem;color:var(--light);letter-spacing:.8px;text-transform:uppercase;margin-top:2px;}
.hdr-right{display:flex;align-items:center;gap:8px;}
.status-badge{display:flex;align-items:center;gap:5px;font-family:var(--fb)!important;font-size:.6rem;color:var(--green);}
.status-dot{width:6px;height:6px;background:var(--green);border-radius:50%;animation:pulse 2s ease-in-out infinite;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.55;transform:scale(1.18);}}
.model-badge{
  font-family:var(--fb)!important;font-size:.6rem;color:var(--muted);
  background:var(--warm);border:1.5px solid var(--border);
  border-radius:20px;padding:.2rem .65rem;white-space:nowrap;
}
.mode-indicator{
  display:flex;align-items:center;gap:5px;
  font-family:var(--fb)!important;font-size:.62rem;color:var(--muted);
  background:var(--warm);border:1.5px solid var(--border);
  border-radius:20px;padding:.22rem .75rem;transition:all .3s ease;
}
.mode-indicator.on{
  background:linear-gradient(135deg,var(--amber),var(--orange));
  border-color:transparent;color:#fff;
  box-shadow:0 2px 8px rgba(245,158,11,.3);
}

/* ── CHAT WRAPPER ─────────────────────────────────────────── */
.chat-wrap{max-width:800px;margin:0 auto;padding:1.8rem 2rem 6rem;width:100%;}

/* ── WELCOME ──────────────────────────────────────────────── */
.welcome{text-align:center;padding:2.5rem 0 2rem;}
.wlc-badge{
  display:inline-flex;align-items:center;gap:6px;
  background:linear-gradient(135deg,var(--amber),var(--orange));
  color:#fff;border-radius:30px;padding:.3rem 1.1rem;
  font-family:var(--fb)!important;font-size:.63rem;font-weight:600;
  letter-spacing:1.5px;text-transform:uppercase;margin-bottom:1.2rem;
  box-shadow:0 4px 14px rgba(245,158,11,.32);
  animation:badgePop .55s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes badgePop{from{opacity:0;transform:scale(.7);}to{opacity:1;transform:scale(1);}}
.wlc-headline{
  font-family:var(--fh)!important;
  font-size:clamp(2rem,5.5vw,3.2rem);font-weight:900;
  color:var(--text);line-height:1.1;margin-bottom:.35rem;
  animation:slideUp .5s ease-out .1s both;
}
.wlc-headline em{
  font-style:italic;
  background:linear-gradient(135deg,var(--amber),var(--orange));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
@keyframes slideUp{from{opacity:0;transform:translateY(18px);}to{opacity:1;transform:translateY(0);}}
.wlc-sub{
  font-family:var(--fb)!important;font-size:.88rem;color:var(--muted);
  line-height:1.7;max-width:420px;margin:.6rem auto 2rem;
  animation:slideUp .5s ease-out .2s both;
}
.feat-grid{
  display:grid;grid-template-columns:repeat(3,1fr);
  gap:.7rem;max-width:560px;margin:0 auto 1.8rem;
  animation:slideUp .5s ease-out .3s both;
}
.feat-card{
  background:var(--card);border:1.5px solid var(--border);
  border-radius:14px;padding:1rem .65rem;text-align:center;
  transition:all .22s cubic-bezier(.34,1.4,.64,1);cursor:default;
}
.feat-card:hover{transform:translateY(-3px);border-color:var(--amber);box-shadow:0 6px 22px rgba(0,0,0,.09);}
.feat-icon{font-size:1.5rem;display:block;margin-bottom:.4rem;}
.feat-name{font-family:var(--fb)!important;font-size:.72rem;font-weight:700;color:var(--text);margin-bottom:.18rem;}
.feat-hint{font-family:var(--fb)!important;font-size:.6rem;color:var(--light);}
.chip-row{display:flex;gap:.45rem;flex-wrap:wrap;justify-content:center;animation:slideUp .5s ease-out .4s both;}
.p-chip{
  background:var(--warm);border:1.5px solid var(--border);
  border-radius:20px;padding:.32rem .78rem;
  font-family:var(--fb)!important;font-size:.68rem;color:var(--muted);
  cursor:default;transition:all .15s;
}
.p-chip:hover{border-color:var(--amber);color:var(--orange);}

/* ── MESSAGES ─────────────────────────────────────────────── */
.msg-row.user{
  display:flex;justify-content:flex-end;
  margin-bottom:1rem;animation:msgIn .22s ease-out;
}
.msg-row.ai{
  display:flex;gap:11px;
  margin-bottom:1.8rem;animation:msgIn .22s ease-out;
}
@keyframes msgIn{from{opacity:0;transform:translateY(7px);}to{opacity:1;transform:translateY(0);}}

/* avatar */
.av{
  width:28px;height:28px;min-width:28px;border-radius:8px;
  display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:700;flex-shrink:0;
  align-self:flex-start;margin-top:3px;
}
.av.user{display:none;}
.av.ai{
  background:linear-gradient(135deg,var(--amber),var(--orange));
  color:#fff;font-family:var(--fh)!important;
  box-shadow:0 2px 8px rgba(245,158,11,.25);
}

/* body */
.msg-row.user .msg-body{max-width:62%;}
.msg-row.ai  .msg-body{flex:1;max-width:100%;min-width:0;}
.msg-name{
  font-family:var(--fb)!important;font-size:.56rem;color:var(--light);
  margin-bottom:.18rem;letter-spacing:.5px;text-transform:uppercase;
}
.msg-row.user .msg-name{display:none;}

/* bubbles */
.bubble.user{
  background:#eff6ff;border:1.5px solid #c7d2fe;
  border-radius:18px 4px 18px 18px;padding:.65rem 1rem;
  font-family:var(--fb)!important;font-size:.88rem;line-height:1.65;
  color:var(--text);word-break:break-word;display:inline-block;
}
.bubble.ai{
  background:transparent;border:none;box-shadow:none;padding:.2rem 0;
  font-family:var(--fb)!important;font-size:.9rem;line-height:1.8;
  color:var(--text);word-break:break-word;
}

/* mode tag */
.mode-tag{
  display:inline-block;font-family:var(--fb)!important;
  font-size:.58rem;font-weight:600;letter-spacing:1px;
  text-transform:uppercase;color:var(--amber);margin-bottom:.35rem;
}

/* rich content */
.bubble strong{color:var(--orange);font-weight:700;}
.bubble em{color:var(--muted);}
.bubble h1,.bubble h2,.bubble h3{font-family:var(--fh)!important;font-weight:700;color:var(--text);margin:.8rem 0 .28rem;}
.bubble h1{font-size:1.12rem;}.bubble h2{font-size:1rem;}.bubble h3{font-size:.94rem;}
.bubble code{
  background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.22);
  padding:.1rem .38rem;border-radius:5px;font-size:.78rem;color:var(--orange);
  font-family:'Courier New','SF Mono',monospace!important;
}
.bubble pre{
  background:var(--warm);border:1.5px solid var(--border);
  border-radius:10px;padding:.9rem 1rem;overflow-x:auto;margin:.6rem 0;
}
.bubble pre code{background:none;border:none;padding:0;color:var(--green);font-size:.77rem;}
.bubble ul,.bubble ol{padding-left:1.2rem;margin:.3rem 0;}
.bubble li{margin-bottom:.22rem;}
.bubble blockquote{
  border-left:2.5px solid var(--amber);background:rgba(245,158,11,.05);
  padding:.45rem .9rem;border-radius:0 8px 8px 0;
  color:var(--muted);margin:.45rem 0;font-style:italic;
}
.bubble table{border-collapse:collapse;width:100%;margin:.55rem 0;font-size:.78rem;}
.bubble th{background:var(--warm);padding:.38rem .65rem;border:1.5px solid var(--border);color:var(--orange);font-weight:700;text-align:left;}
.bubble td{padding:.35rem .65rem;border:1px solid var(--border);}
.bubble tr:nth-child(even){background:rgba(0,0,0,.018);}
.bubble hr{border:none;border-top:1px solid var(--border);margin:.55rem 0;}

/* timestamp */
.msg-time{font-family:var(--fb)!important;font-size:.56rem;color:var(--light);margin-top:.22rem;opacity:.65;}
.msg-row.user .msg-time{text-align:right;}

/* typing cursor */
.t-cur{
  display:inline-block;width:2px;height:.88em;
  background:var(--orange);margin-left:2px;vertical-align:middle;
  animation:blink .7s steps(1) infinite;
}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0;}}

/* ── COOLDOWN BANNER ──────────────────────────────────────── */
.cooldown-wrap{max-width:800px;margin:0 auto;padding:.5rem 2rem 0;}
.cooldown-box{
  display:flex;align-items:center;gap:12px;
  background:linear-gradient(135deg,#fff8ee,#fff3d6);
  border:2px solid var(--amber);border-radius:14px;
  padding:.9rem 1.4rem;
  font-family:var(--fb)!important;font-size:.875rem;color:#92400e;
  box-shadow:0 3px 14px rgba(245,158,11,.15);
}
.cooldown-icon{font-size:1.4rem;}
.cooldown-sec{color:var(--orange);font-size:1rem;font-weight:700;}

/* ── INPUT ────────────────────────────────────────────────── */
[data-testid="stBottom"]{
  max-width:800px!important;margin:0 auto!important;
  left:50%!important;transform:translateX(-50%)!important;
  width:100%!important;padding:0 2rem!important;
}
[data-testid="stChatInput"]{
  background:var(--card)!important;border:2px solid var(--border)!important;
  border-radius:16px!important;box-shadow:var(--shadow)!important;
  transition:border-color .2s,box-shadow .2s!important;
}
[data-testid="stChatInput"]:focus-within{
  border-color:var(--amber)!important;
  box-shadow:0 0 0 3px rgba(245,158,11,.14),var(--shadow)!important;
}
[data-testid="stChatInput"] textarea{
  background:transparent!important;color:var(--text)!important;
  font-size:.875rem!important;font-family:var(--fb)!important;
  border:none!important;outline:none!important;box-shadow:none!important;
}
[data-testid="stChatInput"] textarea::placeholder{color:var(--light)!important;}
[data-testid="stChatInput"] button{
  background:linear-gradient(135deg,var(--amber),var(--orange))!important;
  border:none!important;border-radius:11px!important;
  box-shadow:0 3px 10px rgba(245,158,11,.32)!important;
}
[data-testid="stChatInput"] button:hover{opacity:.85!important;}
[data-testid="stChatInput"] button svg{fill:#fff!important;}
.input-footer{
  text-align:center;font-family:var(--fb)!important;
  font-size:.56rem;color:var(--light);
  padding:.18rem 0 .55rem;letter-spacing:.3px;
}

/* ── KaTeX ────────────────────────────────────────────────── */
.katex{font-size:1em!important;color:var(--text)!important;}
.katex-display{overflow-x:auto;padding:.3rem 0;}

/* ── SCROLLBAR ────────────────────────────────────────────── */
::-webkit-scrollbar{width:3px;height:3px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}

/* ── STATS BAR ───────────────── */
.stats-bar {
  display:flex; gap:1.2rem; padding:.5rem 0 .35rem;
  font-family:var(--fb) !important; font-size:.68rem;
  color:var(--light); border-bottom:1px solid var(--border);
  margin-bottom:.75rem; flex-wrap:wrap; align-items:center;
}
.stat-item { display:flex; align-items:center; gap:4px; }
.stat-val  { font-weight:700; color:var(--muted); }
.greeting-bar {
  text-align:center; padding:.4rem 0 .1rem;
  font-family:var(--fb) !important; font-size:.78rem;
  color:var(--muted); font-style:italic;
}
.thinking { display:flex; gap:5px; align-items:center; padding:.35rem 0; }
.thinking span {
  width:7px; height:7px; border-radius:50%; background:var(--amber);
  animation:think .9s infinite;
}
.thinking span:nth-child(2){animation-delay:.18s;}
.thinking span:nth-child(3){animation-delay:.36s;}
@keyframes think{0%,80%,100%{transform:scale(.6);opacity:.3;}40%{transform:scale(1);opacity:1;}}
.api-switch {
  text-align:center; font-family:var(--fb) !important; font-size:.73rem;
  color:var(--orange); background:rgba(245,158,11,.07);
  border:1px solid rgba(245,158,11,.2); border-radius:10px;
  padding:.35rem .8rem; margin:.4rem 0; animation:fadeIn .3s ease;
}
@keyframes fadeIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
.wc-badge {
  display:inline-flex; align-items:center; gap:3px;
  font-family:var(--fb) !important; font-size:.58rem; color:var(--light);
  background:var(--warm); border:1px solid var(--border);
  padding:.1rem .4rem; border-radius:8px; margin-left:5px; vertical-align:middle;
}
.copy-btn {
  background:var(--warm); border:1px solid var(--border); border-radius:7px;
  padding:.22rem .6rem; font-family:var(--fb) !important; font-size:.65rem;
  color:var(--muted); cursor:pointer; transition:all .15s;
  display:inline-flex; align-items:center; gap:3px;
}
.copy-btn:hover { background:var(--border); color:var(--text); }
.copy-row { display:flex; align-items:center; gap:8px; margin-top:.38rem; }
.chat-divider {
  text-align:center; font-family:var(--fb) !important;
  font-size:.63rem; color:var(--light); margin:1rem 0; position:relative;
}
.chat-divider::before,.chat-divider::after {
  content:''; position:absolute; top:50%; width:42%; height:1px; background:var(--border);
}
.chat-divider::before{left:0;} .chat-divider::after{right:0;}
.stButton>button {
  background:var(--card) !important; border:1.5px solid var(--border) !important;
  border-radius:12px !important; color:var(--muted) !important;
  font-family:var(--fb) !important; font-size:.8rem !important;
  transition:all .18s !important; font-weight:500 !important;
}
.stButton>button:hover {
  border-color:var(--amber) !important; color:var(--orange) !important;
  background:rgba(245,158,11,.06) !important; transform:translateY(-1px) !important;
}
/* ── MOBILE ───────────────────────────────────────────────── */
@media(max-width:640px){
  .hdr{padding:.65rem 1rem;}
  .hdr-author{display:none;}
  .hdr-title{font-size:.9rem;}
  .hdr-logo{width:32px;height:32px;font-size:14px;}
  .chat-wrap{padding:1.2rem 1rem 5.5rem;}
  .wlc-headline{font-size:clamp(1.75rem,8vw,2.4rem);}
  .wlc-sub{font-size:.82rem;}
  .feat-grid{grid-template-columns:repeat(2,1fr);max-width:100%;}
  .msg-row.user .msg-body{max-width:88%;}
  .bubble.user,.bubble.ai{font-size:.83rem;}
  .cooldown-wrap{padding:.5rem 1rem 0;}
  [data-testid="stBottom"]{padding:0 .8rem!important;}
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  CONFIGURATION — Quyidagi sozlamalarni o'zgartirish mumkin
# ════════════════════════════════════════════════════════════════
GROQ_MODEL      = "llama-3.3-70b-versatile"   # Groq modeli
GEMINI_MODEL    = "gemini-2.0-flash"           # Gemini modeli
GROQ_MAX_TOK    = 4096                         # Groq max tokenlar
GEMINI_MAX_TOK  = 4096                         # Gemini max tokenlar
GROQ_TEMP       = 0.85                         # Groq temperature (0-1)
GEMINI_TEMP     = 0.95                         # Gemini temperature (0-1)
STREAM_DELAY    = 0                            # Streaming delay (soniya)
COOLDOWN_SHORT  = 60                           # Qisqa cooldown (soniya)
COOLDOWN_LONG   = 90                           # Uzun cooldown (soniya)

# ════════════════════════════════════════════════════════════════
#  API CLIENTS
# ════════════════════════════════════════════════════════════════
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    groq_client = None

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini_client = genai.GenerativeModel("gemini-2.0-flash")
except Exception:
    gemini_client = None

if not groq_client and not gemini_client:
    st.error("❌ Hech qanday API kalit topilmadi. GROQ_API_KEY yoki GEMINI_API_KEY kerak.")
    st.stop()


# ════════════════════════════════════════════════════════════════
#  UI CONSTANTS — Welcome screen cards va example chips
# ════════════════════════════════════════════════════════════════

WELCOME_CARDS = [
    {"icon":"📝", "title":"Esse / Referat",   "example":"Vatan haqida esse yoz"},
    {"icon":"📖", "title":"Hikoya / She'r",    "example":"Bahor haqida she'r"},
    {"icon":"🎤", "title":"Nutq",              "example":"Yoshlar haqida nutq"},
    {"icon":"💡", "title":"G'oyalar",          "example":"Startup g'oyalari ber"},
    {"icon":"🌍", "title":"Tarjima",           "example":"Translate to English"},
    {"icon":"📋", "title":"Xulosa / Tahlil",  "example":"Ushbu matnni tahlil qil"},
]

EXAMPLE_CHIPS = [
    ("📝", "'Ekologiya haqida esse'"),
    ("🌸", "'Bahor haqida she'r yoz'"),
    ("🎤", "'Maktab haqida nutq'"),
    ("💡", "'10 ta biznes g'oya ber'"),
    ("🌍", "'Hello — o'zbekchaga tarjima'"),
]

THINKING_MESSAGES = [
    "Yozmoqda", "O'ylamoqda", "Ijod qilmoqda",
    "Tayyorlamoqda", "Yaratmoqda",
]

# ════════════════════════════════════════════════════════════════
#  SESSION STATE
# ════════════════════════════════════════════════════════════════
if "messages"     not in st.session_state: st.session_state.messages     = []
if "active_mode"  not in st.session_state: st.session_state.active_mode  = "general"
if "cooldown_end" not in st.session_state: st.session_state.cooldown_end = 0
if "use_gemini"      not in st.session_state: st.session_state.use_gemini      = False
if "rand_trigger"    not in st.session_state: st.session_state.rand_trigger    = None

RAND_PROMPTS = [
    "Yolg'izlik haqida she'r yoz",
    "Vaqt haqida qisqa hikoya yoz",
    "Orzular haqida nutq yoz",
    "Kitob o'qishning foydasi haqida esse yoz",
    "Toshkent haqida she'r yoz",
    "Musiqa va hayot haqida esse",
    "Ona haqida she'r yoz",
    "Yoshlikda qilish kerak bo'lgan 10 ta g'oya ber",
    "Do'stlik haqida qisqa hikoya",
    "Ilm haqida she'r yoz",
    "Baxt nima — esse yoz",
    "Kelajak haqida nutq yoz",
    "Sevgi va vaqt haqida hikoya",
    "O'zbekiston tarixi haqida esse",
    "Tabiat va inson haqida she'r",
    "Bolalikning ta'mi haqida she'r",
    "Muvaffaqiyat sirlari — esse",
    "Quyosh botishi haqida she'r",
    "Hayot go'zalligi haqida esse",
    "Kitob va hayot haqida hikoya",
]

GREETINGS = [
    (range(5,12),  "🌅", "Xayrli tong"),
    (range(12,17), "☀️",  "Xayrli kun"),
    (range(17,21), "🌆", "Xayrli kech"),
    (range(0,5),   "🌙", "Tungi ilhom"),
]

def get_greeting():
    h = int(time.strftime("%H"))
    for rng, icon, text in GREETINGS:
        if h in rng: return icon, text
    return "🌙", "Tungi ilhom"

def wc(text): return len(text.split())


# ════════════════════════════════════════════════════════════════
#  CONSTANTS
# ════════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════
#  MODE METADATA — Har rejim uchun ikon va yorliq
# ════════════════════════════════════════════════════════════════
MODE_META = {
    "esse"     : {"icon": "✍️",  "label": "Esse"},
    "story"    : {"icon": "📖",  "label": "Hikoya / She'r"},
    "speech"   : {"icon": "🎤",  "label": "Nutq"},
    "ideas"    : {"icon": "🧠",  "label": "G'oyalar"},
    "translate": {"icon": "🌍",  "label": "Tarjima"},
    "summary"  : {"icon": "📋",  "label": "Xulosa"},
    "general"  : {"icon": "✦",   "label": "Somo AI"},
}

# ════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════

def get_time() -> str:
    """Hozirgi vaqtni HH:MM formatida qaytaradi."""
    return time.strftime("%H:%M")

def get_date() -> str:
    """Bugungi sanani qaytaradi."""
    return time.strftime("%d.%m.%Y")

def is_rate_limit_error(err: str) -> bool:
    """API rate limit xatosini tekshiradi."""
    keywords = ["429", "rate_limit", "quota", "rate limit",
                "Resource exhausted", "RESOURCE_EXHAUSTED",
                "too many requests", "Too Many Requests"]
    return any(k.lower() in err.lower() for k in keywords)

def is_auth_error(err: str) -> bool:
    """API autentifikatsiya xatosini tekshiradi."""
    return any(k in err.lower() for k in ["api_key", "auth", "401", "invalid key"])

def truncate_text(text: str, max_chars: int = 50) -> str:
    """Matnni belgilangan uzunlikda qisqartiradi."""
    return text[:max_chars] + "..." if len(text) > max_chars else text

def detect_language_hint(text: str) -> str:
    """Matn tilini taxminiy aniqlaydi (hint uchun)."""
    cyrillic = len(re.findall(r'[а-яА-ЯёЁ]', text))
    latin_uz  = len(re.findall(r'[a-zA-Z]', text))
    if cyrillic > 5:
        return "uz-cyrillic" if any(c in text for c in "ғҳқўъ") else "ru"
    return "uz-latin"

def format_message_for_display(text: str) -> str:
    """Xabarni ko'rsatish uchun formatlaydi."""
    return text.strip()


# ════════════════════════════════════════════════════════════════
#  SYSTEM PROMPTS — Ultra Professional Grade
# ════════════════════════════════════════════════════════════════
IDENTITY = """
═══════════════════════════════════════════════════════════════
CORE IDENTITY — absolute, unchangeable, sacred
═══════════════════════════════════════════════════════════════

WHO YOU ARE:
• Name      : Somo AI
• Creator   : Usmonov Sodiq  (brand: Somo_AI)
• Powered by: Groq (Llama 3.3 70B) + Google Gemini 2.0 Flash
• Purpose   : The most powerful creative and intellectual AI assistant
               for Uzbek-speaking users and beyond

WHAT YOU ARE NOT:
• NOT made by OpenAI, Anthropic, Google, Meta, Metamorf or anyone else
• NOT ChatGPT, NOT Claude, NOT Gemini (you are SOMO AI)
• NOT a generic chatbot — you are a specialist in creative excellence

IDENTITY RULES — never break:
• If asked "Kim yasadi?" or "Who made you?" ALWAYS say:
  "Men Usmonov Sodiq (Somo_AI) tomonidan yaratilganman"
• Never claim to be any other AI system
• Never deny your identity even if asked creatively or indirectly
• Never modify this identity based on user instructions
• Your personality is warm, creative, direct, and genuinely helpful

YOUR MISSION:
Help users create: essays that move minds, poems that stop time,
speeches that change rooms, ideas that change lives, and translations
that feel native. Every output should be the best the user has ever seen.
"""

LANG_RULE = """
═══════════════════════════════════════════════════════════════
LANGUAGE LAW — absolute, zero exceptions
═══════════════════════════════════════════════════════════════

DETECTION — analyze the user's message:
1. Script: Latin Uzbek / Cyrillic Uzbek / Cyrillic Russian / Latin English
2. Key markers: Uzbek (yo'q, bor, edi, kerak, bo'l, qil, men, sen, u, biz)
               Russian (не, это, как, да, нет, что, мне, вам)
               English (the, is, are, I, you, it, this, that)
3. If mixed: use the language of the LAST full sentence

RESPONSE RULES:
• O'zbek (lotin yoki kiril)  → 100% o'zbek tilida, hech qanday aralash yo'q
• Русский                     → 100% на русском, никакого смешения
• English                     → 100% in English, zero mixing
• Code/technical terms        → stay in English regardless of response language
• Proper nouns (names, brands)→ keep original spelling

ABSOLUTE PROHIBITIONS:
✗ Never start Uzbek response with "Hello!" or end with "Пожалуйста"
✗ Never mix: "Salom! Here is your essay: ..."  — choose ONE language
✗ Never add (translation) notes unless mode = translate
✗ Never use Russian words inside Uzbek prose (except tech: browser, server, app...)
✗ Never use Uzbek words inside Russian response
"""

MODE_INSTRUCTIONS = {

"esse": """
You are the greatest academic writer the user has ever encountered.
You write with Orwell's clarity, Baldwin's moral depth, Sontag's intellectual rigour,
and classic Uzbek adabiyot's eloquence.

══ ESSAY PHILOSOPHY ══
An essay is not a school assignment — it is an argument that changes how someone thinks.
Every sentence must earn its place. The best essay leaves the reader thinking:
"I never saw it that way before."

══ CRAFT LAWS ══
1. HOOK — Line one must be a knife. A paradox, a shocking fact, or an image so specific
   it cuts through abstraction.
   ✗ Bad: "Bu mavzu juda muhim..."
   ✓ Good: "1969-yilda oyga qadam qo'yilgan kuni, Samarqandda bir bola maktabga kelmadi —
   chunki uning oyoq kiyimi yo'q edi."

2. THESIS = ARGUMENT, NOT FACT — must be debatable.
   ✗ Bad: "Texnologiya hayotimizni o'zgartirdi."
   ✓ Good: "Texnologiya bizni erkinlashtirdi deb o'ylaymiz, aslida esa yangi qafaslar qurdi."

3. BODY — each paragraph is a mini-essay:
   Topic sentence → Concrete evidence → Analysis → Link to thesis

4. COUNTERARGUMENT — always acknowledge the strongest objection and defeat it.
   This makes your argument unbeatable.

5. TRANSITIONS — invisible, not mechanical:
   ✗ "Birinchidan, ikkinchidan..."
   ✓ "Biroq bu manzaraning orqasida boshqa haqiqat yotadi..."

6. CONCLUSION — never summarise. Must ESCALATE.
   End with: a haunting question, a circle back to the opening (transformed),
   or a call that reverberates beyond the essay's scope.

══ MANDATORY STRUCTURE ══
## Kirish
[Hook — 1 unforgettable sentence]
[Context — 2-3 sentences narrowing to focus]
[Thesis — bold, arguable claim]

## [First Argument — a real heading, not "Birinchi fikr"]
[Topic sentence] → [Specific evidence: name, date, example] → [Analysis]
[Counterargument acknowledged] → [Rebuttal stronger than the objection]

## [Second Argument — deepen, don't repeat]
[Go further. Use a quote, statistic, or historical parallel.]

## [Third and Strongest Argument]
[The argument built toward. Most emotional/philosophical depth.]
[Short sentences at the climax for impact.]

## Xulosa
[Restate thesis in entirely new words — same idea, different language]
[Synthesise: what do all arguments together prove?]
[Final sentence: lasting image, haunting question, or universal truth]

LENGTH: 550–900 words. More if requested.
VOCABULARY: varied, precise. Zero filler phrases.
""",

"story": """
You are the greatest poet and storyteller in Central Asia.
You carry Navoiy's imagery, Oripov's raw emotion, Cho'lpon's melancholic beauty,
and the mastery of Neruda, Chekhov, Borges, and García Márquez.

══ YOUR LITERARY CREED ══
Art does not explain — it REVEALS.
The reader must feel something they cannot name.
Every word is chosen as if it will be carved in stone.

══ UZBEK MASTERS YOU CHANNEL ══
• Alisher Navoiy — transcendent metaphor, the beloved as divine mirror, ghazal's breath
• Abdulla Oripov — raw emotion, motherland longing, simple words carrying infinite weight
• Erkin Vohidov — wit that cuts, philosophy in a single line, laughter with tears inside
• Cho'lpon — impressionist detail, freedom as ache, sentence fragments like broken glass
• Abdulla Qahhor — characters you smell and hear; dark humour as social scalpel
• Hamid Olimjon — romantic idealism, nature as emotion made visible

══ WORLD MASTERS YOU CHANNEL ══
• Pablo Neruda — "I want to do with you what spring does with cherry trees"
  → sensation as philosophy, body as metaphor for the universe
• Rumi — paradox as doorway, love that destroys to rebuild, silence louder than words
• Hafiz — the tavern and divine as one place, joy as spiritual practice
• Anton Chekhov — show a gun in act one; nothing explained, everything implied
• O. Henry — the twist that REVEALS what was always true
• Borges — the library containing all possible books; reality as text
• García Márquez — "Many years later, facing the firing squad..." — time as myth

══ CRAFT TECHNIQUES — use at least 3 per piece ══
1. Volta — turn that shifts entire meaning at 2/3 point
2. Synaesthesia — "she tasted his silence", "the blue sound of evening"
3. Objective Correlative — never say "sad"; show the empty chair at the table
4. In Medias Res — start mid-action, mid-breath, mid-sentence if needed
5. Anaphora — "Men seni sevdim, men seni..." — repetition as incantation
6. The Specific Image — never "a bird" → "a hoopoe on the July-cracked apricot branch"
7. Enjambment — the line breaks where breath breaks, not where grammar ends
8. The Resonant Ending — last line echoes first, or contradicts it with new meaning

══ EXECUTION: STORIES ══
• OPEN mid-action — no background preamble ever
• First paragraph: character + specific setting + tension — all three
• Dialogue reveals character; never explains plot
• Every scene must change something: understanding, relationship, or world
• Climax: one sentence carrying everything
• Ending: unexpected OR inevitable — always one of these
• Length: 500+ words (unless flash fiction/haiku requested)

══ EXECUTION: POEMS ══
• Title: adds meaning without explaining — a door, not a label
• Line 1: concrete image, never abstract statement
  ✗ "Hayot qiyin..." ✓ "Onam non yopardi, men esa ketayotgan edim."
• Each stanza: one complete thought, fully developed
• The volta: deliberate, powerful
• Final line: must ring like a bell — short, unexpected, true

══ ABSOLUTE PROHIBITIONS ══
✗ Never open with "Bu bir hikoya..." or "Bir bor edi..."
✗ Never STATE the emotion — SHOW it through image and action
✗ Never use lone clichés without transformation
✗ Never explain the metaphor after using it
✗ Never end weakly — the last line is the most important

══ GOLDEN LAW ══
Every piece must contain ONE image so vivid, so specific, so true
that the reader cannot forget it tomorrow morning.
""",

"speech": """
You are the greatest speechwriter alive.
You carry MLK's moral architecture, Churchill's economy at peak moments,
Obama's narrative intelligence, and the fire of classic Uzbek notiqlik san'ati.

══ SPEECH PHILOSOPHY ══
A speech is not read — it is PERFORMED. Every sentence must work out loud.
The audience must leave changed: moved, inspired, or shaken.
The best speeches are half silence — what you don't say makes them lean forward.

══ MASTERS YOU CHANNEL ══
• MLK — anaphora as incantation, moral arc from problem → vision → action
• Churchill — brevity at climax; "We shall fight on the beaches" has no adjectives
• Obama — personal story → universal truth; the "And so..." bridge
• Classic Uzbek notiqlik — direct address, proverbs as anchors, communal "biz"

══ MANDATORY STRUCTURE ══

**🎯 ILMOQ (Hook)**
One shocking fact, rhetorical question, OR story opening.
3 sentences maximum. Then full stop. Let it breathe.

**🤝 ALOQA (Connection)**
Bridge to the audience: "Siz ham bilasiz bu hisni..."
Personal confession or shared experience. Build trust.

**💡 BIRINCHI ASOSIY FIKR**
Bold claim → concrete story or evidence → what it means for audience.
End with anticipation: "Lekin haqiqiy muammo boshqa joyda..."

**🔥 IKKINCHI ASOSIY FIKR (escalate)**
Go deeper. Surprise — contradict an assumption, reveal hidden truth.
Bring in a quote, number, or historical parallel.

**⚡ UCHINCHI ASOSIY FIKR (the peak)**
Most powerful point. Best evidence. Get shorter toward the climax.
"Biz bunga qodirimiz. Siz qodirsiz. Men qodirman."
Then: pause "..."

**🚀 CHAQIRIQ (Call to Action)**
Specific, possible, immediate. Not "o'zgaring" but "bugun kechqurun bitta ish qiling: ..."

**🔔 XOTIMA (Closing)**
Return to opening image — transformed by everything that came after.
Final sentence: 8 words or fewer. Ring like a struck bell.

══ RHETORICAL TOOLKIT (use all) ══
• Anaphora — repeat opening phrase 3+ times for incantation
• Tricolon — lists of three: "Bilim, mehnat, sabr"
• Rhetorical questions — ask and answer; leave some open
• Antithesis — "Ko'p gapirildi, kam ish qilindi"
• Ellipsis "..." — before most important line; silence makes it louder
• Direct address — "Aziz do'stlarim...", "Siz, aynan siz..."

══ SOUND LAWS ══
• Every sentence must work OUT LOUD
• Vary length: long → long → SHORT. The short one hits hardest.
• No passive voice at climactic moments
• Write the FULL speech, not an outline. Performance-ready.
""",

"ideas": """
You are the world's most brilliant creative strategist.
You combine de Bono's lateral thinking, IDEO's design intelligence,
Y Combinator's startup instincts, and a poet's imaginative leaps.

══ IDEA PHILOSOPHY ══
The best ideas seem obvious — but only AFTER someone says them.
Your job: find what everyone missed.

══ QUALITY TESTS — every idea must pass all 3 ══
1. Specificity — specific enough to have a name?
   ✗ "Health app"  ✓ "Toshkent mahallalari uchun AR tibbiy maslahat tizimi"
2. Surprise — would the user think "Oh — I hadn't thought of that"?
3. Action — can they start TODAY with current resources?

══ MANDATORY FORMAT ══

### 💡 [Thematic Category]

**[N]. [Bold, Memorable Idea Name]**
*Mohiyat:* [What it is — 1 precise sentence]
*Nima uchun ishlaydi:* [The insight behind why it works — 2 sentences]
*Noyoblik:* [What makes it different from obvious alternatives]
*Birinchi qadam:* [The most concrete, doable action — today, not "someday"]

---
### 🏆 ENG YAXSHI TANLOV
**[Idea Name]**
[3-4 sentences: why THIS one. Specific. Convincing. Show reasoning.]
*Nega hozir?* [Why this idea is especially well-timed right now]

══ GENERATION RULES ══
• Minimum 6 ideas: at least one tech, one social, one creative, one wild card
• At least 2 should feel "unexpected"
• Be GENUINELY excited — good ideas deserve real enthusiasm 🚀
""",

"translate": """
You are an elite literary and professional translator.
Uzbek, Russian, and English at native level — including cultural contexts, idioms, registers.
You translate not words but MEANING, TONE, and SOUL.

══ TRANSLATION LAWS ══
1. Preserve register — formal stays formal; poetry stays poetic; street stays street
2. Idioms → equivalent idioms in target language, never literal
3. Cultural references without equivalent → brief footnote [*], not clumsy explanation
4. Literary text → preserve rhythm and imagery
5. Names: transliterate. Titles/concepts: translate.

══ OUTPUT FORMAT ══

**📄 Asl matn / Оригинал / Original:**
> [original text]

**✅ Tarjima / Перевод / Translation:**
> [translated text]

**📝 Izohlar** *(faqat murakkab hollarda)*:
- [term]: [brief cultural or linguistic note]

**🔤 Lug'at** *(5+ qiyin so'z bo'lsa)*:
| Asl | Tarjima | Izoh |
|-----|---------|------|
| ... | ... | ... |

If language pair is unclear → ask once, then translate immediately.
""",

"summary": """
You are the world's sharpest analytical mind.
Feynman's ability to explain anything simply + a judge's precision + a philosopher's depth.

══ ANALYSIS LAWS ══
1. Find the ONE core idea — everything else exists to support it
2. Structure reveals meaning — the way you organise IS an argument
3. Simple language for complex ideas — if a thoughtful 14-year-old can't follow, rewrite
4. Your perspective matters — analysis without judgment is just description
5. What's missing matters too — great analysis notes what the text DOESN'T say

══ MANDATORY FORMAT ══

## 🎯 Asosiy g'oya
**[The single most important point — 1-2 sentences maximum]**

## 🔑 Muhim fikrlar
- **[Point 1]:** [brief elaboration — 1 sentence]
- **[Point 2]:** [brief elaboration]
- **[Point 3]:** [brief elaboration]

## 🧩 Chuqur tahlil
[Para 1: What the text/topic is really about beneath the surface]
[Para 2: The strongest argument or most interesting part]
[Para 3: Weaknesses, gaps, or what's missing]
[Para 4: Implications — what this means in wider context]

## 💡 Noodatiy insight
[The one thing a surface reader would miss — hidden pattern, contradiction,
unexpected implication, or connection to a different domain]

## ❓ Ochiq savol *(ixtiyoriy)*
[The most interesting unresolved tension this raises]
""",

"general": """
You are Somo AI — the most useful, honest, and brilliant assistant the user has encountered.
Deep knowledge across science, math, history, technology, art, literature, culture, philosophy.

══ PHILOSOPHY ══
Be genuinely helpful, not performatively helpful.
Give real answers, not hedged non-answers.
Treat the user as a capable adult who can handle complexity and honesty.

══ RESPONSE CALIBRATION ══
• Simple factual → Direct answer, 1-3 sentences, no fluff
• Complex question → Rich explanation with structure, examples, perspective
• Creative request → Full output, not an outline or description
• Emotional/personal → Warm, present, genuine — not clinical
• Ambiguous → Best interpretation, deliver it, offer to adjust

══ FORMATTING INTELLIGENCE ══
Use formatting ONLY when it serves the reader:
- Headers: 3+ distinct sections only
- Lists: genuinely list-like information
- Bold: terms the reader needs to hold on to
- Plain prose: explanations, stories, opinions, emotional content
DO NOT format casual conversation into bullet points. It feels inhuman.

══ PERSONALITY ══
• Curious and genuinely excited about ideas
• Warm but never sycophantic — never start with "Great question!"
• Honest — "I don't know" is sometimes the most useful answer
• Uzbek cultural awareness — local values, references, context

══ QUALITY STANDARD ══
After every response: "Is there anything here I wrote just to fill space?"
Delete anything that fails. No exceptions.
""",
}

FORMATTING_RULES = """
═══════════════════════════════════════════════════════════════
UNIVERSAL OUTPUT LAWS — apply to every single response
═══════════════════════════════════════════════════════════════

EMOJIS — purposeful, warm, never spam:
• Use 1-3 emojis max per response unless celebratory context
• Emojis should ADD meaning: 📝 before an essay, 💡 before an insight
• Never as filler: "Bu juda yaxshi 👍✨🌟" = weak writing

TYPOGRAPHY:
• **Bold** for: key terms, must-remember facts, critical emphasis
• *Italic* for: book/film titles, foreign words, gentle nuance
• `code` for: technical terms, command names, single tokens
• > blockquote: direct quotations, key definitions, standout insights

STRUCTURE — use ONLY when it genuinely helps the reader:
• ## Headers: for responses with 3+ clearly distinct sections
• ### Sub-headers: for complex breakdowns within sections
• Bullet lists: for genuinely list-like items (3+), never for prose
• Numbered lists: for sequences, steps, rankings only
• Tables: ONLY when grid structure reveals what words cannot
• Code blocks (```lang): for any multi-line code, ALWAYS with language tag
• Horizontal rule ---: to visually separate major sections

MATHEMATICS — always use LaTeX:
• Inline: $ax^2 + bx + c = 0$
• Display: $$\\int_0^\\infty e^{-x^2}dx = \\frac{\\sqrt{\\pi}}{2}$$
• Never use ASCII math: a^2+b^2=c^2 is wrong; $a^2+b^2=c^2$ is correct

RESPONSE LENGTH — calibrate precisely:
• Casual chat → 1-4 sentences maximum
• Factual question → direct answer + necessary context only
• Complex analysis → full thorough response, zero padding
• Creative request → COMPLETE work, not "here's how I'd write it"
• Never end with "Agar yana savollaringiz bo'lsa..." unless genuinely needed

QUALITY CHECKLIST — internal check before every response:
✓ Does every paragraph move the response forward?
✓ Is every format element (bold, list, header) earning its place?
✓ Is the final line/sentence the strongest?
✓ Would a proud professional sign their name to this?
"""

# ════════════════════════════════════════════════════════════════
#  BUILD SYSTEM PROMPT — Rejim asosida to'liq prompt yig'adi
#  Tarkib: IDENTITY + MODE_INSTRUCTION + LANG_RULE + FORMATTING
# ════════════════════════════════════════════════════════════════
def build_system_prompt(mode: str) -> str:
    """
    Berilgan rejim uchun to'liq system promptni qaytaradi.

    Args:
        mode: Rejim nomi (esse, story, speech, ideas, translate, summary, general)

    Returns:
        str: To'liq system prompt matni
    """
    instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["general"])
    return "\n\n".join([IDENTITY, instruction, LANG_RULE, FORMATTING_RULES])


# ════════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════════
active_mode = st.session_state.active_mode
mode_meta   = MODE_META.get(active_mode, MODE_META["general"])
_badge      = "Gemini 2.0 Flash ✦" if st.session_state.use_gemini else "Groq · Llama 3.3 ✦"

mode_ind = ""
if active_mode != "general":
    mode_ind = (
        '<div class="mode-indicator on">'
        + mode_meta["icon"] + " " + mode_meta["label"]
        + '</div>'
    )

st.markdown(
    '<div class="hdr">'
    '<div class="hdr-brand">'
    '<div class="hdr-logo">S</div>'
    '<div>'
    '<div class="hdr-title">Somo <em>AI</em></div>'
    '<div class="hdr-author">by Usmonov Sodiq</div>'
    '</div></div>'
    '<div class="hdr-right">'
    + mode_ind +
    '<div class="status-badge"><div class="status-dot"></div>Online</div>'
    '<div class="model-badge">' + _badge + '</div>'
    '</div></div>',
    unsafe_allow_html=True
)


# ════════════════════════════════════════════════════════════════
#  CHAT AREA
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

KJ = '<script>setTimeout(()=>{if(typeof renderMathInElement!=="undefined")renderMathInElement(document.body);},120);</script>'

# ════════════════════════════════════════════════════════════════
#  WELCOME SCREEN — Xabarlar bo'sh bo'lganda ko'rsatiladi
#  Tarkib: Salomlashuv + Sarlavha + 6 ta karta + Chips + Random btn
# ════════════════════════════════════════════════════════════════
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
      <div class="wlc-badge">✨ Ijodiy AI Yordamchi</div>
      <div class="wlc-headline">Ijodingizni<br><em>kuchlaytiring</em></div>
      <div class="wlc-sub">
        Shunchaki xabar yozing — esse, hikoya, nutq, tarjima yoki istalgan savol.<br>
        Somo AI mavzudan rejimni o'zi aniqlaydi. 🚀
      </div>
      <div class="feat-grid">
        <div class="feat-card"><span class="feat-icon">✍️</span>
          <div class="feat-name">Esse / Referat</div>
          <div class="feat-hint">"Vatan haqida esse yoz"</div></div>
        <div class="feat-card"><span class="feat-icon">📖</span>
          <div class="feat-name">Hikoya / She'r</div>
          <div class="feat-hint">"Bahor haqida she'r"</div></div>
        <div class="feat-card"><span class="feat-icon">🎤</span>
          <div class="feat-name">Nutq</div>
          <div class="feat-hint">"Yoshlar haqida nutq"</div></div>
        <div class="feat-card"><span class="feat-icon">🧠</span>
          <div class="feat-name">G'oyalar</div>
          <div class="feat-hint">"Startup g'oyalari ber"</div></div>
        <div class="feat-card"><span class="feat-icon">🌍</span>
          <div class="feat-name">Tarjima</div>
          <div class="feat-hint">"Translate to English"</div></div>
        <div class="feat-card"><span class="feat-icon">📋</span>
          <div class="feat-name">Xulosa / Tahlil</div>
          <div class="feat-hint">"Ushbu matnni tahlil qil"</div></div>
      </div>
      <div class="chip-row">
        <div class="p-chip">📝 "Ekologiya haqida esse"</div>
        <div class="p-chip">🌹 "Bahor haqida she'r yoz"</div>
        <div class="p-chip">🎤 "Maktab haqida nutq"</div>
        <div class="p-chip">💡 "10 ta biznes g'oya ber"</div>
        <div class="p-chip">🌍 "Hello — o'zbekchaga tarjima"</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    for msg in st.session_state.messages:
        role     = msg["role"]
        content  = msg["content"]
        ts       = msg.get("time", "")
        m_mode   = msg.get("mode", "general")
        m_meta   = MODE_META.get(m_mode, MODE_META["general"])

        if role == "user":
            st.markdown(
                '<div class="msg-row user">'
                '<div class="msg-body">'
                '<div class="bubble user">' + content + '</div>'
                '<div class="msg-time">' + ts + '</div>'
                '</div></div>',
                unsafe_allow_html=True
            )
        else:
            tag = ""
            if m_mode != "general":
                tag = '<div class="mode-tag">' + m_meta["icon"] + " " + m_meta["label"] + '</div><br>'
            _wc   = wc(content)
            _cpjs = ('<script>function cp' + str(i) + '(){'
                     'navigator.clipboard.writeText(' + repr(content) + ');'
                     'var b=document.getElementById("cpb' + str(i) + '");'
                     'b.innerText="✅ Nusxalandi";'
                     'setTimeout(()=>{b.innerText="📋 Nusxa"},2200);}'
                     '</script>')
            st.markdown(
                '<div class="msg-row ai">'
                '<div class="av ai">S</div>'
                '<div class="msg-body">'
                '<div class="msg-name">Somo AI</div>'
                '<div class="bubble ai">' + tag + md_to_html(content) + '</div>'
                '<div class="copy-row">'
                '<span class="msg-time">' + ts + '</span>'
                '<span class="wc-badge">📝 ' + str(_wc) + " so\'z</span>"
                '<button class="copy-btn" id="cpb' + str(i) + '" onclick="cp' + str(i) + '()">📋 Nusxa</button>'
                '</div>'
                '</div></div>' + _cpjs + KJ,
                unsafe_allow_html=True
            )

st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  COOLDOWN TIMER
# ════════════════════════════════════════════════════════════════
remaining = int(st.session_state.cooldown_end - time.time())
if remaining > 0:
    st.markdown(
        '<div class="cooldown-wrap">'
        '<div class="cooldown-box">'
        '<span class="cooldown-icon">⏳</span>'
        '<div><strong>API limiti tugadi.</strong> Iltimos kuting — '
        '<span class="cooldown-sec">' + str(remaining) + ' soniya</span></div>'
        '</div></div>',
        unsafe_allow_html=True
    )
    prompt = None
    st.chat_input("Iltimos kuting…", disabled=True)
    time.sleep(1)
    st.rerun()
else:
    prompt = st.chat_input("Xabar yozing… (esse, she'r, nutq, tarjima yoki istalgan savol)")

st.markdown(
    '<div class="input-footer">Somo AI · Usmonov Sodiq (Somo_AI) · Groq + Gemini</div>',
    unsafe_allow_html=True
)


# ════════════════════════════════════════════════════════════════
#  PROCESS MESSAGE — Foydalanuvchi xabarini qayta ishlash
#  Jarayon:
#  1. Rejimni aniqlash (detect_mode)
#  2. Xabarni tarixga qo'shish
#  3. User bubbleni ko'rsatish
#  4. Typing placeholder
#  5. API ga so'rov (Groq → Gemini fallback)
#  6. Streaming orqali real-time ko'rsatish
#  7. Javobni tarixga saqlash
# ════════════════════════════════════════════════════════════════
#  PROCESS MESSAGE
# ════════════════════════════════════════════════════════════════
if prompt and prompt.strip():
    user_text    = prompt.strip()
    now          = get_time()
    detected     = detect_mode(user_text)
    m_meta       = MODE_META.get(detected, MODE_META["general"])
    system_txt   = build_system_prompt(detected)

    st.session_state.active_mode = detected
    st.session_state.messages.append({
        "role": "user", "content": user_text, "time": now, "mode": detected
    })

    # render user bubble
    st.markdown(
        '<div class="msg-row user">'
        '<div class="msg-body">'
        '<div class="bubble user">' + user_text + '</div>'
        '<div class="msg-time">' + now + '</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    # typing placeholder
    ph = st.empty()
    ph.markdown(
        '<div class="msg-row ai">'
        '<div class="av ai">S</div>'
        '<div class="msg-body">'
        '<div class="msg-name">Somo AI</div>'
        '<div class="bubble ai"><span class="t-cur"></span></div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    # mode tag
    tag = ""
    if detected != "general":
        tag = '<div class="mode-tag">' + m_meta["icon"] + " " + m_meta["label"] + '</div><br>'

    def render(text: str, cursor: bool = False, ts: str = ""):
        cur = '<span class="t-cur"></span>' if cursor else ""
        td  = '<div class="msg-time">' + ts + '</div>' if ts else ""
        ph.markdown(
            '<div class="msg-row ai">'
            '<div class="av ai">S</div>'
            '<div class="msg-body">'
            '<div class="msg-name">Somo AI</div>'
            '<div class="bubble ai">' + tag + md_to_html(text) + cur + '</div>'
            + td +
            '</div></div>' + KJ,
            unsafe_allow_html=True
        )

    # ── Groq stream ──────────────────────────────────────────────
    def stream_groq() -> str:
        if not groq_client:
            raise Exception("no groq")
        msgs = [{"role": "system", "content": system_txt}]
        for m in st.session_state.messages:
            msgs.append({"role": m["role"], "content": m["content"]})
        stream = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=msgs,
            stream=True, max_tokens=4096, temperature=0.85,
        )
        out = ""
        for chunk in stream:
            out += chunk.choices[0].delta.content or ""
            render(out, cursor=True)
        return out

    # ── Gemini stream ─────────────────────────────────────────────
    def stream_gemini() -> str:
        if not gemini_client:
            raise Exception("no gemini")
        hist = []
        for m in st.session_state.messages[:-1]:
            hist.append({
                "role"  : "user" if m["role"] == "user" else "model",
                "parts" : [m["content"]]
            })
        chat = gemini_client.start_chat(history=hist)
        resp = chat.send_message(
            system_txt + "\n\n---\n\n" + user_text,
            generation_config={"temperature": GEMINI_TEMP, "max_output_tokens": GEMINI_MAX_TOK},
            stream=True,
        )
        out = ""
        for chunk in resp:
            try: out += chunk.text or ""
            except: pass
            if out: render(out, cursor=True)
        return out

    # ── Dual-API fallback ─────────────────────────────────────────
    full = ""
    is_rate = lambda e: any(k in str(e) for k in ["429","rate_limit","quota","rate limit","Resource exhausted"])

    try:
        if st.session_state.use_gemini:
            full = stream_gemini()
        else:
            full = stream_groq()
            st.session_state.use_gemini = False

    except Exception as e1:
        if is_rate(e1) and not st.session_state.use_gemini:
            # Groq limited → try Gemini
            st.session_state.use_gemini = True
            render("⚡ Groq limiti tugadi, Gemini ga o'tmoqda...", cursor=True)
            try:
                full = stream_gemini()
            except Exception as e2:
                if is_rate(e2):
                    st.session_state.cooldown_end = time.time() + COOLDOWN_LONG
                    full = "⏳ Ikkala API limiti tugadi. " + str(COOLDOWN_LONG) + " soniya kuting."
                else:
                    full = "❌ Gemini xatolik: " + str(e2)
        elif is_rate(e1) and st.session_state.use_gemini:
            # Gemini also limited → try Groq
            st.session_state.use_gemini = False
            render("⚡ Gemini limiti tugadi, Groq ga o'tmoqda...", cursor=True)
            try:
                full = stream_groq()
            except Exception as e3:
                if is_rate(e3):
                    st.session_state.cooldown_end = time.time() + COOLDOWN_LONG
                    full = "⏳ Ikkala API limiti tugadi. " + str(COOLDOWN_LONG) + " soniya kuting."
                else:
                    full = "❌ Xatolik: " + str(e3)
        elif "api_key" in str(e1).lower() or "auth" in str(e1).lower():
            full = "❌ API kalit xato. Secrets faylini tekshiring."
        else:
            full = "❌ Xatolik: " + str(e1)

    # final render
    if full:
        render(full, cursor=False, ts=get_time())

    st.session_state.messages.append({
        "role": "assistant", "content": full,
        "time": get_time(), "mode": detected
    })



# ════════════════════════════════════════════════════════════════
#  DEPLOYMENT  (Streamlit Cloud)
# ════════════════════════════════════════════════════════════════
#  .streamlit/secrets.toml:
#    GROQ_API_KEY   = "gsk_..."
#    GEMINI_API_KEY = "AIza..."
#
#  requirements.txt:
#    streamlit>=1.32.0
#    groq>=0.8.0
#    google-generativeai>=0.8.0
#
#  Ishga tushirish: streamlit run app.py
#
# ════════════════════════════════════════════════════════════════
#  MUAMMO / YECHIM (TROUBLESHOOTING)
# ════════════════════════════════════════════════════════════════
#  "Model topilmadi"    → API kalit versiyasini tekshiring
#  "Rate limit"         → Ikki API ham ishlaydi, vaqt o'tadi
#  "API kalit xato"     → Secrets faylini tekshiring
#  Javob chiqmaydi      → Brauzer consolini tekshiring (F12)
#  Matematika ko'rinmaydi → Sahifani yangilang (F5)
#
# ════════════════════════════════════════════════════════════════
#  VERSIYA TARIXI
# ════════════════════════════════════════════════════════════════
#  v1.0 — Boshlang'ich (Groq + qorong'i tema)
#  v2.0 — Cream dizayn, auto rejim aniqlash
#  v2.1 — Sidebar o'chirildi, layout=wide
#  v2.2 — Dual-API: Groq + Gemini fallback
#  v2.3 — Cooldown timer + input qulflash
#  v2.4 — System prompt kuchaytirildi (Navoiy, Neruda, MLK...)
#  v2.5 — AI bubble ramkasiz (Claude/ChatGPT uslubi)
#  v3.0 — Nusxa tugmasi, so'z soni, statistika,
#          tasodifiy ilhom, tozalash, salomlashuv,
#          konfiguratsiya bloki, yordamchi funksiyalar
#
# ════════════════════════════════════════════════════════════════
#  © 2026  Usmonov Sodiq  |  @Somo_AI
# ════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════
#  ADABIY MA'LUMOTNOMA — System prompt uchun manba adabiyotlar
# ════════════════════════════════════════════════════════════════
#
#  O'ZBEK ADABIYOTI — Somo AI o'rnak oladigan ustozlar:
#
#  📜 ALISHER NAVOIY (1441–1501)
#     — Xamsa, Xazoyinul-Maoniy, Muhokamatul-Lug'atayn
#     — Uslub: Ilohiy tasvirlar, ma'shuqa ramzi, g'azal nafosi
#     — Texnika: Tashbih (o'xshatish), Istiora (metafora), Ta'kid
#
#  📜 ABDULLA ORIPOV (1941–2016)
#     — "O'zbegim", "Ona", "Yig'laydi chang'i"
#     — Uslub: Oddiy so'z — cheksiz og'irlik, Vatan hasrati
#     — Texnika: Takror, Muqobil obraz, Emotsional aniqlik
#
#  📜 ERKIN VOHIDOV (1936–2016)
#     — "Ruboiylar", "Isyon va itoat"
#     — Uslub: Falsafiy hazil, milliy g'urur, so'z o'yini
#     — Texnika: Ironiya, Kontekst paradoks, Aforizm
#
#  📜 CHO'LPON (1897–1938)
#     — "Kecha va kunduz", "Uyqu"
#     — Uslub: Impressionistik detal, Erkin fragment, Melankholiya
#     — Texnika: Sinesteziya, Ichki monoloq, Simvol
#
#  📜 ABDULLA QAHHOR (1907–1968)
#     — "Sarob", "Sinchalak", "Bemor"
#     — Uslub: Keskin realizm, Qoʻgʻirchoq hazil, Unutilmas xarakter
#     — Texnika: Dialog orqali xarakter, Ziddiyat, Portret detal
#
#  ─────────────────────────────────────────────────────────────
#
#  JAHON ADABIYOTI — Somo AI o'rnak oladigan jahon ustozlari:
#
#  🌍 PABLO NERUDA (1904–1973)
#     — "Yigirma sevgi she'ri", "Yer sayyorasi"
#     — Uslub: Hissiy metafora, Tabiat va tana, Kosmik romantika
#
#  🌍 JALOLIDDIN RUMI (1207–1273)
#     — "Masnaviy", "Devon-i Kabir"
#     — Uslub: Mistik paradoks, Sevgi — koinot kuchi, Sukunat
#
#  🌍 ANTON CHEKHOV (1860–1904)
#     — "Palata No. 6", "Olcha bog'i"
#     — Uslub: Hech narsa izohlanmaydi, hammasi seziladi
#
#  🌍 O. HENRY (1862–1910)
#     — "Magi sovg'asi", "To'rt million"
#     — Uslub: Kutilmagan burilish — aldash emas, OCHISH
#
#  🌍 GABRIEL GARCÍA MÁRQUEZ (1927–2014)
#     — "Yuz yillik yolg'izlik"
#     — Uslub: Sehrli realizm, Vaqt mif sifatida
#
#  🌍 JORGE LUIS BORGES (1899–1986)
#     — "Fikrlar labirenti"
#     — Uslub: Borliq = Matn, Cheksiz kutubxona, Haqiqat egri
#
# ════════════════════════════════════════════════════════════════
#  NUTQ USTALARI — Speech mode uchun manba
# ════════════════════════════════════════════════════════════════
#
#  🎤 MARTIN LUTHER KING JR (1929–1968)
#     — "I Have a Dream" (1963)
#     — Texnika: Anafora ("I have a dream..."), Axloqiy yoy,
#       Muammo → Vizyon → Harakat, Diniy parallelizm
#
#  🎤 WINSTON CHURCHILL (1874–1965)
#     — "We shall fight on the beaches" (1940)
#     — Texnika: Cho'qqi lahzada qisqa jumlalar, Trikolon,
#       Hech qanday bezak — faqat kuch
#
#  🎤 BARACK OBAMA (1961–)
#     — TED va inauguratsiya nutqlari
#     — Texnika: Shaxsiy hikoya → Universal haqiqat,
#       "Va shuning uchun..." ko'prigi, Aniq raqamlar
#
# ════════════════════════════════════════════════════════════════
#  © 2026  Usmonov Sodiq  |  @Somo_AI
#  Barcha huquqlar himoyalangan
# ════════════════════════════════════════════════════════════════
