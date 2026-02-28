import streamlit as st
import pandas as pd
import gspread
import hashlib
import json
import time
import io
import re
import os
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from streamlit_cookies_manager import EncryptedCookieManager

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
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, GradientFill
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except: HAS_OPENPYXL = False

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except: HAS_DOCX = False

# ══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Somo AI | Ultra Pro Max",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════
# COOKIES
# ══════════════════════════════════════════════════════════════════
cookies = EncryptedCookieManager(
    password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Ultra_Pro_Max_2026_XYZ")
)
if not cookies.ready():
    st.stop()

# ══════════════════════════════════════════════════════════════════
# MASTER CSS  —  Butun dastur uchun yagona dizayn tizimi
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

/* ─── GLOBAL ─── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: #0a0a0f !important;
    color: #e2e8f0 !important;
}
.stApp { background: #0a0a0f !important; }

/* ─── HIDE STREAMLIT JUNK ─── */
[data-testid="stSidebarNav"],
.st-emotion-cache-1vt458p,
.st-emotion-cache-k77z8z,
header[data-testid="stHeader"],
#MainMenu, footer { display: none !important; }

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #0f0f20 60%, #12102a 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.25) !important;
    width: 260px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebar"] section { background: transparent !important; }
[data-testid="stSidebar"] .stVerticalBlock { gap: 0 !important; }
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span { color: #64748b !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }

/* Sidebar nav buttons */
div[data-testid="stSidebar"] button {
    background: transparent !important;
    color: #94a3b8 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    padding: 10px 14px !important;
    margin: 1px 0 !important;
    text-align: left !important;
}
div[data-testid="stSidebar"] button:hover {
    background: rgba(99,102,241,0.12) !important;
    color: #c7d2fe !important;
    transform: none !important;
}
div[data-testid="stSidebar"] button[kind="primary"],
div[data-testid="stSidebar"] button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 0 20px rgba(99,102,241,0.35) !important;
}

/* ─── MAIN CONTENT AREA ─── */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stMainBlockContainer"] {
    padding: 20px 28px 60px !important;
    background: #0a0a0f !important;
}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d0d1a; }
::-webkit-scrollbar-thumb { background: #312e81; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #4f46e5; }

/* ══════════════════════════════════════
   HERO BANNER — all pages use this
══════════════════════════════════════ */
.somo-hero {
    position: relative;
    overflow: hidden;
    border-radius: 20px;
    padding: 52px 48px;
    margin-bottom: 32px;
    background: linear-gradient(135deg, #0f0c29 0%, #1a1040 40%, #24006e 70%, #0f0c29 100%);
    border: 1px solid rgba(139,92,246,0.3);
    box-shadow: 0 0 60px rgba(99,102,241,0.15), 0 20px 60px rgba(0,0,0,0.5);
}
.somo-hero::before {
    content: '';
    position: absolute;
    top: -60%;  left: -20%;
    width: 700px; height: 700px;
    background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 65%);
    animation: hero-pulse 8s ease-in-out infinite;
}
.somo-hero::after {
    content: '';
    position: absolute;
    bottom: -40%; right: -10%;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(236,72,153,0.12) 0%, transparent 65%);
    animation: hero-pulse 8s ease-in-out 4s infinite;
}
@keyframes hero-pulse { 0%,100%{transform:scale(1) translateY(0)} 50%{transform:scale(1.15) translateY(-20px)} }

.somo-hero-content { position: relative; z-index: 2; }

.somo-hero h1 {
    font-size: clamp(28px, 4vw, 46px);
    font-weight: 900;
    line-height: 1.15;
    letter-spacing: -1px;
    color: white;
    margin-bottom: 12px;
}
.somo-hero .subtitle {
    font-size: 17px;
    color: rgba(255,255,255,0.65);
    max-width: 520px;
    line-height: 1.6;
    margin-bottom: 24px;
}
.hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}
.hero-badge {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    color: rgba(255,255,255,0.85);
    padding: 6px 16px;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 500;
    backdrop-filter: blur(10px);
}

/* Gradient text */
.g-text {
    background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gshift 4s ease infinite;
}
@keyframes gshift { 0%,100%{background-position:0%} 50%{background-position:100%} }

/* ══════════════════════════════════════
   SECTION HEADER
══════════════════════════════════════ */
.section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 8px;
}
.section-title {
    font-size: 26px;
    font-weight: 800;
    color: #f1f5f9;
    margin-bottom: 6px;
    letter-spacing: -0.5px;
}
.section-desc {
    font-size: 15px;
    color: #64748b;
    margin-bottom: 28px;
}

/* ══════════════════════════════════════
   FEATURE CARDS — dashboard grid
══════════════════════════════════════ */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
}
.somo-card {
    background: linear-gradient(145deg, #13131f, #0f0f1e);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 16px;
    padding: 28px 20px;
    text-align: center;
    transition: all 0.3s cubic-bezier(.4,0,.2,1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.somo-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(99,102,241,0.06), rgba(236,72,153,0.04));
    opacity: 0;
    transition: opacity 0.3s;
}
.somo-card:hover { transform: translateY(-6px); border-color: rgba(99,102,241,0.5); box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px rgba(99,102,241,0.1); }
.somo-card:hover::before { opacity: 1; }
.card-icon { font-size: 36px; margin-bottom: 14px; display: block; filter: drop-shadow(0 4px 12px rgba(99,102,241,0.4)); }
.card-title { font-size: 15px; font-weight: 700; color: #e2e8f0; margin-bottom: 6px; }
.card-desc { font-size: 12px; color: #475569; line-height: 1.5; }

/* Colored card variants */
.card-v1 { border-color: rgba(99,102,241,0.2); }
.card-v1:hover { border-color: rgba(99,102,241,0.6); box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px rgba(99,102,241,0.15); }
.card-v2 { border-color: rgba(16,185,129,0.2); }
.card-v2:hover { border-color: rgba(16,185,129,0.6); box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px rgba(16,185,129,0.15); }
.card-v3 { border-color: rgba(245,158,11,0.2); }
.card-v3:hover { border-color: rgba(245,158,11,0.6); box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px rgba(245,158,11,0.15); }
.card-v4 { border-color: rgba(244,63,94,0.2); }
.card-v4:hover { border-color: rgba(244,63,94,0.6); box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px rgba(244,63,94,0.15); }
.card-v5 { border-color: rgba(6,182,212,0.2); }
.card-v5:hover { border-color: rgba(6,182,212,0.6); box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px rgba(6,182,212,0.15); }
.card-v6 { border-color: rgba(168,85,247,0.2); }
.card-v6:hover { border-color: rgba(168,85,247,0.6); box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px rgba(168,85,247,0.15); }

/* ══════════════════════════════════════
   STAT CARDS
══════════════════════════════════════ */
.stat-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px,1fr)); gap: 12px; margin-bottom: 28px; }
.stat-box {
    background: linear-gradient(145deg, #12121e, #0e0e1c);
    border: 1px solid rgba(99,102,241,0.12);
    border-radius: 14px;
    padding: 18px 16px;
    text-align: center;
}
.stat-val { font-size: 30px; font-weight: 900; color: #f1f5f9; line-height: 1; }
.stat-lbl { font-size: 11px; font-weight: 600; color: #475569; margin-top: 6px; text-transform: uppercase; letter-spacing: 1px; }
.stat-icon { font-size: 22px; margin-bottom: 8px; }

/* ══════════════════════════════════════
   DIVIDER
══════════════════════════════════════ */
.somo-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent);
    margin: 28px 0;
    border: none;
}

/* ══════════════════════════════════════
   GLASS PANEL
══════════════════════════════════════ */
.glass-panel {
    background: rgba(15,15,30,0.6);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 18px;
    padding: 28px;
}

/* ══════════════════════════════════════
   CHAT MESSAGES
══════════════════════════════════════ */
.stChatMessage {
    background: linear-gradient(145deg, #12121e, #0e0e1c) !important;
    border: 1px solid rgba(99,102,241,0.12) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    margin: 6px 0 !important;
    color: #e2e8f0 !important;
}
.stChatMessage p, .stChatMessage span, .stChatMessage li { color: #e2e8f0 !important; }
.stChatMessage code { background: rgba(99,102,241,0.15) !important; color: #a5b4fc !important; border-radius: 4px; padding: 1px 6px; }
.stChatMessage pre { background: #080814 !important; border: 1px solid rgba(99,102,241,0.2) !important; border-radius: 10px !important; }

/* Chat input */
.stChatInputContainer, [data-testid="stChatInput"] {
    background: #0d0d1a !important;
    border-top: 1px solid rgba(99,102,241,0.2) !important;
}
.stChatInputContainer textarea {
    background: #12121e !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stChatInputContainer textarea::placeholder { color: #475569 !important; }
.stChatInputContainer textarea:focus { border-color: rgba(99,102,241,0.6) !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important; outline: none !important; }

/* ══════════════════════════════════════
   STREAMLIT FORM ELEMENTS
══════════════════════════════════════ */
/* Text inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox select,
div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
    background: #12121e !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
    outline: none !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #475569 !important; }

/* Labels */
.stTextInput label, .stTextArea label, .stSelectbox label,
.stSlider label, .stFileUploader label, .stCheckbox label,
[data-testid="stWidgetLabel"] { color: #94a3b8 !important; font-size: 13px !important; font-weight: 600 !important; }

/* Selectbox */
div[data-baseweb="select"] > div {
    background: #12121e !important;
    border-color: rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
div[data-baseweb="select"] svg { fill: #64748b !important; }
div[data-baseweb="popover"] { background: #13131f !important; border: 1px solid rgba(99,102,241,0.3) !important; border-radius: 12px !important; }
div[data-baseweb="popover"] li { color: #e2e8f0 !important; }
div[data-baseweb="popover"] li:hover { background: rgba(99,102,241,0.15) !important; }

/* Slider */
.stSlider [data-baseweb="slider"] div[role="slider"] { background: #6366f1 !important; border-color: #4f46e5 !important; box-shadow: 0 0 12px rgba(99,102,241,0.5) !important; }
.stSlider [data-baseweb="slider"] div[data-testid="stTickBarMin"],
.stSlider [data-baseweb="slider"] div[data-testid="stTickBarMax"] { color: #475569 !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(99,102,241,0.04) !important;
    border: 2px dashed rgba(99,102,241,0.3) !important;
    border-radius: 14px !important;
    padding: 20px !important;
    transition: 0.3s;
}
[data-testid="stFileUploader"]:hover { border-color: rgba(99,102,241,0.6) !important; background: rgba(99,102,241,0.08) !important; }
[data-testid="stFileUploader"] * { color: #94a3b8 !important; }

/* Checkbox */
.stCheckbox [data-baseweb="checkbox"] div { border-color: rgba(99,102,241,0.4) !important; background: transparent !important; border-radius: 5px !important; }
.stCheckbox [data-baseweb="checkbox"] div[aria-checked="true"] { background: #6366f1 !important; border-color: #6366f1 !important; }

/* ══════════════════════════════════════
   BUTTONS — main area
══════════════════════════════════════ */
.stButton > button {
    background: rgba(99,102,241,0.08) !important;
    color: #a5b4fc !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    background: rgba(99,102,241,0.18) !important;
    border-color: rgba(99,102,241,0.5) !important;
    color: #c7d2fe !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(99,102,241,0.2) !important;
}
.stButton > button[kind="primary"],
.stButton > button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border-color: transparent !important;
    box-shadow: 0 0 25px rgba(99,102,241,0.35) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[kind="primaryFormSubmit"]:hover {
    background: linear-gradient(135deg, #4338ca, #6d28d9) !important;
    box-shadow: 0 8px 30px rgba(99,102,241,0.5) !important;
    transform: translateY(-3px) !important;
}

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 20px rgba(16,185,129,0.35) !important;
    transition: all 0.25s !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 30px rgba(16,185,129,0.5) !important;
}

/* ══════════════════════════════════════
   TABS
══════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 6px !important; border-bottom: 1px solid rgba(99,102,241,0.15) !important; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: #475569 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    border-radius: 8px 8px 0 0 !important;
    transition: 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #a5b4fc !important; background: rgba(99,102,241,0.08) !important; }
.stTabs [aria-selected="true"][data-baseweb="tab"] { color: #818cf8 !important; border-bottom: 2px solid #6366f1 !important; }
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding: 20px 0 !important; }

/* ══════════════════════════════════════
   EXPANDER
══════════════════════════════════════ */
.streamlit-expanderHeader {
    background: #12121e !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    background: #0f0f1e !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    color: #cbd5e1 !important;
}

/* ══════════════════════════════════════
   FORMS
══════════════════════════════════════ */
[data-testid="stForm"] {
    background: linear-gradient(145deg, #10101e, #0d0d1a) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 18px !important;
    padding: 28px !important;
}
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border: none !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.35) !important;
}

/* ══════════════════════════════════════
   METRICS
══════════════════════════════════════ */
[data-testid="stMetric"] {
    background: #12121e !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
    border-radius: 14px !important;
    padding: 18px !important;
}
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 12px !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 1px !important; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-weight: 900 !important; font-size: 28px !important; }

/* ══════════════════════════════════════
   DATAFRAME
══════════════════════════════════════ */
.stDataFrame, iframe { border-radius: 12px !important; border: 1px solid rgba(99,102,241,0.15) !important; }

/* ══════════════════════════════════════
   SUCCESS / WARNING / ERROR / INFO
══════════════════════════════════════ */
.stSuccess > div { background: rgba(16,185,129,0.1) !important; border: 1px solid rgba(16,185,129,0.3) !important; border-radius: 10px !important; color: #6ee7b7 !important; }
.stWarning > div { background: rgba(245,158,11,0.1) !important; border: 1px solid rgba(245,158,11,0.3) !important; border-radius: 10px !important; color: #fcd34d !important; }
.stError > div { background: rgba(244,63,94,0.1) !important; border: 1px solid rgba(244,63,94,0.3) !important; border-radius: 10px !important; color: #fca5a5 !important; }
.stInfo > div { background: rgba(99,102,241,0.1) !important; border: 1px solid rgba(99,102,241,0.3) !important; border-radius: 10px !important; color: #a5b4fc !important; }

/* ══════════════════════════════════════
   CODE BLOCK
══════════════════════════════════════ */
.stCode, [data-testid="stCode"] {
    background: #080814 !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important;
}
.stCode code { color: #e2e8f0 !important; font-size: 13px !important; }

/* ══════════════════════════════════════
   CUSTOM NOTIFICATION
══════════════════════════════════════ */
.somo-notify {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1));
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 12px;
    padding: 14px 20px;
    color: #c7d2fe;
    font-weight: 600;
    font-size: 14px;
    margin: 12px 0;
    animation: notify-in 0.4s ease;
}
@keyframes notify-in { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }

.somo-success {
    background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(5,150,105,0.1));
    border: 1px solid rgba(16,185,129,0.35);
    color: #6ee7b7;
    border-radius: 12px; padding: 14px 20px; font-weight: 600; font-size: 14px; margin: 12px 0;
}

/* ══════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════ */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #4f46e5, #7c3aed, #ec4899) !important;
    border-radius: 10px !important;
}
.stProgress > div > div {
    background: rgba(99,102,241,0.15) !important;
    border-radius: 10px !important;
}

/* ══════════════════════════════════════
   SELECT SLIDER
══════════════════════════════════════ */
.stSelectSlider [data-baseweb="slider"] { color: #a5b4fc !important; }

/* ══════════════════════════════════════
   TEMPLATE CARDS
══════════════════════════════════════ */
.tmpl-card {
    background: linear-gradient(145deg, #13131f, #0f0f1e);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 14px;
    transition: all 0.25s;
}
.tmpl-card:hover { border-color: rgba(99,102,241,0.45); transform: translateY(-3px); box-shadow: 0 12px 30px rgba(0,0,0,0.4); }
.tmpl-tag {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}
.tag-excel { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
.tag-word  { background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }
.tag-code  { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.tag-html  { background: rgba(244,63,94,0.15);  color: #fb7185; border: 1px solid rgba(244,63,94,0.3); }
.tag-csv   { background: rgba(168,85,247,0.15); color: #c084fc; border: 1px solid rgba(168,85,247,0.3); }
.tmpl-title { font-size: 15px; font-weight: 700; color: #e2e8f0; margin-bottom: 5px; }
.tmpl-desc  { font-size: 12px; color: #475569; line-height: 1.5; }

/* ══════════════════════════════════════
   HISTORY MESSAGE
══════════════════════════════════════ */
.hist-msg {
    border-left: 3px solid;
    border-radius: 0 12px 12px 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 13px;
}
.hist-user { background: rgba(99,102,241,0.08); border-color: #6366f1; }
.hist-ai   { background: rgba(16,185,129,0.07); border-color: #10b981; }
.hist-role { font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px; }
.hist-user .hist-role { color: #818cf8; }
.hist-ai   .hist-role { color: #34d399; }
.hist-body { color: #94a3b8; line-height: 1.5; }

/* ══════════════════════════════════════
   PROFILE STATS
══════════════════════════════════════ */
.profile-stat {
    background: linear-gradient(145deg, #13131f, #0e0e1c);
    border: 1px solid rgba(99,102,241,0.12);
    border-radius: 14px;
    padding: 22px 18px;
    text-align: center;
}
.p-stat-icon { font-size: 28px; margin-bottom: 10px; }
.p-stat-val  { font-size: 32px; font-weight: 900; color: #f1f5f9; }
.p-stat-lbl  { font-size: 11px; color: #475569; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-top: 4px; }

/* ══════════════════════════════════════
   FOOTER
══════════════════════════════════════ */
.somo-footer {
    text-align: center;
    padding: 40px 20px 20px;
    border-top: 1px solid rgba(99,102,241,0.15);
    margin-top: 60px;
}
.somo-footer .f-title { font-size: 18px; font-weight: 800; color: #e2e8f0; margin-bottom: 8px; }
.somo-footer .f-sub   { font-size: 13px; color: #475569; margin-bottom: 6px; }
.somo-footer .f-copy  { font-size: 11px; color: #334155; margin-top: 16px; }

/* ── MOBILE ── */
@media(max-width:768px) {
    section[data-testid="stMainBlockContainer"] { padding: 12px 14px 40px !important; }
    .somo-hero { padding: 32px 20px; }
    .somo-hero h1 { font-size: 24px; }
    .cards-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# DB & AI CONNECTIONS
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def get_connections():
    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        user_sheet = ss.sheet1
        try:
            chat_sheet = ss.worksheet("ChatHistory")
        except:
            chat_sheet = ss.add_worksheet("ChatHistory", 5000, 5)
            chat_sheet.append_row(["Timestamp","Username","Role","Message","Intent"])
        try:
            fb_sheet = ss.worksheet("Letters")
        except:
            fb_sheet = ss.add_worksheet("Letters", 1000, 8)
            fb_sheet.append_row(["Timestamp","Username","Rating","Category","Message","Email","Status","Files"])
        return user_sheet, chat_sheet, fb_sheet
    except Exception as e:
        st.error(f"❌ Baza xatosi: {e}")
        return None, None, None

user_db, chat_db, fb_db = get_connections()

try:
    ai = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    ai = None

# ══════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

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

def call_ai(messages, temperature=0.6, max_tokens=3000):
    if not ai:
        return "❌ AI xizmati mavjud emas."
    try:
        resp = ai.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ Xatolik: {e}"

def db_log(user, role, content, intent="chat"):
    if chat_db:
        try:
            chat_db.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user, role, content[:400], intent
            ])
        except: pass

# ══════════════════════════════════════════════════════════════════
# INTENT DETECTION
# ══════════════════════════════════════════════════════════════════
def detect_intent(text):
    t = text.lower()
    if any(k in t for k in ["excel","xlsx","jadval","byudjet","budget","spreadsheet",
           "finance","moliya","ombor","inventory","hisobot","salary","ish haqi",
           "sotish","savdo","xarajat","daromad","oylik reja","jadval tuz","grafik","formula"]):
        return "excel"
    if any(k in t for k in ["word","docx","hujjat","rezyume","resume","cv","shartnoma",
           "contract","ariza","maktub","letter","kurs ishi","referat","essay","diplom",
           "biznes reja","business plan","taqdimot matni","hisobot yoz"]):
        return "word"
    if any(k in t for k in ["html","website","veb sahifa","landing page","web page"]):
        return "html"
    if any(k in t for k in ["csv","comma separated","dataset"]):
        return "csv"
    if any(k in t for k in ["python kodi","kod yoz","dastur yaz","script yoz","bot yaz",
           "write code","function yoz","class yoz"]):
        return "code"
    return "chat"

# ══════════════════════════════════════════════════════════════════
# FILE GENERATORS
# ══════════════════════════════════════════════════════════════════
def gen_excel(prompt, temp=0.2):
    if not HAS_OPENPYXL:
        return None, "openpyxl o'rnatilmagan"
    sys_p = """Sen Excel fayl strukturasi uchun JSON qaytaruvchi ekspertsan.
FAQAT quyidagi JSON formatini qaytar, boshqa hech narsa yozma:
{
  "title": "Fayl nomi",
  "sheets": [
    {
      "name": "Varaq nomi",
      "headers": ["H1","H2","H3"],
      "header_color": "4F46E5",
      "rows": [
        ["v1","v2","=SUM(B3:B12)"]
      ],
      "col_widths": [25,15,18],
      "row_height": 20
    }
  ]
}
Qoidalar:
- Kamida 12-18 satr haqiqiy ma'lumot bilan to'ldir
- Excel formulalar ishlat: SUM, AVERAGE, IF, MAX, MIN, VLOOKUP
- Har bir varaq foydali va ma'noli bo'lsin
- FAQAT JSON qaytargin, markdown yo'q, izoh yo'q"""

    raw = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temp, max_tokens=4000)
    raw = re.sub(r'```json|```', '', raw).strip()
    m = re.search(r'\{.*\}', raw, re.DOTALL)
    if not m: return None, "JSON topilmadi"
    try: data = json.loads(m.group())
    except:
        try: data = json.loads(raw)
        except Exception as e: return None, f"JSON: {e}"

    wb = Workbook()
    wb.remove(wb.active)
    PALETTES = [
        ("4F46E5","EEF2FF"), ("059669","ECFDF5"), ("D97706","FFFBEB"),
        ("DC2626","FEF2F2"), ("0891B2","ECFEFF"), ("7C3AED","F5F3FF")
    ]
    for si, sh in enumerate(data.get("sheets", [])):
        ws = wb.create_sheet(title=sh.get("name","Sheet")[:31])
        headers  = sh.get("headers", [])
        hcolor   = sh.get("header_color", PALETTES[si%len(PALETTES)][0])
        _, rcolor = PALETTES[si%len(PALETTES)]
        rows     = sh.get("rows", [])
        widths   = sh.get("col_widths", [])
        rh       = sh.get("row_height", 20)

        # Title row
        if headers:
            end_col = max(len(headers), 1)
            ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_col)
            tc = ws.cell(row=1, column=1, value=sh.get("name","Hisobot"))
            tc.font = Font(name="Calibri", bold=True, size=13, color="FFFFFF")
            tc.fill = PatternFill("solid", fgColor=hcolor)
            tc.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 30

        # Headers row
        if headers:
            th = Side(style="medium", color="FFFFFF")
            for ci, h in enumerate(headers, 1):
                c = ws.cell(row=2, column=ci, value=h)
                c.font = Font(name="Calibri", bold=True, size=11, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor=hcolor)
                c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                c.border = Border(left=th, right=th, top=th, bottom=th)
            ws.row_dimensions[2].height = 24

        # Data rows
        td = Side(style="thin", color="D1D5DB")
        for ri, row in enumerate(rows, 3):
            bg = "FFFFFF" if ri % 2 else rcolor
            for ci, val in enumerate(row, 1):
                c = ws.cell(row=ri, column=ci)
                if isinstance(val, str) and val.startswith("="):
                    c.value = val
                else:
                    try:
                        if isinstance(val, str) and re.match(r'^-?\d+(\.\d+)?$', val.strip()):
                            c.value = float(val)
                            if float(val) == int(float(val)):
                                c.value = int(float(val))
                        else:
                            c.value = val
                    except: c.value = val
                c.fill = PatternFill("solid", fgColor=bg)
                c.border = Border(left=td, right=td, top=td, bottom=td)
                c.font = Font(name="Calibri", size=10)
                c.alignment = Alignment(vertical="center", wrap_text=True)
            ws.row_dimensions[ri].height = rh

        # Column widths
        for ci, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(ci)].width = max(int(w), 8)
        if not widths and headers:
            for ci in range(1, len(headers)+1):
                ws.column_dimensions[get_column_letter(ci)].width = 18

        # Freeze panes
        ws.freeze_panes = "A3"

    if not wb.sheetnames:
        wb.create_sheet("Ma'lumotlar")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    safe = re.sub(r'[^\w\s-]', '', data.get("title","somo")).strip().replace(' ','_')
    fname = f"{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return buf.getvalue(), fname


def gen_word(prompt, temp=0.4):
    if not HAS_DOCX:
        return None, "python-docx o'rnatilmagan"
    sys_p = """Sen professional Word hujjat strukturasi JSON qaytaruvchi ekspertsan.
FAQAT JSON qaytargin:
{
  "title": "Hujjat sarlavhasi",
  "sections": [
    {"type":"heading1","text":"Sarlavha"},
    {"type":"heading2","text":"Kichik sarlavha"},
    {"type":"paragraph","text":"Matn..."},
    {"type":"bullet","items":["1","2","3"]},
    {"type":"numbered","items":["a","b","c"]},
    {"type":"table","headers":["Ustun1","Ustun2"],"rows":[["v1","v2"]]}
  ]
}
Muhim: Mazmunli, haqiqiy va to'liq kontent. Kamida 8-12 bo'lim. Faqat JSON."""

    raw = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temp, max_tokens=4000)
    raw = re.sub(r'```json|```', '', raw).strip()
    m = re.search(r'\{.*\}', raw, re.DOTALL)
    if not m: return None, "Struktura topilmadi"
    try: data = json.loads(m.group())
    except Exception as e: return None, f"JSON: {e}"

    doc = Document()
    # Page margins
    for sec in doc.sections:
        sec.top_margin = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin = Cm(3)
        sec.right_margin = Cm(2.5)

    # Document title
    tp = doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = tp.add_run(data.get("title","Hujjat"))
    run.bold = True
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)
    run.font.name = "Calibri"
    tp.paragraph_format.space_after = Pt(4)

    # Date
    dp = doc.add_paragraph()
    dp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    dr = dp.add_run(f"{datetime.now().strftime('%d.%m.%Y')} — Somo AI")
    dr.font.size = Pt(10)
    dr.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
    dr.font.name = "Calibri"
    dp.paragraph_format.space_after = Pt(18)

    for sec in data.get("sections", []):
        t = sec.get("type","paragraph")
        if t == "heading1":
            h = doc.add_heading(sec.get("text",""), level=1)
            h.runs[0].font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)
            h.runs[0].font.name = "Calibri"
        elif t == "heading2":
            h = doc.add_heading(sec.get("text",""), level=2)
            h.runs[0].font.color.rgb = RGBColor(0x7C, 0x3A, 0xED)
            h.runs[0].font.name = "Calibri"
        elif t == "heading3":
            h = doc.add_heading(sec.get("text",""), level=3)
            h.runs[0].font.color.rgb = RGBColor(0x0E, 0xA5, 0xE9)
            h.runs[0].font.name = "Calibri"
        elif t == "paragraph":
            p = doc.add_paragraph()
            r = p.add_run(sec.get("text",""))
            r.font.size = Pt(11)
            r.font.name = "Calibri"
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = Pt(16)
        elif t == "bullet":
            for item in sec.get("items", []):
                p = doc.add_paragraph(style='List Bullet')
                r = p.add_run(item)
                r.font.size = Pt(11)
                r.font.name = "Calibri"
        elif t == "numbered":
            for item in sec.get("items", []):
                p = doc.add_paragraph(style='List Number')
                r = p.add_run(item)
                r.font.size = Pt(11)
                r.font.name = "Calibri"
        elif t == "table":
            headers_ = sec.get("headers", [])
            rows_ = sec.get("rows", [])
            if headers_:
                tbl = doc.add_table(rows=1+len(rows_), cols=len(headers_))
                tbl.style = 'Table Grid'
                hrow = tbl.rows[0]
                for ci, h in enumerate(headers_):
                    cell = hrow.cells[ci]
                    cell.text = h
                    cell.paragraphs[0].runs[0].font.bold = True
                    cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255,255,255)
                    cell.paragraphs[0].runs[0].font.name = "Calibri"
                    cell.paragraphs[0].runs[0].font.size = Pt(10)
                    from docx.oxml.ns import qn
                    from docx.oxml import OxmlElement
                    tcPr = cell._tc.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:val'),'clear')
                    shd.set(qn('w:color'),'auto')
                    shd.set(qn('w:fill'),'4F46E5')
                    tcPr.append(shd)
                for ri, rdata in enumerate(rows_):
                    rcells = tbl.rows[ri+1].cells
                    for ci, val in enumerate(rdata):
                        if ci < len(rcells):
                            rcells[ci].text = str(val)
                            rcells[ci].paragraphs[0].runs[0].font.size = Pt(10)
                            rcells[ci].paragraphs[0].runs[0].font.name = "Calibri"
                doc.add_paragraph()
        elif t == "divider":
            p = doc.add_paragraph("─"*60)
            p.runs[0].font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # Footer
    footer_sec = doc.sections[0].footer
    fp = footer_sec.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = fp.add_run(f"© {datetime.now().year} Somo AI Ultra Pro Max  |  {data.get('title','')}")
    fr.font.size = Pt(9)
    fr.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
    fr.font.name = "Calibri"

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    safe = re.sub(r'[^\w\s-]', '', data.get("title","somo")).strip().replace(' ','_')
    fname = f"{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    return buf.getvalue(), fname


def gen_code(prompt, temp=0.15):
    sys_p = """Sen tajribali Python dasturchi. Professional, to'liq ishlaydigan kod yoz.
FAQAT Python kodi ber — markdown, tushuntirma, izoh yo'q (kod ichidagi # izohlar yaxshi).
Kod clean, error handling bilan, best practices bo'yicha bo'lsin."""
    raw = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temp, max_tokens=3500)
    raw = re.sub(r'```python|```py|```', '', raw).strip()
    safe = re.sub(r'[^\w]','_', prompt[:30]).strip('_')
    return raw.encode('utf-8'), f"{safe}_{datetime.now().strftime('%H%M%S')}.py"


def gen_html(prompt, temp=0.5):
    sys_p = """Sen professional frontend developer. Chiroyli, zamonaviy, to'liq HTML/CSS/JS sahifa yarat.
Dark theme, Google Fonts, smooth animations, glassmorphism ishlat.
FAQAT HTML kodi ber, markdown yo'q."""
    raw = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temp, max_tokens=4000)
    raw = re.sub(r'```html|```', '', raw).strip()
    safe = re.sub(r'[^\w]','_', prompt[:25]).strip('_')
    return raw.encode('utf-8'), f"{safe}_{datetime.now().strftime('%H%M%S')}.html"


def gen_csv(prompt, temp=0.3):
    sys_p = """Sen ma'lumotlar mutaxassisi. Foydalanuvchi so'roviga asosan CSV formatda katta ma'lumot to'plami ber.
FAQAT CSV (vergul bilan ajratilgan) ber. Birinchi satr sarlavha. Kamida 25 satr.
Hech qanday tushuntirma, markdown yoki qo'shimcha matn yo'q."""
    raw = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temp, max_tokens=3000)
    raw = re.sub(r'```csv|```', '', raw).strip()
    safe = re.sub(r'[^\w]','_', prompt[:25]).strip('_')
    return raw.encode('utf-8'), f"{safe}_{datetime.now().strftime('%H%M%S')}.csv"

# ══════════════════════════════════════════════════════════════════
# DOWNLOAD HELPER
# ══════════════════════════════════════════════════════════════════
MIME = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "py":   "text/x-python",
    "html": "text/html",
    "csv":  "text/csv"
}

def download_block(file_bytes, fname, label):
    ext = fname.rsplit('.',1)[-1]
    mime = MIME.get(ext, "application/octet-stream")
    st.markdown(f'<div class="somo-success">✅ {label} fayl tayyor — yuklab olish uchun bosing</div>',
                unsafe_allow_html=True)
    st.download_button(f"⬇️  {fname}", file_bytes, fname, mime,
                       use_container_width=True, type="primary",
                       key=f"dl_{fname}_{time.time()}")

# ══════════════════════════════════════════════════════════════════
# SESSION RESTORE FROM COOKIE
# ══════════════════════════════════════════════════════════════════
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user and user_db:
        try:
            recs = user_db.get_all_records()
            ud = next((r for r in recs if str(r['username'])==session_user), None)
            if ud and str(ud.get('status','')).lower()=='active':
                st.session_state.update({'username':session_user,'logged_in':True,
                                          'login_time':datetime.now()})
            else:
                st.session_state.logged_in = False
        except: st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

def logout():
    try:
        cookies["somo_user_session"] = ""
        cookies.save()
    except: pass
    keys = list(st.session_state.keys())
    for k in keys: del st.session_state[k]
    st.session_state.logged_in = False
    st.rerun()

# ══════════════════════════════════════════════════════════════════
# ██████████████   LOGIN PAGE   ██████████████
# ══════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:

    st.markdown("""
    <div class="somo-hero" style="text-align:center; padding: 70px 40px;">
        <div class="somo-hero-content">
            <p style="font-size:13px;letter-spacing:3px;font-weight:700;color:#818cf8;margin-bottom:14px;text-transform:uppercase;">
                ✦ Kelajak texnologiyasi
            </p>
            <h1 style="font-size:clamp(36px,5vw,64px);font-weight:900;color:white;letter-spacing:-2px;margin-bottom:16px;">
                🌌 Somo AI
                <span class="g-text">Ultra Pro Max</span>
            </h1>
            <p style="font-size:18px;color:rgba(255,255,255,0.6);max-width:550px;margin:0 auto 28px;line-height:1.7;">
                Excel • Word • Kod • HTML • CSV — Har qanday faylni AI yordamida yarating
            </p>
            <div class="hero-badges" style="justify-content:center;">
                <span class="hero-badge">⚡ Llama 3.3 · 70B</span>
                <span class="hero-badge">📊 Excel Generator</span>
                <span class="hero-badge">📝 Word Generator</span>
                <span class="hero-badge">💻 Kod Generator</span>
                <span class="hero-badge">🌐 HTML Generator</span>
                <span class="hero-badge">🧠 Smart Chat</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards on login page
    st.markdown("""
    <div class="cards-grid">
        <div class="somo-card card-v1"><span class="card-icon">📊</span><div class="card-title">Excel Yaratish</div><div class="card-desc">Jadvallar, formulalar, grafiklar — AI bilan avtomatik</div></div>
        <div class="somo-card card-v2"><span class="card-icon">📝</span><div class="card-title">Word Hujjat</div><div class="card-desc">Rezyume, shartnoma, biznes reja — professional</div></div>
        <div class="somo-card card-v3"><span class="card-icon">💻</span><div class="card-title">Python Kod</div><div class="card-desc">To'liq ishlaydigan skriptlar, botlar, API-lar</div></div>
        <div class="somo-card card-v4"><span class="card-icon">🌐</span><div class="card-title">HTML Sahifa</div><div class="card-desc">Landing page, portfolio, dashboard — tayyor fayl</div></div>
        <div class="somo-card card-v5"><span class="card-icon">📋</span><div class="card-title">CSV Dataset</div><div class="card-desc">Katta ma'lumotlar to'plami — bitta so'rovda</div></div>
        <div class="somo-card card-v6"><span class="card-icon">🔍</span><div class="card-title">Hujjat Tahlili</div><div class="card-desc">PDF va Word fayllarni AI bilan tahlil qilish</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        t1, t2, t3 = st.tabs(["🔒  Kirish", "✍️  Ro'yxatdan o'tish", "ℹ️  Ma'lumot"])

        with t1:
            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                st.markdown('<p class="section-label">Hisobingizga kiring</p>', unsafe_allow_html=True)
                u = st.text_input("Username", placeholder="Username kiriting", key="lu")
                p = st.text_input("Parol", type="password", placeholder="Parolni kiriting", key="lp")
                r_col, b_col = st.columns([1,2])
                with r_col:
                    rem = st.checkbox("Eslab qolish", value=True)
                with b_col:
                    sub = st.form_submit_button("🚀  Kirish", use_container_width=True, type="primary")
                if sub and u and p:
                    if user_db:
                        try:
                            recs = user_db.get_all_records()
                            user = next((r for r in recs if str(r['username'])==u and str(r['password'])==hash_pw(p)), None)
                            if user:
                                if str(user.get('status','')).lower()=='blocked':
                                    st.error("🚫 Hisob bloklangan!")
                                else:
                                    st.session_state.update({'username':u,'logged_in':True,'login_time':datetime.now()})
                                    if rem:
                                        cookies["somo_user_session"] = u
                                        cookies.save()
                                    st.success("✅ Muvaffaqiyatli kirish!")
                                    time.sleep(0.4)
                                    st.rerun()
                            else:
                                st.error("❌ Login yoki parol noto'g'ri!")
                        except Exception as e:
                            st.error(f"❌ {e}")
                    else:
                        st.error("❌ Baza ulanmagan")
                elif sub:
                    st.warning("⚠️ Username va parolni kiriting")

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
                    if not agree:        st.error("❌ Shartlarga rozilik bering!")
                    elif len(nu)<3:      st.error("❌ Username kamida 3 belgi!")
                    elif len(np)<6:      st.error("❌ Parol kamida 6 belgi!")
                    elif np!=nc:         st.error("❌ Parollar mos emas!")
                    elif user_db:
                        try:
                            recs = user_db.get_all_records()
                            if any(r['username']==nu for r in recs):
                                st.error("❌ Bu username band!")
                            else:
                                user_db.append_row([nu, hash_pw(np), "active", str(datetime.now()), 0])
                                st.balloons()
                                st.success("🎉 Muvaffaqiyatli! Endi «Kirish» bo'limiga o'ting.")
                        except Exception as e:
                            st.error(f"❌ {e}")

        with t3:
            st.markdown("""
            <div style="padding: 8px 0;">
            <p class="section-label">Imkoniyatlar</p>
            <p style="color:#e2e8f0;font-weight:700;font-size:16px;margin-bottom:16px;">Somo AI Ultra Pro Max v3.0</p>

            <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);
                        border-radius:12px;padding:16px;margin-bottom:12px;">
                <p style="color:#818cf8;font-weight:700;font-size:13px;margin-bottom:8px;">📁 Fayl Generatorlari</p>
                <p style="color:#64748b;font-size:13px;line-height:1.8;">
                    📊 Excel — rang, formula, bir necha varaq<br>
                    📝 Word — sarlavha, jadval, bullet, footer<br>
                    💻 Python — to'liq ishlaydigan skript<br>
                    🌐 HTML — dark theme, animatsiya<br>
                    📋 CSV — katta datasetlar
                </p>
            </div>
            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
                        border-radius:12px;padding:16px;margin-bottom:12px;">
                <p style="color:#34d399;font-weight:700;font-size:13px;margin-bottom:8px;">🧠 AI Imkoniyatlar</p>
                <p style="color:#64748b;font-size:13px;line-height:1.8;">
                    ⚡ Llama 3.3 · 70B parametr<br>
                    🔍 Smart intent detection<br>
                    📄 PDF & DOCX tahlili<br>
                    🌐 Ko'p tilli javoblar
                </p>
            </div>

            <p style="color:#334155;font-size:12px;margin-top:16px;">
                📧 support@somoai.uz &nbsp;|&nbsp; 👨‍💻 Usmonov Sodiq &nbsp;|&nbsp; v3.0 (2026)
            </p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="somo-footer">
        <div class="f-title">🌌 Somo AI Ultra Pro Max</div>
        <div class="f-sub">Powered by Groq · Llama 3.3 70B · Python · Streamlit</div>
        <div class="f-copy">© 2026 Somo AI — Barcha huquqlar himoyalangan</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════
# SESSION DEFAULTS
# ══════════════════════════════════════════════════════════════════
DEFS = {
    'messages': [], 'total_msgs': 0, 'page': 'home',
    'uploaded_text': '', 'temp': 0.6, 'files_cnt': 0,
    'ai_style': 'Aqlli yordamchi', 'last_files': []
}
for k,v in DEFS.items():
    if k not in st.session_state: st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════
# ████████████  SIDEBAR  ████████████
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo + user
    uname = st.session_state.username
    st.markdown(f"""
    <div style="padding:24px 16px 20px;border-bottom:1px solid rgba(99,102,241,0.15);margin-bottom:8px;">
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">
            <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed,#ec4899);
                        width:46px;height:46px;border-radius:14px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:20px;font-weight:900;color:white;
                        box-shadow:0 0 20px rgba(99,102,241,0.4);flex-shrink:0;">
                {uname[0].upper()}
            </div>
            <div>
                <div style="font-size:15px;font-weight:700;color:#e2e8f0;">{uname}</div>
                <div style="font-size:11px;color:#10b981;font-weight:600;display:flex;align-items:center;gap:4px;">
                    <span style="background:#10b981;width:6px;height:6px;border-radius:50%;display:inline-block;"></span>
                    Aktiv
                </div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.15);
                        border-radius:10px;padding:10px;text-align:center;">
                <div style="font-size:18px;font-weight:900;color:#f1f5f9;">{len(st.session_state.messages)}</div>
                <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:1px;">Xabar</div>
            </div>
            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.15);
                        border-radius:10px;padding:10px;text-align:center;">
                <div style="font-size:18px;font-weight:900;color:#f1f5f9;">{st.session_state.files_cnt}</div>
                <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:1px;">Fayl</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    nav = [
        ("home",     "🏠", "Bosh sahifa"),
        ("chat",     "💬", "Chat AI"),
        ("excel",    "📊", "Excel Generator"),
        ("word",     "📝", "Word Generator"),
        ("code",     "💻", "Kod Generator"),
        ("html",     "🌐", "HTML Generator"),
        ("csv",      "📋", "CSV Generator"),
        ("templates","🎨", "Shablonlar"),
        ("analyze",  "🔍", "Hujjat Tahlili"),
        ("history",  "📜", "Chat Tarixi"),
        ("feedback", "💌", "Fikr bildirish"),
        ("profile",  "👤", "Profil"),
    ]

    st.markdown('<p class="section-label" style="padding: 6px 14px 4px;">Navigatsiya</p>', unsafe_allow_html=True)

    for pid, icon, label in nav:
        is_active = st.session_state.page == pid
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{icon}  {label}", key=f"nav_{pid}",
                     use_container_width=True, type=btn_type):
            st.session_state.page = pid
            st.rerun()

    st.markdown('<hr class="somo-divider" style="margin:10px 0;">', unsafe_allow_html=True)

    # Chat controls (only on chat page)
    if st.session_state.page == "chat":
        st.markdown('<p class="section-label" style="padding:0 14px 4px;">Chat Sozlamalari</p>', unsafe_allow_html=True)
        st.session_state.temp = st.slider("🌡  Ijodkorlik", 0.0, 1.0, st.session_state.temp, 0.05, key="temp_sl")
        st.session_state.ai_style = st.selectbox("🤖  AI uslubi",
            ["Aqlli yordamchi","Do'stona","Rasmiy ekspert","Ijodkor","Texnik"],
            key="ai_sl")
        if st.button("🗑  Chatni tozalash", use_container_width=True, key="clr_chat"):
            st.session_state.messages = []
            st.rerun()
        if st.session_state.messages:
            chat_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
            st.download_button("📥  JSON Export", chat_json.encode(),
                f"chat_{datetime.now():%Y%m%d}.json", use_container_width=True)

    st.markdown('<br>', unsafe_allow_html=True)
    if st.button("🚪  Tizimdan chiqish", use_container_width=True, type="primary", key="logout"):
        logout()

    st.markdown(f"""
    <div style="padding:14px 14px 8px;border-top:1px solid rgba(99,102,241,0.1);margin-top:8px;">
        <p style="font-size:10px;color:#334155;text-align:center;line-height:1.6;">
            🌌 Somo AI Ultra Pro Max<br>
            ⚡ Groq · Llama 3.3 · 70B<br>
            © 2026 Usmonov Sodiq
        </p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: HOME  ██████████
# ══════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    uname = st.session_state.username

    # Hero
    st.markdown(f"""
    <div class="somo-hero">
        <div class="somo-hero-content">
            <p style="font-size:12px;letter-spacing:3px;font-weight:700;color:#818cf8;margin-bottom:12px;text-transform:uppercase;">
                ✦ Somo AI Ultra Pro Max v3.0
            </p>
            <h1>Salom, <span class="g-text">{uname}</span>! 👋</h1>
            <p class="subtitle">
                Bugun nima yaratmoqchisiz? Excel jadval, Word hujjat, Python kod, HTML sahifa yoki shunchaki savol — hammasi shu yerda.
            </p>
            <div class="hero-badges">
                <span class="hero-badge">📊 Excel</span>
                <span class="hero-badge">📝 Word</span>
                <span class="hero-badge">💻 Kod</span>
                <span class="hero-badge">🌐 HTML</span>
                <span class="hero-badge">📋 CSV</span>
                <span class="hero-badge">🔍 Tahlil</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    mins = (datetime.now()-st.session_state.login_time).seconds//60 if 'login_time' in st.session_state else 0
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box">
            <div class="stat-icon">💬</div>
            <div class="stat-val">{len(st.session_state.messages)}</div>
            <div class="stat-lbl">Xabarlar</div>
        </div>
        <div class="stat-box">
            <div class="stat-icon">📁</div>
            <div class="stat-val">{st.session_state.files_cnt}</div>
            <div class="stat-lbl">Fayllar</div>
        </div>
        <div class="stat-box">
            <div class="stat-icon">⏱</div>
            <div class="stat-val">{mins}</div>
            <div class="stat-lbl">Daqiqa</div>
        </div>
        <div class="stat-box">
            <div class="stat-icon">🔥</div>
            <div class="stat-val">{max(1, len(st.session_state.messages)//5)}</div>
            <div class="stat-lbl">Daraja</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards grid — clickable navigation
    st.markdown('<p class="section-label">Funksiyalar</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Nima qilmoqchisiz?</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="cards-grid">
        <div class="somo-card card-v6"><span class="card-icon">💬</span>
            <div class="card-title">Chat AI</div>
            <div class="card-desc">Aqlli suhbat, savol-javob va fayl yaratish</div></div>
        <div class="somo-card card-v1"><span class="card-icon">📊</span>
            <div class="card-title">Excel Generator</div>
            <div class="card-desc">Ranglar, formulalar, bir necha varaqli jadvallar</div></div>
        <div class="somo-card card-v2"><span class="card-icon">📝</span>
            <div class="card-title">Word Generator</div>
            <div class="card-desc">Rezyume, shartnoma, biznes reja, hisobot</div></div>
        <div class="somo-card card-v3"><span class="card-icon">💻</span>
            <div class="card-title">Kod Generator</div>
            <div class="card-desc">Python bot, API, web scraper, ML model</div></div>
        <div class="somo-card card-v4"><span class="card-icon">🌐</span>
            <div class="card-title">HTML Generator</div>
            <div class="card-desc">Portfolio, landing page, dashboard sahifasi</div></div>
        <div class="somo-card card-v5"><span class="card-icon">📋</span>
            <div class="card-title">CSV Generator</div>
            <div class="card-desc">Katta ma'lumotlar to'plami — bir so'rovda</div></div>
        <div class="somo-card card-v6"><span class="card-icon">🎨</span>
            <div class="card-title">Shablonlar</div>
            <div class="card-desc">16 ta tayyor shablon — biznes, kod, ta'lim</div></div>
        <div class="somo-card card-v1"><span class="card-icon">🔍</span>
            <div class="card-title">Hujjat Tahlili</div>
            <div class="card-desc">PDF & DOCX fayllarni AI bilan tahlil qilish</div></div>
        <div class="somo-card card-v2"><span class="card-icon">📜</span>
            <div class="card-title">Chat Tarixi</div>
            <div class="card-desc">Barcha suhbatlar, qidirish va eksport</div></div>
        <div class="somo-card card-v3"><span class="card-icon">💌</span>
            <div class="card-title">Feedback</div>
            <div class="card-desc">Fikr-mulohazalaringizni yuboring</div></div>
        <div class="somo-card card-v4"><span class="card-icon">👤</span>
            <div class="card-title">Profil</div>
            <div class="card-desc">Hisob sozlamalari va statistika</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    # Quick actions
    st.markdown('<p class="section-label">Tezkor Harakatlar</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Shablonlardan Boshlang</p>', unsafe_allow_html=True)

    q1, q2, q3, q4 = st.columns(4)
    quick_items = [
        (q1, "📊", "Oylik Byudjet", "excel"),
        (q2, "📄", "Rezyume Yozish", "word"),
        (q3, "🤖", "Telegram Bot", "code"),
        (q4, "🌐", "Landing Page", "html"),
    ]
    for col, icon, label, page in quick_items:
        with col:
            if st.button(f"{icon}  {label}", use_container_width=True, key=f"quick_{page}"):
                st.session_state.page = page
                st.rerun()

    # Tips
    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:linear-gradient(145deg,rgba(99,102,241,0.06),rgba(139,92,246,0.04));
                border:1px solid rgba(99,102,241,0.15);border-radius:16px;padding:24px;margin-bottom:20px;">
        <p class="section-label">💡 Maslahatlar</p>
        <p class="section-title" style="font-size:18px;">Chat AI dan qanday foydalanish</p>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px;margin-top:16px;">
            <div>
                <p style="color:#818cf8;font-weight:700;font-size:13px;margin-bottom:6px;">📊 Excel uchun</p>
                <p style="color:#64748b;font-size:12px;line-height:1.7;">"Oylik byudjet Excel jadvali yarating" yoki "Xodimlar ish haqi jadvalini tuzing"</p>
            </div>
            <div>
                <p style="color:#34d399;font-weight:700;font-size:13px;margin-bottom:6px;">📝 Word uchun</p>
                <p style="color:#64748b;font-size:12px;line-height:1.7;">"Dasturchi uchun rezyume yozing" yoki "Ijara shartnomasi hujjati tayyorlang"</p>
            </div>
            <div>
                <p style="color:#fbbf24;font-weight:700;font-size:13px;margin-bottom:6px;">💻 Kod uchun</p>
                <p style="color:#64748b;font-size:12px;line-height:1.7;">"Telegram bot kodi yozing" yoki "FastAPI CRUD API yarating"</p>
            </div>
            <div>
                <p style="color:#f472b6;font-weight:700;font-size:13px;margin-bottom:6px;">🌐 HTML uchun</p>
                <p style="color:#64748b;font-size:12px;line-height:1.7;">"Portfolio sahifasi yarating" yoki "Zamonaviy landing page html kodi"</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: CHAT AI  ██████████
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "chat":

    # Hero
    st.markdown("""
    <div class="somo-hero">
        <div class="somo-hero-content">
            <p style="font-size:12px;letter-spacing:3px;font-weight:700;color:#818cf8;margin-bottom:10px;text-transform:uppercase;">
                ✦ Smart Chat
            </p>
            <h1>💬 Chat <span class="g-text">AI</span></h1>
            <p class="subtitle">
                So'zingizni yozing — AI tushunadi. Excel so'rang, Excel beradi. Word so'rang, Word beradi. Oddiy savol — aniq javob.
            </p>
            <div class="hero-badges">
                <span class="hero-badge">🧠 Smart Intent Detection</span>
                <span class="hero-badge">📊 Auto Excel</span>
                <span class="hero-badge">📝 Auto Word</span>
                <span class="hero-badge">💻 Auto Kod</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("""
        <div class="cards-grid" style="grid-template-columns:repeat(auto-fill,minmax(180px,1fr));">
            <div class="somo-card card-v1" style="padding:20px 14px;">
                <span class="card-icon" style="font-size:28px;">📊</span>
                <div class="card-title" style="font-size:13px;">"Oylik byudjet jadvali"</div>
                <div class="card-desc">Excel avtomatik yaratiladi</div></div>
            <div class="somo-card card-v2" style="padding:20px 14px;">
                <span class="card-icon" style="font-size:28px;">📝</span>
                <div class="card-title" style="font-size:13px;">"Rezyume yozing"</div>
                <div class="card-desc">Word fayl tayyorlanadi</div></div>
            <div class="somo-card card-v3" style="padding:20px 14px;">
                <span class="card-icon" style="font-size:28px;">💻</span>
                <div class="card-title" style="font-size:13px;">"Python kodi yozing"</div>
                <div class="card-desc">.py fayl yuklab olish</div></div>
            <div class="somo-card card-v4" style="padding:20px 14px;">
                <span class="card-icon" style="font-size:28px;">🌐</span>
                <div class="card-title" style="font-size:13px;">"Landing page yarat"</div>
                <div class="card-desc">HTML fayl tayyorlanadi</div></div>
            <div class="somo-card card-v5" style="padding:20px 14px;">
                <span class="card-icon" style="font-size:28px;">📋</span>
                <div class="card-title" style="font-size:13px;">"100 ta mahsulot CSV"</div>
                <div class="card-desc">Dataset yaratiladi</div></div>
            <div class="somo-card card-v6" style="padding:20px 14px;">
                <span class="card-icon" style="font-size:28px;">❓</span>
                <div class="card-title" style="font-size:13px;">"AI nima?"</div>
                <div class="card-desc">Matn javob beriladi</div></div>
        </div>
        """, unsafe_allow_html=True)

    # Chat tarixi
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "file_data" in msg:
                fd = msg["file_data"]
                download_block(fd["bytes"], fd["name"], fd["label"])

    # File upload (above chat input)
    with st.expander("📂  Hujjat yuklash (PDF yoki DOCX)", expanded=False):
        upl = st.file_uploader("Fayl tanlang", type=["pdf","docx"], key="chat_upload",
                               label_visibility="collapsed")
        if upl:
            with st.spinner("📄 O'qilmoqda..."):
                txt = process_doc(upl)
                st.session_state.uploaded_text = txt
            if txt:
                st.success(f"✅ {upl.name} — {len(txt):,} belgi")
            else:
                st.error("❌ O'qilmadi")

    # Chat input
    if prompt := st.chat_input("💭  Xabar yozing... (Excel, Word, Kod, HTML so'rasangiz — fayl avtomatik yaratiladi!)", key="chat_in"):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        db_log(st.session_state.username, "User", prompt, "input")

        intent = detect_intent(prompt)

        with st.chat_message("assistant"):
            styles_map = {
                "Aqlli yordamchi": "Sen Somo AI — aqlli, professional va foydali yordamchisan. Usmonov Sodiq yaratgan. Aniq, strukturali va foydali javoblar ber.",
                "Do'stona": "Sen Somo AI — do'stona, samimiy va quvnoq. Foydalanuvchi bilan yaxin do'stdek gaplash.",
                "Rasmiy ekspert": "Sen Somo AI — rasmiy, aniq va professional mutaxassis. Har doim batafsil va dalillangan javob ber.",
                "Ijodkor": "Sen Somo AI — ijodkor, original va noodatiy fikrlaydigan AI. Creative solutions taklif qil.",
                "Texnik": "Sen Somo AI — texnik ekspert. Kod, arxitektura va texnik detallar bo'yicha batafsil javob ber."
            }
            sys_base = styles_map.get(st.session_state.ai_style, styles_map["Aqlli yordamchi"])

            if intent in ("excel","word","html","csv","code"):
                GENERATORS = {
                    "excel": (gen_excel,  "📊 Excel fayl", "xlsx"),
                    "word":  (gen_word,   "📝 Word hujjat", "docx"),
                    "code":  (gen_code,   "💻 Python kodi", "py"),
                    "html":  (gen_html,   "🌐 HTML sahifa", "html"),
                    "csv":   (gen_csv,    "📋 CSV dataset", "csv"),
                }
                gfunc, glabel, gext = GENERATORS[intent]

                emoji_map = {"excel":"📊","word":"📝","code":"💻","html":"🌐","csv":"📋"}
                em = emoji_map[intent]
                st.markdown(f'<div class="somo-notify">{em}  {glabel} yaratilmoqda... Iltimos kuting (10-30 soniya)</div>',
                            unsafe_allow_html=True)
                progress = st.progress(0, text="AI ishlamoqda...")
                for i in range(0, 70, 15):
                    time.sleep(0.25)
                    progress.progress(i, text=f"Tayyorlanmoqda... {i}%")

                try:
                    fb, fn = gfunc(prompt, st.session_state.temp)
                    progress.progress(100, text="Tayyor!")
                    time.sleep(0.2)
                    progress.empty()

                    if fb and isinstance(fb, bytes):
                        resp_txt = f"✅ **{glabel}** muvaffaqiyatli yaratildi!\n\n📁 Fayl: `{fn}`\n\n⬇️ Quyidagi tugma orqali yuklab oling."
                        file_info = {"bytes":fb,"name":fn,"label":glabel}
                        st.markdown(resp_txt)
                        download_block(fb, fn, glabel)
                        st.session_state.files_cnt += 1
                        st.session_state.last_files.append(fn)
                        db_log("Somo AI","Assistant", resp_txt, intent)
                        msg_d = {"role":"assistant","content":resp_txt,"file_data":file_info}
                    else:
                        progress.empty()
                        resp_txt = f"❌ Xatolik yuz berdi: {fn}"
                        st.error(resp_txt)
                        msg_d = {"role":"assistant","content":resp_txt}
                except Exception as e:
                    progress.empty()
                    resp_txt = f"❌ Generator xatoligi: {e}"
                    st.error(resp_txt)
                    msg_d = {"role":"assistant","content":resp_txt}

                st.session_state.messages.append(msg_d)

            else:
                # Normal chat
                with st.spinner("🤔  O'ylayapman..."):
                    msgs = [{"role":"system","content":sys_base}]
                    if st.session_state.uploaded_text:
                        msgs.append({"role":"system","content":
                            f"Yuklangan hujjat mazmuni:\n{st.session_state.uploaded_text[:4000]}"})
                    for m in st.session_state.messages[-20:]:
                        msgs.append({"role":m["role"],"content":m["content"]})

                    response = call_ai(msgs, st.session_state.temp)
                    st.markdown(response)
                    db_log("Somo AI","Assistant", response, "chat")
                    st.session_state.messages.append({"role":"assistant","content":response})

        st.session_state.total_msgs += 1
        st.rerun()

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: EXCEL GENERATOR  ██████████
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "excel":

    st.markdown("""
    <div class="somo-hero">
        <div class="somo-hero-content">
            <p style="font-size:12px;letter-spacing:3px;font-weight:700;color:#34d399;margin-bottom:10px;text-transform:uppercase;">
                ✦ File Generator
            </p>
            <h1>📊 Excel <span class="g-text">Generator</span></h1>
            <p class="subtitle">Har qanday jadval, hisobot va ma'lumotlar bazasini AI bilan professional Excel faylga aylantiring.</p>
            <div class="hero-badges">
                <span class="hero-badge">✅ Formulalar</span>
                <span class="hero-badge">✅ Ranglar</span>
                <span class="hero-badge">✅ Bir necha varaq</span>
                <span class="hero-badge">✅ Freeze panes</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Example cards
    st.markdown('<p class="section-label">Namunalar — bosing va to\'ldiring</p>', unsafe_allow_html=True)

    xl_examples = [
        ("💰","Moliyaviy Byudjet","12 oylik moliyaviy byudjet jadvali: daromad manbalari, xarajatlar (ish haqi, ijara, reklama), foyda, formulalar"),
        ("📦","Inventar Ro'yxati","100 ta mahsulot inventar ro'yxati: ID, nomi, kategoriya, miqdori, narxi, jami qiymat, minimum zaxira"),
        ("👥","Xodimlar Jadvali","Kompaniya xodimlari ish haqi jadvali: ism, lavozim, bo'lim, maosh, bonus, soliq, sof maosh, bank raqami"),
        ("📈","Savdo Hisoboti","Oylik savdo hisoboti: har mahsulot uchun reja, haqiqat, farq, % bajarilish, reyting"),
        ("🎓","Talabalar Bahosi","30 ta talaba baholar jadvali: 6 ta fan, har bir fan uchun 3 ta baho, o'rtacha, reyting, davomat"),
        ("📅","Loyiha Jadvali","IT loyiha Gantt jadvali: vazifalar, mas'ul, boshlash sanasi, tugash sanasi, holat, % bajarilish"),
    ]

    cols_xl = st.columns(3)
    for i, (ico, title, full_prompt) in enumerate(xl_examples):
        with cols_xl[i%3]:
            if st.button(f"{ico}  {title}", key=f"xlq_{i}", use_container_width=True):
                st.session_state["xl_prompt"] = full_prompt

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    col_inp, col_opt = st.columns([3, 1])
    with col_inp:
        xl_prompt = st.text_area(
            "📝  Jadval tavsifi:",
            value=st.session_state.get("xl_prompt",""),
            placeholder="Masalan: 6 xodimlik IT kompaniya uchun oy bo'yicha ish haqi jadvali, bonuslar va soliq chegirmalari bilan...",
            height=140, key="xl_in"
        )
    with col_opt:
        xl_temp = st.slider("Aniqlik darajasi", 0.0, 0.6, 0.15, 0.05, key="xl_temp")
        add_summary = st.checkbox("📊 Xulosa varag'i", value=True)
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        gen_xl = st.button("🚀  Excel Yaratish", use_container_width=True, type="primary", key="gen_xl")

    if gen_xl:
        if not xl_prompt.strip():
            st.warning("⚠️  Jadval tavsifini kiriting!")
        else:
            full_prompt = xl_prompt
            if add_summary:
                full_prompt += "\n\nOxirida umumiy xulosa (Summary) varaqchasi ham qo'sh."
            with st.spinner(""):
                prog = st.progress(0)
                st.markdown('<div class="somo-notify">📊  Excel fayl yaratilmoqda... AI jadval strukturasini tayyorlamoqda</div>', unsafe_allow_html=True)
                for pct in range(0, 75, 12):
                    time.sleep(0.3)
                    prog.progress(pct)
                fb, fn = gen_excel(full_prompt, xl_temp)
                prog.progress(100)
                time.sleep(0.2)
                prog.empty()
                if fb and isinstance(fb, bytes):
                    st.session_state.files_cnt += 1
                    download_block(fb, fn, "Excel")
                else:
                    st.error(f"❌  {fn}")

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: WORD GENERATOR  ██████████
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "word":

    st.markdown("""
    <div class="somo-hero">
        <div class="somo-hero-content">
            <p style="font-size:12px;letter-spacing:3px;font-weight:700;color:#60a5fa;margin-bottom:10px;text-transform:uppercase;">
                ✦ File Generator
            </p>
            <h1>📝 Word <span class="g-text">Generator</span></h1>
            <p class="subtitle">Professional hujjatlarni — rezyume, shartnoma, hisobot, biznes reja — AI bilan bir soniyada yarating.</p>
            <div class="hero-badges">
                <span class="hero-badge">✅ Sarlavhalar</span>
                <span class="hero-badge">✅ Jadvallar</span>
                <span class="hero-badge">✅ Bullet lists</span>
                <span class="hero-badge">✅ Footer</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    wd_examples = [
        ("👤","Rezyume / CV","Python backend dasturchi uchun professional rezyume: shaxsiy ma'lumotlar, 4 yil tajriba, texnik ko'nikmalar, ta'lim, sertifikatlar, portfolio loyihalari"),
        ("🤝","Hamkorlik Xati","IT kompaniyalar o'rtasida hamkorlik taklifnomasi: kompaniya taqdimoti, taklif mazmuni, foyda va shartlar, imzo qismi"),
        ("📋","Ijara Shartnomasi","Turar joy ijara shartnomasi: tomonlar ma'lumoti, ob'ekt tavsifi, ijara muddati, to'lov shartlari, mas'uliyat, fors-major"),
        ("📖","Biznes Reja","Startap uchun to'liq biznes reja: ijroiya xulosa, bozor tahlili, mahsulot tavsifi, marketing, moliyaviy prognoz, risklar"),
        ("🎓","Kurs Ishi","Sun'iy intellekt va machine learning mavzusida kurs ishi: kirish, 3 bob, xulosa, adabiyotlar, 15+ sahifa"),
        ("📑","Buyruq / Qaror","Kompaniya direktori buyrug'i: xodim ishga qabul qilish, lavozimi, ish haqi, boshlanish sanasi, imzo joyi"),
    ]

    c1,c2,c3 = st.columns(3)
    c_wd = [c1,c2,c3]
    for i,(ico,title,fp) in enumerate(wd_examples):
        with c_wd[i%3]:
            if st.button(f"{ico}  {title}", key=f"wdq_{i}", use_container_width=True):
                st.session_state["wd_prompt"] = fp

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    wd_prompt = st.text_area("📝  Hujjat tavsifi:",
        value=st.session_state.get("wd_prompt",""),
        placeholder="Masalan: O'zbekistonda ro'yxatdan o'tgan IT kompaniya uchun dasturchi yollash bo'yicha mehnat shartnomasi...",
        height=140, key="wd_in")

    gen_wd = st.button("🚀  Word Hujjat Yaratish", use_container_width=True, type="primary", key="gen_wd")
    if gen_wd:
        if not wd_prompt.strip():
            st.warning("⚠️  Hujjat tavsifini kiriting!")
        else:
            with st.spinner(""):
                prog = st.progress(0)
                st.markdown('<div class="somo-notify">📝  Word hujjat yaratilmoqda... AI strukturani tayyorlamoqda</div>', unsafe_allow_html=True)
                for pct in range(0, 75, 15):
                    time.sleep(0.3)
                    prog.progress(pct)
                fb, fn = gen_word(wd_prompt)
                prog.progress(100)
                time.sleep(0.2)
                prog.empty()
                if fb and isinstance(fb, bytes):
                    st.session_state.files_cnt += 1
                    download_block(fb, fn, "Word")
                else:
                    st.error(f"❌  {fn}")

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: CODE GENERATOR  ██████████
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "code":

    st.markdown("""
    <div class="somo-hero">
        <div class="somo-hero-content">
            <p style="font-size:12px;letter-spacing:3px;font-weight:700;color:#fbbf24;margin-bottom:10px;text-transform:uppercase;">
                ✦ Code Generator
            </p>
            <h1>💻 Kod <span class="g-text">Generator</span></h1>
            <p class="subtitle">Professional Python kodi — error handling, izohlar va best practices bilan. To'g'ridan-to'g'ri .py fayl.</p>
            <div class="hero-badges">
                <span class="hero-badge">✅ Clean Code</span>
                <span class="hero-badge">✅ Error Handling</span>
                <span class="hero-badge">✅ Izohlar</span>
                <span class="hero-badge">✅ Best Practices</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    code_examples = [
        ("🤖","Telegram Bot","Aiogram v3 bilan Telegram bot: /start, /help komandalar, inline keyboard, callback handler, FSM holatlar, SQLite bazasi"),
        ("🌐","FastAPI CRUD","FastAPI da to'liq CRUD API: User modeli, PostgreSQL + SQLAlchemy, Pydantic, JWT autentifikatsiya, Swagger"),
        ("📊","Dashboard","Streamlit dashboard: CSV yuklash, pandas tahlili, plotly grafiklar, filter va qidiruv, PDF eksport"),
        ("🔍","Web Scraper","BeautifulSoup4 bilan web scraper: sahifa tahlili, ma'lumot ajratish, CSV saqlash, rotating proxy, delay"),
        ("🤖","ML Model","Scikit-learn bilan classification model: ma'lumot tayyorlash, model train, hyperparameter tuning, accuracy hisobot"),
        ("📧","Email Sender","Python smtplib email yuboruvchi: HTML template, attachment, bulk send, queue, retry mexanizmi"),
    ]

    c1,c2,c3 = st.columns(3)
    cc = [c1,c2,c3]
    for i,(ico,title,fp) in enumerate(code_examples):
        with cc[i%3]:
            if st.button(f"{ico}  {title}", key=f"cq_{i}", use_container_width=True):
                st.session_state["cd_prompt"] = fp

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    col_cd, col_co = st.columns([3,1])
    with col_cd:
        cd_prompt = st.text_area("📝  Kod tavsifi:",
            value=st.session_state.get("cd_prompt",""),
            placeholder="Masalan: Telegram bot yozing — foydalanuvchi narx so'raganda Olx.uz dan avtomatik qidirsin...",
            height=140, key="cd_in")
    with col_co:
        cd_temp = st.slider("Ijodkorlik", 0.0, 0.5, 0.1, 0.05, key="cd_temp")
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        gen_cd = st.button("🚀  Kod Yaratish", use_container_width=True, type="primary", key="gen_cd")

    if gen_cd:
        if not cd_prompt.strip():
            st.warning("⚠️  Kod tavsifini kiriting!")
        else:
            with st.spinner("💻  Kod yozilmoqda..."):
                prog = st.progress(0)
                st.markdown('<div class="somo-notify">💻  Python kodi yozilmoqda... AI eng yaxshi yechimni tayyorlamoqda</div>', unsafe_allow_html=True)
                for pct in range(0, 65, 15):
                    time.sleep(0.25)
                    prog.progress(pct)
                fb, fn = gen_code(cd_prompt, cd_temp)
                prog.progress(100)
                prog.empty()
                code_txt = fb.decode('utf-8')
                st.session_state.files_cnt += 1
                st.markdown('<div class="somo-success">✅  Kod tayyor — preview va yuklab olish quyida</div>', unsafe_allow_html=True)
                with st.expander("👁  Kod Preview", expanded=True):
                    st.code(code_txt, language="python")
                st.download_button("⬇️  .py Fayl Yuklab Olish", fb, fn,
                                   "text/x-python", use_container_width=True, type="primary")

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: HTML GENERATOR  ██████████
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "html":

    st.markdown("""
    <div class="somo-hero">
        <div class="somo-hero-content">
            <p style="font-size:12px;letter-spacing:3px;font-weight:700;color:#fb7185;margin-bottom:10px;text-transform:uppercase;">
                ✦ HTML Generator
            </p>
            <h1>🌐 HTML <span class="g-text">Generator</span></h1>
            <p class="subtitle">Zamonaviy, animatsiyali veb sahifalar — CSS, JavaScript bilan. Bitta .html faylda hamma narsa.</p>
            <div class="hero-badges">
                <span class="hero-badge">✅ Dark Theme</span>
                <span class="hero-badge">✅ Animatsiyalar</span>
                <span class="hero-badge">✅ Google Fonts</span>
                <span class="hero-badge">✅ Responsive</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    html_examples = [
        ("🎨","Portfolio","Web developer portfolio sahifasi: hero, about, skills, projects, contact — dark theme, smooth scroll, glassmorphism"),
        ("🛒","Mahsulot Sahifasi","E-commerce mahsulot sahifasi: gallery, narx, rangling, miqdor, add to cart, reviews — minimal zamonaviy dizayn"),
        ("📊","Analytics Dashboard","Ma'lumotlar dashboard: sidebar nav, stat cards, chart placeholders, dark glassmorphism, animated counters"),
        ("🎪","Event Landing","Konferensiya/event landing page: hero countdown, speakers, schedule, tickets, parallax scroll effekti"),
        ("🔐","Login Sahifa","Zamonaviy login/register sahifasi: glassmorphism card, validation, particles background, smooth transitions"),
        ("📰","Blog Post","Zamonaviy blog maqola sahifasi: hero image, typography, table of contents, code blocks, dark/light toggle"),
    ]

    c1,c2,c3 = st.columns(3)
    ch = [c1,c2,c3]
    for i,(ico,title,fp) in enumerate(html_examples):
        with ch[i%3]:
            if st.button(f"{ico}  {title}", key=f"hq_{i}", use_container_width=True):
                st.session_state["ht_prompt"] = fp

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    ht_prompt = st.text_area("📝  Sahifa tavsifi:",
        value=st.session_state.get("ht_prompt",""),
        placeholder="Masalan: AI kompaniyasi uchun zamonaviy landing page — hero, features, pricing, CTA — dark neon dizayn...",
        height=140, key="ht_in")

    gen_ht = st.button("🚀  HTML Yaratish", use_container_width=True, type="primary", key="gen_ht")
    if gen_ht:
        if not ht_prompt.strip():
            st.warning("⚠️  Sahifa tavsifini kiriting!")
        else:
            with st.spinner(""):
                prog = st.progress(0)
                st.markdown('<div class="somo-notify">🌐  HTML sahifa yaratilmoqda... AI dizayn va kod tayyorlamoqda</div>', unsafe_allow_html=True)
                for pct in range(0, 70, 14):
                    time.sleep(0.3)
                    prog.progress(pct)
                fb, fn = gen_html(ht_prompt, 0.5)
                prog.progress(100)
                prog.empty()
                html_txt = fb.decode('utf-8')
                st.session_state.files_cnt += 1
                st.markdown('<div class="somo-success">✅  HTML sahifa tayyor! Faylni yuklab, brauzerda oching.</div>', unsafe_allow_html=True)
                with st.expander("👁  HTML Kod Preview"):
                    st.code(html_txt[:3000]+("..." if len(html_txt)>3000 else ""), language="html")
                st.download_button("⬇️  HTML Fayl Yuklab Olish", fb, fn,
                                   "text/html", use_container_width=True, type="primary")
                st.info("💡  Faylni yuklab oling va ikki marta bosib brauzerda oching")

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: CSV GENERATOR  ██████████
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "csv":

    st.markdown("""
    <div class="somo-hero">
        <div class="somo-hero-content">
            <p style="font-size:12px;letter-spacing:3px;font-weight:700;color:#c084fc;margin-bottom:10px;text-transform:uppercase;">
                ✦ Data Generator
            </p>
            <h1>📋 CSV <span class="g-text">Generator</span></h1>
            <p class="subtitle">Katta ma'lumotlar to'plamini — test data, namuna dataset, amaliy ma'lumotlar — bir so'rovda yarating.</p>
            <div class="hero-badges">
                <span class="hero-badge">✅ 25+ satr</span>
                <span class="hero-badge">✅ Real ma'lumotlar</span>
                <span class="hero-badge">✅ Preview jadval</span>
                <span class="hero-badge">✅ UTF-8</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    csv_examples = [
        ("📦","Mahsulotlar","100 ta mahsulot: ID, nomi, kategoriya, narxi, miqdori, brend, reyting, shtrix-kod"),
        ("👥","Foydalanuvchilar","50 ta foydalanuvchi: ID, ism, familiya, email, telefon, shahar, ro'yxat sanasi, holat"),
        ("🌍","Mamlakatlar","Dunyo mamlakatlari: nomi (o'zbek), poytaxti, aholisi, maydoni, YIM, valyutasi, tillari"),
        ("📱","Ilovalar","Top 100 mobil ilova: nomi, kategoriya, reyting, yuklamalar, narxi, platforma, chiqarilgan yil"),
        ("🎬","Filmlar","Top 100 film: nomi, rejissori, yili, janri, reyting, byudjet, daromad, davomiyligi"),
        ("💼","Kompaniyalar","50 ta kompaniya: nomi, sektori, xodimlar soni, daromad, asos yili, mamlakati, CEO"),
    ]

    c1,c2,c3 = st.columns(3)
    ccsv = [c1,c2,c3]
    for i,(ico,title,fp) in enumerate(csv_examples):
        with ccsv[i%3]:
            if st.button(f"{ico}  {title}", key=f"cvq_{i}", use_container_width=True):
                st.session_state["cv_prompt"] = fp

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    cv_prompt = st.text_area("📝  Dataset tavsifi:",
        value=st.session_state.get("cv_prompt",""),
        placeholder="Masalan: 80 ta O'zbekiston shahri va tumanlari: viloyati, aholisi, maydoni, asosiy sanoat...",
        height=130, key="cv_in")

    gen_cv = st.button("🚀  CSV Yaratish", use_container_width=True, type="primary", key="gen_cv")
    if gen_cv:
        if not cv_prompt.strip():
            st.warning("⚠️  Dataset tavsifini kiriting!")
        else:
            with st.spinner("📋  Dataset yaratilmoqda..."):
                prog = st.progress(0)
                for pct in range(0, 65, 15):
                    time.sleep(0.25)
                    prog.progress(pct)
                fb, fn = gen_csv(cv_prompt)
                prog.progress(100)
                prog.empty()
                st.session_state.files_cnt += 1
                try:
                    df = pd.read_csv(io.BytesIO(fb))
                    st.markdown(f'<div class="somo-success">✅  CSV tayyor — {len(df)} satr, {len(df.columns)} ustun</div>',
                                unsafe_allow_html=True)
                    st.dataframe(df.head(10), use_container_width=True)
                    if len(df) > 10:
                        st.caption(f"↑ Faqat birinchi 10 ta satr ko'rsatildi (jami {len(df)} ta)")
                except:
                    st.markdown('<div class="somo-success">✅  CSV tayyor!</div>', unsafe_allow_html=True)
                st.download_button("⬇️  CSV Yuklab Olish", fb, fn, "text/csv",
                                   use_container_width=True, type="primary")

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: TEMPLATES  ██████████
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "templates":

    st.markdown("""
    <div class="somo-hero">
        <div class="somo-hero-content">
            <p style="font-size:12px;letter-spacing:3px;font-weight:700;color:#818cf8;margin-bottom:10px;text-transform:uppercase;">
                ✦ Template Library
            </p>
            <h1>🎨 Shablonlar <span class="g-text">Markazi</span></h1>
            <p class="subtitle">16 ta professional shablon — bitta bosish bilan yarating yoki Chat AI ga yuboring.</p>
            <div class="hero-badges">
                <span class="hero-badge">📊 Biznes</span>
                <span class="hero-badge">💻 Dasturlash</span>
                <span class="hero-badge">📚 Ta'lim</span>
                <span class="hero-badge">👤 Shaxsiy</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    TEMPLATES = {
        "📊 Biznes": [
            {"ico":"💰","title":"Oylik Byudjet","tag":"excel","tag_cls":"tag-excel",
             "desc":"12 oylik moliyaviy byudjet, SUM/AVERAGE formulalar",
             "prompt":"12 oylik moliyaviy byudjet Excel jadvali: har oy daromad manbalari (ish haqi, freelance, passiv), xarajatlar 8 ta kategoriya (ijara, oziq-ovqat, transport, kommunal, kiyim, sog'liq, ta'lim, ko'ngil ochar), sof foyda, yig'ilgan jamg'arma, formulalar bilan"},
            {"ico":"📈","title":"KPI Dashboard","tag":"excel","tag_cls":"tag-excel",
             "desc":"Kompaniya KPI ko'rsatkichlari, maqsad vs haqiqat",
             "prompt":"Kompaniya KPI Excel dashboard: 15 ta ko'rsatkich (daromad, foyda, xodimlar soni, mijozlar, NPS, churn rate...), har oy maqsad va haqiqiy qiymat, farq foizi, RAG (qizil/sariq/yashil) ranglash"},
            {"ico":"📋","title":"Biznes Reja","tag":"word","tag_cls":"tag-word",
             "desc":"To'liq startap biznes reja hujjati",
             "prompt":"IT startap uchun to'liq biznes reja Word hujjati: ijroiya xulosa, kompaniya tavsifi, bozor tahlili (TAM/SAM/SOM), raqobatchilar, mahsulot/xizmat, marketing va savdo strategiyasi, operatsion reja, moliyaviy prognoz 3 yil, jamoa, risklar va yechimlar"},
            {"ico":"🤝","title":"Hamkorlik Xati","tag":"word","tag_cls":"tag-word",
             "desc":"Professional hamkorlik taklifnomasi",
             "prompt":"Professional hamkorlik taklifnomasi xati Word hujjat: jo'natuvchi kompaniya taqdimoti, qabul qiluvchi kompaniyaga murojaat, hamkorlik taklifi mazmuni, o'zaro foyda, taklif shartlari, javob muddati, imzo va muhr joyi"},
        ],
        "💻 Dasturlash": [
            {"ico":"🤖","title":"Telegram Bot","tag":"code","tag_cls":"tag-code",
             "desc":"Aiogram v3, FSM, inline keyboard",
             "prompt":"Aiogram v3 bilan to'liq Telegram bot: /start, /help, /settings komandalar, InlineKeyboardMarkup va CallbackQuery, FSM holatlar (MultiStepsForm), SQLite bazada foydalanuvchi ma'lumotlari saqlash, admin panel, xabarlar logging, .env konfiguratsiya"},
            {"ico":"🌐","title":"FastAPI REST","tag":"code","tag_cls":"tag-code",
             "desc":"CRUD, JWT, PostgreSQL, Swagger",
             "prompt":"FastAPI da to'liq REST API: User, Post, Comment modellari, SQLAlchemy + PostgreSQL, Pydantic schemalar, JWT Bearer authentication, password hashing, CRUD operatsiyalar, error handlers, CORS, Swagger/OpenAPI dokumentatsiya, alembic migration"},
            {"ico":"🎨","title":"Portfolio Sayt","tag":"html","tag_cls":"tag-html",
             "desc":"Dark theme, glassmorphism, animatsiya",
             "prompt":"Web/ML developer portfolio sahifasi HTML/CSS/JS: animated hero with typewriter effect, about section, skills progress bars (Python, React, ML), projects grid with glassmorphism cards, contact form, particle background, smooth scroll, dark glassmorphism theme, Google Fonts, mobile responsive"},
            {"ico":"📊","title":"Streamlit App","tag":"code","tag_cls":"tag-code",
             "desc":"Data dashboard, grafik, filter",
             "prompt":"Streamlit data analytics dashboard: CSV/Excel yuklash, pandas ma'lumot tozalash, Plotly Express interaktiv grafiklar (bar, line, scatter, pie), dinamik filterlar, statistika xulosa, PDF eksport funksiyasi, sidebar sozlamalari, dark theme"},
        ],
        "📚 Ta'lim": [
            {"ico":"📖","title":"Dars Rejasi","tag":"word","tag_cls":"tag-word",
             "desc":"45 daqiqalik to'liq dars konspekti",
             "prompt":"Informatika fanidan Python dasturlash asoslari bo'yicha 45 daqiqalik dars rejasi Word hujjat: fan, mavzu, sinf, maqsadlar (bilim/ko'nikma/tarbiyaviy), jihozlar, dars bosqichlari (tashkiliy 3 daq, yangi mavzu 20 daq, mustahkamlash 15 daq, baholash 5 daq, uyga vazifa 2 daq), savol-javoblar, baholash mezonlari"},
            {"ico":"📝","title":"Test Savollari","tag":"excel","tag_cls":"tag-excel",
             "desc":"25 ta test, 4 variant, javoblar",
             "prompt":"Python dasturlash asoslari bo'yicha 25 ta test savollari Excel jadvali: №, savol matni, A variant, B variant, C variant, D variant, to'g'ri javob, mavzu (o'zgaruvchilar/tsikllar/funksiyalar/OOP/kutubxonalar), qiyinchilik darajasi (oson/o'rtacha/qiyin), baho"},
            {"ico":"🎓","title":"Baholash Jadvali","tag":"excel","tag_cls":"tag-excel",
             "desc":"30 talaba, 6 fan, o'rtacha, reyting",
             "prompt":"Universitet guruhi uchun to'liq baholash jadvali Excel: 30 talaba (ism-familiya, guruh), 6 ta fan (Matematika, Fizika, Dasturlash, Ingliz tili, Tarix, Chizmachilik), har fandan 3 baho (oraliq1, oraliq2, yakuniy), og'irlikli o'rtacha, GPA, reyting, grant/kontrakt holati, davomad foizi, formulalar"},
            {"ico":"📚","title":"Kurs Ishi","tag":"word","tag_cls":"tag-word",
             "desc":"15+ sahifa, 3 bob, adabiyotlar",
             "prompt":"Kompyuter fanlari yo'nalishi talabasi uchun kurs ishi Word hujjati: mavzu — Zamonaviy sun'iy intellekt texnologiyalari va ularning amaliy qo'llanilishi. Titul varog'i, mundarija, kirish (1 sahifa), 1-bob nazariy asoslar (3 sahifa), 2-bob tahlil (3 sahifa), 3-bob amaliy qism (4 sahifa), xulosa (1 sahifa), adabiyotlar ro'yxati 15 ta, ilovalar"},
        ],
        "👤 Shaxsiy": [
            {"ico":"📄","title":"Rezyume","tag":"word","tag_cls":"tag-word",
             "desc":"Professional CV, zamonaviy format",
             "prompt":"Python/Django backend dasturchi uchun professional rezyume Word hujjat: to'liq ism, kontakt (telefon, email, LinkedIn, GitHub), professional xulosa 3 jumlada, texnik ko'nikmalar (Python, Django, FastAPI, PostgreSQL, Redis, Docker, Git), 2 ta ish joyi tajribasi (mas'uliyatlar bullet-list bilan), ta'lim, sertifikatlar, pet-loyihalar, tillar"},
            {"ico":"📅","title":"Haftalik Reja","tag":"excel","tag_cls":"tag-excel",
             "desc":"7 kun, vazifalar, ustuvorlik, holat",
             "prompt":"Haftalik vazifalar va vaqt boshqaruvi Excel jadvali: 7 kunlik (Dushanba-Yakshanba), har kuni 8 ta vaqt sloti (08:00-22:00 har 2 soat), vazifa nomi, kategoriya (Ish/Ta'lim/Sport/Shaxsiy), ustuvorlik (Yuqori/O'rta/Past), taxminiy vaqt, haqiqiy vaqt, holat (Bajarildi/Jarayonda/Qoldirildi), haftalik xulosa statistika"},
            {"ico":"💰","title":"Shaxsiy Byudjet","tag":"excel","tag_cls":"tag-excel",
             "desc":"Daromad, xarajat, jamg'arma maqsad",
             "prompt":"Shaxsiy moliya boshqaruvi Excel: oylik daromadlar (ish haqi, qo'shimcha, passiv), majburiy xarajatlar (ijara, kommunal, kredit), ixtiyoriy xarajatlar (ovqat, kiyim, ko'ngil ochar, sayohat), jamg'arma maqsad va haqiqat, xarajatlar foizi, oylik trend grafik uchun ma'lumotlar, tavsiyalar"},
            {"ico":"💪","title":"Sport Rejasi","tag":"excel","tag_cls":"tag-excel",
             "desc":"3 oylik trening, progres, ozish",
             "prompt":"3 oylik sport va sog'lom turmush tarziga o'tish rejasi Excel: haftalik trening jadvali (dushanbadan yakshanbaga, soat, mashq turi), har mashq uchun: to'plamlar, takroriylik, og'irlik, dam olish; haftalik ozish maqsadi, haqiqiy og'irlik, kaloriya maqsad, suv ichish, uyqu soati, umumiy progres foizi"},
        ]
    }

    sel = st.selectbox("📁  Kategoriya tanlang:", list(TEMPLATES.keys()), key="tmpl_sel")
    st.markdown(f'<hr class="somo-divider">', unsafe_allow_html=True)

    items = TEMPLATES[sel]
    c1, c2 = st.columns(2)
    cols_t = [c1, c2]

    for i, tmpl in enumerate(items):
        with cols_t[i%2]:
            st.markdown(f"""
            <div class="tmpl-card">
                <span class="tmpl-tag {tmpl['tag_cls']}">{tmpl['tag'].upper()}</span>
                <div class="tmpl-title">{tmpl['ico']}  {tmpl['title']}</div>
                <div class="tmpl-desc">{tmpl['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

            bc1, bc2 = st.columns(2)
            with bc1:
                if st.button(f"🚀  Yaratish", key=f"tgen_{sel}_{i}", use_container_width=True, type="primary"):
                    with st.spinner("⏳  Tayyorlanmoqda..."):
                        tag = tmpl["tag"]
                        if tag == "excel":
                            fb, fn = gen_excel(tmpl["prompt"])
                            if fb and isinstance(fb, bytes):
                                st.session_state.files_cnt += 1
                                st.download_button("⬇️  Excel", fb, fn, MIME["xlsx"], key=f"tdl_{sel}_{i}", type="primary")
                        elif tag == "word":
                            fb, fn = gen_word(tmpl["prompt"])
                            if fb and isinstance(fb, bytes):
                                st.session_state.files_cnt += 1
                                st.download_button("⬇️  Word", fb, fn, MIME["docx"], key=f"tdl_{sel}_{i}", type="primary")
                        elif tag == "code":
                            fb, fn = gen_code(tmpl["prompt"])
                            st.session_state.files_cnt += 1
                            st.download_button("⬇️  .py", fb, fn, MIME["py"], key=f"tdl_{sel}_{i}", type="primary")
                        elif tag == "html":
                            fb, fn = gen_html(tmpl["prompt"])
                            st.session_state.files_cnt += 1
                            st.download_button("⬇️  HTML", fb, fn, MIME["html"], key=f"tdl_{sel}_{i}", type="primary")
            with bc2:
                if st.button(f"💬  Chat AI ga", key=f"tchat_{sel}_{i}", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":tmpl["prompt"]})
                    st.session_state.page = "chat"
                    st.rerun()

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: ANALYZE  ██████████
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "analyze":

    st.markdown("""
    <div class="somo-hero">
        <div class="somo-hero-content">
            <p style="font-size:12px;letter-spacing:3px;font-weight:700;color:#22d3ee;margin-bottom:10px;text-transform:uppercase;">
                ✦ Document Analysis
            </p>
            <h1>🔍 Hujjat <span class="g-text">Tahlili</span></h1>
            <p class="subtitle">PDF yoki Word faylni yuklang — AI xulosa chiqaradi, g'oyalarni ajratadi, savollarga javob beradi.</p>
            <div class="hero-badges">
                <span class="hero-badge">📄 PDF</span>
                <span class="hero-badge">📝 DOCX</span>
                <span class="hero-badge">🧠 AI Tahlil</span>
                <span class="hero-badge">❓ Savol-Javob</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_up, col_act = st.columns([1, 1])

    with col_up:
        st.markdown('<p class="section-label">Fayl Yuklash</p>', unsafe_allow_html=True)
        upl = st.file_uploader("PDF yoki DOCX", type=["pdf","docx"], key="az_up",
                               label_visibility="collapsed")
        if upl:
            with st.spinner("📄  O'qilmoqda..."):
                txt = process_doc(upl)
                st.session_state.uploaded_text = txt
            if txt:
                st.markdown(f'<div class="somo-success">✅  {upl.name} — {len(txt):,} belgi, ~{len(txt.split()):,} so\'z</div>',
                            unsafe_allow_html=True)
                with st.expander("👁  Matnni ko'rish (birinchi 2000 belgi)"):
                    st.text(txt[:2000]+("..." if len(txt)>2000 else ""))
            else:
                st.error("❌  Fayl o'qilmadi yoki bo'sh")

        if not st.session_state.uploaded_text:
            st.markdown("""
            <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.15);
                        border-radius:14px;padding:24px;margin-top:16px;text-align:center;">
                <div style="font-size:40px;margin-bottom:12px;">📂</div>
                <p style="color:#64748b;font-size:14px;">PDF yoki DOCX fayl yuklang</p>
                <p style="color:#334155;font-size:12px;margin-top:8px;">Maksimum hajm: 10 MB</p>
            </div>
            """, unsafe_allow_html=True)

    with col_act:
        st.markdown('<p class="section-label">Tahlil Amaliyotlari</p>', unsafe_allow_html=True)
        if st.session_state.uploaded_text:
            actions = {
                "📝  Qisqa Xulosa":    "Ushbu hujjatni eng muhim 5-7 ta asosiy band bilan qisqa va aniq xulosasini yoz. Har bir bandni ★ bilan boshlat.",
                "🔑  Kalit G'oyalar":  "Hujjatdagi 8-10 ta eng muhim g'oya, fakt va xulosalarni ro'yxat shaklida ajratib chiqar. Har birini batafsil izohlat.",
                "❓  Savol-Javob":     "Hujjat bo'yicha 10 ta muhim savol tuz va har biriga to'liq javob ber. Imtihon savollari formatida bo'lsin.",
                "🌐  Inglizcha":       "Hujjat mazmunini professional ingliz tiliga tarjima qil. Terminlarni to'g'ri tarjima qil.",
                "📊  Statistika":      "Hujjatdagi barcha raqamlar, foizlar, sanalar va statistika ma'lumotlarini jadval ko'rinishida tizimlashtir.",
                "✅  Action Items":    "Hujjatdan aniq amaliy vazifalar, keyingi qadamlar va takliflarni ajratib, ustuvorlik bo'yicha tartibla.",
            }
            for act_lbl, act_prompt in actions.items():
                if st.button(act_lbl, key=f"az_{act_lbl}", use_container_width=True):
                    with st.spinner("🤔  Tahlil qilinmoqda..."):
                        result = call_ai([
                            {"role":"system","content":"Sen professional hujjat tahlilchisan. To'liq va foydali javoblar ber."},
                            {"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:4500]}\n\nVazifa: {act_prompt}"}
                        ], temperature=0.4)
                        st.markdown(f"### {act_lbl}")
                        st.markdown(result)
        else:
            st.markdown("""
            <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.15);
                        border-radius:14px;padding:24px;text-align:center;margin-top:8px;">
                <p style="color:#475569;font-size:14px;">👆  Avval chap tomonda fayl yuklang</p>
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.uploaded_text:
        st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">O\'z Savolingiz</p>', unsafe_allow_html=True)
        c_q, c_b = st.columns([4,1])
        with c_q:
            custom_q = st.text_input("", placeholder="🔍  Hujjat haqida savolingizni yozing...", label_visibility="collapsed", key="az_q")
        with c_b:
            if st.button("🔍  Qidirish", use_container_width=True, type="primary", key="az_ask"):
                if custom_q:
                    with st.spinner(""):
                        ans = call_ai([
                            {"role":"system","content":"Hujjat asosida aniq va batafsil javob ber. Hujjatda yo'q narsa haqida o'zing ixtiro qilma."},
                            {"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:4500]}\n\nSavol: {custom_q}"}
                        ], temperature=0.3)
                        st.markdown(f"**💬 Javob:**\n\n{ans}")

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: HISTORY  ██████████
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "history":

    st.markdown("""
    <div class="somo-hero">
        <div class="somo-hero-content">
            <p style="font-size:12px;letter-spacing:3px;font-weight:700;color:#818cf8;margin-bottom:10px;text-transform:uppercase;">
                ✦ History
            </p>
            <h1>📜 Chat <span class="g-text">Tarixi</span></h1>
            <p class="subtitle">Barcha suhbatlaringiz, qidirish va eksport imkoniyati bilan.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    msgs = st.session_state.messages
    if msgs:
        u_cnt = sum(1 for m in msgs if m["role"]=="user")
        a_cnt = sum(1 for m in msgs if m["role"]=="assistant")
        st.markdown(f"""
        <div class="stat-row" style="grid-template-columns:repeat(4,1fr);">
            <div class="stat-box"><div class="stat-icon">💬</div><div class="stat-val">{len(msgs)}</div><div class="stat-lbl">Jami</div></div>
            <div class="stat-box"><div class="stat-icon">👤</div><div class="stat-val">{u_cnt}</div><div class="stat-lbl">Sizdan</div></div>
            <div class="stat-box"><div class="stat-icon">🤖</div><div class="stat-val">{a_cnt}</div><div class="stat-lbl">AI dan</div></div>
            <div class="stat-box"><div class="stat-icon">📁</div><div class="stat-val">{st.session_state.files_cnt}</div><div class="stat-lbl">Fayllar</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Controls
        col_s, col_e1, col_e2 = st.columns([3,1,1])
        with col_s:
            search = st.text_input("", placeholder="🔍  Xabarlarda qidirish...", label_visibility="collapsed", key="hist_s")
        with col_e1:
            chat_json = json.dumps(msgs, ensure_ascii=False, indent=2)
            st.download_button("📥  JSON", chat_json.encode(), f"somo_chat_{datetime.now():%Y%m%d}.json",
                               use_container_width=True)
        with col_e2:
            txt_exp = "\n\n".join([f"[{m['role'].upper()}]\n{m['content']}" for m in msgs])
            st.download_button("📄  TXT", txt_exp.encode(), f"somo_chat_{datetime.now():%Y%m%d}.txt",
                               use_container_width=True)

        show = msgs
        if search:
            show = [m for m in msgs if search.lower() in m.get("content","").lower()]
            st.markdown(f'<div class="somo-notify">🔍  "{search}" — {len(show)} ta natija</div>', unsafe_allow_html=True)

        st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
        st.markdown(f'<p class="section-label">Xabarlar (oxirgi {min(len(show),50)} ta)</p>', unsafe_allow_html=True)

        for msg in reversed(show[-50:]):
            is_user = msg["role"] == "user"
            css_cls = "hist-user" if is_user else "hist-ai"
            role_lbl = "👤  Siz" if is_user else "🤖  Somo AI"
            body = msg.get("content","")[:350]
            if len(msg.get("content","")) > 350: body += "..."
            st.markdown(f"""
            <div class="hist-msg {css_cls}">
                <div class="hist-role">{role_lbl}</div>
                <div class="hist-body">{body}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;">
            <div style="font-size:60px;margin-bottom:20px;">💬</div>
            <p style="color:#475569;font-size:18px;font-weight:600;">Hali chat tarixi yo'q</p>
            <p style="color:#334155;font-size:14px;margin-top:8px;">Chat AI sahifasiga o'ting va suhbatni boshlang</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💬  Chat AI ga o'tish", type="primary"):
            st.session_state.page = "chat"
            st.rerun()

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: FEEDBACK  ██████████
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "feedback":

    st.markdown("""
    <div class="somo-hero">
        <div class="somo-hero-content">
            <p style="font-size:12px;letter-spacing:3px;font-weight:700;color:#f472b6;margin-bottom:10px;text-transform:uppercase;">
                ✦ Feedback
            </p>
            <h1>💌 Fikr <span class="g-text">Bildirish</span></h1>
            <p class="subtitle">Sizning fikringiz Somo AI ni yaxshiroq qilishga yordam beradi. Har qanday taklif qabul!</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_f, col_s = st.columns([3, 2])

    with col_f:
        st.markdown('<p class="section-label">Fikringizni yuboring</p>', unsafe_allow_html=True)
        with st.form("fb_form", clear_on_submit=True):
            rating = st.select_slider("⭐  Baho bering:",
                options=[1,2,3,4,5], value=5,
                format_func=lambda x: "⭐"*x + f"  ({x}/5)")
            category = st.selectbox("📂  Kategoriya:", [
                "Umumiy fikr","Xato haqida xabar","Yangi funksiya taklifi",
                "Dizayn taklifi","Tezlik muammosi","Boshqa"
            ])
            message = st.text_area("✍️  Xabaringiz:", height=140,
                placeholder="Fikrlaringizni batafsil yozing — 10 ta belgidan ko'p bo'lsin...")
            email = st.text_input("📧  Email (ixtiyoriy):", placeholder="javob olish uchun")
            st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
            sub_fb = st.form_submit_button("📤  Yuborish", use_container_width=True, type="primary")

            if sub_fb:
                if not message or len(message) < 10:
                    st.error("❌  Kamida 10 ta belgidan iborat xabar yozing!")
                elif fb_db:
                    try:
                        fb_db.append_row([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            st.session_state.username, rating, category,
                            message, email or "N/A", "Yangi",
                            st.session_state.files_cnt
                        ])
                        st.balloons()
                        st.markdown('<div class="somo-success">✅  Rahmat! Fikringiz muvaffaqiyatli yuborildi 🙏</div>',
                                    unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌  {e}")
                else:
                    st.error("❌  Baza ulanmagan")

    with col_s:
        st.markdown('<p class="section-label">Statistika</p>', unsafe_allow_html=True)
        if fb_db:
            try:
                all_fb = fb_db.get_all_records()
                if all_fb:
                    st.markdown(f"""
                    <div class="stat-row" style="grid-template-columns:1fr 1fr;">
                        <div class="stat-box"><div class="stat-icon">📨</div>
                            <div class="stat-val">{len(all_fb)}</div><div class="stat-lbl">Jami</div></div>
                        <div class="stat-box"><div class="stat-icon">⭐</div>
                            <div class="stat-val">{sum(int(f.get("Rating",5)) for f in all_fb)/len(all_fb):.1f}</div>
                            <div class="stat-lbl">O'rtacha</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown('<p class="section-label" style="margin-top:16px;">Oxirgi fikrlar</p>', unsafe_allow_html=True)
                    for fb in reversed(all_fb[-5:]):
                        stars = "⭐" * int(fb.get("Rating",5))
                        uname_fb = str(fb.get("Username",""))
                        msg_fb = str(fb.get("Message",""))[:80]
                        st.markdown(f"""
                        <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.12);
                                    border-radius:10px;padding:12px;margin:6px 0;">
                            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                                <span style="font-size:13px;font-weight:700;color:#818cf8;">{uname_fb}</span>
                                <span style="font-size:13px;">{stars}</span>
                            </div>
                            <p style="color:#64748b;font-size:12px;line-height:1.5;">{msg_fb}...</p>
                        </div>
                        """, unsafe_allow_html=True)
            except:
                st.info("Statistika yuklanmadi")

# ══════════════════════════════════════════════════════════════════
# ██████████  PAGE: PROFILE  ██████████
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "profile":
    uname = st.session_state.username
    mins = (datetime.now()-st.session_state.login_time).seconds//60 if 'login_time' in st.session_state else 0

    st.markdown(f"""
    <div class="somo-hero" style="text-align:center;">
        <div class="somo-hero-content">
            <div style="width:90px;height:90px;background:linear-gradient(135deg,#4f46e5,#7c3aed,#ec4899);
                        border-radius:24px;margin:0 auto 20px;display:flex;align-items:center;justify-content:center;
                        font-size:42px;font-weight:900;color:white;box-shadow:0 0 40px rgba(99,102,241,0.5);">
                {uname[0].upper()}
            </div>
            <h1 style="font-size:32px;">{uname}</h1>
            <p style="color:rgba(255,255,255,0.6);font-size:15px;margin-top:8px;">
                🟢 Aktiv  ·  Somo AI Ultra Pro Max
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    p_stats = [
        ("💬", len(st.session_state.messages), "Xabarlar"),
        ("📁", st.session_state.files_cnt,      "Fayllar"),
        ("⏱",  mins,                            "Daqiqa"),
        ("🔥",  max(1,len(st.session_state.messages)//5), "Daraja"),
    ]
    cols_ps = st.columns(4)
    for col, (icon, val, lbl) in zip(cols_ps, p_stats):
        with col:
            st.markdown(f"""
            <div class="profile-stat">
                <div class="p-stat-icon">{icon}</div>
                <div class="p-stat-val">{val}</div>
                <div class="p-stat-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    col_pw, col_info = st.columns(2)

    with col_pw:
        st.markdown('<p class="section-label">Xavfsizlik</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-title" style="font-size:18px;">🔑 Parolni O\'zgartirish</p>', unsafe_allow_html=True)
        with st.form("pw_form"):
            old_pw = st.text_input("Joriy parol", type="password", key="pw_old")
            new_pw = st.text_input("Yangi parol (min 6 belgi)", type="password", key="pw_new")
            conf_pw = st.text_input("Tasdiqlash", type="password", key="pw_conf")
            if st.form_submit_button("🔄  Parolni yangilash", type="primary", use_container_width=True):
                if len(new_pw) < 6:
                    st.error("❌  Yangi parol kamida 6 belgi!")
                elif new_pw != conf_pw:
                    st.error("❌  Parollar mos emas!")
                elif user_db:
                    try:
                        recs = user_db.get_all_records()
                        idx = next((i for i,r in enumerate(recs)
                            if str(r['username'])==uname and str(r['password'])==hash_pw(old_pw)), None)
                        if idx is not None:
                            user_db.update_cell(idx+2, 2, hash_pw(new_pw))
                            st.success("✅  Parol muvaffaqiyatli yangilandi!")
                        else:
                            st.error("❌  Joriy parol noto'g'ri!")
                    except Exception as e:
                        st.error(f"❌  {e}")

    with col_info:
        st.markdown('<p class="section-label">Sessiya</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-title" style="font-size:18px;">📊 Ma\'lumotlar</p>', unsafe_allow_html=True)
        if 'login_time' in st.session_state:
            login_str = st.session_state.login_time.strftime('%d.%m.%Y %H:%M')
        else:
            login_str = "—"

        st.markdown(f"""
        <div style="background:linear-gradient(145deg,#13131f,#0e0e1c);
                    border:1px solid rgba(99,102,241,0.15);border-radius:16px;padding:22px;">
            <div style="margin-bottom:14px;">
                <p style="color:#475569;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Kirish vaqti</p>
                <p style="color:#e2e8f0;font-size:15px;font-weight:600;margin-top:4px;">{login_str}</p>
            </div>
            <div style="margin-bottom:14px;">
                <p style="color:#475569;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Sessiya davomiyligi</p>
                <p style="color:#e2e8f0;font-size:15px;font-weight:600;margin-top:4px;">{mins} daqiqa</p>
            </div>
            <div style="margin-bottom:14px;">
                <p style="color:#475569;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Yaratilgan fayllar</p>
                <p style="color:#10b981;font-size:15px;font-weight:600;margin-top:4px;">{st.session_state.files_cnt} ta</p>
            </div>
            <div>
                <p style="color:#475569;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Chat xabarlari</p>
                <p style="color:#818cf8;font-size:15px;font-weight:600;margin-top:4px;">{len(st.session_state.messages)} ta</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        st.markdown('<p class="section-label" style="margin-top:8px;">AI Sozlamalari</p>', unsafe_allow_html=True)
        new_style = st.selectbox("AI uslubi:",
            ["Aqlli yordamchi","Do'stona","Rasmiy ekspert","Ijodkor","Texnik"],
            key="prof_style",
            index=["Aqlli yordamchi","Do'stona","Rasmiy ekspert","Ijodkor","Texnik"].index(
                st.session_state.ai_style) if st.session_state.ai_style in ["Aqlli yordamchi","Do'stona","Rasmiy ekspert","Ijodkor","Texnik"] else 0)
        if st.button("💾  Saqlash", type="primary", key="save_style", use_container_width=True):
            st.session_state.ai_style = new_style
            st.success("✅  Saqlandi!")

# ══════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="somo-footer">
    <div class="f-title">🌌 Somo AI <span style="background:linear-gradient(90deg,#818cf8,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Ultra Pro Max</span></div>
    <div class="f-sub">📊 Excel · 📝 Word · 💻 Kod · 🌐 HTML · 📋 CSV · 🧠 Chat AI</div>
    <div class="f-sub" style="margin-top:6px;">⚡ Groq · Llama 3.3 · 70B Parameters · Python · Streamlit</div>
    <div class="f-sub" style="margin-top:10px;">
        👨‍💻 <strong style="color:#e2e8f0;">Usmonov Sodiq</strong>
        &nbsp;·&nbsp;
        👨‍💻 <strong style="color:#e2e8f0;">Davlatov Mironshoh</strong>
    </div>
    <div class="f-sub" style="margin-top:6px;">📧 support@somoai.uz &nbsp;|&nbsp; 🌐 www.somoai.uz</div>
    <div class="f-copy">© 2026 Somo AI Ultra Pro Max v3.0 — Barcha huquqlar himoyalangan</div>
</div>
""", unsafe_allow_html=True)
