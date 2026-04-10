# ═══════════════════════════════════════════════════════════
# SOMO AI  v7.1  —  "Obsidian & Ember" Premium Design
# Stack : Streamlit · Groq · Google Sheets · bcrypt
# Fixes : suggestion→AI, cache UI calls, None guard, UnboundLocal
# ═══════════════════════════════════════════════════════════

import streamlit as st
import gspread
import os
import hashlib
import time
from datetime import datetime
from typing import Optional

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
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════
# CSS — "Obsidian & Ember"
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Outfit:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

:root {
  --bg:         #05050a;
  --surface:    #0b0a12;
  --surface2:   #11101c;
  --surface3:   #18172a;
  --border:     rgba(240,169,78,0.10);
  --border-h:   rgba(240,169,78,0.35);
  --accent:     #f0a94e;
  --accent-dim: rgba(240,169,78,0.15);
  --accent-glow:rgba(240,169,78,0.08);
  --amber:      #e07f3a;
  --green:      #4ade80;
  --red:        #f87171;
  --text:       #f0ece4;
  --text-dim:   #a09888;
  --muted:      #5a5468;
  --muted2:     #2a2838;

  --font-brand: 'Cormorant Garamond', Georgia, serif;
  --font-ui:    'Outfit', sans-serif;
  --font-mono:  'Fira Code', monospace;

  --radius-sm:  8px;
  --radius-md:  12px;
  --radius-lg:  18px;
  --radius-xl:  24px;

  --shadow-sm:  0 2px 8px rgba(0,0,0,0.4);
  --shadow-md:  0 4px 20px rgba(0,0,0,0.5);
  --shadow-glow:0 0 32px rgba(240,169,78,0.12);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--font-ui) !important;
}

header[data-testid="stHeader"],
[data-testid="stSidebarNav"],
#MainMenu, footer { display: none !important; }

.main .block-container,
[data-testid="stMainBlockContainer"] {
  padding: 0 !important;
  max-width: 100% !important;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: var(--muted2);
  border-radius: 99px;
  transition: background 0.2s;
}
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
  width: 256px !important;
}
[data-testid="collapsedControl"] {
  display: flex !important;
  color: var(--accent) !important;
}

[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--text-dim) !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-ui) !important;
  font-size: 13px !important;
  padding: 9px 14px !important;
  width: 100% !important;
  text-align: left !important;
  transition: all 0.18s !important;
  letter-spacing: 0.2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--accent-glow) !important;
  color: var(--text) !important;
  transform: none !important;
}

[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {
  background: var(--accent) !important;
  box-shadow: 0 0 8px rgba(240,169,78,0.5) !important;
}

.stTextInput input,
.stTextArea textarea {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  font-family: var(--font-ui) !important;
  font-size: 14px !important;
  padding: 11px 16px !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
  caret-color: var(--accent) !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
  border-color: rgba(240,169,78,0.6) !important;
  box-shadow: 0 0 0 3px rgba(240,169,78,0.08), var(--shadow-sm) !important;
  outline: none !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder { color: var(--muted) !important; }
.stTextInput label,
.stTextArea label,
[data-testid="stWidgetLabel"] {
  color: var(--text-dim) !important;
  font-family: var(--font-ui) !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  letter-spacing: 1.2px !important;
  text-transform: uppercase !important;
}

.stButton > button {
  background: var(--surface2) !important;
  color: var(--text-dim) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  font-family: var(--font-ui) !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 10px 20px !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  cursor: pointer !important;
  letter-spacing: 0.3px !important;
  position: relative !important;
  overflow: hidden !important;
}
.stButton > button:hover {
  background: var(--surface3) !important;
  border-color: var(--border-h) !important;
  color: var(--text) !important;
  transform: translateY(-1px) !important;
  box-shadow: var(--shadow-sm) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #e07f3a 0%, #f0a94e 50%, #e8c473 100%) !important;
  color: #1a0f02 !important;
  border: none !important;
  font-weight: 700 !important;
  letter-spacing: 0.5px !important;
  box-shadow: 0 4px 20px rgba(240,169,78,0.25), var(--shadow-sm) !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, #c96d28 0%, #e09840 50%, #d4b060 100%) !important;
  box-shadow: 0 6px 28px rgba(240,169,78,0.35), var(--shadow-md) !important;
  transform: translateY(-2px) !important;
  color: #0f0802 !important;
}

[data-testid="stForm"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-xl) !important;
  padding: 28px 24px !important;
  box-shadow: var(--shadow-md) !important;
}
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, #e07f3a, #f0a94e, #e8c473) !important;
  color: #1a0f02 !important;
  border: none !important;
  font-weight: 700 !important;
  width: 100% !important;
  font-size: 14px !important;
  letter-spacing: 0.8px !important;
  box-shadow: 0 4px 20px rgba(240,169,78,0.2) !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
  background: linear-gradient(135deg, #c96d28, #e09840, #d4b060) !important;
  box-shadow: 0 6px 28px rgba(240,169,78,0.3) !important;
  transform: translateY(-1px) !important;
}

.stSuccess > div {
  background: rgba(74,222,128,0.06) !important;
  border: 1px solid rgba(74,222,128,0.2) !important;
  color: #86efac !important;
  border-radius: var(--radius-md) !important;
  font-family: var(--font-ui) !important;
}
.stError > div {
  background: rgba(248,113,113,0.06) !important;
  border: 1px solid rgba(248,113,113,0.2) !important;
  color: #fca5a5 !important;
  border-radius: var(--radius-md) !important;
  font-family: var(--font-ui) !important;
}
.stWarning > div {
  background: rgba(251,191,36,0.06) !important;
  border: 1px solid rgba(251,191,36,0.2) !important;
  color: #fcd34d !important;
  border-radius: var(--radius-md) !important;
  font-family: var(--font-ui) !important;
}

.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  font-family: var(--font-ui) !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  letter-spacing: 1px !important;
  text-transform: uppercase !important;
  padding: 12px 24px !important;
  border-radius: 0 !important;
  transition: color 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-dim) !important; }
.stTabs [aria-selected="true"][data-baseweb="tab"] {
  color: var(--accent) !important;
  border-bottom: 2px solid var(--accent) !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background: transparent !important;
  padding: 20px 0 !important;
}

.stChatMessage {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 16px 20px !important;
  margin: 6px 0 !important;
  transition: border-color 0.2s !important;
  position: relative !important;
}
.stChatMessage:hover { border-color: rgba(240,169,78,0.2) !important; }
[data-testid="stChatMessage"][data-testid*="user"],
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
  border-left: 3px solid var(--accent) !important;
  background: var(--surface2) !important;
}
.stChatMessage p {
  color: var(--text) !important;
  font-family: var(--font-ui) !important;
  font-size: 14.5px !important;
  line-height: 1.7 !important;
}
.stChatMessage code {
  background: rgba(240,169,78,0.1) !important;
  color: var(--accent) !important;
  border: 1px solid rgba(240,169,78,0.15) !important;
  border-radius: 4px !important;
  padding: 1px 6px !important;
  font-family: var(--font-mono) !important;
  font-size: 13px !important;
}
.stChatMessage pre {
  background: #020205 !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  padding: 16px !important;
}
.stChatMessage pre code {
  background: transparent !important;
  border: none !important;
  color: #e2c08d !important;
}

[data-testid="stChatInputContainer"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInputContainer"] > div:focus-within {
  border-color: rgba(240,169,78,0.4) !important;
  box-shadow: 0 0 0 3px rgba(240,169,78,0.06) !important;
}
[data-testid="stChatInputContainer"] textarea {
  background: transparent !important;
  color: var(--text) !important;
  font-family: var(--font-ui) !important;
  font-size: 14px !important;
  caret-color: var(--accent) !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder { color: var(--muted) !important; }
[data-testid="stChatInputContainer"] button {
  background: linear-gradient(135deg, #e07f3a, #f0a94e) !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  color: #1a0f02 !important;
  transition: all 0.2s !important;
}
[data-testid="stChatInputContainer"] button:hover {
  background: linear-gradient(135deg, #c96d28, #e09840) !important;
  box-shadow: 0 2px 12px rgba(240,169,78,0.3) !important;
}

div[data-testid="stBottom"] > div {
  background: rgba(5,5,10,0.96) !important;
  backdrop-filter: blur(20px) !important;
  -webkit-backdrop-filter: blur(20px) !important;
  border-top: 1px solid var(--border) !important;
  padding: 10px 20px 14px !important;
}

div[data-baseweb="select"] > div {
  background: var(--surface2) !important;
  border-color: var(--border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--text) !important;
  font-family: var(--font-ui) !important;
}
div[data-baseweb="popover"] {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-md) !important;
}
div[data-baseweb="popover"] li { color: var(--text) !important; }
div[data-baseweb="popover"] li:hover { background: var(--accent-glow) !important; }

[data-testid="stExpander"] {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
}
[data-testid="stExpander"] summary {
  background: var(--surface) !important;
  color: var(--text) !important;
  border-radius: var(--radius-md) !important;
}

hr { border-color: var(--border) !important; }
p, span, li { color: var(--text) !important; font-family: var(--font-ui) !important; }
h1, h2, h3 { font-family: var(--font-brand) !important; }

@keyframes ember-drift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes pulse-ring {
  0%   { transform: scale(0.95); opacity: 0.7; }
  50%  { transform: scale(1.05); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.7; }
}
@keyframes fade-up {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

.login-wrapper { animation: fade-up 0.6s ease both; }
.login-logo-ring { animation: pulse-ring 3s ease-in-out infinite; }

.sug-chip-hover:hover {
  border-color: rgba(240,169,78,0.4) !important;
  background: rgba(240,169,78,0.06) !important;
}

@media (max-width: 768px) {
  [data-testid="stSidebar"] { width: 85vw !important; }
  .stChatMessage { padding: 12px 14px !important; }
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
# FIX: st.warning/st.error moved outside @st.cache_resource
#      so UI calls don't fire inside a cached context
# ═══════════════════════════════════════════════════════════

@st.cache_resource
def _connect_db():
    """Pure connection — no Streamlit UI calls inside cache."""
    if not HAS_OAUTH:
        return None, "oauth2client o'rnatilmagan"
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets.get("gcp_service_account", {}),
            ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"],
        )
        gc = gspread.authorize(creds)
        ws = gc.open("Somo_Users").sheet1
        try:
            first = ws.row_values(1)
            if not first or first[0] != "username":
                ws.insert_row(["username", "password", "status", "created_at"], 1)
        except Exception:
            pass
        return ws, None
    except Exception as e:
        return None, str(e)[:120]


def get_db():
    """Wrapper that shows UI alerts outside the cached function."""
    ws, err = _connect_db()
    if err:
        st.warning(f"⚠️ Google Sheets: {err}")
    return ws


@st.cache_data(ttl=300)
def _load_all_users() -> list:
    ws, _ = _connect_db()
    if ws:
        try:
            return ws.get_all_records()
        except Exception:
            pass
    return []


def find_user(username: str) -> Optional[dict]:
    return next(
        (u for u in _load_all_users() if u.get("username") == username), None
    )


def user_exists(username: str) -> bool:
    return find_user(username) is not None


def save_user(username: str, password: str) -> bool:
    ws = get_db()
    if not ws:
        return False
    try:
        ws.append_row(
            [username, hash_pw(password), "active",
             datetime.now().strftime("%Y-%m-%d %H:%M")]
        )
        _load_all_users.clear()
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
    return Groq(api_key=key) if key else None


def stream_groq(messages: list, temperature: float = 0.7):
    client = get_groq()
    if not client:
        yield "❌ Groq API ulanmagan. `GROQ_API_KEY` ni tekshiring."
        return
    last_error = ""
    for attempt in range(3):
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
            return
        except Exception as e:
            last_error = str(e)
            if "429" in last_error or "rate" in last_error.lower():
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                yield "⚠️ Rate limit — bir daqiqa kuting."
                return
            elif "401" in last_error or "auth" in last_error.lower():
                yield "❌ API kalit noto'g'ri."
                return
            else:
                yield f"❌ Xato: {last_error[:120]}"
                return


# ═══════════════════════════════════════════════════════════
# SESSION STATE
# FIX: added "pending_prompt" for suggestion chip → AI flow
# ═══════════════════════════════════════════════════════════

_defaults = {
    "logged_in":      False,
    "username":       "",
    "login_time":     None,
    "messages":       [],
    "temperature":    0.7,
    "sys_prompt":     (
        "Sen Somo AI — aqlli, professional yordamchi. "
        "Foydalanuvchi qaysi tilda yozsa, o'sha tilda javob ber."
    ),
    "pending_prompt": None,   # ← NEW: suggestion chip pending message
}
for _k, _v in _defaults.items():
    st.session_state.setdefault(_k, _v)


# ═══════════════════════════════════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════════════════════════════════

def do_login(username: str, password: str) -> tuple[bool, str]:
    user = find_user(username)
    if not user:
        return False, "Foydalanuvchi topilmadi."
    if str(user.get("status", "")).lower() == "blocked":
        return False, "Hisob bloklangan."
    if not check_pw(password, str(user.get("password", ""))):
        return False, "Parol noto'g'ri."
    return True, "ok"


def do_register(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if len(username) < 3:
        return False, "Username kamida 3 belgi bo'lishi kerak."
    if len(password) < 6:
        return False, "Parol kamida 6 belgi bo'lishi kerak."
    if user_exists(username):
        return False, "Bu username allaqachon band."
    if not save_user(username, password):
        return False, "Saqlashda xato."
    return True, "ok"


def logout():
    for key in ("logged_in", "username", "login_time", "messages", "pending_prompt"):
        st.session_state[key] = _defaults[key]
    st.rerun()


# ═══════════════════════════════════════════════════════════
# LOGIN PAGE
# FIX: submitted/submitted2 initialised before form so no
#      UnboundLocalError if form hasn't rendered yet
# ═══════════════════════════════════════════════════════════

def render_login():
    _, col, _ = st.columns([1, 1.1, 1])

    with col:
        st.markdown("""
        <div class="login-wrapper" style="text-align:center; padding: 52px 0 36px;">
          <div style="position:relative; width:72px; height:72px; margin:0 auto 20px;">
            <div class="login-logo-ring" style="
              position:absolute; inset:-6px;
              border-radius:20px;
              background: linear-gradient(135deg, rgba(240,169,78,0.2), rgba(224,127,58,0.05));
              border: 1px solid rgba(240,169,78,0.2);
            "></div>
            <div style="
              width:72px; height:72px;
              background: linear-gradient(145deg, #1a1208, #2d1e08);
              border-radius:18px;
              border: 1px solid rgba(240,169,78,0.3);
              display:flex; align-items:center; justify-content:center;
              font-size:28px;
              box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(240,169,78,0.1),
                          inset 0 1px 0 rgba(240,169,78,0.15);
              position:relative;
            ">◈</div>
          </div>
          <div style="
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 38px; font-weight: 700; letter-spacing: -0.5px;
            line-height: 1; margin-bottom: 8px;
            background: linear-gradient(135deg, #f0ece4 0%, #f0a94e 60%, #e8c473 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
          ">Somo AI</div>
          <div style="
            font-family: 'Outfit', sans-serif; font-size: 12px; font-weight: 500;
            letter-spacing: 3px; text-transform: uppercase; color: #5a5468; margin-bottom: 4px;
          ">Llama 3.3 · 70B · Groq</div>
          <div style="
            width: 40px; height: 1px;
            background: linear-gradient(90deg, transparent, rgba(240,169,78,0.4), transparent);
            margin: 16px auto 0;
          "></div>
        </div>
        """, unsafe_allow_html=True)

        tab_in, tab_reg = st.tabs(["  Kirish  ", "  Ro'yxat  "])

        # ── Login tab ─────────────────────────────────────
        with tab_in:
            # FIX: initialise before form to avoid UnboundLocalError
            login_submitted = False
            login_username = ""
            login_password = ""

            with st.form("login_form", clear_on_submit=False):
                login_username = st.text_input("Username", placeholder="username")
                login_password = st.text_input(
                    "Parol", type="password", placeholder="••••••••"
                )
                login_submitted = st.form_submit_button(
                    "Kirish  →", use_container_width=True, type="primary"
                )

            if login_submitted:
                u = login_username.strip()
                p = login_password
                if not u or not p:
                    st.error("Username va parolni kiriting.")
                else:
                    ok, msg = do_login(u, p)
                    if ok:
                        st.session_state.logged_in  = True
                        st.session_state.username   = u
                        st.session_state.login_time = datetime.now()
                        st.rerun()
                    else:
                        st.error(msg)

        # ── Register tab ──────────────────────────────────
        with tab_reg:
            # FIX: initialise before form to avoid UnboundLocalError
            reg_submitted = False
            reg_username  = ""
            reg_password  = ""
            reg_confirm   = ""

            with st.form("reg_form", clear_on_submit=True):
                reg_username = st.text_input(
                    "Username", placeholder="kamida 3 belgi", key="r_u"
                )
                reg_password = st.text_input(
                    "Parol", type="password", placeholder="kamida 6 belgi", key="r_p"
                )
                reg_confirm = st.text_input(
                    "Parolni tasdiqlang", type="password", key="r_c"
                )
                reg_submitted = st.form_submit_button(
                    "Hisob yaratish  →", use_container_width=True, type="primary"
                )

            if reg_submitted:
                if reg_password != reg_confirm:
                    st.error("Parollar mos emas.")
                else:
                    ok, msg = do_register(reg_username, reg_password)
                    if ok:
                        st.success("✅ Hisob yaratildi! Kirish bo'limiga o'ting.")
                    else:
                        st.error(msg)

        # ── Status dots ───────────────────────────────────
        db_ok   = _connect_db()[0] is not None
        groq_ok = get_groq() is not None
        st.markdown(f"""
        <div style="
          display:flex; align-items:center; justify-content:center; gap:20px;
          padding: 24px 0 48px;
          font-family: 'Fira Code', monospace; font-size: 11px;
        ">
          <div style="display:flex;align-items:center;gap:6px;">
            <span style="
              width:6px;height:6px;border-radius:50%;
              background:{'#4ade80' if db_ok else '#f87171'};
              display:inline-block;
              box-shadow: 0 0 6px {'rgba(74,222,128,0.6)' if db_ok else 'rgba(248,113,113,0.6)'};
            "></span>
            <span style="color:{'#86efac' if db_ok else '#fca5a5'};">Sheets</span>
          </div>
          <div style="width:1px;height:12px;background:rgba(90,84,104,0.4);"></div>
          <div style="display:flex;align-items:center;gap:6px;">
            <span style="
              width:6px;height:6px;border-radius:50%;
              background:{'#4ade80' if groq_ok else '#f87171'};
              display:inline-block;
              box-shadow: 0 0 6px {'rgba(74,222,128,0.6)' if groq_ok else 'rgba(248,113,113,0.6)'};
            "></span>
            <span style="color:{'#86efac' if groq_ok else '#fca5a5'};">Groq</span>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        uname         = st.session_state.username
        msgs          = st.session_state.messages
        avatar_letter = (uname[:1] or "?").upper()
        mins = 0
        if st.session_state.login_time:
            mins = int(
                (datetime.now() - st.session_state.login_time).total_seconds() // 60
            )
        user_msg_count = sum(1 for m in msgs if m["role"] == "user")

        st.markdown(f"""
        <div style="padding: 24px 16px 16px;">
          <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
            <div style="
              width:40px; height:40px;
              background: linear-gradient(145deg, #1a1208, #2d1e08);
              border: 1px solid rgba(240,169,78,0.3);
              border-radius:12px; flex-shrink:0;
              display:flex; align-items:center; justify-content:center;
              font-family:'Cormorant Garamond',serif;
              font-size:18px; font-weight:700;
              color: #f0a94e;
              box-shadow: 0 0 12px rgba(240,169,78,0.1);
            ">{avatar_letter}</div>
            <div>
              <div style="
                font-family:'Outfit',sans-serif;
                font-size:14px; font-weight:600;
                color:#f0ece4; letter-spacing:0.2px;
              ">{uname}</div>
              <div style="
                font-size:10px; font-family:'Fira Code',monospace;
                color:#4ade80; margin-top:2px; letter-spacing:0.5px;
              ">● aktiv</div>
            </div>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:4px;">
            <div style="
              background: linear-gradient(145deg, #0f0e1a, #15132a);
              border: 1px solid rgba(240,169,78,0.1);
              border-radius:10px; padding:12px 10px; text-align:center;
            ">
              <div style="
                font-family:'Cormorant Garamond',serif;
                font-size:22px; font-weight:700; color:#f0a94e; line-height:1;
              ">{user_msg_count}</div>
              <div style="
                font-size:9px; font-family:'Fira Code',monospace;
                color:#5a5468; text-transform:uppercase; letter-spacing:1px; margin-top:4px;
              ">xabar</div>
            </div>
            <div style="
              background: linear-gradient(145deg, #0f0e1a, #15132a);
              border: 1px solid rgba(240,169,78,0.1);
              border-radius:10px; padding:12px 10px; text-align:center;
            ">
              <div style="
                font-family:'Cormorant Garamond',serif;
                font-size:22px; font-weight:700; color:#f0a94e; line-height:1;
              ">{mins}</div>
              <div style="
                font-size:9px; font-family:'Fira Code',monospace;
                color:#5a5468; text-transform:uppercase; letter-spacing:1px; margin-top:4px;
              ">daqiqa</div>
            </div>
          </div>
        </div>
        <div style="
          height:1px; margin:0 16px 16px;
          background: linear-gradient(90deg, transparent, rgba(240,169,78,0.15), transparent);
        "></div>
        <p style="
          font-size:9px; font-family:'Fira Code',monospace;
          color:#5a5468; text-transform:uppercase;
          letter-spacing:2px; padding:0 16px 8px;
        ">Sozlamalar</p>
        """, unsafe_allow_html=True)

        st.session_state.temperature = st.slider(
            "Ijodkorlik", 0.0, 1.0,
            st.session_state.temperature, 0.05, key="temp_sl",
            help="Past → aniq, Yuqori → ijodkor",
        )

        st.session_state.sys_prompt = st.text_area(
            "Tizim xabari",
            value=st.session_state.sys_prompt,
            height=88, key="sys_ta",
            help="AI ning xulq-atvori",
        )

        st.markdown("""
        <div style="
          height:1px; margin:12px 16px;
          background: linear-gradient(90deg, transparent, rgba(240,169,78,0.12), transparent);
        "></div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑 Tozala", use_container_width=True, key="clr_btn"):
                st.session_state.messages       = []
                st.session_state.pending_prompt = None
                st.rerun()
        with col2:
            if st.button("→ Chiq", use_container_width=True, key="logout_btn"):
                logout()

        groq_ok = get_groq() is not None
        st.markdown(f"""
        <div style="
          padding:14px 16px;
          font-family:'Fira Code',monospace; font-size:10px;
          display:flex; align-items:center; gap:6px;
        ">
          <span style="
            width:5px;height:5px;border-radius:50%;
            background:{'#4ade80' if groq_ok else '#f87171'};
            display:inline-block;
            box-shadow: 0 0 5px {'rgba(74,222,128,0.5)' if groq_ok else 'rgba(248,113,113,0.5)'};
          "></span>
          <span style="color:{'#86efac' if groq_ok else '#fca5a5'};">
            {'Groq — tayyor' if groq_ok else 'Groq — ulanmagan'}
          </span>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# CHAT PAGE
# ═══════════════════════════════════════════════════════════

def build_api_messages() -> list:
    api_msgs = [{"role": "system", "content": st.session_state.sys_prompt}]
    api_msgs.extend(
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-20:]
    )
    return api_msgs


def _generate_response(prompt: str) -> None:
    """
    Append user message, stream AI reply, append assistant message.
    Shared by both chat_input and suggestion-chip flows.
    """
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # FIX: guard against None from st.write_stream
        full_resp = st.write_stream(
            stream_groq(build_api_messages(), st.session_state.temperature)
        )

    if full_resp:
        st.session_state.messages.append(
            {"role": "assistant", "content": full_resp}
        )


def render_chat():
    render_sidebar()

    uname = st.session_state.username

    # ── Header bar ────────────────────────────────────────
    st.markdown("""
    <div style="
      padding: 24px 36px 18px;
      border-bottom: 1px solid rgba(240,169,78,0.08);
      display:flex; align-items:center; justify-content:space-between;
      background: linear-gradient(180deg, rgba(11,10,18,0.95), transparent);
      position: sticky; top: 0; z-index: 10;
      backdrop-filter: blur(12px);
    ">
      <div style="display:flex; align-items:center; gap:14px;">
        <div style="
          width:38px; height:38px;
          background: linear-gradient(145deg, #1a1208, #2d1e08);
          border:1px solid rgba(240,169,78,0.3);
          border-radius:11px;
          display:flex; align-items:center; justify-content:center;
          font-size:16px;
          box-shadow: 0 0 16px rgba(240,169,78,0.1);
        ">◈</div>
        <div>
          <div style="
            font-family:'Cormorant Garamond',serif;
            font-size:22px; font-weight:700; letter-spacing:-0.3px;
            color:#f0ece4; line-height:1;
          ">Somo AI</div>
          <div style="
            font-size:10px; font-family:'Fira Code',monospace;
            color:#5a5468; margin-top:3px; letter-spacing:0.5px;
          ">llama-3.3-70b · groq</div>
        </div>
      </div>
      <div style="
        width:80px; height:1px;
        background: linear-gradient(90deg, rgba(240,169,78,0.3), transparent);
      "></div>
    </div>
    <div style="height:12px;"></div>
    """, unsafe_allow_html=True)

    # ── Welcome / empty state ─────────────────────────────
    if not st.session_state.messages and not st.session_state.pending_prompt:
        st.markdown(f"""
        <div style="
          text-align:center;
          padding: 64px 24px 40px;
          animation: fade-up 0.5s ease both;
        ">
          <div style="
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: clamp(32px, 5vw, 52px);
            font-weight: 700; letter-spacing: -1px; line-height: 1.1;
            margin-bottom: 14px;
            background: linear-gradient(135deg, #f0ece4 0%, #f0a94e 55%, #e8c473 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
          ">Salom, {uname}.</div>
          <p style="
            font-family:'Outfit',sans-serif;
            font-size:15px; color:#5a5468;
            max-width:360px; margin:0 auto 40px;
            line-height:1.65; font-weight:400;
          ">Savolingizni yozing yoki quyidagi mavzulardan birini tanlang</p>
          <div style="
            width:48px; height:1px;
            background: linear-gradient(90deg, transparent, rgba(240,169,78,0.4), transparent);
            margin: 0 auto 36px;
          "></div>
        </div>
        """, unsafe_allow_html=True)

        # FIX: suggestion chips now set pending_prompt + rerun
        # so the AI response is properly generated on next render
        suggestions = [
            "🐍  Python da Telegram bot",
            "📖  Ingliz tilini o'rgatish",
            "📄  Resume yaxshilash",
            "🗄️  SQL va NoSQL farqi",
        ]
        cols = st.columns(2)
        for i, sug in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(sug, key=f"sug_{i}", use_container_width=True):
                    clean = sug.split("  ", 1)[-1]
                    st.session_state.pending_prompt = clean
                    st.rerun()

    # ── Message history ───────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # FIX: handle pending_prompt from suggestion chips
    # This runs after existing messages are rendered, generating AI reply
    if st.session_state.pending_prompt:
        pending = st.session_state.pending_prompt
        st.session_state.pending_prompt = None   # clear before generating
        _generate_response(pending)

    # ── Chat input ────────────────────────────────────────
    if prompt := st.chat_input("Savolingizni yozing...", key="chat_input"):
        _generate_response(prompt)


# ═══════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════

if st.session_state.logged_in:
    render_chat()
else:
    render_login()
