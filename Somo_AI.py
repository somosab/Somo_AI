import streamlit as st
from groq import Groq
import time
import re

# ─── Markdown → HTML ─────────────────────────────────────────────────────────
def md_to_html(text):
    math_blocks = {}
    def save_math(m):
        key = f"__MATH{len(math_blocks)}__"
        math_blocks[key] = m.group(0)
        return key
    text = re.sub(r'\$\$.+?\$\$', save_math, text, flags=re.DOTALL)
    text = re.sub(r'\$.+?\$', save_math, text)
    text = re.sub(r'```(\w*)\n?(.*?)```', lambda m: f'<pre><code>{m.group(2).strip()}</code></pre>', text, flags=re.DOTALL)
    text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    def replace_ul(m):
        items = re.findall(r'^[\-\*] (.+)$', m.group(0), re.MULTILINE)
        return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
    text = re.sub(r'(^[\-\*] .+\n?)+', replace_ul, text, flags=re.MULTILINE)
    def replace_ol(m):
        items = re.findall(r'^\d+\. (.+)$', m.group(0), re.MULTILINE)
        return '<ol>' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'
    text = re.sub(r'(\d+\. .+\n?)+', replace_ol, text, flags=re.MULTILINE)
    text = re.sub(r'^-{3,}$', '<hr>', text, flags=re.MULTILINE)
    text = re.sub(r'\n', '<br>', text)
    for key, val in math_blocks.items():
        text = text.replace(key, val)
    return text

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EduCreate AI",
    page_icon="✏️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400;1,9..144,700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[
    {left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}
  ]});"></script>

<style>
  :root {
    --ink:     #1a1208;
    --paper:   #fef9f0;
    --warm:    #fdf3dc;
    --card:    #fffcf5;
    --border:  #ecdfc4;
    --amber:   #f59e0b;
    --orange:  #ea580c;
    --muted:   #8a7455;
    --light:   #c4a97a;
    --green:   #15803d;
    --rose:    #e11d48;
    --fh: 'Fraunces', serif;
    --fb: 'Plus Jakarta Sans', sans-serif;
  }

  html, body {
    background: var(--paper) !important;
    margin: 0; padding: 0;
    -webkit-font-smoothing: antialiased;
  }
  * { box-sizing: border-box; }

  [data-testid="stAppViewContainer"],
  [data-testid="stMain"], .main {
    background: var(--paper) !important;
  }

  /* Hide ALL Streamlit chrome */
  #MainMenu, footer, header,
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  [data-testid="stSidebar"],
  [data-testid="collapsedControl"] { display: none !important; }

  .block-container,
  [data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
  }

  /* ══════════════════════════════════
     TOP NAV BAR
  ══════════════════════════════════ */
  .topnav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.9rem 1.8rem;
    background: rgba(254,249,240,0.96);
    border-bottom: 1.5px solid var(--border);
    position: sticky; top: 0; z-index: 999;
    backdrop-filter: blur(16px);
  }
  .nav-brand {
    display: flex; align-items: center; gap: 10px;
  }
  .nav-logo {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--amber), var(--orange));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
    box-shadow: 0 3px 10px rgba(245,158,11,0.3);
    flex-shrink: 0;
  }
  .nav-title {
    font-family: var(--fh) !important;
    font-size: 1.15rem; font-weight: 900;
    color: var(--ink);
    line-height: 1;
  }
  .nav-title em { color: var(--orange); font-style: italic; }
  .nav-sub {
    font-family: var(--fb) !important;
    font-size: 0.6rem; color: var(--light);
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-top: 2px;
  }
  .nav-right {
    display: flex; align-items: center; gap: 8px;
  }
  .nav-mode-pill {
    background: var(--warm);
    border: 1.5px solid var(--border);
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-family: var(--fb) !important;
    font-size: 0.65rem; color: var(--muted);
    display: flex; align-items: center; gap: 5px;
  }
  .nav-lang-pill {
    background: linear-gradient(135deg, var(--green), #16a34a);
    border-radius: 20px;
    padding: 0.25rem 0.65rem;
    font-family: var(--fb) !important;
    font-size: 0.65rem; color: white;
  }

  /* ══════════════════════════════════
     MODE SELECTOR BAR
  ══════════════════════════════════ */
  .mode-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.8rem;
    overflow-x: auto;
    background: var(--warm);
    border-bottom: 1.5px solid var(--border);
    scrollbar-width: none;
  }
  .mode-bar::-webkit-scrollbar { display: none; }
  .mode-pill {
    display: flex; align-items: center; gap: 6px;
    padding: 0.4rem 0.9rem;
    border-radius: 20px;
    border: 1.5px solid var(--border);
    background: var(--card);
    font-family: var(--fb) !important;
    font-size: 0.72rem; font-weight: 500;
    color: var(--muted);
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.18s;
    flex-shrink: 0;
  }
  .mode-pill:hover {
    border-color: var(--amber);
    color: var(--orange);
    background: #fff8ee;
  }
  .mode-pill.active {
    background: linear-gradient(135deg, var(--amber), var(--orange));
    border-color: transparent;
    color: white;
    box-shadow: 0 3px 10px rgba(245,158,11,0.3);
    font-weight: 600;
  }

  /* ══════════════════════════════════
     CHAT AREA
  ══════════════════════════════════ */
  .chat-wrap {
    max-width: 820px;
    margin: 0 auto;
    padding: 2rem 1.5rem 6rem;
    min-height: calc(100vh - 180px);
  }

  /* ── WELCOME SCREEN ── */
  .welcome {
    display: flex; flex-direction: column;
    align-items: center; text-align: center;
    padding: 2.5rem 0 3rem;
  }
  .w-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(135deg, var(--amber), var(--orange));
    color: white; border-radius: 30px;
    padding: 0.35rem 1.1rem;
    font-family: var(--fb) !important;
    font-size: 0.65rem; font-weight: 600;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 14px rgba(245,158,11,0.35);
    animation: badgePop 0.6s cubic-bezier(0.34,1.56,0.64,1);
  }
  @keyframes badgePop { from{opacity:0;transform:scale(0.7)} to{opacity:1;transform:scale(1)} }

  .w-headline {
    font-family: var(--fh) !important;
    font-size: clamp(2.2rem, 6vw, 3.5rem);
    font-weight: 900;
    color: var(--ink);
    line-height: 1.1;
    margin-bottom: 0.3rem;
    animation: slideUp 0.5s ease-out 0.1s both;
  }
  .w-headline em {
    color: var(--orange);
    font-style: italic;
    background: linear-gradient(135deg, var(--amber), var(--orange));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  @keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }

  .w-sub {
    font-family: var(--fb) !important;
    font-size: clamp(0.82rem, 2.2vw, 0.95rem);
    color: var(--muted); line-height: 1.7;
    max-width: 480px; margin: 0.8rem auto 2.5rem;
    animation: slideUp 0.5s ease-out 0.2s both;
  }

  /* Mode cards grid */
  .mode-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    width: 100%; max-width: 580px;
    margin-bottom: 2rem;
    animation: slideUp 0.5s ease-out 0.3s both;
  }
  .m-card {
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 16px;
    padding: 1.1rem 0.7rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.34,1.56,0.64,1);
    position: relative; overflow: hidden;
  }
  .m-card::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(245,158,11,0.06), rgba(234,88,12,0.06));
    opacity: 0; transition: opacity 0.2s;
  }
  .m-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); border-color: var(--amber); }
  .m-card:hover::before { opacity: 1; }
  .m-card .mc-icon { font-size: 1.7rem; margin-bottom: 0.5rem; display: block; }
  .m-card .mc-name {
    font-family: var(--fb) !important;
    font-size: 0.75rem; font-weight: 700;
    color: var(--ink); margin-bottom: 0.2rem;
  }
  .m-card .mc-hint {
    font-family: var(--fb) !important;
    font-size: 0.62rem; color: var(--light);
  }

  /* Example chips */
  .ex-row {
    display: flex; gap: 0.5rem; flex-wrap: wrap;
    justify-content: center;
    animation: slideUp 0.5s ease-out 0.4s both;
  }
  .ex-chip {
    background: var(--warm);
    border: 1.5px solid var(--border);
    border-radius: 20px;
    padding: 0.38rem 0.85rem;
    font-family: var(--fb) !important;
    font-size: 0.7rem; color: var(--muted);
    cursor: pointer; transition: all 0.15s;
  }
  .ex-chip:hover { border-color: var(--amber); color: var(--orange); background: #fff8ee; }

  /* ── MESSAGES ── */
  .msg-row {
    display: flex; gap: 11px; margin-bottom: 1.4rem;
    animation: msgIn 0.3s cubic-bezier(0.34,1.2,0.64,1);
  }
  @keyframes msgIn { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
  .msg-row.user { flex-direction: row-reverse; }

  .m-av {
    width: 32px; height: 32px; min-width: 32px;
    border-radius: 10px; display: flex;
    align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0;
    align-self: flex-start; margin-top: 2px;
  }
  .m-av.user {
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    box-shadow: 0 2px 8px rgba(99,102,241,0.3);
  }
  .m-av.ai {
    background: linear-gradient(135deg, var(--amber), var(--orange));
    box-shadow: 0 2px 8px rgba(245,158,11,0.3);
  }

  .m-body { max-width: 78%; }
  .m-name {
    font-family: var(--fb) !important;
    font-size: 0.6rem; color: var(--light);
    margin-bottom: 0.28rem; letter-spacing: 1px; text-transform: uppercase;
  }
  .msg-row.user .m-name { text-align: right; }

  .m-bubble {
    padding: 0.85rem 1.1rem;
    border-radius: 14px;
    font-family: var(--fb) !important;
    font-size: 0.875rem; line-height: 1.75;
    color: var(--ink); word-break: break-word;
  }
  .m-bubble.user {
    background: linear-gradient(135deg, #eff6ff, #eef2ff);
    border: 1.5px solid #c7d2fe;
    border-top-right-radius: 4px;
  }
  .m-bubble.ai {
    background: var(--card);
    border: 1.5px solid var(--border);
    border-top-left-radius: 4px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  }

  /* Bubble content */
  .m-bubble strong { color: var(--orange); font-weight: 700; }
  .m-bubble em { color: var(--muted); }
  .m-bubble h1,.m-bubble h2,.m-bubble h3 {
    font-family: var(--fh) !important;
    color: var(--ink); margin: 0.8rem 0 0.3rem; font-weight: 700;
  }
  .m-bubble code {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.22);
    padding: 0.1rem 0.38rem; border-radius: 5px;
    font-size: 0.8rem; color: var(--orange);
    font-family: 'Courier New', monospace !important;
  }
  .m-bubble pre {
    background: var(--warm); border: 1.5px solid var(--border);
    border-radius: 10px; padding: 0.9rem; overflow-x: auto; margin: 0.6rem 0;
  }
  .m-bubble pre code { background:none; border:none; padding:0; color: var(--green); font-size:0.78rem; }
  .m-bubble ul,.m-bubble ol { padding-left: 1.2rem; margin: 0.35rem 0; }
  .m-bubble li { margin-bottom: 0.22rem; }
  .m-bubble blockquote {
    border-left: 3px solid var(--amber);
    background: rgba(245,158,11,0.06);
    padding: 0.5rem 0.9rem; border-radius: 0 8px 8px 0;
    color: var(--muted); margin: 0.5rem 0; font-style: italic;
  }
  .m-bubble table { border-collapse: collapse; width: 100%; margin: 0.6rem 0; font-size: 0.8rem; }
  .m-bubble th {
    background: var(--warm); padding: 0.4rem 0.7rem;
    border: 1.5px solid var(--border); color: var(--orange); font-weight: 700;
  }
  .m-bubble td { padding: 0.35rem 0.7rem; border: 1px solid var(--border); }
  .m-bubble tr:nth-child(even) { background: rgba(0,0,0,0.02); }

  /* Mode tag */
  .m-tag {
    display: inline-block;
    font-family: var(--fb) !important;
    font-size: 0.58rem; letter-spacing: 1.5px; text-transform: uppercase;
    background: linear-gradient(135deg, var(--amber), var(--orange));
    color: white; padding: 0.15rem 0.55rem; border-radius: 10px;
    margin-bottom: 0.45rem; font-weight: 600;
  }
  .m-time {
    font-family: var(--fb) !important;
    font-size: 0.58rem; color: var(--light);
    margin-top: 0.28rem; opacity: 0.7;
  }
  .msg-row.user .m-time { text-align: right; }

  /* Typing cursor */
  .t-cursor {
    display: inline-block; width: 2px; height: 0.9em;
    background: var(--orange); margin-left: 2px;
    vertical-align: middle;
    animation: blink 0.65s steps(1) infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

  /* ══════════════════════════════════
     SETTINGS PANEL (modal)
  ══════════════════════════════════ */
  .settings-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(26,18,8,0.4);
    backdrop-filter: blur(4px);
    z-index: 2000;
  }
  .settings-overlay.open { display: block; }
  .settings-panel {
    position: fixed; top: 50%; left: 50%;
    transform: translate(-50%, -50%) scale(0.92);
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 20px;
    padding: 1.8rem;
    width: min(420px, 92vw);
    box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    z-index: 2001;
    opacity: 0; pointer-events: none;
    transition: all 0.25s cubic-bezier(0.34,1.4,0.64,1);
  }
  .settings-panel.open {
    opacity: 1; pointer-events: all;
    transform: translate(-50%, -50%) scale(1);
  }
  .sp-title {
    font-family: var(--fh) !important;
    font-size: 1.3rem; font-weight: 900;
    color: var(--ink); margin-bottom: 1.2rem;
    display: flex; align-items: center; justify-content: space-between;
  }
  .sp-close {
    width: 28px; height: 28px;
    background: var(--warm); border: 1.5px solid var(--border);
    border-radius: 8px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; transition: all 0.15s;
  }
  .sp-close:hover { background: var(--rose); color: white; border-color: var(--rose); }
  .sp-sec {
    font-family: var(--fb) !important;
    font-size: 0.6rem; letter-spacing: 2.5px; text-transform: uppercase;
    color: var(--light); margin: 1rem 0 0.5rem;
  }
  .sp-model-grid {
    display: flex; flex-direction: column; gap: 0.35rem;
  }
  .sp-model-item {
    padding: 0.55rem 0.9rem;
    background: var(--warm); border: 1.5px solid var(--border);
    border-radius: 10px; cursor: pointer;
    font-family: var(--fb) !important;
    font-size: 0.78rem; color: var(--ink);
    transition: all 0.15s;
  }
  .sp-model-item:hover { border-color: var(--amber); background: #fff8ee; }
  .sp-model-item.sel { background: #fff3e0; border-color: var(--orange); color: var(--orange); font-weight: 600; }
  .sp-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.5rem 0; border-bottom: 1px solid var(--border);
    font-family: var(--fb) !important; font-size: 0.8rem;
  }
  .sp-row .sk { color: var(--muted); }
  .sp-row .sv { color: var(--ink); font-weight: 600; }
  .sp-clear {
    width: 100%; padding: 0.7rem; margin-top: 1.2rem;
    background: transparent; border: 1.5px solid var(--rose);
    border-radius: 12px; color: var(--rose);
    font-family: var(--fb) !important; font-size: 0.82rem; font-weight: 600;
    cursor: pointer; transition: all 0.15s;
  }
  .sp-clear:hover { background: var(--rose); color: white; }

  /* ══════════════════════════════════
     BOTTOM INPUT BAR
  ══════════════════════════════════ */
  [data-testid="stChatInput"] {
    background: var(--card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 18px !important;
    margin: 0 1rem 1rem !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
  }
  [data-testid="stChatInput"]:focus-within {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 4px rgba(245,158,11,0.12), 0 4px 20px rgba(0,0,0,0.08) !important;
  }
  [data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--ink) !important;
    font-size: 0.88rem !important;
    font-family: var(--fb) !important;
    border: none !important; outline: none !important; box-shadow: none !important;
  }
  [data-testid="stChatInput"] textarea::placeholder { color: var(--light) !important; }
  [data-testid="stChatInput"] button {
    background: linear-gradient(135deg, var(--amber), var(--orange)) !important;
    border: none !important; border-radius: 12px !important;
    box-shadow: 0 3px 10px rgba(245,158,11,0.35) !important;
    transition: opacity 0.15s !important;
  }
  [data-testid="stChatInput"] button:hover { opacity: 0.85 !important; }
  [data-testid="stChatInput"] button svg { fill: white !important; }

  /* Bottom bar wrapper */
  .input-wrap {
    position: sticky; bottom: 0;
    background: linear-gradient(to top, var(--paper) 70%, transparent);
    padding: 0.5rem 0 0;
  }
  .input-hint {
    text-align: center;
    font-family: var(--fb) !important;
    font-size: 0.58rem; color: var(--light);
    padding-bottom: 0.4rem; letter-spacing: 0.5px;
  }

  /* ══════════════════════════════════
     RESPONSIVE — MOBILE
  ══════════════════════════════════ */
  @media (max-width: 640px) {
    .topnav { padding: 0.75rem 1rem; }
    .nav-title { font-size: 1rem; }
    .nav-sub { display: none; }
    .mode-bar { padding: 0.6rem 1rem; gap: 0.4rem; }
    .mode-pill { font-size: 0.68rem; padding: 0.35rem 0.75rem; }
    .chat-wrap { padding: 1.2rem 1rem 5.5rem; }
    .w-headline { font-size: clamp(1.8rem, 8vw, 2.5rem); }
    .w-sub { font-size: 0.82rem; }
    .mode-grid { grid-template-columns: repeat(2, 1fr); gap: 0.6rem; }
    .m-card { padding: 0.9rem 0.5rem; }
    .m-card .mc-icon { font-size: 1.4rem; }
    .m-card .mc-name { font-size: 0.7rem; }
    .m-body { max-width: 88%; }
    .m-bubble { font-size: 0.83rem; padding: 0.75rem 0.9rem; }
    .ex-chip { font-size: 0.67rem; padding: 0.32rem 0.7rem; }
    [data-testid="stChatInput"] { margin: 0 0.6rem 0.7rem !important; border-radius: 14px !important; }
  }

  /* KaTeX */
  .katex { font-size: 1em !important; color: var(--ink) !important; }
  .katex-display { overflow-x: auto; padding: 0.3rem 0; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 3px; height: 3px; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── Groq Client ─────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("❌ GROQ_API_KEY topilmadi. Streamlit Secrets ga qo'shing.")
    st.stop()

# ─── Session State ────────────────────────────────────────────────────────────
if "messages" not in st.session_state: st.session_state.messages = []
if "mode"     not in st.session_state: st.session_state.mode     = "esse"
if "lang"     not in st.session_state: st.session_state.lang     = "uz"
if "model"    not in st.session_state: st.session_state.model    = "llama-3.3-70b-versatile"
if "temp"     not in st.session_state: st.session_state.temp     = 0.85

MODES = {
    "esse":     {"icon": "✍️",  "label": "Esse",      "full": "Esse / Referat",   "hint": "Maqola yozish"},
    "story":    {"icon": "📖",  "label": "Hikoya",    "full": "Hikoya / She'r",   "hint": "Ijodiy yozuv"},
    "speech":   {"icon": "🎤",  "label": "Nutq",      "full": "Nutq / Taqdimot",  "hint": "Chiqish matni"},
    "ideas":    {"icon": "🧠",  "label": "G'oyalar",  "full": "G'oya generatsiya","hint": "Beyin fırtınası"},
    "translate":{"icon": "🌍",  "label": "Tarjima",   "full": "Tarjimon",         "hint": "UZ↔RU↔EN"},
    "summary":  {"icon": "📋",  "label": "Xulosa",    "full": "Xulosa / Tahlil",  "hint": "Tahlil qilish"},
}
LANGS = {"uz": "🇺🇿 UZ", "ru": "🇷🇺 RU", "en": "🇬🇧 EN"}
MODELS = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

# ─── System Prompt ────────────────────────────────────────────────────────────
IDENTITY = """
IDENTITY (never change, never fabricate):
- Your name: Somo_AI
- Created by: Usmonov Sodiq 
- Built on: Groq infrastructure
- NOT made by OpenAI, Google, Anthropic, Metamorf, or any other company
- If asked who created you: say "Men Usmonov Sodiq tomonidan yaratilganman"
"""

LANG_MAP = {
    "uz": "ALWAYS respond in Uzbek.",
    "ru": "ALWAYS respond in Russian.",
    "en": "ALWAYS respond in English.",
}

MODE_MAP = {
    "esse":     "You are EduCreate AI, an expert essay and academic writing assistant for students. Help write well-structured essays with intro, body, conclusion. Use rich formatting.",
    "story":    "You are EduCreate AI, a creative storytelling assistant. Help write vivid stories, poems, fairy tales. Use beautiful language and literary techniques.",
    "speech":   "You are EduCreate AI, a public speaking coach. Help write powerful speeches and presentations with strong openings and memorable closings.",
    "ideas":    "You are EduCreate AI, a brainstorming expert. Generate creative, original ideas in organized lists with explanations. Inspire and motivate.",
    "translate":"You are EduCreate AI, a multilingual translation expert. Translate accurately between Uzbek, Russian, and English. Explain key vocabulary when helpful.",
    "summary":  "You are EduCreate AI, an analysis expert. Summarize and analyze texts clearly using tables, lists, and structured formats.",
}

RULES = """
FORMATTING:
- Use emojis naturally 🎯✨📚
- **bold** key terms, *italics* for nuance
- Headers ## ### for structure
- Lists, tables, blockquotes as needed
- Math: $inline$ and $$display$$ LaTeX

PERSONALITY:
- Warm, encouraging, student-friendly 🌟
- Enthusiastic about creativity and learning
- Concise but thorough
"""

def get_system():
    return f"{IDENTITY}\n{MODE_MAP[st.session_state.mode]}\nLANGUAGE: {LANG_MAP[st.session_state.lang]}\n{RULES}"

def get_time():
    return time.strftime("%H:%M")

# ─── TOP NAV ─────────────────────────────────────────────────────────────────
cur = MODES[st.session_state.mode]
model_short = st.session_state.model.replace("llama-3.3-","L3.3-").replace("-versatile","").replace("llama3-","L3-").replace("-8192","").replace("-32768","").upper()

st.markdown(f"""
<div class="topnav">
  <div class="nav-brand">
    <div class="nav-logo">✏️</div>
    <div>
      <div class="nav-title">Edu<em>Create</em> AI</div>
      <div class="nav-sub">by Usmonov Sodiq · Somo_AI</div>
    </div>
  </div>
  <div class="nav-right">
    <div class="nav-mode-pill">{cur['icon']} {cur['label']}</div>
    <div class="nav-lang-pill">{LANGS[st.session_state.lang]}</div>
    <div class="nav-mode-pill" style="cursor:pointer" onclick="openSettings()">⚙️</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── MODE BAR ────────────────────────────────────────────────────────────────
mode_pills = ""
for k, m in MODES.items():
    active = "active" if st.session_state.mode == k else ""
    mode_pills += f'<div class="mode-pill {active}" onclick="setMode(\'{k}\')">{m["icon"]} {m["label"]}</div>'

st.markdown(f'<div class="mode-bar">{mode_pills}</div>', unsafe_allow_html=True)

# Handle mode changes via Streamlit buttons (hidden, triggered by JS)
cols = st.columns(len(MODES))
for i, (k, m) in enumerate(MODES.items()):
    with cols[i]:
        if st.button(m["icon"], key=f"mb_{k}", help=m["full"], use_container_width=True):
            st.session_state.mode = k
            st.rerun()

# Hide the actual streamlit buttons (we use the HTML pills above)
st.markdown("""
<style>
  /* Hide the functional buttons but keep them clickable via JS workaround */
  div[data-testid="stHorizontalBlock"] { display: none !important; }
</style>
<script>
function setMode(mode) {
  // Find and click the hidden streamlit button
  const btns = window.parent.document.querySelectorAll('button');
  for(let b of btns) {
    if(b.getAttribute('data-testid') === 'baseButton-secondary' && b.title === {
      'esse': 'Esse / Referat', 'story': "Hikoya / She'r",
      'speech': 'Nutq / Taqdimot', 'ideas': "G'oya generatsiya",
      'translate': 'Tarjimon', 'summary': 'Xulosa / Tahlil'
    }[mode]) { b.click(); break; }
  }
}
function openSettings() {
  document.getElementById('settingsOverlay').classList.add('open');
  document.getElementById('settingsPanel').classList.add('open');
}
function closeSettings() {
  document.getElementById('settingsOverlay').classList.remove('open');
  document.getElementById('settingsPanel').classList.remove('open');
}
</script>
""", unsafe_allow_html=True)

# ─── MESSAGES ────────────────────────────────────────────────────────────────
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome">
      <div class="w-badge">✨ O'quvchilar uchun AI Yordamchi</div>
      <div class="w-headline">Ijodingizni<br><em>kuchlaytiring</em></div>
      <div class="w-sub">
        Esse, hikoya, nutq, g'oyalar va tarjima — barchasi bir joyda.<br>
        O'z tilida, o'z uslubida. 🚀
      </div>
      <div class="mode-grid">
        <div class="m-card"><span class="mc-icon">✍️</span><div class="mc-name">Esse / Referat</div><div class="mc-hint">Maqola yozish</div></div>
        <div class="m-card"><span class="mc-icon">📖</span><div class="mc-name">Hikoya / She'r</div><div class="mc-hint">Ijodiy yozuv</div></div>
        <div class="m-card"><span class="mc-icon">🎤</span><div class="mc-name">Nutq</div><div class="mc-hint">Taqdimot matni</div></div>
        <div class="m-card"><span class="mc-icon">🧠</span><div class="mc-name">G'oyalar</div><div class="mc-hint">Beyin fırtınası</div></div>
        <div class="m-card"><span class="mc-icon">🌍</span><div class="mc-name">Tarjimon</div><div class="mc-hint">UZ↔RU↔EN</div></div>
        <div class="m-card"><span class="mc-icon">📋</span><div class="mc-name">Xulosa</div><div class="mc-hint">Tahlil qilish</div></div>
      </div>
      <div class="ex-row">
        <div class="ex-chip">📝 "Vatan haqida esse yoz"</div>
        <div class="ex-chip">🌹 "Bahor haqida she'r"</div>
        <div class="ex-chip">🎤 "Yoshlar haqida nutq"</div>
        <div class="ex-chip">💡 "Biznes g'oyalar ber"</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"]
        ts      = msg.get("time", "")
        m_mode  = msg.get("mode", st.session_state.mode)
        mode_info = MODES.get(m_mode, cur)

        if role == "user":
            st.markdown(f"""
            <div class="msg-row user">
              <div class="m-av user">👤</div>
              <div class="m-body">
                <div class="m-name">Siz</div>
                <div class="m-bubble user">{content}</div>
                <div class="m-time">{ts}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-row ai">
              <div class="m-av ai">✏️</div>
              <div class="m-body">
                <div class="m-name">EduCreate AI</div>
                <div class="m-bubble ai">
                  <div class="m-tag">{mode_info['icon']} {mode_info['label']}</div><br>
                  {md_to_html(content)}
                </div>
                <div class="m-time">{ts}</div>
              </div>
            </div>
            <script>setTimeout(()=>{{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},100);</script>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─── SETTINGS MODAL ──────────────────────────────────────────────────────────
msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
models_html = ""
for mdl in MODELS:
    sel = "sel" if mdl == st.session_state.model else ""
    short = mdl.replace("llama-3.3-","L3.3-").replace("-versatile","").replace("llama3-","L3-").replace("-8192","").replace("-32768","").upper()
    models_html += f'<div class="sp-model-item {sel}">{short} <span style="color:var(--light);font-size:0.65rem">({mdl})</span></div>'

lang_btns = ""
for lk, lv in LANGS.items():
    active_style = "background:linear-gradient(135deg,var(--amber),var(--orange));color:white;border-color:transparent;" if lk == st.session_state.lang else ""
    lang_btns += f'<div class="sp-model-item" style="{active_style}">{lv}</div>'

st.markdown(f"""
<div class="settings-overlay" id="settingsOverlay" onclick="closeSettings()"></div>
<div class="settings-panel" id="settingsPanel">
  <div class="sp-title">
    ⚙️ Sozlamalar
    <div class="sp-close" onclick="closeSettings()">✕</div>
  </div>

  <div class="sp-sec">📊 Statistika</div>
  <div class="sp-row"><span class="sk">So'rovlar</span><span class="sv">{msg_count}</span></div>
  <div class="sp-row"><span class="sk">Joriy rejim</span><span class="sv">{cur['icon']} {cur['full']}</span></div>
  <div class="sp-row"><span class="sk">Til</span><span class="sv">{LANGS[st.session_state.lang]}</span></div>
  <div class="sp-row"><span class="sk">Model</span><span class="sv">{model_short}</span></div>
  <div class="sp-row"><span class="sk">Creativity</span><span class="sv">{st.session_state.temp}</span></div>

  <div class="sp-sec">ℹ️ Dastur haqida</div>
  <div class="sp-row"><span class="sk">Nomi</span><span class="sv">EduCreate AI</span></div>
  <div class="sp-row"><span class="sk">Yaratuvchi</span><span class="sv">Usmonov Sodiq</span></div>
  <div class="sp-row"><span class="sk">Brand</span><span class="sv">Somo_AI</span></div>
  <div class="sp-row"><span class="sk">Versiya</span><span class="sv">v3.0 · Groq</span></div>

  <div style="background:rgba(245,158,11,0.08);border:1.5px solid rgba(245,158,11,0.2);border-radius:10px;padding:0.7rem 0.9rem;margin-top:1rem;">
    <div style="font-family:var(--fb);font-size:0.7rem;color:var(--muted);line-height:1.6;">
      💡 Rejim va tilni o'zgartirish uchun tepadan foydalaning.<br>
      Model va temperature sozlamalari uchun keyingi versiyada yangilanadi.
    </div>
  </div>

  <button class="sp-clear" onclick="if(confirm('Barcha xabarlarni o\\'chirish?'))window.location.reload()">
    🗑️ Chatni tozalash
  </button>
</div>
""", unsafe_allow_html=True)

# ─── CHAT INPUT ──────────────────────────────────────────────────────────────
placeholders = {
    "esse":     "Esse mavzusini yozing... (masalan: 'Ekologiya haqida esse')",
    "story":    "Hikoya yoki she'r so'rang... (masalan: 'Bahor haqida she'r yoz')",
    "speech":   "Nutq mavzusini kiriting... (masalan: 'Yoshlar haqida nutq')",
    "ideas":    "G'oya so'rang... (masalan: 'Startup g'oyalari ber')",
    "translate":"Tarjima qilish uchun matn yozing...",
    "summary":  "Tahlil qilmoqchi bo'lgan matnni kiriting...",
}
st.markdown('<div class="input-wrap">', unsafe_allow_html=True)
prompt = st.chat_input(placeholders.get(st.session_state.mode, "Yozing..."))
st.markdown(f'<div class="input-hint">EduCreate AI · by Usmonov Sodiq (Somo_AI) · {cur["icon"]} {cur["full"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─── MODE SELECTOR (hidden Streamlit logic) ───────────────────────────────────
with st.expander("", expanded=False):
    for k in MODES:
        if st.button(k, key=f"sel_{k}"):
            st.session_state.mode = k
            st.rerun()

# ─── PROCESS MESSAGE ─────────────────────────────────────────────────────────
if prompt and prompt.strip():
    user_text    = prompt.strip()
    current_mode = st.session_state.mode
    mode_info    = MODES[current_mode]

    st.session_state.messages.append({
        "role": "user", "content": user_text,
        "time": get_time(), "mode": current_mode
    })

    st.markdown(f"""
    <div class="msg-row user">
      <div class="m-av user">👤</div>
      <div class="m-body">
        <div class="m-name">Siz</div>
        <div class="m-bubble user">{user_text}</div>
        <div class="m-time">{get_time()}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    typing_ph = st.empty()
    typing_ph.markdown("""
    <div class="msg-row ai">
      <div class="m-av ai">✏️</div>
      <div class="m-body">
        <div class="m-name">EduCreate AI</div>
        <div class="m-bubble ai"><span class="t-cursor"></span></div>
      </div>
    </div>""", unsafe_allow_html=True)

    api_msgs = [{"role": "system", "content": get_system()}]
    for m in st.session_state.messages:
        api_msgs.append({"role": m["role"], "content": m["content"]})

    full_response = ""
    try:
        completion = client.chat.completions.create(
            model=st.session_state.model,
            messages=api_msgs,
            stream=True,
            max_tokens=2048,
            temperature=st.session_state.temp,
        )
        for chunk in completion:
            delta = chunk.choices[0].delta.content or ""
            full_response += delta
            typing_ph.markdown(f"""
            <div class="msg-row ai">
              <div class="m-av ai">✏️</div>
              <div class="m-body">
                <div class="m-name">EduCreate AI</div>
                <div class="m-bubble ai">
                  <div class="m-tag">{mode_info['icon']} {mode_info['label']}</div><br>
                  {md_to_html(full_response)}<span class="t-cursor"></span>
                </div>
              </div>
            </div>
            <script>setTimeout(()=>{{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},80);</script>
            """, unsafe_allow_html=True)

        typing_ph.markdown(f"""
        <div class="msg-row ai">
          <div class="m-av ai">✏️</div>
          <div class="m-body">
            <div class="m-name">EduCreate AI</div>
            <div class="m-bubble ai">
              <div class="m-tag">{mode_info['icon']} {mode_info['label']}</div><br>
              {md_to_html(full_response)}
            </div>
            <div class="m-time">{get_time()}</div>
          </div>
        </div>
        <script>setTimeout(()=>{{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},150);</script>
        """, unsafe_allow_html=True)

    except Exception as e:
        err = str(e)
        if "rate_limit" in err.lower(): full_response = "⏳ Juda ko'p so'rov. Bir daqiqa kuting."
        elif "model"     in err.lower(): full_response = f"❌ Model topilmadi: `{st.session_state.model}`."
        elif "auth"      in err.lower(): full_response = "❌ API kalit xato. GROQ_API_KEY ni tekshiring."
        else:                            full_response = f"❌ Xatolik: {err}"
        typing_ph.markdown(f"""
        <div class="msg-row ai">
          <div class="m-av ai">✏️</div>
          <div class="m-body">
            <div class="m-name">EduCreate AI</div>
            <div class="m-bubble ai">{full_response}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant", "content": full_response,
        "time": get_time(), "mode": current_mode
    })

