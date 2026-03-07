import streamlit as st
from groq import Groq
import time, re

# ═══════════════════════════════════════════════════════════════
#  MARKDOWN → HTML  (bold, italic, code, headers, lists, tables)
# ═══════════════════════════════════════════════════════════════
def md_to_html(text):
    """Convert markdown-flavoured text to safe HTML for st.markdown bubbles."""
    math_blocks = {}

    def save_math(m):
        key = f"__MATH{len(math_blocks)}__"
        math_blocks[key] = m.group(0)
        return key

    # Protect LaTeX before any other transforms
    text = re.sub(r'\$\$.+?\$\$', save_math, text, flags=re.DOTALL)
    text = re.sub(r'\$.+?\$',     save_math, text)

    # Fenced code blocks  ```lang\n...\n```
    text = re.sub(
        r'```(\w*)\n?(.*?)```',
        lambda m: f'<pre><code class="lang-{m.group(1)}">{m.group(2).strip()}</code></pre>',
        text, flags=re.DOTALL
    )

    # Inline code  `code`
    text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)

    # Headers  ### ## #
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', text, flags=re.MULTILINE)

    # Bold + italic  ***text***
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold  **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic  *text*
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)

    # Blockquote  > text
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)

    # Unordered list  - item  or  * item
    def build_ul(m):
        items = re.findall(r'^[\-\*] (.+)$', m.group(0), re.MULTILINE)
        lis   = ''.join(f'<li>{i}</li>' for i in items)
        return f'<ul>{lis}</ul>'
    text = re.sub(r'(^[\-\*] .+\n?)+', build_ul, text, flags=re.MULTILINE)

    # Ordered list  1. item
    def build_ol(m):
        items = re.findall(r'^\d+\. (.+)$', m.group(0), re.MULTILINE)
        lis   = ''.join(f'<li>{i}</li>' for i in items)
        return f'<ol>{lis}</ol>'
    text = re.sub(r'(\d+\. .+\n?)+', build_ol, text, flags=re.MULTILINE)

    # Horizontal rule  ---
    text = re.sub(r'^-{3,}$', '<hr>', text, flags=re.MULTILINE)

    # Newlines → <br>
    text = re.sub(r'\n', '<br>', text)

    # Restore LaTeX
    for key, val in math_blocks.items():
        text = text.replace(key, val)

    return text


# ═══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Somo AI",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ═══════════════════════════════════════════════════════════════
#  STYLES  —  full cream design, Fraunces + DM Sans
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0">

<!-- Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,700;0,9..144,900;1,9..144,400;1,9..144,700&family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<!-- KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{
    delimiters:[
      {left:'$$',right:'$$',display:true},
      {left:'$', right:'$', display:false}
    ]
  });"></script>

<style>
/* ─────────────────────────────────────────────
   DESIGN TOKENS
───────────────────────────────────────────── */
:root {
  --cream   : #fdf6e3;
  --warm    : #f5ead0;
  --card    : #fffef8;
  --border  : #e8dfc8;
  --amber   : #f59e0b;
  --orange  : #ea580c;
  --text    : #1c1408;
  --muted   : #7c6d52;
  --light   : #b09878;
  --green   : #15803d;
  --blue    : #3b82f6;
  --indigo  : #6366f1;
  --rose    : #e11d48;
  --fh      : 'Fraunces', serif;
  --fb      : 'DM Sans', sans-serif;
  --shadow  : 0 2px 12px rgba(0,0,0,.07);
  --shadow-lg: 0 8px 32px rgba(0,0,0,.12);
}

/* ─────────────────────────────────────────────
   RESET / BASE
───────────────────────────────────────────── */
html, body {
  background : var(--cream) !important;
  margin     : 0;
  padding    : 0;
  -webkit-font-smoothing: antialiased;
}

*, *::before, *::after { box-sizing: border-box; }

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main { background: var(--cream) !important; }

/* Hide all Streamlit chrome */
#MainMenu,
footer,
header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }

.block-container,
[data-testid="stMainBlockContainer"] {
  padding    : 0 !important;
  max-width  : 100% !important;
}

/* ─────────────────────────────────────────────
   TOP HEADER  (logo + mode pills + status)
───────────────────────────────────────────── */
.hdr {
  display         : flex;
  align-items     : center;
  justify-content : space-between;
  gap             : 12px;
  padding         : .72rem 2rem;
  background      : rgba(253,246,227,.97);
  border-bottom   : 1.5px solid var(--border);
  position        : sticky;
  top             : 0;
  z-index         : 200;
  backdrop-filter : blur(16px);
}

/* Brand */
.hdr-brand {
  display     : flex;
  align-items : center;
  gap         : 9px;
  flex-shrink : 0;
}

.hdr-logo {
  width           : 34px;
  height          : 34px;
  background      : linear-gradient(135deg, var(--amber), var(--orange));
  border-radius   : 9px;
  display         : flex;
  align-items     : center;
  justify-content : center;
  font-family     : var(--fh) !important;
  font-size       : 15px;
  font-weight     : 900;
  color           : #fff;
  box-shadow      : 0 3px 10px rgba(245,158,11,.32);
  flex-shrink     : 0;
  letter-spacing  : -.5px;
}

.hdr-title {
  font-family : var(--fh) !important;
  font-size   : .95rem;
  font-weight : 900;
  color       : var(--text);
  line-height : 1;
}
.hdr-title em { color: var(--orange); font-style: italic; }

.hdr-author {
  font-family    : var(--fb) !important;
  font-size      : .56rem;
  color          : var(--light);
  letter-spacing : 1px;
  margin-top     : 2px;
  text-transform : uppercase;
}

/* Mode pills — scrollable center strip */
.hdr-modes {
  display         : flex;
  align-items     : center;
  gap             : .38rem;
  flex            : 1;
  justify-content : center;
  overflow-x      : auto;
  scrollbar-width : none;
  padding         : 0 .5rem;
}
.hdr-modes::-webkit-scrollbar { display: none; }

.mpill {
  display         : flex;
  align-items     : center;
  gap             : 4px;
  padding         : .26rem .7rem;
  border-radius   : 20px;
  border          : 1.5px solid var(--border);
  background      : var(--warm);
  font-family     : var(--fb) !important;
  font-size       : .65rem;
  font-weight     : 500;
  color           : var(--muted);
  cursor          : pointer;
  white-space     : nowrap;
  flex-shrink     : 0;
  transition      : all .15s ease;
  user-select     : none;
}
.mpill:hover {
  border-color : var(--amber);
  color        : var(--orange);
  background   : #fff8ee;
}
.mpill.on {
  background   : linear-gradient(135deg, var(--amber), var(--orange));
  border-color : transparent;
  color        : #fff;
  font-weight  : 600;
  box-shadow   : 0 2px 8px rgba(245,158,11,.3);
}

/* Status badge */
.hdr-status {
  display     : flex;
  align-items : center;
  gap         : 5px;
  flex-shrink : 0;
}
.status-dot {
  width         : 6px;
  height        : 6px;
  background    : var(--green);
  border-radius : 50%;
  animation     : pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1;   transform: scale(1);   }
  50%       { opacity: .6; transform: scale(1.15); }
}
.status-txt {
  font-family : var(--fb) !important;
  font-size   : .6rem;
  color       : var(--green);
}
.model-badge {
  font-family    : var(--fb) !important;
  font-size      : .6rem;
  color          : var(--muted);
  background     : var(--warm);
  border         : 1.5px solid var(--border);
  border-radius  : 20px;
  padding        : .2rem .6rem;
  white-space    : nowrap;
}

/* ─────────────────────────────────────────────
   CHAT WRAPPER  (centred column)
───────────────────────────────────────────── */
.chat-wrap {
  max-width : 800px;
  margin    : 0 auto;
  padding   : 1.6rem 2rem 5.5rem;
  width     : 100%;
}

/* ─────────────────────────────────────────────
   WELCOME SCREEN
───────────────────────────────────────────── */
.welcome {
  text-align : center;
  padding    : 2rem 0 1.5rem;
}

.wlc-badge {
  display        : inline-flex;
  align-items    : center;
  gap            : 6px;
  background     : linear-gradient(135deg, var(--amber), var(--orange));
  color          : #fff;
  border-radius  : 30px;
  padding        : .3rem 1rem;
  font-family    : var(--fb) !important;
  font-size      : .62rem;
  font-weight    : 600;
  letter-spacing : 1.5px;
  text-transform : uppercase;
  margin-bottom  : 1.1rem;
  box-shadow     : 0 4px 14px rgba(245,158,11,.32);
  animation      : badgePop .55s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes badgePop {
  from { opacity: 0; transform: scale(.7); }
  to   { opacity: 1; transform: scale(1); }
}

.wlc-headline {
  font-family : var(--fh) !important;
  font-size   : clamp(2rem, 5.5vw, 3rem);
  font-weight : 900;
  color       : var(--text);
  line-height : 1.1;
  margin-bottom: .35rem;
  animation   : slideUp .5s ease-out .1s both;
}
.wlc-headline em {
  font-style                : italic;
  background                : linear-gradient(135deg, var(--amber), var(--orange));
  -webkit-background-clip   : text;
  -webkit-text-fill-color   : transparent;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0);    }
}

.wlc-sub {
  font-family   : var(--fb) !important;
  font-size     : .875rem;
  color         : var(--muted);
  line-height   : 1.7;
  max-width     : 420px;
  margin        : .6rem auto 2rem;
  animation     : slideUp .5s ease-out .2s both;
}

/* 3-col feature grid */
.feat-grid {
  display               : grid;
  grid-template-columns : repeat(3, 1fr);
  gap                   : .65rem;
  max-width             : 560px;
  margin                : 0 auto 1.6rem;
  animation             : slideUp .5s ease-out .3s both;
}
.feat-card {
  background    : var(--card);
  border        : 1.5px solid var(--border);
  border-radius : 14px;
  padding       : .95rem .6rem;
  text-align    : center;
  cursor        : default;
  transition    : all .22s cubic-bezier(.34,1.4,.64,1);
}
.feat-card:hover {
  transform    : translateY(-3px);
  border-color : var(--amber);
  box-shadow   : 0 6px 22px rgba(0,0,0,.09);
}
.feat-icon  { font-size: 1.5rem; display: block; margin-bottom: .4rem; }
.feat-name  {
  font-family : var(--fb) !important;
  font-size   : .7rem;
  font-weight : 700;
  color       : var(--text);
  margin-bottom: .18rem;
}
.feat-hint  {
  font-family : var(--fb) !important;
  font-size   : .58rem;
  color       : var(--light);
}

/* Prompt chips */
.chip-row {
  display         : flex;
  gap             : .42rem;
  flex-wrap       : wrap;
  justify-content : center;
  animation       : slideUp .5s ease-out .4s both;
}
.p-chip {
  background    : var(--warm);
  border        : 1.5px solid var(--border);
  border-radius : 20px;
  padding       : .3rem .75rem;
  font-family   : var(--fb) !important;
  font-size     : .68rem;
  color         : var(--muted);
  cursor        : default;
  transition    : all .15s;
}
.p-chip:hover { border-color: var(--amber); color: var(--orange); }

/* ─────────────────────────────────────────────
   MESSAGE ROWS
───────────────────────────────────────────── */
.msg-row {
  display       : flex;
  gap           : 10px;
  margin-bottom : 1.25rem;
  animation     : msgIn .28s cubic-bezier(.34,1.2,.64,1);
}
@keyframes msgIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0);    }
}
.msg-row.user { flex-direction: row-reverse; }

/* Avatar */
.av {
  width           : 30px;
  height          : 30px;
  min-width       : 30px;
  border-radius   : 8px;
  display         : flex;
  align-items     : center;
  justify-content : center;
  font-size       : 12px;
  font-weight     : 700;
  flex-shrink     : 0;
  align-self      : flex-start;
  margin-top      : 2px;
}
.av.user { background: linear-gradient(135deg, var(--indigo), var(--blue)); color: #fff; }
.av.ai   {
  background  : linear-gradient(135deg, var(--amber), var(--orange));
  color       : #fff;
  font-family : var(--fh) !important;
  font-size   : 13px;
  box-shadow  : 0 2px 8px rgba(245,158,11,.3);
}

/* Message body */
.msg-body { max-width: 76%; }
.msg-name {
  font-family    : var(--fb) !important;
  font-size      : .58rem;
  color          : var(--light);
  margin-bottom  : .22rem;
  letter-spacing : .5px;
  text-transform : uppercase;
}
.msg-row.user .msg-name { text-align: right; }

/* Bubble */
.bubble {
  padding       : .82rem 1.05rem;
  border-radius : 14px;
  font-family   : var(--fb) !important;
  font-size     : .875rem;
  line-height   : 1.75;
  color         : var(--text);
  word-break    : break-word;
}
.bubble.user {
  background          : #eff6ff;
  border              : 1.5px solid #c7d2fe;
  border-top-right-radius : 3px;
}
.bubble.ai {
  background              : var(--card);
  border                  : 1.5px solid var(--border);
  border-top-left-radius  : 3px;
  box-shadow              : var(--shadow);
}

/* Mode tag inside AI bubble */
.mode-tag {
  display        : inline-block;
  font-family    : var(--fb) !important;
  font-size      : .56rem;
  font-weight    : 700;
  letter-spacing : 1.5px;
  text-transform : uppercase;
  background     : linear-gradient(135deg, var(--amber), var(--orange));
  color          : #fff;
  padding        : .14rem .5rem;
  border-radius  : 8px;
  margin-bottom  : .42rem;
}

/* Bubble rich content */
.bubble strong { color: var(--orange); font-weight: 700; }
.bubble em     { color: var(--muted); }

.bubble h1, .bubble h2, .bubble h3 {
  font-family   : var(--fh) !important;
  font-weight   : 700;
  color         : var(--text);
  margin        : .8rem 0 .28rem;
}
.bubble h1 { font-size: 1.12rem; }
.bubble h2 { font-size: 1rem;    }
.bubble h3 { font-size: .94rem;  }

.bubble code {
  background    : rgba(245,158,11,.1);
  border        : 1px solid rgba(245,158,11,.22);
  padding       : .1rem .38rem;
  border-radius : 5px;
  font-size     : .78rem;
  color         : var(--orange);
  font-family   : 'Courier New', 'SF Mono', monospace !important;
}
.bubble pre {
  background    : var(--warm);
  border        : 1.5px solid var(--border);
  border-radius : 10px;
  padding       : .9rem 1rem;
  overflow-x    : auto;
  margin        : .6rem 0;
}
.bubble pre code {
  background : none;
  border     : none;
  padding    : 0;
  color      : var(--green);
  font-size  : .77rem;
}
.bubble ul, .bubble ol { padding-left: 1.2rem; margin: .3rem 0; }
.bubble li  { margin-bottom: .22rem; }
.bubble blockquote {
  border-left   : 2.5px solid var(--amber);
  background    : rgba(245,158,11,.05);
  padding       : .45rem .9rem;
  border-radius : 0 8px 8px 0;
  color         : var(--muted);
  margin        : .45rem 0;
  font-style    : italic;
}
.bubble table {
  border-collapse : collapse;
  width           : 100%;
  margin          : .55rem 0;
  font-size       : .78rem;
}
.bubble th {
  background  : var(--warm);
  padding     : .38rem .65rem;
  border      : 1.5px solid var(--border);
  color       : var(--orange);
  font-weight : 700;
  text-align  : left;
}
.bubble td { padding: .35rem .65rem; border: 1px solid var(--border); }
.bubble tr:nth-child(even) { background: rgba(0,0,0,.018); }
.bubble hr { border: none; border-top: 1px solid var(--border); margin: .55rem 0; }

/* Timestamp */
.msg-time {
  font-family : var(--fb) !important;
  font-size   : .56rem;
  color       : var(--light);
  margin-top  : .22rem;
  opacity     : .65;
}
.msg-row.user .msg-time { text-align: right; }

/* Typing cursor */
.t-cur {
  display        : inline-block;
  width          : 2px;
  height         : .88em;
  background     : var(--orange);
  margin-left    : 2px;
  vertical-align : middle;
  animation      : blink .7s steps(1) infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

/* ─────────────────────────────────────────────
   CHAT INPUT  (Streamlit native, restyled)
───────────────────────────────────────────── */
[data-testid="stBottom"] {
  max-width  : 800px !important;
  margin     : 0 auto !important;
  left       : 50% !important;
  transform  : translateX(-50%) !important;
  width      : 100% !important;
  padding    : 0 2rem !important;
}

[data-testid="stChatInput"] {
  background : var(--card) !important;
  border     : 2px solid var(--border) !important;
  border-radius: 16px !important;
  box-shadow : var(--shadow) !important;
  transition : border-color .2s, box-shadow .2s !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color : var(--amber) !important;
  box-shadow   : 0 0 0 3px rgba(245,158,11,.14), var(--shadow) !important;
}
[data-testid="stChatInput"] textarea {
  background  : transparent !important;
  color       : var(--text) !important;
  font-size   : .875rem !important;
  font-family : var(--fb) !important;
  border      : none !important;
  outline     : none !important;
  box-shadow  : none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
  color: var(--light) !important;
}
[data-testid="stChatInput"] button {
  background    : linear-gradient(135deg, var(--amber), var(--orange)) !important;
  border        : none !important;
  border-radius : 11px !important;
  box-shadow    : 0 3px 10px rgba(245,158,11,.32) !important;
  transition    : opacity .15s !important;
}
[data-testid="stChatInput"] button:hover { opacity: .85 !important; }
[data-testid="stChatInput"] button svg   { fill: #fff !important; }

.input-footer {
  text-align  : center;
  font-family : var(--fb) !important;
  font-size   : .56rem;
  color       : var(--light);
  padding     : .18rem 0 .55rem;
  letter-spacing: .3px;
}

/* ─────────────────────────────────────────────
   KATEX
───────────────────────────────────────────── */
.katex          { font-size: 1em !important; color: var(--text) !important; }
.katex-display  { overflow-x: auto; padding: .3rem 0; }

/* ─────────────────────────────────────────────
   SCROLLBAR
───────────────────────────────────────────── */
::-webkit-scrollbar       { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* ─────────────────────────────────────────────
   RESPONSIVE  — mobile ≤ 640px
───────────────────────────────────────────── */
@media (max-width: 640px) {
  .hdr              { padding: .65rem 1rem; gap: 8px; }
  .hdr-author       { display: none; }
  .hdr-title        { font-size: .88rem; }
  .hdr-logo         { width: 30px; height: 30px; font-size: 13px; }
  .mpill            { font-size: .6rem; padding: .22rem .6rem; }

  .chat-wrap        { padding: 1.2rem 1rem 5rem; }

  .wlc-headline     { font-size: clamp(1.75rem, 8vw, 2.4rem); }
  .wlc-sub          { font-size: .82rem; }
  .feat-grid        { grid-template-columns: repeat(2, 1fr); max-width: 100%; }
  .feat-card        { padding: .8rem .5rem; }

  .msg-body         { max-width: 88%; }
  .bubble           { font-size: .83rem; padding: .68rem .85rem; }
  .p-chip           { font-size: .63rem; padding: .26rem .65rem; }

  [data-testid="stBottom"] { padding: 0 .8rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  GROQ CLIENT
# ═══════════════════════════════════════════════════════════════
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("❌ GROQ_API_KEY topilmadi. Streamlit Secrets ga qo'shing.")
    st.stop()


# ═══════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "esse"


# ═══════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════
MODES = {
    "esse"     : {"icon": "✍️",  "label": "Esse",     "full": "Esse / Referat",    "ph": "Esse mavzusini yozing… (masalan: 'Vatan haqida esse')"},
    "story"    : {"icon": "📖",  "label": "Hikoya",   "full": "Hikoya / She'r",    "ph": "Hikoya yoki she'r so'rang… (masalan: 'Bahor haqida she'r')"},
    "speech"   : {"icon": "🎤",  "label": "Nutq",     "full": "Nutq / Taqdimot",   "ph": "Nutq mavzusini kiriting… (masalan: 'Yoshlar haqida nutq')"},
    "ideas"    : {"icon": "🧠",  "label": "G'oyalar", "full": "G'oya generatsiya", "ph": "G'oya so'rang… (masalan: 'Startup g'oyalari ber')"},
    "translate": {"icon": "🌍",  "label": "Tarjima",  "full": "Tarjimon",          "ph": "Tarjima qilish uchun matn yozing…"},
    "summary"  : {"icon": "📋",  "label": "Xulosa",   "full": "Xulosa / Tahlil",   "ph": "Tahlil qilmoqchi bo'lgan matnni kiriting…"},
}

MODEL = "llama-3.3-70b-versatile"

LANG_DETECT = """
LANGUAGE RULE: Detect the user's language from their message and always reply in that exact language.
- Uzbek message  → reply in Uzbek
- Russian message → reply in Russian
- English message → reply in English
"""

IDENTITY = """
IDENTITY — never change, never invent:
- Your name    : Somo AI
- Created by   : Usmonov Sodiq  (brand: Somo_AI)
- Powered by   : Groq
- NOT made by OpenAI, Anthropic, Google, Metamorf or any other company
- If asked who made you: say "Men Usmonov Sodiq (Somo_AI) tomonidan yaratilganman"
"""

MODE_INSTRUCTIONS = {
    "esse"     : "You specialise in academic essays and reports. Write with clear intro, body paragraphs, and conclusion. Use rich markdown: headers, bold key terms, numbered lists, blockquotes for evidence.",
    "story"    : "You specialise in creative writing — stories, poems, fairy tales. Use vivid imagery, metaphor, narrative arc. Make the language beautiful and emotionally resonant.",
    "speech"   : "You specialise in public speaking scripts. Craft powerful openings, structured arguments, rhetorical questions, and memorable closings. Make every sentence land.",
    "ideas"    : "You specialise in brainstorming. Generate original, diverse, actionable ideas. Organise them in numbered lists with brief explanations. Be inspiring and energetic.",
    "translate": "You specialise in translation between Uzbek, Russian and English. Translate accurately while preserving tone and style. For student texts add a short vocabulary note for difficult words.",
    "summary"  : "You specialise in text analysis and summarisation. Extract key points in bullet lists, provide structured analysis with headers, and explain complex ideas simply.",
}

GENERAL_RULES = """
FORMATTING — always apply:
- Emojis used naturally and contextually ✨
- **bold** for key concepts, *italics* for nuance
- Headers ## and ### for long structured answers
- Tables, bullet lists, blockquotes where appropriate
- Code blocks with language tag for any code
- For mathematics: $inline LaTeX$ or $$display LaTeX$$

PERSONALITY:
- Warm, encouraging, student-friendly
- Concise but never shallow
- Celebrate good ideas and creative effort 🌟
"""

def build_system_prompt(mode: str) -> str:
    return "\n\n".join([IDENTITY, MODE_INSTRUCTIONS[mode], LANG_DETECT, GENERAL_RULES])

def get_time() -> str:
    return time.strftime("%H:%M")


# ═══════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════
cur = MODES[st.session_state.mode]

mode_pills_html = "".join(
    f'<div class="mpill {"on" if k == st.session_state.mode else ""}">'
    f'{m["icon"]} {m["label"]}</div>'
    for k, m in MODES.items()
)

st.markdown(f"""
<div class="hdr">

  <!-- Brand -->
  <div class="hdr-brand">
    <div class="hdr-logo">S</div>
    <div>
      <div class="hdr-title">Somo <em>AI</em></div>
      <div class="hdr-author">by Usmonov Sodiq</div>
    </div>
  </div>

  <!-- Mode selector (visual only) -->
  <div class="hdr-modes">{mode_pills_html}</div>

  <!-- Status -->
  <div class="hdr-status">
    <div class="status-dot"></div>
    <span class="status-txt">Online</span>
    <div class="model-badge">Llama 3.3 · 70B</div>
  </div>

</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  HIDDEN STREAMLIT BUTTONS  (drive mode state)
# ═══════════════════════════════════════════════════════════════
cols = st.columns(len(MODES))
for i, (k, m) in enumerate(MODES.items()):
    with cols[i]:
        if st.button(f"{m['icon']} {m['label']}", key=f"mbtn_{k}", help=m["full"]):
            st.session_state.mode = k
            st.rerun()

# Hide the native Streamlit buttons — we use the CSS pills above
st.markdown(
    "<style>div[data-testid='stHorizontalBlock']{display:none!important;}</style>",
    unsafe_allow_html=True
)


# ═══════════════════════════════════════════════════════════════
#  CHAT AREA
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

if not st.session_state.messages:
    # ── Welcome screen ──────────────────────────────────────────
    st.markdown(f"""
    <div class="welcome">

      <div class="wlc-badge">✨ Ijodiy AI Yordamchi</div>

      <div class="wlc-headline">
        Ijodingizni<br><em>kuchlaytiring</em>
      </div>

      <div class="wlc-sub">
        Esse, hikoya, nutq, g'oyalar va tarjima — barchasi bir joyda.<br>
        O'z tilida, o'z uslubida. 🚀
      </div>

      <div class="feat-grid">
        <div class="feat-card">
          <span class="feat-icon">✍️</span>
          <div class="feat-name">Esse / Referat</div>
          <div class="feat-hint">Maqola yozish</div>
        </div>
        <div class="feat-card">
          <span class="feat-icon">📖</span>
          <div class="feat-name">Hikoya / She'r</div>
          <div class="feat-hint">Ijodiy yozuv</div>
        </div>
        <div class="feat-card">
          <span class="feat-icon">🎤</span>
          <div class="feat-name">Nutq</div>
          <div class="feat-hint">Taqdimot matni</div>
        </div>
        <div class="feat-card">
          <span class="feat-icon">🧠</span>
          <div class="feat-name">G'oyalar</div>
          <div class="feat-hint">Beyin fırtınası</div>
        </div>
        <div class="feat-card">
          <span class="feat-icon">🌍</span>
          <div class="feat-name">Tarjimon</div>
          <div class="feat-hint">UZ ↔ RU ↔ EN</div>
        </div>
        <div class="feat-card">
          <span class="feat-icon">📋</span>
          <div class="feat-name">Xulosa</div>
          <div class="feat-hint">Tahlil qilish</div>
        </div>
      </div>

      <div class="chip-row">
        <div class="p-chip">📝 "Vatan haqida esse yoz"</div>
        <div class="p-chip">🌹 "Bahor haqida she'r"</div>
        <div class="p-chip">🎤 "Yoshlar haqida nutq"</div>
        <div class="p-chip">💡 "Startup g'oyalari ber"</div>
        <div class="p-chip">🌍 "Translate to English"</div>
      </div>

    </div>
    """, unsafe_allow_html=True)

else:
    # ── Render chat history ──────────────────────────────────────
    for msg in st.session_state.messages:
        role      = msg["role"]
        content   = msg["content"]
        ts        = msg.get("time", "")
        msg_mode  = msg.get("mode", st.session_state.mode)
        mode_info = MODES.get(msg_mode, cur)

        if role == "user":
            st.markdown(f"""
            <div class="msg-row user">
              <div class="av user">U</div>
              <div class="msg-body">
                <div class="msg-name">Siz</div>
                <div class="bubble user">{content}</div>
                <div class="msg-time">{ts}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            rendered = md_to_html(content)
            st.markdown(f"""
            <div class="msg-row ai">
              <div class="av ai">S</div>
              <div class="msg-body">
                <div class="msg-name">Somo AI</div>
                <div class="bubble ai">
                  <div class="mode-tag">{mode_info['icon']} {mode_info['label']}</div><br>
                  {rendered}
                </div>
                <div class="msg-time">{ts}</div>
              </div>
            </div>
            <script>
              setTimeout(() => {{
                if (typeof renderMathInElement !== 'undefined')
                  renderMathInElement(document.body);
              }}, 120);
            </script>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)   # end .chat-wrap


# ═══════════════════════════════════════════════════════════════
#  INPUT  +  FOOTER
# ═══════════════════════════════════════════════════════════════
prompt = st.chat_input(cur["ph"])

st.markdown(
    '<div class="input-footer">Somo AI · Usmonov Sodiq (Somo_AI) · Powered by Groq</div>',
    unsafe_allow_html=True
)


# ═══════════════════════════════════════════════════════════════
#  PROCESS INCOMING MESSAGE
# ═══════════════════════════════════════════════════════════════
if prompt and prompt.strip():
    user_text    = prompt.strip()
    active_mode  = st.session_state.mode
    mode_info    = MODES[active_mode]
    now          = get_time()

    # Save user message
    st.session_state.messages.append({
        "role"    : "user",
        "content" : user_text,
        "time"    : now,
        "mode"    : active_mode,
    })

    # Render user bubble immediately
    st.markdown(f"""
    <div class="msg-row user">
      <div class="av user">U</div>
      <div class="msg-body">
        <div class="msg-name">Siz</div>
        <div class="bubble user">{user_text}</div>
        <div class="msg-time">{now}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Typing indicator
    response_placeholder = st.empty()
    response_placeholder.markdown("""
    <div class="msg-row ai">
      <div class="av ai">S</div>
      <div class="msg-body">
        <div class="msg-name">Somo AI</div>
        <div class="bubble ai"><span class="t-cur"></span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Build API message list
    api_messages = [{"role": "system", "content": build_system_prompt(active_mode)}]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    # Stream response from Groq
    full_response = ""
    try:
        stream = client.chat.completions.create(
            model       = MODEL,
            messages    = api_messages,
            stream      = True,
            max_tokens  = 2048,
            temperature = 0.8,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_response += delta

            response_placeholder.markdown(f"""
            <div class="msg-row ai">
              <div class="av ai">S</div>
              <div class="msg-body">
                <div class="msg-name">Somo AI</div>
                <div class="bubble ai">
                  <div class="mode-tag">{mode_info['icon']} {mode_info['label']}</div><br>
                  {md_to_html(full_response)}<span class="t-cur"></span>
                </div>
              </div>
            </div>
            <script>
              setTimeout(() => {{
                if (typeof renderMathInElement !== 'undefined')
                  renderMathInElement(document.body);
              }}, 80);
            </script>
            """, unsafe_allow_html=True)

        # Final render — cursor removed, timestamp added
        response_placeholder.markdown(f"""
        <div class="msg-row ai">
          <div class="av ai">S</div>
          <div class="msg-body">
            <div class="msg-name">Somo AI</div>
            <div class="bubble ai">
              <div class="mode-tag">{mode_info['icon']} {mode_info['label']}</div><br>
              {md_to_html(full_response)}
            </div>
            <div class="msg-time">{get_time()}</div>
          </div>
        </div>
        <script>
          setTimeout(() => {{
            if (typeof renderMathInElement !== 'undefined')
              renderMathInElement(document.body);
          }}, 160);
        </script>
        """, unsafe_allow_html=True)

    except Exception as exc:
        err_msg = str(exc)
        if "rate_limit" in err_msg.lower():
            full_response = "⏳ Juda ko'p so'rov yuborildi. Bir daqiqa kuting va qayta urinib ko'ring."
        elif "auth" in err_msg.lower() or "api_key" in err_msg.lower():
            full_response = "❌ API kalit xato. GROQ_API_KEY ni tekshiring."
        elif "model" in err_msg.lower():
            full_response = f"❌ Model topilmadi. Iltimos boshqa model tanlang."
        else:
            full_response = f"❌ Xatolik yuz berdi: {err_msg}"

        response_placeholder.markdown(f"""
        <div class="msg-row ai">
          <div class="av ai">S</div>
          <div class="msg-body">
            <div class="msg-name">Somo AI</div>
            <div class="bubble ai">{full_response}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Save assistant message
    st.session_state.messages.append({
        "role"    : "assistant",
        "content" : full_response,
        "time"    : get_time(),
        "mode"    : active_mode,
    })
