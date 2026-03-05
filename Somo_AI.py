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
    page_title="Somo AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[
    {left:'$$',right:'$$',display:true},
    {left:'$',right:'$',display:false},
    {left:'\\\\(',right:'\\\\)',display:false},
    {left:'\\\\[',right:'\\\\]',display:true}
  ]});"></script>

<style>
  :root {
    --bg:      #faf8f4;
    --bg2:     #f3f0ea;
    --bg3:     #ede9e0;
    --border:  #ddd8cc;
    --accent:  #6c5ce7;
    --accent2: #a855f7;
    --text:    #1a1814;
    --muted:   #8a8070;
    --user-bg: #ede9ff;
    --ai-bg:   #ffffff;
    --green:   #059669;
    --fh: 'Syne', sans-serif;
    --fm: 'Space Mono', monospace;
  }

  html, body { background: var(--bg) !important; margin: 0; padding: 0; }
  * { font-family: var(--fm) !important; box-sizing: border-box; }

  [data-testid="stAppViewContainer"],
  [data-testid="stMain"], .main { background: var(--bg) !important; }

  /* Hide all Streamlit chrome */
  #MainMenu, footer, header,
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"] { display: none !important; }

  .block-container,
  [data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
  }

  /* ══════════════════════════════════════
     SIDEBAR — Desktop
  ══════════════════════════════════════ */
  [data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 260px !important;
    max-width: 280px !important;
  }
  [data-testid="stSidebar"] > div { padding: 1.4rem 1.1rem !important; }
  [data-testid="stSidebarContent"] { background: var(--bg2) !important; }
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] div { color: var(--text) !important; }
  [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-size: 0.78rem !important;
  }
  [data-testid="stSidebar"] [data-testid="stSelectbox"] svg { fill: var(--muted) !important; }
  [data-testid="stSidebar"] [data-testid="stSlider"] label { display: none !important; }
  [data-testid="stSidebar"] button {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-size: 0.75rem !important;
    transition: all 0.2s !important;
  }
  [data-testid="stSidebar"] button:hover {
    border-color: #e05c6a !important;
    color: #e05c6a !important;
    background: rgba(224,92,106,0.07) !important;
  }

  /* ══════════════════════════════════════
     HEADER BAR
  ══════════════════════════════════════ */
  .chat-header {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1.5rem;
    border-bottom: 1px solid var(--border);
    background: rgba(250,248,244,0.97);
    position: sticky; top: 0; z-index: 999;
    backdrop-filter: blur(12px);
  }
  .chat-header-left { display: flex; align-items: center; gap: 10px; }
  .h-avatar {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
  }
  .h-title {
    font-family: var(--fh) !important;
    font-size: 1rem; font-weight: 800;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .h-online { font-size: 0.62rem; color: var(--green); letter-spacing: 1px; margin-top: 1px; }
  .h-badge {
    background: var(--bg3); border: 1px solid var(--border);
    border-radius: 20px; padding: 0.25rem 0.7rem;
    font-size: 0.6rem; color: var(--muted); letter-spacing: 1.5px;
  }

  /* ══════════════════════════════════════
     MESSAGES
  ══════════════════════════════════════ */
  .msgs-area { padding: 1.5rem 1.5rem 1rem; }

  .welcome {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 3.5rem 1.5rem; text-align: center;
  }
  .w-glyph {
    font-size: 2.8rem; margin-bottom: 1rem;
    filter: drop-shadow(0 0 20px rgba(108,92,231,0.35));
    animation: float 3s ease-in-out infinite;
  }
  @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-7px)} }
  .w-title {
    font-family: var(--fh) !important;
    font-size: 1.8rem; font-weight: 800;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.4rem;
  }
  .w-sub {
    color: var(--muted); font-size: 0.68rem;
    letter-spacing: 2px; text-transform: uppercase; margin-bottom: 1.8rem;
  }
  .w-chips { display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: center; }
  .w-chip {
    background: var(--bg3); border: 1px solid var(--border);
    border-radius: 20px; padding: 0.35rem 0.8rem;
    font-size: 0.68rem; color: var(--muted);
  }

  .msg-row {
    display: flex; gap: 10px; margin-bottom: 1.3rem;
    animation: fadeUp 0.25s ease-out;
  }
  @keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
  .msg-row.user { flex-direction: row-reverse; }

  .m-av {
    width: 30px; height: 30px; min-width: 30px;
    border-radius: 8px; display: flex;
    align-items: center; justify-content: center;
    font-size: 13px; flex-shrink: 0; align-self: flex-start;
  }
  .m-av.user { background: linear-gradient(135deg, var(--accent), var(--accent2)); }
  .m-av.ai   { background: var(--bg3); border: 1px solid var(--border); }

  .m-body { max-width: 78%; }
  .m-name {
    font-size: 0.6rem; color: var(--muted);
    margin-bottom: 0.25rem; letter-spacing: 1px; text-transform: uppercase;
  }
  .msg-row.user .m-name { text-align: right; }

  .m-bubble {
    padding: 0.8rem 1rem; border-radius: 12px;
    font-size: 0.82rem; line-height: 1.75;
    color: var(--text); word-break: break-word;
  }
  .m-bubble.user {
    background: var(--user-bg);
    border: 1px solid rgba(108,92,231,0.3);
    border-top-right-radius: 4px;
  }
  .m-bubble.ai {
    background: var(--ai-bg);
    border: 1px solid var(--border);
    border-top-left-radius: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  }
  .m-bubble code {
    background: rgba(108,92,231,0.08);
    border: 1px solid rgba(108,92,231,0.18);
    padding: 0.1rem 0.35rem; border-radius: 4px;
    font-size: 0.78rem; color: var(--accent);
  }
  .m-bubble pre {
    background: #f0ece3; border: 1px solid var(--border);
    border-radius: 8px; padding: 0.9rem; overflow-x: auto; margin: 0.5rem 0;
  }
  .m-bubble pre code { background:none; border:none; padding:0; color:#4c3d99; font-size:0.76rem; }
  .m-bubble strong { color: #5b4dd1; }
  .m-bubble em { color: #6b7280; }
  .m-bubble h1,.m-bubble h2,.m-bubble h3 {
    font-family: var(--fh) !important;
    color: var(--text); margin: 0.6rem 0 0.25rem;
  }
  .m-bubble ul,.m-bubble ol { padding-left: 1.1rem; margin: 0.3rem 0; }
  .m-bubble li { margin-bottom: 0.2rem; }
  .m-bubble blockquote {
    border-left: 3px solid var(--accent); padding-left: 0.8rem;
    color: var(--muted); margin: 0.4rem 0; font-style: italic;
  }
  .m-bubble table { border-collapse: collapse; width: 100%; margin: 0.5rem 0; font-size: 0.76rem; }
  .m-bubble th {
    background: var(--bg3); padding: 0.4rem 0.7rem;
    border: 1px solid var(--border); color: var(--accent); font-weight: 600;
  }
  .m-bubble td { padding: 0.35rem 0.7rem; border: 1px solid var(--border); }
  .m-bubble tr:nth-child(even) { background: rgba(0,0,0,0.02); }
  .m-time { font-size: 0.58rem; color: var(--muted); margin-top: 0.25rem; opacity: 0.5; }
  .msg-row.user .m-time { text-align: right; }

  /* Typing cursor */
  .t-cursor {
    display: inline-block; width: 2px; height: 0.85em;
    background: var(--accent); margin-left: 2px;
    vertical-align: middle;
    animation: blink 0.65s steps(1) infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

  /* ══════════════════════════════════════
     CHAT INPUT
  ══════════════════════════════════════ */
  [data-testid="stChatInput"] {
    background: var(--ai-bg) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 14px !important;
    margin: 0 1.5rem 1.2rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
  }
  [data-testid="stChatInput"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(108,92,231,0.12) !important;
  }
  [data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    font-size: 0.84rem !important;
    border: none !important; outline: none !important; box-shadow: none !important;
  }
  [data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; }
  [data-testid="stChatInput"] button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    border: none !important; border-radius: 10px !important;
    color: white !important;
    transition: opacity 0.2s !important;
  }
  [data-testid="stChatInput"] button:hover { opacity: 0.85 !important; }
  [data-testid="stChatInput"] button svg { fill: white !important; }

  /* ══════════════════════════════════════
     SIDEBAR CUSTOM HTML
  ══════════════════════════════════════ */
  .sb-logo {
    display: flex; align-items: center; gap: 10px;
    padding-bottom: 1.1rem; margin-bottom: 1.3rem;
    border-bottom: 1px solid var(--border);
  }
  .sb-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 9px; display: flex;
    align-items: center; justify-content: center; font-size: 16px;
  }
  .sb-brand {
    font-family: var(--fh) !important; font-size: 1.15rem; font-weight: 800;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .sb-ver { font-size: 0.56rem; color: var(--muted) !important; letter-spacing: 2px; text-transform: uppercase; }
  .sb-sec {
    font-size: 0.58rem; letter-spacing: 3px; text-transform: uppercase;
    color: var(--muted) !important; margin: 1.1rem 0 0.45rem;
  }
  .sb-stats { margin-top: 1.8rem; padding-top: 1.1rem; border-top: 1px solid var(--border); }
  .sb-row { display: flex; justify-content: space-between; font-size: 0.67rem; margin-bottom: 0.35rem; }
  .sb-row .k { color: var(--muted) !important; }
  .sb-row .v { color: var(--text) !important; font-weight: 600; }

  /* ══════════════════════════════════════
     MOBILE RESPONSIVE  (≤ 768px)
  ══════════════════════════════════════ */
  @media (max-width: 768px) {

    /* Collapse Streamlit sidebar completely */
    [data-testid="stSidebar"] {
      display: none !important;
    }
    /* Hide sidebar toggle arrow */
    [data-testid="collapsedControl"],
    button[kind="header"] { display: none !important; }

    /* Full width main */
    [data-testid="stMain"], .main,
    [data-testid="stAppViewContainer"] { width: 100% !important; }

    .block-container,
    [data-testid="stMainBlockContainer"] {
      padding: 0 !important;
      padding-bottom: 70px !important;
    }

    /* Header compact */
    .chat-header { padding: 0.75rem 1rem; }
    .h-title { font-size: 0.9rem; }
    .h-online { font-size: 0.58rem; }

    /* Show mobile bottom bar */
    .mobile-bar { display: flex !important; }

    /* Messages full width */
    .msgs-area { padding: 1rem 0.9rem 0.5rem; }
    .m-body { max-width: 85%; }
    .m-bubble { font-size: 0.8rem; padding: 0.7rem 0.85rem; }

    /* Welcome screen smaller */
    .welcome { padding: 2.5rem 1rem; }
    .w-title { font-size: 1.5rem; }
    .w-chip { font-size: 0.65rem; padding: 0.3rem 0.65rem; }

    /* Chat input full width */
    [data-testid="stChatInput"] {
      margin: 0 0.75rem 0.75rem !important;
      border-radius: 12px !important;
    }

    /* Mobile drawer overlay */
    .mob-drawer {
      display: block !important;
    }
  }

  /* ── Mobile bottom navigation bar ── */
  .mobile-bar {
    display: none;
    position: fixed;
    bottom: 0; left: 0; right: 0;
    height: 56px;
    background: rgba(250,248,244,0.97);
    border-top: 1px solid var(--border);
    backdrop-filter: blur(12px);
    z-index: 1000;
    align-items: center;
    justify-content: space-around;
    padding: 0 1rem;
  }
  .mob-btn {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 3px; background: none; border: none;
    cursor: pointer; padding: 0.3rem 0.6rem;
    border-radius: 10px;
    transition: background 0.15s;
    color: var(--muted);
    font-size: 0.56rem;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    -webkit-tap-highlight-color: transparent;
  }
  .mob-btn:active { background: var(--bg3); }
  .mob-btn .icon { font-size: 1.2rem; }
  .mob-btn.active { color: var(--accent); }

  /* ── Mobile drawer (slide-up settings panel) ── */
  .mob-drawer {
    display: none;
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: var(--bg2);
    border-top: 1px solid var(--border);
    border-radius: 20px 20px 0 0;
    z-index: 2000;
    padding: 1.2rem 1.5rem 2.5rem;
    transform: translateY(100%);
    transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1);
    box-shadow: 0 -8px 32px rgba(0,0,0,0.12);
  }
  .mob-drawer.open { transform: translateY(0); }
  .mob-drawer-handle {
    width: 40px; height: 4px;
    background: var(--border);
    border-radius: 2px;
    margin: 0 auto 1.2rem;
  }
  .mob-drawer-title {
    font-family: var(--fh) !important;
    font-size: 1rem; font-weight: 700;
    color: var(--text);
    margin-bottom: 1.2rem;
  }
  .mob-setting-row {
    margin-bottom: 1rem;
  }
  .mob-setting-label {
    font-size: 0.62rem; letter-spacing: 2px;
    text-transform: uppercase; color: var(--muted);
    margin-bottom: 0.4rem;
  }
  .mob-model-list {
    display: flex; flex-direction: column; gap: 0.4rem;
  }
  .mob-model-item {
    padding: 0.55rem 0.9rem;
    background: var(--bg3); border: 1px solid var(--border);
    border-radius: 8px; font-size: 0.75rem; color: var(--text);
    cursor: pointer; transition: all 0.15s;
    -webkit-tap-highlight-color: transparent;
  }
  .mob-model-item.selected {
    background: var(--user-bg);
    border-color: var(--accent);
    color: var(--accent);
  }
  .mob-close-btn {
    width: 100%; padding: 0.7rem;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: white; border: none; border-radius: 10px;
    font-size: 0.82rem; cursor: pointer; margin-top: 1rem;
    font-family: var(--fm) !important;
    -webkit-tap-highlight-color: transparent;
  }
  .mob-overlay {
    display: none;
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.3);
    z-index: 1999;
    backdrop-filter: blur(2px);
  }
  .mob-overlay.open { display: block; }

  /* KaTeX */
  .katex { font-size: 1em !important; color: var(--text) !important; }
  .katex-display { overflow-x: auto; padding: 0.4rem 0; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 3px; height: 3px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: #c8c0b0; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── Groq Client ─────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("❌ GROQ_API_KEY topilmadi. Streamlit Secrets ga qo'shing.")
    st.stop()

# ─── Session State ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div class="sb-icon">✦</div>
      <div>
        <div class="sb-brand">Somo AI</div>
        <div class="sb-ver">V2.0 · GROQ</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">Model</div>', unsafe_allow_html=True)
    model = st.selectbox("Model", [
        "llama-3.3-70b-versatile",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ], label_visibility="collapsed")

    st.markdown('<div class="sb-sec">Temperature</div>', unsafe_allow_html=True)
    temperature = st.slider("Temp", 0.0, 1.5, 0.7, 0.05, label_visibility="collapsed")

    st.markdown('<div class="sb-sec">Max Tokens</div>', unsafe_allow_html=True)
    max_tokens = st.slider("Tokens", 256, 4096, 1024, 128, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⟳  Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    model_short = model.split("-")[0].upper()
    st.markdown(f"""
    <div class="sb-stats">
      <div class="sb-row"><span class="k">Messages</span><span class="v">{msg_count}</span></div>
      <div class="sb-row"><span class="k">Model</span><span class="v">{model_short}</span></div>
      <div class="sb-row"><span class="k">Temp</span><span class="v">{temperature}</span></div>
      <div class="sb-row"><span class="k">Max tokens</span><span class="v">{max_tokens}</span></div>
    </div>
    """, unsafe_allow_html=True)

# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Somo AI — a highly intelligent, multilingual AI assistant powered by Groq.

LANGUAGE RULES:
- CRITICAL: Always detect the user's language and respond in the EXACT SAME language
- User writes Uzbek → respond in Uzbek
- User writes Russian → respond in Russian
- User writes Spanish → respond in Spanish
- Default to English only if language is unclear

FORMATTING — always use rich markdown:
- Use emojis naturally and contextually throughout responses 🎯✨🔥
- **bold** for key terms and emphasis
- *italics* for nuance or examples
- `code` for technical terms, file names, commands
- Headers (## ###) for structured long answers
- Lists, tables, blockquotes where appropriate
- Code blocks with language tags for code snippets

MATH & SCIENCE — always use LaTeX:
- Inline: $expression$ — e.g., $2^4 = 16$, $\\frac{a}{b}$
- Display: $$expression$$ — e.g., $$E = mc^2$$, $$\\int_0^\\infty e^{-x}dx = 1$$
- Always show working steps for math problems

PERSONALITY:
- Warm, precise, enthusiastic 🤝
- Clever and occasionally witty
- Always thorough but concise
- Structure long answers with clear sections"""

# ─── Header ──────────────────────────────────────────────────────────────────
m_badge = (model
    .replace("llama-3.3-","L3.3-").replace("-versatile","")
    .replace("llama3-","L3-").replace("-8192","").replace("-32768","").upper())

st.markdown(f"""
<div class="chat-header">
  <div class="chat-header-left">
    <div class="h-avatar">✦</div>
    <div>
      <div class="h-title">Somo AI</div>
      <div class="h-online">● ONLINE</div>
    </div>
  </div>
  <div class="h-badge">{m_badge}</div>
</div>
""", unsafe_allow_html=True)

# ─── Messages Area ────────────────────────────────────────────────────────────
st.markdown('<div class="msgs-area">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
      <div class="w-glyph">✦</div>
      <div class="w-title">Somo AI</div>
      <div class="w-sub">Multilingual · Smart · Fast</div>
      <div class="w-chips">
        <div class="w-chip">🧮 Math &amp; Science</div>
        <div class="w-chip">💬 Any language</div>
        <div class="w-chip">💻 Code &amp; Debug</div>
        <div class="w-chip">📊 Data Analysis</div>
        <div class="w-chip">✍️ Creative writing</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        ts = msg.get("time", "")
        if role == "user":
            st.markdown(f"""
            <div class="msg-row user">
              <div class="m-av user">👤</div>
              <div class="m-body">
                <div class="m-name">You</div>
                <div class="m-bubble user">{content}</div>
                <div class="m-time">{ts}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-row ai">
              <div class="m-av ai">✦</div>
              <div class="m-body">
                <div class="m-name">Somo AI</div>
                <div class="m-bubble ai">{md_to_html(content)}</div>
                <div class="m-time">{ts}</div>
              </div>
            </div>
            <script>setTimeout(function(){{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},100);</script>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─── Chat Input ───────────────────────────────────────────────────────────────
prompt = st.chat_input("Message Somo AI… (any language)")

# ─── Mobile Bottom Bar + Drawer ──────────────────────────────────────────────
st.markdown(f"""
<!-- Mobile bottom navigation -->
<div class="mobile-bar" id="mobileBar">
  <button class="mob-btn active" onclick="scrollToBottom()">
    <span class="icon">💬</span>Chat
  </button>
  <button class="mob-btn" onclick="clearChat()">
    <span class="icon">🗑️</span>Clear
  </button>
  <button class="mob-btn" onclick="openDrawer()">
    <span class="icon">⚙️</span>Settings
  </button>
</div>

<!-- Overlay -->
<div class="mob-overlay" id="mobOverlay" onclick="closeDrawer()"></div>

<!-- Slide-up settings drawer -->
<div class="mob-drawer" id="mobDrawer">
  <div class="mob-drawer-handle"></div>
  <div class="mob-drawer-title">⚙️ Settings</div>

  <div class="mob-setting-row">
    <div class="mob-setting-label">Current Model</div>
    <div style="font-size:0.75rem; color:var(--accent); padding:0.4rem 0.9rem; background:var(--user-bg); border:1px solid var(--accent); border-radius:8px; display:inline-block;">
      {model}
    </div>
  </div>

  <div class="mob-setting-row">
    <div class="mob-setting-label">Temperature</div>
    <div style="font-size:0.8rem; color:var(--text); font-weight:600;">{temperature}</div>
  </div>

  <div class="mob-setting-row">
    <div class="mob-setting-label">Max Tokens</div>
    <div style="font-size:0.8rem; color:var(--text); font-weight:600;">{max_tokens}</div>
  </div>

  <div class="mob-setting-row" style="margin-top:1rem;">
    <div class="mob-setting-label">Stats</div>
    <div style="font-size:0.75rem; color:var(--muted);">
      {msg_count} messages sent
    </div>
  </div>

  <div style="color:var(--muted);font-size:0.68rem;margin-top:0.8rem;line-height:1.6;">
    💡 To change model/temperature, use the sidebar on desktop or rotate your device.
  </div>

  <button class="mob-close-btn" onclick="closeDrawer()">✓ Close</button>
</div>

<script>
function openDrawer() {{
  document.getElementById('mobDrawer').classList.add('open');
  document.getElementById('mobOverlay').classList.add('open');
}}
function closeDrawer() {{
  document.getElementById('mobDrawer').classList.remove('open');
  document.getElementById('mobOverlay').classList.remove('open');
}}
function scrollToBottom() {{
  window.scrollTo({{top: document.body.scrollHeight, behavior: 'smooth'}});
}}
function clearChat() {{
  if(confirm('Clear all messages?')) {{
    window.location.reload();
  }}
}}
</script>
""", unsafe_allow_html=True)

# ─── Process ─────────────────────────────────────────────────────────────────
def get_time():
    return time.strftime("%H:%M")

if prompt and prompt.strip():
    user_text = prompt.strip()
    st.session_state.messages.append({"role": "user", "content": user_text, "time": get_time()})

    st.markdown(f"""
    <div class="msg-row user">
      <div class="m-av user">👤</div>
      <div class="m-body">
        <div class="m-name">You</div>
        <div class="m-bubble user">{user_text}</div>
        <div class="m-time">{get_time()}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    typing_ph = st.empty()
    typing_ph.markdown("""
    <div class="msg-row ai">
      <div class="m-av ai">✦</div>
      <div class="m-body">
        <div class="m-name">Somo AI</div>
        <div class="m-bubble ai"><span class="t-cursor"></span></div>
      </div>
    </div>""", unsafe_allow_html=True)

    messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in st.session_state.messages:
        messages_for_api.append({"role": m["role"], "content": m["content"]})

    full_response = ""
    try:
        completion = client.chat.completions.create(
            model=model, messages=messages_for_api,
            stream=True, max_tokens=max_tokens, temperature=temperature,
        )
        for chunk in completion:
            delta = chunk.choices[0].delta.content or ""
            full_response += delta
            typing_ph.markdown(f"""
            <div class="msg-row ai">
              <div class="m-av ai">✦</div>
              <div class="m-body">
                <div class="m-name">Somo AI</div>
                <div class="m-bubble ai">{md_to_html(full_response)}<span class="t-cursor"></span></div>
              </div>
            </div>
            <script>setTimeout(function(){{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},80);</script>
            """, unsafe_allow_html=True)

        typing_ph.markdown(f"""
        <div class="msg-row ai">
          <div class="m-av ai">✦</div>
          <div class="m-body">
            <div class="m-name">Somo AI</div>
            <div class="m-bubble ai">{md_to_html(full_response)}</div>
            <div class="m-time">{get_time()}</div>
          </div>
        </div>
        <script>setTimeout(function(){{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},150);</script>
        """, unsafe_allow_html=True)

    except Exception as e:
        err = str(e)
        if "rate_limit" in err.lower():    full_response = "⏳ Too many requests. Please wait."
        elif "model" in err.lower():       full_response = f"❌ Model not found: `{model}`."
        elif "auth" in err.lower():        full_response = "❌ Invalid API key."
        else:                              full_response = f"❌ Error: {err}"
        typing_ph.markdown(f"""
        <div class="msg-row ai">
          <div class="m-av ai">✦</div>
          <div class="m-body">
            <div class="m-name">Somo AI</div>
            <div class="m-bubble ai">{md_to_html(full_response)}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": full_response, "time": get_time()})
