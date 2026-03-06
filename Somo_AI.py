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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,700;0,9..144,900;1,9..144,400&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[
    {left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}
  ]});"></script>

<style>
  :root {
    --cream:   #fdf6e3;
    --warm:    #f5ead0;
    --card:    #fffef8;
    --border:  #e8dfc8;
    --amber:   #f59e0b;
    --orange:  #ea580c;
    --forest:  #15803d;
    --sky:     #0369a1;
    --rose:    #e11d48;
    --text:    #1c1408;
    --muted:   #7c6d52;
    --light:   #a89878;
    --fh: 'Fraunces', serif;
    --fb: 'DM Sans', sans-serif;
  }

  html, body { background: var(--cream) !important; margin: 0; padding: 0; }
  * { box-sizing: border-box; }

  [data-testid="stAppViewContainer"],
  [data-testid="stMain"], .main { background: var(--cream) !important; }

  #MainMenu, footer, header,
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"] { display: none !important; }

  .block-container,
  [data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }

  /* ══ SIDEBAR ══ */
  [data-testid="stSidebar"] {
    background: var(--warm) !important;
    border-right: 2px solid var(--border) !important;
    min-width: 270px !important;
    max-width: 290px !important;
  }
  [data-testid="stSidebar"] > div,
  [data-testid="stSidebar"] section,
  [data-testid="stSidebarContent"] {
    background: var(--warm) !important;
    padding: 1.4rem 1.1rem !important;
  }

  /* All text inside sidebar */
  [data-testid="stSidebar"] *,
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] div,
  [data-testid="stSidebar"] label {
    color: var(--text) !important;
    font-family: var(--fb) !important;
  }

  /* Sidebar buttons — mode switchers */
  [data-testid="stSidebar"] button {
    background: var(--cream) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: var(--fb) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: var(--text) !important;
    text-align: left !important;
    padding: 0.55rem 0.9rem !important;
    transition: all 0.18s !important;
    width: 100% !important;
    margin-bottom: 0.3rem !important;
  }
  [data-testid="stSidebar"] button:hover {
    background: var(--card) !important;
    border-color: var(--amber) !important;
    color: var(--orange) !important;
    box-shadow: 0 2px 8px rgba(245,158,11,0.18) !important;
  }
  [data-testid="stSidebar"] button p {
    color: inherit !important;
    font-family: var(--fb) !important;
    font-size: 0.82rem !important;
    margin: 0 !important;
  }

  /* Active button highlight */
  [data-testid="stSidebar"] button[kind="secondary"],
  [data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
    background: var(--cream) !important;
  }

  /* Selectbox */
  [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: var(--cream) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-size: 0.8rem !important;
    font-family: var(--fb) !important;
  }
  [data-testid="stSidebar"] [data-testid="stSelectbox"] svg { fill: var(--muted) !important; }

  /* Slider */
  [data-testid="stSidebar"] [data-testid="stSlider"] label { display: none !important; }
  [data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: var(--amber) !important;
  }
  [data-testid="stSidebar"] [data-testid="stSlider"] div[data-testid="stThumbValue"] {
    color: var(--orange) !important;
    font-size: 0.72rem !important;
  }

  /* Clear button — special red style */
  [data-testid="stSidebar"] button[key="clear_btn"],
  [data-testid="stSidebar"] div:last-child button {
    color: var(--muted) !important;
  }
  [data-testid="stSidebar"] div:last-child button:hover {
    border-color: var(--rose) !important;
    color: var(--rose) !important;
    background: rgba(225,29,72,0.06) !important;
  }

  /* Sidebar custom */
  .sb-logo {
    display: flex; align-items: center; gap: 10px;
    padding-bottom: 1.2rem; margin-bottom: 1.4rem;
    border-bottom: 2px dashed var(--border);
  }
  .sb-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, var(--amber), var(--orange));
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 3px 10px rgba(245,158,11,0.35);
  }
  .sb-brand {
    font-family: var(--fh) !important;
    font-size: 1.25rem; font-weight: 900;
    color: var(--text) !important;
    line-height: 1.1;
  }
  .sb-brand span { color: var(--orange); }
  .sb-tagline { font-size: 0.6rem; color: var(--light) !important; letter-spacing: 1.5px; text-transform: uppercase; font-family: var(--fb) !important; }

  .sb-sec {
    font-family: var(--fb) !important;
    font-size: 0.6rem; letter-spacing: 2.5px; text-transform: uppercase;
    color: var(--light) !important; margin: 1.2rem 0 0.5rem;
  }

  /* Mode cards in sidebar */
  .mode-card {
    display: flex; align-items: center; gap: 10px;
    padding: 0.6rem 0.8rem;
    border-radius: 10px;
    border: 1.5px solid transparent;
    cursor: pointer;
    transition: all 0.18s;
    margin-bottom: 0.4rem;
    background: transparent;
  }
  .mode-card:hover { background: var(--cream); border-color: var(--border); }
  .mode-card.active { background: var(--card); border-color: var(--amber); box-shadow: 0 2px 8px rgba(245,158,11,0.18); }
  .mode-icon { font-size: 1.2rem; }
  .mode-label { font-family: var(--fb) !important; font-size: 0.8rem; font-weight: 500; color: var(--text) !important; }
  .mode-desc  { font-family: var(--fb) !important; font-size: 0.65rem; color: var(--light) !important; }

  .sb-divider { height: 1px; background: var(--border); margin: 1.2rem 0; border: none; }

  .sb-stats { padding-top: 0.5rem; }
  .sb-row { display: flex; justify-content: space-between; font-size: 0.7rem; margin-bottom: 0.4rem; font-family: var(--fb) !important; }
  .sb-row .k { color: var(--light) !important; }
  .sb-row .v { color: var(--text) !important; font-weight: 600; }

  /* ══ HEADER ══ */
  .chat-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.9rem 2rem;
    border-bottom: 2px solid var(--border);
    background: rgba(253,246,227,0.96);
    position: sticky; top: 0; z-index: 999;
    backdrop-filter: blur(12px);
  }
  .chat-header-left { display: flex; align-items: center; gap: 12px; }
  .h-avatar {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, var(--amber), var(--orange));
    border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
    box-shadow: 0 3px 12px rgba(245,158,11,0.3);
  }
  .h-title {
    font-family: var(--fh) !important;
    font-size: 1.1rem; font-weight: 900;
    color: var(--text);
  }
  .h-title span { color: var(--orange); }
  .h-mode {
    font-size: 0.62rem; color: var(--muted);
    letter-spacing: 1px; margin-top: 1px;
    font-family: var(--fb) !important;
  }
  .h-right { display: flex; align-items: center; gap: 10px; }
  .h-badge {
    background: var(--warm); border: 1.5px solid var(--border);
    border-radius: 20px; padding: 0.28rem 0.75rem;
    font-size: 0.62rem; color: var(--muted);
    letter-spacing: 1px; font-family: var(--fb) !important;
  }
  .h-lang-badge {
    background: linear-gradient(135deg, var(--forest), #16a34a);
    border-radius: 20px; padding: 0.28rem 0.75rem;
    font-size: 0.62rem; color: white;
    letter-spacing: 1px; font-family: var(--fb) !important;
  }

  /* ══ MESSAGES ══ */
  .msgs-area { padding: 2rem 2rem 1rem; }

  /* Welcome */
  .welcome {
    display: flex; flex-direction: column;
    align-items: center; text-align: center;
    padding: 3rem 2rem;
  }
  .welcome-badge {
    background: linear-gradient(135deg, var(--amber), var(--orange));
    color: white; font-family: var(--fb) !important;
    font-size: 0.65rem; letter-spacing: 2px; text-transform: uppercase;
    padding: 0.3rem 1rem; border-radius: 20px; margin-bottom: 1.2rem;
    box-shadow: 0 3px 12px rgba(245,158,11,0.3);
  }
  .w-title {
    font-family: var(--fh) !important;
    font-size: 2.6rem; font-weight: 900;
    color: var(--text); line-height: 1.1;
    margin-bottom: 0.6rem;
  }
  .w-title span { color: var(--orange); font-style: italic; }
  .w-sub {
    color: var(--muted); font-size: 0.85rem;
    max-width: 420px; line-height: 1.6; margin-bottom: 2.5rem;
    font-family: var(--fb) !important;
  }

  /* Mode grid */
  .mode-grid {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem; width: 100%; max-width: 600px; margin-bottom: 2rem;
  }
  .mode-tile {
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 14px; padding: 1.1rem 0.8rem;
    text-align: center; cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  }
  .mode-tile:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    border-color: var(--amber);
  }
  .mode-tile .t-icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
  .mode-tile .t-name {
    font-family: var(--fb) !important;
    font-size: 0.75rem; font-weight: 600;
    color: var(--text);
  }
  .mode-tile .t-hint {
    font-family: var(--fb) !important;
    font-size: 0.62rem; color: var(--light); margin-top: 0.2rem;
  }

  /* Example prompts */
  .ex-prompts { display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: center; }
  .ex-chip {
    background: var(--warm); border: 1.5px solid var(--border);
    border-radius: 20px; padding: 0.4rem 0.9rem;
    font-size: 0.7rem; color: var(--muted);
    font-family: var(--fb) !important;
    cursor: pointer; transition: all 0.15s;
  }
  .ex-chip:hover { border-color: var(--amber); color: var(--orange); }

  /* Messages */
  .msg-row {
    display: flex; gap: 12px; margin-bottom: 1.5rem;
    animation: fadeUp 0.25s ease-out;
  }
  @keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
  .msg-row.user { flex-direction: row-reverse; }

  .m-av {
    width: 34px; height: 34px; min-width: 34px;
    border-radius: 10px; display: flex;
    align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0; align-self: flex-start;
  }
  .m-av.user { background: linear-gradient(135deg, var(--sky), #0ea5e9); }
  .m-av.ai   { background: linear-gradient(135deg, var(--amber), var(--orange)); box-shadow: 0 2px 8px rgba(245,158,11,0.3); }

  .m-body { max-width: 72%; }
  .m-name {
    font-size: 0.62rem; color: var(--light);
    margin-bottom: 0.3rem; letter-spacing: 1px;
    text-transform: uppercase; font-family: var(--fb) !important;
  }
  .msg-row.user .m-name { text-align: right; }

  .m-bubble {
    padding: 0.9rem 1.15rem; border-radius: 14px;
    font-size: 0.85rem; line-height: 1.75;
    color: var(--text); word-break: break-word;
    font-family: var(--fb) !important;
  }
  .m-bubble.user {
    background: #dbeafe;
    border: 1.5px solid #bfdbfe;
    border-top-right-radius: 4px;
  }
  .m-bubble.ai {
    background: var(--card);
    border: 1.5px solid var(--border);
    border-top-left-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
  .m-bubble strong { color: var(--orange); font-weight: 700; }
  .m-bubble em { color: var(--muted); font-style: italic; }
  .m-bubble h1,.m-bubble h2,.m-bubble h3 {
    font-family: var(--fh) !important;
    color: var(--text); margin: 0.8rem 0 0.3rem;
  }
  .m-bubble code {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.25);
    padding: 0.1rem 0.4rem; border-radius: 5px;
    font-size: 0.8rem; color: var(--orange);
    font-family: monospace !important;
  }
  .m-bubble pre {
    background: var(--warm); border: 1.5px solid var(--border);
    border-radius: 10px; padding: 1rem; overflow-x: auto; margin: 0.6rem 0;
  }
  .m-bubble pre code { background:none; border:none; padding:0; color:var(--forest); font-size:0.78rem; }
  .m-bubble ul,.m-bubble ol { padding-left: 1.2rem; margin: 0.35rem 0; }
  .m-bubble li { margin-bottom: 0.25rem; }
  .m-bubble blockquote {
    border-left: 3px solid var(--amber); padding-left: 0.9rem;
    color: var(--muted); margin: 0.5rem 0; font-style: italic;
    background: rgba(245,158,11,0.05); border-radius: 0 8px 8px 0; padding: 0.5rem 0.9rem;
  }
  .m-bubble table { border-collapse: collapse; width: 100%; margin: 0.6rem 0; font-size: 0.8rem; }
  .m-bubble th {
    background: var(--warm); padding: 0.45rem 0.75rem;
    border: 1.5px solid var(--border); color: var(--orange); font-weight: 700;
  }
  .m-bubble td { padding: 0.4rem 0.75rem; border: 1px solid var(--border); }
  .m-bubble tr:nth-child(even) { background: rgba(0,0,0,0.02); }

  .m-time { font-size: 0.58rem; color: var(--light); margin-top: 0.3rem; opacity: 0.7; font-family: var(--fb) !important; }
  .msg-row.user .m-time { text-align: right; }

  /* Mode tag on bubble */
  .m-mode-tag {
    display: inline-block;
    font-size: 0.58rem; letter-spacing: 1.5px; text-transform: uppercase;
    background: linear-gradient(135deg, var(--amber), var(--orange));
    color: white; padding: 0.15rem 0.5rem; border-radius: 10px;
    margin-bottom: 0.4rem; font-family: var(--fb) !important;
  }

  /* Typing cursor */
  .t-cursor {
    display: inline-block; width: 2px; height: 0.9em;
    background: var(--orange); margin-left: 2px;
    vertical-align: middle;
    animation: blink 0.65s steps(1) infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

  /* ══ CHAT INPUT ══ */
  [data-testid="stChatInput"] {
    background: var(--card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 16px !important;
    margin: 0 2rem 1.5rem !important;
    box-shadow: 0 3px 12px rgba(0,0,0,0.07) !important;
  }
  [data-testid="stChatInput"]:focus-within {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.15) !important;
  }
  [data-testid="stChatInput"] textarea {
    background: transparent !important; color: var(--text) !important;
    font-size: 0.85rem !important; font-family: var(--fb) !important;
    border: none !important; outline: none !important; box-shadow: none !important;
  }
  [data-testid="stChatInput"] textarea::placeholder { color: var(--light) !important; }
  [data-testid="stChatInput"] button {
    background: linear-gradient(135deg, var(--amber), var(--orange)) !important;
    border: none !important; border-radius: 11px !important;
    box-shadow: 0 3px 10px rgba(245,158,11,0.3) !important;
  }
  [data-testid="stChatInput"] button svg { fill: white !important; }

  /* ══ MOBILE ══ */
  @media (max-width: 768px) {
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stMain"], .main,
    [data-testid="stAppViewContainer"] { width: 100% !important; }
    .block-container, [data-testid="stMainBlockContainer"] {
      padding: 0 !important; padding-bottom: 70px !important;
    }
    .chat-header { padding: 0.75rem 1rem; }
    .h-title { font-size: 0.95rem; }
    .msgs-area { padding: 1rem 0.85rem 0.5rem; }
    .m-body { max-width: 86%; }
    .m-bubble { font-size: 0.82rem; }
    .mode-grid { grid-template-columns: repeat(2, 1fr); max-width: 100%; }
    .w-title { font-size: 1.8rem; }
    [data-testid="stChatInput"] { margin: 0 0.75rem 0.75rem !important; }
    .mobile-bar { display: flex !important; }
  }

  /* Mobile bar */
  .mobile-bar {
    display: none; position: fixed;
    bottom: 0; left: 0; right: 0; height: 58px;
    background: rgba(253,246,227,0.97);
    border-top: 2px solid var(--border);
    backdrop-filter: blur(12px); z-index: 1000;
    align-items: center; justify-content: space-around;
  }
  .mob-btn {
    display: flex; flex-direction: column; align-items: center;
    gap: 2px; background: none; border: none; cursor: pointer;
    padding: 0.3rem 0.8rem; border-radius: 10px;
    color: var(--light); font-size: 0.55rem; letter-spacing: 0.5px;
    text-transform: uppercase; font-family: var(--fb) !important;
    -webkit-tap-highlight-color: transparent;
  }
  .mob-btn .icon { font-size: 1.2rem; }
  .mob-btn.active { color: var(--orange); }

  .mob-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(0,0,0,0.25); z-index: 1999;
  }
  .mob-overlay.open { display: block; }

  .mob-drawer {
    display: none; position: fixed;
    bottom: 0; left: 0; right: 0;
    background: var(--warm);
    border-top: 2px solid var(--border);
    border-radius: 20px 20px 0 0;
    z-index: 2000; padding: 1.2rem 1.5rem 2.5rem;
    transform: translateY(100%);
    transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1);
    box-shadow: 0 -8px 32px rgba(0,0,0,0.12);
  }
  .mob-drawer.open { transform: translateY(0); }
  .mob-handle { width: 40px; height: 4px; background: var(--border); border-radius: 2px; margin: 0 auto 1.2rem; }
  .mob-drawer-title { font-family: var(--fh) !important; font-size: 1.1rem; font-weight: 900; color: var(--text); margin-bottom: 1rem; }
  .mob-info-row { display: flex; justify-content: space-between; padding: 0.6rem 0; border-bottom: 1px solid var(--border); font-family: var(--fb) !important; font-size: 0.78rem; }
  .mob-info-row .mk { color: var(--light); }
  .mob-info-row .mv { color: var(--text); font-weight: 600; }
  .mob-close {
    width: 100%; padding: 0.75rem; margin-top: 1.2rem;
    background: linear-gradient(135deg, var(--amber), var(--orange));
    color: white; border: none; border-radius: 12px;
    font-size: 0.85rem; font-family: var(--fb) !important;
    cursor: pointer; font-weight: 600;
    box-shadow: 0 3px 12px rgba(245,158,11,0.3);
  }

  .katex { font-size: 1em !important; }
  .katex-display { overflow-x: auto; padding: 0.4rem 0; }
  ::-webkit-scrollbar { width: 3px; height: 3px; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── Groq Client ─────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("❌ GROQ_API_KEY topilmadi.")
    st.stop()

# ─── Session State ────────────────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "mode"        not in st.session_state: st.session_state.mode        = "esse"
if "lang"        not in st.session_state: st.session_state.lang        = "uz"

MODES = {
    "esse":    {"icon": "✍️",  "label": "Esse / Referat",   "desc": "Maqola yozish",     "color": "#ea580c"},
    "story":   {"icon": "📖",  "label": "Hikoya / She'r",   "desc": "Ijodiy yozuv",      "color": "#7c3aed"},
    "speech":  {"icon": "🎤",  "label": "Nutq / Taqdimot",  "desc": "Chiqish matni",     "color": "#0369a1"},
    "ideas":   {"icon": "🧠",  "label": "G'oya generatsiya","desc": "Beyin fırtınası",   "color": "#15803d"},
    "translate":{"icon":"🌍",  "label": "Tarjimon",         "desc": "UZ ↔ RU ↔ EN",     "color": "#b45309"},
    "summary": {"icon": "📋",  "label": "Xulosa / Tahlil",  "desc": "Matnni tahlil qil", "color": "#be123c"},
}

LANGS = {"uz": "🇺🇿 UZ", "ru": "🇷🇺 RU", "en": "🇬🇧 EN"}

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div class="sb-icon">✏️</div>
      <div>
        <div class="sb-brand">Edu<span>Create</span> AI</div>
        <div class="sb-tagline">Ijodiy AI Yordamchi</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">✨ Yaratish Rejimi</div>', unsafe_allow_html=True)
    for key, m in MODES.items():
        active_class = "active" if st.session_state.mode == key else ""
        if st.button(f"{m['icon']}  {m['label']}", key=f"mode_{key}", use_container_width=True):
            st.session_state.mode = key
            st.rerun()

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sb-sec">🌍 Til / Language</div>', unsafe_allow_html=True)
    lang_options = list(LANGS.keys())
    lang_labels  = list(LANGS.values())
    selected_lang = st.selectbox("Til", lang_labels,
        index=lang_options.index(st.session_state.lang),
        label_visibility="collapsed")
    st.session_state.lang = lang_options[lang_labels.index(selected_lang)]

    st.markdown('<div class="sb-sec">⚙️ Model Sozlamalari</div>', unsafe_allow_html=True)
    model = st.selectbox("Model", [
        "llama-3.3-70b-versatile",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ], label_visibility="collapsed")

    temperature = st.slider("Temp", 0.0, 1.5, 0.85, 0.05, label_visibility="collapsed")
    max_tokens  = st.slider("Tokens", 256, 4096, 2048, 128, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️  Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    cur_mode  = MODES[st.session_state.mode]
    st.markdown(f"""
    <hr class="sb-divider">
    <div class="sb-stats">
      <div class="sb-row"><span class="k">Rejim</span><span class="v">{cur_mode['icon']} {cur_mode['label']}</span></div>
      <div class="sb-row"><span class="k">Til</span><span class="v">{LANGS[st.session_state.lang]}</span></div>
      <div class="sb-row"><span class="k">So'rovlar</span><span class="v">{msg_count}</span></div>
      <div class="sb-row"><span class="k">Creativity</span><span class="v">{temperature}</span></div>
    </div>
    """, unsafe_allow_html=True)

# ─── System Prompts per mode ──────────────────────────────────────────────────
LANG_INSTR = {
    "uz": "ALWAYS respond in Uzbek (O'zbek tilida javob ber).",
    "ru": "ALWAYS respond in Russian (Всегда отвечай на русском языке).",
    "en": "ALWAYS respond in English.",
}

IDENTITY = """
IDENTITY — who you are (CRITICAL, never change this):
- Your name is EduCreate AI
- You were created by Somo_AI (the developer's username/brand)
- You are built on Groq infrastructure using large language models
- You are NOT made by "Metamorf AI", OpenAI, Google, Anthropic, or any other company
- If asked who made you, always say: "Men Somo_AI tomonidan yaratilganman" (or in the user's language)
- Never invent organizations, teams, or backstories about your creation
- Keep identity answers short and honest
"""

MODE_PROMPTS = {
    "esse": """You are EduCreate AI — a creative writing expert for students, created by Somo_AI.
Help write essays, reports, and academic articles. Structure them with intro, body, conclusion.
Use rich formatting: headers, bullet points, quotes. Make content engaging and educational.""",

    "story": """You are EduCreate AI — a creative storytelling assistant for students, created by Somo_AI.
Help write stories, poems, fairy tales, and creative texts. Be imaginative and vivid.
Use beautiful language, metaphors, and narrative techniques. Bring characters to life.""",

    "speech": """You are EduCreate AI — a public speaking coach for students, created by Somo_AI.
Help write speeches, presentations, and performance texts. Make them persuasive and memorable.
Structure with strong opening, key points, powerful closing. Include rhetorical devices.""",

    "ideas": """You are EduCreate AI — a brainstorming and ideation expert for students, created by Somo_AI.
Generate creative ideas, mind maps, project concepts. Think outside the box.
Present ideas in organized lists with explanations. Inspire and motivate.""",

    "translate": """You are EduCreate AI — a multilingual translation expert, created by Somo_AI.
Translate accurately between Uzbek, Russian, and English. Preserve meaning and style.
For student texts, also explain key vocabulary and grammar points.""",

    "summary": """You are EduCreate AI — an analysis and summarization expert for students, created by Somo_AI.
Summarize texts, analyze literature, explain concepts clearly.
Use tables, bullet points, and structured formats. Make complex ideas simple.""",
}

GENERAL_RULES = """
FORMATTING — always use rich markdown:
- Use emojis naturally throughout 🎯✨📚
- **bold** for key terms, *italics* for emphasis
- Headers (##, ###) for structure
- Lists, tables, blockquotes as needed
- For math: $inline$ and $$display$$ LaTeX

PERSONALITY:
- Warm, encouraging, student-friendly 🌟
- Celebrate creativity and effort
- Explain clearly with examples
- Be enthusiastic about learning"""

def get_system_prompt():
    lang_instr = LANG_INSTR.get(st.session_state.lang, LANG_INSTR["uz"])
    mode_instr = MODE_PROMPTS.get(st.session_state.mode, MODE_PROMPTS["esse"])
    return f"{IDENTITY}\n{mode_instr}\n\nLANGUAGE: {lang_instr}\n{GENERAL_RULES}"

# ─── Header ──────────────────────────────────────────────────────────────────
cur_mode = MODES[st.session_state.mode]
m_badge = model.replace("llama-3.3-","L3.3-").replace("-versatile","").replace("llama3-","L3-").replace("-8192","").replace("-32768","").upper()

st.markdown(f"""
<div class="chat-header">
  <div class="chat-header-left">
    <div class="h-avatar">✏️</div>
    <div>
      <div class="h-title">Edu<span>Create</span> AI</div>
      <div class="h-mode">{cur_mode['icon']} {cur_mode['label']} rejimida</div>
    </div>
  </div>
  <div class="h-right">
    <div class="h-lang-badge">{LANGS[st.session_state.lang]}</div>
    <div class="h-badge">{m_badge}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Messages ────────────────────────────────────────────────────────────────
st.markdown('<div class="msgs-area">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome">
      <div class="welcome-badge">✨ O'quvchilar uchun AI Yordamchi</div>
      <div class="w-title">Ijodingizni<br><span>kuchlaytiring</span></div>
      <div class="w-sub">Esse, hikoya, nutq, g'oyalar va tarjima — barchasi bir joyda.
      O'z tilida, o'z uslubida. 🚀</div>
      <div class="mode-grid">
        <div class="mode-tile"><div class="t-icon">✍️</div><div class="t-name">Esse / Referat</div><div class="t-hint">Maqola yozish</div></div>
        <div class="mode-tile"><div class="t-icon">📖</div><div class="t-name">Hikoya / She'r</div><div class="t-hint">Ijodiy yozuv</div></div>
        <div class="mode-tile"><div class="t-icon">🎤</div><div class="t-name">Nutq</div><div class="t-hint">Taqdimot matni</div></div>
        <div class="mode-tile"><div class="t-icon">🧠</div><div class="t-name">G'oyalar</div><div class="t-hint">Beyin fırtınası</div></div>
        <div class="mode-tile"><div class="t-icon">🌍</div><div class="t-name">Tarjimon</div><div class="t-hint">UZ ↔ RU ↔ EN</div></div>
        <div class="mode-tile"><div class="t-icon">📋</div><div class="t-name">Xulosa</div><div class="t-hint">Tahlil qilish</div></div>
      </div>
      <div class="ex-prompts">
        <div class="ex-chip">📝 "Vatan haqida esse yoz"</div>
        <div class="ex-chip">🌹 "Bahor haqida she'r"</div>
        <div class="ex-chip">🎤 "Maktab hayoti haqida nutq"</div>
        <div class="ex-chip">💡 "Biznes g'oyalar ber"</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"]
        ts      = msg.get("time", "")
        msg_mode = msg.get("mode", "")
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
            mode_info = MODES.get(msg_mode, cur_mode)
            st.markdown(f"""
            <div class="msg-row ai">
              <div class="m-av ai">✏️</div>
              <div class="m-body">
                <div class="m-name">EduCreate AI</div>
                <div class="m-bubble ai">
                  <div class="m-mode-tag">{mode_info['icon']} {mode_info['label']}</div><br>
                  {md_to_html(content)}
                </div>
                <div class="m-time">{ts}</div>
              </div>
            </div>
            <script>setTimeout(function(){{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},100);</script>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─── Chat Input ───────────────────────────────────────────────────────────────
placeholders = {
    "esse":    "Esse mavzusini yozing... (masalan: 'Ekologiya haqida esse')",
    "story":   "Hikoya yoki she'r so'rang... (masalan: 'Bahor haqida she'r yoz')",
    "speech":  "Nutq mavzusini kiriting... (masalan: 'Yoshlar haqida nutq')",
    "ideas":   "G'oya so'rang... (masalan: 'Maktab gazetasi uchun g'oyalar')",
    "translate":"Tarjima qilish uchun matn kiriting...",
    "summary": "Tahlil qilmoqchi bo'lgan matnni kiriting...",
}
prompt = st.chat_input(placeholders.get(st.session_state.mode, "Yozing..."))

# ─── Mobile Bar ──────────────────────────────────────────────────────────────
msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
st.markdown(f"""
<div class="mobile-bar">
  <button class="mob-btn active" onclick="window.scrollTo({{top:document.body.scrollHeight,behavior:'smooth'}})">
    <span class="icon">💬</span>Chat
  </button>
  <button class="mob-btn" onclick="openMobDrawer()">
    <span class="icon">{cur_mode['icon']}</span>Rejim
  </button>
  <button class="mob-btn" onclick="openSettingsDrawer()">
    <span class="icon">⚙️</span>Sozlama
  </button>
</div>

<div class="mob-overlay" id="mobOv" onclick="closeAll()"></div>

<div class="mob-drawer" id="settingsDrawer">
  <div class="mob-handle"></div>
  <div class="mob-drawer-title">⚙️ Sozlamalar</div>
  <div class="mob-info-row"><span class="mk">Rejim</span><span class="mv">{cur_mode['icon']} {cur_mode['label']}</span></div>
  <div class="mob-info-row"><span class="mk">Til</span><span class="mv">{LANGS[st.session_state.lang]}</span></div>
  <div class="mob-info-row"><span class="mk">Model</span><span class="mv">{m_badge}</span></div>
  <div class="mob-info-row"><span class="mk">Creativity</span><span class="mv">{temperature}</span></div>
  <div class="mob-info-row"><span class="mk">So'rovlar</span><span class="mv">{msg_count}</span></div>
  <div style="color:#a89878;font-size:0.68rem;margin-top:0.8rem;font-family:'DM Sans',sans-serif;line-height:1.6;">
    💡 Rejim va tilni o'zgartirish uchun desktop versiyadan foydalaning.
  </div>
  <button class="mob-close" onclick="closeAll()">✓ Yopish</button>
</div>

<script>
function openSettingsDrawer(){{
  document.getElementById('settingsDrawer').classList.add('open');
  document.getElementById('mobOv').classList.add('open');
}}
function closeAll(){{
  document.querySelectorAll('.mob-drawer').forEach(d=>d.classList.remove('open'));
  document.getElementById('mobOv').classList.remove('open');
}}
</script>
""", unsafe_allow_html=True)

# ─── Process ─────────────────────────────────────────────────────────────────
def get_time():
    return time.strftime("%H:%M")

if prompt and prompt.strip():
    user_text    = prompt.strip()
    current_mode = st.session_state.mode

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

    api_msgs = [{"role": "system", "content": get_system_prompt()}]
    for m in st.session_state.messages:
        api_msgs.append({"role": m["role"], "content": m["content"]})

    full_response = ""
    mode_info = MODES[current_mode]
    try:
        completion = client.chat.completions.create(
            model=model, messages=api_msgs,
            stream=True, max_tokens=max_tokens, temperature=temperature,
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
                  <div class="m-mode-tag">{mode_info['icon']} {mode_info['label']}</div><br>
                  {md_to_html(full_response)}<span class="t-cursor"></span>
                </div>
              </div>
            </div>
            <script>setTimeout(function(){{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},80);</script>
            """, unsafe_allow_html=True)

        typing_ph.markdown(f"""
        <div class="msg-row ai">
          <div class="m-av ai">✏️</div>
          <div class="m-body">
            <div class="m-name">EduCreate AI</div>
            <div class="m-bubble ai">
              <div class="m-mode-tag">{mode_info['icon']} {mode_info['label']}</div><br>
              {md_to_html(full_response)}
            </div>
            <div class="m-time">{get_time()}</div>
          </div>
        </div>
        <script>setTimeout(function(){{if(typeof renderMathInElement!=='undefined')renderMathInElement(document.body);}},150);</script>
        """, unsafe_allow_html=True)

    except Exception as e:
        err = str(e)
        if "rate_limit" in err.lower(): full_response = "⏳ Juda ko'p so'rov. Bir daqiqa kuting."
        elif "model" in err.lower():    full_response = f"❌ Model topilmadi: `{model}`."
        elif "auth" in err.lower():     full_response = "❌ API kalit xato."
        else:                           full_response = f"❌ Xatolik: {err}"
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
