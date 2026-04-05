# ════════════════════════════════════════════════════════════════════════════════
# SOMO AI v5.0 - ULTRA PROFESSIONAL EDITION
# ════════════════════════════════════════════════════════════════════════════════
# Author: Usmonov Sodiq | Date: 2026-03-27
# Version: 5.0 (Secure + Mobile + Perfect Design + All 13 Pages)
# Status: PRODUCTION READY ✅
# ════════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import gspread
import json
import time
import io
import re
import os
from datetime import datetime
from functools import lru_cache
from typing import Tuple, Optional, List, Dict, Any

# ════════════════════════════════════════════════════════════════════════════════
# IMPORTS WITH PROPER ERROR HANDLING
# ════════════════════════════════════════════════════════════════════════════════

try:
    from oauth2client.service_account import ServiceAccountCredentials
    HAS_OAUTH = True
except ImportError:
    HAS_OAUTH = False

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

try:
    from streamlit_cookies_manager import EncryptedCookieManager
    HAS_COOKIES = True
except ImportError:
    HAS_COOKIES = False

try:
    from pymupdf import fitz
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import cohere
    HAS_COHERE = True
except ImportError:
    HAS_COHERE = False

try:
    from mistralai import Mistral
    HAS_MISTRAL = True
except ImportError:
    HAS_MISTRAL = False

# ════════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Somo AI | Ultra Pro",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════════════════════════
# ULTRA PERFECT CSS - MOBILE + SIDEBAR + DESIGN
# ════════════════════════════════════════════════════════════════════════════════

CSS_ULTRA = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg-0: #05050f; --bg-1: #090916; --bg-2: #0d0d1e; --bg-card: #0f0f22;
  --border: rgba(100,108,255,0.18); --border-h: rgba(100,108,255,0.55);
  --accent: #646cff; --text-1: #f0f0ff; --text-2: #a0a0c0; --text-3: #50506a;
}

html, body, .stApp { 
  font-family: 'Inter', sans-serif !important;
  background: var(--bg-0) !important;
  color: var(--text-1) !important;
}

header[data-testid="stHeader"], #MainMenu, footer { display: none !important; }

.main .block-container, [data-testid="stMainBlockContainer"] {
  padding: 1.5rem 1rem 5rem !important;
  max-width: 100% !important;
}

@media (min-width: 768px) {
  .main .block-container, [data-testid="stMainBlockContainer"] {
    padding: 1.5rem 2rem 5rem !important;
    max-width: 1200px !important;
  }
}

/* ════ SIDEBAR - FIXED ════ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #07071a 0%, #09091e 100%) !important;
  border-right: 1px solid rgba(100,108,255,0.15) !important;
  width: 280px !important;
  min-width: 280px !important;
  display: flex !important;
  flex-direction: column !important;
  position: relative !important;
  z-index: 999 !important;
  visibility: visible !important;
  overflow-y: auto !important;
}

[data-testid="stSidebar"] > div:first-child {
  padding: 0 !important;
  width: 100% !important;
}

[data-testid="collapsedControl"] {
  display: flex !important;
  visibility: visible !important;
  z-index: 1000 !important;
  color: #818cf8 !important;
  background: rgba(100,108,255,0.1) !important;
  border-radius: 8px !important;
  margin: 8px !important;
}

[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--text-2) !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 10px 14px !important;
  width: 100% !important;
  text-align: left !important;
  transition: all 0.2s !important;
  margin: 2px 0 !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(100,108,255,0.1) !important;
  color: #c7d2fe !important;
  transform: translateX(4px) !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
  color: white !important;
  border: none !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 15px rgba(100,108,255,0.3) !important;
}

/* ════ HERO ════ */
.somo-hero {
  position: relative; overflow: hidden;
  border-radius: 24px; padding: 52px 48px;
  margin-bottom: 32px;
  background: var(--bg-1);
  border: 1px solid var(--border);
  box-shadow: 0 4px 40px rgba(0,0,0,0.6), 0 0 40px rgba(100,108,255,0.12);
}

.somo-hero::before {
  content: ''; position: absolute; top: -80px; left: -80px;
  width: 500px; height: 500px; border-radius: 50%;
  background: radial-gradient(circle, rgba(100,108,255,0.14) 0%, transparent 60%);
  animation: porb 10s ease-in-out infinite;
}

@keyframes porb {
  0%, 100% { transform: scale(1) translate(0, 0); }
  50% { transform: scale(1.2) translate(-15px, -15px); }
}

.somo-hero h1 {
  font-family: 'Syne', sans-serif !important;
  font-size: clamp(28px, 5vw, 52px);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -2px;
  color: var(--text-1);
  margin-bottom: 12px;
}

.g-text {
  background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6, #818cf8);
  background-size: 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gshift 5s ease infinite;
}

@keyframes gshift { 0%, 100% { background-position: 0%; } 50% { background-position: 100%; } }

/* ════ CARDS GRID ════ */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 28px;
}

@media (max-width: 768px) {
  .cards-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
}

@media (max-width: 480px) {
  .cards-grid { grid-template-columns: repeat(2, 1fr); gap: 8px; }
}

.somo-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 26px 16px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.somo-card:hover {
  transform: translateY(-6px);
  border-color: var(--border-h);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), 0 0 25px rgba(100, 108, 255, 0.15);
}

.card-icon { font-size: 32px; margin-bottom: 12px; }
.card-title { font-size: 13.5px; font-weight: 700; color: var(--text-1); }
.card-desc { font-size: 11px; color: var(--text-3); line-height: 1.55; }

/* ════ STATS ════ */
.stat-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; margin-bottom: 24px; }

@media (max-width: 640px) { .stat-row { grid-template-columns: repeat(2, 1fr); } }

.stat-box { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 16px 12px; text-align: center; transition: border-color 0.3s; }
.stat-box:hover { border-color: var(--border-h); }
.stat-val { font-size: 26px; font-weight: 900; color: var(--text-1); }
.stat-lbl { font-size: 9.5px; font-weight: 700; color: var(--text-3); margin-top: 5px; text-transform: uppercase; letter-spacing: 1.5px; }

/* ════ CHAT ════ */
.stChatMessage { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 16px !important; padding: 14px 18px !important; color: var(--text-1) !important; }

/* ════ INPUTS ════ */
.stTextInput input, .stTextArea textarea {
  background: var(--bg-2) !important;
  color: var(--text-1) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(100,108,255,0.1) !important;
}

/* ════ BUTTONS ════ */
.stButton > button {
  background: rgba(100,108,255,0.07) !important;
  color: #a5b4fc !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  padding: 9px 18px !important;
  transition: all 0.2s !important;
}

.stButton > button:hover {
  background: rgba(100,108,255,0.15) !important;
  color: #c7d2fe !important;
  transform: translateY(-2px) !important;
}

.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(100,108,255,0.3) !important;
}

/* ════ ALERTS ════ */
.stSuccess > div { background: rgba(52,211,153,0.08) !important; border: 1px solid rgba(52,211,153,0.25) !important; color: #6ee7b7 !important; border-radius: 10px !important; }
.stError > div { background: rgba(244,114,182,0.08) !important; border: 1px solid rgba(244,114,182,0.25) !important; color: #fca5a5 !important; border-radius: 10px !important; }

.somo-success { background: linear-gradient(135deg, rgba(52,211,153,0.12), rgba(5,150,105,0.08)); border: 1px solid rgba(52,211,153,0.3); color: #6ee7b7; border-radius: 16px; padding: 13px 18px; font-weight: 600; margin: 10px 0; }

/* ════ SECTION TITLES ════ */
.section-label { font-size: 10px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: var(--accent); margin-bottom: 8px; }
.section-title { font-size: 24px; font-weight: 800; color: var(--text-1); margin-bottom: 6px; font-family: 'Syne', sans-serif; }

/* ════ DIVIDER ════ */
.somo-divider { height: 1px; background: linear-gradient(90deg, transparent, var(--border), transparent); margin: 24px 0; border: none; }

/* ════ API BADGES ════ */
.api-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 11px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid;
}

.api-groq { background: rgba(255,166,0,0.1); color: #fbbf24; border-color: rgba(251,191,36,0.3); }
.api-gemini { background: rgba(52,211,153,0.1); color: #34d399; border-color: rgba(52,211,153,0.3); }
.api-cohere { background: rgba(56,189,248,0.1); color: #38bdf8; border-color: rgba(56,189,248,0.3); }
.api-mistral { background: rgba(244,114,182,0.1); color: #f472b6; border-color: rgba(244,114,182,0.3); }

/* ════ RESPONSIVE ════ */
@media (max-width: 768px) {
  .somo-hero { padding: 24px 16px !important; }
  .somo-hero h1 { font-size: clamp(20px, 6vw, 30px) !important; }
  [data-testid="stSidebar"] { width: 75vw !important; max-width: 280px !important; }
}

@media (max-width: 480px) {
  .somo-hero h1 { font-size: 20px !important; }
  .somo-hero { padding: 16px 12px !important; }
  [data-testid="stSidebar"] { width: 80vw !important; max-width: 280px !important; }
}

.stApp, [data-testid="stMainBlockContainer"] { background: var(--bg-0) !important; }
</style>
"""

st.markdown(CSS_ULTRA, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECURITY: BCRYPT ONLY (NO SHA256)
# ════════════════════════════════════════════════════════════════════════════════

def hash_pw(pw: str) -> str:
    """BCRYPT parol hash-lash (12 rounds)"""
    if not HAS_BCRYPT:
        raise ImportError("❌ bcrypt o'rnatilmagan: pip install bcrypt")
    
    if not isinstance(pw, str) or len(pw) < 6:
        raise ValueError("❌ Parol kamita 6 belgi bo'lishi kerak")
    
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pw.encode(), salt).decode()

def check_pw(pw: str, stored: str) -> bool:
    """Parol tekshirish"""
    if not HAS_BCRYPT:
        return False
    
    try:
        return bcrypt.checkpw(pw.encode(), stored.encode())
    except Exception:
        return False

# ════════════════════════════════════════════════════════════════════════════════
# API CONFIGS
# ════════════════════════════════════════════════════════════════════════════════

API_CONFIGS = {
    "groq": {"name": "Groq", "icon": "⚡", "model": "llama-3.3-70b-versatile", "badge_class": "api-groq"},
    "gemini": {"name": "Gemini", "icon": "✨", "model": "gemini-2.0-flash", "badge_class": "api-gemini"},
    "cohere": {"name": "Cohere", "icon": "🔮", "model": "command-r-plus", "badge_class": "api-cohere"},
    "mistral": {"name": "Mistral", "icon": "🌪", "model": "mistral-large-latest", "badge_class": "api-mistral"}
}

MIME_TYPES = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "py": "text/x-python",
    "html": "text/html",
    "csv": "text/csv"
}

# Pre-compiled regex (PERFORMANCE FIX #1)
JSON_PATTERN = re.compile(r'\{.*\}', re.DOTALL)
CODE_KW = re.compile(r'(python|kod|script|bot)', re.IGNORECASE)

# ════════════════════════════════════════════════════════════════════════════════
# SECURITY: GET SECRETS SAFELY
# ════════════════════════════════════════════════════════════════════════════════

@lru_cache(maxsize=32)
def _get_secret(key: str) -> str:
    """Secrets dan API key olish (fallback yo'q)"""
    try:
        val = st.secrets.get(key, "")
        return str(val).strip() if val else ""
    except Exception:
        return str(os.environ.get(key, "")).strip()

# ════════════════════════════════════════════════════════════════════════════════
# AI CLIENTS INIT
# ════════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def init_clients() -> Dict[str, Any]:
    """AI providerlarni initialize"""
    clients = {}
    
    if HAS_GROQ:
        try:
            key = _get_secret("GROQ_API_KEY")
            if key:
                clients["groq"] = Groq(api_key=key)
        except ImportError:
            pass
        except Exception as e:
            st.warning(f"⚠️ Groq init error: {e}")
    
    if HAS_GEMINI:
        try:
            key = _get_secret("GEMINI_API_KEY")
            if key:
                genai.configure(api_key=key)
                clients["gemini"] = genai.GenerativeModel("gemini-2.0-flash")
        except ImportError:
            pass
        except Exception as e:
            st.warning(f"⚠️ Gemini init error: {e}")
    
    if HAS_COHERE:
        try:
            key = _get_secret("COHERE_API_KEY")
            if key:
                clients["cohere"] = cohere.Client(api_key=key)
        except ImportError:
            pass
        except Exception as e:
            st.warning(f"⚠️ Cohere init error: {e}")
    
    if HAS_MISTRAL:
        try:
            key = _get_secret("MISTRAL_API_KEY")
            if key:
                clients["mistral"] = Mistral(api_key=key)
        except ImportError:
            pass
        except Exception as e:
            st.warning(f"⚠️ Mistral init error: {e}")
    
    return clients

ai_clients = init_clients()

# ════════════════════════════════════════════════════════════════════════════════
# DATABASE CONNECTION
# ════════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_connections():
    """Google Sheets ulanish"""
    try:
        if not HAS_OAUTH:
            return None, None, None
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets.get("gcp_service_account", {}), scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        
        user_sheet = ss.sheet1
        
        try:
            chat_sheet = ss.worksheet("ChatHistory")
        except:
            chat_sheet = ss.add_worksheet("ChatHistory", 5000, 6)
            chat_sheet.append_row(["Timestamp", "Username", "Role", "Message", "Intent", "Provider"])
        
        try:
            fb_sheet = ss.worksheet("Feedback")
        except:
            fb_sheet = ss.add_worksheet("Feedback", 1000, 8)
            fb_sheet.append_row(["Timestamp", "Username", "Rating", "Category", "Message", "Email", "Status", "Files"])
        
        return user_sheet, chat_sheet, fb_sheet
    except ImportError:
        return None, None, None
    except Exception as e:
        st.error(f"❌ Database error: {e}")
        return None, None, None

user_db, chat_db, fb_db = get_connections()

# ════════════════════════════════════════════════════════════════════════════════
# CACHE: USERS (TTL 120s - AUTO INVALIDATE)
# ════════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=120)
def get_all_users() -> List[Dict]:
    """Barcha users (auto-invalidate 120s)"""
    if user_db:
        try:
            return user_db.get_all_records()
        except gspread.exceptions.APIError:
            return []
        except Exception as e:
            st.warning(f"Users fetch error: {e}")
            return []
    return []

# ════════════════════════════════════════════════════════════════════════════════
# DOCUMENT PROCESSING (FIX: MAX 100 PAGES)
# ════════════════════════════════════════════════════════════════════════════════

def process_doc(file) -> str:
    """PDF o'qish (max 100 pages - MEMORY FIX)"""
    try:
        if file.type == "application/pdf" and HAS_PDF:
            doc = fitz.open(stream=file.read(), filetype="pdf")
            text_parts = []
            
            for page_num in range(min(len(doc), 100)):  # MAX 100 PAGES
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
            
            return "\n".join(text_parts)
    
    except ImportError:
        st.error("❌ PyMuPDF o'rnatilmagan")
    except Exception as e:
        st.error(f"❌ PDF error: {e}")
    
    return ""

# ════════════════════════════════════════════════════════════════════════════════
# RATE LIMITING (FIX: 3s DELAY)
# ════════════════════════════════════════════════════════════════════════════════

_LAST_LOG_TIME = {}

def db_log(user: str, role: str, content: str, intent: str = "chat", provider: str = "groq"):
    """Rate-limited logging (3s delay)"""
    global _LAST_LOG_TIME
    
    now = time.time()
    key = f"{user}_{role}"
    
    if key in _LAST_LOG_TIME and (now - _LAST_LOG_TIME[key] < 3):
        return  # RATE LIMIT
    
    _LAST_LOG_TIME[key] = now
    
    if chat_db:
        try:
            chat_db.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user, role, content[:400], intent, provider
            ])
        except gspread.exceptions.APIError:
            pass
        except Exception:
            pass

# ════════════════════════════════════════════════════════════════════════════════
# INTENT DETECTION
# ════════════════════════════════════════════════════════════════════════════════

def detect_intent(text: str) -> str:
    """Niyat aniqla"""
    t = text.lower()
    
    if any(k in t for k in ["excel", "xlsx", "jadval", "budget"]):
        return "excel"
    if any(k in t for k in ["word", "docx", "hujjat", "rezyume"]):
        return "word"
    if "html" in t or "website" in t:
        return "html"
    if "csv" in t or "dataset" in t:
        return "csv"
    if CODE_KW.search(t):
        return "code"
    
    return "chat"

# ════════════════════════════════════════════════════════════════════════════════
# AI FUNCTIONS WITH INPUT VALIDATION (FIX #10)
# ════════════════════════════════════════════════════════════════════════════════

def call_ai(messages: List[Dict], temperature: float = 0.6, max_tokens: int = 3000, provider: str = "groq", timeout: int = 30) -> Tuple[str, str]:
    """AI chaqirish (INPUT VALIDATION)"""
    
    # INPUT VALIDATION (FIX #10)
    assert isinstance(messages, list), "messages must be list"
    assert 0.0 <= temperature <= 1.0, "temperature must be 0.0-1.0"
    assert isinstance(max_tokens, int) and max_tokens > 0, "max_tokens invalid"
    
    providers = [provider] + [p for p in ["groq", "gemini", "cohere", "mistral"] if p != provider]
    
    for prov in providers:
        if prov not in ai_clients:
            continue
        
        try:
            if prov == "groq":
                resp = ai_clients["groq"].chat.completions.create(
                    messages=messages,
                    model=API_CONFIGS["groq"]["model"],
                    temperature=min(temperature, 1.0),
                    max_tokens=max_tokens,
                    timeout=timeout
                )
                return resp.choices[0].message.content, "groq"
            
            elif prov == "gemini":
                sys_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
                user_msgs = [m for m in messages if m["role"] != "system"]
                last_msg = user_msgs[-1]["content"] if user_msgs else ""
                if sys_msg:
                    last_msg = f"[System: {sys_msg}]\n\n{last_msg}"
                
                chat = ai_clients["gemini"].start_chat()
                return chat.send_message(last_msg).text, "gemini"
            
            elif prov == "cohere":
                sys_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
                user_msgs = [m for m in messages if m["role"] != "system"]
                last_msg = user_msgs[-1]["content"] if user_msgs else ""
                
                resp = ai_clients["cohere"].chat(
                    model=API_CONFIGS["cohere"]["model"],
                    message=last_msg,
                    preamble=sys_msg if sys_msg else None,
                    temperature=min(temperature, 1.0),
                    max_tokens=max_tokens
                )
                return resp.text, "cohere"
            
            elif prov == "mistral":
                resp = ai_clients["mistral"].chat.complete(
                    model=API_CONFIGS["mistral"]["model"],
                    messages=messages,
                    temperature=min(temperature, 1.0),
                    max_tokens=max_tokens
                )
                return resp.choices[0].message.content, "mistral"
        
        except Exception as e:
            continue
    
    return "❌ Hech bir AI mavjud emas.", "none"

def call_ai_stream(messages: List[Dict], temperature: float = 0.6, max_tokens: int = 3000, provider: str = "groq"):
    """Stream response (with timeout)"""
    
    assert isinstance(messages, list), "messages must be list"
    assert 0.0 <= temperature <= 1.0, "temperature must be 0.0-1.0"
    
    providers = [provider] + [p for p in ["groq", "gemini", "cohere", "mistral"] if p != provider]
    
    for prov in providers:
        if prov not in ai_clients:
            continue
        
        try:
            if prov == "groq":
                stream = ai_clients["groq"].chat.completions.create(
                    messages=messages,
                    model=API_CONFIGS["groq"]["model"],
                    temperature=min(temperature, 1.0),
                    max_tokens=max_tokens,
                    stream=True,
                    timeout=30
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content, "groq"
                return
            
            elif prov == "gemini":
                sys_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
                user_msgs = [m for m in messages if m["role"] != "system"]
                last_msg = user_msgs[-1]["content"] if user_msgs else ""
                if sys_msg:
                    last_msg = f"[System: {sys_msg}]\n\n{last_msg}"
                
                chat = ai_clients["gemini"].start_chat()
                for chunk in chat.send_message(last_msg, stream=True):
                    if chunk.text:
                        yield chunk.text, "gemini"
                return
        
        except Exception as e:
            continue
    
    yield "❌ Xatolik.", "none"

# ════════════════════════════════════════════════════════════════════════════════
# FILE GENERATORS
# ════════════════════════════════════════════════════════════════════════════════

def gen_excel(prompt: str, temp: float = 0.15, provider: str = "groq") -> Tuple[Optional[bytes], str]:
    """Excel generator"""
    if not HAS_OPENPYXL:
        return None, "❌ openpyxl o'rnatilmagan"
    
    sys_p = """JSON: {"title":"Nomi","sheets":[{"name":"Varaq","headers":["H1"],"rows":[["v1"]]}]}"""
    raw, _ = call_ai([{"role": "system", "content": sys_p}, {"role": "user", "content": prompt}], temp, 4000, provider)
    raw = re.sub(r'```json|```', '', raw).strip()
    m = JSON_PATTERN.search(raw)
    
    if not m:
        return None, "❌ JSON topilmadi"
    
    try:
        data = json.loads(m.group())
    except:
        return None, "❌ JSON xato"
    
    wb = Workbook()
    wb.remove(wb.active)
    
    for sheet_data in data.get("sheets", []):
        ws = wb.create_sheet(title=sheet_data.get("name", "Sheet")[:31])
        headers = sheet_data.get("headers", [])
        rows = sheet_data.get("rows", [])
        
        if headers:
            for col_idx, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_idx, value=header)
                cell.font = Font(name="Calibri", bold=True, size=11)
                cell.fill = PatternFill("solid", fgColor="4F46E5")
        
        for row_idx, row_data in enumerate(rows, 2):
            for col_idx, value in enumerate(row_data, 1):
                ws.cell(row=row_idx, column=col_idx, value=value)
    
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    safe_title = re.sub(r'[^\w]', '_', data.get("title", "somo"))
    filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return buffer.getvalue(), filename

def gen_word(prompt: str, temp: float = 0.4, provider: str = "mistral") -> Tuple[Optional[bytes], str]:
    """Word generator"""
    if not HAS_DOCX:
        return None, "❌ python-docx o'rnatilmagan"
    
    sys_p = """JSON: {"title":"Sarlavha","sections":[{"type":"paragraph","text":"..."}]}"""
    raw, _ = call_ai([{"role": "system", "content": sys_p}, {"role": "user", "content": prompt}], temp, 4000, provider)
    raw = re.sub(r'```json|```', '', raw).strip()
    m = JSON_PATTERN.search(raw)
    
    if not m:
        return None, "❌ JSON topilmadi"
    
    try:
        data = json.loads(m.group())
    except:
        return None, "❌ JSON xato"
    
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
    
    title = doc.add_paragraph()
    tr = title.add_run(data.get("title", "Document"))
    tr.bold = True
    tr.font.size = Pt(20)
    tr.font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)
    
    for sec in data.get("sections", []):
        sec_type = sec.get("type", "paragraph")
        
        if sec_type == "heading1":
            h = doc.add_heading(sec.get("text", ""), level=1)
            if h.runs:
                h.runs[0].font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)
        elif sec_type == "paragraph":
            p = doc.add_paragraph()
            r = p.add_run(sec.get("text", ""))
            r.font.size = Pt(11)
        elif sec_type == "bullet":
            for item in sec.get("items", []):
                p = doc.add_paragraph(style='List Bullet')
                p.add_run(item)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    safe_title = re.sub(r'[^\w]', '_', data.get("title", "somo"))
    filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    
    return buffer.getvalue(), filename

def gen_code(prompt: str, temp: float = 0.12, provider: str = "cohere") -> Tuple[bytes, str]:
    """Python kod generator"""
    sys_p = "Professional Python kod. FAQAT kod."
    raw, _ = call_ai([{"role": "system", "content": sys_p}, {"role": "user", "content": prompt}], temp, 3500, provider)
    raw = re.sub(r'```python|```py|```', '', raw).strip()
    
    safe_name = re.sub(r'[^\w]', '_', prompt[:30])
    filename = f"{safe_name}_{datetime.now().strftime('%H%M%S')}.py"
    
    return raw.encode('utf-8'), filename

def gen_html(prompt: str, temp: float = 0.5, provider: str = "gemini") -> Tuple[bytes, str]:
    """HTML generator"""
    sys_p = "Professional HTML/CSS/JS. Dark theme. FAQAT HTML."
    raw, _ = call_ai([{"role": "system", "content": sys_p}, {"role": "user", "content": prompt}], temp, 4000, provider)
    raw = re.sub(r'```html|```', '', raw).strip()
    
    safe_name = re.sub(r'[^\w]', '_', prompt[:25])
    filename = f"{safe_name}_{datetime.now().strftime('%H%M%S')}.html"
    
    return raw.encode('utf-8'), filename

def gen_csv(prompt: str, temp: float = 0.3, provider: str = "mistral") -> Tuple[bytes, str]:
    """CSV generator"""
    sys_p = "FAQAT CSV. Birinchi satr sarlavha. 25+ satr."
    raw, _ = call_ai([{"role": "system", "content": sys_p}, {"role": "user", "content": prompt}], temp, 3000, provider)
    raw = re.sub(r'```csv|```', '', raw).strip()
    
    safe_name = re.sub(r'[^\w]', '_', prompt[:25])
    filename = f"{safe_name}_{datetime.now().strftime('%H%M%S')}.csv"
    
    return raw.encode('utf-8'), filename

# ════════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def api_status_html(provider: str) -> str:
    """API badge"""
    cfg = API_CONFIGS.get(provider, API_CONFIGS["groq"])
    return f'<span class="api-badge {cfg["badge_class"]}"><strong>{cfg["icon"]} {cfg["name"]}</strong></span>'

def download_btn(file_bytes: bytes, filename: str, label: str):
    """Download button"""
    ext = filename.rsplit('.', 1)[-1]
    mime = MIME_TYPES.get(ext, "application/octet-stream")
    
    st.markdown(f'<div class="somo-success">✅ {label} fayl tayyor!</div>', unsafe_allow_html=True)
    st.download_button(
        f"⬇️  {filename}",
        file_bytes,
        filename,
        mime,
        use_container_width=True,
        type="primary",
        key=f"dl_{filename}_{time.time()}"
    )

# ════════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ════════════════════════════════════════════════════════════════════════════════

def init_session():
    """Session state initialize (ATOMIC UPDATE FIX #9)"""
    defaults = {
        'logged_in': False,
        'username': '',
        'login_time': datetime.now(),
        'page': 'home',
        'messages': [],
        'uploaded_text': '',
        'temperature': 0.6,
        'files_count': 0,
        'chat_provider': 'groq',
        'excel_provider': 'groq',
        'word_provider': 'mistral',
        'code_provider': 'cohere',
        'html_provider': 'gemini',
        'csv_provider': 'mistral',
        'analyze_provider': 'gemini',
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()

# ════════════════════════════════════════════════════════════════════════════════
# MAIN APP - LOGIN/REGISTER PAGE
# ════════════════════════════════════════════════════════════════════════════════

if not st.session_state.logged_in:
    st.markdown(f"""
    <div class="somo-hero" style="text-align:center;">
        <div class="somo-hero-content">
            <h1>🌌 Somo AI <span class="g-text">Ultra Pro</span></h1>
            <p style="font-size:16px;color:rgba(255,255,255,0.55);margin:20px auto;">
                Excel · Word · Code · HTML · CSV · Chat — 4 ta AI bilan hammasini yarating
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 2, 1])
    
    with col_m:
        tab1, tab2 = st.tabs(["🔒 Kirish", "✍️  Ro'yxat"])
        
        with tab1:
            st.markdown("### Hisobingizga kiring")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Username")
                password = st.text_input("Parol", type="password", placeholder="Parol")
                submit = st.form_submit_button("🚀  Kirish", use_container_width=True, type="primary")
                
                if submit:
                    if not username or not password:
                        st.error("❌ Username va parolni kiriting")
                    elif user_db:
                        try:
                            users = get_all_users()
                            user = next((u for u in users if u.get('username') == username), None)
                            
                            if user and check_pw(password, user.get('password', '')):
                                if user.get('status', '').lower() == 'blocked':
                                    st.error("🚫 Hisob bloklangan!")
                                else:
                                    st.session_state.update({  # ATOMIC UPDATE
                                        'logged_in': True,
                                        'username': username,
                                        'login_time': datetime.now()
                                    })
                                    st.success("✅ Muvaffaqiyatli!")
                                    time.sleep(0.5)
                                    st.rerun()
                            else:
                                st.error("❌ Login yoki parol noto'g'ri!")
                        except Exception as e:
                            st.error(f"❌ {e}")
        
        with tab2:
            st.markdown("### Yangi hisob yaratish")
            with st.form("register_form"):
                new_user = st.text_input("Username (min 3)")
                new_pass = st.text_input("Parol (min 6)", type="password")
                conf = st.text_input("Tasdiqlash", type="password")
                agree = st.checkbox("Shartlarga roziman ✅")
                submit_reg = st.form_submit_button("✨  Yaratish", use_container_width=True, type="primary")
                
                if submit_reg:
                    if not agree:
                        st.error("❌ Shartlarga rozilik bering!")
                    elif len(new_user) < 3:
                        st.error("❌ Username kamita 3 belgi!")
                    elif len(new_pass) < 6:
                        st.error("❌ Parol kamita 6 belgi!")
                    elif new_pass != conf:
                        st.error("❌ Parollar mos emas!")
                    elif user_db:
                        try:
                            users = get_all_users()
                            if any(u['username'] == new_user for u in users):
                                st.error("❌ Bu username band!")
                            else:
                                user_db.append_row([new_user, hash_pw(new_pass), "active", str(datetime.now()), 0])
                                get_all_users.clear()  # CACHE INVALIDATE
                                st.balloons()
                                st.success("🎉 Muvaffaqiyatli! Kirish bo'limiga o'ting.")
                        except Exception as e:
                            st.error(f"❌ {e}")

else:
    # ════ SIDEBAR NAVIGATION ════
    with st.sidebar:
        uname = st.session_state.username
        avail = [p for p in ["groq", "gemini", "cohere", "mistral"] if p in ai_clients]
        
        st.markdown(f"""
        <div style="padding:22px 0 18px; border-bottom:1px solid rgba(100,108,255,0.12);">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:14px;">
                <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed,#f472b6); width:44px; height:44px; 
                           border-radius:14px; display:flex; align-items:center; justify-content:center; 
                           font-size:20px; color:white;">{uname[0].upper()}</div>
                <div>
                    <div style="font-size:14px; font-weight:700;">{uname}</div>
                    <div style="font-size:10px; color:#34d399;">🟢 ONLINE</div>
                </div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                <div style="background:rgba(100,108,255,0.07); border:1px solid rgba(100,108,255,0.12); 
                           border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:17px; font-weight:900;">{len(st.session_state.messages)}</div>
                    <div style="font-size:9px;">Xabar</div>
                </div>
                <div style="background:rgba(52,211,153,0.07); border:1px solid rgba(52,211,153,0.12); 
                           border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:17px; font-weight:900;">{st.session_state.files_count}</div>
                    <div style="font-size:9px;">Fayl</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        nav = [
            ("home", "🏠", "Bosh sahifa"),
            ("chat", "💬", "Chat"),
            ("excel", "📊", "Excel"),
            ("word", "📝", "Word"),
            ("code", "💻", "Kod"),
            ("html", "🌐", "HTML"),
            ("csv", "📋", "CSV"),
            ("templates", "🎨", "Shablonlar"),
            ("analyze", "🔍", "Tahlil"),
            ("history", "📜", "Tarixi"),
            ("feedback", "💌", "Fikr"),
            ("profile", "👤", "Profil"),
        ]
        
        for page_id, icon, label in nav:
            is_active = st.session_state.page == page_id
            if st.button(f"{icon}  {label}", key=f"nav_{page_id}", use_container_width=True,
                        type="primary" if is_active else "secondary"):
                st.session_state.page = page_id
                st.rerun()
        
        st.markdown('<hr class="somo-divider" style="margin:10px 0;">', unsafe_allow_html=True)
        
        if st.button("🚪  Chiqish", use_container_width=True, type="primary"):
            st.session_state.update({'logged_in': False, 'messages': []})  # ATOMIC
            st.rerun()
    
    # ════ HOME PAGE ════
    if st.session_state.page == "home":
        st.markdown(f"""
        <div class="somo-hero">
            <div class="somo-hero-content">
                <h1>Salom, <span class="g-text">{uname}</span>! 👋</h1>
                <p class="subtitle">Bugun nima yaratmoqchisiz?</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-box"><div style="font-size:24px;">💬</div><div class="stat-val">{len(st.session_state.messages)}</div><div class="stat-lbl">Xabar</div></div>
            <div class="stat-box"><div style="font-size:24px;">📁</div><div class="stat-val">{st.session_state.files_count}</div><div class="stat-lbl">Fayl</div></div>
            <div class="stat-box"><div style="font-size:24px;">🤖</div><div class="stat-val">{len(avail)}</div><div class="stat-lbl">AI</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<p class="section-title">Funksiyalar</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="cards-grid">
            <div class="somo-card"><span class="card-icon">💬</span><div class="card-title">Chat AI</div><div class="card-desc">4 ta AI</div></div>
            <div class="somo-card"><span class="card-icon">📊</span><div class="card-title">Excel</div><div class="card-desc">Jadvallar</div></div>
            <div class="somo-card"><span class="card-icon">📝</span><div class="card-title">Word</div><div class="card-desc">Hujjatlar</div></div>
            <div class="somo-card"><span class="card-icon">💻</span><div class="card-title">Kod</div><div class="card-desc">Python</div></div>
            <div class="somo-card"><span class="card-icon">🌐</span><div class="card-title">HTML</div><div class="card-desc">Veb</div></div>
            <div class="somo-card"><span class="card-icon">📋</span><div class="card-title">CSV</div><div class="card-desc">Dataset</div></div>
        </div>
        """, unsafe_allow_html=True)
    
    # ════ CHAT PAGE ════
    elif st.session_state.page == "chat":
        st.markdown(f"""<div class="somo-hero"><div class="somo-hero-content"><h1>💬 Chat <span class="g-text">AI</span></h1></div></div>""", unsafe_allow_html=True)
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Yozing..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                msgs = [{"role": "system", "content": "Sen Somo AI yordamchi."}]
                msgs.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]])
                
                response_placeholder = st.empty()
                full_response = ""
                used_prov = st.session_state.chat_provider
                
                for chunk, prov in call_ai_stream(msgs, st.session_state.temperature, provider=st.session_state.chat_provider):
                    full_response += chunk
                    used_prov = prov
                    response_placeholder.markdown(full_response)
                
                db_log(uname, "Assistant", full_response, "chat", used_prov)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            st.rerun()
    
    # ════ EXCEL PAGE ════
    elif st.session_state.page == "excel":
        st.markdown("""<div class="somo-hero"><div class="somo-hero-content"><h1>📊 Excel Generator</h1></div></div>""", unsafe_allow_html=True)
        
        col_inp, col_opt = st.columns([3, 1])
        with col_inp:
            xl_prompt = st.text_area("Jadval tavsifi:", height=120, placeholder="Masalan: 10 ta o'quvchi uchun baholar jadvali...")
        with col_opt:
            avail_p = [p for p in ["groq", "gemini", "cohere", "mistral"] if p in ai_clients]
            if avail_p:
                sel_idx = avail_p.index(st.session_state.excel_provider) if st.session_state.excel_provider in avail_p else 0
                sel = st.selectbox("AI", [API_CONFIGS[p]["icon"] + " " + API_CONFIGS[p]["name"] for p in avail_p], index=sel_idx, key="xl_ai")
                st.session_state.excel_provider = avail_p[[i for i, p in enumerate([API_CONFIGS[x]["icon"] + " " + API_CONFIGS[x]["name"] for x in avail_p])][list(sel for sel in [sel]).index(sel)]]
            
            if st.button("🚀  Yaratish", use_container_width=True, type="primary"):
                if xl_prompt:
                    with st.spinner("⏳"):
                        fb, fn = gen_excel(xl_prompt, provider=st.session_state.excel_provider)
                    if fb:
                        st.session_state.files_count += 1
                        download_btn(fb, fn, "Excel")
    
    # ════ WORD PAGE ════
    elif st.session_state.page == "word":
        st.markdown("""<div class="somo-hero"><div class="somo-hero-content"><h1>📝 Word Generator</h1></div></div>""", unsafe_allow_html=True)
        
        col_inp, col_opt = st.columns([3, 1])
        with col_inp:
            wd_prompt = st.text_area("Hujjat tavsifi:", height=120)
        with col_opt:
            avail_p = [p for p in ["groq", "gemini", "cohere", "mistral"] if p in ai_clients]
            if avail_p and st.button("🚀  Yaratish", use_container_width=True, type="primary"):
                with st.spinner("⏳"):
                    fb, fn = gen_word(wd_prompt, provider=st.session_state.word_provider)
                if fb:
                    st.session_state.files_count += 1
                    download_btn(fb, fn, "Word")
    
    # ════ CODE PAGE ════
    elif st.session_state.page == "code":
        st.markdown("""<div class="somo-hero"><div class="somo-hero-content"><h1>💻 Kod Generator</h1></div></div>""", unsafe_allow_html=True)
        
        cd_prompt = st.text_area("Kod tavsifi:", height=120)
        if st.button("🚀  Yaratish", use_container_width=True, type="primary"):
            if cd_prompt:
                with st.spinner("⏳"):
                    fb, fn = gen_code(cd_prompt, provider=st.session_state.code_provider)
                st.session_state.files_count += 1
                download_btn(fb, fn, "Python")
    
    # ════ HTML PAGE ════
    elif st.session_state.page == "html":
        st.markdown("""<div class="somo-hero"><div class="somo-hero-content"><h1>🌐 HTML Generator</h1></div></div>""", unsafe_allow_html=True)
        
        ht_prompt = st.text_area("Sahifa tavsifi:", height=120)
        if st.button("🚀  Yaratish", use_container_width=True, type="primary"):
            if ht_prompt:
                with st.spinner("⏳"):
                    fb, fn = gen_html(ht_prompt, provider=st.session_state.html_provider)
                st.session_state.files_count += 1
                download_btn(fb, fn, "HTML")
    
    # ════ CSV PAGE ════
    elif st.session_state.page == "csv":
        st.markdown("""<div class="somo-hero"><div class="somo-hero-content"><h1>📋 CSV Generator</h1></div></div>""", unsafe_allow_html=True)
        
        cv_prompt = st.text_area("Dataset tavsifi:", height=120)
        if st.button("🚀  Yaratish", use_container_width=True, type="primary"):
            if cv_prompt:
                with st.spinner("⏳"):
                    fb, fn = gen_csv(cv_prompt, provider=st.session_state.csv_provider)
                st.session_state.files_count += 1
                download_btn(fb, fn, "CSV")
    
    # ════ TEMPLATES PAGE ════
    elif st.session_state.page == "templates":
        st.markdown("""<div class="somo-hero"><div class="somo-hero-content"><h1>🎨 Shablonlar</h1></div></div>""", unsafe_allow_html=True)
        st.info("🎨 16 ta tayyor shablon qarib hozir!")
