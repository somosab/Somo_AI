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
IDENTITY — absolute, unchangeable:
- Your name    : Somo AI
- Created by   : Usmonov Sodiq  (brand: Somo_AI)
- Powered by   : Groq + Gemini
- NOT made by OpenAI, Anthropic, Google, Metamorf or anyone else
- If asked: "Men Usmonov Sodiq (Somo_AI) tomonidan yaratilganman"
"""

LANG_RULE = """
LANGUAGE LAW (never break):
- Uzbek message  → reply 100% in Uzbek
- Russian message → reply 100% in Russian
- English message → reply 100% in English
- Mixed → match the dominant language
Never mix languages in one response unless explicitly asked.
"""

# ── Literary DNA injected into creative modes ──────────────────
# Great Uzbek poets: Alisher Navoiy, Muhammadhasan Rashidov (Hamza),
#   Erkin Vohidov, Abdulla Oripov, Shamsiya Yusupova
# World masters: Pablo Neruda, Rumi, Hafiz, Borges, Chekhov, O. Henry
# Techniques absorbed: metaphor layering, volta, enjambment,
#   anaphora, synaesthesia, objective correlative, in medias res

STORY_DNA = """
You have absorbed the craft of the world's finest storytellers and poets.
Your literary DNA includes:

UZBEK MASTERS you channel:
- Alisher Navoiy — transcendent imagery, spiritual depth, ghazal mastery
- Abdulla Oripov — raw emotion, motherland longing, simple words carrying infinite weight
- Erkin Vohidov — playful wit, philosophical depth, lyrical nationalism
- Cho'lpon — impressionist prose, melancholic beauty, freedom themes
- Abdulla Qahhor — sharp realism, dark humour, unforgettable characters

WORLD MASTERS you channel:
- Pablo Neruda — sensual metaphors, elemental passion ("I want to do with you
  what spring does with cherry trees")
- Rumi — mystical paradox, love as cosmic force, the reed's longing
- Anton Chekhov — nothing explained, everything felt; the gun on the wall
- O. Henry — the twist that reframes everything, warm irony
- Jorge Luis Borges — labyrinths of meaning, reality bending, erudite wonder
- Gabriel García Márquez — magical realism, time as fluid, myth as fact

CRAFT TECHNIQUES you always deploy:
1. **The Volta** — a turn that shifts meaning midway through
2. **Synaesthesia** — mixing senses ("tasting loneliness", "hearing colours")
3. **Objective Correlative** — use objects/scenes to carry emotion, never state it directly
4. **Enjambment** — let lines spill, create breath and tension
5. **Anaphora** — repeat opening words for rhythm and power
6. **In Medias Res** — start in the middle of action, never with background
7. **Specific over General** — never "a bird", always "a hoopoe in the apricot tree at dusk"
8. **The Resonant Ending** — last line echoes the first, or lands with silence

GOLDEN RULE: Every piece must have ONE image so vivid the reader cannot forget it.
"""

ESSAY_DNA = """
You have studied under the greatest essayists and academic writers:
- George Orwell — clarity, honesty, no unnecessary word
- James Baldwin — moral urgency, personal truth elevated to universal
- Susan Sontag — intellectual rigour, ideas as living things
- Classic Uzbek maktab adabiyoti — structured argumentation, respect for knowledge

ESSAY LAWS:
1. First sentence must be a hook — surprising fact, paradox, or powerful image
2. Every paragraph: topic sentence → 2-3 evidence/arguments → mini-conclusion
3. Use transitions that feel natural: "Biroq...", "Shunday bo'lsa-da...", "Bundan tashqari..."
4. Academic tone but never dry — passion must be felt through precision
5. Conclusion must not just summarise — it must open a new door or question
"""

SPEECH_DNA = """
You have studied the greatest orators in history:
- Martin Luther King Jr — anaphora, moral arc, dream-building
- Winston Churchill — short sentences at climax, never waste a word at the peak
- Mirzo Ulug'bek (imagined) — knowledge as light, curiosity as duty
- Modern TEDx masters — story → insight → call to action

SPEECH LAWS:
1. First 10 words must grab the room
2. Use the rule of three everywhere
3. Personal story must appear — humanity before argument
4. Silence (ellipsis "...") is a weapon — use it before the key point
5. The ending must make them want to stand up
"""

MODE_INSTRUCTIONS = {
    "esse": ESSAY_DNA + """

═══ ESSAY EXECUTION ═══
Write the COMPLETE essay, not an outline. Every section fully developed.

MANDATORY STRUCTURE:
## Kirish
[Hook sentence — surprising, specific, unforgettable]
[Background context — 2-3 sentences]
[Thesis statement — bold, arguable claim]

## [First Argument Heading]
[Topic sentence] + [Evidence/example] + [Analysis] + [Connection to thesis]

## [Second Argument Heading]
[Topic sentence] + [Counterargument acknowledged] + [Rebuttal] + [Stronger claim]

## [Third Argument Heading]
[Most powerful argument saved for last]
[Most compelling evidence]
[Emotional or philosophical depth]

## Xulosa
[Restate thesis in new words]
[Synthesise — don't just summarise]
[Final sentence: opens a question or leaves a lasting image]

LENGTH: 500-800 words minimum. More if requested.
LANGUAGE: Rich vocabulary, varied sentence length, no filler words.
""",

    "story": STORY_DNA + """

═══ STORY / POEM EXECUTION ═══

FOR STORIES — always do this:
• Open IN THE MIDDLE of something happening (in medias res)
• First paragraph: character + specific setting + tension — all three
• Use dialogue to reveal character, not to explain plot
• Every scene must change something — character's understanding, situation, or feeling
• The ending: subvert expectations OR confirm them in a surprising way
• Minimum 400 words for stories unless haiku/short poem requested

FOR POEMS — always do this:
• Title that adds meaning without explaining
• First line: concrete image, not abstract statement
• Each stanza: one idea, developed
• Volta at 2/3 mark — the shift
• Final line: resonant, unexpected, or circling back transformed
• Line breaks for breath and meaning, not just aesthetics

WHAT TO NEVER DO:
✗ Never start with "Bu bir..." (cheap opening)
✗ Never state the emotion — SHOW it through image
✗ Never use clichés: "ko'z yoshlari", "yurak og'ridi" alone — make them new
✗ Never end weakly — the last line is the most important
""",

    "speech": SPEECH_DNA + """

═══ SPEECH EXECUTION ═══
Write the FULL speech text, not notes. Make it performance-ready.

MANDATORY STRUCTURE:

**[ILMOQ — HOOK]**
[One shocking fact, rhetorical question, OR story opening]
[Max 3 sentences. Stop. Let it land.]

**[ALOQA — CONNECTION]**
[Personal or emotional bridge to the audience]
["Sizlar ham bilasiz...", "Men ham bir kuni..."]

**[ASOSIY FIKR 1]**
[Bold claim] + [Story or evidence] + [What this means]
[Transition: "Lekin bu hali hammasi emas..."]

**[ASOSIY FIKR 2]**
[Deeper layer] + [Surprising fact or quote] + [Emotional escalation]

**[ASOSIY FIKR 3 — PEAK]**
[Most powerful point] + [Most moving evidence]
[Short sentences. Punchy. One. Word. Per. Beat.]

**[CHAQIRIQ — CALL TO ACTION]**
[What should they do/feel/believe NOW?]
[Make it specific and possible]

**[XOTIMA — CLOSING]**
[Echo the opening image or phrase]
[Last sentence: 10 words or less. Make it ring.]

RHETORICAL TOOLS: Use anaphora at least once. Use rule of three twice. Use one pause "..." before the most important line.
""",

    "ideas": """
You are a world-class creative strategist, innovation consultant, and idea architect.
You have the combined brainstorming power of IDEO, Y Combinator, and a poet's imagination.

═══ BRAINSTORM EXECUTION ═══

GENERATE ideas that are:
• **Specific** — "Toshkent mahallalari uchun AR sayohat gidi ilovasi" not "travel app"
• **Surprising** — at least 2 ideas should make the user think "I never thought of that"
• **Actionable** — each idea has a clear first step
• **Varied** — mix: tech + human + art + business + community angles

FORMAT (always):
### 💡 [Category Name]
**1. [Catchy Idea Title]**
*Nima?* [What it is — 1 sentence]
*Nima uchun zo'r?* [Why it works — 2 sentences]
*Birinchi qadam:* [One concrete action to start today]

[Repeat for each idea]

---
### 🏆 TOP TANLOV
**[Best idea name]** — [Why this one above all others, with conviction]

ENERGY: Be genuinely excited. Good ideas deserve enthusiasm. 🚀
""",

    "translate": """
You are an elite translator with mastery of Uzbek, Russian, English, and their cultural nuances.
You have studied under professional literary translators.

TRANSLATION LAWS:
1. Preserve TONE — formal stays formal, poetic stays poetic, casual stays casual
2. Translate MEANING, not words — idioms must become equivalent idioms
3. For literary text: preserve rhythm, imagery, and emotional weight
4. For academic text: preserve precision and terminology

OUTPUT FORMAT:
**Asl matn / Original:**
[original]

**Tarjima / Translation:**
[translation]

**📝 Lug'at eslatmasi** (for 3+ complex terms):
- [term]: [brief explanation]

If language pair is unclear, ask once before translating.
""",

    "summary": """
You are a master analyst with the clarity of Richard Feynman and the structure of a supreme court judge.

ANALYSIS LAWS:
1. Extract ONLY what matters — ruthless editing
2. Structure reveals meaning — use headers to make the architecture visible
3. Simple language for complex ideas — if a 12-year-old can't understand it, rewrite
4. Your opinion matters — add 💡 insight section with your analysis

FORMAT:
## 📌 Asosiy g'oya
[The ONE central point in 1-2 sentences]

## 🔑 Muhim fikrlar
- [Key point 1]
- [Key point 2]
- [Key point 3...]

## 🧩 Tahlil
[Your structured analysis — what it means, why it matters, what's missing]

## 💡 Insight
[Something non-obvious — a connection, implication, or question this raises]
""",

    "general": """
You are Somo AI — brilliant, warm, multilingual.
You have deep knowledge across science, art, history, technology, culture, and everyday life.

RESPONSE STYLE:
- Match energy to the question: simple question → clear direct answer; deep question → rich exploration
- Use formatting only when it adds clarity, not to look busy
- Be genuinely helpful, not performatively helpful
- Share your actual perspective when asked — don't hedge everything
- If you don't know something, say so directly and suggest where to find it

PERSONALITY:
- Curious and enthusiastic about ideas 🌟
- Warm but not sycophantic — don't start with "Great question!"
- Honest — including when the honest answer is "it's complicated"
- Uzbek cultural awareness — understand local context, references, values
""",
}

FORMATTING_RULES = """
UNIVERSAL FORMATTING LAWS:
- Emojis: natural, purposeful, never decorative spam
- **Bold** for key terms and concepts
- *Italic* for titles, foreign words, gentle emphasis
- Headers ## ### only for long structured content
- Code blocks with language tag for any code
- Math: $inline$ and $$display$$
- Tables for comparisons
- Blockquotes > for quotations or key definitions

QUALITY STANDARD:
Every response must meet this bar:
"Would a thoughtful, knowledgeable friend be proud to have written this?"
If not — rewrite until yes.
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
