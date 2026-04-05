# ═══════════════════════════════════════════════════════════
# SOMO AI  v5.0
# Stack : Streamlit · Groq · Google Sheets · bcrypt
# Pages : Login / Register  →  Chat
# ═══════════════════════════════════════════════════════════

import streamlit as st
import gspread
import json
import time
import os
import hashlib
from datetime import datetime
from typing import Optional

# ── Optional imports ────────────────────────────────────────
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

try:
    from oauth2client.service_account import ServiceAccountCredentials
    HAS_OAUTH = True
except ImportError:
    HAS_OAUTH = False

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

# ═══════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Somo AI",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════
# CSS — Premium Dark
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:        #080810;
  --surface:   #0e0e1a;
  --surface2:  #141424;
  --border:    rgba(139,92,246,0.15);
  --border-h:  rgba(139,92,246,0.45);
  --accent:    #8b5cf6;
  --accent2:   #6366f1;
  --green:     #10b981;
  --red:       #f43f5e;
  --text:      #f1f0ff;
  --muted:     #6b6b8a;
  --muted2:    #3a3a5c;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}

/* Hide Streamlit chrome */
header[data-testid="stHeader"],
[data-testid="stSidebarNav"],
#MainMenu, footer { display: none !important; }

/* Main container */
.main .block-container,
[data-testid="stMainBlockContainer"] {
  padding: 0 !important;
  max-width: 100% !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--muted2); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
  width: 240px !important;
}
[data-testid="collapsedControl"] {
  display: flex !important;
  color: var(--accent) !important;
}
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--muted) !important;
  border: none !important;
  border-radius: 8px !important;
  font-size: 13px !important;
  padding: 8px 12px !important;
  width: 100% !important;
  text-align: left !important;
  transition: all 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(139,92,246,0.08) !important;
  color: var(--text) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: rgba(139,92,246,0.15) !important;
  color: #c4b5fd !important;
  border: 1px solid rgba(139,92,246,0.25) !important;
}

/* ── INPUTS ── */
.stTextInput input,
.stTextArea textarea {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
  transition: border-color 0.2s !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(139,92,246,0.1) !important;
}
.stTextInput label,
.stTextArea label,
[data-testid="stWidgetLabel"] {
  color: var(--muted) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  letter-spacing: 0.5px !important;
}

/* ── BUTTONS ── */
.stButton > button {
  background: var(--surface2) !important;
  color: #c4b5fd !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  padding: 10px 20px !important;
  transition: all 0.2s !important;
  cursor: pointer !important;
}
.stButton > button:hover {
  background: rgba(139,92,246,0.12) !important;
  border-color: var(--border-h) !important;
  transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 4px 20px rgba(139,92,246,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
  box-shadow: 0 6px 24px rgba(139,92,246,0.45) !important;
  transform: translateY(-2px) !important;
}

/* ── FORM ── */
[data-testid="stForm"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 16px !important;
  padding: 28px 24px !important;
}
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  color: white !important;
  border: none !important;
  font-weight: 700 !important;
  width: 100% !important;
}

/* ── ALERTS ── */
.stSuccess > div {
  background: rgba(16,185,129,0.08) !important;
  border: 1px solid rgba(16,185,129,0.25) !important;
  color: #6ee7b7 !important;
  border-radius: 10px !important;
}
.stError > div {
  background: rgba(244,63,94,0.08) !important;
  border: 1px solid rgba(244,63,94,0.25) !important;
  color: #fda4af !important;
  border-radius: 10px !important;
}
.stWarning > div {
  background: rgba(245,158,11,0.08) !important;
  border: 1px solid rgba(245,158,11,0.25) !important;
  color: #fcd34d !important;
  border-radius: 10px !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  padding: 10px 20px !important;
  border-radius: 0 !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text) !important; }
.stTabs [aria-selected="true"][data-baseweb="tab"] {
  color: #c4b5fd !important;
  border-bottom: 2px solid var(--accent) !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background: transparent !important;
  padding: 20px 0 !important;
}

/* ── CHAT ── */
.stChatMessage {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 14px 18px !important;
  margin: 4px 0 !important;
}
.stChatMessage p { color: var(--text) !important; }
.stChatMessage code {
  background: rgba(139,92,246,0.15) !important;
  color: #c4b5fd !important;
  border-radius: 4px !important;
  padding: 1px 5px !important;
  font-family: 'JetBrains Mono', monospace !important;
}
.stChatMessage pre {
  background: #040408 !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}

/* Chat input */
[data-testid="stChatInputContainer"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
[data-testid="stChatInputContainer"] textarea {
  background: transparent !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
}
[data-testid="stChatInputContainer"] button {
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  border: none !important;
  border-radius: 8px !important;
  color: white !important;
}
div[data-testid="stBottom"] > div {
  background: rgba(8,8,16,0.95) !important;
  backdrop-filter: blur(16px) !important;
  border-top: 1px solid var(--border) !important;
  padding: 8px 16px 12px !important;
}

/* ── SELECT ── */
div[data-baseweb="select"] > div {
  background: var(--surface2) !important;
  border-color: var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
}
div[data-baseweb="popover"] {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
div[data-baseweb="popover"] li { color: var(--text) !important; }
div[data-baseweb="popover"] li:hover { background: rgba(139,92,246,0.1) !important; }

/* ── EXPANDER ── */
[data-testid="stExpander"] {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
  background: var(--surface) !important;
  color: var(--text) !important;
  border-radius: 10px !important;
}

/* ── MISC ── */
hr { border-color: var(--border) !important; }
p, span, li { color: var(--text) !important; }

/* ── MOBILE ── */
@media (max-width: 768px) {
  [data-testid="stSidebar"] { width: 80vw !important; }
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HELPERS: PASSWORD
# ═══════════════════════════════════════════════════════════

def hash_pw(password: str) -> str:
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    return hashlib.sha256(password.encode()).hexdigest()


def check_pw(password: str, hashed: str) -> bool:
    if not hashed:
        return False
    if HAS_BCRYPT and hashed.startswith(("$2b$", "$2a$")):
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception:
            pass
    return hashlib.sha256(password.encode()).hexdigest() == hashed

# ═══════════════════════════════════════════════════════════
# HELPERS: SECRETS
# ═══════════════════════════════════════════════════════════

def get_secret(key: str) -> str:
    try:
        val = st.secrets.get(key, "")
        if val:
            return str(val).strip()
    except Exception:
        pass
    return os.environ.get(key, "").strip()

# ═══════════════════════════════════════════════════════════
# DATABASE — Google Sheets
# ═══════════════════════════════════════════════════════════

@st.cache_resource
def get_db():
    """Google Sheets ulanish."""
    try:
        if not HAS_OAUTH:
            return None
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets.get("gcp_service_account", {}),
            ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        ws = ss.sheet1
        # Header yo'q bo'lsa qo'shamiz
        try:
            first = ws.row_values(1)
            if not first or first[0] != "username":
                ws.insert_row(["username", "password", "status", "created_at"], 1)
        except Exception:
            pass
        return ws
    except Exception as e:
        return None


@st.cache_data(ttl=60)
def load_users() -> list:
    ws = get_db()
    if ws:
        try:
            return ws.get_all_records()
        except Exception:
            pass
    return []


def save_user(username: str, password: str) -> bool:
    ws = get_db()
    if not ws:
        return False
    try:
        ws.append_row([
            username,
            hash_pw(password),
            "active",
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ])
        load_users.clear()
        return True
    except Exception:
        return False

# ═══════════════════════════════════════════════════════════
# GROQ CLIENT
# ═══════════════════════════════════════════════════════════

@st.cache_resource
def get_groq():
    if not HAS_GROQ:
        return None
    key = get_secret("GROQ_API_KEY")
    if not key:
        return None
    try:
        return Groq(api_key=key)
    except Exception:
        return None


def stream_groq(messages: list, temperature: float = 0.7):
    """Groq stream generator."""
    client = get_groq()
    if not client:
        yield "❌ Groq API ulanmagan. `GROQ_API_KEY` ni tekshiring."
        return
    try:
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=temperature,
            max_tokens=2048,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        err = str(e)
        if "429" in err or "rate" in err.lower():
            yield "⚠️ Rate limit — bir daqiqa kuting va qayta yuboring."
        elif "401" in err or "auth" in err.lower():
            yield "❌ API kalit noto'g'ri."
        else:
            yield f"❌ Xato: {err[:120]}"

# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════

_defaults = {
    "logged_in":   False,
    "username":    "",
    "login_time":  None,
    "messages":    [],          # [{role, content}]
    "temperature": 0.7,
    "sys_prompt":  "Sen Somo AI — aqlli, professional yordamchi. Foydalanuvchi qaysi tilda yozsa, o'sha tilda javob ber.",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════════════════════════════════

def do_login(username: str, password: str) -> tuple[bool, str]:
    users = load_users()
    user  = next((u for u in users if u.get("username") == username), None)
    if not user:
        return False, "Foydalanuvchi topilmadi."
    if str(user.get("status", "")).lower() == "blocked":
        return False, "Hisob bloklangan."
    if not check_pw(password, str(user.get("password", ""))):
        return False, "Parol noto'g'ri."
    return True, "ok"


def do_register(username: str, password: str) -> tuple[bool, str]:
    if len(username) < 3:
        return False, "Username kamida 3 belgi bo'lishi kerak."
    if len(password) < 6:
        return False, "Parol kamida 6 belgi bo'lishi kerak."
    users = load_users()
    if any(u.get("username") == username for u in users):
        return False, "Bu username band."
    ok = save_user(username, password)
    if not ok:
        return False, "Saqlashda xato. Google Sheets ulanishini tekshiring."
    return True, "ok"


def logout():
    st.session_state.logged_in = False
    st.session_state.username  = ""
    st.session_state.login_time = None
    st.session_state.messages  = []
    st.rerun()

# ═══════════════════════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════════════════════

def render_login():
    # Centered layout
    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        # Logo / title
        st.markdown("""
        <div style="text-align:center; padding: 48px 0 32px;">
            <div style="
                width: 56px; height: 56px;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                border-radius: 16px;
                display: flex; align-items: center; justify-content: center;
                font-size: 26px;
                margin: 0 auto 16px;
                box-shadow: 0 8px 32px rgba(99,102,241,0.35);
            ">◆</div>
            <h1 style="
                font-size: 28px; font-weight: 700;
                color: #f1f0ff; letter-spacing: -0.5px;
                margin-bottom: 6px;
            ">Somo AI</h1>
            <p style="font-size: 13px; color: #6b6b8a;">
                Aqlli yordamchi · Groq · Llama 3.3
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_in, tab_reg = st.tabs(["  Kirish  ", "  Ro'yxat  "])

        # ── LOGIN ──
        with tab_in:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="username")
                password = st.text_input("Parol", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Kirish →", use_container_width=True, type="primary")

            if submitted:
                if not username or not password:
                    st.error("Username va parolni kiriting.")
                else:
                    ok, msg = do_login(username, password)
                    if ok:
                        st.session_state.logged_in  = True
                        st.session_state.username   = username
                        st.session_state.login_time = datetime.now()
                        st.rerun()
                    else:
                        st.error(msg)

        # ── REGISTER ──
        with tab_reg:
            with st.form("reg_form", clear_on_submit=True):
                nu = st.text_input("Username", placeholder="kamida 3 belgi", key="r_u")
                np = st.text_input("Parol", type="password", placeholder="kamida 6 belgi", key="r_p")
                nc = st.text_input("Parolni tasdiqlang", type="password", key="r_c")
                submitted2 = st.form_submit_button("Hisob yaratish →", use_container_width=True, type="primary")

            if submitted2:
                if np != nc:
                    st.error("Parollar mos emas.")
                else:
                    ok, msg = do_register(nu, np)
                    if ok:
                        st.success("✅ Hisob yaratildi! Kirish bo'limiga o'ting.")
                    else:
                        st.error(msg)

        # DB status
        db_ok = get_db() is not None
        groq_ok = get_groq() is not None
        st.markdown(f"""
        <div style="
            display: flex; gap: 12px; justify-content: center;
            padding: 20px 0 40px; font-size: 11px;
            font-family: 'JetBrains Mono', monospace;
        ">
            <span style="color: {'#10b981' if db_ok else '#f43f5e'};">
                {'●' if db_ok else '○'} Sheets
            </span>
            <span style="color: {'#10b981' if groq_ok else '#f43f5e'};">
                {'●' if groq_ok else '○'} Groq
            </span>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SIDEBAR (chat page)
# ═══════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        uname = st.session_state.username
        msgs  = st.session_state.messages
        mins  = 0
        if st.session_state.login_time:
            mins = int((datetime.now() - st.session_state.login_time).seconds / 60)

        # User card
        st.markdown(f"""
        <div style="padding: 20px 16px 16px;">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
                <div style="
                    width: 38px; height: 38px;
                    background: linear-gradient(135deg,#6366f1,#8b5cf6);
                    border-radius: 10px; flex-shrink: 0;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 16px; font-weight: 700; color: white;
                ">{uname[0].upper()}</div>
                <div>
                    <div style="font-size:13px;font-weight:600;color:#f1f0ff;">{uname}</div>
                    <div style="font-size:10px;color:#10b981;margin-top:1px;">● online</div>
                </div>
            </div>
            <div style="
                display: grid; grid-template-columns: 1fr 1fr;
                gap: 8px; margin-bottom: 4px;
            ">
                <div style="
                    background: rgba(99,102,241,0.08);
                    border: 1px solid rgba(99,102,241,0.15);
                    border-radius: 8px; padding: 10px; text-align:center;
                ">
                    <div style="font-size:18px;font-weight:700;color:#f1f0ff;">{len([m for m in msgs if m['role']=='user'])}</div>
                    <div style="font-size:9px;color:#6b6b8a;text-transform:uppercase;letter-spacing:1px;">Xabar</div>
                </div>
                <div style="
                    background: rgba(99,102,241,0.08);
                    border: 1px solid rgba(99,102,241,0.15);
                    border-radius: 8px; padding: 10px; text-align:center;
                ">
                    <div style="font-size:18px;font-weight:700;color:#f1f0ff;">{mins}</div>
                    <div style="font-size:9px;color:#6b6b8a;text-transform:uppercase;letter-spacing:1px;">Daqiqa</div>
                </div>
            </div>
        </div>
        <hr style="border-color:rgba(139,92,246,0.12);margin:0 0 8px;">
        """, unsafe_allow_html=True)

        # Settings
        st.markdown('<p style="font-size:10px;color:#6b6b8a;text-transform:uppercase;letter-spacing:2px;padding:8px 16px 4px;">Sozlamalar</p>', unsafe_allow_html=True)

        st.session_state.temperature = st.slider(
            "Ijodkorlik", 0.0, 1.0,
            st.session_state.temperature, 0.05,
            key="temp_sl",
            help="Past = aniq, yuqori = ijodkor"
        )

        st.session_state.sys_prompt = st.text_area(
            "Tizim xabari",
            value=st.session_state.sys_prompt,
            height=90, key="sys_ta",
            help="AI ning xulq-atvori"
        )

        st.markdown('<hr style="border-color:rgba(139,92,246,0.12);margin:8px 0;">', unsafe_allow_html=True)

        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑 Tozala", use_container_width=True, key="clr_btn"):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("🚪 Chiq", use_container_width=True, key="logout_btn"):
                logout()

        # Groq status
        groq_ok = get_groq() is not None
        st.markdown(f"""
        <div style="padding:12px 16px;font-size:11px;font-family:'JetBrains Mono',monospace;color:{'#10b981' if groq_ok else '#f43f5e'};">
            {'● Groq — tayyor' if groq_ok else '○ Groq — ulanmagan'}
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# CHAT PAGE
# ═══════════════════════════════════════════════════════════

def render_chat():
    render_sidebar()

    uname = st.session_state.username

    # Header
    st.markdown(f"""
    <div style="
        padding: 28px 32px 20px;
        border-bottom: 1px solid rgba(139,92,246,0.12);
        display: flex; align-items: center; gap: 16px;
    ">
        <div style="
            width: 40px; height: 40px;
            background: linear-gradient(135deg,#6366f1,#8b5cf6);
            border-radius: 12px;
            display:flex; align-items:center; justify-content:center;
            font-size:18px; box-shadow:0 4px 16px rgba(99,102,241,0.3);
        ">◆</div>
        <div>
            <div style="font-size:18px;font-weight:700;color:#f1f0ff;letter-spacing:-0.3px;">
                Somo AI
            </div>
            <div style="font-size:12px;color:#6b6b8a;margin-top:1px;">
                Llama 3.3 · 70B · via Groq
            </div>
        </div>
    </div>
    <div style="height:16px;"></div>
    """, unsafe_allow_html=True)

    # Welcome (empty state)
    if not st.session_state.messages:
        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 60px 20px 40px;
        ">
            <div style="
                font-size: 42px;
                background: linear-gradient(135deg,#6366f1,#8b5cf6,#a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 800;
                letter-spacing: -1px;
                margin-bottom: 10px;
            ">Salom, {uname}!</div>
            <p style="font-size:15px;color:#6b6b8a;max-width:400px;margin:0 auto 32px;line-height:1.6;">
                Savolingizni yozing — men javob beraman.
            </p>
            <div style="
                display: flex; flex-wrap: wrap;
                gap: 10px; justify-content: center;
                max-width: 560px; margin: 0 auto;
            ">
        """, unsafe_allow_html=True)

        # Suggestion chips
        suggestions = [
            "Python da Telegram bot yozing",
            "Ingliz tilini o'rganishga maslahat bering",
            "Resumeni qanday yaxshilash mumkin?",
            "SQL va NoSQL farqi nima?",
        ]
        cols = st.columns(2)
        for i, sug in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(sug, key=f"sug_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": sug})
                    st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)

    # Message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Yozing...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # AI response
        with st.chat_message("assistant"):
            # Build messages for API
            api_msgs = [{"role": "system", "content": st.session_state.sys_prompt}]
            # Last 20 messages (context window)
            for m in st.session_state.messages[-20:]:
                api_msgs.append({"role": m["role"], "content": m["content"]})

            placeholder = st.empty()
            full_resp   = ""

            for chunk in stream_groq(api_msgs, st.session_state.temperature):
                full_resp += chunk
                placeholder.markdown(full_resp + "▌")

            placeholder.markdown(full_resp)

        st.session_state.messages.append({
            "role": "assistant", "content": full_resp
        })

        st.rerun()

# ═══════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════

if st.session_state.logged_in:
    render_chat()
else:
    render_login()
