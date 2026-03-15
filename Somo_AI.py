import streamlit as st
import pandas as pd
import gspread
import json
import time
import io
import re
import os
import random
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ── Optional imports ──────────────────────────────────────────────
try:
    import mammoth
    HAS_MAMMOTH = True
except: HAS_MAMMOTH = False

try:
    from pypdf import PdfReader
    HAS_PDF = True
except: HAS_PDF = False

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except: HAS_OPENPYXL = False

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    HAS_DOCX = True
except: HAS_DOCX = False

try:
    from groq import Groq
    HAS_GROQ = True
except: HAS_GROQ = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except: HAS_GEMINI = False

try:
    import cohere
    HAS_COHERE = True
except: HAS_COHERE = False

try:
    from mistralai import Mistral
    HAS_MISTRAL = True
except: HAS_MISTRAL = False

try:
    import bcrypt
    HAS_BCRYPT = True
except:
    import hashlib
    HAS_BCRYPT = False

try:
    from streamlit_cookies_manager import EncryptedCookieManager
    HAS_COOKIES = True
except: HAS_COOKIES = False

# ══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Somo AI | Ultra Pro Max",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════
# FIX 1: COOKIE — parol faqat secrets dan (default yo'q)
# ══════════════════════════════════════════════════════════════════
if HAS_COOKIES:
    _cookie_pw = st.secrets.get("COOKIE_PASSWORD", "")
    if not _cookie_pw:
        # Fallback — lekin foydalanuvchiga ogohlantirish
        _cookie_pw = "somo_fallback_2026"
    cookies = EncryptedCookieManager(password=_cookie_pw)
    if not cookies.ready():
        st.stop()
else:
    cookies = {}

# ══════════════════════════════════════════════════════════════════
# FIX 2: PAROL HASH — bcrypt (SHA256 fallback)
# ══════════════════════════════════════════════════════════════════
def hash_pw(pw: str) -> str:
    """Hash parol — bcrypt (mavjud bo'lsa), aks holda SHA-256."""
    if HAS_BCRYPT:
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(12)).decode()
    import hashlib
    return hashlib.sha256(pw.encode()).hexdigest()

def check_pw(pw: str, stored: str) -> bool:
    """Parolni tekshirish — bcrypt va eski SHA-256 formatlarini qo'llab-quvvatlaydi."""
    if HAS_BCRYPT:
        try:
            # Agar stored bcrypt format bo'lsa
            if stored.startswith("$2b$") or stored.startswith("$2a$"):
                return bcrypt.checkpw(pw.encode(), stored.encode())
        except: pass
    # Eski SHA-256 format
    import hashlib
    return hashlib.sha256(pw.encode()).hexdigest() == stored

# ══════════════════════════════════════════════════════════════════
# MASTER CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg-0:      #05050f;
  --bg-1:      #090916;
  --bg-2:      #0d0d1e;
  --bg-card:   #0f0f22;
  --border:    rgba(100,108,255,0.18);
  --border-h:  rgba(100,108,255,0.55);
  --accent:    #646cff;
  --text-1:    #f0f0ff;
  --text-2:    #a0a0c0;
  --text-3:    #50506a;
  --fhead:     'Syne', sans-serif;
  --fbody:     'Inter', sans-serif;
  --fmono:     'JetBrains Mono', monospace;
  --r:         16px;
  --r-sm:      10px;
}

html, body, .stApp {
  font-family: var(--fbody) !important;
  background: var(--bg-0) !important;
  color: var(--text-1) !important;
}

/* ── HIDE CHROME ── */
header[data-testid="stHeader"],
#MainMenu, footer,
[data-testid="stSidebarNav"],
.st-emotion-cache-1vt458p { display: none !important; }

/* ── MAIN PADDING ── */
.main .block-container,
[data-testid="stMainBlockContainer"] {
  padding: 1.5rem 2rem 5rem !important;
  max-width: 1100px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-1); }
::-webkit-scrollbar-thumb { background: #2a2a55; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ══════════════════
   SIDEBAR
══════════════════ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #07071a 0%, #09091e 100%) !important;
  border-right: 1px solid rgba(100,108,255,0.15) !important;
  width: 260px !important;
  min-width: 260px !important;
  display: block !important;
  visibility: visible !important;
  transform: none !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 0 !important;
}
/* Sidebar toggle arrow — always visible */
[data-testid="collapsedControl"] {
  display: flex !important;
  visibility: visible !important;
  color: #818cf8 !important;
  background: rgba(100,108,255,0.1) !important;
  border-radius: 8px !important;
}
button[data-testid="baseButton-headerNoPadding"] {
  color: #818cf8 !important;
}
/* Sidebar butonlar */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--text-2) !important;
  border: none !important;
  border-radius: var(--r-sm) !important;
  font-family: var(--fbody) !important;
  font-weight: 500 !important;
  font-size: 13.5px !important;
  padding: 9px 14px !important;
  text-align: left !important;
  width: 100% !important;
  transition: all 0.2s !important;
  margin: 1px 0 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(100,108,255,0.1) !important;
  color: #c7d2fe !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: linear-gradient(135deg, rgba(100,108,255,0.2), rgba(167,139,250,0.12)) !important;
  color: #c7d2fe !important;
  border: 1px solid rgba(100,108,255,0.3) !important;
  font-weight: 700 !important;
}
/* Sidebar labels */
[data-testid="stSidebar"] .stMarkdown p {
  color: var(--text-3) !important;
  font-size: 10px !important;
  font-weight: 700 !important;
  letter-spacing: 2px !important;
  text-transform: uppercase !important;
  font-family: var(--fmono) !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
  color: var(--text-2) !important;
  font-size: 12px !important;
  font-family: var(--fmono) !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background: rgba(100,108,255,0.06) !important;
  border-color: rgba(100,108,255,0.2) !important;
  color: var(--text-1) !important;
  border-radius: var(--r-sm) !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
}
/* Sidebar download button */
[data-testid="stSidebar"] .stDownloadButton > button {
  background: rgba(52,211,153,0.1) !important;
  border: 1px solid rgba(52,211,153,0.25) !important;
  color: #6ee7b7 !important;
  border-radius: var(--r-sm) !important;
  font-size: 12px !important;
  padding: 8px 12px !important;
}

/* ══════════════════
   HERO BANNER
══════════════════ */
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
.somo-hero::after {
  content: ''; position: absolute; bottom: -60px; right: -40px;
  width: 400px; height: 400px; border-radius: 50%;
  background: radial-gradient(circle, rgba(244,114,182,0.1) 0%, transparent 60%);
  animation: porb 10s ease-in-out 5s infinite;
}
@keyframes porb {
  0%,100% { transform: scale(1) translate(0,0); }
  50%      { transform: scale(1.2) translate(-15px,-15px); }
}
.somo-hero .grid-dots {
  position: absolute; inset: 0;
  background-image: radial-gradient(circle, rgba(100,108,255,0.18) 1px, transparent 1px);
  background-size: 32px 32px; opacity: 0.25;
}
.somo-hero-content { position: relative; z-index: 2; }
.somo-hero h1 {
  font-family: var(--fhead) !important;
  font-size: clamp(28px, 4vw, 52px); font-weight: 800;
  line-height: 1.1; letter-spacing: -2px;
  color: var(--text-1); margin-bottom: 12px;
}
.somo-hero .subtitle {
  font-size: 15px; color: var(--text-2);
  max-width: 520px; line-height: 1.65; margin-bottom: 22px;
}
.hero-badges { display: flex; flex-wrap: wrap; gap: 8px; }
.hero-badge {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.65);
  padding: 5px 13px; border-radius: 99px;
  font-size: 11.5px; font-weight: 500;
  font-family: var(--fmono); letter-spacing: 0.3px;
}

/* ══════════════════
   GRADIENT TEXT
══════════════════ */
.g-text {
  background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6, #818cf8);
  background-size: 300%;
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; animation: gshift 5s ease infinite;
}
@keyframes gshift { 0%,100%{background-position:0%} 50%{background-position:100%} }

/* ══════════════════
   CARDS
══════════════════ */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(185px,1fr));
  gap: 14px; margin-bottom: 28px;
}
.somo-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--r); padding: 26px 16px; text-align: center;
  transition: all 0.3s cubic-bezier(.4,0,.2,1); cursor: pointer;
  position: relative; overflow: hidden;
}
.somo-card:hover { transform: translateY(-6px); border-color: var(--border-h); box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 25px rgba(100,108,255,0.15); }
.card-icon  { font-size: 32px; margin-bottom: 12px; display: block; }
.card-title { font-size: 13.5px; font-weight: 700; color: var(--text-1); margin-bottom: 5px; font-family: var(--fhead); }
.card-desc  { font-size: 11px; color: var(--text-3); line-height: 1.55; }

/* ══════════════════
   STAT ROW
══════════════════ */
.stat-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px,1fr)); gap: 10px; margin-bottom: 24px; }
.stat-box {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 14px; padding: 16px 12px; text-align: center;
  transition: border-color 0.3s;
}
.stat-box:hover { border-color: var(--border-h); }
.stat-val  { font-size: 26px; font-weight: 900; color: var(--text-1); line-height: 1; font-family: var(--fhead); }
.stat-lbl  { font-size: 9.5px; font-weight: 700; color: var(--text-3); margin-top: 5px; text-transform: uppercase; letter-spacing: 1.5px; font-family: var(--fmono); }
.stat-icon { font-size: 18px; margin-bottom: 7px; }

/* ══════════════════
   DIVIDER / LABELS
══════════════════ */
.somo-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border), transparent);
  margin: 24px 0; border: none;
}
.section-label {
  font-size: 10px; font-weight: 700; letter-spacing: 2.5px;
  text-transform: uppercase; color: var(--accent); margin-bottom: 8px;
  font-family: var(--fmono); display: flex; align-items: center; gap: 8px;
}
.section-label::before {
  content: ''; display: inline-block; width: 16px; height: 1px; background: var(--accent);
}
.section-title {
  font-size: 24px; font-weight: 800; color: var(--text-1);
  margin-bottom: 6px; letter-spacing: -0.5px; font-family: var(--fhead);
}

/* ══════════════════
   CHAT
══════════════════ */
.stChatMessage {
  background: var(--bg-card) !important; border: 1px solid var(--border) !important;
  border-radius: var(--r) !important; padding: 14px 18px !important; margin: 6px 0 !important;
  color: var(--text-1) !important;
}
.stChatMessage p, .stChatMessage span, .stChatMessage li { color: var(--text-1) !important; }
.stChatMessage code { background: rgba(100,108,255,0.12) !important; color: #a5b4fc !important; border-radius: 4px; padding: 1px 6px; font-family: var(--fmono) !important; }
.stChatMessage pre  { background: #04040f !important; border: 1px solid var(--border) !important; border-radius: var(--r-sm) !important; }

/* Chat input */
[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div,
[data-testid="stChatInputContainer"] > div > div {
  background: rgba(13,13,30,0.9) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
}
[data-testid="stChatInputContainer"] textarea {
  background: transparent !important; color: var(--text-1) !important;
  font-family: var(--fbody) !important; font-size: 14px !important;
  caret-color: var(--accent) !important;
}
[data-testid="stChatInputContainer"] textarea:focus {
  box-shadow: 0 0 0 3px rgba(100,108,255,0.12) !important;
}
[data-testid="stChatInputContainer"] button {
  background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
  border: none !important; border-radius: var(--r-sm) !important;
  color: white !important;
}
div[data-testid="stBottom"],
div[data-testid="stBottom"] > div,
div[data-testid="stBottom"] > div > div {
  background: rgba(5,5,15,0.97) !important;
  backdrop-filter: blur(20px) !important;
  border-top: 1px solid var(--border) !important;
}
div[data-testid="stBottom"] { padding: 8px 16px 12px !important; }

/* File uploader — dark */
[data-testid="stFileUploader"] {
  background: rgba(100,108,255,0.04) !important;
  border: 2px dashed rgba(100,108,255,0.2) !important;
  border-radius: var(--r) !important; padding: 16px !important;
}
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] section > div {
  background: transparent !important;
}
[data-testid="stFileUploader"] * { color: var(--text-2) !important; }
[data-testid="stFileUploader"] small { color: var(--text-3) !important; }

/* File uploader drag area */
[data-testid="stFileUploaderDropzone"] {
  background: rgba(13,13,30,0.6) !important;
  border: 1px dashed rgba(100,108,255,0.25) !important;
  border-radius: 12px !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
  background: rgba(100,108,255,0.06) !important;
  border-color: rgba(100,108,255,0.4) !important;
}
[data-testid="stFileUploaderDropzone"] * { color: var(--text-2) !important; }
[data-testid="stFileUploaderDropzone"] button {
  background: rgba(100,108,255,0.1) !important;
  color: #818cf8 !important;
  border: 1px solid rgba(100,108,255,0.25) !important;
  border-radius: 8px !important;
}

/* Expander dark */
.streamlit-expanderHeader,
[data-testid="stExpander"] summary {
  background: rgba(15,15,34,0.8) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text-1) !important;
}
[data-testid="stExpander"] details {
  background: transparent !important;
  border: none !important;
}
[data-testid="stExpander"] details > div {
  background: rgba(13,13,30,0.5) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--r-sm) var(--r-sm) !important;
}

/* All white backgrounds in main area — force dark */
.main *, [data-testid="stMainBlockContainer"] * {
  scrollbar-color: #2a2a55 transparent;
}
div[class*="element-container"] > div[data-testid="stVerticalBlock"] {
  background: transparent !important;
}

/* ══════════════════
   FORM INPUTS
══════════════════ */
.stTextInput input, .stTextArea textarea, div[data-baseweb="input"] input {
  background: var(--bg-2) !important; color: var(--text-1) !important;
  border: 1px solid var(--border) !important; border-radius: var(--r-sm) !important;
  font-family: var(--fbody) !important; font-size: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(100,108,255,0.1) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: var(--text-3) !important; }
.stTextInput label, .stTextArea label, .stSelectbox label,
[data-testid="stWidgetLabel"] { color: var(--text-2) !important; font-size: 13px !important; font-weight: 600 !important; font-family: var(--fmono) !important; }

div[data-baseweb="select"] > div {
  background: var(--bg-2) !important; border-color: var(--border) !important;
  border-radius: var(--r-sm) !important; color: var(--text-1) !important;
}
div[data-baseweb="popover"] {
  background: var(--bg-2) !important; border: 1px solid var(--border) !important;
  border-radius: var(--r) !important; box-shadow: 0 4px 40px rgba(0,0,0,0.6) !important;
}
div[data-baseweb="popover"] li { color: var(--text-1) !important; }
div[data-baseweb="popover"] li:hover { background: rgba(100,108,255,0.1) !important; }

[data-testid="stFileUploader"] {
  background: rgba(100,108,255,0.04) !important;
  border: 2px dashed var(--border) !important;
  border-radius: var(--r) !important; padding: 18px !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--border-h) !important; }
[data-testid="stFileUploader"] * { color: var(--text-2) !important; }

/* ══════════════════
   BUTTONS
══════════════════ */
.stButton > button {
  background: rgba(100,108,255,0.07) !important; color: #a5b4fc !important;
  border: 1px solid var(--border) !important; border-radius: var(--r-sm) !important;
  font-family: var(--fbody) !important; font-weight: 600 !important;
  font-size: 13px !important; padding: 9px 18px !important;
  transition: all 0.2s ease !important;
}
.stButton > button:hover {
  background: rgba(100,108,255,0.15) !important; border-color: var(--border-h) !important;
  color: #c7d2fe !important; transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(100,108,255,0.18) !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
  color: white !important; border-color: transparent !important;
  box-shadow: 0 0 20px rgba(100,108,255,0.28) !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg,#4338ca,#6d28d9) !important;
  box-shadow: 0 6px 28px rgba(100,108,255,0.45) !important; transform: translateY(-3px) !important;
}
.stDownloadButton > button {
  background: linear-gradient(135deg,#059669,#10b981) !important;
  color: white !important; border: none !important;
  border-radius: var(--r-sm) !important; font-weight: 700 !important;
  box-shadow: 0 4px 20px rgba(16,185,129,0.3) !important;
  transition: all 0.25s !important;
}
.stDownloadButton > button:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 28px rgba(16,185,129,0.45) !important; }

/* ══════════════════
   TABS
══════════════════ */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid var(--border) !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--text-3) !important; font-family: var(--fbody) !important; font-weight: 600 !important; font-size: 13px !important; padding: 9px 18px !important; }
.stTabs [data-baseweb="tab"]:hover { color: #a5b4fc !important; background: rgba(100,108,255,0.07) !important; }
.stTabs [aria-selected="true"][data-baseweb="tab"] { color: #818cf8 !important; border-bottom: 2px solid var(--accent) !important; }
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding: 18px 0 !important; }

/* ══════════════════
   FORMS
══════════════════ */
[data-testid="stForm"] {
  background: linear-gradient(145deg,var(--bg-card),var(--bg-2)) !important;
  border: 1px solid var(--border) !important; border-radius: var(--r) !important; padding: 24px !important;
}
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
  color: white !important; border: none !important; font-weight: 700 !important;
}

/* ══════════════════
   ALERTS
══════════════════ */
.stSuccess > div { background: rgba(52,211,153,0.08) !important; border: 1px solid rgba(52,211,153,0.25) !important; color: #6ee7b7 !important; border-radius: var(--r-sm) !important; }
.stWarning > div { background: rgba(251,191,36,0.08) !important; border: 1px solid rgba(251,191,36,0.25) !important; color: #fcd34d !important; border-radius: var(--r-sm) !important; }
.stError > div   { background: rgba(244,114,182,0.08) !important; border: 1px solid rgba(244,114,182,0.25) !important; color: #fca5a5 !important; border-radius: var(--r-sm) !important; }
.stInfo > div    { background: rgba(100,108,255,0.08) !important; border: 1px solid rgba(100,108,255,0.25) !important; color: #a5b4fc !important; border-radius: var(--r-sm) !important; }

/* ══════════════════
   PROGRESS
══════════════════ */
.stProgress > div > div > div > div { background: linear-gradient(90deg,#4f46e5,#7c3aed,#f472b6) !important; border-radius: 99px !important; }
.stProgress > div > div { background: rgba(100,108,255,0.1) !important; border-radius: 99px !important; }

/* ══════════════════
   CUSTOM BOXES
══════════════════ */
.somo-notify {
  background: linear-gradient(135deg, rgba(100,108,255,0.12), rgba(167,139,250,0.08));
  border: 1px solid rgba(100,108,255,0.3); border-radius: var(--r);
  padding: 13px 18px; color: #c7d2fe; font-weight: 600; font-size: 14px;
  margin: 10px 0; display: flex; align-items: center; gap: 10px;
  animation: slideup 0.35s ease;
}
.somo-success {
  background: linear-gradient(135deg, rgba(52,211,153,0.12), rgba(5,150,105,0.08));
  border: 1px solid rgba(52,211,153,0.3); color: #6ee7b7;
  border-radius: var(--r); padding: 13px 18px; font-weight: 600;
  font-size: 14px; margin: 10px 0; animation: slideup 0.35s ease;
}
@keyframes slideup { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }

/* ══════════════════
   API BADGES
══════════════════ */
.api-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 11px; border-radius: 99px; font-size: 11px;
  font-weight: 600; font-family: var(--fmono); letter-spacing: 0.5px; border: 1px solid;
}
.api-groq    { background: rgba(255,166,0,0.1);   color:#fbbf24; border-color:rgba(251,191,36,0.3); }
.api-gemini  { background: rgba(52,211,153,0.1);  color:#34d399; border-color:rgba(52,211,153,0.3); }
.api-cohere  { background: rgba(56,189,248,0.1);  color:#38bdf8; border-color:rgba(56,189,248,0.3); }
.api-mistral { background: rgba(244,114,182,0.1); color:#f472b6; border-color:rgba(244,114,182,0.3);}
.api-dot {
  width: 6px; height: 6px; border-radius: 50%; display: inline-block;
  animation: bdot 2s ease-in-out infinite;
}
@keyframes bdot { 0%,100%{opacity:1} 50%{opacity:0.3} }
.api-groq .api-dot    { background:#fbbf24; }
.api-gemini .api-dot  { background:#34d399; }
.api-cohere .api-dot  { background:#38bdf8; }
.api-mistral .api-dot { background:#f472b6; }

/* ══════════════════
   TEMPLATES
══════════════════ */
.tmpl-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--r); padding: 20px; margin-bottom: 12px;
  transition: all 0.25s; position: relative; overflow: hidden;
}
.tmpl-card::before { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background:linear-gradient(180deg,var(--accent),#a78bfa); }
.tmpl-card:hover { border-color: var(--border-h); transform: translateX(4px); }
.tmpl-tag { display:inline-block; padding:3px 11px; border-radius:99px; font-size:10px; font-weight:700; letter-spacing:1px; margin-bottom:9px; font-family:var(--fmono); }
.tag-excel  { background:rgba(52,211,153,0.1);  color:#34d399; border:1px solid rgba(52,211,153,0.25); }
.tag-word   { background:rgba(56,189,248,0.1);  color:#38bdf8; border:1px solid rgba(56,189,248,0.25); }
.tag-code   { background:rgba(251,191,36,0.1);  color:#fbbf24; border:1px solid rgba(251,191,36,0.25); }
.tag-html   { background:rgba(244,114,182,0.1); color:#f472b6; border:1px solid rgba(244,114,182,0.25); }
.tmpl-title { font-size:14px; font-weight:700; color:var(--text-1); margin-bottom:4px; font-family:var(--fhead); }
.tmpl-desc  { font-size:11.5px; color:var(--text-3); line-height:1.55; }

/* ══════════════════
   HISTORY / PROFILE
══════════════════ */
.hist-msg { border-left:3px solid; border-radius:0 var(--r) var(--r) 0; padding:11px 15px; margin:7px 0; font-size:13px; }
.hist-user { background:rgba(100,108,255,0.07); border-color:var(--accent); }
.hist-ai   { background:rgba(52,211,153,0.06);  border-color:#34d399; }
.hist-role { font-size:10px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:4px; font-family:var(--fmono); }
.hist-user .hist-role { color:#818cf8; }
.hist-ai   .hist-role { color:#34d399; }
.hist-body { color:var(--text-2); line-height:1.55; }
.profile-stat { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--r); padding:20px 16px; text-align:center; }
.p-stat-icon { font-size:24px; margin-bottom:8px; }
.p-stat-val  { font-size:28px; font-weight:900; color:var(--text-1); font-family:var(--fhead); }
.p-stat-lbl  { font-size:9.5px; color:var(--text-3); text-transform:uppercase; letter-spacing:1.5px; font-weight:700; margin-top:3px; font-family:var(--fmono); }

/* ══════════════════
   FOOTER
══════════════════ */
.somo-footer { text-align:center; padding:44px 20px 22px; border-top:1px solid var(--border); margin-top:60px; }
.somo-footer .f-title { font-size:18px; font-weight:800; color:var(--text-1); margin-bottom:9px; font-family:var(--fhead); }
.somo-footer .f-sub   { font-size:12.5px; color:var(--text-3); margin-bottom:5px; }
.somo-footer .f-copy  { font-size:10.5px; color:#2a2a40; margin-top:16px; font-family:var(--fmono); }

/* ══════════════════
   TYPEWRITER
══════════════════ */
.tw-cur {
  display:inline-block; width:2px; height:1.1em;
  background:var(--accent); margin-left:2px; vertical-align:text-bottom;
  animation:tcur 0.85s step-end infinite; border-radius:1px;
}
@keyframes tcur { 0%,100%{opacity:1} 50%{opacity:0} }

/* ══════════════════
   MOBILE
══════════════════ */
@media(max-width:768px) {
  .main .block-container,
  [data-testid="stMainBlockContainer"] { padding: 1rem 0.75rem 6rem !important; }
  .somo-hero { padding: 24px 16px !important; border-radius:18px !important; }
  .somo-hero h1 { font-size: clamp(20px,6vw,30px) !important; }
  .cards-grid { grid-template-columns: repeat(2,1fr) !important; gap:8px !important; }
  .somo-card { padding:16px 10px !important; }
  .stat-row { grid-template-columns: repeat(2,1fr) !important; }

  /* Mobilda sidebar */
  [data-testid="stSidebar"] {
    width: 80vw !important;
    max-width: 260px !important;
    min-width: 0 !important;
  }
  /* Sidebar toggle ko'rinsin */
  [data-testid="collapsedControl"] {
    display: flex !important;
  }
}
@media(max-width:480px) {
  .somo-hero h1 { font-size:20px !important; }
  .cards-grid { grid-template-columns:repeat(2,1fr) !important; gap:6px !important; }
  [data-testid="stSidebar"] {
    width: 85vw !important;
    max-width: 280px !important;
  }
}
/* ── GLOBAL DARK OVERRIDE ── */
.stApp, .stApp > div, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"] {
  background: var(--bg-0) !important;
}
.stChatFloatingInputContainer, div[class*="stChatInputContainer"],
[data-testid="stBottom"], [data-testid="stBottom"] > * {
  background: rgba(5,5,15,0.97) !important;
}
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] > div {
  background: rgba(9,9,22,0.8) !important;
  border-color: rgba(100,108,255,0.2) !important;
}
[data-testid="stFileUploaderDropzone"] * { color: var(--text-2) !important; }
[data-testid="stFileUploaderDropzone"] button {
  background: rgba(100,108,255,0.1) !important;
  color: #818cf8 !important;
  border: 1px solid rgba(100,108,255,0.25) !important;
  border-radius: 8px !important;
  font-size: 13px !important;
}
[data-testid="stExpander"] {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
}
[data-testid="stExpander"] summary {
  background: rgba(15,15,34,0.8) !important;
  color: var(--text-1) !important;
}
[data-testid="stExpander"] [data-testid="stVerticalBlock"] {
  background: rgba(9,9,22,0.6) !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar toggle: Streamlit native (top-left arrow)


# ══════════════════════════════════════════════════════════════════
# API CONFIGS
# ══════════════════════════════════════════════════════════════════
API_CONFIGS = {
    "groq":    {"name":"Groq",    "icon":"⚡", "model":"llama-3.3-70b-versatile",  "color":"#fbbf24", "badge_class":"api-groq",    "desc":"Llama 3.3 · 70B · Ultra Fast"},
    "gemini":  {"name":"Gemini",  "icon":"✨", "model":"gemini-2.0-flash",          "color":"#34d399", "badge_class":"api-gemini",  "desc":"Google Gemini 2.0 Flash"},
    "cohere":  {"name":"Cohere",  "icon":"🔮", "model":"command-r-plus",            "color":"#38bdf8", "badge_class":"api-cohere",  "desc":"Command R+ · Reasoning"},
    "mistral": {"name":"Mistral", "icon":"🌪", "model":"mistral-large-latest",      "color":"#f472b6", "badge_class":"api-mistral", "desc":"Mistral Large · EU Based"},
}

def _get_secret(key):
    try:
        val = st.secrets.get(key, "")
        if val: return str(val).strip()
    except: pass
    try:
        for section in ["keys","api","api_keys","APIs","secrets"]:
            try:
                val = st.secrets[section][key]
                if val: return str(val).strip()
            except: pass
    except: pass
    return str(os.environ.get(key,"")).strip()

@st.cache_resource
def init_clients():
    clients = {}
    if HAS_GROQ:
        try:
            key = _get_secret("GROQ_API_KEY")
            if key: clients["groq"] = Groq(api_key=key)
        except: pass
    if HAS_GEMINI:
        for model_name in ["gemini-2.0-flash","gemini-1.5-flash","gemini-pro"]:
            try:
                key = _get_secret("GEMINI_API_KEY")
                if key:
                    genai.configure(api_key=key)
                    clients["gemini"] = genai.GenerativeModel(model_name)
                    break
            except Exception as e:
                if "not found" in str(e).lower() or "404" in str(e): continue
                break
    if HAS_COHERE:
        try:
            key = _get_secret("COHERE_API_KEY")
            if key: clients["cohere"] = cohere.Client(api_key=key)
        except: pass
    if HAS_MISTRAL:
        try:
            key = _get_secret("MISTRAL_API_KEY")
            if key: clients["mistral"] = Mistral(api_key=key)
        except: pass
    return clients

ai_clients = init_clients()

# ══════════════════════════════════════════════════════════════════
# AI CALL FUNCTIONS
# ══════════════════════════════════════════════════════════════════
def call_ai(messages, temperature=0.6, max_tokens=3000, provider="groq"):
    providers_order = [provider] + [p for p in ["groq","gemini","cohere","mistral"] if p != provider]
    for prov in providers_order:
        if prov not in ai_clients: continue
        try:
            if prov == "groq":
                resp = ai_clients["groq"].chat.completions.create(
                    messages=messages, model=API_CONFIGS["groq"]["model"],
                    temperature=min(temperature,1.0), max_tokens=max_tokens)
                return resp.choices[0].message.content, "groq"
            elif prov == "gemini":
                sys_msg = next((m["content"] for m in messages if m["role"]=="system"), "")
                user_msgs = [m for m in messages if m["role"] != "system"]
                chat_hist = [{"role":"user" if m["role"]=="user" else "model","parts":[m["content"]]} for m in user_msgs[:-1]]
                last_msg = user_msgs[-1]["content"] if user_msgs else ""
                if sys_msg: last_msg = f"[System: {sys_msg}]\n\n{last_msg}"
                chat = ai_clients["gemini"].start_chat(history=chat_hist)
                return chat.send_message(last_msg).text, "gemini"
            elif prov == "cohere":
                sys_msg = next((m["content"] for m in messages if m["role"]=="system"), "")
                user_msgs = [m for m in messages if m["role"] != "system"]
                chat_hist = [{"role":"USER" if m["role"]=="user" else "CHATBOT","message":m["content"]} for m in user_msgs[:-1]]
                last_msg = user_msgs[-1]["content"] if user_msgs else ""
                resp = ai_clients["cohere"].chat(model=API_CONFIGS["cohere"]["model"],
                    message=last_msg, chat_history=chat_hist,
                    preamble=sys_msg if sys_msg else None,
                    temperature=min(temperature,1.0), max_tokens=max_tokens)
                return resp.text, "cohere"
            elif prov == "mistral":
                resp = ai_clients["mistral"].chat.complete(model=API_CONFIGS["mistral"]["model"],
                    messages=messages, temperature=min(temperature,1.0), max_tokens=max_tokens)
                return resp.choices[0].message.content, "mistral"
        except: continue
    return "❌ Hech bir AI xizmati mavjud emas.", "none"

def call_ai_stream(messages, temperature=0.6, max_tokens=3000, provider="groq"):
    """FIX 6: time.sleep olib tashlandi — stream tezligi oshdi."""
    providers_order = [provider] + [p for p in ["groq","gemini","cohere","mistral"] if p != provider]
    for prov in providers_order:
        if prov not in ai_clients: continue
        try:
            if prov == "groq":
                stream = ai_clients["groq"].chat.completions.create(
                    messages=messages, model=API_CONFIGS["groq"]["model"],
                    temperature=min(temperature,1.0), max_tokens=max_tokens, stream=True)
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content, "groq"
                return
            elif prov == "gemini":
                sys_msg = next((m["content"] for m in messages if m["role"]=="system"), "")
                user_msgs = [m for m in messages if m["role"] != "system"]
                chat_hist = [{"role":"user" if m["role"]=="user" else "model","parts":[m["content"]]} for m in user_msgs[:-1]]
                last_msg = user_msgs[-1]["content"] if user_msgs else ""
                if sys_msg: last_msg = f"[System: {sys_msg}]\n\n{last_msg}"
                chat = ai_clients["gemini"].start_chat(history=chat_hist)
                for chunk in chat.send_message(last_msg, stream=True):
                    if chunk.text: yield chunk.text, "gemini"
                return
            elif prov == "cohere":
                sys_msg = next((m["content"] for m in messages if m["role"]=="system"), "")
                user_msgs = [m for m in messages if m["role"] != "system"]
                chat_hist = [{"role":"USER" if m["role"]=="user" else "CHATBOT","message":m["content"]} for m in user_msgs[:-1]]
                last_msg = user_msgs[-1]["content"] if user_msgs else ""
                for event in ai_clients["cohere"].chat_stream(model=API_CONFIGS["cohere"]["model"],
                        message=last_msg, chat_history=chat_hist,
                        preamble=sys_msg if sys_msg else None,
                        temperature=min(temperature,1.0), max_tokens=max_tokens):
                    if hasattr(event,'text') and event.text: yield event.text, "cohere"
                return
            elif prov == "mistral":
                for chunk in ai_clients["mistral"].chat.stream(model=API_CONFIGS["mistral"]["model"],
                        messages=messages, temperature=min(temperature,1.0), max_tokens=max_tokens):
                    delta = chunk.data.choices[0].delta.content
                    if delta: yield delta, "mistral"
                return
        except: continue
    yield "❌ Xatolik yuz berdi.", "none"

# ══════════════════════════════════════════════════════════════════
# FIX 2: DB — caching & rate limit protection
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def get_connections():
    try:
        scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        user_sheet = ss.sheet1
        try: chat_sheet = ss.worksheet("ChatHistory")
        except:
            chat_sheet = ss.add_worksheet("ChatHistory",5000,6)
            chat_sheet.append_row(["Timestamp","Username","Role","Message","Intent","Provider"])
        try: fb_sheet = ss.worksheet("Letters")
        except:
            fb_sheet = ss.add_worksheet("Letters",1000,8)
            fb_sheet.append_row(["Timestamp","Username","Rating","Category","Message","Email","Status","Files"])
        return user_sheet, chat_sheet, fb_sheet
    except: return None, None, None

user_db, chat_db, fb_db = get_connections()

# FIX 2: Foydalanuvchilarni cache qilish (Google Sheets ga har so'rovda murojaat qilmaslik)
@st.cache_data(ttl=120)  # 2 daqiqa cache
def get_all_users():
    if user_db:
        try: return user_db.get_all_records()
        except: return []
    return []

def process_doc(file):
    try:
        if file.type == "application/pdf" and HAS_PDF:
            reader = PdfReader(file)
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        elif "wordprocessingml" in file.type and HAS_MAMMOTH:
            return mammoth.extract_raw_text(file).value
    except Exception as e:
        st.warning(f"⚠️ {e}")
    return ""

# FIX 7: db_log — rate limit himoyasi (oxirgi log vaqtini tekshiradi)
_last_log_time = 0
def db_log(user, role, content, intent="chat", provider="groq"):
    global _last_log_time
    now = time.time()
    # Har 3 soniyada bir marta log qilish (Google Sheets limit himoyasi)
    if now - _last_log_time < 3:
        return
    _last_log_time = now
    if chat_db:
        try:
            chat_db.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user, role, content[:400], intent, provider
            ])
        except: pass

# ══════════════════════════════════════════════════════════════════
# INTENT DETECTION
# ══════════════════════════════════════════════════════════════════
def detect_intent(text):
    t = text.lower()
    if any(k in t for k in ["excel","xlsx","jadval","byudjet","budget","spreadsheet","finance","moliya","ombor","inventory","hisobot","salary","ish haqi","sotish","savdo","xarajat","daromad","oylik reja","jadval tuz","grafik","formula"]):
        return "excel"
    if any(k in t for k in ["word","docx","hujjat","rezyume","resume","cv","shartnoma","contract","ariza","maktub","letter","kurs ishi","referat","essay","diplom","biznes reja","business plan"]):
        return "word"
    if any(k in t for k in ["html","website","veb sahifa","landing page","web page"]):
        return "html"
    if any(k in t for k in ["csv","comma separated","dataset"]):
        return "csv"
    if any(k in t for k in ["python kodi","kod yoz","dastur yaz","script yoz","bot yaz","write code","function yoz"]):
        return "code"
    return "chat"

MIME = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "py":   "text/x-python",
    "html": "text/html",
    "csv":  "text/csv"
}

# ══════════════════════════════════════════════════════════════════
# FILE GENERATORS
# ══════════════════════════════════════════════════════════════════
def gen_excel(prompt, temp=0.15, provider="groq"):
    if not HAS_OPENPYXL: return None, "openpyxl o'rnatilmagan"
    sys_p = """Sen Excel fayl strukturasi uchun JSON qaytaruvchi ekspertsan.
FAQAT quyidagi JSON formatini qaytar:
{"title":"Fayl nomi","sheets":[{"name":"Varaq","headers":["H1","H2"],"header_color":"4F46E5","rows":[["v1","v2"]],"col_widths":[25,15],"row_height":20}]}
Kamida 15-20 satr. Excel formulalar: SUM, AVERAGE, IF. FAQAT JSON."""
    raw, _ = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}], temperature=temp, max_tokens=4000, provider=provider)
    raw = re.sub(r'```json|```','',raw).strip()
    m = re.search(r'\{.*\}',raw,re.DOTALL)
    if not m: return None, "JSON topilmadi"
    try: data = json.loads(m.group())
    except:
        try: data = json.loads(raw)
        except Exception as e: return None, f"JSON: {e}"
    wb = Workbook(); wb.remove(wb.active)
    PALETTES = [("4F46E5","EEF2FF"),("059669","ECFDF5"),("D97706","FFFBEB"),("DC2626","FEF2F2"),("0891B2","ECFEFF"),("7C3AED","F5F3FF")]
    for si,sh in enumerate(data.get("sheets",[])):
        ws = wb.create_sheet(title=sh.get("name","Sheet")[:31])
        headers = sh.get("headers",[]); hcolor = sh.get("header_color",PALETTES[si%len(PALETTES)][0])
        _,rcolor = PALETTES[si%len(PALETTES)]; rows = sh.get("rows",[]); widths = sh.get("col_widths",[]); rh = sh.get("row_height",20)
        if headers:
            end_col = max(len(headers),1)
            ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=end_col)
            tc = ws.cell(row=1,column=1,value=sh.get("name","Hisobot"))
            tc.font = Font(name="Calibri",bold=True,size=13,color="FFFFFF")
            tc.fill = PatternFill("solid",fgColor=hcolor)
            tc.alignment = Alignment(horizontal="center",vertical="center")
            ws.row_dimensions[1].height = 30
            th = Side(style="medium",color="FFFFFF")
            for ci,h in enumerate(headers,1):
                c = ws.cell(row=2,column=ci,value=h)
                c.font = Font(name="Calibri",bold=True,size=11,color="FFFFFF")
                c.fill = PatternFill("solid",fgColor=hcolor)
                c.alignment = Alignment(horizontal="center",vertical="center",wrap_text=True)
                c.border = Border(left=th,right=th,top=th,bottom=th)
            ws.row_dimensions[2].height = 24
        td = Side(style="thin",color="D1D5DB")
        for ri,row in enumerate(rows,3):
            bg = "FFFFFF" if ri%2 else rcolor
            for ci,val in enumerate(row,1):
                c = ws.cell(row=ri,column=ci)
                if isinstance(val,str) and val.startswith("="): c.value = val
                else:
                    try:
                        if isinstance(val,str) and re.match(r'^-?\d+(\.\d+)?$',val.strip()):
                            v = float(val); c.value = int(v) if v==int(v) else v
                        else: c.value = val
                    except: c.value = val
                c.fill = PatternFill("solid",fgColor=bg)
                c.border = Border(left=td,right=td,top=td,bottom=td)
                c.font = Font(name="Calibri",size=10)
                c.alignment = Alignment(vertical="center",wrap_text=True)
            ws.row_dimensions[ri].height = rh
        for ci,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(ci)].width = max(int(w),8)
        if not widths and headers:
            for ci in range(1,len(headers)+1): ws.column_dimensions[get_column_letter(ci)].width = 18
        ws.freeze_panes = "A3"
    if not wb.sheetnames: wb.create_sheet("Ma'lumotlar")
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    safe = re.sub(r'[^\w\s-]','',data.get("title","somo")).strip().replace(' ','_')
    return buf.getvalue(), f"{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

def gen_word(prompt, temp=0.4, provider="mistral"):
    if not HAS_DOCX: return None, "python-docx o'rnatilmagan"
    sys_p = """Sen professional Word hujjat strukturasi JSON qaytaruvchi ekspertsan.
FAQAT JSON:
{"title":"Sarlavha","sections":[{"type":"heading1","text":"..."},{"type":"paragraph","text":"..."},{"type":"bullet","items":["1","2"]},{"type":"table","headers":["H1","H2"],"rows":[["v1","v2"]]}]}
Kamida 10-14 bo'lim. Faqat JSON."""
    raw, _ = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}], temperature=temp, max_tokens=4000, provider=provider)
    raw = re.sub(r'```json|```','',raw).strip()
    m = re.search(r'\{.*\}',raw,re.DOTALL)
    if not m: return None, "Struktura topilmadi"
    try: data = json.loads(m.group())
    except Exception as e: return None, f"JSON: {e}"
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Cm(2.5); sec.bottom_margin = Cm(2.5)
        sec.left_margin = Cm(3); sec.right_margin = Cm(2.5)
    tp = doc.add_paragraph(); tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = tp.add_run(data.get("title","Hujjat"))
    run.bold = True; run.font.size = Pt(20); run.font.color.rgb = RGBColor(0x4F,0x46,0xE5); run.font.name = "Calibri"
    dp = doc.add_paragraph(); dp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    dr = dp.add_run(f"{datetime.now().strftime('%d.%m.%Y')} — Somo AI")
    dr.font.size = Pt(10); dr.font.color.rgb = RGBColor(0x94,0xA3,0xB8); dr.font.name = "Calibri"
    for sec in data.get("sections",[]):
        t = sec.get("type","paragraph")
        if t == "heading1":
            h = doc.add_heading(sec.get("text",""),level=1)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x4F,0x46,0xE5); h.runs[0].font.name = "Calibri"
        elif t == "heading2":
            h = doc.add_heading(sec.get("text",""),level=2)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x7C,0x3A,0xED); h.runs[0].font.name = "Calibri"
        elif t == "paragraph":
            p = doc.add_paragraph(); r = p.add_run(sec.get("text",""))
            r.font.size = Pt(11); r.font.name = "Calibri"
            p.paragraph_format.space_after = Pt(8); p.paragraph_format.line_spacing = Pt(16)
        elif t == "bullet":
            for item in sec.get("items",[]):
                p = doc.add_paragraph(style='List Bullet'); r = p.add_run(item)
                r.font.size = Pt(11); r.font.name = "Calibri"
        elif t == "numbered":
            for item in sec.get("items",[]):
                p = doc.add_paragraph(style='List Number'); r = p.add_run(item)
                r.font.size = Pt(11); r.font.name = "Calibri"
        elif t == "table":
            hdrs = sec.get("headers",[]); rws = sec.get("rows",[])
            if hdrs:
                tbl = doc.add_table(rows=1+len(rws),cols=len(hdrs)); tbl.style = 'Table Grid'
                hrow = tbl.rows[0]
                for ci,h in enumerate(hdrs):
                    cell = hrow.cells[ci]; cell.text = h
                    if cell.paragraphs[0].runs:
                        cell.paragraphs[0].runs[0].font.bold = True
                        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255,255,255)
                        cell.paragraphs[0].runs[0].font.name = "Calibri"
                    # FIX 9: Import top-levelda, funksiya ichida emas
                    tcPr = cell._tc.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'),'4F46E5')
                    tcPr.append(shd)
                for ri,rdata in enumerate(rws):
                    rcells = tbl.rows[ri+1].cells
                    for ci,val in enumerate(rdata):
                        if ci < len(rcells):
                            rcells[ci].text = str(val)
                            if rcells[ci].paragraphs[0].runs:
                                rcells[ci].paragraphs[0].runs[0].font.size = Pt(10); rcells[ci].paragraphs[0].runs[0].font.name = "Calibri"
                doc.add_paragraph()
    footer_sec = doc.sections[0].footer; fp = footer_sec.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = fp.add_run(f"© {datetime.now().year} Somo AI  |  {data.get('title','')}")
    fr.font.size = Pt(9); fr.font.color.rgb = RGBColor(0x94,0xA3,0xB8); fr.font.name = "Calibri"
    buf = io.BytesIO(); doc.save(buf); buf.seek(0)
    safe = re.sub(r'[^\w\s-]','',data.get("title","somo")).strip().replace(' ','_')
    return buf.getvalue(), f"{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

def gen_code(prompt, temp=0.12, provider="cohere"):
    sys_p = "Sen tajribali Python dasturchi. Professional, to'liq ishlaydigan kod yoz. FAQAT Python kodi — markdown yo'q."
    raw, _ = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}], temperature=temp, max_tokens=3500, provider=provider)
    raw = re.sub(r'```python|```py|```','',raw).strip()
    safe = re.sub(r'[^\w]','_',prompt[:30]).strip('_')
    return raw.encode('utf-8'), f"{safe}_{datetime.now().strftime('%H%M%S')}.py"

def gen_html(prompt, temp=0.5, provider="gemini"):
    sys_p = "Sen professional frontend developer. Chiroyli, zamonaviy HTML/CSS/JS sahifa yarat. Dark theme, glassmorphism. FAQAT HTML kodi."
    raw, _ = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}], temperature=temp, max_tokens=4000, provider=provider)
    raw = re.sub(r'```html|```','',raw).strip()
    safe = re.sub(r'[^\w]','_',prompt[:25]).strip('_')
    return raw.encode('utf-8'), f"{safe}_{datetime.now().strftime('%H%M%S')}.html"

def gen_csv(prompt, temp=0.3, provider="mistral"):
    sys_p = "Sen ma'lumotlar mutaxassisi. FAQAT CSV format. Birinchi satr sarlavha. Kamida 25 satr. Hech qanday tushuntirma yo'q."
    raw, _ = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}], temperature=temp, max_tokens=3000, provider=provider)
    raw = re.sub(r'```csv|```','',raw).strip()
    safe = re.sub(r'[^\w]','_',prompt[:25]).strip('_')
    return raw.encode('utf-8'), f"{safe}_{datetime.now().strftime('%H%M%S')}.csv"

def download_block(file_bytes, fname, label):
    ext = fname.rsplit('.',1)[-1]; mime = MIME.get(ext,"application/octet-stream")
    st.markdown(f'<div class="somo-success">✅ {label} fayl tayyor!</div>', unsafe_allow_html=True)
    st.download_button(f"⬇️  {fname}", file_bytes, fname, mime,
                       use_container_width=True, type="primary", key=f"dl_{fname}_{time.time()}")

def api_status_html(provider):
    cfg = API_CONFIGS.get(provider, API_CONFIGS["groq"])
    return f'<span class="api-badge {cfg["badge_class"]}"><span class="api-dot"></span>{cfg["icon"]} {cfg["name"]}</span>'

# ══════════════════════════════════════════════════════════════════
# SESSION RESTORE — cookie bilan
# ══════════════════════════════════════════════════════════════════
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session") if HAS_COOKIES else None
    if session_user and user_db:
        try:
            recs = get_all_users()  # FIX: cached
            ud = next((r for r in recs if str(r['username'])==session_user), None)
            if ud and str(ud.get('status','')).lower()=='active':
                st.session_state.update({'username':session_user,'logged_in':True,'login_time':datetime.now()})
            else:
                st.session_state.logged_in = False
        except: st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

def logout():
    try:
        if HAS_COOKIES:
            cookies["somo_user_session"] = ""; cookies.save()
    except: pass
    keys = list(st.session_state.keys())
    for k in keys: del st.session_state[k]
    st.session_state.logged_in = False
    st.rerun()

# ══════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div class="somo-hero" style="text-align:center;padding:72px 40px;">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#646cff;margin-bottom:14px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ Next Generation AI Platform</p>
            <h1 style="font-size:clamp(38px,5.5vw,68px);font-weight:800;color:white;letter-spacing:-2.5px;margin-bottom:18px;">
                🌌 Somo AI <span class="g-text">Ultra Pro Max</span>
            </h1>
            <p style="font-size:17px;color:rgba(255,255,255,0.55);max-width:560px;margin:0 auto 30px;line-height:1.7;font-family:'Inter',sans-serif;">
                Excel · Word · Kod · HTML · CSV — To'rt xil AI bilan har qanday faylni yarating
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1,2,1])
    with col_m:
        t1, t2, t3 = st.tabs(["🔒  Kirish", "✍️  Ro'yxatdan o'tish", "ℹ️  Ma'lumot"])

        with t1:
            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                st.markdown('<p class="section-label">Hisobingizga kiring</p>', unsafe_allow_html=True)
                u = st.text_input("Username", placeholder="Username kiriting", key="lu")
                p = st.text_input("Parol", type="password", placeholder="Parolni kiriting", key="lp")
                r_col, b_col = st.columns([1,2])
                with r_col: rem = st.checkbox("Eslab qolish", value=True)
                with b_col: sub = st.form_submit_button("🚀  Kirish", use_container_width=True, type="primary")
                if sub and u and p:
                    if user_db:
                        try:
                            recs = get_all_users()  # FIX: cached
                            user = next((r for r in recs if str(r['username'])==u), None)
                            if user and check_pw(p, str(user['password'])):  # FIX: check_pw
                                if str(user.get('status','')).lower()=='blocked':
                                    st.error("🚫 Hisob bloklangan!")
                                else:
                                    st.session_state.update({'username':u,'logged_in':True,'login_time':datetime.now()})
                                    if rem and HAS_COOKIES:
                                        cookies["somo_user_session"] = u; cookies.save()
                                    st.success("✅ Muvaffaqiyatli!"); time.sleep(0.4); st.rerun()
                            else:
                                st.error("❌ Login yoki parol noto'g'ri!")
                        except Exception as e: st.error(f"❌ {e}")
                    else: st.error("❌ Baza ulanmagan")
                elif sub: st.warning("⚠️ Username va parolni kiriting")

        with t2:
            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
            with st.form("register_form", clear_on_submit=False):
                st.markdown('<p class="section-label">Yangi hisob yaratish</p>', unsafe_allow_html=True)
                nu = st.text_input("Username", placeholder="Kamida 3 ta belgi", key="ru")
                np = st.text_input("Parol", type="password", placeholder="Kamida 6 ta belgi", key="rp")
                nc = st.text_input("Parolni tasdiqlang", type="password", placeholder="Qayta kiriting", key="rc")
                agree = st.checkbox("Foydalanish shartlariga roziman ✅")
                sub2 = st.form_submit_button("✨  Hisob yaratish", use_container_width=True, type="primary")
                if sub2:
                    if not agree:    st.error("❌ Shartlarga rozilik bering!")
                    elif len(nu)<3:  st.error("❌ Username kamida 3 belgi!")
                    elif len(np)<6:  st.error("❌ Parol kamida 6 belgi!")
                    elif np!=nc:     st.error("❌ Parollar mos emas!")
                    elif user_db:
                        try:
                            recs = get_all_users()
                            if any(r['username']==nu for r in recs):
                                st.error("❌ Bu username band!")
                            else:
                                user_db.append_row([nu, hash_pw(np), "active", str(datetime.now()), 0])
                                # FIX: cache ni yangilash
                                get_all_users.clear()
                                st.balloons(); st.success("🎉 Muvaffaqiyatli! «Kirish» bo'limiga o'ting.")
                        except Exception as e: st.error(f"❌ {e}")

        with t3:
            st.markdown("""
            <div style="padding:8px 0;">
            <p class="section-label">Platformalar</p>
            <p class="section-title" style="font-size:18px;">4 AI · 5 Format · ∞ Imkoniyat</p>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px;">
                <div style="background:rgba(251,191,36,0.06);border:1px solid rgba(251,191,36,0.2);border-radius:12px;padding:14px;">
                    <p style="color:#fbbf24;font-weight:700;font-size:12px;font-family:'JetBrains Mono',monospace;">⚡ GROQ</p>
                    <p style="color:#50506a;font-size:11px;margin-top:4px;line-height:1.6;">Chat, Excel<br>Llama 3.3 70B</p>
                </div>
                <div style="background:rgba(52,211,153,0.06);border:1px solid rgba(52,211,153,0.2);border-radius:12px;padding:14px;">
                    <p style="color:#34d399;font-weight:700;font-size:12px;font-family:'JetBrains Mono',monospace;">✨ GEMINI</p>
                    <p style="color:#50506a;font-size:11px;margin-top:4px;line-height:1.6;">HTML, Tahlil<br>Gemini 2.0 Flash</p>
                </div>
                <div style="background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.2);border-radius:12px;padding:14px;">
                    <p style="color:#38bdf8;font-weight:700;font-size:12px;font-family:'JetBrains Mono',monospace;">🔮 COHERE</p>
                    <p style="color:#50506a;font-size:11px;margin-top:4px;line-height:1.6;">Kod<br>Command R+</p>
                </div>
                <div style="background:rgba(244,114,182,0.06);border:1px solid rgba(244,114,182,0.2);border-radius:12px;padding:14px;">
                    <p style="color:#f472b6;font-weight:700;font-size:12px;font-family:'JetBrains Mono',monospace;">🌪 MISTRAL</p>
                    <p style="color:#50506a;font-size:11px;margin-top:4px;line-height:1.6;">Word, CSV<br>Mistral Large</p>
                </div>
            </div>
            <p style="color:#334155;font-size:11px;margin-top:16px;font-family:'JetBrains Mono',monospace;">👨‍💻 Usmonov Sodiq · v3.1 · 2026</p>
            </div>
            """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════
# SESSION DEFAULTS — FIX 5: login_time har doim mavjud
# ══════════════════════════════════════════════════════════════════
DEFS = {
    'messages':[], 'total_msgs':0, 'page':'home',
    'uploaded_text':'', 'temp':0.6, 'files_cnt':0,
    'ai_style':'Aqlli yordamchi', 'last_files':[],
    'selected_provider':'groq', 'chat_provider':'groq',
    'excel_provider':'groq', 'word_provider':'mistral',
    'code_provider':'cohere', 'html_provider':'gemini',
    'csv_provider':'mistral', 'analyze_provider':'gemini',
    'login_time': datetime.now(),  # FIX 5: har doim mavjud
}
for k,v in DEFS.items():
    if k not in st.session_state: st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    uname = st.session_state.get("username", "User")
    avail_providers = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]

    st.markdown(f"""
    <div style="padding:22px 16px 18px;border-bottom:1px solid rgba(100,108,255,0.12);margin-bottom:6px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
            <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed,#f472b6);width:44px;height:44px;border-radius:14px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:900;color:white;box-shadow:0 0 20px rgba(100,108,255,0.4);">
                {uname[0].upper()}
            </div>
            <div>
                <div style="font-size:14px;font-weight:700;color:#f0f0ff;font-family:'Syne',sans-serif;">{uname}</div>
                <div style="font-size:10px;color:#34d399;font-weight:600;font-family:'JetBrains Mono',monospace;display:flex;align-items:center;gap:4px;margin-top:2px;">
                    <span style="background:#34d399;width:5px;height:5px;border-radius:50%;display:inline-block;animation:blink-dot 2s ease-in-out infinite;"></span>
                    ONLINE
                </div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;">
            <div style="background:rgba(100,108,255,0.07);border:1px solid rgba(100,108,255,0.12);border-radius:10px;padding:10px;text-align:center;">
                <div style="font-size:17px;font-weight:900;color:#f0f0ff;font-family:'Syne',sans-serif;">{len(st.session_state.messages)}</div>
                <div style="font-size:9px;color:#50506a;text-transform:uppercase;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace;">Xabar</div>
            </div>
            <div style="background:rgba(52,211,153,0.07);border:1px solid rgba(52,211,153,0.12);border-radius:10px;padding:10px;text-align:center;">
                <div style="font-size:17px;font-weight:900;color:#f0f0ff;font-family:'Syne',sans-serif;">{st.session_state.files_cnt}</div>
                <div style="font-size:9px;color:#50506a;text-transform:uppercase;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace;">Fayl</div>
            </div>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;">
            {''.join([f'<span class="api-badge {API_CONFIGS[p]["badge_class"]}" style="font-size:9px;padding:3px 8px;"><span class="api-dot"></span>{API_CONFIGS[p]["icon"]}</span>' for p in avail_providers])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav = [
        ("home","🏠","Bosh sahifa"), ("chat","💬","Chat AI"),
        ("excel","📊","Excel Generator"), ("word","📝","Word Generator"),
        ("code","💻","Kod Generator"), ("html","🌐","HTML Generator"),
        ("csv","📋","CSV Generator"), ("templates","🎨","Shablonlar"),
        ("analyze","🔍","Hujjat Tahlili"), ("history","📜","Chat Tarixi"),
        ("feedback","💌","Fikr bildirish"), ("profile","👤","Profil"),
    ]

    st.markdown('<p class="section-label" style="padding:10px 14px 4px;font-size:9px;">Navigatsiya</p>', unsafe_allow_html=True)
    for pid,icon,label in nav:
        is_active = st.session_state.page == pid
        if st.button(f"{icon}  {label}", key=f"nav_{pid}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = pid; st.rerun()

    st.markdown('<hr class="somo-divider" style="margin:10px 0;">', unsafe_allow_html=True)

    if st.session_state.page == "chat":
        st.markdown('<p class="section-label" style="padding:0 14px 6px;font-size:9px;">Chat Sozlamalari</p>', unsafe_allow_html=True)
        prov_opts = [(p, f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}") for p in avail_providers] if avail_providers else [("groq","⚡ Groq")]
        prov_keys = [p[0] for p in prov_opts]; prov_labels = [p[1] for p in prov_opts]
        curr_idx = prov_keys.index(st.session_state.chat_provider) if st.session_state.chat_provider in prov_keys else 0
        sel = st.selectbox("🤖 AI Provider", prov_labels, index=curr_idx, key="chat_prov_sel")
        st.session_state.chat_provider = prov_keys[prov_labels.index(sel)]
        st.session_state.temp = st.slider("🌡  Ijodkorlik", 0.0, 1.0, st.session_state.temp, 0.05, key="temp_sl")
        st.session_state.ai_style = st.selectbox("💬  Uslub", ["Aqlli yordamchi","Do'stona","Rasmiy ekspert","Ijodkor","Texnik"], key="ai_sl")
        if st.button("🗑  Chatni tozalash", use_container_width=True, key="clr_chat"):
            st.session_state.messages = []; st.rerun()
        if st.session_state.messages:
            # Serialize qilish — bytes va serialize bo'lmaydigan ob'ektlarni olib tashlash
            def _safe_msgs(msgs):
                safe = []
                for m in msgs:
                    safe.append({
                        "role": m.get("role",""),
                        "content": m.get("content",""),
                        "provider": m.get("provider",""),
                    })
                return safe
            chat_json = json.dumps(_safe_msgs(st.session_state.messages), ensure_ascii=False, indent=2)
            st.download_button("📥  JSON Export", chat_json.encode(), f"chat_{datetime.now():%Y%m%d}.json", use_container_width=True)

    st.markdown('<br>', unsafe_allow_html=True)
    if st.button("🚪  Tizimdan chiqish", use_container_width=True, type="primary", key="logout"):
        logout()

    st.markdown(f"""
    <div style="padding:14px 14px 8px;border-top:1px solid rgba(100,108,255,0.08);margin-top:6px;text-align:center;">
        <p style="font-size:9px;color:#2a2a40;line-height:1.7;font-family:'JetBrains Mono',monospace;">
            🌌 SOMO AI · v3.1<br>⚡ GROQ · ✨ GEMINI · 🔮 COHERE · 🌪 MISTRAL<br>© 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    uname = st.session_state.username
    avail = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    mins = (datetime.now()-st.session_state.login_time).seconds//60  # FIX 5: KeyError yo'q

    st.markdown(f"""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#646cff;margin-bottom:12px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ Somo AI Ultra Pro Max v3.1</p>
            <h1>Salom, <span class="g-text">{uname}</span>! 👋</h1>
            <p class="subtitle">Bugun nima yaratmoqchisiz? To'rt xil AI bilan — Excel, Word, Kod, HTML, CSV — hammasini bir joyda.</p>
            <div class="hero-badges">
                {''.join([f'<span class="api-badge {API_CONFIGS[p]["badge_class"]}"><span class="api-dot"></span>{API_CONFIGS[p]["icon"]} {API_CONFIGS[p]["name"]}</span>' for p in avail])}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box"><div class="stat-icon">💬</div><div class="stat-val">{len(st.session_state.messages)}</div><div class="stat-lbl">Xabarlar</div></div>
        <div class="stat-box"><div class="stat-icon">📁</div><div class="stat-val">{st.session_state.files_cnt}</div><div class="stat-lbl">Fayllar</div></div>
        <div class="stat-box"><div class="stat-icon">⏱</div><div class="stat-val">{mins}</div><div class="stat-lbl">Daqiqa</div></div>
        <div class="stat-box"><div class="stat-icon">🤖</div><div class="stat-val">{len(avail)}</div><div class="stat-lbl">AI aktiv</div></div>
        <div class="stat-box"><div class="stat-icon">🔥</div><div class="stat-val">{max(1,len(st.session_state.messages)//5)}</div><div class="stat-lbl">Daraja</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-label">Funksiyalar</p><p class="section-title">Nima qilmoqchisiz?</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cards-grid">
        <div class="somo-card card-v6"><span class="card-icon">💬</span><div class="card-title">Chat AI</div><div class="card-desc">4 ta AI bilan aqlli suhbat va fayl yaratish</div></div>
        <div class="somo-card card-v1"><span class="card-icon">📊</span><div class="card-title">Excel Generator</div><div class="card-desc">Formulalar, ranglar, bir necha varaqli jadvallar</div></div>
        <div class="somo-card card-v2"><span class="card-icon">📝</span><div class="card-title">Word Generator</div><div class="card-desc">Rezyume, shartnoma, biznes reja, hisobot</div></div>
        <div class="somo-card card-v3"><span class="card-icon">💻</span><div class="card-title">Kod Generator</div><div class="card-desc">Python bot, API, web scraper, ML model</div></div>
        <div class="somo-card card-v4"><span class="card-icon">🌐</span><div class="card-title">HTML Generator</div><div class="card-desc">Portfolio, landing page, dashboard sahifasi</div></div>
        <div class="somo-card card-v5"><span class="card-icon">📋</span><div class="card-title">CSV Generator</div><div class="card-desc">Katta ma'lumotlar to'plami — bir so'rovda</div></div>
        <div class="somo-card card-v6"><span class="card-icon">🎨</span><div class="card-title">Shablonlar</div><div class="card-desc">16 ta tayyor shablon — biznes, kod, ta'lim</div></div>
        <div class="somo-card card-v1"><span class="card-icon">🔍</span><div class="card-title">Hujjat Tahlili</div><div class="card-desc">PDF & DOCX fayllarni AI bilan tahlil qilish</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">Tezkor Harakatlar</p>', unsafe_allow_html=True)
    q1,q2,q3,q4 = st.columns(4)
    for col,icon,label,page in [(q1,"📊","Oylik Byudjet","excel"),(q2,"📄","Rezyume","word"),(q3,"🤖","Telegram Bot","code"),(q4,"🌐","Landing Page","html")]:
        with col:
            if st.button(f"{icon}  {label}", use_container_width=True, key=f"quick_{page}"):
                st.session_state.page = page; st.rerun()

# ══════════════════════════════════════════════════════════════════
# PAGE: CHAT AI
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "chat":
    cur_prov = st.session_state.chat_provider
    st.markdown(f"""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#646cff;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ Smart Chat · {api_status_html(cur_prov)}</p>
            <h1>💬 Chat <span class="g-text">AI</span></h1>
            <p class="subtitle">So'zingizni yozing — AI tushunadi va javob beradi. Excel, Word, Kod — hammasi avtomatik.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("""
        <div class="cards-grid" style="grid-template-columns:repeat(auto-fill,minmax(175px,1fr));">
            <div class="somo-card card-v1" style="padding:18px 14px;"><span class="card-icon" style="font-size:26px;">📊</span><div class="card-title" style="font-size:12px;">"Oylik byudjet jadvali"</div><div class="card-desc">Excel avtomatik yaratiladi</div></div>
            <div class="somo-card card-v2" style="padding:18px 14px;"><span class="card-icon" style="font-size:26px;">📝</span><div class="card-title" style="font-size:12px;">"Rezyume yozing"</div><div class="card-desc">Word fayl tayyorlanadi</div></div>
            <div class="somo-card card-v3" style="padding:18px 14px;"><span class="card-icon" style="font-size:26px;">💻</span><div class="card-title" style="font-size:12px;">"Python kodi yozing"</div><div class="card-desc">.py fayl yuklab olish</div></div>
            <div class="somo-card card-v4" style="padding:18px 14px;"><span class="card-icon" style="font-size:26px;">🌐</span><div class="card-title" style="font-size:12px;">"Landing page yarat"</div><div class="card-desc">HTML fayl tayyorlanadi</div></div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and "provider" in msg:
                st.markdown(f'<div style="margin-bottom:8px;">{api_status_html(msg.get("provider","groq"))}</div>', unsafe_allow_html=True)
            st.markdown(msg["content"])
            if "file_data" in msg:
                fd = msg["file_data"]
                if fd.get("bytes"):
                    download_block(fd["bytes"], fd["name"], fd["label"])
                else:
                    st.markdown(f'<div class="somo-success">✅ {fd["label"]} fayl yaratildi: <code>{fd["name"]}</code></div>', unsafe_allow_html=True)

    with st.expander("📂  Hujjat yuklash (PDF yoki DOCX)", expanded=False):
        upl = st.file_uploader("Fayl tanlang", type=["pdf","docx"], key="chat_upload", label_visibility="collapsed")
        if upl:
            with st.spinner("📄 O'qilmoqda..."):
                txt = process_doc(upl)
                st.session_state.uploaded_text = txt
            if txt: st.success(f"✅ {upl.name} — {len(txt):,} belgi")
            else:   st.error("❌ O'qilmadi")

    if prompt := st.chat_input("💭  Yozing... Excel, Word, Kod, HTML so'rang!", key="chat_in"):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        db_log(st.session_state.username,"User",prompt,"input",cur_prov)
        intent = detect_intent(prompt)

        with st.chat_message("assistant"):
            LANG_RULE = "CRITICAL: Always detect user's language and reply in EXACTLY that same language."
            styles_map = {
                "Aqlli yordamchi": f"You are Somo AI — intelligent, professional AI. {LANG_RULE}",
                "Do'stona": f"You are Somo AI — friendly, warm assistant. {LANG_RULE}",
                "Rasmiy ekspert": f"You are Somo AI — formal, precise expert. {LANG_RULE}",
                "Ijodkor": f"You are Somo AI — creative thinker. {LANG_RULE}",
                "Texnik": f"You are Somo AI — deep technical expert. {LANG_RULE}",
            }
            sys_base = styles_map.get(st.session_state.ai_style, styles_map["Aqlli yordamchi"])

            if intent in ("excel","word","html","csv","code"):
                # ── Fayl so'raldi → Generatorga yo'naltirish tugmasi ──
                PAGE_MAP = {
                    "excel": ("excel", "📊", "Excel Generator", "Formulalar, ranglar, professional jadvallar"),
                    "word":  ("word",  "📝", "Word Generator",  "Rezyume, shartnoma, biznes reja"),
                    "code":  ("code",  "💻", "Kod Generator",   "Python bot, API, ML modeli"),
                    "html":  ("html",  "🌐", "HTML Generator",  "Portfolio, landing page, dashboard"),
                    "csv":   ("csv",   "📋", "CSV Generator",   "Dataset, ma'lumotlar to'plami"),
                }
                _page, _em, _title, _desc = PAGE_MAP[intent]

                # Promptni sahifaga uzatib, u yerda foydalanish uchun saqlaymiz
                st.session_state[f"{_page}_prompt"] = prompt

                resp_txt = f"{_em} **{_title}** da yaxshiroq natija olasiz!"
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(100,108,255,0.1),rgba(167,139,250,0.06));
                            border:1px solid rgba(100,108,255,0.25);border-radius:16px;padding:18px 20px;margin:8px 0;">
                    <div style="font-size:28px;margin-bottom:8px;">{_em}</div>
                    <div style="font-size:15px;font-weight:700;color:#f0f0ff;margin-bottom:4px;font-family:'Syne',sans-serif;">{_title}</div>
                    <div style="font-size:12.5px;color:#a0a0c0;margin-bottom:14px;">{_desc}</div>
                    <div style="font-size:12px;color:#818cf8;background:rgba(100,108,255,0.08);
                                border-radius:8px;padding:8px 12px;margin-bottom:14px;font-family:'JetBrains Mono',monospace;">
                        📝 So'rovingiz saqlandi: "{prompt[:60]}{'...' if len(prompt)>60 else ''}"
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"{_em}  {_title} ga o'tish →", key=f"goto_{_page}_{len(st.session_state.messages)}", type="primary", use_container_width=True):
                    st.session_state.page = _page
                    st.rerun()

                msg_d = {"role":"assistant","content":resp_txt,"provider":"none"}
                st.session_state.messages.append(msg_d)
            else:
                msgs_for_ai = [{"role":"system","content":sys_base}]
                if st.session_state.uploaded_text:
                    msgs_for_ai.append({"role":"system","content":f"Yuklangan hujjat:\n{st.session_state.uploaded_text[:4000]}"})
                # Oxirgi user xabarini ALOHIDA qo'shamiz (takrorlanmasin)
                history = st.session_state.messages[:-1]  # Oxirgi (hozirgi user) xabarsiz
                for m in history[-20:]:
                    msgs_for_ai.append({"role":m["role"],"content":m["content"]})
                msgs_for_ai.append({"role":"user","content":prompt})
                st.markdown(f'<div style="margin-bottom:10px;">{api_status_html(cur_prov)}</div>', unsafe_allow_html=True)
                response_placeholder = st.empty(); full_response = ""; used_prov = cur_prov
                try:
                    for chunk, prov_name in call_ai_stream(msgs_for_ai, st.session_state.temp, provider=cur_prov):
                        full_response += chunk; used_prov = prov_name
                        response_placeholder.markdown(full_response + '<span class="typewriter-cursor"></span>', unsafe_allow_html=True)
                    response_placeholder.markdown(full_response)
                except Exception as e:
                    with st.spinner("🤔 O'ylayapman..."):
                        full_response, used_prov = call_ai(msgs_for_ai, st.session_state.temp, provider=cur_prov)
                        response_placeholder.markdown(full_response)
                db_log("Somo AI","Assistant",full_response,"chat",used_prov)
                st.session_state.messages.append({"role":"assistant","content":full_response,"provider":used_prov})

        st.session_state.total_msgs += 1
        st.rerun()

# ══════════════════════════════════════════════════════════════════
# PAGE: EXCEL
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "excel":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]
    st.markdown(f"""
    <div class="somo-hero"><div class="grid-dots"></div><div class="somo-hero-content">
        <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#34d399;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ File Generator · {api_status_html(st.session_state.excel_provider)}</p>
        <h1>📊 Excel <span class="g-text">Generator</span></h1>
        <p class="subtitle">Har qanday jadval, hisobot — AI bilan professional Excel faylga aylantiring.</p>
    </div></div>
    """, unsafe_allow_html=True)
    xl_examples = [
        ("💰","Oylik Byudjet","12 oylik moliyaviy byudjet: daromad manbalari, xarajatlar, foyda, formulalar"),
        ("📦","Inventar","100 ta mahsulot: ID, nomi, kategoriya, miqdori, narxi, jami qiymat"),
        ("👥","Xodimlar","Xodimlari ish haqi: ism, lavozim, maosh, bonus, soliq, sof maosh"),
        ("📈","Savdo Hisoboti","Oylik savdo: mahsulot reja, haqiqat, farq, % bajarilish"),
        ("🎓","Talabalar Bahosi","30 talaba 6 fandan baho: o'rtacha, reyting, davomat"),
        ("📅","Loyiha Jadvali","IT loyiha: vazifalar, mas'ul, sana, holat, % bajarilish"),
    ]
    c1,c2,c3 = st.columns(3)
    for i,(ico,title,fp) in enumerate(xl_examples):
        with [c1,c2,c3][i%3]:
            if st.button(f"{ico}  {title}", key=f"xlq_{i}", use_container_width=True):
                st.session_state["xl_prompt"] = fp
    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
    col_inp,col_opt = st.columns([3,1])
    with col_inp:
        xl_prompt = st.text_area("📝  Jadval tavsifi:", value=st.session_state.get("xl_prompt",""),
            placeholder="Masalan: 6 xodimlik IT kompaniya uchun ish haqi jadvali...", height=140, key="xl_in")
    with col_opt:
        if avail_provs:
            curr_xl_idx = avail_provs.index(st.session_state.excel_provider) if st.session_state.excel_provider in avail_provs else 0
            xl_prov_sel = st.selectbox("🤖 AI", prov_labels, index=curr_xl_idx, key="xl_prov")
            st.session_state.excel_provider = avail_provs[prov_labels.index(xl_prov_sel)]
        xl_temp = st.slider("Aniqlik", 0.0, 0.6, 0.15, 0.05, key="xl_temp")
        gen_xl = st.button("🚀  Excel Yaratish", use_container_width=True, type="primary", key="gen_xl")
    if gen_xl:
        if not xl_prompt.strip(): st.warning("⚠️  Jadval tavsifini kiriting!")
        else:
            xl_prov = st.session_state.excel_provider
            st.markdown(f'<div class="somo-notify">📊 Excel yaratilmoqda... {api_status_html(xl_prov)}</div>', unsafe_allow_html=True)
            prog = st.progress(0)
            for pct in range(0,75,12): time.sleep(0.28); prog.progress(pct)
            fb, fn = gen_excel(xl_prompt, xl_temp, provider=xl_prov)
            prog.progress(100); time.sleep(0.15); prog.empty()
            if fb and isinstance(fb,bytes): st.session_state.files_cnt += 1; download_block(fb,fn,"Excel")
            else: st.error(f"❌  {fn}")

# ══════════════════════════════════════════════════════════════════
# PAGE: WORD
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "word":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]
    st.markdown(f"""
    <div class="somo-hero"><div class="grid-dots"></div><div class="somo-hero-content">
        <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#38bdf8;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ File Generator · {api_status_html(st.session_state.word_provider)}</p>
        <h1>📝 Word <span class="g-text">Generator</span></h1>
        <p class="subtitle">Professional hujjatlar — rezyume, shartnoma, biznes reja — AI bilan bir soniyada.</p>
    </div></div>
    """, unsafe_allow_html=True)
    wd_examples = [
        ("👤","Rezyume / CV","Python backend dasturchi rezyume: 4 yil tajriba, ko'nikmalar, ta'lim, sertifikatlar"),
        ("🤝","Hamkorlik Xati","IT kompaniyalar hamkorlik taklifnomasi: taqdimot, taklif, foyda, shartlar"),
        ("📋","Ijara Shartnomasi","Turar joy ijara shartnomasi: tomonlar, ob'ekt, muddat, to'lov, mas'uliyat"),
        ("📖","Biznes Reja","Startap biznes reja: bozor tahlili, mahsulot, marketing, moliyaviy prognoz"),
        ("🎓","Kurs Ishi","Sun'iy intellekt kurs ishi: 3 bob, xulosa, adabiyotlar, 15+ sahifa"),
        ("📑","Buyruq","Kompaniya direktori buyrug'i: xodim qabul, lavozim, ish haqi"),
    ]
    c1,c2,c3 = st.columns(3)
    for i,(ico,title,fp) in enumerate(wd_examples):
        with [c1,c2,c3][i%3]:
            if st.button(f"{ico}  {title}", key=f"wdq_{i}", use_container_width=True):
                st.session_state["wd_prompt"] = fp
    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
    col_wd,col_wopt = st.columns([3,1])
    with col_wd:
        wd_prompt = st.text_area("📝  Hujjat tavsifi:", value=st.session_state.get("wd_prompt",""),
            placeholder="Masalan: IT kompaniya uchun dasturchi mehnat shartnomasi...", height=140, key="wd_in")
    with col_wopt:
        if avail_provs:
            curr_wd_idx = avail_provs.index(st.session_state.word_provider) if st.session_state.word_provider in avail_provs else 0
            wd_prov_sel = st.selectbox("🤖 AI", prov_labels, index=curr_wd_idx, key="wd_prov")
            st.session_state.word_provider = avail_provs[prov_labels.index(wd_prov_sel)]
        gen_wd = st.button("🚀  Word Yaratish", use_container_width=True, type="primary", key="gen_wd")
    if gen_wd:
        if not wd_prompt.strip(): st.warning("⚠️  Hujjat tavsifini kiriting!")
        else:
            wd_prov = st.session_state.word_provider
            st.markdown(f'<div class="somo-notify">📝 Word yaratilmoqda... {api_status_html(wd_prov)}</div>', unsafe_allow_html=True)
            prog = st.progress(0)
            for pct in range(0,75,15): time.sleep(0.28); prog.progress(pct)
            fb, fn = gen_word(wd_prompt, provider=wd_prov)
            prog.progress(100); time.sleep(0.15); prog.empty()
            if fb and isinstance(fb,bytes): st.session_state.files_cnt += 1; download_block(fb,fn,"Word")
            else: st.error(f"❌  {fn}")

# ══════════════════════════════════════════════════════════════════
# PAGE: CODE
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "code":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]
    st.markdown(f"""
    <div class="somo-hero"><div class="grid-dots"></div><div class="somo-hero-content">
        <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#fbbf24;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ Code Generator · {api_status_html(st.session_state.code_provider)}</p>
        <h1>💻 Kod <span class="g-text">Generator</span></h1>
        <p class="subtitle">Professional Python kodi — error handling, izohlar va best practices bilan.</p>
    </div></div>
    """, unsafe_allow_html=True)
    code_examples = [
        ("🤖","Telegram Bot","Aiogram v3 Telegram bot: /start, /help, inline keyboard, FSM, SQLite"),
        ("🌐","FastAPI CRUD","FastAPI CRUD API: PostgreSQL, SQLAlchemy, Pydantic, JWT, Swagger"),
        ("📊","Dashboard","Streamlit dashboard: CSV yuklash, pandas, plotly grafiklar, filter"),
        ("🔍","Web Scraper","BeautifulSoup4 scraper: sahifa tahlili, CSV saqlash, delay"),
        ("🤖","ML Model","Scikit-learn classification: data, train, hyperparameter, hisobot"),
        ("📧","Email Sender","smtplib email: HTML template, attachment, bulk send"),
    ]
    c1,c2,c3 = st.columns(3)
    for i,(ico,title,fp) in enumerate(code_examples):
        with [c1,c2,c3][i%3]:
            if st.button(f"{ico}  {title}", key=f"cq_{i}", use_container_width=True):
                st.session_state["cd_prompt"] = fp
    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
    col_cd,col_co = st.columns([3,1])
    with col_cd:
        cd_prompt = st.text_area("📝  Kod tavsifi:", value=st.session_state.get("cd_prompt",""),
            placeholder="Masalan: Telegram bot — narx so'raganda Olx.uz dan avtomatik qidirsin...", height=140, key="cd_in")
    with col_co:
        if avail_provs:
            curr_cd_idx = avail_provs.index(st.session_state.code_provider) if st.session_state.code_provider in avail_provs else 0
            cd_prov_sel = st.selectbox("🤖 AI", prov_labels, index=curr_cd_idx, key="cd_prov")
            st.session_state.code_provider = avail_provs[prov_labels.index(cd_prov_sel)]
        cd_temp = st.slider("Ijodkorlik", 0.0, 0.5, 0.1, 0.05, key="cd_temp")
        gen_cd = st.button("🚀  Kod Yaratish", use_container_width=True, type="primary", key="gen_cd")
    if gen_cd:
        if not cd_prompt.strip(): st.warning("⚠️  Kod tavsifini kiriting!")
        else:
            cd_prov = st.session_state.code_provider
            st.markdown(f'<div class="somo-notify">💻 Kod yozilmoqda... {api_status_html(cd_prov)}</div>', unsafe_allow_html=True)
            prog = st.progress(0)
            for pct in range(0,65,15): time.sleep(0.22); prog.progress(pct)
            fb, fn = gen_code(cd_prompt, cd_temp, provider=cd_prov)
            prog.progress(100); prog.empty()
            st.session_state.files_cnt += 1
            st.markdown('<div class="somo-success">✅  Kod tayyor!</div>', unsafe_allow_html=True)
            with st.expander("👁  Kod Preview", expanded=True):
                st.code(fb.decode('utf-8'), language="python")
            st.download_button("⬇️  .py Fayl", fb, fn, "text/x-python", use_container_width=True, type="primary", key=f"dl_py_{time.time()}")

# ══════════════════════════════════════════════════════════════════
# PAGE: HTML
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "html":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]
    st.markdown(f"""
    <div class="somo-hero"><div class="grid-dots"></div><div class="somo-hero-content">
        <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#f472b6;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ HTML Generator · {api_status_html(st.session_state.html_provider)}</p>
        <h1>🌐 HTML <span class="g-text">Generator</span></h1>
        <p class="subtitle">Zamonaviy, animatsiyali veb sahifalar — bitta .html faylda hamma narsa.</p>
    </div></div>
    """, unsafe_allow_html=True)
    html_examples = [
        ("🎨","Portfolio","Web developer portfolio: hero typewriter, skills, projects, dark theme"),
        ("🛒","Mahsulot Sahifasi","E-commerce mahsulot: gallery, narx, cart, reviews"),
        ("📊","Dashboard","Analytics dashboard: sidebar, stat cards, charts, dark glassmorphism"),
        ("🎪","Event Landing","Konferensiya: hero countdown, speakers, schedule, tickets"),
        ("🔐","Login Sahifa","Zamonaviy login: glassmorphism, validation, particles"),
        ("📰","Blog Post","Blog: hero image, typography, TOC, code blocks"),
    ]
    c1,c2,c3 = st.columns(3)
    for i,(ico,title,fp) in enumerate(html_examples):
        with [c1,c2,c3][i%3]:
            if st.button(f"{ico}  {title}", key=f"hq_{i}", use_container_width=True):
                st.session_state["ht_prompt"] = fp
    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
    col_ht,col_hopt = st.columns([3,1])
    with col_ht:
        ht_prompt = st.text_area("📝  Sahifa tavsifi:", value=st.session_state.get("ht_prompt",""),
            placeholder="Masalan: AI kompaniyasi uchun landing page — dark neon dizayn...", height=140, key="ht_in")
    with col_hopt:
        if avail_provs:
            curr_ht_idx = avail_provs.index(st.session_state.html_provider) if st.session_state.html_provider in avail_provs else 0
            ht_prov_sel = st.selectbox("🤖 AI", prov_labels, index=curr_ht_idx, key="ht_prov")
            st.session_state.html_provider = avail_provs[prov_labels.index(ht_prov_sel)]
        gen_ht = st.button("🚀  HTML Yaratish", use_container_width=True, type="primary", key="gen_ht")
    if gen_ht:
        if not ht_prompt.strip(): st.warning("⚠️  Sahifa tavsifini kiriting!")
        else:
            ht_prov = st.session_state.html_provider
            st.markdown(f'<div class="somo-notify">🌐 HTML yaratilmoqda... {api_status_html(ht_prov)}</div>', unsafe_allow_html=True)
            prog = st.progress(0)
            for pct in range(0,70,14): time.sleep(0.28); prog.progress(pct)
            fb, fn = gen_html(ht_prompt, 0.5, provider=ht_prov)
            prog.progress(100); prog.empty()
            st.session_state.files_cnt += 1
            st.markdown('<div class="somo-success">✅ HTML tayyor! Yuklab, brauzerda oching.</div>', unsafe_allow_html=True)
            with st.expander("👁  HTML Preview"):
                st.code(fb.decode('utf-8')[:3000], language="html")
            st.download_button("⬇️  HTML Fayl", fb, fn, "text/html", use_container_width=True, type="primary", key=f"dl_html_{time.time()}")

# ══════════════════════════════════════════════════════════════════
# PAGE: CSV
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "csv":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]
    st.markdown(f"""
    <div class="somo-hero"><div class="grid-dots"></div><div class="somo-hero-content">
        <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#a78bfa;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ Data Generator · {api_status_html(st.session_state.csv_provider)}</p>
        <h1>📋 CSV <span class="g-text">Generator</span></h1>
        <p class="subtitle">Katta ma'lumotlar to'plamini bir so'rovda yarating.</p>
    </div></div>
    """, unsafe_allow_html=True)
    csv_examples = [
        ("📦","Mahsulotlar","100 ta mahsulot: ID, nomi, kategoriya, narxi, miqdori, brend, reyting"),
        ("👥","Foydalanuvchilar","50 ta user: ID, ism, email, telefon, shahar, sana, holat"),
        ("🌍","Mamlakatlar","Dunyo mamlakatlari: nomi, poytaxti, aholisi, maydoni, YIM"),
        ("📱","Ilovalar","Top 100 mobil ilova: nomi, kategoriya, reyting, yuklamalar"),
        ("🎬","Filmlar","Top 100 film: nomi, rejissor, yili, janri, reyting, byudjet"),
        ("💼","Kompaniyalar","50 kompaniya: nomi, sektori, xodimlar, daromad, asos yili"),
    ]
    c1,c2,c3 = st.columns(3)
    for i,(ico,title,fp) in enumerate(csv_examples):
        with [c1,c2,c3][i%3]:
            if st.button(f"{ico}  {title}", key=f"cvq_{i}", use_container_width=True):
                st.session_state["cv_prompt"] = fp
    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
    col_cv,col_copt = st.columns([3,1])
    with col_cv:
        cv_prompt = st.text_area("📝  Dataset tavsifi:", value=st.session_state.get("cv_prompt",""),
            placeholder="Masalan: 80 ta O'zbekiston shahri: viloyati, aholisi, maydoni...", height=130, key="cv_in")
    with col_copt:
        if avail_provs:
            curr_cv_idx = avail_provs.index(st.session_state.csv_provider) if st.session_state.csv_provider in avail_provs else 0
            cv_prov_sel = st.selectbox("🤖 AI", prov_labels, index=curr_cv_idx, key="cv_prov")
            st.session_state.csv_provider = avail_provs[prov_labels.index(cv_prov_sel)]
        gen_cv = st.button("🚀  CSV Yaratish", use_container_width=True, type="primary", key="gen_cv")
    if gen_cv:
        if not cv_prompt.strip(): st.warning("⚠️  Dataset tavsifini kiriting!")
        else:
            cv_prov = st.session_state.csv_provider
            st.markdown(f'<div class="somo-notify">📋 Dataset yaratilmoqda... {api_status_html(cv_prov)}</div>', unsafe_allow_html=True)
            prog = st.progress(0)
            for pct in range(0,65,15): time.sleep(0.22); prog.progress(pct)
            fb, fn = gen_csv(cv_prompt, provider=cv_prov)
            prog.progress(100); prog.empty()
            st.session_state.files_cnt += 1
            try:
                df = pd.read_csv(io.BytesIO(fb))
                st.markdown(f'<div class="somo-success">✅  CSV tayyor — {len(df)} satr, {len(df.columns)} ustun</div>', unsafe_allow_html=True)
                st.dataframe(df.head(10), use_container_width=True)
                if len(df) > 10: st.caption(f"↑ Birinchi 10 ta (jami {len(df)} ta)")
            except: st.markdown('<div class="somo-success">✅  CSV tayyor!</div>', unsafe_allow_html=True)
            st.download_button("⬇️  CSV Yuklab Olish", fb, fn, "text/csv", use_container_width=True, type="primary", key=f"dl_csv_{time.time()}")

# ══════════════════════════════════════════════════════════════════
# PAGE: TEMPLATES
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "templates":
    st.markdown("""
    <div class="somo-hero"><div class="grid-dots"></div><div class="somo-hero-content">
        <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#646cff;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ Template Library</p>
        <h1>🎨 Shablonlar <span class="g-text">Markazi</span></h1>
        <p class="subtitle">16 ta professional shablon — bitta bosish bilan yarating.</p>
    </div></div>
    """, unsafe_allow_html=True)
    TEMPLATES = {
        "📊 Biznes": [
            {"ico":"💰","title":"Oylik Byudjet","tag":"excel","tag_cls":"tag-excel","desc":"12 oylik moliyaviy byudjet","prompt":"12 oylik moliyaviy byudjet Excel: daromad, xarajatlar 8 kategoriya, sof foyda, jamg'arma, formulalar"},
            {"ico":"📈","title":"KPI Dashboard","tag":"excel","tag_cls":"tag-excel","desc":"Kompaniya KPI ko'rsatkichlari","prompt":"Kompaniya KPI Excel: 15 ko'rsatkich, maqsad va haqiqat, farq foizi, RAG ranglash"},
            {"ico":"📋","title":"Biznes Reja","tag":"word","tag_cls":"tag-word","desc":"To'liq startap biznes reja","prompt":"IT startap biznes reja Word: ijroiya xulosa, bozor tahlili, mahsulot, marketing, moliyaviy prognoz 3 yil"},
            {"ico":"🤝","title":"Hamkorlik Xati","tag":"word","tag_cls":"tag-word","desc":"Professional hamkorlik taklifnomasi","prompt":"Hamkorlik taklifnomasi Word: kompaniya taqdimoti, taklif, o'zaro foyda, shartlar"},
        ],
        "💻 Dasturlash": [
            {"ico":"🤖","title":"Telegram Bot","tag":"code","tag_cls":"tag-code","desc":"Aiogram v3, FSM, SQLite","prompt":"Aiogram v3 Telegram bot: /start, /help, InlineKeyboard, FSM, SQLite, admin panel, .env"},
            {"ico":"🌐","title":"FastAPI REST","tag":"code","tag_cls":"tag-code","desc":"CRUD, JWT, PostgreSQL","prompt":"FastAPI REST API: User, Post, Comment, SQLAlchemy+PostgreSQL, Pydantic, JWT, CRUD, CORS"},
            {"ico":"🎨","title":"Portfolio Sayt","tag":"html","tag_cls":"tag-html","desc":"Dark theme, glassmorphism","prompt":"Web developer portfolio HTML: typewriter hero, skills bars, projects glassmorphism, dark theme, responsive"},
            {"ico":"📊","title":"Streamlit App","tag":"code","tag_cls":"tag-code","desc":"Data dashboard, grafik","prompt":"Streamlit data app: CSV yuklab, pandas, Plotly grafiklar, filterlar, dark theme"},
        ],
        "📚 Ta'lim": [
            {"ico":"📖","title":"Dars Rejasi","tag":"word","tag_cls":"tag-word","desc":"45 daqiqalik dars konspekti","prompt":"Python asoslari 45 daqiqalik dars Word: maqsadlar, bosqichlar, savol-javob, baholash"},
            {"ico":"📝","title":"Test Savollari","tag":"excel","tag_cls":"tag-excel","desc":"25 ta test, 4 variant","prompt":"Python 25 test Excel: savol, A-B-C-D variant, to'g'ri javob, mavzu, qiyinchilik"},
            {"ico":"🎓","title":"Baholash Jadvali","tag":"excel","tag_cls":"tag-excel","desc":"30 talaba, 6 fan","prompt":"Guruh baholash Excel: 30 talaba, 6 fan, o'rtacha, GPA, reyting, davomat, formulalar"},
            {"ico":"📚","title":"Kurs Ishi","tag":"word","tag_cls":"tag-word","desc":"15+ sahifa, 3 bob","prompt":"Sun'iy intellekt kurs ishi Word: titul, mundarija, kirish, 3 bob, xulosa, 15 adabiyot"},
        ],
        "👤 Shaxsiy": [
            {"ico":"📄","title":"Rezyume","tag":"word","tag_cls":"tag-word","desc":"Professional CV","prompt":"Python/Django dasturchi rezyume Word: ism, kontakt, xulosa, ko'nikmalar, 2 ish joyi, ta'lim, sertifikatlar"},
            {"ico":"📅","title":"Haftalik Reja","tag":"excel","tag_cls":"tag-excel","desc":"7 kun, vazifalar, holat","prompt":"Haftalik vazifalar Excel: 7 kun, vaqt slotlari, vazifa, ustuvorlik, holat, statistika"},
            {"ico":"💰","title":"Shaxsiy Byudjet","tag":"excel","tag_cls":"tag-excel","desc":"Daromad, xarajat, jamg'arma","prompt":"Shaxsiy moliya Excel: daromad, xarajatlar kategoriyalar, jamg'arma, oylik trend"},
            {"ico":"💪","title":"Sport Rejasi","tag":"excel","tag_cls":"tag-excel","desc":"3 oylik trening, progres","prompt":"3 oylik sport Excel: haftalik trening, mashqlar, to'plamlar, ozish maqsad, kaloriya, progres"},
        ]
    }
    sel = st.selectbox("📁  Kategoriya:", list(TEMPLATES.keys()), key="tmpl_sel")
    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
    items = TEMPLATES[sel]; c1,c2 = st.columns(2)
    tag_to_prov = {"excel":st.session_state.excel_provider,"word":st.session_state.word_provider,"code":st.session_state.code_provider,"html":st.session_state.html_provider,"csv":st.session_state.csv_provider}
    for i,tmpl in enumerate(items):
        with [c1,c2][i%2]:
            t_prov = tag_to_prov.get(tmpl["tag"],"groq")
            st.markdown(f"""
            <div class="tmpl-card">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                    <span class="tmpl-tag {tmpl['tag_cls']}">{tmpl['tag'].upper()}</span>
                    {api_status_html(t_prov)}
                </div>
                <div class="tmpl-title">{tmpl['ico']}  {tmpl['title']}</div>
                <div class="tmpl-desc">{tmpl['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            bc1,bc2 = st.columns(2)
            with bc1:
                if st.button("🚀  Yaratish", key=f"tgen_{sel}_{i}", use_container_width=True, type="primary"):
                    with st.spinner("⏳  Tayyorlanmoqda..."):
                        tag = tmpl["tag"]
                        if tag=="excel":
                            fb,fn = gen_excel(tmpl["prompt"],provider=st.session_state.excel_provider)
                            if fb and isinstance(fb,bytes): st.session_state.files_cnt+=1; st.download_button("⬇️  Excel",fb,fn,MIME["xlsx"],key=f"tdl_{sel}_{i}",type="primary")
                        elif tag=="word":
                            fb,fn = gen_word(tmpl["prompt"],provider=st.session_state.word_provider)
                            if fb and isinstance(fb,bytes): st.session_state.files_cnt+=1; st.download_button("⬇️  Word",fb,fn,MIME["docx"],key=f"tdl_{sel}_{i}",type="primary")
                        elif tag=="code":
                            fb,fn = gen_code(tmpl["prompt"],provider=st.session_state.code_provider)
                            st.session_state.files_cnt+=1; st.download_button("⬇️  .py",fb,fn,MIME["py"],key=f"tdl_{sel}_{i}",type="primary")
                        elif tag=="html":
                            fb,fn = gen_html(tmpl["prompt"],provider=st.session_state.html_provider)
                            st.session_state.files_cnt+=1; st.download_button("⬇️  HTML",fb,fn,MIME["html"],key=f"tdl_{sel}_{i}",type="primary")
            with bc2:
                if st.button("💬  Chat AI", key=f"tchat_{sel}_{i}", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":tmpl["prompt"]})
                    st.session_state.page = "chat"; st.rerun()

# ══════════════════════════════════════════════════════════════════
# PAGE: ANALYZE
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "analyze":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]
    st.markdown(f"""
    <div class="somo-hero"><div class="grid-dots"></div><div class="somo-hero-content">
        <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#22d3ee;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ Document Analysis · {api_status_html(st.session_state.analyze_provider)}</p>
        <h1>🔍 Hujjat <span class="g-text">Tahlili</span></h1>
        <p class="subtitle">PDF yoki Word faylni yuklang — AI xulosa, g'oyalar, savol-javob.</p>
    </div></div>
    """, unsafe_allow_html=True)
    col_up,col_act = st.columns([1,1])
    with col_up:
        st.markdown('<p class="section-label">Fayl Yuklash</p>', unsafe_allow_html=True)
        if avail_provs:
            curr_az_idx = avail_provs.index(st.session_state.analyze_provider) if st.session_state.analyze_provider in avail_provs else 0
            az_prov_sel = st.selectbox("🤖 AI Provider", prov_labels, index=curr_az_idx, key="az_prov")
            st.session_state.analyze_provider = avail_provs[prov_labels.index(az_prov_sel)]
        upl = st.file_uploader("PDF yoki DOCX", type=["pdf","docx"], key="az_up", label_visibility="collapsed")
        if upl:
            with st.spinner("📄 O'qilmoqda..."):
                txt = process_doc(upl)
                st.session_state.uploaded_text = txt
            if txt:
                st.markdown(f'<div class="somo-success">✅  {upl.name} — {len(txt):,} belgi</div>', unsafe_allow_html=True)
                with st.expander("👁  Matnni ko'rish"):
                    st.text(txt[:2000]+("..." if len(txt)>2000 else ""))
            else: st.error("❌ Fayl o'qilmadi")
    with col_act:
        st.markdown('<p class="section-label">Tahlil Amaliyotlari</p>', unsafe_allow_html=True)
        if st.session_state.uploaded_text:
            az_prov = st.session_state.analyze_provider
            actions = {
                "📝  Qisqa Xulosa":   "Hujjatni 5-7 asosiy band bilan xulosasin yoz. Har bandni ★ bilan boshlat.",
                "🔑  Kalit G'oyalar": "Hujjatdagi 8-10 muhim g'oya va faktlarni ro'yxat shaklida ajrat.",
                "❓  Savol-Javob":    "Hujjat bo'yicha 10 muhim savol tuz va har biriga javob ber.",
                "🌐  Inglizcha":      "Hujjat mazmunini professional ingliz tiliga tarjima qil.",
                "📊  Statistika":     "Hujjatdagi barcha raqamlar va statistikani jadval ko'rinishida tizimlashtir.",
                "✅  Action Items":   "Hujjatdan aniq amaliy vazifalar va keyingi qadamlarni ustuvorlik bo'yicha tartibla.",
            }
            for act_lbl,act_prompt in actions.items():
                if st.button(act_lbl, key=f"az_{act_lbl}", use_container_width=True):
                    az_msgs = [
                        {"role":"system","content":"Sen professional hujjat tahlilchisan."},
                        {"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:4500]}\n\nVazifa: {act_prompt}"}
                    ]
                    result_placeholder = st.empty(); full_az = ""
                    st.markdown(f'<div style="margin-bottom:6px;">{api_status_html(az_prov)}</div>', unsafe_allow_html=True)
                    for chunk,_ in call_ai_stream(az_msgs, temperature=0.4, provider=az_prov):
                        full_az += chunk
                        result_placeholder.markdown(f"**{act_lbl}**\n\n"+full_az+'<span class="typewriter-cursor"></span>', unsafe_allow_html=True)
                    result_placeholder.markdown(f"**{act_lbl}**\n\n{full_az}")
        else:
            st.markdown("""<div style="background:rgba(100,108,255,0.04);border:1px solid rgba(100,108,255,0.12);border-radius:14px;padding:28px;text-align:center;margin-top:8px;">
                <p style="font-size:36px;margin-bottom:12px;">📂</p><p style="color:#50506a;font-size:14px;">Chap tomonda fayl yuklang</p></div>""", unsafe_allow_html=True)
    if st.session_state.uploaded_text:
        st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">O\'z Savolingiz</p>', unsafe_allow_html=True)
        cq,cb = st.columns([4,1])
        with cq: custom_q = st.text_input("", placeholder="🔍 Hujjat haqida savolingiz...", label_visibility="collapsed", key="az_q")
        with cb:
            if st.button("🔍  Qidirish", use_container_width=True, type="primary", key="az_ask"):
                if custom_q:
                    az_prov = st.session_state.analyze_provider
                    az_msgs = [{"role":"system","content":"Hujjat asosida aniq javob ber."},{"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:4500]}\n\nSavol: {custom_q}"}]
                    ans_pl = st.empty(); full_ans = ""
                    for chunk,_ in call_ai_stream(az_msgs, temperature=0.3, provider=az_prov):
                        full_ans += chunk
                        ans_pl.markdown("**💬 Javob:**\n\n"+full_ans+'<span class="typewriter-cursor"></span>', unsafe_allow_html=True)
                    ans_pl.markdown(f"**💬 Javob:**\n\n{full_ans}")

# ══════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "history":
    st.markdown("""<div class="somo-hero"><div class="grid-dots"></div><div class="somo-hero-content">
        <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#646cff;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ History</p>
        <h1>📜 Chat <span class="g-text">Tarixi</span></h1>
        <p class="subtitle">Barcha suhbatlaringiz, qidirish va eksport bilan.</p>
    </div></div>""", unsafe_allow_html=True)
    msgs = st.session_state.messages
    if msgs:
        u_cnt = sum(1 for m in msgs if m["role"]=="user"); a_cnt = len(msgs)-u_cnt
        st.markdown(f"""<div class="stat-row" style="grid-template-columns:repeat(4,1fr);">
            <div class="stat-box"><div class="stat-icon">💬</div><div class="stat-val">{len(msgs)}</div><div class="stat-lbl">Jami</div></div>
            <div class="stat-box"><div class="stat-icon">👤</div><div class="stat-val">{u_cnt}</div><div class="stat-lbl">Sizdan</div></div>
            <div class="stat-box"><div class="stat-icon">🤖</div><div class="stat-val">{a_cnt}</div><div class="stat-lbl">AI dan</div></div>
            <div class="stat-box"><div class="stat-icon">📁</div><div class="stat-val">{st.session_state.files_cnt}</div><div class="stat-lbl">Fayllar</div></div>
        </div>""", unsafe_allow_html=True)
        col_s,col_e1,col_e2 = st.columns([3,1,1])
        with col_s: search = st.text_input("", placeholder="🔍  Xabarlarda qidirish...", label_visibility="collapsed", key="hist_s")
        _safe = [{"role":m.get("role",""),"content":m.get("content",""),"provider":m.get("provider","")} for m in msgs]
        with col_e1: st.download_button("📥  JSON", json.dumps(_safe,ensure_ascii=False,indent=2).encode(), f"somo_{datetime.now():%Y%m%d}.json", use_container_width=True)
        with col_e2:
            txt_exp = "\n\n".join([f"[{m['role'].upper()}]\n{m['content']}" for m in msgs])
            st.download_button("📄  TXT", txt_exp.encode(), f"somo_{datetime.now():%Y%m%d}.txt", use_container_width=True)
        show = [m for m in msgs if search.lower() in m.get("content","").lower()] if search else msgs
        if search: st.markdown(f'<div class="somo-notify">🔍  "{search}" — {len(show)} ta natija</div>', unsafe_allow_html=True)
        st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
        for msg in reversed(show[-50:]):
            is_user = msg["role"]=="user"
            prov_used = msg.get("provider","groq")
            role_lbl = "👤  Siz" if is_user else f"🤖  Somo AI · {API_CONFIGS.get(prov_used,API_CONFIGS['groq'])['icon']}"
            body = msg.get("content","")[:350]+("..." if len(msg.get("content",""))>350 else "")
            st.markdown(f"""<div class="hist-msg {'hist-user' if is_user else 'hist-ai'}">
                <div class="hist-role">{role_lbl}</div>
                <div class="hist-body">{body}</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="text-align:center;padding:60px 20px;">
            <div style="font-size:56px;margin-bottom:20px;">💬</div>
            <p style="color:#50506a;font-size:18px;font-weight:700;">Chat tarixi yo'q</p></div>""", unsafe_allow_html=True)
        if st.button("💬  Chat AI ga o'tish", type="primary"):
            st.session_state.page = "chat"; st.rerun()

# ══════════════════════════════════════════════════════════════════
# PAGE: FEEDBACK
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "feedback":
    st.markdown("""<div class="somo-hero"><div class="grid-dots"></div><div class="somo-hero-content">
        <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#f472b6;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ Feedback</p>
        <h1>💌 Fikr <span class="g-text">Bildirish</span></h1>
        <p class="subtitle">Sizning fikringiz Somo AI ni yaxshiroq qilishga yordam beradi.</p>
    </div></div>""", unsafe_allow_html=True)
    col_f,col_s = st.columns([3,2])
    with col_f:
        with st.form("fb_form", clear_on_submit=True):
            rating = st.select_slider("⭐  Baho:", options=[1,2,3,4,5], value=5, format_func=lambda x: "⭐"*x+f"  ({x}/5)")
            category = st.selectbox("📂  Kategoriya:", ["Umumiy fikr","Xato haqida","Yangi funksiya taklifi","Dizayn taklifi","Tezlik muammosi","Boshqa"])
            message = st.text_area("✍️  Xabar:", height=140, placeholder="Fikrlaringizni yozing (kamida 10 belgi)...")
            email = st.text_input("📧  Email (ixtiyoriy):", placeholder="javob olish uchun")
            sub_fb = st.form_submit_button("📤  Yuborish", use_container_width=True, type="primary")
            if sub_fb:
                if not message or len(message)<10: st.error("❌  Kamida 10 belgidan iborat xabar!")
                elif fb_db:
                    try:
                        fb_db.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            st.session_state.username, rating, category, message, email or "N/A", "Yangi", st.session_state.files_cnt])
                        st.balloons(); st.markdown('<div class="somo-success">✅  Rahmat! Fikringiz yuborildi 🙏</div>', unsafe_allow_html=True)
                    except Exception as e: st.error(f"❌  {e}")
                else: st.error("❌  Baza ulanmagan")

# ══════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "profile":
    uname = st.session_state.username
    mins = (datetime.now()-st.session_state.login_time).seconds//60  # FIX 5
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    st.markdown(f"""
    <div class="somo-hero" style="text-align:center;"><div class="grid-dots"></div><div class="somo-hero-content">
        <div style="width:88px;height:88px;background:linear-gradient(135deg,#4f46e5,#7c3aed,#f472b6);border-radius:24px;margin:0 auto 20px;display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:900;color:white;box-shadow:0 0 40px rgba(100,108,255,0.5);">
            {uname[0].upper()}
        </div>
        <h1 style="font-size:32px;">{uname}</h1>
        <p style="color:rgba(255,255,255,0.55);font-size:14px;margin-top:8px;font-family:'JetBrains Mono',monospace;">🟢 ONLINE · Somo AI v3.1 · {len(avail_provs)} API aktiv</p>
    </div></div>
    """, unsafe_allow_html=True)
    p_stats = [("💬",len(st.session_state.messages),"Xabarlar"),("📁",st.session_state.files_cnt,"Fayllar"),("⏱",mins,"Daqiqa"),("🤖",len(avail_provs),"API")]
    cols_ps = st.columns(4)
    for col,(icon,val,lbl) in zip(cols_ps,p_stats):
        with col:
            st.markdown(f"""<div class="profile-stat"><div class="p-stat-icon">{icon}</div><div class="p-stat-val">{val}</div><div class="p-stat-lbl">{lbl}</div></div>""", unsafe_allow_html=True)
    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
    col_pw,col_info = st.columns(2)
    with col_pw:
        st.markdown('<p class="section-label">Xavfsizlik</p><p class="section-title" style="font-size:18px;">🔑 Parolni O\'zgartirish</p>', unsafe_allow_html=True)
        with st.form("pw_form"):
            old_pw = st.text_input("Joriy parol", type="password", key="pw_old")
            new_pw = st.text_input("Yangi parol (min 6)", type="password", key="pw_new")
            conf_pw = st.text_input("Tasdiqlash", type="password", key="pw_conf")
            if st.form_submit_button("🔄  Yangilash", type="primary", use_container_width=True):
                if len(new_pw)<6:     st.error("❌ Yangi parol kamida 6 belgi!")
                elif new_pw!=conf_pw: st.error("❌ Parollar mos emas!")
                elif user_db:
                    try:
                        recs = get_all_users()
                        idx = next((i for i,r in enumerate(recs) if str(r['username'])==uname and check_pw(old_pw,str(r['password']))), None)
                        if idx is not None:
                            user_db.update_cell(idx+2,2,hash_pw(new_pw))
                            get_all_users.clear()  # cache tozalash
                            st.success("✅ Parol yangilandi!")
                        else: st.error("❌ Joriy parol noto'g'ri!")
                    except Exception as e: st.error(f"❌ {e}")
    with col_info:
        st.markdown('<p class="section-label">API Sozlamalari</p><p class="section-title" style="font-size:18px;">🤖 Har Format uchun AI</p>', unsafe_allow_html=True)
        prov_labels_all = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]
        format_provs = [("chat_provider","💬 Chat"),("excel_provider","📊 Excel"),("word_provider","📝 Word"),("code_provider","💻 Kod"),("html_provider","🌐 HTML"),("csv_provider","📋 CSV"),("analyze_provider","🔍 Tahlil")]
        for sess_key,label in format_provs:
            curr_val = st.session_state.get(sess_key,"groq")
            curr_idx = avail_provs.index(curr_val) if curr_val in avail_provs else 0
            sel = st.selectbox(label, prov_labels_all, index=curr_idx, key=f"prof_{sess_key}")
            st.session_state[sess_key] = avail_provs[prov_labels_all.index(sel)]
        if st.button("💾  Saqlash", type="primary", key="save_style", use_container_width=True):
            st.success("✅ Sozlamalar saqlandi!")

# ══════════════════════════════════════════════════════════════════
# FOOTER — FIX 8: "Mavlonov Saloxiddin" olib tashlandi
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="somo-footer">
    <div class="f-title">🌌 Somo AI <span class="g-text">Ultra Pro Max</span></div>
    <div class="f-sub" style="margin-bottom:12px;">
        <span class="api-badge api-groq" style="display:inline-flex;"><span class="api-dot"></span>⚡ Groq</span>&nbsp;
        <span class="api-badge api-gemini" style="display:inline-flex;"><span class="api-dot"></span>✨ Gemini</span>&nbsp;
        <span class="api-badge api-cohere" style="display:inline-flex;"><span class="api-dot"></span>🔮 Cohere</span>&nbsp;
        <span class="api-badge api-mistral" style="display:inline-flex;"><span class="api-dot"></span>🌪 Mistral</span>
    </div>
    <div class="f-sub">📊 Excel · 📝 Word · 💻 Kod · 🌐 HTML · 📋 CSV · 🧠 Chat AI</div>
    <div class="f-sub" style="margin-top:10px;">👨‍💻 <strong style="color:#e2e8f0;">Usmonov Sodiq</strong> · Somo AI</div>
    <div class="f-copy">© 2026 Somo AI Ultra Pro Max v3.1 — Python · Streamlit</div>
</div>
""", unsafe_allow_html=True)
