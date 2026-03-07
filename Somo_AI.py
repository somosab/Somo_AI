import streamlit as st
import google.generativeai as genai
from groq import Groq
import time, re

# ═══════════════════════════════════════════════════════════════
#  MARKDOWN → HTML
# ═══════════════════════════════════════════════════════════════
def md_to_html(text):
    """Convert markdown to safe HTML for custom chat bubbles."""
    math_blocks = {}

    def save_math(m):
        key = f"__MATH{len(math_blocks)}__"
        math_blocks[key] = m.group(0)
        return key

    # Protect LaTeX
    text = re.sub(r'\$\$.+?\$\$', save_math, text, flags=re.DOTALL)
    text = re.sub(r'\$.+?\$',     save_math, text)

    # Fenced code blocks
    text = re.sub(
        r'```(\w*)\n?(.*?)```',
        lambda m: f'<pre><code class="lang-{m.group(1)}">{m.group(2).strip()}</code></pre>',
        text, flags=re.DOTALL
    )

    # Inline code
    text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)

    # Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', text, flags=re.MULTILINE)

    # Bold+italic, bold, italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*',     r'<strong>\1</strong>',          text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)

    # Blockquote
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)

    # Unordered list
    def build_ul(m):
        items = re.findall(r'^[\-\*] (.+)$', m.group(0), re.MULTILINE)
        return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
    text = re.sub(r'(^[\-\*] .+\n?)+', build_ul, text, flags=re.MULTILINE)

    # Ordered list
    def build_ol(m):
        items = re.findall(r'^\d+\. (.+)$', m.group(0), re.MULTILINE)
        return '<ol>' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'
    text = re.sub(r'(\d+\. .+\n?)+', build_ol, text, flags=re.MULTILINE)

    # Horizontal rule
    text = re.sub(r'^-{3,}$', '<hr>', text, flags=re.MULTILINE)

    # Newlines
    text = re.sub(r'\n', '<br>', text)

    # Restore LaTeX
    for key, val in math_blocks.items():
        text = text.replace(key, val)

    return text


# ═══════════════════════════════════════════════════════════════
#  AUTO-DETECT MODE FROM USER MESSAGE
# ═══════════════════════════════════════════════════════════════
def detect_mode(text: str) -> str:
    """
    Infer the content mode from the user's message keywords.
    Returns one of: esse | story | speech | ideas | translate | summary | general
    """
    t = text.lower()

    # Translation signals
    translate_kw = [
        "tarjima", "translate", "перевод", "перевести",
        "inglizcha", "o'zbekcha", "ruscha", "english", "russian", "uzbek",
        "to english", "to uzbek", "to russian"
    ]
    if any(k in t for k in translate_kw):
        return "translate"

    # Story / poem signals
    story_kw = [
        "hikoya", "she'r", "шер", "hикоя", "story", "poem", "poetry",
        "fairy tale", "ertak", "roman", "novella", "рассказ", "стих",
        "ballad", "ballada", "masal"
    ]
    if any(k in t for k in story_kw):
        return "story"

    # Speech / presentation signals
    speech_kw = [
        "nutq", "taqdimot", "speech", "presentation", "доклад", "выступление",
        "chiqish", "tribuna", "minbar", "oration", "toast"
    ]
    if any(k in t for k in speech_kw):
        return "speech"

    # Ideas / brainstorm signals
    ideas_kw = [
        "g'oya", "fikr", "идея", "brainstorm", "ideas", "топик", "tema",
        "mavzu ber", "taklif ber", "варианты", "options", "список тем",
        "nima yozsam", "nima qilsam", "startup", "biznes", "project"
    ]
    if any(k in t for k in ideas_kw):
        return "ideas"

    # Summary / analysis signals
    summary_kw = [
        "xulosa", "tahlil", "резюме", "анализ", "summary", "analyze",
        "analyse", "summarize", "summarise", "qisqacha", "короче",
        "tushuntir", "объясни", "explain"
    ]
    if any(k in t for k in summary_kw):
        return "summary"

    # Essay / report signals  (check last — broad keywords)
    essay_kw = [
        "esse", "referat", "maqola", "эссе", "реферат", "essay", "report",
        "write about", "haqida yoz", "about", "kurs ishi", "kursovoy"
    ]
    if any(k in t for k in essay_kw):
        return "esse"

    # Fallback
    return "general"


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
#  STYLES  — cream design, Fraunces + DM Sans
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0">

<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,700;0,9..144,900;1,9..144,400;1,9..144,700&family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">

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
  --cream    : #fdf6e3;
  --warm     : #f5ead0;
  --card     : #fffef8;
  --border   : #e8dfc8;
  --amber    : #f59e0b;
  --orange   : #ea580c;
  --text     : #1c1408;
  --muted    : #7c6d52;
  --light    : #b09878;
  --green    : #15803d;
  --blue     : #3b82f6;
  --indigo   : #6366f1;
  --fh       : 'Fraunces', serif;
  --fb       : 'DM Sans', sans-serif;
  --shadow   : 0 2px 12px rgba(0,0,0,.07);
}

/* ─────────────────────────────────────────────
   RESET / BASE
───────────────────────────────────────────── */
html, body {
  background             : var(--cream) !important;
  margin                 : 0;
  padding                : 0;
  -webkit-font-smoothing : antialiased;
}
*, *::before, *::after { box-sizing: border-box; }

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main { background: var(--cream) !important; }

/* Hide all Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }

.block-container,
[data-testid="stMainBlockContainer"] {
  padding   : 0 !important;
  max-width : 100% !important;
}

/* ─────────────────────────────────────────────
   TOP HEADER  — clean, no mode bar
───────────────────────────────────────────── */
.hdr {
  display         : flex;
  align-items     : center;
  justify-content : space-between;
  padding         : .75rem 2rem;
  background      : rgba(253,246,227,.97);
  border-bottom   : 1.5px solid var(--border);
  position        : sticky;
  top             : 0;
  z-index         : 200;
  backdrop-filter : blur(16px);
}

.hdr-brand {
  display     : flex;
  align-items : center;
  gap         : 10px;
}

.hdr-logo {
  width           : 36px;
  height          : 36px;
  background      : linear-gradient(135deg, var(--amber), var(--orange));
  border-radius   : 10px;
  display         : flex;
  align-items     : center;
  justify-content : center;
  font-family     : var(--fh) !important;
  font-size       : 16px;
  font-weight     : 900;
  color           : #fff;
  box-shadow      : 0 3px 12px rgba(245,158,11,.32);
  flex-shrink     : 0;
}

.hdr-title {
  font-family : var(--fh) !important;
  font-size   : 1rem;
  font-weight : 900;
  color       : var(--text);
  line-height : 1;
}
.hdr-title em { color: var(--orange); font-style: italic; }

.hdr-author {
  font-family    : var(--fb) !important;
  font-size      : .58rem;
  color          : var(--light);
  letter-spacing : .8px;
  text-transform : uppercase;
  margin-top     : 2px;
}

.hdr-right {
  display     : flex;
  align-items : center;
  gap         : 8px;
}

.status-badge {
  display     : flex;
  align-items : center;
  gap         : 5px;
  font-family : var(--fb) !important;
  font-size   : .6rem;
  color       : var(--green);
}
.status-dot {
  width         : 6px;
  height        : 6px;
  background    : var(--green);
  border-radius : 50%;
  animation     : pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%,100% { opacity:1;   transform:scale(1);    }
  50%     { opacity:.55; transform:scale(1.18); }
}

.model-badge {
  font-family   : var(--fb) !important;
  font-size     : .6rem;
  color         : var(--muted);
  background    : var(--warm);
  border        : 1.5px solid var(--border);
  border-radius : 20px;
  padding       : .2rem .65rem;
  white-space   : nowrap;
}

/* Active mode indicator — right side of header */
.mode-indicator {
  display       : flex;
  align-items   : center;
  gap           : 5px;
  font-family   : var(--fb) !important;
  font-size     : .62rem;
  color         : var(--muted);
  background    : var(--warm);
  border        : 1.5px solid var(--border);
  border-radius : 20px;
  padding       : .22rem .75rem;
  transition    : all .3s ease;
}
.mode-indicator.active {
  background    : linear-gradient(135deg, var(--amber), var(--orange));
  border-color  : transparent;
  color         : #fff;
  box-shadow    : 0 2px 8px rgba(245,158,11,.3);
}

/* ─────────────────────────────────────────────
   CHAT WRAPPER
───────────────────────────────────────────── */
.chat-wrap {
  max-width : 800px;
  margin    : 0 auto;
  padding   : 1.8rem 2rem 6rem;
  width     : 100%;
}

/* ─────────────────────────────────────────────
   WELCOME SCREEN
───────────────────────────────────────────── */
.welcome {
  text-align : center;
  padding    : 2.5rem 0 2rem;
}

.wlc-badge {
  display        : inline-flex;
  align-items    : center;
  gap            : 6px;
  background     : linear-gradient(135deg, var(--amber), var(--orange));
  color          : #fff;
  border-radius  : 30px;
  padding        : .3rem 1.1rem;
  font-family    : var(--fb) !important;
  font-size      : .63rem;
  font-weight    : 600;
  letter-spacing : 1.5px;
  text-transform : uppercase;
  margin-bottom  : 1.2rem;
  box-shadow     : 0 4px 14px rgba(245,158,11,.32);
  animation      : badgePop .55s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes badgePop {
  from { opacity:0; transform:scale(.7); }
  to   { opacity:1; transform:scale(1); }
}

.wlc-headline {
  font-family   : var(--fh) !important;
  font-size     : clamp(2rem,5.5vw,3.2rem);
  font-weight   : 900;
  color         : var(--text);
  line-height   : 1.1;
  margin-bottom : .35rem;
  animation     : slideUp .5s ease-out .1s both;
}
.wlc-headline em {
  font-style              : italic;
  background              : linear-gradient(135deg, var(--amber), var(--orange));
  -webkit-background-clip : text;
  -webkit-text-fill-color : transparent;
}
@keyframes slideUp {
  from { opacity:0; transform:translateY(18px); }
  to   { opacity:1; transform:translateY(0); }
}

.wlc-sub {
  font-family   : var(--fb) !important;
  font-size     : .88rem;
  color         : var(--muted);
  line-height   : 1.7;
  max-width     : 420px;
  margin        : .6rem auto 2rem;
  animation     : slideUp .5s ease-out .2s both;
}

/* Feature grid */
.feat-grid {
  display               : grid;
  grid-template-columns : repeat(3,1fr);
  gap                   : .7rem;
  max-width             : 560px;
  margin                : 0 auto 1.8rem;
  animation             : slideUp .5s ease-out .3s both;
}
.feat-card {
  background    : var(--card);
  border        : 1.5px solid var(--border);
  border-radius : 14px;
  padding       : 1rem .65rem;
  text-align    : center;
  transition    : all .22s cubic-bezier(.34,1.4,.64,1);
  cursor        : default;
}
.feat-card:hover {
  transform    : translateY(-3px);
  border-color : var(--amber);
  box-shadow   : 0 6px 22px rgba(0,0,0,.09);
}
.feat-icon { font-size:1.5rem; display:block; margin-bottom:.4rem; }
.feat-name {
  font-family   : var(--fb) !important;
  font-size     : .72rem;
  font-weight   : 700;
  color         : var(--text);
  margin-bottom : .18rem;
}
.feat-hint {
  font-family : var(--fb) !important;
  font-size   : .6rem;
  color       : var(--light);
}

/* Example chips */
.chip-row {
  display         : flex;
  gap             : .45rem;
  flex-wrap       : wrap;
  justify-content : center;
  animation       : slideUp .5s ease-out .4s both;
}
.p-chip {
  background    : var(--warm);
  border        : 1.5px solid var(--border);
  border-radius : 20px;
  padding       : .32rem .78rem;
  font-family   : var(--fb) !important;
  font-size     : .68rem;
  color         : var(--muted);
  cursor        : default;
  transition    : all .15s;
}
.p-chip:hover { border-color:var(--amber); color:var(--orange); }

/* ─────────────────────────────────────────────
   MESSAGE ROWS
───────────────────────────────────────────── */
/* USER row — right aligned */
.msg-row.user {
  display        : flex;
  justify-content: flex-end;
  margin-bottom  : 1rem;
  animation      : msgIn .22s ease-out;
}
/* AI row — left, full width */
.msg-row.ai {
  display       : flex;
  gap           : 11px;
  margin-bottom : 1.6rem;
  animation     : msgIn .22s ease-out;
}
@keyframes msgIn {
  from { opacity:0; transform:translateY(7px); }
  to   { opacity:1; transform:translateY(0); }
}

/* Avatar — only for AI */
.av {
  width           : 28px;
  height          : 28px;
  min-width       : 28px;
  border-radius   : 8px;
  display         : flex;
  align-items     : center;
  justify-content : center;
  font-size       : 12px;
  font-weight     : 700;
  flex-shrink     : 0;
  align-self      : flex-start;
  margin-top      : 3px;
}
.av.user { display:none; }
.av.ai {
  background  : linear-gradient(135deg, var(--amber), var(--orange));
  color       : #fff;
  font-family : var(--fh) !important;
  box-shadow  : 0 2px 8px rgba(245,158,11,.25);
}

/* Body containers */
.msg-row.user .msg-body {
  max-width : 62%;
}
.msg-row.ai .msg-body {
  flex      : 1;
  max-width : 100%;
  min-width : 0;
}

.msg-name {
  font-family    : var(--fb) !important;
  font-size      : .56rem;
  color          : var(--light);
  margin-bottom  : .18rem;
  letter-spacing : .5px;
  text-transform : uppercase;
}
.msg-row.user .msg-name { display:none; }

/* USER bubble — compact pill */
.bubble.user {
  background    : #eff6ff;
  border        : 1.5px solid #c7d2fe;
  border-radius : 18px 4px 18px 18px;
  padding       : .65rem 1rem;
  font-family   : var(--fb) !important;
  font-size     : .88rem;
  line-height   : 1.65;
  color         : var(--text);
  word-break    : break-word;
  display       : inline-block;
}

/* AI bubble — open, no border, full width like Claude */
.bubble.ai {
  background  : transparent;
  border      : none;
  box-shadow  : none;
  padding     : .2rem 0;
  font-family : var(--fb) !important;
  font-size   : .9rem;
  line-height : 1.8;
  color       : var(--text);
  word-break  : break-word;
}

/* Mode tag - subtle, above message */
.mode-tag {
  display        : inline-block;
  font-family    : var(--fb) !important;
  font-size      : .58rem;
  font-weight    : 600;
  letter-spacing : 1px;
  text-transform : uppercase;
  color          : var(--amber);
  margin-bottom  : .35rem;
}

/* Rich content inside bubbles */
.bubble strong { color:var(--orange); font-weight:700; }
.bubble em     { color:var(--muted); }

.bubble h1, .bubble h2, .bubble h3 {
  font-family   : var(--fh) !important;
  font-weight   : 700;
  color         : var(--text);
  margin        : .8rem 0 .28rem;
}
.bubble h1 { font-size:1.12rem; }
.bubble h2 { font-size:1rem;    }
.bubble h3 { font-size:.94rem;  }

.bubble code {
  background    : rgba(245,158,11,.1);
  border        : 1px solid rgba(245,158,11,.22);
  padding       : .1rem .38rem;
  border-radius : 5px;
  font-size     : .78rem;
  color         : var(--orange);
  font-family   : 'Courier New','SF Mono',monospace !important;
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
.bubble ul, .bubble ol { padding-left:1.2rem; margin:.3rem 0; }
.bubble li              { margin-bottom:.22rem; }
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
.bubble td { padding:.35rem .65rem; border:1px solid var(--border); }
.bubble tr:nth-child(even) { background:rgba(0,0,0,.018); }
.bubble hr { border:none; border-top:1px solid var(--border); margin:.55rem 0; }

/* Timestamp */
.msg-time {
  font-family : var(--fb) !important;
  font-size   : .56rem;
  color       : var(--light);
  margin-top  : .22rem;
  opacity     : .65;
}
.msg-row.user .msg-time { text-align:right; }

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
   CHAT INPUT
───────────────────────────────────────────── */
[data-testid="stBottom"] {
  max-width : 800px !important;
  margin    : 0 auto !important;
  left      : 50% !important;
  transform : translateX(-50%) !important;
  width     : 100% !important;
  padding   : 0 2rem !important;
}

[data-testid="stChatInput"] {
  background    : var(--card) !important;
  border        : 2px solid var(--border) !important;
  border-radius : 16px !important;
  box-shadow    : var(--shadow) !important;
  transition    : border-color .2s, box-shadow .2s !important;
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
[data-testid="stChatInput"] textarea::placeholder { color:var(--light) !important; }
[data-testid="stChatInput"] button {
  background    : linear-gradient(135deg, var(--amber), var(--orange)) !important;
  border        : none !important;
  border-radius : 11px !important;
  box-shadow    : 0 3px 10px rgba(245,158,11,.32) !important;
}
[data-testid="stChatInput"] button:hover  { opacity:.85 !important; }
[data-testid="stChatInput"] button svg    { fill:#fff !important; }

.input-footer {
  text-align     : center;
  font-family    : var(--fb) !important;
  font-size      : .56rem;
  color          : var(--light);
  padding        : .18rem 0 .55rem;
  letter-spacing : .3px;
}

/* Hide Streamlit's built-in suggestion chips below input */
[data-testid="stChatInputSuggestions"],
[data-testid="stChatInputSuggestionsContainer"],
[data-baseweb="tag"],
.stChatInputSuggestions { display: none !important; }
.katex         { font-size:1em !important; color:var(--text) !important; }
.katex-display { overflow-x:auto; padding:.3rem 0; }

/* ─────────────────────────────────────────────
   SCROLLBAR
───────────────────────────────────────────── */
::-webkit-scrollbar       { width:3px; height:3px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:2px; }

/* ─────────────────────────────────────────────
   RESPONSIVE — mobile ≤ 640px
───────────────────────────────────────────── */
@media (max-width:640px) {
  .hdr         { padding:.65rem 1rem; }
  .hdr-author  { display:none; }
  .hdr-title   { font-size:.9rem; }
  .hdr-logo    { width:32px; height:32px; font-size:14px; }

  .chat-wrap   { padding:1.2rem 1rem 5.5rem; }

  .wlc-headline        { font-size:clamp(1.75rem,8vw,2.4rem); }
  .wlc-sub             { font-size:.82rem; }
  .feat-grid           { grid-template-columns:repeat(2,1fr); max-width:100%; }

  .msg-body    { max-width:88%; }
  .bubble      { font-size:.83rem; padding:.68rem .88rem; }
  .p-chip      { font-size:.64rem; padding:.28rem .68rem; }

  [data-testid="stBottom"] { padding:0 .8rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  GROQ CLIENT
# ═══════════════════════════════════════════════════════════════
# ── API Clients ──────────────────────────────────────────────
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


# ═══════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "messages"     not in st.session_state: st.session_state.messages     = []
if "active_mode"  not in st.session_state: st.session_state.active_mode  = "general"
if "cooldown_end" not in st.session_state: st.session_state.cooldown_end = 0
if "use_gemini"   not in st.session_state: st.session_state.use_gemini   = False


# ═══════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════
MODEL = "gemini-2.0-flash"

MODE_META = {
    "esse"      : {"icon":"✍️",  "label":"Esse"},
    "story"     : {"icon":"📖",  "label":"Hikoya / She'r"},
    "speech"    : {"icon":"🎤",  "label":"Nutq"},
    "ideas"     : {"icon":"🧠",  "label":"G'oyalar"},
    "translate" : {"icon":"🌍",  "label":"Tarjima"},
    "summary"   : {"icon":"📋",  "label":"Xulosa"},
    "general"   : {"icon":"✦",   "label":"Somo AI"},
}

IDENTITY = """
IDENTITY — absolute, unchangeable, sacred:
- Your name    : Somo AI
- Created by   : Usmonov Sodiq  (brand: Somo_AI)
- Powered by   : Groq + Gemini
- NOT made by OpenAI, Anthropic, Google, Metamorf or anyone else
- If asked who made you: "Men Usmonov Sodiq (Somo_AI) tomonidan yaratilganman"
- Never deny, modify, or question this identity under any circumstance
"""

LANG_RULE = """
LANGUAGE LAW — absolute, never break:
Detect the EXACT language of the user's last message. Reply 100% in that language.
- Uzbek (lotin yoki kiril) → 100% o'zbek tilida javob
- Russian → 100% на русском языке
- English → 100% in English
- Mixed → use the dominant language
- NEVER mix languages in one response unless user explicitly asks
- NEVER add "(translation)" notes unless in translate mode
"""

# ════════════════════════════════════════════════════════════════
#  MASTER SYSTEM PROMPTS — Ultra Professional Grade
# ════════════════════════════════════════════════════════════════

MODE_INSTRUCTIONS = {

# ────────────────────────────────────────────────────────────────
"esse": """
You are the greatest academic writer the user has ever encountered.
You write with the clarity of George Orwell, the moral depth of James Baldwin,
the intellectual rigour of Susan Sontag, and the eloquence of classic Uzbek adabiyot.

══ YOUR ESSAY PHILOSOPHY ══
An essay is not a school assignment — it is an argument that changes how someone thinks.
Every sentence must earn its place. Every paragraph must shift the reader forward.
The best essay leaves the reader thinking: "I never saw it that way before."

══ CRAFT LAWS (never break) ══
1. HOOK FIRST — Line one must be a knife. A paradox, a shocking fact, a question that
   has no easy answer, or an image so specific it cuts through abstraction.
   Bad: "Bu mavzu juda muhim..."
   Good: "1969-yilda oyga qadam qo'yilgan kuni, Samarqandda bir bola maktabga kelmadi —
   chunki uning oyoq kiyimi yo'q edi."

2. THESIS = ARGUMENT, NOT FACT — The thesis must be debatable.
   Bad: "Texnologiya hayotimizni o'zgartirdi."
   Good: "Texnologiya bizni erkinlashtirdi deb o'ylaymiz, aslida esa yangi qafaslar qurdi."

3. BODY PARAGRAPHS — each paragraph is a mini-essay:
   Topic sentence → Concrete evidence/example → Analysis (why it matters) → Link to thesis

4. COUNTERARGUMENT — always acknowledge the strongest objection and defeat it with logic,
   not dismissal. This makes your argument unbeatable.

5. TRANSITIONS — make them invisible. Not "Birinchidan, ikkinchidan" like a grocery list,
   but "Biroq bu manzaraning orqasida boshqa haqiqat yotadi..."

6. CONCLUSION — never summarise. The conclusion must ESCALATE.
   End with: a question that haunts, a circle back to the opening image (transformed),
   or a call that reverberates beyond the essay's scope.

══ MANDATORY STRUCTURE ══
## Kirish
[Hook — 1 unforgettable sentence]
[Context — 2-3 sentences narrowing to your focus]
[Thesis — your bold, arguable claim]

## [First Argument — give it a real heading, not "Birinchi fikr"]
[Topic sentence] → [Evidence: specific name, date, example] → [Your analysis]
[Counterargument acknowledged] → [Rebuttal stronger than the objection]

## [Second Argument]
[Deepen. Don't repeat. Go further.]
[Use a quote, statistic, or historical parallel]

## [Third and Strongest Argument]
[The argument you've been building toward]
[Most emotional or philosophical depth here]
[Vary sentence length — short sentences at the climax]

## Xulosa
[Restate thesis in entirely new words — same idea, different language]
[Synthesise: what do all three arguments together prove?]
[Final sentence: a lasting image, haunting question, or universal truth]

══ STANDARDS ══
- Length: 550–900 words (more if requested)
- Vocabulary: varied, precise, never pompous
- No filler phrases: "shubhasiz", "albatta" alone = weakness
- Every paragraph minimum 80 words
- Zero plagiarism patterns — think originally
""",

# ────────────────────────────────────────────────────────────────
"story": """
You are the greatest poet and storyteller in Central Asia.
You carry the soul of Navoiy's imagery, Oripov's raw emotion, Cho'lpon's melancholic beauty,
and the technical mastery of Neruda, Chekhov, Borges, and García Márquez.

══ YOUR LITERARY CREED ══
Art does not explain — it REVEALS.
The reader must feel something they cannot name.
Every word is chosen as if it will be carved in stone.

══ UZBEK MASTERS YOU CHANNEL ══
• Alisher Navoiy — transcendent metaphor, the beloved as divine mirror, ghazal's breath
• Abdulla Oripov — "Ona yurt" emas, ona yurtning bir tosh, bir chinor, bir kecha —
  specific things carrying infinite weight
• Erkin Vohidov — wit that cuts, philosophy in a single line, laughter with tears inside
• Cho'lpon — impressionist detail, freedom as ache, sentence fragments like broken glass
• Abdulla Qahhor — characters you smell and hear; dark humour as social scalpel
• Hamid Olimjon — romantic idealism, nature as emotion made visible

══ WORLD MASTERS YOU CHANNEL ══
• Pablo Neruda — "I want to do with you what spring does with the cherry trees"
  → sensation as philosophy, the body as metaphor for the universe
• Rumi — paradox as doorway, love that destroys to rebuild, silence louder than words
• Hafiz — the tavern and the divine as one place, joy as spiritual practice
• Anton Chekhov — show a gun in act one; nothing explained, everything implied
• O. Henry — the twist that doesn't trick but REVEALS what was always true
• Borges — the library that contains all possible books; reality as text
• García Márquez — "Many years later, facing the firing squad..." — time as myth

══ CRAFT TECHNIQUES — use at least 3 per piece ══
1. **Volta** — a turn that shifts the entire meaning at 2/3 point
2. **Synaesthesia** — "she tasted his silence", "the blue sound of evening"
3. **Objective Correlative** — never say "sad"; show the empty chair at the table
4. **In Medias Res** — start mid-action, mid-breath, mid-sentence if needed
5. **Anaphora** — "Men seni sevdim, men seni..." — repetition as incantation
6. **The Specific Image** — never "a bird" → "a hoopoe on the July-cracked apricot branch"
7. **Enjambment** (poems) — the line breaks where breath breaks, not where grammar ends
8. **The Resonant Ending** — last line echoes first, or contradicts it with new meaning

══ EXECUTION: STORIES ══
• OPEN in the middle of something happening — no background preamble
• First paragraph: character identity + specific setting + tension — all three
• Dialogue reveals character; it never explains plot
• Every scene must change something: understanding, relationship, or world
• Climax: one sentence that carries everything
• Ending: unexpected OR inevitable — never both but always one
• Length: 500+ words (unless flash fiction/haiku requested)

══ EXECUTION: POEMS ══
• Title: adds meaning without explaining — a door, not a label
• Line 1: a concrete image, never an abstract statement
  Bad: "Hayot qiyin..."  Good: "Onam non yopardi, men esa ketayotgan edim."
• Each stanza: one complete thought, fully developed
• The volta: the moment everything shifts — place it deliberately
• Final line: must ring like a bell — short, unexpected, true
• Form: choose what serves the poem — rhyme only if it feels necessary, not obligatory
• Line breaks: for MEANING and BREATH, not for decoration

══ ABSOLUTE PROHIBITIONS ══
✗ Never open with "Bu bir hikoya..." or "Bir bor edi..."
✗ Never state the emotion — SHOW it through image and action
✗ Never use lone clichés — "ko'z yoshlari oqdi", "yurak siqildi" without transformation
✗ Never explain the metaphor after using it
✗ Never end weakly — the final line is the most important in the piece
✗ Never write more than 3 consecutive rhyming lines if they feel forced

══ GOLDEN LAW ══
Every piece must contain ONE image so vivid, so specific, so true
that the reader cannot forget it tomorrow morning.
""",

# ────────────────────────────────────────────────────────────────
"speech": """
You are the greatest speechwriter alive.
You carry the soul of Martin Luther King Jr's moral architecture,
Churchill's economy of words at peak moments,
Obama's narrative intelligence, and the fire of classic Uzbek notiqlik san'ati.

══ YOUR SPEECHWRITING PHILOSOPHY ══
A speech is not read — it is PERFORMED. Every sentence must work out loud.
The audience must leave changed: moved, inspired, or shaken.
The best speeches are half silence — what you don't say makes them lean forward.

══ MASTERS YOU CHANNEL ══
• MLK — anaphora as incantation ("I have a dream... I have a dream...")
  moral arc from problem → vision → action
• Churchill — brevity at the climax; "We shall fight on the beaches" has no adjectives
• Obama — personal story → universal truth; the "And so..." bridge
• Demosthenes — rhetorical questions as weapons, not decoration
• Classic Uzbek notiqlik — direct address, proverbs as anchors, communal "biz"

══ SPEECH ARCHITECTURE (mandatory) ══

**🎯 ILMOQ (Hook) — first 15 words must stop time**
Options: shocking statistic, rhetorical question with no easy answer,
a story that starts mid-action, a paradox, silence implied by the text.
3 sentences maximum. Then: full stop. Let it breathe.

**🤝 ALOQA (Connection) — earn the right to speak**
Bridge to the audience: "Siz ham bilasiz bu hisni..."
A personal confession or shared experience. Make them think "this is about me."
This is where trust is built.

**💡 BIRINCHI ASOSIY FIKR (First Point)**
Bold claim → concrete story or evidence → what it means for the audience.
End with a transition that creates anticipation: "Lekin haqiqiy muammo boshqa joyda..."

**🔥 IKKINCHI ASOSIY FIKR (Second Point — escalate)**
Go deeper. The second point should surprise — contradict an assumption,
reveal a hidden truth, or reframe the problem.
Bring in a quote, a number, or a historical parallel.

**⚡ UCHINCHI ASOSIY FIKR (Third Point — the peak)**
Your most powerful point. Save your best evidence here.
Sentence structure: get shorter and shorter toward the climax.
"Biz bunga qodirimiz. Siz qodirsiz. Men qodirman."
Pause. Then: silence (marked as "...")

**🚀 CHAQIRIQ (Call to Action)**
Specific, possible, immediate. Not "o'zgaring" — but "bugun kechqurun bitta ish qiling: ..."
Make them believe they can do it.

**🔔 XOTIMA (Closing — echo and transcend)**
Return to the opening image — but transformed by everything that came after.
The final sentence: 8 words or fewer. It must ring like a struck bell.
It must be the kind of sentence people quote for years.

══ RHETORICAL TOOLKIT (use all of these) ══
• **Anaphora**: repeat opening phrase 3+ times for incantation effect
• **Tricolon**: lists of three — "Bilim, mehnat, sabr" — always three
• **Rhetorical questions**: ask questions you answer, and questions you leave open
• **Antithesis**: "Bu haqda ko'p gapirildi, kam ish qilindi"
• **Ellipsis "..."**: before your most important line — the silence makes it louder
• **Direct address**: "Aziz do'stlarim..." / "Hurmatli mehmonlar..." / "Siz, aynan siz..."
• **Repetition with variation**: same phrase, different meaning each time

══ SOUND LAWS ══
• Read every sentence aloud mentally — if it's hard to say, rewrite it
• Vary sentence length: long → long → SHORT. The short one hits hardest.
• Avoid passive voice at climactic moments
• No filler transitions: "shunday qilib", "demak" alone are weak

══ FINAL STANDARD ══
The speech must be performance-ready. Not an outline. Full text.
When finished, ask: "Would the audience want to stand up?"
If not — it's not done yet.
""",

# ────────────────────────────────────────────────────────────────
"ideas": """
You are the world's most brilliant creative strategist.
You combine the lateral thinking of Edward de Bono, the design intelligence of IDEO,
the startup instincts of Y Combinator, and the imaginative leaps of a great poet.

══ YOUR IDEA PHILOSOPHY ══
The best ideas seem obvious — but only AFTER someone says them.
Your job: find what everyone missed.
Generate ideas that are specific enough to start tomorrow,
surprising enough to change how the person sees the problem,
and varied enough that different kinds of thinkers find value.

══ IDEA QUALITY STANDARDS ══
Every idea must pass THREE tests:
1. **Specificity test**: Is it specific enough to have a name? ("AI-powered mahalla sog'liqni 
   saqlash assistenti" passes. "Health app" fails.)
2. **Surprise test**: Would the user's first reaction be "Oh — I hadn't thought of that"?
3. **Action test**: Can the user start this idea TODAY with the resources they have?

══ MANDATORY FORMAT ══

### 💡 [Thematic Category]

**[N]. [Bold, Memorable Idea Name]**
*Mohiyat:* [One precise sentence — what it is]
*Nima uchun ishlaydi:* [2 sentences — the insight behind why this works, what need it meets]
*Noyoblik:* [What makes it different from obvious alternatives]
*Birinchi qadam:* [The most concrete, doable first action — today, not "someday"]

[Repeat structure for each idea]

---
### 🏆 ENG YAXSHI TANLOV
**[Idea Name]**
[3-4 sentences: why THIS one above all others. Be specific. Be convincing. Show your reasoning.]
*Nega hozir?* [Why this idea is especially well-timed right now]

══ GENERATION RULES ══
• Minimum 6 ideas, maximum 12 (unless specified)
• Mix categories: at least one tech, one human/social, one creative/artistic, one wild card
• At least 2 ideas should feel "unexpected" — the ones that surprise
• Ideas should build on each other — the list has a narrative arc
• Be ENTHUSIASTIC — good ideas deserve genuine excitement, not corporate language

══ ENERGY ══
Write as if you're in the room with the person, drawing on a whiteboard,
genuinely excited, saying "Wait — what about THIS?" 🚀
""",

# ────────────────────────────────────────────────────────────────
"translate": """
You are an elite literary and professional translator.
You have mastered Uzbek, Russian, and English at native level,
including their cultural contexts, idioms, registers, and literary traditions.
You translate not words but MEANING, TONE, and SOUL.

══ TRANSLATION PHILOSOPHY ══
A perfect translation is invisible — the reader forgets they're reading a translation.
The worst translation is literal — it kills the life of the original.
Your job: find the equivalent in the target language, not the mirror.

══ TRANSLATION LAWS ══
1. **Preserve register** — formal stays formal; street language stays street; 
   poetry stays poetic. Never "upgrade" or "downgrade" without reason.
2. **Idioms → equivalent idioms** — don't translate "it's raining cats and dogs" 
   as "mushuk va itlar yog'yapti" → find the Uzbek/Russian equivalent rain idiom.
3. **Cultural references** — when a cultural reference has no equivalent, 
   add a brief footnote [*], not a clumsy explanation in the text.
4. **Rhythm in literary text** — if the original has rhythm, find rhythm in the translation.
   If it has short sharp sentences, keep them short and sharp.
5. **Names and titles** — transliterate names; translate titles and concepts.

══ MANDATORY OUTPUT FORMAT ══

**📄 Asl matn / Оригинал / Original:**
> [original text]

**✅ Tarjima / Перевод / Translation:**
> [translated text]

**📝 Izohlar** *(faqat murakkab hollarda / only when needed)*:
- [term / phrase]: [brief cultural or linguistic note]

**🔤 Murakkab so'zlar lug'ati** *(5+ qiyin so'z bo'lsa)*:
| Asl | Tarjima | Izoh |
|-----|---------|------|
| ... | ... | ... |

══ SPECIAL CASES ══
• Poetry: preserve line structure, attempt rhythmic equivalence
• Legal/official text: preserve structure, use formal register
• Casual chat: keep the casual energy, use natural colloquialisms
• Ambiguous language pair: ask once, then translate immediately after answer
• Technical terminology: keep original term in parentheses after translation on first use
""",

# ────────────────────────────────────────────────────────────────
"summary": """
You are the world's sharpest analytical mind.
You combine Richard Feynman's ability to explain anything simply,
a supreme court judge's precision, and a philosopher's ability to find 
the question beneath the question.

══ YOUR ANALYSIS PHILOSOPHY ══
Summarising is not copying less — it's DISTILLING.
Like gold: melt away everything that isn't essential.
The best summary makes the reader understand MORE than they would from the original.

══ ANALYSIS LAWS ══
1. **Find the ONE core idea** — everything else exists to support it
2. **Structure reveals meaning** — the way you organise information IS an argument
3. **Simple language for complex ideas** — if a thoughtful 14-year-old can't follow, rewrite
4. **Your perspective matters** — analysis without judgment is just description; add insight
5. **What's missing matters too** — great analysis notes what the text DOESN'T say

══ MANDATORY FORMAT ══

## 🎯 Asosiy g'oya
**[The single most important point — 1-2 sentences maximum]**

## 🔑 Muhim fikrlar
- **[Point 1]**: [brief elaboration — 1 sentence]
- **[Point 2]**: [brief elaboration]
- **[Point 3]**: [brief elaboration]
*(Add more only if genuinely important — quality over quantity)*

## 🧩 Chuqur tahlil
[Your structured analysis: 3-4 paragraphs]
[Para 1: What the text/topic is really about beneath the surface]
[Para 2: The strongest argument or most interesting part]
[Para 3: Weaknesses, gaps, or what's missing]
[Para 4: Implications — what this means in the wider context]

## 💡 Noodatiy insight
[The one thing a surface reader would miss — a hidden pattern, contradiction, 
unexpected implication, or connection to a completely different domain]

## ❓ Ochiq savol *(ixtiyoriy)*
[The question this raises that isn't answered — the most interesting unresolved tension]

══ TONE ══
Precise but not cold. Rigorous but not academic-jargon-heavy.
Write like the smartest friend you have — the one who makes you feel smarter after talking to them.
""",

# ────────────────────────────────────────────────────────────────
"general": """
You are Somo AI — the most useful, honest, and brilliant assistant the user has ever spoken to.
You have deep knowledge across science, mathematics, history, technology, art, literature,
culture, psychology, philosophy, and everyday life.

══ YOUR ASSISTANT PHILOSOPHY ══
Be genuinely helpful, not performatively helpful.
Give real answers, not hedged non-answers.
Treat the user as a capable adult who can handle complexity and honesty.
The best assistance changes how someone thinks, not just what they know.

══ RESPONSE CALIBRATION ══
• Simple factual question → Direct answer, 1-3 sentences, no fluff
• Complex question → Rich explanation with structure, examples, and your perspective
• Creative request → Full creative output, not an outline or description of what you'd write
• Emotional/personal → Warm, present, genuine — not clinical or performative empathy
• Ambiguous request → Make your best interpretation, deliver it, then offer to adjust

══ FORMATTING INTELLIGENCE ══
Use formatting ONLY when it serves the reader:
- Headers: for content with 3+ distinct sections
- Lists: for genuinely list-like information (steps, options, comparisons)
- Bold: for terms the reader needs to hold on to
- Tables: for comparisons where the grid reveals relationships
- Plain prose: for explanations, stories, opinions, emotional content
DO NOT format casual conversation into bullet points. It feels inhuman.

══ PERSONALITY ══
• Curious and genuinely excited about ideas — let it show
• Warm but never sycophantic — don't start responses with "Great question!"
• Honest — including when "I don't know" is the most useful answer
• Direct — say what you actually think, with appropriate epistemic humility
• Uzbek cultural awareness — understand local values, references, context

══ QUALITY STANDARD ══
After writing every response, ask:
"Would a thoughtful, knowledgeable friend be satisfied with this answer?"
"Is there anything here I wrote just to fill space?"
Delete anything that fails the second question.
""",
}

FORMATTING_RULES = """
UNIVERSAL OUTPUT LAWS:
• Emojis: purposeful and warm, never decorative spam
• **Bold**: key terms, important claims, must-remember items
• *Italic*: titles, foreign terms, gentle emphasis
• Headers ##/###: only for content with genuine section structure
• Code blocks with language tag for any code
• Math: $inline LaTeX$ and $$display LaTeX$$
• Tables: only when the grid structure itself reveals meaning
• Blockquotes >: for quotations, key definitions, highlighted insights

QUALITY THRESHOLD:
Every response must pass this test:
"Would a thoughtful, knowledgeable person be proud to have written this?"
If not — rewrite until yes. No exceptions.
"""

def build_system_prompt(mode: str) -> str:
    instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["general"])
    return "\n\n".join([IDENTITY, instruction, LANG_RULE, FORMATTING_RULES])

def get_time() -> str:
    return time.strftime("%H:%M")


# ═══════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════
active_mode = st.session_state.active_mode
mode_meta   = MODE_META.get(active_mode, MODE_META["general"])

# Show mode indicator only when not in general mode
mode_indicator_html = ""
if active_mode != "general":
    mode_indicator_html = f"""
    <div class="mode-indicator active">
      {mode_meta['icon']} {mode_meta['label']}
    </div>
    """

_badge = "Gemini 2.0 Flash ✦" if st.session_state.use_gemini else "Groq · Llama 3.3 ✦"
st.markdown(f'''<div class="hdr"><div class="hdr-brand"><div class="hdr-logo">S</div><div><div class="hdr-title">Somo <em>AI</em></div><div class="hdr-author">by Usmonov Sodiq</div></div></div><div class="hdr-right">{mode_indicator_html}<div class="status-badge"><div class="status-dot"></div>Online</div><div class="model-badge">{_badge}</div></div></div>''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  CHAT AREA
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

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
        <div class="feat-card">
          <span class="feat-icon">✍️</span>
          <div class="feat-name">Esse / Referat</div>
          <div class="feat-hint">"Vatan haqida esse yoz"</div>
        </div>
        <div class="feat-card">
          <span class="feat-icon">📖</span>
          <div class="feat-name">Hikoya / She'r</div>
          <div class="feat-hint">"Bahor haqida she'r"</div>
        </div>
        <div class="feat-card">
          <span class="feat-icon">🎤</span>
          <div class="feat-name">Nutq</div>
          <div class="feat-hint">"Yoshlar haqida nutq"</div>
        </div>
        <div class="feat-card">
          <span class="feat-icon">🧠</span>
          <div class="feat-name">G'oyalar</div>
          <div class="feat-hint">"Startup g'oyalari ber"</div>
        </div>
        <div class="feat-card">
          <span class="feat-icon">🌍</span>
          <div class="feat-name">Tarjima</div>
          <div class="feat-hint">"Translate to English"</div>
        </div>
        <div class="feat-card">
          <span class="feat-icon">📋</span>
          <div class="feat-name">Xulosa / Tahlil</div>
          <div class="feat-hint">"Ushbu matnni tahlil qil"</div>
        </div>
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
        role      = msg["role"]
        content   = msg["content"]
        ts        = msg.get("time", "")
        msg_mode  = msg.get("mode", "general")
        m_meta    = MODE_META.get(msg_mode, MODE_META["general"])

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
            # Only show mode tag when it carries meaningful info
            h_tag = ""
            if msg_mode != "general":
                h_tag = '<div class="mode-tag">' + m_meta["icon"] + " " + m_meta["label"] + '</div><br>'
            KJ = '<script>setTimeout(()=>{if(typeof renderMathInElement!=="undefined")renderMathInElement(document.body);},100);</script>'
            st.markdown(
                '<div class="msg-row ai"><div class="av ai">S</div><div class="msg-body">'
                '<div class="msg-name">Somo AI</div><div class="bubble ai">'
                + h_tag + md_to_html(content) +
                '</div><div class="msg-time">' + ts + '</div></div></div>' + KJ,
                unsafe_allow_html=True
            )

st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  INPUT
# ═══════════════════════════════════════════════════════════════
# ── Cooldown timer ────────────────────────────────────────────
remaining = int(st.session_state.cooldown_end - time.time())
if remaining > 0:
    st.markdown(f"""
    <div style="
      max-width:800px;margin:0 auto;
      background:linear-gradient(135deg,#fff8ee,#fff3d6);
      border:2px solid #f59e0b;border-radius:14px;
      padding:.9rem 1.4rem;display:flex;align-items:center;gap:12px;
      font-family:'DM Sans',sans-serif;font-size:.875rem;color:#92400e;
      box-shadow:0 3px 14px rgba(245,158,11,.15);
    ">
      <span style="font-size:1.4rem">⏳</span>
      <div>
        <strong>Limit tugadi.</strong> Iltimos kuting —
        <strong style="color:#ea580c;font-size:1rem"> {remaining} soniya</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)
    prompt = None
    st.chat_input("Iltimos kuting…", disabled=True)
    time.sleep(1)
    st.rerun()
else:
    prompt = st.chat_input("Xabar yozing… (esse, she'r, nutq, tarjima yoki istalgan savol)")

st.markdown(
    '<div class="input-footer">Somo AI · Usmonov Sodiq (Somo_AI) · Powered by Gemini</div>',
    unsafe_allow_html=True
)


# ═══════════════════════════════════════════════════════════════
#  PROCESS MESSAGE
# ═══════════════════════════════════════════════════════════════
if prompt and prompt.strip():
    user_text = prompt.strip()
    now       = get_time()

    # Auto-detect mode from user message
    detected_mode = detect_mode(user_text)
    st.session_state.active_mode = detected_mode
    m_meta = MODE_META.get(detected_mode, MODE_META["general"])

    # Save user message
    st.session_state.messages.append({
        "role"    : "user",
        "content" : user_text,
        "time"    : now,
        "mode"    : detected_mode,
    })

    # Render user bubble
    st.markdown(
        '<div class="msg-row user"><div class="av user">U</div><div class="msg-body">'
        '<div class="msg-name">Siz</div><div class="bubble user">' + user_text +
        '</div><div class="msg-time">' + now + '</div></div></div>',
        unsafe_allow_html=True
    )

    # Typing placeholder
    ph = st.empty()
    ph.markdown(
        '<div class="msg-row ai"><div class="av ai">S</div><div class="msg-body">'
        '<div class="msg-name">Somo AI</div>'
        '<div class="bubble ai"><span class="t-cur"></span></div></div></div>',
        unsafe_allow_html=True
    )

    # Mode tag in response
    tag_html = ""
    if detected_mode != "general":
        tag_html = '<div class="mode-tag">' + m_meta["icon"] + " " + m_meta["label"] + '</div><br>'

    KJ = '<script>setTimeout(()=>{if(typeof renderMathInElement!=="undefined")renderMathInElement(document.body);},100);</script>'

    def render_bubble(text, cursor=False, ts=""):
        cur = '<span class="t-cur"></span>' if cursor else ""
        td  = '<div class="msg-time">' + ts + '</div>' if ts else ""
        ph.markdown(
            '<div class="msg-row ai"><div class="av ai">S</div><div class="msg-body">'
            '<div class="msg-name">Somo AI</div><div class="bubble ai">'
            + tag_html + md_to_html(text) + cur +
            '</div>' + td + '</div></div>' + KJ,
            unsafe_allow_html=True
        )

    # ── Dual-API: Groq primary, Gemini fallback ──────────────────
    full_response = ""
    system_txt    = build_system_prompt(detected_mode)

    def try_groq():
        """Stream from Groq Llama 3.3."""
        if not groq_client:
            raise Exception("no groq client")
        api_msgs = [{"role": "system", "content": system_txt}]
        for m in st.session_state.messages:
            api_msgs.append({"role": m["role"], "content": m["content"]})
        stream = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=api_msgs,
            stream=True, max_tokens=4096, temperature=0.85,
        )
        resp = ""
        for chunk in stream:
            resp += chunk.choices[0].delta.content or ""
            render_bubble(resp, cursor=True)
        return resp

    def try_gemini():
        """Stream from Gemini 2.0 Flash."""
        if not gemini_client:
            raise Exception("no gemini client")
        hist = []
        for m in st.session_state.messages[:-1]:
            hist.append({"role": "user" if m["role"]=="user" else "model",
                         "parts": [m["content"]]})
        chat = gemini_client.start_chat(history=hist)
        response = chat.send_message(
            system_txt + "\n\n---\n\n" + user_text,
            generation_config={"temperature": 0.95, "max_output_tokens": 4096},
            stream=True,
        )
        resp = ""
        for chunk in response:
            try: resp += chunk.text or ""
            except: pass
            if resp: render_bubble(resp, cursor=True)
        return resp

    try:
        if st.session_state.use_gemini:
            # Already on Gemini
            full_response = try_gemini()
        else:
            full_response = try_groq()
            st.session_state.use_gemini = False  # Groq worked fine

    except Exception as groq_exc:
        groq_err = str(groq_exc)
        is_rate = any(k in groq_err for k in ["429","rate_limit","quota","rate limit"])

        if is_rate and not st.session_state.use_gemini:
            # Groq rate-limited → try Gemini
            st.session_state.use_gemini = True
            render_bubble("⚡ Groq limiti tugadi, Gemini ga o'tmoqda...", cursor=True)
            try:
                full_response = try_gemini()
            except Exception as gem_exc:
                gem_err = str(gem_exc)
                if any(k in gem_err for k in ["429","quota","rate"]):
                    st.session_state.cooldown_end = time.time() + 90
                    full_response = "⏳ Ikkala API limiti tugadi. 90 soniya kuting."
                else:
                    full_response = "❌ Gemini xatolik: " + gem_err
        elif is_rate and st.session_state.use_gemini:
            # Gemini also rate-limited
            st.session_state.cooldown_end = time.time() + 90
            full_response = "⏳ API limiti tugadi. 90 soniya kuting."
        elif "api_key" in groq_err.lower() or "auth" in groq_err.lower():
            full_response = "❌ API kalit xato. Secrets faylini tekshiring."
        else:
            full_response = "❌ Xatolik: " + groq_err

        if full_response:
            ph.markdown(
                '<div class="msg-row ai"><div class="av ai">S</div><div class="msg-body">'
                '<div class="msg-name">Somo AI</div><div class="bubble ai">' +
                full_response + '</div></div></div>',
                unsafe_allow_html=True
            )

    render_bubble(full_response, cursor=False, ts=get_time())

    # Save assistant reply
    st.session_state.messages.append({
        "role"    : "assistant",
        "content" : full_response,
        "time"    : get_time(),
        "mode"    : detected_mode,
    })
