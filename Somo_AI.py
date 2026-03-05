import streamlit as st
from groq import Groq
import time
import re

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Somo AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {
    delimiters: [
      {left: '$$', right: '$$', display: true},
      {left: '$', right: '$', display: false},
      {left: '\\\\(', right: '\\\\)', display: false},
      {left: '\\\\[', right: '\\\\]', display: true}
    ]
  });"></script>

<style>
  :root {
    --bg:        #0a0a0f;
    --bg2:       #111118;
    --bg3:       #1a1a24;
    --border:    #2a2a3a;
    --accent:    #7c6af7;
    --accent2:   #c084fc;
    --text:      #e8e8f0;
    --muted:     #6b6b80;
    --user-bg:   #1e1b3a;
    --ai-bg:     #141420;
    --green:     #34d399;
    --font-head: 'Syne', sans-serif;
    --font-mono: 'Space Mono', monospace;
  }

  /* ── Global reset ── */
  html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
  }

  /* Hide Streamlit branding */
  #MainMenu, footer, header,
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"] { display: none !important; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
  }
  [data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1.2rem !important; }

  .sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 2rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid var(--border);
  }
  .sidebar-logo .icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }
  .sidebar-logo .brand {
    font-family: var(--font-head);
    font-size: 1.3rem;
    font-weight: 800;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
  }
  .sidebar-logo .version {
    font-size: 0.6rem;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: -2px;
  }

  .sidebar-section-title {
    font-size: 0.65rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin: 1.5rem 0 0.6rem 0;
  }

  /* Selectbox */
  [data-testid="stSelectbox"] label { display: none !important; }
  [data-testid="stSelectbox"] > div > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
  }

  /* Slider */
  [data-testid="stSlider"] label { color: var(--muted) !important; font-size: 0.75rem !important; }
  [data-testid="stSlider"] [data-testid="stTickBarMin"],
  [data-testid="stSlider"] [data-testid="stTickBarMax"] { color: var(--muted) !important; font-size: 0.7rem !important; }

  /* Clear button */
  .clear-btn {
    width: 100%;
    padding: 0.55rem 0;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
    margin-top: 0.5rem;
    letter-spacing: 1px;
  }
  .clear-btn:hover {
    border-color: #e05c6a;
    color: #e05c6a;
    background: rgba(224,92,106,0.06);
  }

  .sidebar-stats {
    margin-top: auto;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
  }
  .stat-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    color: var(--muted);
    margin-bottom: 0.4rem;
  }
  .stat-row span:last-child { color: var(--text); }

  /* ── Main area ── */
  [data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
  }
  .block-container {
    padding: 0 !important;
    max-width: 100% !important;
  }

  /* ── Header ── */
  .chat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 2.5rem;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(10px);
  }
  .chat-header-left { display: flex; align-items: center; gap: 12px; }
  .header-avatar {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
  }
  .header-title {
    font-family: var(--font-head);
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text);
  }
  .header-subtitle { font-size: 0.68rem; color: var(--green); letter-spacing: 1px; }
  .header-model-badge {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 1px;
  }

  /* ── Chat area ── */
  .chat-area {
    padding: 2rem 2.5rem;
    min-height: calc(100vh - 200px);
  }

  .welcome-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem 2rem;
    text-align: center;
  }
  .welcome-glyph {
    font-size: 3.5rem;
    margin-bottom: 1.5rem;
    filter: drop-shadow(0 0 30px rgba(124,106,247,0.5));
    animation: float 3s ease-in-out infinite;
  }
  @keyframes float {
    0%,100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
  }
  .welcome-title {
    font-family: var(--font-head);
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.8rem;
  }
  .welcome-sub {
    color: var(--muted);
    font-size: 0.8rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
  }
  .welcome-chips {
    display: flex;
    gap: 0.7rem;
    flex-wrap: wrap;
    justify-content: center;
  }
  .chip {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.45rem 1rem;
    font-size: 0.72rem;
    color: var(--muted);
    cursor: pointer;
    transition: all 0.2s;
  }
  .chip:hover {
    border-color: var(--accent);
    color: var(--accent);
  }

  /* ── Messages ── */
  .msg-wrapper {
    display: flex;
    gap: 14px;
    margin-bottom: 1.8rem;
    animation: fadeSlide 0.3s ease-out;
  }
  @keyframes fadeSlide {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .msg-wrapper.user { flex-direction: row-reverse; }

  .msg-avatar {
    width: 34px; height: 34px; min-width: 34px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
  }
  .msg-avatar.user { background: linear-gradient(135deg, var(--accent), var(--accent2)); }
  .msg-avatar.ai   { background: var(--bg3); border: 1px solid var(--border); }

  .msg-body { max-width: 72%; }
  .msg-name {
    font-size: 0.65rem;
    color: var(--muted);
    margin-bottom: 0.35rem;
    letter-spacing: 1px;
    text-transform: uppercase;
  }
  .msg-wrapper.user .msg-name { text-align: right; }

  .msg-bubble {
    padding: 0.9rem 1.2rem;
    border-radius: 14px;
    font-size: 0.85rem;
    line-height: 1.7;
    color: var(--text);
    position: relative;
  }
  .msg-bubble.user {
    background: var(--user-bg);
    border: 1px solid rgba(124,106,247,0.3);
    border-top-right-radius: 4px;
  }
  .msg-bubble.ai {
    background: var(--ai-bg);
    border: 1px solid var(--border);
    border-top-left-radius: 4px;
  }

  .msg-bubble code {
    background: rgba(124,106,247,0.12);
    border: 1px solid rgba(124,106,247,0.2);
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-size: 0.82rem;
    color: var(--accent2);
  }
  .msg-bubble pre {
    background: #0d0d18;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    overflow-x: auto;
    margin: 0.7rem 0;
  }
  .msg-bubble pre code {
    background: none;
    border: none;
    padding: 0;
    color: #a8b9ff;
    font-size: 0.8rem;
  }
  .msg-bubble strong { color: var(--accent2); }
  .msg-bubble em { color: #94a3b8; }
  .msg-bubble h1, .msg-bubble h2, .msg-bubble h3 {
    font-family: var(--font-head);
    color: var(--text);
    margin: 0.8rem 0 0.4rem;
  }
  .msg-bubble ul, .msg-bubble ol {
    padding-left: 1.3rem;
    margin: 0.4rem 0;
  }
  .msg-bubble li { margin-bottom: 0.3rem; }
  .msg-bubble blockquote {
    border-left: 3px solid var(--accent);
    padding-left: 1rem;
    color: var(--muted);
    margin: 0.5rem 0;
    font-style: italic;
  }
  .msg-bubble table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.7rem 0;
    font-size: 0.8rem;
  }
  .msg-bubble th {
    background: var(--bg3);
    padding: 0.5rem 0.8rem;
    border: 1px solid var(--border);
    text-align: left;
    color: var(--accent2);
    font-weight: 600;
  }
  .msg-bubble td {
    padding: 0.45rem 0.8rem;
    border: 1px solid var(--border);
  }
  .msg-bubble tr:nth-child(even) { background: rgba(255,255,255,0.02); }

  .msg-time {
    font-size: 0.62rem;
    color: var(--muted);
    margin-top: 0.35rem;
    opacity: 0.6;
  }
  .msg-wrapper.user .msg-time { text-align: right; }

  /* Typing cursor */
  .typing-cursor {
    display: inline-block;
    width: 2px;
    height: 1em;
    background: var(--accent);
    margin-left: 2px;
    vertical-align: middle;
    animation: blink 0.7s steps(1) infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

  /* ── Input area ── */
  .input-area {
    position: sticky;
    bottom: 0;
    background: linear-gradient(to top, var(--bg) 80%, transparent);
    padding: 1.2rem 2.5rem 1.8rem;
  }
  .input-wrapper {
    display: flex;
    gap: 10px;
    align-items: flex-end;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 0.6rem 0.6rem 0.6rem 1rem;
    transition: border-color 0.2s;
  }
  .input-wrapper:focus-within { border-color: var(--accent); }

  /* Override streamlit text_area */
  [data-testid="stTextArea"] { flex: 1; }
  [data-testid="stTextArea"] label { display: none !important; }
  [data-testid="stTextArea"] textarea {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.85rem !important;
    resize: none !important;
    min-height: 24px !important;
    padding: 4px 0 !important;
  }
  [data-testid="stTextArea"] textarea::placeholder { color: var(--muted) !important; }

  /* Send button */
  [data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.2rem !important;
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
    cursor: pointer !important;
    transition: opacity 0.2s !important;
    white-space: nowrap !important;
  }
  [data-testid="stButton"] > button:hover { opacity: 0.85 !important; }

  /* KaTeX styling */
  .katex { font-size: 1em !important; color: var(--text) !important; }
  .katex-display { overflow-x: auto; padding: 0.5rem 0; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--muted); }
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
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <div class="icon">✦</div>
      <div>
        <div class="brand">Somo AI</div>
        <div class="version">v2.0 · Groq</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">Model</div>', unsafe_allow_html=True)
    model = st.selectbox("Model", [
        "llama-3.3-70b-versatile",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ], label_visibility="collapsed")

    st.markdown('<div class="sidebar-section-title">Temperature</div>', unsafe_allow_html=True)
    temperature = st.slider("Temp", 0.0, 1.5, 0.7, 0.05, label_visibility="collapsed")

    st.markdown('<div class="sidebar-section-title">Max Tokens</div>', unsafe_allow_html=True)
    max_tokens = st.slider("Tokens", 256, 4096, 1024, 128, label_visibility="collapsed")

    if st.button("⟳  Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.markdown(f"""
    <div class="sidebar-stats">
      <div class="stat-row"><span>Messages</span><span>{msg_count}</span></div>
      <div class="stat-row"><span>Model</span><span>{model.split('-')[0]}</span></div>
      <div class="stat-row"><span>Temp</span><span>{temperature}</span></div>
    </div>
    """, unsafe_allow_html=True)

# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Somo AI, a highly intelligent, multilingual assistant. 

LANGUAGE RULES:
- Default language: English
- CRITICAL: Detect the user's language and ALWAYS respond in the SAME language they used
- If user writes in Uzbek → respond in Uzbek
- If user writes in Russian → respond in Russian  
- If user writes in Spanish → respond in Spanish
- And so on for any language

FORMATTING RULES:
- Use emojis naturally and contextually throughout your responses 🎯
- Use **bold** for emphasis and important terms
- Use *italics* for nuance or examples
- Use `code` for technical terms, commands, variable names
- Use proper markdown: headers (##, ###), lists, tables, blockquotes
- For math: ALWAYS use LaTeX notation wrapped in $ for inline ($x^2$) or $$ for display ($$E=mc^2$$)
- Format mathematical expressions beautifully: fractions, powers, integrals, etc.
- Use code blocks with language tags for programming

PERSONALITY:
- Friendly, precise, and genuinely helpful 🤝
- Use natural conversational flow
- Be enthusiastic about complex topics
- Show personality with appropriate humor when suitable
- Always structure longer answers with clear sections

MATH/SCIENCE:
- Always render math with LaTeX: $2^2 = 4$, $$\\int_0^\\infty e^{-x} dx = 1$$
- Explain steps clearly
- Use tables for comparisons"""

# ─── Header ──────────────────────────────────────────────────────────────────
model_short = model.replace("llama-3.3-", "").replace("-versatile", "").replace("llama3-", "").replace("-8192", "").replace("-32768", "").upper()
st.markdown(f"""
<div class="chat-header">
  <div class="chat-header-left">
    <div class="header-avatar">✦</div>
    <div>
      <div class="header-title">Somo AI</div>
      <div class="header-subtitle">● ONLINE</div>
    </div>
  </div>
  <div class="header-model-badge">{model_short}</div>
</div>
""", unsafe_allow_html=True)

# ─── Chat Display ─────────────────────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-screen">
          <div class="welcome-glyph">✦</div>
          <div class="welcome-title">Somo AI</div>
          <div class="welcome-sub">Multilingual · Smart · Fast</div>
          <div class="welcome-chips">
            <div class="chip">🧮 Solve math problems</div>
            <div class="chip">💬 Chat in any language</div>
            <div class="chip">💻 Write & debug code</div>
            <div class="chip">📊 Analyze data</div>
            <div class="chip">✍️ Creative writing</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        import datetime
        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            ts = msg.get("time", "")
            if role == "user":
                st.markdown(f"""
                <div class="msg-wrapper user">
                  <div class="msg-avatar user">👤</div>
                  <div class="msg-body">
                    <div class="msg-name">You</div>
                    <div class="msg-bubble user">{content}</div>
                    <div class="msg-time">{ts}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-wrapper ai">
                  <div class="msg-avatar ai">✦</div>
                  <div class="msg-body">
                    <div class="msg-name">Somo AI</div>
                    <div class="msg-bubble ai" id="msg-{len(st.session_state.messages)}">{content}</div>
                    <div class="msg-time">{ts}</div>
                  </div>
                </div>
                <script>
                  if(typeof renderMathInElement !== 'undefined') {{
                    renderMathInElement(document.body);
                  }}
                </script>
                """, unsafe_allow_html=True)

# ─── Input Area ───────────────────────────────────────────────────────────────
st.markdown('<div class="input-area">', unsafe_allow_html=True)

col1, col2 = st.columns([11, 1])
with col1:
    user_input = st.text_area(
        "Message",
        placeholder="Message Somo AI... (any language)",
        key=f"input_{st.session_state.input_key}",
        height=52,
        label_visibility="collapsed"
    )
with col2:
    send = st.button("↑", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─── Handle Send ─────────────────────────────────────────────────────────────
def get_time():
    return time.strftime("%H:%M")

def process_message(prompt):
    import datetime

    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": get_time()
    })

    messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in st.session_state.messages:
        messages_for_api.append({"role": m["role"], "content": m["content"]})

    # Typing animation placeholder
    typing_placeholder = st.empty()
    typing_placeholder.markdown("""
    <div class="msg-wrapper ai">
      <div class="msg-avatar ai">✦</div>
      <div class="msg-body">
        <div class="msg-name">Somo AI</div>
        <div class="msg-bubble ai">
          <span class="typing-cursor"></span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    full_response = ""
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages_for_api,
            stream=True,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        for chunk in completion:
            delta = chunk.choices[0].delta.content or ""
            full_response += delta
            # Animated typing display
            typing_placeholder.markdown(f"""
            <div class="msg-wrapper ai">
              <div class="msg-avatar ai">✦</div>
              <div class="msg-body">
                <div class="msg-name">Somo AI</div>
                <div class="msg-bubble ai">{full_response}<span class="typing-cursor"></span></div>
              </div>
            </div>
            <script>
              if(typeof renderMathInElement !== 'undefined') {{
                renderMathInElement(document.body);
              }}
            </script>
            """, unsafe_allow_html=True)

        # Final render without cursor
        typing_placeholder.empty()

    except Exception as e:
        err = str(e)
        if "rate_limit" in err.lower():
            full_response = "⏳ Too many requests. Please wait a moment and try again."
        elif "model" in err.lower():
            full_response = f"❌ Model not found: `{model}`. Please select a different model."
        elif "auth" in err.lower() or "api_key" in err.lower():
            full_response = "❌ Invalid API key. Please check your GROQ_API_KEY."
        else:
            full_response = f"❌ Error: {err}"
        typing_placeholder.empty()

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "time": get_time()
    })

if send and user_input and user_input.strip():
    prompt = user_input.strip()
    st.session_state.input_key += 1
    process_message(prompt)
    st.rerun()
