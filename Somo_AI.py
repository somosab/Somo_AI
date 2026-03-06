import streamlit as st
from groq import Groq
import time
import re

def md_to_html(text):
    math_blocks = {}
    def save_math(m):
        key = f"__M{len(math_blocks)}__"
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

st.set_page_config(page_title="Somo AI", page_icon="◆", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});"></script>
<style>
  :root {
    --bg:       #f9f9f7;
    --surface:  #ffffff;
    --border:   #e8e8e4;
    --accent:   #d97706;
    --accent2:  #92400e;
    --text:     #1a1a18;
    --sub:      #6b6b63;
    --muted:    #9b9b90;
    --user-bg:  #f0f4ff;
    --user-bdr: #c7d2fe;
    --ai-bg:    #ffffff;
    --code-bg:  #f4f4f0;
    --fn: 'Inter', -apple-system, sans-serif;
  }

  html, body { background: var(--bg) !important; margin: 0; padding: 0; }
  * { box-sizing: border-box; font-family: var(--fn) !important; }
  [data-testid="stAppViewContainer"], [data-testid="stMain"], .main { background: var(--bg) !important; }
  #MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"],
  [data-testid="stStatusWidget"], [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
  .block-container, [data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }

  /* ── HEADER ── */
  .hdr {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.85rem 1.5rem;
    border-bottom: 1px solid var(--border);
    background: rgba(249,249,247,0.95);
    position: sticky; top: 0; z-index: 100;
    backdrop-filter: blur(12px);
    max-width: 100%;
  }
  .hdr-left { display: flex; align-items: center; gap: 10px; }
  .hdr-dot {
    width: 32px; height: 32px;
    background: var(--accent);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 14px; font-weight: 700;
    flex-shrink: 0;
  }
  .hdr-name { font-size: 0.95rem; font-weight: 600; color: var(--text); }
  .hdr-by   { font-size: 0.62rem; color: var(--muted); margin-top: 1px; }
  .hdr-right { display: flex; align-items: center; gap: 6px; }
  .hdr-pill {
    font-size: 0.62rem; color: var(--sub);
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px; padding: 0.22rem 0.65rem;
    white-space: nowrap;
  }
  .hdr-online { font-size: 0.62rem; color: #16a34a; display: flex; align-items: center; gap: 4px; }
  .hdr-online::before { content:''; width:6px; height:6px; background:#16a34a; border-radius:50%; display:inline-block; }

  /* ── CHAT AREA ── */
  .chat-area {
    max-width: 720px; margin: 0 auto;
    padding: 1.8rem 1.4rem 5rem;
  }

  /* Welcome */
  .welcome { padding: 3rem 0 2rem; text-align: center; }
  .wlc-icon {
    width: 52px; height: 52px;
    background: var(--accent);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 22px; font-weight: 700;
    margin: 0 auto 1.2rem;
    box-shadow: 0 4px 16px rgba(217,119,6,0.25);
  }
  .wlc-title { font-size: 1.5rem; font-weight: 600; color: var(--text); margin-bottom: 0.4rem; }
  .wlc-sub   { font-size: 0.85rem; color: var(--sub); line-height: 1.6; max-width: 360px; margin: 0 auto 2rem; }
  .wlc-chips { display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: center; }
  .wlc-chip  {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px; padding: 0.35rem 0.8rem;
    font-size: 0.72rem; color: var(--sub); cursor: default;
    transition: border-color 0.15s;
  }
  .wlc-chip:hover { border-color: var(--accent); color: var(--accent); }

  /* Messages */
  .msg { display: flex; gap: 10px; margin-bottom: 1.2rem; animation: fadeUp 0.2s ease-out; }
  @keyframes fadeUp { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
  .msg.user { flex-direction: row-reverse; }

  .av {
    width: 28px; height: 28px; min-width: 28px;
    border-radius: 7px; display: flex; align-items: center;
    justify-content: center; font-size: 12px;
    flex-shrink: 0; align-self: flex-start; margin-top: 1px;
  }
  .av.user { background: #6366f1; color: white; }
  .av.ai   { background: var(--accent); color: white; font-weight: 700; font-size: 11px; }

  .mbody { max-width: 80%; }
  .mname { font-size: 0.6rem; color: var(--muted); margin-bottom: 0.22rem; letter-spacing: 0.5px; }
  .msg.user .mname { text-align: right; }

  .bubble {
    padding: 0.75rem 1rem; border-radius: 12px;
    font-size: 0.875rem; line-height: 1.7;
    color: var(--text); word-break: break-word;
  }
  .bubble.user {
    background: var(--user-bg);
    border: 1px solid var(--user-bdr);
    border-top-right-radius: 3px;
  }
  .bubble.ai {
    background: var(--ai-bg);
    border: 1px solid var(--border);
    border-top-left-radius: 3px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  }

  /* Bubble content */
  .bubble strong { color: var(--accent2); font-weight: 600; }
  .bubble em     { color: var(--sub); }
  .bubble h1, .bubble h2, .bubble h3 {
    font-weight: 600; color: var(--text);
    margin: 0.75rem 0 0.25rem; font-size: 1rem;
  }
  .bubble h1 { font-size: 1.1rem; }
  .bubble code {
    background: var(--code-bg); border: 1px solid var(--border);
    padding: 0.1rem 0.35rem; border-radius: 4px;
    font-size: 0.8rem; color: #b45309;
    font-family: 'SF Mono', 'Fira Code', monospace !important;
  }
  .bubble pre {
    background: var(--code-bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.85rem; overflow-x: auto; margin: 0.5rem 0;
  }
  .bubble pre code { background: none; border: none; padding: 0; color: #1d4ed8; font-size: 0.78rem; }
  .bubble ul, .bubble ol { padding-left: 1.2rem; margin: 0.3rem 0; }
  .bubble li { margin-bottom: 0.2rem; }
  .bubble blockquote {
    border-left: 2px solid var(--accent);
    padding: 0.4rem 0.8rem; margin: 0.4rem 0;
    color: var(--sub); font-style: italic;
    background: rgba(217,119,6,0.04); border-radius: 0 6px 6px 0;
  }
  .bubble table { border-collapse: collapse; width: 100%; margin: 0.5rem 0; font-size: 0.8rem; }
  .bubble th { background: var(--code-bg); padding: 0.38rem 0.65rem; border: 1px solid var(--border); font-weight: 600; text-align: left; }
  .bubble td { padding: 0.35rem 0.65rem; border: 1px solid var(--border); }
  .bubble tr:nth-child(even) { background: rgba(0,0,0,0.015); }
  .bubble hr { border: none; border-top: 1px solid var(--border); margin: 0.6rem 0; }

  .mtime { font-size: 0.58rem; color: var(--muted); margin-top: 0.22rem; opacity: 0.6; }
  .msg.user .mtime { text-align: right; }

  /* Cursor */
  .cur {
    display: inline-block; width: 2px; height: 0.85em;
    background: var(--accent); margin-left: 2px;
    vertical-align: middle; animation: blink 0.7s steps(1) infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

  /* ── INPUT ── */
  [data-testid="stChatInput"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    margin: 0 1.2rem 1rem !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
  }
  [data-testid="stChatInput"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(217,119,6,0.1), 0 2px 12px rgba(0,0,0,0.06) !important;
  }
  [data-testid="stChatInput"] textarea {
    background: transparent !important; color: var(--text) !important;
    font-size: 0.875rem !important; border: none !important;
    outline: none !important; box-shadow: none !important;
  }
  [data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; }
  [data-testid="stChatInput"] button {
    background: var(--accent) !important; border: none !important;
    border-radius: 8px !important;
  }
  [data-testid="stChatInput"] button svg { fill: white !important; }

  .input-footer {
    text-align: center; font-size: 0.58rem;
    color: var(--muted); padding: 0 0 0.6rem;
    letter-spacing: 0.3px;
  }

  /* ── MOBILE ── */
  @media (max-width: 600px) {
    .hdr { padding: 0.7rem 1rem; }
    .hdr-name { font-size: 0.88rem; }
    .hdr-by { display: none; }
    .chat-area { padding: 1.2rem 0.9rem 5rem; }
    .mbody { max-width: 88%; }
    .bubble { font-size: 0.84rem; padding: 0.65rem 0.85rem; }
    .wlc-title { font-size: 1.25rem; }
    [data-testid="stChatInput"] { margin: 0 0.7rem 0.8rem !important; }
  }

  .katex { font-size: 1em !important; }
  .katex-display { overflow-x: auto; padding: 0.3rem 0; }
  ::-webkit-scrollbar { width: 3px; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Groq ──────────────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("❌ GROQ_API_KEY topilmadi.")
    st.stop()

# ── State ─────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

MODEL   = "llama-3.3-70b-versatile"
MBADGE  = "Llama 3.3 · 70B"

SYSTEM = """You are Somo AI — a smart, multilingual assistant created by Usmonov Sodiq.

IDENTITY (never change):
- Name: Somo AI
- Creator: Usmonov Sodiq
- Brand: Somo_AI
- Not made by OpenAI, Anthropic, Google, or any other company
- If asked who made you: "Men Usmonov Sodiq (Somo_AI) tomonidan yaratilganman"

LANGUAGE: Detect user's language and ALWAYS reply in the same language.
- Uzbek → Uzbek, Russian → Russian, English → English

FORMATTING:
- Use emojis naturally ✨
- **bold** key terms, *italics* for emphasis
- Headers ## ### for long answers
- Lists, tables, code blocks as needed
- Math: $inline$ or $$display$$ LaTeX

PERSONALITY:
- Clear, helpful, friendly
- Concise but thorough
- Never verbose without reason
"""

def get_time():
    return time.strftime("%H:%M")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hdr">
  <div class="hdr-left">
    <div class="hdr-dot">S</div>
    <div>
      <div class="hdr-name">Somo AI</div>
      <div class="hdr-by">by Usmonov Sodiq</div>
    </div>
  </div>
  <div class="hdr-right">
    <div class="hdr-online">Online</div>
    <div class="hdr-pill">{MBADGE}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Messages ──────────────────────────────────────────────────────────────────
st.markdown('<div class="chat-area">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
      <div class="wlc-icon">S</div>
      <div class="wlc-title">Somo AI bilan suhbat</div>
      <div class="wlc-sub">
        Savolingizni yozing — istalgan tilda.<br>
        Esse, she'r, kod, tarjima, matematik masalalar va boshqa har narsa.
      </div>
      <div class="wlc-chips">
        <div class="wlc-chip">✍️ Esse yoz</div>
        <div class="wlc-chip">🌍 Tarjima qil</div>
        <div class="wlc-chip">💻 Kod yoz</div>
        <div class="wlc-chip">🧮 Matematika</div>
        <div class="wlc-chip">💡 G'oya ber</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"]
        ts      = msg.get("time", "")
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

# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.chat_input("Xabar yozing…")
st.markdown('<div class="input-footer">Somo AI · Usmonov Sodiq · Groq</div>', unsafe_allow_html=True)

# ── Process ───────────────────────────────────────────────────────────────────
if prompt and prompt.strip():
    user_text = prompt.strip()
    st.session_state.messages.append({"role": "user", "content": user_text, "time": get_time()})

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

    api_msgs = [{"role": "system", "content": SYSTEM}]
    for m in st.session_state.messages:
        api_msgs.append({"role": m["role"], "content": m["content"]})

    full = ""
    try:
        stream = client.chat.completions.create(
            model=MODEL, messages=api_msgs,
            stream=True, max_tokens=2048, temperature=0.7,
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

    st.session_state.messages.append({"role": "assistant", "content": full, "time": get_time()})
