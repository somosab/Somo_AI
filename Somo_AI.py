import streamlit as st
import pandas as pd
import gspread
import hashlib
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
    initial_sidebar_state="auto"
)

# ══════════════════════════════════════════════════════════════════
# COOKIES
# ══════════════════════════════════════════════════════════════════
if HAS_COOKIES:
    cookies = EncryptedCookieManager(
        password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Ultra_Pro_Max_2026_XYZ")
    )
    if not cookies.ready():
        st.stop()
else:
    cookies = {}

# ══════════════════════════════════════════════════════════════════
# MASTER CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');

/* ─── RESET & BASE ─── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg-0:       #05050f;
  --bg-1:       #090916;
  --bg-2:       #0d0d1e;
  --bg-3:       #111128;
  --bg-card:    #0f0f22;
  --border:     rgba(100,108,255,0.18);
  --border-h:   rgba(100,108,255,0.55);
  --accent:     #646cff;
  --accent-2:   #a78bfa;
  --accent-3:   #f472b6;
  --accent-4:   #34d399;
  --accent-5:   #38bdf8;
  --text-1:     #f0f0ff;
  --text-2:     #a0a0c0;
  --text-3:     #50506a;
  --font-head:  'Syne', sans-serif;
  --font-body:  'Inter', sans-serif;
  --font-mono:  'JetBrains Mono', monospace;
  --radius:     16px;
  --radius-sm:  10px;
  --shadow:     0 4px 40px rgba(0,0,0,0.6);
  --glow:       0 0 40px rgba(100,108,255,0.25);
  --glow-sm:    0 0 20px rgba(100,108,255,0.15);
}

html, body, .stApp {
    font-family: var(--font-body) !important;
    background: var(--bg-0) !important;
    color: var(--text-1) !important;
}
.stApp { background: var(--bg-0) !important; }

/* Noise overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.35;
}

/* ─── HIDE STREAMLIT CHROME ─── */
[data-testid="stSidebarNav"],
.st-emotion-cache-1vt458p, .st-emotion-cache-k77z8z,
header[data-testid="stHeader"],
#MainMenu, footer { display: none !important; }

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07071a 0%, #09091e 100%) !important;
    border-right: 1px solid var(--border) !important;
    width: 268px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebar"] section { background: transparent !important; }
[data-testid="stSidebar"] .stVerticalBlock { gap: 0 !important; }
[data-testid="stSidebar"] * { color: var(--text-2) !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span {
    color: var(--text-3) !important;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 700;
    font-family: var(--font-mono) !important;
}

div[data-testid="stSidebar"] button {
    background: transparent !important;
    color: var(--text-2) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    font-family: var(--font-body) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    padding: 10px 14px !important;
    margin: 1px 0 !important;
    text-align: left !important;
    letter-spacing: 0.1px !important;
}
div[data-testid="stSidebar"] button:hover {
    background: rgba(100,108,255,0.1) !important;
    color: #c7d2fe !important;
}
div[data-testid="stSidebar"] button[kind="primary"],
div[data-testid="stSidebar"] button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg,rgba(100,108,255,0.2),rgba(167,139,250,0.15)) !important;
    color: #c7d2fe !important;
    font-weight: 700 !important;
    border: 1px solid var(--border) !important;
}

/* ─── MAIN ─── */
.main .block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stMainBlockContainer"] {
    padding: 24px 32px 80px !important;
    padding-top: 68px !important;
    background: var(--bg-0) !important;
}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-1); }
::-webkit-scrollbar-thumb { background: #2a2a55; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ════════════════════════════════
   HERO BANNER
════════════════════════════════ */
.somo-hero {
    position: relative;
    overflow: hidden;
    border-radius: 24px;
    padding: 56px 52px;
    margin-bottom: 36px;
    background: var(--bg-1);
    border: 1px solid var(--border);
    box-shadow: var(--shadow), var(--glow);
}
.somo-hero::before {
    content: '';
    position: absolute;
    top: -80px; left: -80px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(100,108,255,0.14) 0%, transparent 60%);
    animation: pulse-orb 10s ease-in-out infinite;
}
.somo-hero::after {
    content: '';
    position: absolute;
    bottom: -60px; right: -40px;
    width: 450px; height: 450px;
    background: radial-gradient(circle, rgba(244,114,182,0.10) 0%, transparent 60%);
    animation: pulse-orb 10s ease-in-out 5s infinite;
}
@keyframes pulse-orb {
    0%,100% { transform: scale(1) translate(0,0); }
    50% { transform: scale(1.2) translate(-20px,-20px); }
}

/* Grid dots background */
.somo-hero .grid-dots {
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle, rgba(100,108,255,0.2) 1px, transparent 1px);
    background-size: 32px 32px;
    opacity: 0.3;
}

.somo-hero-content { position: relative; z-index: 2; }
.somo-hero h1 {
    font-family: var(--font-head) !important;
    font-size: clamp(30px,4vw,52px);
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -1.5px;
    color: var(--text-1);
    margin-bottom: 14px;
}
.somo-hero .subtitle {
    font-size: 16px;
    color: var(--text-2);
    max-width: 540px;
    line-height: 1.65;
    margin-bottom: 26px;
}
.hero-badges { display: flex; flex-wrap: wrap; gap: 8px; }
.hero-badge {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.7);
    padding: 5px 14px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 500;
    font-family: var(--font-mono);
    backdrop-filter: blur(8px);
    letter-spacing: 0.3px;
}

/* ═══ API INDICATOR BADGE ═══ */
.api-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 600;
    font-family: var(--font-mono);
    letter-spacing: 0.5px;
    border: 1px solid;
}
.api-groq    { background: rgba(255,166,0,0.1);    color:#fbbf24; border-color:rgba(251,191,36,0.3);  }
.api-gemini  { background: rgba(52,211,153,0.1);   color:#34d399; border-color:rgba(52,211,153,0.3);  }
.api-cohere  { background: rgba(56,189,248,0.1);   color:#38bdf8; border-color:rgba(56,189,248,0.3);  }
.api-mistral { background: rgba(244,114,182,0.1);  color:#f472b6; border-color:rgba(244,114,182,0.3); }
.api-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    display: inline-block;
    animation: blink-dot 2s ease-in-out infinite;
}
@keyframes blink-dot { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
.api-groq .api-dot    { background:#fbbf24; }
.api-gemini .api-dot  { background:#34d399; }
.api-cohere .api-dot  { background:#38bdf8; }
.api-mistral .api-dot { background:#f472b6; }

/* ════════════════════════════════
   GRADIENT TEXT
════════════════════════════════ */
.g-text {
    background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6, #818cf8);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: g-shift 5s ease infinite;
}
@keyframes g-shift { 0%,100%{background-position:0%} 50%{background-position:100%} }

/* ════════════════════════════════
   TYPEWRITER ANIMATION
════════════════════════════════ */
.typewriter-container {
    position: relative;
    display: inline-block;
}
.typewriter-cursor {
    display: inline-block;
    width: 2px;
    height: 1.1em;
    background: var(--accent);
    margin-left: 2px;
    vertical-align: text-bottom;
    animation: cursor-blink 0.85s step-end infinite;
    border-radius: 1px;
    box-shadow: 0 0 8px var(--accent);
}
@keyframes cursor-blink { 0%,100%{opacity:1} 50%{opacity:0} }

/* Streaming message style */
.streaming-msg {
    background: linear-gradient(145deg, var(--bg-card), var(--bg-2)) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 18px 20px !important;
    position: relative;
    overflow: hidden;
}
.streaming-msg::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 60%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    animation: scan-line 2.5s ease-in-out infinite;
}
@keyframes scan-line { 0%{left:-60%} 100%{left:160%} }

/* ════════════════════════════════
   SECTION LABELS
════════════════════════════════ */
.section-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 8px;
    font-family: var(--font-mono);
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::before {
    content: '';
    display: inline-block;
    width: 16px;
    height: 1px;
    background: var(--accent);
}
.section-title {
    font-size: 26px;
    font-weight: 800;
    color: var(--text-1);
    margin-bottom: 6px;
    letter-spacing: -0.5px;
    font-family: var(--font-head);
}
.section-desc { font-size: 14px; color: var(--text-3); margin-bottom: 28px; }

/* ════════════════════════════════
   CARDS GRID
════════════════════════════════ */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px,1fr));
    gap: 14px;
    margin-bottom: 32px;
}
.somo-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px 18px;
    text-align: center;
    transition: all 0.3s cubic-bezier(.4,0,.2,1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.somo-card::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: var(--radius);
    opacity: 0;
    transition: opacity 0.3s;
    background: radial-gradient(circle at 50% 0%, rgba(100,108,255,0.1), transparent 70%);
}
.somo-card:hover { transform: translateY(-6px); border-color: var(--border-h); box-shadow: 0 20px 50px rgba(0,0,0,0.5), var(--glow-sm); }
.somo-card:hover::after { opacity: 1; }
.card-icon { font-size: 34px; margin-bottom: 14px; display: block; }
.card-title { font-size: 14px; font-weight: 700; color: var(--text-1); margin-bottom: 6px; font-family: var(--font-head); }
.card-desc { font-size: 11.5px; color: var(--text-3); line-height: 1.55; }

.card-v1:hover { border-color: rgba(100,108,255,0.6); box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 30px rgba(100,108,255,0.2); }
.card-v2:hover { border-color: rgba(52,211,153,0.6);  box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 30px rgba(52,211,153,0.2); }
.card-v3:hover { border-color: rgba(251,191,36,0.6);  box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 30px rgba(251,191,36,0.15); }
.card-v4:hover { border-color: rgba(244,114,182,0.6); box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 30px rgba(244,114,182,0.2); }
.card-v5:hover { border-color: rgba(56,189,248,0.6);  box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 30px rgba(56,189,248,0.2); }
.card-v6:hover { border-color: rgba(167,139,250,0.6); box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 30px rgba(167,139,250,0.2); }

/* ════════════════════════════════
   STAT BOXES
════════════════════════════════ */
.stat-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px,1fr)); gap: 12px; margin-bottom: 28px; }
.stat-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 14px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.stat-box:hover { border-color: var(--border-h); }
.stat-val { font-size: 28px; font-weight: 900; color: var(--text-1); line-height: 1; font-family: var(--font-head); }
.stat-lbl { font-size: 10px; font-weight: 700; color: var(--text-3); margin-top: 6px; text-transform: uppercase; letter-spacing: 1.5px; font-family: var(--font-mono); }
.stat-icon { font-size: 20px; margin-bottom: 8px; }

/* ════════════════════════════════
   DIVIDER
════════════════════════════════ */
.somo-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 28px 0;
    border: none;
}

/* ════════════════════════════════
   CHAT MESSAGES
════════════════════════════════ */
.stChatMessage {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 16px 20px !important;
    margin: 8px 0 !important;
    color: var(--text-1) !important;
}
.stChatMessage p, .stChatMessage span, .stChatMessage li { color: var(--text-1) !important; }
.stChatMessage code { background: rgba(100,108,255,0.12) !important; color: #a5b4fc !important; border-radius: 4px; padding: 1px 6px; font-family: var(--font-mono) !important; }
.stChatMessage pre { background: #04040f !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; }

/* ════════════════════════════════
   CHAT INPUT
════════════════════════════════ */
[data-testid="stChatInput"],
.stChatInputContainer,
div[data-testid="stChatInputContainer"],
div.stChatFloatingInputContainer,
div[class*="stChatInput"],
div[class*="ChatInput"] {
    background: var(--bg-0) !important;
    border-top: 1px solid var(--border) !important;
    box-shadow: none !important;
    padding: 12px 20px !important;
}
[data-testid="stChatInput"] > div,
[data-testid="stChatInputContainer"] > div,
div[class*="stChatInput"] > div {
    background: var(--bg-0) !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputContainer"] textarea,
.stChatInputContainer textarea,
div[class*="stChatInput"] textarea {
    background: var(--bg-2) !important;
    color: var(--text-1) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    padding: 14px 18px !important;
    caret-color: var(--accent) !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInputContainer"] textarea::placeholder,
.stChatInputContainer textarea::placeholder { color: var(--text-3) !important; font-size: 13px !important; }
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInputContainer"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(100,108,255,0.12), var(--glow-sm) !important;
    outline: none !important;
}
[data-testid="stChatInput"] button,
[data-testid="stChatInputContainer"] button,
.stChatInputContainer button {
    background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    color: white !important;
    box-shadow: 0 0 15px rgba(100,108,255,0.4) !important;
    transition: all 0.2s !important;
}
[data-testid="stChatInput"] button:hover,
[data-testid="stChatInputContainer"] button:hover {
    box-shadow: 0 0 25px rgba(100,108,255,0.6) !important;
    transform: scale(1.05) !important;
}
div[data-testid="stBottom"],
div[data-testid="stBottom"] > div,
div[data-testid="stBottom"] > div > div {
    background: var(--bg-0) !important;
    border-top: 1px solid var(--border) !important;
}

/* ════════════════════════════════
   FORM ELEMENTS
════════════════════════════════ */
.stTextInput input, .stTextArea textarea, .stSelectbox select,
div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
    background: var(--bg-2) !important;
    color: var(--text-1) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(100,108,255,0.1) !important;
    outline: none !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: var(--text-3) !important; }

.stTextInput label, .stTextArea label, .stSelectbox label,
.stSlider label, .stFileUploader label, .stCheckbox label,
[data-testid="stWidgetLabel"] {
    color: var(--text-2) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    font-family: var(--font-mono) !important;
    letter-spacing: 0.3px !important;
}

div[data-baseweb="select"] > div {
    background: var(--bg-2) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-1) !important;
}
div[data-baseweb="select"] svg { fill: var(--text-3) !important; }
div[data-baseweb="popover"] {
    background: var(--bg-3) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow) !important;
}
div[data-baseweb="popover"] li { color: var(--text-1) !important; }
div[data-baseweb="popover"] li:hover { background: rgba(100,108,255,0.1) !important; }

.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 12px rgba(100,108,255,0.5) !important;
}

[data-testid="stFileUploader"] {
    background: rgba(100,108,255,0.04) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 20px !important;
    transition: 0.3s;
}
[data-testid="stFileUploader"]:hover { border-color: var(--border-h) !important; background: rgba(100,108,255,0.08) !important; }
[data-testid="stFileUploader"] * { color: var(--text-2) !important; }

.stCheckbox [data-baseweb="checkbox"] div { border-color: var(--border) !important; background: transparent !important; border-radius: 5px !important; }
.stCheckbox [data-baseweb="checkbox"] div[aria-checked="true"] { background: var(--accent) !important; border-color: var(--accent) !important; }

/* ════════════════════════════════
   BUTTONS
════════════════════════════════ */
.stButton > button {
    background: rgba(100,108,255,0.07) !important;
    color: #a5b4fc !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    padding: 10px 20px !important;
    transition: all 0.22s ease !important;
    letter-spacing: 0.1px !important;
}
.stButton > button:hover {
    background: rgba(100,108,255,0.15) !important;
    border-color: var(--border-h) !important;
    color: #c7d2fe !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(100,108,255,0.2) !important;
}
.stButton > button[kind="primary"],
.stButton > button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    color: white !important;
    border-color: transparent !important;
    box-shadow: 0 0 25px rgba(100,108,255,0.3) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[kind="primaryFormSubmit"]:hover {
    background: linear-gradient(135deg,#4338ca,#6d28d9) !important;
    box-shadow: 0 6px 30px rgba(100,108,255,0.5) !important;
    transform: translateY(-3px) !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg,#059669,#10b981) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 20px rgba(16,185,129,0.3) !important;
    transition: all 0.25s !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 30px rgba(16,185,129,0.5) !important;
}

/* ════════════════════════════════
   TABS
════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 4px !important;
    border-bottom: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: var(--text-3) !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    padding: 10px 20px !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    transition: 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #a5b4fc !important; background: rgba(100,108,255,0.07) !important; }
.stTabs [aria-selected="true"][data-baseweb="tab"] { color: #818cf8 !important; border-bottom: 2px solid var(--accent) !important; }
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding: 20px 0 !important; }

/* ════════════════════════════════
   EXPANDER
════════════════════════════════ */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-1) !important;
    font-weight: 600 !important;
    font-family: var(--font-body) !important;
}
.streamlit-expanderContent {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
    color: var(--text-2) !important;
}

/* ════════════════════════════════
   FORMS
════════════════════════════════ */
[data-testid="stForm"] {
    background: linear-gradient(145deg,var(--bg-card),var(--bg-2)) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 28px !important;
}
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    color: white !important;
    border: none !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 20px rgba(100,108,255,0.35) !important;
}

/* ════════════════════════════════
   METRICS
════════════════════════════════ */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 18px !important;
}
[data-testid="stMetricLabel"] { color: var(--text-3) !important; font-size: 11px !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 1.5px !important; font-family: var(--font-mono) !important; }
[data-testid="stMetricValue"] { color: var(--text-1) !important; font-weight: 900 !important; font-size: 28px !important; font-family: var(--font-head) !important; }

/* ════════════════════════════════
   DATAFRAME
════════════════════════════════ */
.stDataFrame, iframe { border-radius: var(--radius) !important; border: 1px solid var(--border) !important; }

/* ════════════════════════════════
   ALERTS
════════════════════════════════ */
.stSuccess > div { background: rgba(52,211,153,0.08) !important; border: 1px solid rgba(52,211,153,0.25) !important; border-radius: var(--radius-sm) !important; color: #6ee7b7 !important; }
.stWarning > div { background: rgba(251,191,36,0.08) !important; border: 1px solid rgba(251,191,36,0.25) !important; border-radius: var(--radius-sm) !important; color: #fcd34d !important; }
.stError > div   { background: rgba(244,114,182,0.08) !important; border: 1px solid rgba(244,114,182,0.25) !important; border-radius: var(--radius-sm) !important; color: #fca5a5 !important; }
.stInfo > div    { background: rgba(100,108,255,0.08) !important; border: 1px solid rgba(100,108,255,0.25) !important; border-radius: var(--radius-sm) !important; color: #a5b4fc !important; }

/* ════════════════════════════════
   PROGRESS BAR
════════════════════════════════ */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg,#4f46e5,#7c3aed,#f472b6) !important;
    border-radius: 99px !important;
    box-shadow: 0 0 10px rgba(100,108,255,0.4) !important;
}
.stProgress > div > div { background: rgba(100,108,255,0.1) !important; border-radius: 99px !important; }

/* ════════════════════════════════
   CODE BLOCKS
════════════════════════════════ */
.stCode, [data-testid="stCode"] {
    background: #04040f !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
.stCode code { color: #e2e8f0 !important; font-size: 13px !important; font-family: var(--font-mono) !important; }

/* ════════════════════════════════
   CUSTOM NOTIFICATIONS
════════════════════════════════ */
.somo-notify {
    background: linear-gradient(135deg, rgba(100,108,255,0.12), rgba(167,139,250,0.08));
    border: 1px solid rgba(100,108,255,0.3);
    border-radius: var(--radius);
    padding: 14px 20px;
    color: #c7d2fe;
    font-weight: 600;
    font-size: 14px;
    margin: 12px 0;
    animation: slide-in 0.35s ease;
    display: flex;
    align-items: center;
    gap: 10px;
}
.somo-success {
    background: linear-gradient(135deg, rgba(52,211,153,0.12), rgba(5,150,105,0.08));
    border: 1px solid rgba(52,211,153,0.3);
    color: #6ee7b7;
    border-radius: var(--radius);
    padding: 14px 20px;
    font-weight: 600;
    font-size: 14px;
    margin: 12px 0;
    animation: slide-in 0.35s ease;
}
@keyframes slide-in { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }

/* ════════════════════════════════
   API SELECTOR TABS (custom)
════════════════════════════════ */
.api-selector {
    display: flex;
    gap: 8px;
    padding: 6px;
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 16px;
    flex-wrap: wrap;
}
.api-option {
    flex: 1;
    padding: 8px 14px;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-weight: 600;
    font-family: var(--font-mono);
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
    min-width: 80px;
}
.api-option.active-groq    { background: rgba(251,191,36,0.15); color:#fbbf24; border-color: rgba(251,191,36,0.35); }
.api-option.active-gemini  { background: rgba(52,211,153,0.15); color:#34d399; border-color: rgba(52,211,153,0.35); }
.api-option.active-cohere  { background: rgba(56,189,248,0.15); color:#38bdf8; border-color: rgba(56,189,248,0.35); }
.api-option.active-mistral { background: rgba(244,114,182,0.15);color:#f472b6; border-color: rgba(244,114,182,0.35); }

/* ════════════════════════════════
   TEMPLATE CARDS
════════════════════════════════ */
.tmpl-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px;
    margin-bottom: 14px;
    transition: all 0.25s;
    position: relative;
    overflow: hidden;
}
.tmpl-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
    border-radius: 3px 0 0 3px;
}
.tmpl-card:hover { border-color: var(--border-h); transform: translateX(4px); box-shadow: 0 8px 30px rgba(0,0,0,0.4); }
.tmpl-tag { display: inline-block; padding: 3px 12px; border-radius: 99px; font-size: 10px; font-weight: 700; letter-spacing: 1px; margin-bottom: 10px; font-family: var(--font-mono); }
.tag-excel  { background: rgba(52,211,153,0.12); color:#34d399; border:1px solid rgba(52,211,153,0.25); }
.tag-word   { background: rgba(56,189,248,0.12);  color:#38bdf8; border:1px solid rgba(56,189,248,0.25); }
.tag-code   { background: rgba(251,191,36,0.12);  color:#fbbf24; border:1px solid rgba(251,191,36,0.25); }
.tag-html   { background: rgba(244,114,182,0.12); color:#f472b6; border:1px solid rgba(244,114,182,0.25); }
.tag-csv    { background: rgba(167,139,250,0.12); color:#a78bfa; border:1px solid rgba(167,139,250,0.25); }
.tmpl-title { font-size: 15px; font-weight: 700; color: var(--text-1); margin-bottom: 5px; font-family: var(--font-head); }
.tmpl-desc  { font-size: 12px; color: var(--text-3); line-height: 1.55; }

/* ════════════════════════════════
   HISTORY
════════════════════════════════ */
.hist-msg { border-left: 3px solid; border-radius: 0 var(--radius) var(--radius) 0; padding: 12px 16px; margin: 8px 0; font-size: 13px; }
.hist-user { background: rgba(100,108,255,0.07); border-color: var(--accent); }
.hist-ai   { background: rgba(52,211,153,0.06);  border-color: var(--accent-4); }
.hist-role { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 5px; font-family: var(--font-mono); }
.hist-user .hist-role { color: #818cf8; }
.hist-ai   .hist-role { color: #34d399; }
.hist-body { color: var(--text-2); line-height: 1.55; }

/* ════════════════════════════════
   PROFILE
════════════════════════════════ */
.profile-stat { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 22px 18px; text-align: center; transition: border-color 0.3s; }
.profile-stat:hover { border-color: var(--border-h); }
.p-stat-icon { font-size: 26px; margin-bottom: 10px; }
.p-stat-val  { font-size: 30px; font-weight: 900; color: var(--text-1); font-family: var(--font-head); }
.p-stat-lbl  { font-size: 10px; color: var(--text-3); text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; margin-top: 4px; font-family: var(--font-mono); }

/* ════════════════════════════════
   FOOTER
════════════════════════════════ */
.somo-footer { text-align: center; padding: 48px 20px 24px; border-top: 1px solid var(--border); margin-top: 64px; }
.somo-footer .f-title { font-size: 20px; font-weight: 800; color: var(--text-1); margin-bottom: 10px; font-family: var(--font-head); letter-spacing: -0.5px; }
.somo-footer .f-sub   { font-size: 13px; color: var(--text-3); margin-bottom: 5px; }
.somo-footer .f-copy  { font-size: 11px; color: #2a2a40; margin-top: 18px; font-family: var(--font-mono); }

/* ════════════════════════════════
   SIDEBAR TOGGLE BUTTON
════════════════════════════════ */
/* Hide Streamlit's default collapse arrow, we use our own */
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Our custom toggle button - always visible */
#somo-sidebar-toggle {
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 9999;
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg, #0f0f22, #14142a);
    border: 1px solid rgba(100,108,255,0.35);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5), 0 0 15px rgba(100,108,255,0.15);
    transition: all 0.25s cubic-bezier(.4,0,.2,1);
    -webkit-tap-highlight-color: transparent;
    user-select: none;
}
#somo-sidebar-toggle:hover {
    border-color: rgba(100,108,255,0.7);
    box-shadow: 0 4px 20px rgba(0,0,0,0.5), 0 0 25px rgba(100,108,255,0.35);
    transform: scale(1.05);
    background: linear-gradient(135deg, #13133a, #1a1440);
}
#somo-sidebar-toggle:active { transform: scale(0.96); }

.toggle-icon {
    display: flex;
    flex-direction: column;
    gap: 4.5px;
    width: 18px;
}
.toggle-icon span {
    display: block;
    height: 2px;
    background: #818cf8;
    border-radius: 2px;
    transition: all 0.3s ease;
}
.toggle-icon span:nth-child(1) { width: 18px; }
.toggle-icon span:nth-child(2) { width: 12px; }
.toggle-icon span:nth-child(3) { width: 16px; }
#somo-sidebar-toggle:hover .toggle-icon span { background: #c7d2fe; }
#somo-sidebar-toggle:hover .toggle-icon span:nth-child(2) { width: 18px; }

/* ════════════════════════════════
   BOTTOM MOBILE NAV BAR
════════════════════════════════ */
#somo-bottom-nav {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 8888;
    background: linear-gradient(180deg, rgba(9,9,30,0.95), rgba(7,7,26,0.98));
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-top: 1px solid rgba(100,108,255,0.2);
    padding: 8px 4px 12px;
    box-shadow: 0 -10px 40px rgba(0,0,0,0.5);
}
.bnav-items {
    display: flex;
    justify-content: space-around;
    align-items: center;
    gap: 2px;
    max-width: 480px;
    margin: 0 auto;
}
.bnav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    padding: 6px 8px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
    flex: 1;
    max-width: 64px;
    -webkit-tap-highlight-color: transparent;
}
.bnav-item:active { transform: scale(0.9); }
.bnav-icon { font-size: 20px; line-height: 1; }
.bnav-label { font-size: 9px; color: #3d4060; font-weight: 600; letter-spacing: 0.3px; text-align: center; font-family: 'Inter', sans-serif; }
.bnav-item.bnav-active .bnav-label { color: #818cf8; }
.bnav-item.bnav-active { background: rgba(100,108,255,0.12); }

/* ════════════════════════════════
   MOBILE FULL RESPONSIVE
════════════════════════════════ */
@media(max-width: 768px) {
    /* Main content padding */
    section[data-testid="stMainBlockContainer"] {
        padding: 56px 12px 110px !important;
    }

    /* Hero */
    .somo-hero {
        padding: 28px 18px !important;
        border-radius: 18px !important;
        margin-bottom: 20px !important;
    }
    .somo-hero h1 { font-size: clamp(22px, 6vw, 32px) !important; letter-spacing: -0.8px !important; }
    .somo-hero .subtitle { font-size: 13.5px !important; line-height: 1.6 !important; margin-bottom: 16px !important; }
    .hero-badge { font-size: 10.5px !important; padding: 4px 10px !important; }

    /* Cards - 2 per row on mobile */
    .cards-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 10px !important;
        margin-bottom: 20px !important;
    }
    .somo-card { padding: 18px 12px !important; border-radius: 14px !important; }
    .card-icon { font-size: 26px !important; margin-bottom: 8px !important; }
    .card-title { font-size: 12px !important; }
    .card-desc { font-size: 10px !important; }

    /* Stat row - 2 per row */
    .stat-row {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 8px !important;
    }
    .stat-val { font-size: 22px !important; }
    .stat-lbl { font-size: 9px !important; }

    /* Sidebar hide on mobile, show bottom nav */
    [data-testid="stSidebar"] {
        width: 100% !important;
        max-width: 280px !important;
    }

    /* Bottom nav visible on mobile */
    #somo-bottom-nav { display: block !important; }

    /* Section titles */
    .section-title { font-size: 20px !important; }

    /* Template cards */
    .tmpl-card { padding: 16px !important; }
    .tmpl-title { font-size: 13px !important; }
    .tmpl-desc { font-size: 11px !important; }

    /* Text areas */
    .stTextArea textarea { font-size: 14px !important; }

    /* Buttons full width on mobile */
    .stButton > button { font-size: 13px !important; padding: 9px 14px !important; }

    /* History messages */
    .hist-msg { font-size: 12px !important; padding: 10px 12px !important; }

    /* Chat input */
    [data-testid="stChatInput"] textarea { font-size: 14px !important; }

    /* Forms */
    [data-testid="stForm"] { padding: 18px !important; border-radius: 14px !important; }

    /* Profile stats - 2 per row */
    .profile-stat { padding: 16px 12px !important; }
    .p-stat-val { font-size: 24px !important; }

    /* Footer */
    .somo-footer { padding: 28px 16px 16px !important; margin-top: 30px !important; }
    .somo-footer .f-title { font-size: 16px !important; }

    /* API badges row */
    .api-selector { gap: 6px !important; }
    .api-option { min-width: 60px !important; font-size: 10px !important; padding: 6px 8px !important; }

    /* Divider */
    .somo-divider { margin: 18px 0 !important; }
}

@media(max-width: 480px) {
    section[data-testid="stMainBlockContainer"] { padding: 52px 10px 105px !important; }
    .somo-hero { padding: 22px 14px !important; border-radius: 14px !important; }
    .somo-hero h1 { font-size: 20px !important; }
    .somo-hero .subtitle { font-size: 12.5px !important; }
    .cards-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 8px !important; }
    .somo-card { padding: 14px 10px !important; border-radius: 12px !important; }
    .card-icon { font-size: 22px !important; }
    .card-title { font-size: 11px !important; }
    .card-desc { font-size: 9.5px !important; }
    .stat-val { font-size: 20px !important; }
}

/* Tablet */
@media(min-width: 769px) and (max-width: 1024px) {
    section[data-testid="stMainBlockContainer"] { padding: 20px 20px 70px !important; }
    .cards-grid { grid-template-columns: repeat(3, 1fr) !important; }
    .somo-hero { padding: 40px 36px !important; }
    .somo-hero h1 { font-size: 36px !important; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SIDEBAR TOGGLE BUTTON + MOBILE BOTTOM NAV
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div id="somo-sidebar-toggle" onclick="somoToggleSidebar()" title="Sidebar ochish/yopish">
    <div class="toggle-icon">
        <span></span><span></span><span></span>
    </div>
</div>

<div id="somo-bottom-nav">
    <div class="bnav-items">
        <div class="bnav-item bnav-active" onclick="somoSetPage('home')" id="bnav-home">
            <div class="bnav-icon">🏠</div><div class="bnav-label">Bosh</div>
        </div>
        <div class="bnav-item" onclick="somoSetPage('chat')" id="bnav-chat">
            <div class="bnav-icon">💬</div><div class="bnav-label">Chat</div>
        </div>
        <div class="bnav-item" onclick="somoSetPage('excel')" id="bnav-excel">
            <div class="bnav-icon">📊</div><div class="bnav-label">Excel</div>
        </div>
        <div class="bnav-item" onclick="somoSetPage('word')" id="bnav-word">
            <div class="bnav-icon">📝</div><div class="bnav-label">Word</div>
        </div>
        <div class="bnav-item" onclick="somoSetPage('code')" id="bnav-code">
            <div class="bnav-icon">💻</div><div class="bnav-label">Kod</div>
        </div>
        <div class="bnav-item" onclick="somoToggleMoreMenu()" id="bnav-more">
            <div class="bnav-icon">☰</div><div class="bnav-label">Ko'proq</div>
        </div>
    </div>
</div>

<div id="somo-more-menu" style="display:none;position:fixed;bottom:72px;left:10px;right:10px;z-index:9990;
     background:linear-gradient(145deg,#09091e,#0d0d22);border:1px solid rgba(100,108,255,0.25);
     border-radius:18px;padding:16px;box-shadow:0 -10px 40px rgba(0,0,0,0.7);backdrop-filter:blur(20px);">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:4px;">
        <div onclick="somoSetPage('html');somoToggleMoreMenu();" style="text-align:center;padding:12px 4px;border-radius:12px;background:rgba(100,108,255,0.07);border:1px solid rgba(100,108,255,0.15);cursor:pointer;-webkit-tap-highlight-color:transparent;">
            <div style="font-size:22px;">🌐</div><div style="font-size:9.5px;color:#64748b;margin-top:4px;font-weight:700;">HTML</div></div>
        <div onclick="somoSetPage('csv');somoToggleMoreMenu();" style="text-align:center;padding:12px 4px;border-radius:12px;background:rgba(100,108,255,0.07);border:1px solid rgba(100,108,255,0.15);cursor:pointer;-webkit-tap-highlight-color:transparent;">
            <div style="font-size:22px;">📋</div><div style="font-size:9.5px;color:#64748b;margin-top:4px;font-weight:700;">CSV</div></div>
        <div onclick="somoSetPage('templates');somoToggleMoreMenu();" style="text-align:center;padding:12px 4px;border-radius:12px;background:rgba(100,108,255,0.07);border:1px solid rgba(100,108,255,0.15);cursor:pointer;-webkit-tap-highlight-color:transparent;">
            <div style="font-size:22px;">🎨</div><div style="font-size:9.5px;color:#64748b;margin-top:4px;font-weight:700;">Shablon</div></div>
        <div onclick="somoSetPage('analyze');somoToggleMoreMenu();" style="text-align:center;padding:12px 4px;border-radius:12px;background:rgba(100,108,255,0.07);border:1px solid rgba(100,108,255,0.15);cursor:pointer;-webkit-tap-highlight-color:transparent;">
            <div style="font-size:22px;">🔍</div><div style="font-size:9.5px;color:#64748b;margin-top:4px;font-weight:700;">Tahlil</div></div>
        <div onclick="somoSetPage('history');somoToggleMoreMenu();" style="text-align:center;padding:12px 4px;border-radius:12px;background:rgba(100,108,255,0.07);border:1px solid rgba(100,108,255,0.15);cursor:pointer;-webkit-tap-highlight-color:transparent;">
            <div style="font-size:22px;">📜</div><div style="font-size:9.5px;color:#64748b;margin-top:4px;font-weight:700;">Tarix</div></div>
        <div onclick="somoSetPage('feedback');somoToggleMoreMenu();" style="text-align:center;padding:12px 4px;border-radius:12px;background:rgba(100,108,255,0.07);border:1px solid rgba(100,108,255,0.15);cursor:pointer;-webkit-tap-highlight-color:transparent;">
            <div style="font-size:22px;">💌</div><div style="font-size:9.5px;color:#64748b;margin-top:4px;font-weight:700;">Fikr</div></div>
        <div onclick="somoSetPage('profile');somoToggleMoreMenu();" style="text-align:center;padding:12px 4px;border-radius:12px;background:rgba(100,108,255,0.07);border:1px solid rgba(100,108,255,0.15);cursor:pointer;-webkit-tap-highlight-color:transparent;">
            <div style="font-size:22px;">👤</div><div style="font-size:9.5px;color:#64748b;margin-top:4px;font-weight:700;">Profil</div></div>
        <div onclick="somoToggleMoreMenu();" style="text-align:center;padding:12px 4px;border-radius:12px;background:rgba(244,114,182,0.07);border:1px solid rgba(244,114,182,0.2);cursor:pointer;-webkit-tap-highlight-color:transparent;">
            <div style="font-size:22px;color:#f472b6;">✕</div><div style="font-size:9.5px;color:#f472b6;margin-top:4px;font-weight:700;">Yopish</div></div>
    </div>
</div>

<script>
(function() {

// ── Sidebar toggle ──────────────────────────────────────
window.somoToggleSidebar = function() {
    try {
        var doc = window.parent.document;
        var sidebar = doc.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) return;

        // Get current visibility state
        var sidebarRect = sidebar.getBoundingClientRect();
        var isVisible = sidebarRect.left >= -10;

        // Apply transition
        sidebar.style.transition = 'transform 0.32s cubic-bezier(.4,0,.2,1)';
        sidebar.style.position = 'fixed';
        sidebar.style.zIndex = '9990';
        sidebar.style.height = '100vh';
        sidebar.style.top = '0';

        if (isVisible) {
            // Hide sidebar
            sidebar.style.transform = 'translateX(-110%)';
            // Show open button indicator
            var toggle = document.getElementById('somo-sidebar-toggle');
            if (toggle) {
                toggle.style.background = 'linear-gradient(135deg, #1a1440, #2a1a60)';
                toggle.style.borderColor = 'rgba(100,108,255,0.6)';
                toggle.setAttribute('data-open', '0');
                toggle.title = 'Sidebar ochish';
            }
        } else {
            // Show sidebar
            sidebar.style.transform = 'translateX(0)';
            var toggle2 = document.getElementById('somo-sidebar-toggle');
            if (toggle2) {
                toggle2.style.background = 'linear-gradient(135deg, #0f0f22, #14142a)';
                toggle2.style.borderColor = 'rgba(100,108,255,0.35)';
                toggle2.setAttribute('data-open', '1');
                toggle2.title = 'Sidebar yopish';
            }
        }

        // On mobile, click outside to close
        if (window.innerWidth <= 768 && !isVisible) {
            doc.addEventListener('click', function closeSidebar(e) {
                if (!sidebar.contains(e.target) && e.target.id !== 'somo-sidebar-toggle') {
                    sidebar.style.transform = 'translateX(-110%)';
                    doc.removeEventListener('click', closeSidebar);
                }
            }, { once: false });
        }
    } catch(e) { console.warn('Sidebar toggle error:', e); }
};

// ── Mobile bottom nav page switch ──────────────────────
window.somoSetPage = function(pageName) {
    var iconMap = {
        'home':'🏠','chat':'💬','excel':'📊','word':'📝',
        'code':'💻','html':'🌐','csv':'📋','templates':'🎨',
        'analyze':'🔍','history':'📜','feedback':'💌','profile':'👤'
    };
    var icon = iconMap[pageName];
    if (!icon) return;
    try {
        var doc = window.parent.document;
        var buttons = doc.querySelectorAll('[data-testid="stSidebar"] button');
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].textContent.trim().charAt(0) === icon) {
                buttons[i].click();
                break;
            }
        }
    } catch(e) { console.warn('setPage:', e); }

    // Update active state
    var items = document.querySelectorAll('.bnav-item');
    for (var j = 0; j < items.length; j++) { items[j].classList.remove('bnav-active'); }
    var el = document.getElementById('bnav-' + pageName);
    if (el) el.classList.add('bnav-active');

    // Close more menu
    var menu = document.getElementById('somo-more-menu');
    if (menu) menu.style.display = 'none';
};

// ── More menu toggle ────────────────────────────────────
window.somoToggleMoreMenu = function() {
    var menu = document.getElementById('somo-more-menu');
    if (!menu) return;
    if (menu.style.display === 'none' || !menu.style.display) {
        menu.style.display = 'block';
    } else {
        menu.style.display = 'none';
    }
};

// Close more menu on outside tap
document.addEventListener('touchstart', function(e) {
    var menu = document.getElementById('somo-more-menu');
    var moreBtn = document.getElementById('bnav-more');
    if (menu && menu.style.display !== 'none') {
        if (!menu.contains(e.target) && moreBtn && !moreBtn.contains(e.target)) {
            menu.style.display = 'none';
        }
    }
}, { passive: true });

// ── Responsive check ────────────────────────────────────
function somoCheckMobile() {
    var w = window.innerWidth;
    var nav = document.getElementById('somo-bottom-nav');
    var toggle = document.getElementById('somo-sidebar-toggle');
    if (nav) nav.style.display = (w <= 768) ? 'block' : 'none';
    if (toggle) {
        toggle.style.top    = (w <= 768) ? '8px'  : '14px';
        toggle.style.left   = (w <= 768) ? '8px'  : '14px';
        toggle.style.width  = (w <= 768) ? '38px' : '42px';
        toggle.style.height = (w <= 768) ? '38px' : '42px';
    }
}
somoCheckMobile();
window.addEventListener('resize', somoCheckMobile);

})();
</script>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# API CLIENTS SETUP
# ══════════════════════════════════════════════════════════════════
API_CONFIGS = {
    "groq": {
        "name": "Groq",
        "icon": "⚡",
        "model": "llama-3.3-70b-versatile",
        "color": "#fbbf24",
        "badge_class": "api-groq",
        "desc": "Llama 3.3 · 70B · Ultra Fast"
    },
    "gemini": {
        "name": "Gemini",
        "icon": "✨",
        "model": "gemini-2.0-flash",
        "color": "#34d399",
        "badge_class": "api-gemini",
        "desc": "Google Gemini · 1.5 Flash"
    },
    "cohere": {
        "name": "Cohere",
        "icon": "🔮",
        "model": "command-r-plus",
        "color": "#38bdf8",
        "badge_class": "api-cohere",
        "desc": "Command R+ · Reasoning"
    },
    "mistral": {
        "name": "Mistral",
        "icon": "🌪",
        "model": "mistral-large-latest",
        "color": "#f472b6",
        "badge_class": "api-mistral",
        "desc": "Mistral Large · EU Based"
    }
}

def _get_secret(key):
    """Safely get API key from secrets — multiple formats supported."""
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
    import os
    return str(os.environ.get(key,"")).strip()

# Initialize clients
@st.cache_resource
def init_clients():
    clients = {}

    # Groq
    if HAS_GROQ:
        try:
            key = _get_secret("GROQ_API_KEY")
            if key: clients["groq"] = Groq(api_key=key)
        except: pass

    # Gemini
    if HAS_GEMINI:
        for model_name in ["gemini-2.0-flash","gemini-2.0-flash","gemini-pro"]:
            try:
                key = _get_secret("GEMINI_API_KEY")
                if key:
                    genai.configure(api_key=key)
                    clients["gemini"] = genai.GenerativeModel(model_name)
                    break
            except Exception as e:
                if "not found" in str(e).lower() or "404" in str(e):
                    continue
                break

    # Cohere
    if HAS_COHERE:
        try:
            key = _get_secret("COHERE_API_KEY")
            if key: clients["cohere"] = cohere.Client(api_key=key)
        except: pass

    # Mistral
    if HAS_MISTRAL:
        try:
            key = _get_secret("MISTRAL_API_KEY")
            if key: clients["mistral"] = Mistral(api_key=key)
        except: pass

    return clients

ai_clients = init_clients()

# ══════════════════════════════════════════════════════════════════
# CALL AI FUNCTION — multi-API dispatcher
# ══════════════════════════════════════════════════════════════════
def call_ai(messages, temperature=0.6, max_tokens=3000, provider="groq"):
    """Call the selected AI provider. Falls back through providers if needed."""
    # Choose provider with fallback
    providers_order = [provider] + [p for p in ["groq","gemini","cohere","mistral"] if p != provider]

    for prov in providers_order:
        if prov not in ai_clients:
            continue
        try:
            if prov == "groq":
                resp = ai_clients["groq"].chat.completions.create(
                    messages=messages,
                    model=API_CONFIGS["groq"]["model"],
                    temperature=min(temperature, 1.0),
                    max_tokens=max_tokens
                )
                return resp.choices[0].message.content, "groq"

            elif prov == "gemini":
                # Convert to Gemini format
                sys_msg = next((m["content"] for m in messages if m["role"]=="system"), "")
                user_msgs = [m for m in messages if m["role"] != "system"]
                chat_hist = []
                for m in user_msgs[:-1]:
                    role = "user" if m["role"]=="user" else "model"
                    chat_hist.append({"role": role, "parts": [m["content"]]})
                last_msg = user_msgs[-1]["content"] if user_msgs else ""
                if sys_msg:
                    last_msg = f"[System: {sys_msg}]\n\n{last_msg}"
                chat = ai_clients["gemini"].start_chat(history=chat_hist)
                resp = chat.send_message(last_msg)
                return resp.text, "gemini"

            elif prov == "cohere":
                sys_msg = next((m["content"] for m in messages if m["role"]=="system"), "")
                user_msgs = [m for m in messages if m["role"] != "system"]
                chat_hist = []
                for m in user_msgs[:-1]:
                    role = "USER" if m["role"]=="user" else "CHATBOT"
                    chat_hist.append({"role": role, "message": m["content"]})
                last_msg = user_msgs[-1]["content"] if user_msgs else ""
                resp = ai_clients["cohere"].chat(
                    model=API_CONFIGS["cohere"]["model"],
                    message=last_msg,
                    chat_history=chat_hist,
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

    return "❌ Hech bir AI xizmati mavjud emas yoki xatolik yuz berdi.", "none"

def call_ai_stream(messages, temperature=0.6, max_tokens=3000, provider="groq"):
    """Streaming version — yields text chunks. Falls back to non-stream if needed."""
    providers_order = [provider] + [p for p in ["groq","gemini","cohere","mistral"] if p != provider]

    for prov in providers_order:
        if prov not in ai_clients:
            continue
        try:
            if prov == "groq":
                stream = ai_clients["groq"].chat.completions.create(
                    messages=messages,
                    model=API_CONFIGS["groq"]["model"],
                    temperature=min(temperature, 1.0),
                    max_tokens=max_tokens,
                    stream=True
                )
                full = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        yield chunk.choices[0].delta.content, "groq"
                return

            elif prov == "gemini":
                sys_msg = next((m["content"] for m in messages if m["role"]=="system"), "")
                user_msgs = [m for m in messages if m["role"] != "system"]
                chat_hist = []
                for m in user_msgs[:-1]:
                    role = "user" if m["role"]=="user" else "model"
                    chat_hist.append({"role": role, "parts": [m["content"]]})
                last_msg = user_msgs[-1]["content"] if user_msgs else ""
                if sys_msg:
                    last_msg = f"[System: {sys_msg}]\n\n{last_msg}"
                chat = ai_clients["gemini"].start_chat(history=chat_hist)
                resp = chat.send_message(last_msg, stream=True)
                for chunk in resp:
                    if chunk.text:
                        yield chunk.text, "gemini"
                return

            elif prov == "cohere":
                # Cohere supports streaming too
                sys_msg = next((m["content"] for m in messages if m["role"]=="system"), "")
                user_msgs = [m for m in messages if m["role"] != "system"]
                chat_hist = []
                for m in user_msgs[:-1]:
                    role = "USER" if m["role"]=="user" else "CHATBOT"
                    chat_hist.append({"role": role, "message": m["content"]})
                last_msg = user_msgs[-1]["content"] if user_msgs else ""
                resp = ai_clients["cohere"].chat_stream(
                    model=API_CONFIGS["cohere"]["model"],
                    message=last_msg,
                    chat_history=chat_hist,
                    preamble=sys_msg if sys_msg else None,
                    temperature=min(temperature, 1.0),
                    max_tokens=max_tokens
                )
                for event in resp:
                    if hasattr(event, 'text') and event.text:
                        yield event.text, "cohere"
                return

            elif prov == "mistral":
                stream = ai_clients["mistral"].chat.stream(
                    model=API_CONFIGS["mistral"]["model"],
                    messages=messages,
                    temperature=min(temperature, 1.0),
                    max_tokens=max_tokens
                )
                for chunk in stream:
                    delta = chunk.data.choices[0].delta.content
                    if delta:
                        yield delta, "mistral"
                return

        except Exception as e:
            # fallback to next
            continue

    yield "❌ Xatolik yuz berdi.", "none"

# ══════════════════════════════════════════════════════════════════
# DB & UTILITY
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
            chat_sheet = ss.add_worksheet("ChatHistory", 5000, 6)
            chat_sheet.append_row(["Timestamp","Username","Role","Message","Intent","Provider"])
        try:
            fb_sheet = ss.worksheet("Letters")
        except:
            fb_sheet = ss.add_worksheet("Letters", 1000, 8)
            fb_sheet.append_row(["Timestamp","Username","Rating","Category","Message","Email","Status","Files"])
        return user_sheet, chat_sheet, fb_sheet
    except Exception as e:
        return None, None, None

user_db, chat_db, fb_db = get_connections()

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

def db_log(user, role, content, intent="chat", provider="groq"):
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

MIME = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "py":   "text/x-python",
    "html": "text/html",
    "csv":  "text/csv"
}

# ══════════════════════════════════════════════════════════════════
# FILE GENERATORS — use appropriate API per type
# ══════════════════════════════════════════════════════════════════
def gen_excel(prompt, temp=0.15, provider="groq"):
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
- Kamida 15-20 satr haqiqiy ma'lumot
- Excel formulalar: SUM, AVERAGE, IF, MAX, MIN, VLOOKUP
- Har bir varaq foydali va ma'noli
- FAQAT JSON, markdown yoki izoh yo'q"""

    raw, _ = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temp, max_tokens=4000, provider=provider)
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
        ("4F46E5","EEF2FF"),("059669","ECFDF5"),("D97706","FFFBEB"),
        ("DC2626","FEF2F2"),("0891B2","ECFEFF"),("7C3AED","F5F3FF")
    ]
    for si, sh in enumerate(data.get("sheets",[])):
        ws = wb.create_sheet(title=sh.get("name","Sheet")[:31])
        headers  = sh.get("headers",[])
        hcolor   = sh.get("header_color", PALETTES[si%len(PALETTES)][0])
        _, rcolor= PALETTES[si%len(PALETTES)]
        rows     = sh.get("rows",[])
        widths   = sh.get("col_widths",[])
        rh       = sh.get("row_height",20)

        if headers:
            end_col = max(len(headers),1)
            ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=end_col)
            tc = ws.cell(row=1,column=1,value=sh.get("name","Hisobot"))
            tc.font = Font(name="Calibri",bold=True,size=13,color="FFFFFF")
            tc.fill = PatternFill("solid",fgColor=hcolor)
            tc.alignment = Alignment(horizontal="center",vertical="center")
            ws.row_dimensions[1].height = 30

        if headers:
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
                if isinstance(val,str) and val.startswith("="):
                    c.value = val
                else:
                    try:
                        if isinstance(val,str) and re.match(r'^-?\d+(\.\d+)?$',val.strip()):
                            v = float(val)
                            c.value = int(v) if v==int(v) else v
                        else: c.value = val
                    except: c.value = val
                c.fill = PatternFill("solid",fgColor=bg)
                c.border = Border(left=td,right=td,top=td,bottom=td)
                c.font = Font(name="Calibri",size=10)
                c.alignment = Alignment(vertical="center",wrap_text=True)
            ws.row_dimensions[ri].height = rh

        for ci,w in enumerate(widths,1):
            ws.column_dimensions[get_column_letter(ci)].width = max(int(w),8)
        if not widths and headers:
            for ci in range(1,len(headers)+1):
                ws.column_dimensions[get_column_letter(ci)].width = 18
        ws.freeze_panes = "A3"

    if not wb.sheetnames:
        wb.create_sheet("Ma'lumotlar")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    safe = re.sub(r'[^\w\s-]','',data.get("title","somo")).strip().replace(' ','_')
    fname = f"{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return buf.getvalue(), fname


def gen_word(prompt, temp=0.4, provider="mistral"):
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
Muhim: Mazmunli, haqiqiy va to'liq kontent. Kamida 10-14 bo'lim. Faqat JSON."""

    raw, _ = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temp, max_tokens=4000, provider=provider)
    raw = re.sub(r'```json|```','',raw).strip()
    m = re.search(r'\{.*\}',raw,re.DOTALL)
    if not m: return None, "Struktura topilmadi"
    try: data = json.loads(m.group())
    except Exception as e: return None, f"JSON: {e}"

    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Cm(2.5); sec.bottom_margin = Cm(2.5)
        sec.left_margin = Cm(3); sec.right_margin = Cm(2.5)

    tp = doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = tp.add_run(data.get("title","Hujjat"))
    run.bold = True; run.font.size = Pt(20)
    run.font.color.rgb = RGBColor(0x4F,0x46,0xE5)
    run.font.name = "Calibri"
    tp.paragraph_format.space_after = Pt(4)

    dp = doc.add_paragraph()
    dp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    dr = dp.add_run(f"{datetime.now().strftime('%d.%m.%Y')} — Somo AI")
    dr.font.size = Pt(10); dr.font.color.rgb = RGBColor(0x94,0xA3,0xB8)
    dr.font.name = "Calibri"
    dp.paragraph_format.space_after = Pt(18)

    for sec in data.get("sections",[]):
        t = sec.get("type","paragraph")
        if t == "heading1":
            h = doc.add_heading(sec.get("text",""),level=1)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x4F,0x46,0xE5); h.runs[0].font.name = "Calibri"
        elif t == "heading2":
            h = doc.add_heading(sec.get("text",""),level=2)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x7C,0x3A,0xED); h.runs[0].font.name = "Calibri"
        elif t == "heading3":
            h = doc.add_heading(sec.get("text",""),level=3)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x0E,0xA5,0xE9); h.runs[0].font.name = "Calibri"
        elif t == "paragraph":
            p = doc.add_paragraph()
            r = p.add_run(sec.get("text",""))
            r.font.size = Pt(11); r.font.name = "Calibri"
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = Pt(16)
        elif t == "bullet":
            for item in sec.get("items",[]):
                p = doc.add_paragraph(style='List Bullet')
                r = p.add_run(item); r.font.size = Pt(11); r.font.name = "Calibri"
        elif t == "numbered":
            for item in sec.get("items",[]):
                p = doc.add_paragraph(style='List Number')
                r = p.add_run(item); r.font.size = Pt(11); r.font.name = "Calibri"
        elif t == "table":
            hdrs = sec.get("headers",[]); rws = sec.get("rows",[])
            if hdrs:
                tbl = doc.add_table(rows=1+len(rws),cols=len(hdrs))
                tbl.style = 'Table Grid'
                hrow = tbl.rows[0]
                for ci,h in enumerate(hdrs):
                    cell = hrow.cells[ci]; cell.text = h
                    if cell.paragraphs[0].runs:
                        cell.paragraphs[0].runs[0].font.bold = True
                        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255,255,255)
                        cell.paragraphs[0].runs[0].font.name = "Calibri"
                        cell.paragraphs[0].runs[0].font.size = Pt(10)
                    from docx.oxml.ns import qn
                    from docx.oxml import OxmlElement
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
                                rcells[ci].paragraphs[0].runs[0].font.size = Pt(10)
                                rcells[ci].paragraphs[0].runs[0].font.name = "Calibri"
                doc.add_paragraph()
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    footer_sec = doc.sections[0].footer
    fp = footer_sec.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = fp.add_run(f"© {datetime.now().year} Somo AI Ultra Pro Max  |  {data.get('title','')}")
    fr.font.size = Pt(9); fr.font.color.rgb = RGBColor(0x94,0xA3,0xB8); fr.font.name = "Calibri"

    buf = io.BytesIO()
    doc.save(buf); buf.seek(0)
    safe = re.sub(r'[^\w\s-]','',data.get("title","somo")).strip().replace(' ','_')
    fname = f"{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    return buf.getvalue(), fname


def gen_code(prompt, temp=0.12, provider="cohere"):
    sys_p = """Sen tajribali Python dasturchi. Professional, to'liq ishlaydigan kod yoz.
FAQAT Python kodi ber — markdown, tushuntirma yo'q (kod ichidagi # izohlar yaxshi).
Kod clean, error handling bilan, best practices bo'yicha."""
    raw, _ = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temp, max_tokens=3500, provider=provider)
    raw = re.sub(r'```python|```py|```','',raw).strip()
    safe = re.sub(r'[^\w]','_',prompt[:30]).strip('_')
    return raw.encode('utf-8'), f"{safe}_{datetime.now().strftime('%H%M%S')}.py"


def gen_html(prompt, temp=0.5, provider="gemini"):
    sys_p = """Sen professional frontend developer. Chiroyli, zamonaviy, to'liq HTML/CSS/JS sahifa yarat.
Dark theme, Google Fonts, smooth animations, glassmorphism ishlat.
FAQAT HTML kodi ber, markdown yo'q."""
    raw, _ = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temp, max_tokens=4000, provider=provider)
    raw = re.sub(r'```html|```','',raw).strip()
    safe = re.sub(r'[^\w]','_',prompt[:25]).strip('_')
    return raw.encode('utf-8'), f"{safe}_{datetime.now().strftime('%H%M%S')}.html"


def gen_csv(prompt, temp=0.3, provider="mistral"):
    sys_p = """Sen ma'lumotlar mutaxassisi. Foydalanuvchi so'roviga asosan CSV formatda katta ma'lumot to'plami ber.
FAQAT CSV (vergul bilan ajratilgan). Birinchi satr sarlavha. Kamida 25 satr.
Hech qanday tushuntirma, markdown yoki qo'shimcha matn yo'q."""
    raw, _ = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temp, max_tokens=3000, provider=provider)
    raw = re.sub(r'```csv|```','',raw).strip()
    safe = re.sub(r'[^\w]','_',prompt[:25]).strip('_')
    return raw.encode('utf-8'), f"{safe}_{datetime.now().strftime('%H%M%S')}.csv"

# ══════════════════════════════════════════════════════════════════
# DOWNLOAD BLOCK
# ══════════════════════════════════════════════════════════════════
def download_block(file_bytes, fname, label):
    ext = fname.rsplit('.',1)[-1]
    mime = MIME.get(ext,"application/octet-stream")
    st.markdown(f'<div class="somo-success">✅ {label} fayl tayyor — yuklab olish uchun bosing</div>',
                unsafe_allow_html=True)
    st.download_button(f"⬇️  {fname}", file_bytes, fname, mime,
                       use_container_width=True, type="primary",
                       key=f"dl_{fname}_{time.time()}")

# ══════════════════════════════════════════════════════════════════
# API STATUS INDICATOR
# ══════════════════════════════════════════════════════════════════
def api_status_html(provider):
    cfg = API_CONFIGS.get(provider, API_CONFIGS["groq"])
    return f'<span class="api-badge {cfg["badge_class"]}"><span class="api-dot"></span>{cfg["icon"]} {cfg["name"]}</span>'

# ══════════════════════════════════════════════════════════════════
# SESSION RESTORE FROM COOKIE
# ══════════════════════════════════════════════════════════════════
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session") if HAS_COOKIES else None
    if session_user and user_db:
        try:
            recs = user_db.get_all_records()
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
            cookies["somo_user_session"] = ""
            cookies.save()
    except: pass
    keys = list(st.session_state.keys())
    for k in keys: del st.session_state[k]
    st.session_state.logged_in = False
    st.rerun()

# ══════════════════════════════════════════════════════════════════
# ████████████████   LOGIN PAGE   ████████████████
# ══════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div class="somo-hero" style="text-align:center; padding:72px 40px;">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#646cff;margin-bottom:14px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
                ✦ Next Generation AI Platform
            </p>
            <h1 style="font-size:clamp(38px,5.5vw,68px);font-weight:800;color:white;letter-spacing:-2.5px;margin-bottom:18px;">
                🌌 Somo AI
                <span class="g-text">Ultra Pro Max</span>
            </h1>
            <p style="font-size:17px;color:rgba(255,255,255,0.55);max-width:560px;margin:0 auto 30px;line-height:1.7;font-family:'Inter',sans-serif;">
                Excel · Word · Kod · HTML · CSV — To'rt xil AI bilan har qanday faylni yarating
            </p>
            <div class="hero-badges" style="justify-content:center; gap: 10px;" id="api-status-badges">
                <span class="api-badge api-groq"><span class="api-dot"></span>⚡ Groq / Llama 3.3</span>
                <span class="api-badge api-gemini"><span class="api-dot"></span>✨ Google Gemini</span>
                <span class="api-badge api-cohere"><span class="api-dot"></span>🔮 Cohere R+</span>
                <span class="api-badge api-mistral"><span class="api-dot"></span>🌪 Mistral Large</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Dynamic API status on login page
    _api_status_html = ""
    _api_defs = [
        ("groq", "api-groq", "⚡", "Groq · Llama 3.3"),
        ("gemini", "api-gemini", "✨", "Gemini 2.0"),
        ("cohere", "api-cohere", "🔮", "Cohere R+"),
        ("mistral", "api-mistral", "🌪", "Mistral Large"),
    ]
    _all_connected = True
    for _pkey, _pclass, _picon, _pname in _api_defs:
        _connected = _pkey in ai_clients
        if not _connected: _all_connected = False
        if _connected:
            _api_status_html += f'<span class="api-badge {_pclass}"><span class="api-dot"></span>{_picon} {_pname} ✅</span>'
        else:
            _api_status_html += f'<span style="display:inline-flex;align-items:center;gap:5px;padding:4px 12px;border-radius:99px;font-size:11px;font-weight:600;background:rgba(100,100,100,0.08);border:1px solid rgba(100,100,100,0.2);color:#4a4a6a;">{_picon} {_pname} ❌</span>'
    
    _status_msg = "✅ Barcha AI lar ulangan" if _all_connected else f"⚡ {len(ai_clients)}/4 AI ulangan"
    st.markdown(f"""
    <div style="text-align:center;margin:-16px 0 20px;padding:12px 20px;background:rgba(100,108,255,0.05);
                border-radius:14px;border:1px solid rgba(100,108,255,0.12);">
        <p style="font-size:11px;color:#646cff;font-weight:700;margin-bottom:10px;letter-spacing:1px;
                  text-transform:uppercase;font-family:'JetBrains Mono',monospace;">{_status_msg}</p>
        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px;">{_api_status_html}</div>
    </div>
    """, unsafe_allow_html=True)

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
                                    if rem and HAS_COOKIES:
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
                    if not agree:    st.error("❌ Shartlarga rozilik bering!")
                    elif len(nu)<3:  st.error("❌ Username kamida 3 belgi!")
                    elif len(np)<6:  st.error("❌ Parol kamida 6 belgi!")
                    elif np!=nc:     st.error("❌ Parollar mos emas!")
                    elif user_db:
                        try:
                            recs = user_db.get_all_records()
                            if any(r['username']==nu for r in recs):
                                st.error("❌ Bu username band!")
                            else:
                                user_db.append_row([nu,hash_pw(np),"active",str(datetime.now()),0])
                                st.balloons()
                                st.success("🎉 Muvaffaqiyatli! Endi «Kirish» bo'limiga o'ting.")
                        except Exception as e:
                            st.error(f"❌ {e}")

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
                    <p style="color:#50506a;font-size:11px;margin-top:4px;line-height:1.6;">Kod, Analitika<br>Command R+</p>
                </div>
                <div style="background:rgba(244,114,182,0.06);border:1px solid rgba(244,114,182,0.2);border-radius:12px;padding:14px;">
                    <p style="color:#f472b6;font-weight:700;font-size:12px;font-family:'JetBrains Mono',monospace;">🌪 MISTRAL</p>
                    <p style="color:#50506a;font-size:11px;margin-top:4px;line-height:1.6;">Word, CSV<br>Mistral Large</p>
                </div>
            </div>
            <p style="color:#334155;font-size:11px;margin-top:16px;font-family:'JetBrains Mono',monospace;">
                👨‍💻 Usmonov Sodiq &nbsp;|&nbsp; v3.0 &nbsp;|&nbsp; 2026
            </p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="somo-footer">
        <div class="f-title">🌌 Somo AI <span class="g-text">Ultra Pro Max</span></div>
        <div class="f-sub">⚡ Groq · ✨ Gemini · 🔮 Cohere · 🌪 Mistral</div>
        <div class="f-copy">© 2026 Somo AI — Barcha huquqlar himoyalangan · v3.0</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════
# SESSION DEFAULTS
# ══════════════════════════════════════════════════════════════════
DEFS = {
    'messages': [], 'total_msgs': 0, 'page': 'home',
    'uploaded_text': '', 'temp': 0.6, 'files_cnt': 0,
    'ai_style': 'Aqlli yordamchi', 'last_files': [],
    'selected_provider': 'groq',
    'chat_provider': 'groq',
    'excel_provider': 'groq',
    'word_provider': 'mistral',
    'code_provider': 'cohere',
    'html_provider': 'gemini',
    'csv_provider': 'mistral',
    'analyze_provider': 'gemini',
}
for k,v in DEFS.items():
    if k not in st.session_state: st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════
# ████████████  SIDEBAR  ████████████
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    uname = st.session_state.username
    avail_providers = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    
    st.markdown(f"""
    <div style="padding:22px 16px 18px;border-bottom:1px solid rgba(100,108,255,0.12);margin-bottom:6px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
            <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed,#f472b6);
                        width:44px;height:44px;border-radius:14px;flex-shrink:0;
                        display:flex;align-items:center;justify-content:center;
                        font-size:18px;font-weight:900;color:white;
                        box-shadow:0 0 20px rgba(100,108,255,0.4);">
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

    st.markdown('<p class="section-label" style="padding:10px 14px 4px;font-size:9px;">Navigatsiya</p>', unsafe_allow_html=True)
    for pid, icon, label in nav:
        is_active = st.session_state.page == pid
        if st.button(f"{icon}  {label}", key=f"nav_{pid}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = pid
            st.rerun()

    st.markdown('<hr class="somo-divider" style="margin:10px 0;">', unsafe_allow_html=True)

    if st.session_state.page == "chat":
        st.markdown('<p class="section-label" style="padding:0 14px 6px;font-size:9px;">Chat Sozlamalari</p>', unsafe_allow_html=True)
        provider_options = [(p, f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}") for p in avail_providers] if avail_providers else [("groq","⚡ Groq")]
        provider_keys = [p[0] for p in provider_options]
        provider_labels = [p[1] for p in provider_options]
        curr_idx = provider_keys.index(st.session_state.chat_provider) if st.session_state.chat_provider in provider_keys else 0
        sel = st.selectbox("🤖 AI Provider", provider_labels, index=curr_idx, key="chat_prov_sel")
        st.session_state.chat_provider = provider_keys[provider_labels.index(sel)]
        st.session_state.temp = st.slider("🌡  Ijodkorlik", 0.0, 1.0, st.session_state.temp, 0.05, key="temp_sl")
        st.session_state.ai_style = st.selectbox("💬  Uslub",
            ["Aqlli yordamchi","Do'stona","Rasmiy ekspert","Ijodkor","Texnik"], key="ai_sl")
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
    <div style="padding:14px 14px 8px;border-top:1px solid rgba(100,108,255,0.08);margin-top:6px;text-align:center;">
        <p style="font-size:9px;color:#2a2a40;line-height:1.7;font-family:'JetBrains Mono',monospace;">
            🌌 SOMO AI · v3.0<br>
            ⚡ GROQ · ✨ GEMINI · 🔮 COHERE · 🌪 MISTRAL<br>
            © 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    uname = st.session_state.username
    avail = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]

    st.markdown(f"""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#646cff;margin-bottom:12px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
                ✦ Somo AI Ultra Pro Max v3.0
            </p>
            <h1>Salom, <span class="g-text">{uname}</span>! 👋</h1>
            <p class="subtitle">
                Bugun nima yaratmoqchisiz? To'rt xil AI bilan — Excel, Word, Kod, HTML, CSV — hammasini bir joyda.
            </p>
            <div class="hero-badges">
                {''.join([f'<span class="api-badge {API_CONFIGS[p]["badge_class"]}"><span class="api-dot"></span>{API_CONFIGS[p]["icon"]} {API_CONFIGS[p]["name"]}</span>' for p in avail])}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    mins = (datetime.now()-st.session_state.login_time).seconds//60 if 'login_time' in st.session_state else 0
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box"><div class="stat-icon">💬</div><div class="stat-val">{len(st.session_state.messages)}</div><div class="stat-lbl">Xabarlar</div></div>
        <div class="stat-box"><div class="stat-icon">📁</div><div class="stat-val">{st.session_state.files_cnt}</div><div class="stat-lbl">Fayllar</div></div>
        <div class="stat-box"><div class="stat-icon">⏱</div><div class="stat-val">{mins}</div><div class="stat-lbl">Daqiqa</div></div>
        <div class="stat-box"><div class="stat-icon">🤖</div><div class="stat-val">{len(avail)}</div><div class="stat-lbl">AI aktiv</div></div>
        <div class="stat-box"><div class="stat-icon">🔥</div><div class="stat-val">{max(1,len(st.session_state.messages)//5)}</div><div class="stat-lbl">Daraja</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-label">Funksiyalar</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Nima qilmoqchisiz?</p>', unsafe_allow_html=True)
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
    st.markdown('<p class="section-label">API Holati</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title" style="font-size:20px;">Ulangan AI Platformalar</p>', unsafe_allow_html=True)

    api_cols = st.columns(4)
    api_data = [
        ("groq",    "Excel + Chat",   "Llama 3.3 70B"),
        ("gemini",  "HTML + Tahlil",  "Gemini 2.0 Flash"),
        ("cohere",  "Python Kod",     "Command R+"),
        ("mistral", "Word + CSV",     "Mistral Large"),
    ]
    for col, (prov, use, model) in zip(api_cols, api_data):
        cfg = API_CONFIGS[prov]
        connected = prov in ai_clients
        status_color = "#34d399" if connected else "#f87171"
        status_text = "Ulangan" if connected else "Ulanmagan"
        with col:
            st.markdown(f"""
            <div style="background:rgba({('100,108,255' if prov=='groq' else '52,211,153' if prov=='gemini' else '56,189,248' if prov=='cohere' else '244,114,182')},0.05);
                        border:1px solid rgba({('100,108,255' if prov=='groq' else '52,211,153' if prov=='gemini' else '56,189,248' if prov=='cohere' else '244,114,182')},0.2);
                        border-radius:14px;padding:18px;text-align:center;margin-bottom:8px;">
                <div style="font-size:28px;margin-bottom:10px;">{cfg['icon']}</div>
                <div style="font-size:14px;font-weight:800;color:#f0f0ff;font-family:'Syne',sans-serif;margin-bottom:4px;">{cfg['name']}</div>
                <div style="font-size:10px;color:#50506a;font-family:'JetBrains Mono',monospace;margin-bottom:8px;">{model}</div>
                <div style="font-size:10px;font-weight:700;color:{status_color};font-family:'JetBrains Mono',monospace;">● {status_text}</div>
                <div style="font-size:10px;color:#50506a;margin-top:4px;">{use}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">Tezkor Harakatlar</p>', unsafe_allow_html=True)
    q1,q2,q3,q4 = st.columns(4)
    for col,icon,label,page in [(q1,"📊","Oylik Byudjet","excel"),(q2,"📄","Rezyume Yozish","word"),(q3,"🤖","Telegram Bot","code"),(q4,"🌐","Landing Page","html")]:
        with col:
            if st.button(f"{icon}  {label}", use_container_width=True, key=f"quick_{page}"):
                st.session_state.page = page
                st.rerun()

# ══════════════════════════════════════════════════════════════════
# PAGE: CHAT AI — with streaming typewriter effect
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "chat":
    cur_prov = st.session_state.chat_provider
    cfg = API_CONFIGS.get(cur_prov, API_CONFIGS["groq"])

    st.markdown(f"""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#646cff;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
                ✦ Smart Chat · {api_status_html(cur_prov)}
            </p>
            <h1>💬 Chat <span class="g-text">AI</span></h1>
            <p class="subtitle">
                So'zingizni yozing — AI tushunadi va javob yozayotgandek ko'rsatadi. Excel, Word, Kod — hammasi avtomatik.
            </p>
            <div class="hero-badges">
                <span class="hero-badge">🔴 Live Streaming</span>
                <span class="hero-badge">🧠 Smart Intent</span>
                <span class="hero-badge">📊 Auto Excel</span>
                <span class="hero-badge">📝 Auto Word</span>
                <span class="hero-badge">💻 Auto Kod</span>
            </div>
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
            <div class="somo-card card-v5" style="padding:18px 14px;"><span class="card-icon" style="font-size:26px;">📋</span><div class="card-title" style="font-size:12px;">"100 mahsulot CSV"</div><div class="card-desc">Dataset yaratiladi</div></div>
            <div class="somo-card card-v6" style="padding:18px 14px;"><span class="card-icon" style="font-size:26px;">❓</span><div class="card-title" style="font-size:12px;">"AI nima?"</div><div class="card-desc">Matn javob beriladi</div></div>
        </div>
        """, unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            # Show provider badge for assistant
            if msg["role"] == "assistant" and "provider" in msg:
                prov_used = msg.get("provider","groq")
                cfg_used = API_CONFIGS.get(prov_used, API_CONFIGS["groq"])
                st.markdown(f'<div style="margin-bottom:8px;">{api_status_html(prov_used)}</div>',
                            unsafe_allow_html=True)
            st.markdown(msg["content"])
            if "file_data" in msg:
                fd = msg["file_data"]
                download_block(fd["bytes"], fd["name"], fd["label"])

    # File upload
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
    if prompt := st.chat_input("💭  Yozing... Excel, Word, Kod, HTML so'rang — fayl avtomatik yaratiladi!", key="chat_in"):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        db_log(st.session_state.username,"User",prompt,"input",cur_prov)

        intent = detect_intent(prompt)

        with st.chat_message("assistant"):
            LANG_RULE = (
                "CRITICAL: Always detect user's language and reply in EXACTLY that same language. "
                "Uzbek → Uzbek. English → English. Russian → Russian. Never switch unless user does."
            )
            styles_map = {
                "Aqlli yordamchi": f"You are Somo AI — an intelligent, professional AI. Clear, structured answers. {LANG_RULE}",
                "Do'stona": f"You are Somo AI — friendly, warm, talk like a close friend. {LANG_RULE}",
                "Rasmiy ekspert": f"You are Somo AI — formal, precise, detailed expert answers. {LANG_RULE}",
                "Ijodkor": f"You are Somo AI — creative, unconventional thinker. {LANG_RULE}",
                "Texnik": f"You are Somo AI — deep technical expert. Code, architecture details. {LANG_RULE}",
            }
            sys_base = styles_map.get(st.session_state.ai_style, styles_map["Aqlli yordamchi"])

            if intent in ("excel","word","html","csv","code"):
                GENERATORS = {
                    "excel": (gen_excel, "📊 Excel fayl", "xlsx", st.session_state.excel_provider),
                    "word":  (gen_word,  "📝 Word hujjat","docx", st.session_state.word_provider),
                    "code":  (gen_code,  "💻 Python kodi","py",   st.session_state.code_provider),
                    "html":  (gen_html,  "🌐 HTML sahifa","html", st.session_state.html_provider),
                    "csv":   (gen_csv,   "📋 CSV dataset","csv",  st.session_state.csv_provider),
                }
                gfunc, glabel, gext, gen_prov = GENERATORS[intent]
                cfg_gen = API_CONFIGS.get(gen_prov, API_CONFIGS["groq"])

                em = {"excel":"📊","word":"📝","code":"💻","html":"🌐","csv":"📋"}[intent]
                st.markdown(f'<div class="somo-notify">{em} {glabel} yaratilmoqda... {api_status_html(gen_prov)} ishlamoqda</div>',
                            unsafe_allow_html=True)
                prog = st.progress(0, text="")
                for i in range(0,70,14):
                    time.sleep(0.25)
                    prog.progress(i)
                try:
                    fb, fn = gfunc(prompt, provider=gen_prov)
                    prog.progress(100)
                    time.sleep(0.15)
                    prog.empty()
                    if fb and isinstance(fb, bytes):
                        resp_txt = f"✅ **{glabel}** tayyor!\n\n📁 `{fn}` · {api_status_html(gen_prov)}"
                        file_info = {"bytes":fb,"name":fn,"label":glabel}
                        st.markdown(f'<div style="margin-bottom:8px;">{api_status_html(gen_prov)}</div>',
                                    unsafe_allow_html=True)
                        st.markdown(f"✅ **{glabel}** muvaffaqiyatli yaratildi! — `{fn}`")
                        download_block(fb, fn, glabel)
                        st.session_state.files_cnt += 1
                        st.session_state.last_files.append(fn)
                        db_log("Somo AI","Assistant",resp_txt,intent,gen_prov)
                        msg_d = {"role":"assistant","content":resp_txt,"file_data":file_info,"provider":gen_prov}
                    else:
                        prog.empty()
                        resp_txt = f"❌ Xatolik: {fn}"
                        st.error(resp_txt)
                        msg_d = {"role":"assistant","content":resp_txt,"provider":gen_prov}
                except Exception as e:
                    prog.empty()
                    resp_txt = f"❌ {e}"
                    st.error(resp_txt)
                    msg_d = {"role":"assistant","content":resp_txt,"provider":cur_prov}
                st.session_state.messages.append(msg_d)

            else:
                # ── TYPEWRITER STREAMING ──────────────────────────────
                msgs_for_ai = [{"role":"system","content":sys_base}]
                if st.session_state.uploaded_text:
                    msgs_for_ai.append({"role":"system","content":
                        f"Yuklangan hujjat:\n{st.session_state.uploaded_text[:4000]}"})
                for m in st.session_state.messages[-22:]:
                    msgs_for_ai.append({"role":m["role"],"content":m["content"]})

                # Show API badge
                st.markdown(f'<div style="margin-bottom:10px;">{api_status_html(cur_prov)}</div>',
                            unsafe_allow_html=True)

                response_placeholder = st.empty()
                full_response = ""
                used_prov = cur_prov

                # Stream with typewriter effect
                try:
                    for chunk, prov_name in call_ai_stream(msgs_for_ai, st.session_state.temp,
                                                           provider=cur_prov):
                        full_response += chunk
                        used_prov = prov_name
                        # Show streaming text with cursor
                        response_placeholder.markdown(
                            full_response + '<span class="typewriter-cursor"></span>',
                            unsafe_allow_html=True
                        )
                        time.sleep(0.008)  # tiny delay for smooth effect

                    # Final render without cursor
                    response_placeholder.markdown(full_response)

                except Exception as e:
                    # Fallback to non-streaming
                    with st.spinner("🤔 O'ylayapman..."):
                        full_response, used_prov = call_ai(msgs_for_ai, st.session_state.temp,
                                                           provider=cur_prov)
                        response_placeholder.markdown(full_response)

                db_log("Somo AI","Assistant",full_response,"chat",used_prov)
                st.session_state.messages.append({
                    "role":"assistant","content":full_response,"provider":used_prov
                })

        st.session_state.total_msgs += 1
        st.rerun()

# ══════════════════════════════════════════════════════════════════
# PAGE: EXCEL GENERATOR
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "excel":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]

    st.markdown(f"""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#34d399;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
                ✦ File Generator · {api_status_html(st.session_state.excel_provider)}
            </p>
            <h1>📊 Excel <span class="g-text">Generator</span></h1>
            <p class="subtitle">Har qanday jadval, hisobot va ma'lumotlarni AI bilan professional Excel faylga aylantiring.</p>
            <div class="hero-badges">
                <span class="hero-badge">✅ Formulalar</span>
                <span class="hero-badge">✅ Ranglar</span>
                <span class="hero-badge">✅ Bir necha varaq</span>
                <span class="hero-badge">✅ Freeze panes</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    xl_examples = [
        ("💰","Moliyaviy Byudjet","12 oylik moliyaviy byudjet jadvali: daromad manbalari, xarajatlar (ish haqi, ijara, reklama), foyda, formulalar"),
        ("📦","Inventar Ro'yxati","100 ta mahsulot inventar: ID, nomi, kategoriya, miqdori, narxi, jami qiymat, minimum zaxira"),
        ("👥","Xodimlar Jadvali","Kompaniya xodimlari ish haqi: ism, lavozim, bo'lim, maosh, bonus, soliq, sof maosh"),
        ("📈","Savdo Hisoboti","Oylik savdo: har mahsulot reja, haqiqat, farq, % bajarilish, reyting"),
        ("🎓","Talabalar Bahosi","30 ta talaba 6 fandan baho: o'rtacha, reyting, davomat foizi"),
        ("📅","Loyiha Jadvali","IT loyiha Gantt: vazifalar, mas'ul, sana, holat, % bajarilish"),
    ]
    c1,c2,c3 = st.columns(3)
    for i,(ico,title,fp) in enumerate(xl_examples):
        with [c1,c2,c3][i%3]:
            if st.button(f"{ico}  {title}", key=f"xlq_{i}", use_container_width=True):
                st.session_state["xl_prompt"] = fp

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    col_inp, col_opt = st.columns([3,1])
    with col_inp:
        xl_prompt = st.text_area("📝  Jadval tavsifi:",
            value=st.session_state.get("xl_prompt",""),
            placeholder="Masalan: 6 xodimlik IT kompaniya uchun oy bo'yicha ish haqi jadvali, bonuslar va soliq chegirmalari bilan...",
            height=140, key="xl_in")
    with col_opt:
        if avail_provs:
            curr_xl_idx = avail_provs.index(st.session_state.excel_provider) if st.session_state.excel_provider in avail_provs else 0
            xl_prov_sel = st.selectbox("🤖 AI", prov_labels, index=curr_xl_idx, key="xl_prov")
            st.session_state.excel_provider = avail_provs[prov_labels.index(xl_prov_sel)]
        xl_temp = st.slider("Aniqlik", 0.0, 0.6, 0.15, 0.05, key="xl_temp")
        add_summary = st.checkbox("📊 Xulosa varag'i", value=True)
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        gen_xl = st.button("🚀  Excel Yaratish", use_container_width=True, type="primary", key="gen_xl")

    if gen_xl:
        if not xl_prompt.strip():
            st.warning("⚠️  Jadval tavsifini kiriting!")
        else:
            fp = xl_prompt + ("\n\nOxirida umumiy xulosa (Summary) varag'i ham qo'sh." if add_summary else "")
            xl_prov = st.session_state.excel_provider
            st.markdown(f'<div class="somo-notify">📊 Excel yaratilmoqda... {api_status_html(xl_prov)}</div>',
                        unsafe_allow_html=True)
            prog = st.progress(0)
            for pct in range(0,75,12):
                time.sleep(0.28)
                prog.progress(pct)
            fb, fn = gen_excel(fp, xl_temp, provider=xl_prov)
            prog.progress(100); time.sleep(0.15); prog.empty()
            if fb and isinstance(fb, bytes):
                st.session_state.files_cnt += 1
                download_block(fb, fn, "Excel")
            else:
                st.error(f"❌  {fn}")

# ══════════════════════════════════════════════════════════════════
# PAGE: WORD GENERATOR
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "word":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]

    st.markdown(f"""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#38bdf8;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
                ✦ File Generator · {api_status_html(st.session_state.word_provider)}
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
        ("👤","Rezyume / CV","Python backend dasturchi uchun professional rezyume: 4 yil tajriba, texnik ko'nikmalar, ta'lim, sertifikatlar"),
        ("🤝","Hamkorlik Xati","IT kompaniyalar o'rtasida hamkorlik taklifnomasi: kompaniya taqdimoti, taklif mazmuni, foyda va shartlar"),
        ("📋","Ijara Shartnomasi","Turar joy ijara shartnomasi: tomonlar, ob'ekt, muddat, to'lov, mas'uliyat, fors-major"),
        ("📖","Biznes Reja","Startap uchun to'liq biznes reja: bozor tahlili, mahsulot, marketing, moliyaviy prognoz"),
        ("🎓","Kurs Ishi","Sun'iy intellekt mavzusida kurs ishi: 3 bob, xulosa, adabiyotlar, 15+ sahifa"),
        ("📑","Buyruq / Qaror","Kompaniya direktori buyrug'i: xodim ishga qabul, lavozim, ish haqi, imzo"),
    ]
    c1,c2,c3 = st.columns(3)
    for i,(ico,title,fp) in enumerate(wd_examples):
        with [c1,c2,c3][i%3]:
            if st.button(f"{ico}  {title}", key=f"wdq_{i}", use_container_width=True):
                st.session_state["wd_prompt"] = fp

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    col_wd, col_wopt = st.columns([3,1])
    with col_wd:
        wd_prompt = st.text_area("📝  Hujjat tavsifi:",
            value=st.session_state.get("wd_prompt",""),
            placeholder="Masalan: O'zbekistonda ro'yxatdan o'tgan IT kompaniya uchun dasturchi yollash bo'yicha mehnat shartnomasi...",
            height=140, key="wd_in")
    with col_wopt:
        if avail_provs:
            curr_wd_idx = avail_provs.index(st.session_state.word_provider) if st.session_state.word_provider in avail_provs else 0
            wd_prov_sel = st.selectbox("🤖 AI", prov_labels, index=curr_wd_idx, key="wd_prov")
            st.session_state.word_provider = avail_provs[prov_labels.index(wd_prov_sel)]
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        gen_wd = st.button("🚀  Word Yaratish", use_container_width=True, type="primary", key="gen_wd")

    if gen_wd:
        if not wd_prompt.strip():
            st.warning("⚠️  Hujjat tavsifini kiriting!")
        else:
            wd_prov = st.session_state.word_provider
            st.markdown(f'<div class="somo-notify">📝 Word hujjat yaratilmoqda... {api_status_html(wd_prov)}</div>',
                        unsafe_allow_html=True)
            prog = st.progress(0)
            for pct in range(0,75,15):
                time.sleep(0.28)
                prog.progress(pct)
            fb, fn = gen_word(wd_prompt, provider=wd_prov)
            prog.progress(100); time.sleep(0.15); prog.empty()
            if fb and isinstance(fb, bytes):
                st.session_state.files_cnt += 1
                download_block(fb, fn, "Word")
            else:
                st.error(f"❌  {fn}")

# ══════════════════════════════════════════════════════════════════
# PAGE: CODE GENERATOR
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "code":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]

    st.markdown(f"""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#fbbf24;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
                ✦ Code Generator · {api_status_html(st.session_state.code_provider)}
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
        ("🤖","Telegram Bot","Aiogram v3 bilan Telegram bot: /start, /help, inline keyboard, FSM holatlar, SQLite bazasi"),
        ("🌐","FastAPI CRUD","FastAPI da to'liq CRUD API: PostgreSQL, SQLAlchemy, Pydantic, JWT auth, Swagger"),
        ("📊","Dashboard","Streamlit dashboard: CSV yuklash, pandas tahlili, plotly grafiklar, filter, qidiruv"),
        ("🔍","Web Scraper","BeautifulSoup4 web scraper: sahifa tahlili, CSV saqlash, rotating proxy, delay"),
        ("🤖","ML Model","Scikit-learn classification: data tayyorlash, train, hyperparameter tuning, hisobot"),
        ("📧","Email Sender","smtplib email: HTML template, attachment, bulk send, queue, retry"),
    ]
    c1,c2,c3 = st.columns(3)
    for i,(ico,title,fp) in enumerate(code_examples):
        with [c1,c2,c3][i%3]:
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
        if avail_provs:
            curr_cd_idx = avail_provs.index(st.session_state.code_provider) if st.session_state.code_provider in avail_provs else 0
            cd_prov_sel = st.selectbox("🤖 AI", prov_labels, index=curr_cd_idx, key="cd_prov")
            st.session_state.code_provider = avail_provs[prov_labels.index(cd_prov_sel)]
        cd_temp = st.slider("Ijodkorlik", 0.0, 0.5, 0.1, 0.05, key="cd_temp")
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
        gen_cd = st.button("🚀  Kod Yaratish", use_container_width=True, type="primary", key="gen_cd")

    if gen_cd:
        if not cd_prompt.strip():
            st.warning("⚠️  Kod tavsifini kiriting!")
        else:
            cd_prov = st.session_state.code_provider
            st.markdown(f'<div class="somo-notify">💻 Python kodi yozilmoqda... {api_status_html(cd_prov)}</div>',
                        unsafe_allow_html=True)
            prog = st.progress(0)
            for pct in range(0,65,15):
                time.sleep(0.22)
                prog.progress(pct)
            fb, fn = gen_code(cd_prompt, cd_temp, provider=cd_prov)
            prog.progress(100); prog.empty()
            code_txt = fb.decode('utf-8')
            st.session_state.files_cnt += 1
            st.markdown('<div class="somo-success">✅  Kod tayyor — preview va yuklab olish quyida</div>',
                        unsafe_allow_html=True)
            with st.expander("👁  Kod Preview", expanded=True):
                st.code(code_txt, language="python")
            st.download_button("⬇️  .py Fayl Yuklab Olish", fb, fn,
                               "text/x-python", use_container_width=True, type="primary",
                               key=f"dl_py_{time.time()}")

# ══════════════════════════════════════════════════════════════════
# PAGE: HTML GENERATOR
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "html":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]

    st.markdown(f"""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#f472b6;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
                ✦ HTML Generator · {api_status_html(st.session_state.html_provider)}
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
        ("🎨","Portfolio","Web developer portfolio: hero typewriter, skills, projects glassmorphism, dark theme"),
        ("🛒","Mahsulot Sahifasi","E-commerce mahsulot: gallery, narx, cart, reviews — minimal zamonaviy dizayn"),
        ("📊","Analytics Dashboard","Data dashboard: sidebar nav, stat cards, charts — dark glassmorphism"),
        ("🎪","Event Landing","Konferensiya landing page: hero countdown, speakers, schedule, tickets, parallax"),
        ("🔐","Login Sahifa","Zamonaviy login: glassmorphism card, validation, particles background"),
        ("📰","Blog Post","Blog maqola: hero image, typography, TOC, code blocks, dark/light toggle"),
    ]
    c1,c2,c3 = st.columns(3)
    for i,(ico,title,fp) in enumerate(html_examples):
        with [c1,c2,c3][i%3]:
            if st.button(f"{ico}  {title}", key=f"hq_{i}", use_container_width=True):
                st.session_state["ht_prompt"] = fp

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    col_ht, col_hopt = st.columns([3,1])
    with col_ht:
        ht_prompt = st.text_area("📝  Sahifa tavsifi:",
            value=st.session_state.get("ht_prompt",""),
            placeholder="Masalan: AI kompaniyasi uchun zamonaviy landing page — hero, features, pricing, CTA — dark neon dizayn...",
            height=140, key="ht_in")
    with col_hopt:
        if avail_provs:
            curr_ht_idx = avail_provs.index(st.session_state.html_provider) if st.session_state.html_provider in avail_provs else 0
            ht_prov_sel = st.selectbox("🤖 AI", prov_labels, index=curr_ht_idx, key="ht_prov")
            st.session_state.html_provider = avail_provs[prov_labels.index(ht_prov_sel)]
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        gen_ht = st.button("🚀  HTML Yaratish", use_container_width=True, type="primary", key="gen_ht")

    if gen_ht:
        if not ht_prompt.strip():
            st.warning("⚠️  Sahifa tavsifini kiriting!")
        else:
            ht_prov = st.session_state.html_provider
            st.markdown(f'<div class="somo-notify">🌐 HTML sahifa yaratilmoqda... {api_status_html(ht_prov)}</div>',
                        unsafe_allow_html=True)
            prog = st.progress(0)
            for pct in range(0,70,14):
                time.sleep(0.28)
                prog.progress(pct)
            fb, fn = gen_html(ht_prompt, 0.5, provider=ht_prov)
            prog.progress(100); prog.empty()
            html_txt = fb.decode('utf-8')
            st.session_state.files_cnt += 1
            st.markdown('<div class="somo-success">✅ HTML tayyor! Faylni yuklab, brauzerda oching.</div>',
                        unsafe_allow_html=True)
            with st.expander("👁  HTML Kod Preview"):
                st.code(html_txt[:3000]+("..." if len(html_txt)>3000 else ""), language="html")
            st.download_button("⬇️  HTML Fayl Yuklab Olish", fb, fn,
                               "text/html", use_container_width=True, type="primary",
                               key=f"dl_html_{time.time()}")
            st.info("💡  Faylni yuklab oling va ikki marta bosib brauzerda oching")

# ══════════════════════════════════════════════════════════════════
# PAGE: CSV GENERATOR
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "csv":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]

    st.markdown(f"""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#a78bfa;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
                ✦ Data Generator · {api_status_html(st.session_state.csv_provider)}
            </p>
            <h1>📋 CSV <span class="g-text">Generator</span></h1>
            <p class="subtitle">Katta ma'lumotlar to'plamini — test data, namuna dataset — bir so'rovda yarating.</p>
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
        ("📦","Mahsulotlar","100 ta mahsulot: ID, nomi, kategoriya, narxi, miqdori, brend, reyting"),
        ("👥","Foydalanuvchilar","50 ta user: ID, ism, familiya, email, telefon, shahar, sana, holat"),
        ("🌍","Mamlakatlar","Dunyo mamlakatlari: nomi, poytaxti, aholisi, maydoni, YIM, valyuta"),
        ("📱","Ilovalar","Top 100 mobil ilova: nomi, kategoriya, reyting, yuklamalar, narxi"),
        ("🎬","Filmlar","Top 100 film: nomi, rejissori, yili, janri, reyting, byudjet, daromad"),
        ("💼","Kompaniyalar","50 ta kompaniya: nomi, sektori, xodimlar, daromad, asos yili, mamlakat"),
    ]
    c1,c2,c3 = st.columns(3)
    for i,(ico,title,fp) in enumerate(csv_examples):
        with [c1,c2,c3][i%3]:
            if st.button(f"{ico}  {title}", key=f"cvq_{i}", use_container_width=True):
                st.session_state["cv_prompt"] = fp

    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    col_cv, col_copt = st.columns([3,1])
    with col_cv:
        cv_prompt = st.text_area("📝  Dataset tavsifi:",
            value=st.session_state.get("cv_prompt",""),
            placeholder="Masalan: 80 ta O'zbekiston shahri: viloyati, aholisi, maydoni, asosiy sanoat...",
            height=130, key="cv_in")
    with col_copt:
        if avail_provs:
            curr_cv_idx = avail_provs.index(st.session_state.csv_provider) if st.session_state.csv_provider in avail_provs else 0
            cv_prov_sel = st.selectbox("🤖 AI", prov_labels, index=curr_cv_idx, key="cv_prov")
            st.session_state.csv_provider = avail_provs[prov_labels.index(cv_prov_sel)]
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        gen_cv = st.button("🚀  CSV Yaratish", use_container_width=True, type="primary", key="gen_cv")

    if gen_cv:
        if not cv_prompt.strip():
            st.warning("⚠️  Dataset tavsifini kiriting!")
        else:
            cv_prov = st.session_state.csv_provider
            st.markdown(f'<div class="somo-notify">📋 Dataset yaratilmoqda... {api_status_html(cv_prov)}</div>',
                        unsafe_allow_html=True)
            prog = st.progress(0)
            for pct in range(0,65,15):
                time.sleep(0.22)
                prog.progress(pct)
            fb, fn = gen_csv(cv_prompt, provider=cv_prov)
            prog.progress(100); prog.empty()
            st.session_state.files_cnt += 1
            try:
                df = pd.read_csv(io.BytesIO(fb))
                st.markdown(f'<div class="somo-success">✅  CSV tayyor — {len(df)} satr, {len(df.columns)} ustun</div>',
                            unsafe_allow_html=True)
                st.dataframe(df.head(10), use_container_width=True)
                if len(df) > 10:
                    st.caption(f"↑ Birinchi 10 ta satr (jami {len(df)} ta)")
            except:
                st.markdown('<div class="somo-success">✅  CSV tayyor!</div>', unsafe_allow_html=True)
            st.download_button("⬇️  CSV Yuklab Olish", fb, fn, "text/csv",
                               use_container_width=True, type="primary",
                               key=f"dl_csv_{time.time()}")

# ══════════════════════════════════════════════════════════════════
# PAGE: TEMPLATES
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "templates":
    st.markdown("""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#646cff;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
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
             "prompt":"12 oylik moliyaviy byudjet Excel jadvali: har oy daromad (ish haqi, freelance, passiv), xarajatlar 8 kategoriya, sof foyda, yig'ilgan jamg'arma, formulalar bilan"},
            {"ico":"📈","title":"KPI Dashboard","tag":"excel","tag_cls":"tag-excel",
             "desc":"Kompaniya KPI ko'rsatkichlari, maqsad vs haqiqat",
             "prompt":"Kompaniya KPI Excel dashboard: 15 ko'rsatkich, har oy maqsad va haqiqat, farq foizi, RAG ranglash"},
            {"ico":"📋","title":"Biznes Reja","tag":"word","tag_cls":"tag-word",
             "desc":"To'liq startap biznes reja hujjati",
             "prompt":"IT startap uchun to'liq biznes reja Word hujjati: ijroiya xulosa, bozor tahlili, mahsulot, marketing, moliyaviy prognoz 3 yil, risklar"},
            {"ico":"🤝","title":"Hamkorlik Xati","tag":"word","tag_cls":"tag-word",
             "desc":"Professional hamkorlik taklifnomasi",
             "prompt":"Professional hamkorlik taklifnomasi xati Word: kompaniya taqdimoti, taklif mazmuni, o'zaro foyda, shartlar, imzo joyi"},
        ],
        "💻 Dasturlash": [
            {"ico":"🤖","title":"Telegram Bot","tag":"code","tag_cls":"tag-code",
             "desc":"Aiogram v3, FSM, inline keyboard",
             "prompt":"Aiogram v3 bilan to'liq Telegram bot: /start, /help, InlineKeyboard, FSM, SQLite baza, admin panel, .env konfiguratsiya"},
            {"ico":"🌐","title":"FastAPI REST","tag":"code","tag_cls":"tag-code",
             "desc":"CRUD, JWT, PostgreSQL, Swagger",
             "prompt":"FastAPI REST API: User, Post, Comment modellari, SQLAlchemy+PostgreSQL, Pydantic, JWT, CRUD, CORS, Swagger"},
            {"ico":"🎨","title":"Portfolio Sayt","tag":"html","tag_cls":"tag-html",
             "desc":"Dark theme, glassmorphism, animatsiya",
             "prompt":"Web developer portfolio HTML/CSS/JS: typewriter hero, skills bars, projects glassmorphism cards, particle background, dark theme, mobile responsive"},
            {"ico":"📊","title":"Streamlit App","tag":"code","tag_cls":"tag-code",
             "desc":"Data dashboard, grafik, filter",
             "prompt":"Streamlit data analytics app: CSV/Excel yuklash, pandas, Plotly Express grafiklar, dinamik filterlar, PDF eksport, dark theme"},
        ],
        "📚 Ta'lim": [
            {"ico":"📖","title":"Dars Rejasi","tag":"word","tag_cls":"tag-word",
             "desc":"45 daqiqalik to'liq dars konspekti",
             "prompt":"Informatika Python asoslari 45 daqiqalik dars rejasi Word: fan, mavzu, maqsadlar, bosqichlar, savol-javob, baholash mezonlari"},
            {"ico":"📝","title":"Test Savollari","tag":"excel","tag_cls":"tag-excel",
             "desc":"25 ta test, 4 variant, javoblar",
             "prompt":"Python asoslari 25 test Excel: №, savol, A-B-C-D variant, to'g'ri javob, mavzu, qiyinchilik, baho"},
            {"ico":"🎓","title":"Baholash Jadvali","tag":"excel","tag_cls":"tag-excel",
             "desc":"30 talaba, 6 fan, o'rtacha, reyting",
             "prompt":"Universitet guruh baholash Excel: 30 talaba, 6 fan, 3 baho, og'irlikli o'rtacha, GPA, reyting, grant/kontrakt, davomat, formulalar"},
            {"ico":"📚","title":"Kurs Ishi","tag":"word","tag_cls":"tag-word",
             "desc":"15+ sahifa, 3 bob, adabiyotlar",
             "prompt":"Kompyuter fanlari kurs ishi Word: mavzu — Sun'iy intellekt. Titul, mundarija, kirish, 3 bob, xulosa, 15 ta adabiyot, ilovalar"},
        ],
        "👤 Shaxsiy": [
            {"ico":"📄","title":"Rezyume","tag":"word","tag_cls":"tag-word",
             "desc":"Professional CV, zamonaviy format",
             "prompt":"Python/Django backend dasturchi rezyume Word: ism, kontakt, xulosa, ko'nikmalar, 2 ish joyi, ta'lim, sertifikatlar, loyihalar, tillar"},
            {"ico":"📅","title":"Haftalik Reja","tag":"excel","tag_cls":"tag-excel",
             "desc":"7 kun, vazifalar, ustuvorlik, holat",
             "prompt":"Haftalik vazifalar Excel: 7 kun, 8 vaqt sloti, vazifa, kategoriya, ustuvorlik, taxminiy/haqiqiy vaqt, holat, haftalik statistika"},
            {"ico":"💰","title":"Shaxsiy Byudjet","tag":"excel","tag_cls":"tag-excel",
             "desc":"Daromad, xarajat, jamg'arma maqsad",
             "prompt":"Shaxsiy moliya Excel: oylik daromad, majburiy/ixtiyoriy xarajatlar, jamg'arma, xarajatlar foizi, oylik trend, tavsiyalar"},
            {"ico":"💪","title":"Sport Rejasi","tag":"excel","tag_cls":"tag-excel",
             "desc":"3 oylik trening, progres, ozish",
             "prompt":"3 oylik sport rejasi Excel: haftalik trening, mashqlar, to'plamlar, takroriylik, og'irlik, ozish maqsad, kaloriya, suv, uyqu, progres foizi"},
        ]
    }

    sel = st.selectbox("📁  Kategoriya:", list(TEMPLATES.keys()), key="tmpl_sel")
    st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)

    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    items = TEMPLATES[sel]
    c1, c2 = st.columns(2)
    for i, tmpl in enumerate(items):
        with [c1,c2][i%2]:
            tag_to_prov = {"excel":st.session_state.excel_provider,"word":st.session_state.word_provider,
                           "code":st.session_state.code_provider,"html":st.session_state.html_provider,"csv":st.session_state.csv_provider}
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
            bc1, bc2 = st.columns(2)
            with bc1:
                if st.button(f"🚀  Yaratish", key=f"tgen_{sel}_{i}", use_container_width=True, type="primary"):
                    with st.spinner("⏳  Tayyorlanmoqda..."):
                        tag = tmpl["tag"]
                        if tag == "excel":
                            fb, fn = gen_excel(tmpl["prompt"], provider=st.session_state.excel_provider)
                            if fb and isinstance(fb, bytes):
                                st.session_state.files_cnt += 1
                                st.download_button("⬇️  Excel", fb, fn, MIME["xlsx"], key=f"tdl_{sel}_{i}", type="primary")
                        elif tag == "word":
                            fb, fn = gen_word(tmpl["prompt"], provider=st.session_state.word_provider)
                            if fb and isinstance(fb, bytes):
                                st.session_state.files_cnt += 1
                                st.download_button("⬇️  Word", fb, fn, MIME["docx"], key=f"tdl_{sel}_{i}", type="primary")
                        elif tag == "code":
                            fb, fn = gen_code(tmpl["prompt"], provider=st.session_state.code_provider)
                            st.session_state.files_cnt += 1
                            st.download_button("⬇️  .py", fb, fn, MIME["py"], key=f"tdl_{sel}_{i}", type="primary")
                        elif tag == "html":
                            fb, fn = gen_html(tmpl["prompt"], provider=st.session_state.html_provider)
                            st.session_state.files_cnt += 1
                            st.download_button("⬇️  HTML", fb, fn, MIME["html"], key=f"tdl_{sel}_{i}", type="primary")
            with bc2:
                if st.button(f"💬  Chat AI", key=f"tchat_{sel}_{i}", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":tmpl["prompt"]})
                    st.session_state.page = "chat"
                    st.rerun()

# ══════════════════════════════════════════════════════════════════
# PAGE: ANALYZE
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "analyze":
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]
    prov_labels = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]

    st.markdown(f"""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#22d3ee;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
                ✦ Document Analysis · {api_status_html(st.session_state.analyze_provider)}
            </p>
            <h1>🔍 Hujjat <span class="g-text">Tahlili</span></h1>
            <p class="subtitle">PDF yoki Word faylni yuklang — AI xulosa chiqaradi, g'oyalarni ajratadi, savollarga javob beradi.</p>
            <div class="hero-badges">
                <span class="hero-badge">📄 PDF</span>
                <span class="hero-badge">📝 DOCX</span>
                <span class="hero-badge">🧠 AI Tahlil</span>
                <span class="hero-badge">❓ Q&A</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_up, col_act = st.columns([1,1])
    with col_up:
        st.markdown('<p class="section-label">Fayl Yuklash</p>', unsafe_allow_html=True)
        if avail_provs:
            curr_az_idx = avail_provs.index(st.session_state.analyze_provider) if st.session_state.analyze_provider in avail_provs else 0
            az_prov_sel = st.selectbox("🤖 AI Provider", prov_labels, index=curr_az_idx, key="az_prov")
            st.session_state.analyze_provider = avail_provs[prov_labels.index(az_prov_sel)]

        upl = st.file_uploader("PDF yoki DOCX", type=["pdf","docx"], key="az_up",
                               label_visibility="collapsed")
        if upl:
            with st.spinner("📄 O'qilmoqda..."):
                txt = process_doc(upl)
                st.session_state.uploaded_text = txt
            if txt:
                st.markdown(f'<div class="somo-success">✅  {upl.name} — {len(txt):,} belgi, ~{len(txt.split()):,} so\'z</div>',
                            unsafe_allow_html=True)
                with st.expander("👁  Matnni ko'rish"):
                    st.text(txt[:2000]+("..." if len(txt)>2000 else ""))
            else:
                st.error("❌ Fayl o'qilmadi")

    with col_act:
        st.markdown('<p class="section-label">Tahlil Amaliyotlari</p>', unsafe_allow_html=True)
        if st.session_state.uploaded_text:
            az_prov = st.session_state.analyze_provider
            actions = {
                "📝  Qisqa Xulosa":   "Hujjatni 5-7 asosiy band bilan qisqa xulosasini yoz. Har bandni ★ bilan boshlat.",
                "🔑  Kalit G'oyalar": "Hujjatdagi 8-10 muhim g'oya, fakt va xulosalarni ro'yxat shaklida ajrat. Har birini izohlat.",
                "❓  Savol-Javob":    "Hujjat bo'yicha 10 muhim savol tuz va har biriga to'liq javob ber.",
                "🌐  Inglizcha":      "Hujjat mazmunini professional ingliz tiliga tarjima qil.",
                "📊  Statistika":     "Hujjatdagi barcha raqamlar, foizlar, sanalar va statistikani jadval ko'rinishida tizimlashtir.",
                "✅  Action Items":   "Hujjatdan aniq amaliy vazifalar va keyingi qadamlarni ustuvorlik bo'yicha tartibla.",
            }
            for act_lbl, act_prompt in actions.items():
                if st.button(act_lbl, key=f"az_{act_lbl}", use_container_width=True):
                    az_msgs = [
                        {"role":"system","content":"Sen professional hujjat tahlilchisan. To'liq va foydali javoblar ber."},
                        {"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:4500]}\n\nVazifa: {act_prompt}"}
                    ]
                    result_placeholder = st.empty()
                    full_az = ""
                    st.markdown(f'<div style="margin-bottom:6px;">{api_status_html(az_prov)}</div>',
                                unsafe_allow_html=True)
                    for chunk, _ in call_ai_stream(az_msgs, temperature=0.4, provider=az_prov):
                        full_az += chunk
                        result_placeholder.markdown(
                            f"**{act_lbl}**\n\n" + full_az + '<span class="typewriter-cursor"></span>',
                            unsafe_allow_html=True
                        )
                        time.sleep(0.008)
                    result_placeholder.markdown(f"**{act_lbl}**\n\n{full_az}")
        else:
            st.markdown("""
            <div style="background:rgba(100,108,255,0.04);border:1px solid rgba(100,108,255,0.12);
                        border-radius:14px;padding:28px;text-align:center;margin-top:8px;">
                <p style="font-size:36px;margin-bottom:12px;">📂</p>
                <p style="color:#50506a;font-size:14px;">Chap tomonda fayl yuklang</p>
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.uploaded_text:
        st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">O\'z Savolingiz</p>', unsafe_allow_html=True)
        cq, cb = st.columns([4,1])
        with cq:
            custom_q = st.text_input("", placeholder="🔍 Hujjat haqida savolingizni yozing...",
                                     label_visibility="collapsed", key="az_q")
        with cb:
            if st.button("🔍  Qidirish", use_container_width=True, type="primary", key="az_ask"):
                if custom_q:
                    az_prov = st.session_state.analyze_provider
                    az_msgs = [
                        {"role":"system","content":"Hujjat asosida aniq javob ber. Hujjatda yo'q narsa haqida ixtiro qilma."},
                        {"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:4500]}\n\nSavol: {custom_q}"}
                    ]
                    ans_placeholder = st.empty()
                    full_ans = ""
                    for chunk, _ in call_ai_stream(az_msgs, temperature=0.3, provider=az_prov):
                        full_ans += chunk
                        ans_placeholder.markdown(
                            "**💬 Javob:**\n\n" + full_ans + '<span class="typewriter-cursor"></span>',
                            unsafe_allow_html=True
                        )
                        time.sleep(0.008)
                    ans_placeholder.markdown(f"**💬 Javob:**\n\n{full_ans}")

# ══════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "history":
    st.markdown("""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#646cff;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ History</p>
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

        col_s, col_e1, col_e2 = st.columns([3,1,1])
        with col_s:
            search = st.text_input("", placeholder="🔍  Xabarlarda qidirish...",
                                   label_visibility="collapsed", key="hist_s")
        with col_e1:
            st.download_button("📥  JSON", json.dumps(msgs,ensure_ascii=False,indent=2).encode(),
                               f"somo_chat_{datetime.now():%Y%m%d}.json", use_container_width=True)
        with col_e2:
            txt_exp = "\n\n".join([f"[{m['role'].upper()}] [{m.get('provider','?')}]\n{m['content']}" for m in msgs])
            st.download_button("📄  TXT", txt_exp.encode(),
                               f"somo_chat_{datetime.now():%Y%m%d}.txt", use_container_width=True)

        show = msgs
        if search:
            show = [m for m in msgs if search.lower() in m.get("content","").lower()]
            st.markdown(f'<div class="somo-notify">🔍  "{search}" — {len(show)} ta natija</div>',
                        unsafe_allow_html=True)

        st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
        for msg in reversed(show[-50:]):
            is_user = msg["role"] == "user"
            css_cls = "hist-user" if is_user else "hist-ai"
            prov_used = msg.get("provider","groq")
            role_lbl = "👤  Siz" if is_user else f"🤖  Somo AI · {API_CONFIGS.get(prov_used,API_CONFIGS['groq'])['icon']} {API_CONFIGS.get(prov_used,API_CONFIGS['groq'])['name']}"
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
            <div style="font-size:56px;margin-bottom:20px;">💬</div>
            <p style="color:#50506a;font-size:18px;font-weight:700;font-family:'Syne',sans-serif;">Chat tarixi yo'q</p>
            <p style="color:#334155;font-size:13px;margin-top:8px;">Chat AI sahifasiga o'ting va suhbatni boshlang</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💬  Chat AI ga o'tish", type="primary"):
            st.session_state.page = "chat"
            st.rerun()

# ══════════════════════════════════════════════════════════════════
# PAGE: FEEDBACK
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "feedback":
    st.markdown("""
    <div class="somo-hero">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <p style="font-size:11px;letter-spacing:3.5px;font-weight:700;color:#f472b6;margin-bottom:10px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">✦ Feedback</p>
            <h1>💌 Fikr <span class="g-text">Bildirish</span></h1>
            <p class="subtitle">Sizning fikringiz Somo AI ni yaxshiroq qilishga yordam beradi.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_f, col_s = st.columns([3,2])
    with col_f:
        st.markdown('<p class="section-label">Fikringizni yuboring</p>', unsafe_allow_html=True)
        with st.form("fb_form", clear_on_submit=True):
            rating = st.select_slider("⭐  Baho:", options=[1,2,3,4,5], value=5,
                format_func=lambda x: "⭐"*x + f"  ({x}/5)")
            category = st.selectbox("📂  Kategoriya:", [
                "Umumiy fikr","Xato haqida xabar","Yangi funksiya taklifi",
                "Dizayn taklifi","Tezlik muammosi","API haqida","Boshqa"])
            message = st.text_area("✍️  Xabar:", height=140,
                placeholder="Fikrlaringizni batafsil yozing (kamida 10 ta belgi)...")
            email = st.text_input("📧  Email (ixtiyoriy):", placeholder="javob olish uchun")
            sub_fb = st.form_submit_button("📤  Yuborish", use_container_width=True, type="primary")
            if sub_fb:
                if not message or len(message) < 10:
                    st.error("❌  Kamida 10 ta belgidan iborat xabar yozing!")
                elif fb_db:
                    try:
                        fb_db.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            st.session_state.username, rating, category,
                            message, email or "N/A", "Yangi", st.session_state.files_cnt])
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
                    avg_rating = sum(int(f.get("Rating",5)) for f in all_fb)/len(all_fb)
                    st.markdown(f"""
                    <div class="stat-row" style="grid-template-columns:1fr 1fr;">
                        <div class="stat-box"><div class="stat-icon">📨</div><div class="stat-val">{len(all_fb)}</div><div class="stat-lbl">Jami</div></div>
                        <div class="stat-box"><div class="stat-icon">⭐</div><div class="stat-val">{avg_rating:.1f}</div><div class="stat-lbl">O'rtacha</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown('<p class="section-label" style="margin-top:14px;">Oxirgi fikrlar</p>', unsafe_allow_html=True)
                    for fb in reversed(all_fb[-5:]):
                        stars = "⭐"*int(fb.get("Rating",5))
                        st.markdown(f"""
                        <div style="background:rgba(100,108,255,0.05);border:1px solid rgba(100,108,255,0.1);
                                    border-radius:12px;padding:12px;margin:6px 0;">
                            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                                <span style="font-size:12px;font-weight:700;color:#818cf8;font-family:'JetBrains Mono',monospace;">{str(fb.get('Username',''))}</span>
                                <span style="font-size:12px;">{stars}</span>
                            </div>
                            <p style="color:#50506a;font-size:12px;line-height:1.5;">{str(fb.get('Message',''))[:80]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
            except:
                st.info("Statistika yuklanmadi")

# ══════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ══════════════════════════════════════════════════════════════════
elif st.session_state.page == "profile":
    uname = st.session_state.username
    mins = (datetime.now()-st.session_state.login_time).seconds//60 if 'login_time' in st.session_state else 0
    avail_provs = [p for p in ["groq","gemini","cohere","mistral"] if p in ai_clients]

    st.markdown(f"""
    <div class="somo-hero" style="text-align:center;">
        <div class="grid-dots"></div>
        <div class="somo-hero-content">
            <div style="width:88px;height:88px;background:linear-gradient(135deg,#4f46e5,#7c3aed,#f472b6);
                        border-radius:24px;margin:0 auto 20px;display:flex;align-items:center;justify-content:center;
                        font-size:40px;font-weight:900;color:white;
                        box-shadow:0 0 40px rgba(100,108,255,0.5);font-family:'Syne',sans-serif;">
                {uname[0].upper()}
            </div>
            <h1 style="font-size:32px;">{uname}</h1>
            <p style="color:rgba(255,255,255,0.55);font-size:14px;margin-top:8px;font-family:'JetBrains Mono',monospace;">
                🟢 ONLINE · Somo AI Ultra Pro Max · {len(avail_provs)} API aktiv
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    p_stats = [
        ("💬", len(st.session_state.messages), "Xabarlar"),
        ("📁", st.session_state.files_cnt, "Fayllar"),
        ("⏱", mins, "Daqiqa"),
        ("🤖", len(avail_provs), "API"),
    ]
    cols_ps = st.columns(4)
    for col,(icon,val,lbl) in zip(cols_ps,p_stats):
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
            if st.form_submit_button("🔄  Yangilash", type="primary", use_container_width=True):
                if len(new_pw)<6:     st.error("❌ Yangi parol kamida 6 belgi!")
                elif new_pw!=conf_pw: st.error("❌ Parollar mos emas!")
                elif user_db:
                    try:
                        recs = user_db.get_all_records()
                        idx = next((i for i,r in enumerate(recs)
                            if str(r['username'])==uname and str(r['password'])==hash_pw(old_pw)), None)
                        if idx is not None:
                            user_db.update_cell(idx+2,2,hash_pw(new_pw))
                            st.success("✅ Parol muvaffaqiyatli yangilandi!")
                        else:
                            st.error("❌ Joriy parol noto'g'ri!")
                    except Exception as e:
                        st.error(f"❌ {e}")

    with col_info:
        st.markdown('<p class="section-label">API Sozlamalari</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-title" style="font-size:18px;">🤖 Har Format uchun AI</p>', unsafe_allow_html=True)

        prov_labels_all = [f"{API_CONFIGS[p]['icon']} {API_CONFIGS[p]['name']}" for p in avail_provs]
        format_provs = [
            ("chat_provider",    "💬 Chat"),
            ("excel_provider",   "📊 Excel"),
            ("word_provider",    "📝 Word"),
            ("code_provider",    "💻 Kod"),
            ("html_provider",    "🌐 HTML"),
            ("csv_provider",     "📋 CSV"),
            ("analyze_provider", "🔍 Tahlil"),
        ]
        for sess_key, label in format_provs:
            curr_val = st.session_state.get(sess_key, "groq")
            curr_idx = avail_provs.index(curr_val) if curr_val in avail_provs else 0
            sel = st.selectbox(label, prov_labels_all, index=curr_idx, key=f"prof_{sess_key}")
            st.session_state[sess_key] = avail_provs[prov_labels_all.index(sel)]

        if st.button("💾  Saqlash", type="primary", key="save_style", use_container_width=True):
            st.success("✅ Sozlamalar saqlandi!")

        st.markdown('<hr class="somo-divider">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">Sessiya ma\'lumotlari</p>', unsafe_allow_html=True)
        login_str = st.session_state.login_time.strftime('%d.%m.%Y %H:%M') if 'login_time' in st.session_state else "—"
        st.markdown(f"""
        <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:14px;padding:18px;">
            <div style="margin-bottom:12px;"><p style="color:var(--text-3);font-size:10px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;font-family:'JetBrains Mono',monospace;">Kirish vaqti</p><p style="color:var(--text-1);font-size:14px;font-weight:600;margin-top:3px;">{login_str}</p></div>
            <div style="margin-bottom:12px;"><p style="color:var(--text-3);font-size:10px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;font-family:'JetBrains Mono',monospace;">Sessiya</p><p style="color:var(--text-1);font-size:14px;font-weight:600;margin-top:3px;">{mins} daqiqa</p></div>
            <div><p style="color:var(--text-3);font-size:10px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;font-family:'JetBrains Mono',monospace;">Chat xabarlari</p><p style="color:#818cf8;font-size:14px;font-weight:600;margin-top:3px;">{len(st.session_state.messages)} ta</p></div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# FOOTER
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
    <div class="f-sub" style="margin-top:10px;">
        👨‍💻 <strong style="color:#e2e8f0;">Usmonov Sodiq</strong>
        &nbsp;·&nbsp;
        👨‍💻 <strong style="color:#e2e8f0;">Mavlonov Saloxiddin</strong>
    </div>
    <div class="f-copy">© 2026 Somo AI Ultra Pro Max v3.0 — Barcha huquqlar himoyalangan · Python · Streamlit</div>
</div>
""", unsafe_allow_html=True)

