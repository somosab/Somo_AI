import streamlit as st
import pandas as pd
import gspread
import hashlib
import json
import time
import io
import re
import os
import base64
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ── Optional imports ──────────────────────────────────
try:
    import mammoth
    HAS_MAMMOTH = True
except:
    HAS_MAMMOTH = False

try:
    from pypdf import PdfReader
    HAS_PDF = True
except:
    HAS_PDF = False

try:
    from openpyxl import Workbook
    from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side)
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except:
    HAS_OPENPYXL = False

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except:
    HAS_DOCX = False

try:
    from streamlit_cookies_manager import EncryptedCookieManager
    HAS_COOKIES = True
except:
    HAS_COOKIES = False

# ─────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Somo AI | Ultra Pro Max",
    page_icon="♾️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────
# COOKIES
# ─────────────────────────────────────────────────────
if HAS_COOKIES:
    cookies = EncryptedCookieManager(
        password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Ultra_2026_XYZ")
    )
    if not cookies.ready():
        st.stop()
else:
    cookies = {}

# ─────────────────────────────────────────────────────
# GLOBAL CSS — ULTRA PRO DESIGN
# ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --primary: #6C5CE7;
  --primary-light: #a29bfe;
  --accent: #fd79a8;
  --accent2: #00cec9;
  --dark: #0d0d1a;
  --card-bg: rgba(255,255,255,0.06);
  --glass: rgba(255,255,255,0.08);
  --border: rgba(255,255,255,0.12);
  --text: #f0f0ff;
  --text-muted: rgba(240,240,255,0.55);
  --success: #00b894;
  --warning: #fdcb6e;
  --error: #d63031;
}

* { font-family: 'DM Sans', sans-serif; box-sizing: border-box; }

/* ── App BG ── */
.stApp {
  background: #0d0d1a !important;
  background-image:
    radial-gradient(ellipse 80% 60% at 20% 10%, rgba(108,92,231,0.18) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 80%, rgba(253,121,168,0.12) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 50% 50%, rgba(0,206,201,0.06) 0%, transparent 70%) !important;
  min-height: 100vh;
}

/* ── Hide Streamlit defaults ── */
[data-testid="stSidebarNav"],
#MainMenu, footer, header { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: rgba(13,13,26,0.97) !important;
  border-right: 1px solid var(--border) !important;
  backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

div[data-testid="stSidebar"] button {
  background: var(--glass) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  font-weight: 500 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
  transition: all 0.25s cubic-bezier(.4,0,.2,1) !important;
  width: 100% !important;
  padding: 11px 16px !important;
  margin: 3px 0 !important;
  text-align: left !important;
}
div[data-testid="stSidebar"] button:hover {
  background: linear-gradient(135deg, var(--primary), #a29bfe) !important;
  border-color: transparent !important;
  transform: translateX(6px) !important;
  box-shadow: 0 4px 20px rgba(108,92,231,0.4) !important;
}

/* ── Main content ── */
.main .block-container {
  padding: 0 !important;
  max-width: 100% !important;
}

/* ── Hero Home ── */
.home-hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  overflow: hidden;
  text-align: center;
}

.home-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 70% 60% at 50% 30%, rgba(108,92,231,0.22) 0%, transparent 70%),
    radial-gradient(ellipse 40% 40% at 20% 80%, rgba(253,121,168,0.15) 0%, transparent 60%);
  pointer-events: none;
  z-index: 0;
}

/* Floating particles */
.particle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, var(--primary-light), transparent);
  animation: particleFloat linear infinite;
  opacity: 0;
  pointer-events: none;
  z-index: 0;
}

@keyframes particleFloat {
  0%   { transform: translateY(100vh) scale(0); opacity: 0; }
  10%  { opacity: 0.6; }
  90%  { opacity: 0.4; }
  100% { transform: translateY(-10vh) scale(1.5); opacity: 0; }
}

/* ── Logo ── */
.logo-wrap {
  position: relative;
  z-index: 2;
  margin-bottom: 30px;
}
.logo-icon {
  font-size: 80px;
  display: block;
  animation: logoPulse 3s ease-in-out infinite;
  filter: drop-shadow(0 0 30px rgba(108,92,231,0.8));
}
@keyframes logoPulse {
  0%,100% { transform: scale(1) rotate(0deg); filter: drop-shadow(0 0 30px rgba(108,92,231,0.8)); }
  50%      { transform: scale(1.08) rotate(5deg); filter: drop-shadow(0 0 50px rgba(253,121,168,0.9)); }
}

.brand-name {
  font-family: 'Syne', sans-serif;
  font-size: 72px;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, var(--primary-light) 40%, var(--accent) 80%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin: 0;
  letter-spacing: -2px;
}
.brand-tagline {
  font-size: 18px;
  color: var(--text-muted);
  margin: 12px 0 40px;
  font-weight: 300;
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* ── Feature grid home ── */
.home-feat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  max-width: 900px;
  margin: 0 auto 50px;
  position: relative;
  z-index: 2;
}
.home-feat-item {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 24px 16px;
  transition: all 0.35s cubic-bezier(.4,0,.2,1);
  cursor: pointer;
  backdrop-filter: blur(10px);
}
.home-feat-item:hover {
  background: rgba(108,92,231,0.2);
  border-color: var(--primary);
  transform: translateY(-8px) scale(1.04);
  box-shadow: 0 20px 50px rgba(108,92,231,0.3);
}
.home-feat-icon { font-size: 36px; display: block; margin-bottom: 10px; }
.home-feat-title { font-size: 13px; font-weight: 600; color: var(--text); }

/* ── CTA button ── */
.cta-btn {
  display: inline-block;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white !important;
  font-family: 'Syne', sans-serif;
  font-size: 18px;
  font-weight: 700;
  padding: 18px 50px;
  border-radius: 50px;
  text-decoration: none;
  transition: all 0.3s;
  position: relative;
  z-index: 2;
  cursor: pointer;
  border: none;
  box-shadow: 0 10px 40px rgba(108,92,231,0.5);
  letter-spacing: 1px;
}
.cta-btn:hover {
  transform: translateY(-4px) scale(1.04);
  box-shadow: 0 20px 60px rgba(108,92,231,0.7);
}

/* ── API pills ── */
.api-pills { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; position: relative; z-index: 2; margin-bottom: 30px; }
.api-pill-on {
  background: rgba(0,184,148,0.15);
  border: 1px solid rgba(0,184,148,0.4);
  color: #00b894;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}
.api-pill-off {
  background: rgba(214,48,49,0.12);
  border: 1px solid rgba(214,48,49,0.3);
  color: #d63031;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

/* ── Glass cards ── */
.glass-card {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 28px;
  backdrop-filter: blur(15px);
  transition: all 0.3s;
}
.glass-card:hover {
  border-color: rgba(108,92,231,0.4);
  box-shadow: 0 10px 40px rgba(108,92,231,0.15);
}

/* ── Page header ── */
.page-header {
  background: var(--glass);
  border-bottom: 1px solid var(--border);
  padding: 20px 32px;
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 0;
  backdrop-filter: blur(20px);
  position: sticky;
  top: 0;
  z-index: 100;
}
.page-title {
  font-family: 'Syne', sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: var(--text);
  margin: 0;
}
.page-subtitle { font-size: 13px; color: var(--text-muted); margin: 0; }

/* ── Chat ── */
.chat-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px 24px 120px;
}

.stChatMessage {
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: 18px !important;
  padding: 16px 20px !important;
  margin: 10px 0 !important;
  backdrop-filter: blur(10px) !important;
  color: var(--text) !important;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
}
.stChatMessage p { color: var(--text) !important; }
.stChatMessage * { color: var(--text) !important; }

.stChatMessage[data-testid="user-message"] {
  background: rgba(108,92,231,0.15) !important;
  border-color: rgba(108,92,231,0.35) !important;
}

/* ── Typing animation ── */
.typing-dots {
  display: inline-flex;
  gap: 5px;
  align-items: center;
  padding: 16px 20px;
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 18px;
  margin: 8px 0;
}
.typing-dot {
  width: 8px; height: 8px;
  background: var(--primary-light);
  border-radius: 50%;
  animation: typingBounce 1.4s ease-in-out infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; background: var(--accent); }
.typing-dot:nth-child(3) { animation-delay: 0.4s; background: var(--accent2); }
@keyframes typingBounce {
  0%,80%,100% { transform: scale(0.6) translateY(0); opacity: 0.5; }
  40% { transform: scale(1) translateY(-8px); opacity: 1; }
}

/* ── Chat input ── */
.stChatInputContainer {
  background: rgba(13,13,26,0.9) !important;
  border-top: 1px solid var(--border) !important;
  padding: 16px 24px !important;
  backdrop-filter: blur(20px) !important;
  position: fixed !important;
  bottom: 0 !important;
  left: 0 !important;
  right: 0 !important;
  z-index: 999 !important;
}
[data-testid="stChatInput"] {
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  color: var(--text) !important;
}
[data-testid="stChatInput"]:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(108,92,231,0.2) !important;
}

/* ── Metric cards ── */
.metric-row { display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0; }
.metric-card {
  flex: 1;
  min-width: 120px;
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px;
  text-align: center;
}
.metric-num {
  font-family: 'Syne', sans-serif;
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--primary-light), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.metric-lbl { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

/* ── Section title ── */
.section-title {
  font-family: 'Syne', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 6px;
}
.section-sub { font-size: 14px; color: var(--text-muted); margin-bottom: 24px; }

/* ── Generator cards ── */
.gen-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
.gen-card {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 22px;
  cursor: pointer;
  transition: all 0.3s;
}
.gen-card:hover {
  border-color: var(--primary);
  transform: translateY(-4px);
  box-shadow: 0 15px 40px rgba(108,92,231,0.25);
}
.gen-card-icon { font-size: 32px; margin-bottom: 10px; display: block; }
.gen-card-title { font-weight: 700; font-size: 15px; color: var(--text); margin-bottom: 6px; }
.gen-card-desc { font-size: 12px; color: var(--text-muted); line-height: 1.5; }

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--primary), #a29bfe) !important;
  color: white !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  font-family: 'DM Sans', sans-serif !important;
  transition: all 0.3s !important;
  padding: 10px 20px !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(108,92,231,0.45) !important;
  background: linear-gradient(135deg, #7d6fe8, var(--accent)) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stMultiSelect > div > div {
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(108,92,231,0.2) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 4px !important;
  gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: 10px !important;
  color: var(--text-muted) !important;
  font-weight: 500 !important;
  padding: 10px 18px !important;
  border: none !important;
  transition: all 0.25s !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--primary), #a29bfe) !important;
  color: white !important;
}

/* ── Labels ── */
label, .stSelectbox label, .stTextInput label, .stTextArea label, .stSlider label { color: var(--text-muted) !important; }
p, li, span { color: var(--text) !important; }
h1,h2,h3,h4,h5 {
  font-family: 'Syne', sans-serif !important;
  color: var(--text) !important;
}

/* ── Success/error ── */
.stSuccess, .stInfo, .stWarning, .stError { border-radius: 12px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 3px; }

/* ── Notification toast ── */
.toast {
  background: linear-gradient(135deg, rgba(108,92,231,0.9), rgba(253,121,168,0.9));
  color: white;
  padding: 14px 22px;
  border-radius: 14px;
  font-weight: 600;
  font-size: 14px;
  margin: 10px 0;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.15);
  animation: slideDown 0.4s cubic-bezier(.4,0,.2,1);
}
@keyframes slideDown { from{opacity:0;transform:translateY(-12px)} to{opacity:1;transform:translateY(0)} }

/* ── Image preview ── */
.img-preview {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border);
  box-shadow: 0 10px 40px rgba(0,0,0,0.4);
}

/* ── Profile avatar ── */
.profile-avatar {
  width: 90px; height: 90px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  display: flex; align-items: center; justify-content: center;
  font-family: 'Syne', sans-serif;
  font-size: 38px; font-weight: 800;
  color: white;
  margin: 0 auto 12px;
  border: 3px solid rgba(255,255,255,0.15);
  box-shadow: 0 0 30px rgba(108,92,231,0.5);
}

/* ── Sidebar user card ── */
.sb-user {
  text-align: center;
  padding: 20px 16px;
  margin-bottom: 16px;
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 18px;
}
.sb-avatar {
  width: 60px; height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  font-family: 'Syne', sans-serif;
  font-size: 26px; font-weight: 800;
  color: white; line-height: 60px;
  margin: 0 auto 10px;
}
.sb-name { font-size: 15px; font-weight: 700; color: var(--text) !important; }
.sb-badge {
  display: inline-block;
  background: rgba(0,184,148,0.15);
  border: 1px solid rgba(0,184,148,0.3);
  color: #00b894 !important;
  padding: 3px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-top: 4px;
}

/* ── Login page ── */
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: stretch;
  background: #0d0d1a;
}
.login-left {
  flex: 1;
  padding: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.login-left::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 70% at 40% 40%, rgba(108,92,231,0.2) 0%, transparent 70%);
}
.login-right {
  flex: 1;
  padding: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: var(--glass);
  border-left: 1px solid var(--border);
  backdrop-filter: blur(20px);
}
.login-brand {
  font-family: 'Syne', sans-serif;
  font-size: 58px; font-weight: 800;
  background: linear-gradient(135deg, #fff, var(--primary-light), var(--accent));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  margin: 0; line-height: 1.1;
  position: relative; z-index: 1;
}
.login-sub { font-size: 16px; color: var(--text-muted); margin: 12px 0 40px; position: relative; z-index: 1; }

/* ── Floating robot illustration ── */
.robot-float {
  position: absolute;
  right: -30px; top: 50%;
  transform: translateY(-50%);
  font-size: 200px;
  opacity: 0.08;
  pointer-events: none;
  animation: robotBob 4s ease-in-out infinite;
}
@keyframes robotBob {
  0%,100% { transform: translateY(-50%) rotate(-5deg); }
  50%      { transform: translateY(calc(-50% - 20px)) rotate(5deg); }
}

/* ── Streaming text ── */
@keyframes cursorBlink {
  0%,100% { opacity: 1; }
  50% { opacity: 0; }
}
.stream-cursor::after {
  content: '▋';
  animation: cursorBlink 0.8s infinite;
  color: var(--primary-light);
  font-size: 0.9em;
}

/* ── Image gen card ── */
.img-gen-result {
  border-radius: 20px;
  overflow: hidden;
  border: 2px solid var(--border);
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  transition: all 0.3s;
}
.img-gen-result:hover {
  border-color: var(--primary);
  box-shadow: 0 20px 60px rgba(108,92,231,0.4);
  transform: scale(1.01);
}

/* ── Markdown in chat ── */
.stMarkdown code {
  background: rgba(108,92,231,0.2) !important;
  color: var(--primary-light) !important;
  border-radius: 6px !important;
  padding: 2px 6px !important;
}
.stMarkdown pre {
  background: rgba(0,0,0,0.4) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}

/* ── Download button ── */
.stDownloadButton > button {
  background: linear-gradient(135deg, var(--success), #00cec9) !important;
  color: white !important; font-weight: 700 !important;
  border-radius: 12px !important; border: none !important;
}

/* ── Mobile ── */
@media(max-width:768px) {
  .brand-name { font-size: 44px; }
  .home-feat-grid { grid-template-columns: repeat(3,1fr); }
  .login-left { padding: 40px 24px; }
  .login-right { padding: 40px 24px; }
}

/* ── Expander ── */
.streamlit-expanderHeader {
  background: var(--glass) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
}

/* ── Slider ── */
.stSlider > div > div { color: var(--text) !important; }
.stSlider [data-baseweb="slider"] div { background: var(--primary) !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background: var(--glass) !important;
  border: 2px dashed var(--border) !important;
  border-radius: 16px !important;
  color: var(--text-muted) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--primary) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# GOOGLE SHEETS DB
# ─────────────────────────────────────────────────────
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
        chat_sheet = ss.worksheet("ChatHistory")
        try:
            fb_sheet = ss.worksheet("Letters")
        except:
            fb_sheet = ss.add_worksheet("Letters", 1000, 10)
            fb_sheet.append_row(["Timestamp","Username","Rating","Category","Message","Email","Status"])
        return user_sheet, chat_sheet, fb_sheet
    except Exception as e:
        return None, None, None

user_db, chat_db, fb_db = get_connections()

# ─────────────────────────────────────────────────────
# MULTI-API CLIENTS
# ─────────────────────────────────────────────────────
def _get_secret(*keys):
    for key in keys:
        for try_key in [key, key.lower()]:
            try:
                v = st.secrets[try_key]
                if v: return str(v).strip()
            except: pass
        for section in ["api_keys", "keys", "secrets", "env"]:
            for try_key in [key, key.lower()]:
                try:
                    v = st.secrets[section][try_key]
                    if v: return str(v).strip()
                except: pass
        v = os.environ.get(key) or os.environ.get(key.lower())
        if v: return v.strip()
    return None

def init_clients():
    clients = {}
    errors  = {}

    # 1. GROQ
    try:
        k = _get_secret("GROQ_API_KEY")
        if k:
            from groq import Groq as _G
            clients["groq"] = _G(api_key=k)
        else:
            errors["groq"] = "GROQ_API_KEY yo'q"
    except Exception as e:
        errors["groq"] = str(e)[:80]

    # 2. CEREBRAS
    try:
        k = _get_secret("CEREBRAS_API_KEY")
        if k:
            from cerebras.cloud.sdk import Cerebras as _C
            clients["cerebras"] = _C(api_key=k)
        else:
            errors["cerebras"] = "CEREBRAS_API_KEY yo'q"
    except Exception as e:
        errors["cerebras"] = str(e)[:80]

    # 3. GEMINI
    try:
        k = _get_secret("GEMINI_API_KEY")
        if k:
            import google.generativeai as genai
            genai.configure(api_key=k)
            clients["gemini"] = genai.GenerativeModel("gemini-2.0-flash")
            clients["gemini_key"] = k
            clients["gemini_vision"] = genai.GenerativeModel("gemini-2.0-flash")
        else:
            errors["gemini"] = "GEMINI_API_KEY yo'q"
    except Exception as e:
        errors["gemini"] = str(e)[:80]

    # 4. MISTRAL
    try:
        k = _get_secret("MISTRAL_API_KEY")
        if k:
            try:
                from mistralai import Mistral as _M
                clients["mistral"] = _M(api_key=k)
            except ImportError:
                from mistralai.client import MistralClient as _MC
                clients["mistral"] = _MC(api_key=k)
        else:
            errors["mistral"] = "MISTRAL_API_KEY yo'q"
    except Exception as e:
        errors["mistral"] = str(e)[:80]

    # 5. COHERE
    try:
        k = _get_secret("COHERE_API_KEY")
        if k:
            import cohere as _co
            clients["cohere"] = _co.Client(k)
        else:
            errors["cohere"] = "COHERE_API_KEY yo'q"
    except Exception as e:
        errors["cohere"] = str(e)[:80]

    # 6. OPENROUTER
    try:
        k = _get_secret("OPENROUTER_API_KEY")
        if k:
            try:
                from openai import OpenAI as _OAI
                clients["openrouter"] = _OAI(base_url="https://openrouter.ai/api/v1", api_key=k)
            except ImportError:
                clients["openrouter"] = {"type":"requests","key":k}
            clients["openrouter_key"] = k
        else:
            errors["openrouter"] = "OPENROUTER_API_KEY yo'q"
    except Exception as e:
        errors["openrouter"] = str(e)[:80]

    # 7. STABILITY AI (rasm generatsiyasi)
    try:
        k = _get_secret("STABILITY_API_KEY", "STABILITY_KEY")
        if k:
            clients["stability"] = k
        else:
            errors["stability"] = "STABILITY_API_KEY yo'q (ixtiyoriy)"
    except Exception as e:
        errors["stability"] = str(e)[:80]

    # 8. TOGETHER AI (rasm generatsiyasi bepul)
    try:
        k = _get_secret("TOGETHER_API_KEY")
        if k:
            clients["together"] = k
        else:
            errors["together"] = "TOGETHER_API_KEY yo'q (ixtiyoriy)"
    except Exception as e:
        errors["together"] = str(e)[:80]

    return clients, errors

if 'ai_clients' not in st.session_state:
    _c, _e = init_clients()
    st.session_state.ai_clients = _c
    st.session_state.api_errors = _e

ai_clients = st.session_state.ai_clients
api_errors  = st.session_state.api_errors

# ─────────────────────────────────────────────────────
# AI CALL FUNCTIONS
# ─────────────────────────────────────────────────────
PROVIDER_MAP = {
    "chat":    ["cerebras","groq","mistral","cohere","gemini","openrouter"],
    "code":    ["cerebras","groq","mistral","openrouter","gemini","cohere"],
    "csv":     ["cerebras","groq","mistral","cohere","gemini","openrouter"],
    "excel":   ["gemini","mistral","groq","cerebras","cohere","openrouter"],
    "word":    ["gemini","mistral","groq","cerebras","cohere","openrouter"],
    "analyze": ["gemini","mistral","cohere","groq","cerebras","openrouter"],
    "html":    ["openrouter","cerebras","groq","mistral","gemini","cohere"],
    "vision":  ["gemini","openrouter","groq"],
}

def best_provider(task="chat"):
    for p in PROVIDER_MAP.get(task, ["groq","gemini"]):
        if p in ai_clients:
            return p
    for p in ["cerebras","groq","gemini","mistral","cohere","openrouter"]:
        if p in ai_clients: return p
    return None

def _call_cerebras(messages, temp, max_tok):
    r = ai_clients["cerebras"].chat.completions.create(
        messages=messages, model="llama-3.3-70b",
        temperature=min(temp,1.0), max_tokens=max_tok)
    return r.choices[0].message.content

def _call_groq(messages, temp, max_tok):
    r = ai_clients["groq"].chat.completions.create(
        messages=messages, model="llama-3.3-70b-versatile",
        temperature=temp, max_tokens=max_tok)
    return r.choices[0].message.content

def _call_gemini(messages, temp, max_tok):
    parts = [f"[{m['role'].upper()}]: {m['content']}" for m in messages]
    r = ai_clients["gemini"].generate_content("\n\n".join(parts))
    return r.text

def _call_mistral(messages, temp, max_tok):
    cl = ai_clients["mistral"]
    try:
        r = cl.chat.complete(model="mistral-small-latest", messages=messages,
                             temperature=temp, max_tokens=max_tok)
    except AttributeError:
        from mistralai.models.chat_completion import ChatMessage
        mm = [ChatMessage(role=m["role"] if m["role"]!="system" else "user", content=m["content"]) for m in messages]
        r = cl.chat(model="mistral-small-latest", messages=mm, temperature=temp, max_tokens=max_tok)
    return r.choices[0].message.content

def _call_cohere(messages, temp, max_tok):
    sys_msg = next((m["content"] for m in messages if m["role"]=="system"), "")
    user_msg = next((m["content"] for m in reversed(messages) if m["role"]=="user"), "")
    r = ai_clients["cohere"].chat(model="command-r-plus", message=user_msg,
                                   preamble=sys_msg, temperature=temp, max_tokens=max_tok)
    return r.text

def _call_openrouter(messages, temp, max_tok):
    cl = ai_clients.get("openrouter")
    if isinstance(cl, dict):
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {cl['key']}", "Content-Type":"application/json",
                     "HTTP-Referer":"https://somo-ai.streamlit.app"},
            json={"model":"meta-llama/llama-3.1-8b-instruct:free","messages":messages,
                  "temperature":temp,"max_tokens":max_tok}, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    else:
        r = cl.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct:free",
            messages=messages, temperature=temp, max_tokens=max_tok,
            extra_headers={"HTTP-Referer":"https://somo-ai.streamlit.app","X-Title":"Somo AI"})
        return r.choices[0].message.content

CALLERS = {
    "cerebras": _call_cerebras,
    "groq":     _call_groq,
    "gemini":   _call_gemini,
    "mistral":  _call_mistral,
    "cohere":   _call_cohere,
    "openrouter": _call_openrouter,
}

def call_ai(messages, temperature=0.6, max_tokens=3000, provider=None):
    if provider is None:
        provider = best_provider("chat")
    if provider and provider in ai_clients and provider in CALLERS:
        try:
            return CALLERS[provider](messages, temperature, max_tokens)
        except Exception:
            pass
    for p, caller in CALLERS.items():
        if p != provider and p in ai_clients:
            try:
                return caller(messages, temperature, max_tokens)
            except Exception:
                continue
    return ("❌ Hech qanday AI ulanmagan!\n\nStreamlit Secrets'ga qo'shing:\n"
            "• GROQ_API_KEY → groq.com/console\n"
            "• GEMINI_API_KEY → aistudio.google.com\n"
            "• CEREBRAS_API_KEY → cloud.cerebras.ai")

# ─────────────────────────────────────────────────────
# IMAGE GENERATION
# ─────────────────────────────────────────────────────
def generate_image(prompt: str) -> tuple:
    """
    Rasm generatsiyasi - Pollinations.ai (bepul, API key shart emas)
    Fallback: Stability AI yoki Together AI
    """
    # 1. Pollinations.ai — BEPUL, hech qanday API key shart emas!
    try:
        encoded = requests.utils.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&enhance=true"
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content, "image/jpeg", "pollinations"
    except Exception:
        pass

    # 2. Stability AI
    if "stability" in ai_clients:
        try:
            r = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={"Authorization": f"Bearer {ai_clients['stability']}",
                         "Content-Type": "application/json"},
                json={"text_prompts": [{"text": prompt, "weight": 1}],
                      "cfg_scale": 7, "height": 1024, "width": 1024,
                      "steps": 30, "samples": 1},
                timeout=60
            )
            if r.status_code == 200:
                img_b64 = r.json()["artifacts"][0]["base64"]
                return base64.b64decode(img_b64), "image/png", "stability"
        except Exception:
            pass

    # 3. Together AI
    if "together" in ai_clients:
        try:
            r = requests.post(
                "https://api.together.xyz/v1/images/generations",
                headers={"Authorization": f"Bearer {ai_clients['together']}",
                         "Content-Type": "application/json"},
                json={"model": "black-forest-labs/FLUX.1-schnell-Free",
                      "prompt": prompt, "width": 1024, "height": 1024, "n": 1},
                timeout=60
            )
            if r.status_code == 200:
                img_url = r.json()["data"][0]["url"]
                img_r = requests.get(img_url, timeout=30)
                return img_r.content, "image/png", "together"
        except Exception:
            pass

    return None, None, None

# ─────────────────────────────────────────────────────
# IMAGE ANALYSIS (Vision)
# ─────────────────────────────────────────────────────
def analyze_image_with_ai(image_bytes: bytes, question: str, mime_type: str = "image/jpeg") -> str:
    """Rasmni AI bilan tahlil qilish"""

    # 1. Gemini Vision (eng yaxshi)
    if "gemini" in ai_clients:
        try:
            import google.generativeai as genai
            import PIL.Image
            img = PIL.Image.open(io.BytesIO(image_bytes))
            model = ai_clients.get("gemini_vision", ai_clients["gemini"])
            response = model.generate_content([
                question or "Ushbu rasmni batafsil tahlil qil. Nima ko'ryapsan? Asosiy elementlarni tushuntir.",
                img
            ])
            return response.text
        except Exception as e:
            pass

    # 2. OpenRouter Vision (claude-3 yoki gpt-4v)
    if "openrouter" in ai_clients and "openrouter_key" in ai_clients:
        try:
            img_b64 = base64.b64encode(image_bytes).decode()
            cl = ai_clients["openrouter"]
            if not isinstance(cl, dict):
                response = cl.chat.completions.create(
                    model="google/gemini-2.0-flash-thinking-exp:free",
                    messages=[{"role":"user","content":[
                        {"type":"image_url","image_url":{"url":f"data:{mime_type};base64,{img_b64}"}},
                        {"type":"text","text": question or "Rasmni tahlil qil"}
                    ]}],
                    max_tokens=1500
                )
                return response.choices[0].message.content
        except Exception as e:
            pass

    # 3. Groq Vision (llava)
    if "groq" in ai_clients:
        try:
            img_b64 = base64.b64encode(image_bytes).decode()
            response = ai_clients["groq"].chat.completions.create(
                model="llava-v1.5-7b-4096-preview",
                messages=[{"role":"user","content":[
                    {"type":"image_url","image_url":{"url":f"data:{mime_type};base64,{img_b64}"}},
                    {"type":"text","text": question or "Rasmni tahlil qil"}
                ]}],
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            pass

    return "❌ Rasm tahlili uchun Gemini yoki OpenRouter API keyi kerak."

# ─────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────
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
        st.warning(f"⚠️ Fayl: {e}")
    return ""

def save_to_db(user, role, content):
    if chat_db:
        try:
            chat_db.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 user, role, content[:500]])
        except:
            pass

# ─────────────────────────────────────────────────────
# INTENT DETECTION
# ─────────────────────────────────────────────────────
EXCEL_KW = ["excel","xlsx","jadval","table","spreadsheet","budget","byudjet","hisobot",
            "report","moliya","daromad","xarajat","oylik","salary","sotish","sales",
            "inventory","ombor","statistika","formula","hisoblash","ro'yxat","list"]
WORD_KW  = ["word","docx","hujjat","document","letter","maktub","rezyume","resume","cv",
            "shartnoma","contract","ariza","biznes reja","essay","insho","maqola","diplom"]
CODE_KW  = ["python kodi","write code","kod yoz","dastur yoz","script","function yoz","bot yaz",
            "python script","python program","kodni yoz"]
HTML_KW  = ["html","website","web page","landing page","veb sahifa","html kod","web sayt"]
CSV_KW   = ["csv","comma separated","csv fayl","dataset yarat","ma'lumotlar bazasi kichik"]
IMAGE_GEN_KW = ["rasm yarat","rasm chiz","rasm gener","draw","create image","generate image",
                "paint","surat yarat","rasmini yarat","tasvirini yarat","photo generate"]
IMAGE_ANALYZE_KW = ["rasmni tahlil","rasmni ko'r","rasmda nima","bu rasmda","rasmni tushuntir",
                    "analyze image","describe image","what is in this image","image analyze"]

def detect_intent(text):
    t = text.lower()
    if any(k in t for k in IMAGE_GEN_KW):   return "image_gen"
    if any(k in t for k in IMAGE_ANALYZE_KW): return "image_analyze"
    if any(k in t for k in EXCEL_KW):         return "excel"
    if any(k in t for k in WORD_KW):           return "word"
    if any(k in t for k in HTML_KW):           return "html"
    if any(k in t for k in CSV_KW):            return "csv"
    if any(k in t for k in CODE_KW):           return "code"
    return "chat"

# ─────────────────────────────────────────────────────
# FILE GENERATORS
# ─────────────────────────────────────────────────────
def generate_excel(prompt, temperature=0.3):
    if not HAS_OPENPYXL:
        return None, "openpyxl o'rnatilmagan"
    sys_p = """Sen Excel fayl strukturasini JSON formatida qaytaruvchi ekspertsan.
FAQAT quyidagi JSON formatida javob ber (boshqa hech narsa yozma, JSON dan oldin ham keyin ham):
{
  "title": "Fayl nomi",
  "sheets": [{
      "name": "Varaq nomi",
      "headers": ["Ustun1","Ustun2","Ustun3"],
      "header_colors": ["4472C4","4472C4","4472C4"],
      "rows": [["qiymat1","qiymat2","qiymat3"],["val","val","=SUM(B2:B10)"]],
      "column_widths": [20,15,15]
  }]
}
Kamida 12-18 satr, formulalar ishlat, faqat JSON."""

    raw = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temperature, max_tokens=4500,
                  provider=best_provider("excel"))
    raw = re.sub(r'```json|```','',raw).strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match: return None, "AI strukturani to'g'ri qaytarmadi"
    try:
        data = json.loads(match.group())
    except:
        try:
            data = json.loads(raw)
        except Exception as e:
            return None, f"JSON xatosi: {e}"

    wb = Workbook()
    wb.remove(wb.active)
    THEMES = [("4F81BD","DEEAF1"),("70AD47","E2EFDA"),("7030A0","EAD1FF"),
              ("FF6600","FFE5CC"),("0070C0","CCE5FF"),("FF0000","FFE0E0"),
              ("6C5CE7","E8E3FF"),("00B894","D4F7EF")]

    for si, sd in enumerate(data.get("sheets",[])):
        ws = wb.create_sheet(title=sd.get("name",f"Varaq{si+1}")[:30])
        headers     = sd.get("headers",[])
        hcolors     = sd.get("header_colors",[])
        col_widths  = sd.get("column_widths",[])
        rows_data   = sd.get("rows",[])
        th, tr = THEMES[si % len(THEMES)]

        # Title row
        if sd.get("name"):
            ws.merge_cells(start_row=1, start_column=1,
                           end_row=1, end_column=max(len(headers),1))
            tc = ws.cell(row=1, column=1, value=sd.get("name",""))
            tc.font = Font(bold=True, size=15, color="FFFFFF", name="Calibri")
            tc.fill = PatternFill("solid", fgColor=th)
            tc.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 30

        # Header row
        if headers:
            for ci, h in enumerate(headers, 1):
                c = ws.cell(row=2, column=ci, value=h)
                hc = hcolors[ci-1] if ci-1 < len(hcolors) else th
                c.font = Font(bold=True, size=11, color="FFFFFF", name="Calibri")
                c.fill = PatternFill("solid", fgColor=hc)
                c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                s = Side(style="thin", color="FFFFFF")
                c.border = Border(left=s, right=s, top=s, bottom=s)
            ws.row_dimensions[2].height = 24

        # Data rows
        for ri, row in enumerate(rows_data, 3):
            rc = "FFFFFF" if ri % 2 else tr
            for ci, val in enumerate(row, 1):
                c = ws.cell(row=ri, column=ci)
                if isinstance(val, str) and val.startswith("="):
                    c.value = val
                    c.font = Font(color="0B5394", name="Calibri", size=10, bold=True)
                else:
                    try:
                        if isinstance(val, str) and re.match(r'^-?\d+\.?\d*$', val.strip()):
                            c.value = float(val)
                        else:
                            c.value = val
                    except:
                        c.value = val
                    c.font = Font(name="Calibri", size=10)
                c.fill = PatternFill("solid", fgColor=rc)
                s2 = Side(style="thin", color="D0D0D0")
                c.border = Border(left=s2, right=s2, top=s2, bottom=s2)
                c.alignment = Alignment(vertical="center", wrap_text=True)
            ws.row_dimensions[ri].height = 20

        # Column widths
        for ci, w in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(ci)].width = max(w, 8)
        if not col_widths and headers:
            for ci in range(1, len(headers)+1):
                ws.column_dimensions[get_column_letter(ci)].width = 18

        ws.freeze_panes = "A3"
        ws.sheet_view.showGridLines = True

    if not wb.sheetnames:
        wb.create_sheet("Ma'lumotlar")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    fname = f"{data.get('title','somo_excel')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return buf.getvalue(), fname


def generate_word(prompt, temperature=0.4):
    if not HAS_DOCX:
        return None, "python-docx o'rnatilmagan"
    sys_p = """Sen Word hujjat strukturasini JSON formatida yaratuvchi ekspertsan.
Faqat quyidagi JSON formatida javob ber:
{
  "title": "Hujjat nomi",
  "sections": [
    {"type":"heading1","text":"Sarlavha"},
    {"type":"paragraph","text":"Matn..."},
    {"type":"bullet","items":["Element 1","Element 2"]},
    {"type":"table","headers":["Ustun1","Ustun2"],"rows":[["val1","val2"]]}
  ]
}
To'liq, mazmunli kontent. Faqat JSON."""
    raw = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temperature, max_tokens=4500,
                  provider=best_provider("word"))
    raw = re.sub(r'```json|```','',raw).strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match: return None, "Struktura xatosi"
    try:
        data = json.loads(match.group())
    except Exception as e:
        return None, f"JSON xatosi: {e}"

    doc = Document()
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(11)

    # Page margin
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(3)
        section.right_margin = Cm(2)

    # Title
    tp = doc.add_heading(data.get("title","Hujjat"), level=0)
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in tp.runs:
        run.font.size = Pt(24)
        run.font.color.rgb = RGBColor(0x6C, 0x5C, 0xE7)

    # Date line
    dp = doc.add_paragraph(f"Sana: {datetime.now().strftime('%d.%m.%Y')}")
    dp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in dp.runs:
        run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        run.font.size = Pt(10)
    doc.add_paragraph()

    for sec in data.get("sections", []):
        t = sec.get("type", "paragraph")
        if t == "heading1":
            h = doc.add_heading(sec.get("text",""), level=1)
            for run in h.runs:
                run.font.color.rgb = RGBColor(0x6C, 0x5C, 0xE7)
        elif t == "heading2":
            h = doc.add_heading(sec.get("text",""), level=2)
            for run in h.runs:
                run.font.color.rgb = RGBColor(0xA2, 0x9B, 0xFE)
        elif t == "paragraph":
            p = doc.add_paragraph(sec.get("text",""))
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.first_line_indent = Cm(1)
        elif t == "bullet":
            for item in sec.get("items", []):
                doc.add_paragraph(item, style='List Bullet')
        elif t == "numbered":
            for item in sec.get("items", []):
                doc.add_paragraph(item, style='List Number')
        elif t == "table":
            hdrs = sec.get("headers", [])
            rows = sec.get("rows", [])
            if hdrs:
                tbl = doc.add_table(rows=1+len(rows), cols=len(hdrs))
                tbl.style = 'Table Grid'
                # Header
                for ci, h in enumerate(hdrs):
                    cell = tbl.rows[0].cells[ci]
                    cell.text = h
                    p = cell.paragraphs[0]
                    p.runs[0].font.bold = True
                    p.runs[0].font.color.rgb = RGBColor(255,255,255)
                    from docx.oxml.ns import qn
                    from docx.oxml import OxmlElement
                    tcPr = cell._tc.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:val'),'clear')
                    shd.set(qn('w:color'),'auto')
                    shd.set(qn('w:fill'),'6C5CE7')
                    tcPr.append(shd)
                # Data rows
                for ri, row_d in enumerate(rows):
                    for ci, val in enumerate(row_d):
                        if ci < len(tbl.rows[ri+1].cells):
                            tbl.rows[ri+1].cells[ci].text = str(val)
        elif t == "quote":
            p = doc.add_paragraph(sec.get("text",""))
            p.paragraph_format.left_indent = Cm(2)
            for run in p.runs:
                run.font.italic = True
                run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        doc.add_paragraph()

    # Footer
    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fp.text = f"© {datetime.now().year} Somo AI | {data.get('title','Hujjat')}"
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if fp.runs:
        fp.runs[0].font.size = Pt(9)
        fp.runs[0].font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    fname = f"{data.get('title','somo_doc')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    return buf.getvalue(), fname


def generate_code(prompt, temperature=0.2):
    sys_p = """Sen professional Python dasturchi. FAQAT Python kodi ber.
Kodning boshida maqsad haqida qisqa izoh (# ...) qo'y.
Ishlaydigan, to'liq, xatosiz kod yoz. Faqat kod, tushuntirma yozma."""
    code = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                   temperature=temperature, max_tokens=4000,
                   provider=best_provider("code"))
    code = re.sub(r'```python|```py|```','',code).strip()
    fname = f"somo_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    return code.encode('utf-8'), fname


def generate_html(prompt, temperature=0.5):
    sys_p = """Sen professional web developer. To'liq, zamonaviy HTML/CSS/JS sahifa yarat.
Inline CSS va JS ishlat (bitta faylda). Dark theme, animatsiyalar, responsive dizayn.
FAQAT HTML kod, boshqa hech narsa yozma."""
    html = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                   temperature=temperature, max_tokens=5000,
                   provider=best_provider("html"))
    html = re.sub(r'```html|```','',html).strip()
    fname = f"somo_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    return html.encode('utf-8'), fname


def generate_csv(prompt, temperature=0.3):
    sys_p = """Sen ma'lumotlar ekspersisan. FAQAT CSV format ber.
Birinchi qator — sarlavha. Kamida 20-25 satr. Vergul bilan ajratilgan.
Faqat CSV, hech qanday tushuntirma yoki kod yozma."""
    csv_data = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                       temperature=temperature, max_tokens=3000,
                       provider=best_provider("csv"))
    csv_data = re.sub(r'```csv|```','',csv_data).strip()
    fname = f"somo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return csv_data.encode('utf-8'), fname

# ─────────────────────────────────────────────────────
# SESSION — Cookie restore
# ─────────────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    session_user = None
    if HAS_COOKIES:
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
        except:
            st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

def logout():
    if HAS_COOKIES:
        try:
            cookies["somo_user_session"] = ""
            cookies.save()
        except:
            pass
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state.logged_in = False
    st.rerun()

# ─────────────────────────────────────────────────────
# ★ LOGIN / REGISTER PAGE
# ─────────────────────────────────────────────────────
if not st.session_state.logged_in:

    # Build API badges
    api_badges = ""
    for nm, ic, label in [("cerebras","🧠","Cerebras"),("groq","⚡","Groq"),("gemini","✨","Gemini"),
                           ("mistral","💫","Mistral"),("cohere","🌊","Cohere"),("openrouter","🌐","OpenRouter")]:
        cls = "api-pill-on" if nm in ai_clients else "api-pill-off"
        api_badges += f"<span class='{cls}'>{ic} {label}</span>"

    # Left hero
    st.markdown(f"""
    <style>
    .stApp {{ background: #0d0d1a !important; }}
    </style>

    <div style="display:flex;min-height:100vh;background:#0d0d1a;">
      <!-- Left -->
      <div style="flex:1.2;padding:70px 60px;display:flex;flex-direction:column;justify-content:center;
                  position:relative;overflow:hidden;background:radial-gradient(ellipse 80% 70% at 30% 40%,rgba(108,92,231,0.18) 0%,transparent 70%);">
        <div style="position:relative;z-index:2;">
          <div style="font-size:90px;animation:logoPulse 3s ease-in-out infinite;display:inline-block;
                      filter:drop-shadow(0 0 30px rgba(108,92,231,0.9));">♾️</div>
          <h1 style="font-family:'Syne',sans-serif;font-size:64px;font-weight:800;margin:10px 0 8px;
                     background:linear-gradient(135deg,#fff 0%,#a29bfe 45%,#fd79a8 85%);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
                     line-height:1;letter-spacing:-2px;">Somo-AI</h1>
          <p style="color:rgba(240,240,255,0.55);font-size:17px;margin:0 0 36px;font-weight:300;
                    letter-spacing:2px;text-transform:uppercase;">Universal AI Platform</p>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:36px;max-width:420px;">
            {''.join([f"""<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
                border-radius:14px;padding:14px 16px;display:flex;align-items:center;gap:10px;">
                <span style="font-size:22px;">{ic}</span>
                <div><div style="font-weight:600;font-size:13px;color:#f0f0ff;">{nm}</div>
                <div style="font-size:11px;color:rgba(240,240,255,0.5);">{desc}</div></div></div>"""
                for ic,nm,desc in [
                    ("📊","Excel Generator","Avtomatik jadvallar"),
                    ("📝","Word Generator","Professional hujjatlar"),
                    ("💻","Kod Generator","Python & web"),
                    ("🎨","Rasm Yaratish","AI image generation"),
                    ("🔍","Rasm Tahlili","Vision AI"),
                    ("🌐","HTML Sahifa","Landing pages"),
                ]])}
          </div>

          <p style="color:rgba(240,240,255,0.4);font-size:12px;margin-bottom:12px;font-weight:600;
                    letter-spacing:1px;text-transform:uppercase;">Ulangan AI Modellar</p>
          <div style="display:flex;flex-wrap:wrap;gap:8px;">{api_badges}</div>
        </div>
        <div style="position:absolute;right:-60px;top:50%;transform:translateY(-50%);
                    font-size:220px;opacity:0.05;pointer-events:none;animation:robotBob 4s ease-in-out infinite;">🤖</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Right — form overlay
    col1, col2, col3 = st.columns([1.2, 1, 0.1])
    with col2:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                    border-radius:24px;padding:36px 32px;backdrop-filter:blur(20px);margin-top:-80px;">
        """, unsafe_allow_html=True)

        t1, t2, t3 = st.tabs(["🔒 Kirish", "✍️ Ro'yxat", "ℹ️ Haqida"])

        with t1:
            with st.form("login_form"):
                st.markdown("### 👋 Xush kelibsiz!")
                u = st.text_input("👤 Username", placeholder="username")
                p = st.text_input("🔑 Parol", type="password", placeholder="••••••••")
                col_r, col_c = st.columns(2)
                with col_r: rem = st.checkbox("Eslab qolish", value=True)
                sub = st.form_submit_button("🚀 Kirish", use_container_width=True, type="primary")
                if sub and u and p:
                    if user_db:
                        try:
                            recs = user_db.get_all_records()
                            hp = hash_pw(p)
                            user = next((r for r in recs if str(r['username'])==u and str(r['password'])==hp), None)
                            if user:
                                if str(user.get('status','')).lower() == 'blocked':
                                    st.error("🚫 Hisob bloklangan!")
                                else:
                                    st.session_state.update({'username':u,'logged_in':True,'login_time':datetime.now()})
                                    if rem and HAS_COOKIES:
                                        try:
                                            cookies["somo_user_session"] = u
                                            cookies.save()
                                        except:
                                            pass
                                    st.success("✅ Muvaffaqiyatli!")
                                    time.sleep(0.5)
                                    st.rerun()
                            else:
                                st.error("❌ Login yoki parol xato!")
                        except Exception as e:
                            st.error(f"❌ {e}")
                    else:
                        st.error("❌ Baza ulanmagan")

        with t2:
            with st.form("reg_form"):
                st.markdown("### ✨ Yangi Hisob")
                nu = st.text_input("👤 Username (min 3 belgi)")
                np_ = st.text_input("🔑 Parol (min 6 belgi)", type="password")
                nc = st.text_input("🔑 Tasdiqlash", type="password")
                agree = st.checkbox("Foydalanish shartlariga roziman ✅")
                sub2 = st.form_submit_button("🎉 Ro'yxatdan o'tish", use_container_width=True, type="primary")
                if sub2:
                    if not agree:   st.error("❌ Shartlarga rozilik bering!")
                    elif len(nu)<3: st.error("❌ Username kamida 3 belgi!")
                    elif len(np_)<6: st.error("❌ Parol kamida 6 belgi!")
                    elif np_!=nc:   st.error("❌ Parollar mos emas!")
                    elif user_db:
                        try:
                            recs = user_db.get_all_records()
                            if any(r['username']==nu for r in recs):
                                st.error("❌ Username band!")
                            else:
                                user_db.append_row([nu,hash_pw(np_),"active",str(datetime.now())])
                                st.balloons()
                                st.success("🎉 Ro'yxatdan o'tdingiz! Kirish bo'limiga o'ting.")
                        except Exception as e:
                            st.error(f"❌ {e}")

        with t3:
            st.markdown("""
### 🌌 Somo AI Ultra Pro Max v5.0

**AI Modellari:**
- ⚡ Groq + Llama 3.3 70B — Eng tez
- ✨ Google Gemini 2.0 Flash — Vision
- 🧠 Cerebras — Ultra tez
- 💫 Mistral Large — Yevropa AI
- 🌊 Cohere Command-R+ — RAG
- 🌐 OpenRouter — Bepul modellar

**Funksiyalar:**
📊 Excel • 📝 Word • 💻 Kod  
🌐 HTML • 📋 CSV • 🧠 Chat  
🎨 Rasm Yaratish • 🔍 Rasm Tahlili  
📄 PDF/DOCX Tahlil

👨‍💻 **Yaratuvchi:** Usmonov Sodiq  
👨‍💻 **Yordamchi:** Davlatov Mironshoh  
📅 **v5.0 Ultra** (2026)
            """)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;color:rgba(240,240,255,0.3);padding:30px;font-size:12px;'>
        🔒 Xavfsiz • ⚡ 24/7 Online • ♾️ 6x AI Models<br>
        © 2026 Somo AI Ultra Pro Max v5.0
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────
# SESSION DEFAULTS (after login)
# ─────────────────────────────────────────────────────
defaults = {
    'messages': [], 'total_msgs': 0, 'page': 'home',
    'uploaded_text': '', 'temperature': 0.6,
    'files_created': 0, 'ai_personality': 'Aqlli yordamchi',
    'chat_image': None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class='sb-user'>
        <div class='sb-avatar'>{st.session_state.username[0].upper()}</div>
        <div class='sb-name'>{st.session_state.username}</div>
        <div class='sb-badge'>● Aktiv</div>
    </div>
    """, unsafe_allow_html=True)

    # API status
    api_n = len([k for k in ai_clients if k not in ["gemini_key","gemini_vision","openrouter_key",
                                                       "stability","together"]])
    color = "#00b894" if api_n >= 3 else "#fdcb6e" if api_n >= 1 else "#d63031"
    st.markdown(f"""
    <div style='background:rgba(0,184,148,0.08);border:1px solid rgba(0,184,148,0.2);
                border-radius:12px;padding:10px 14px;margin-bottom:14px;'>
        <span style='color:{color};font-size:12px;font-weight:700;'>🔗 {api_n}/6 AI Ulangan</span>
        <div style='margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;'>
    """, unsafe_allow_html=True)
    row = ""
    for nm, ic in [("cerebras","🧠"),("groq","⚡"),("gemini","✨"),
                   ("mistral","💫"),("cohere","🌊"),("openrouter","🌐")]:
        c = "#00b894" if nm in ai_clients else "#d63031"
        row += f"<span style='color:{c};font-size:10px;font-weight:600;'>{ic}{'✓' if nm in ai_clients else '✗'}</span>"
    st.markdown(row + "</div></div>", unsafe_allow_html=True)

    if st.button("🔄 Qayta Ulanish", use_container_width=True, key="sb_reconnect"):
        for k in ['ai_clients','api_errors']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    st.markdown("### 🧭 Navigatsiya")
    pages = [
        ("home",     "🏠 Bosh sahifa"),
        ("chat",     "💬 Chat AI"),
        ("excel",    "📊 Excel"),
        ("word",     "📝 Word"),
        ("code",     "💻 Kod"),
        ("html",     "🌐 HTML"),
        ("csv",      "📋 CSV"),
        ("imggen",   "🎨 Rasm Yaratish"),
        ("imganalyze","🔍 Rasm Tahlili"),
        ("templates","⭐ Shablonlar"),
        ("analyze",  "📄 Hujjat Tahlili"),
        ("history",  "📜 Tarix"),
        ("feedback", "💌 Fikr"),
        ("profile",  "👤 Profil"),
    ]
    for pid, lbl in pages:
        t = "primary" if st.session_state.page == pid else "secondary"
        if st.button(lbl, use_container_width=True, key=f"nav_{pid}", type=t):
            st.session_state.page = pid
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Sessiya")
    ca, cb = st.columns(2)
    with ca:
        st.markdown(f"""<div class='metric-card' style='padding:12px;'>
            <div class='metric-num' style='font-size:22px;'>💬{len(st.session_state.messages)}</div>
            <div class='metric-lbl'>Xabarlar</div></div>""", unsafe_allow_html=True)
    with cb:
        st.markdown(f"""<div class='metric-card' style='padding:12px;'>
            <div class='metric-num' style='font-size:22px;'>📁{st.session_state.files_created}</div>
            <div class='metric-lbl'>Fayllar</div></div>""", unsafe_allow_html=True)

    if 'login_time' in st.session_state:
        mins = (datetime.now()-st.session_state.login_time).seconds // 60
        st.markdown(f"""<div class='metric-card' style='padding:12px;margin-top:8px;'>
            <div class='metric-num' style='font-size:22px;'>⏱{mins}</div>
            <div class='metric-lbl'>Daqiqa online</div></div>""", unsafe_allow_html=True)

    if st.session_state.page == "chat":
        st.markdown("---")
        st.markdown("### ⚙️ Chat")
        st.session_state.temperature = st.slider("🌡 Ijodkorlik", 0.0, 1.0,
                                                    st.session_state.temperature, 0.1)
        st.session_state.ai_personality = st.selectbox("🤖 AI uslubi", [
            "Aqlli yordamchi","Do'stona","Rasmiy mutaxassis",
            "Ijodkor yozuvchi","Texnik ekspert"])
        if st.button("🗑 Chatni tozalash", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        if st.session_state.messages:
            st.download_button("📥 JSON export",
                json.dumps(st.session_state.messages,ensure_ascii=False,indent=2).encode(),
                f"chat_{datetime.now().strftime('%Y%m%d')}.json",
                use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Chiqish", use_container_width=True, type="primary"):
        logout()

# ─────────────────────────────────────────────────────
# HELPER: Download button
# ─────────────────────────────────────────────────────
def show_download(file_bytes, fname, mime, label):
    if file_bytes:
        st.session_state.files_created += 1
        st.markdown("<div class='toast'>✅ Fayl tayyor! Yuklab olish uchun bosing.</div>",
                    unsafe_allow_html=True)
        st.download_button(f"⬇️ {label} yuklab olish", data=file_bytes,
                           file_name=fname, mime=mime,
                           use_container_width=True, type="primary")

def page_header(icon, title, sub):
    st.markdown(f"""
    <div style='background:var(--glass);border-bottom:1px solid var(--border);
                padding:24px 32px;backdrop-filter:blur(20px);margin-bottom:24px;'>
        <div style='display:flex;align-items:center;gap:16px;'>
            <span style='font-size:40px;'>{icon}</span>
            <div>
                <h2 style='font-family:Syne,sans-serif;font-size:26px;font-weight:700;
                           color:#f0f0ff;margin:0;'>{title}</h2>
                <p style='color:rgba(240,240,255,0.5);font-size:14px;margin:2px 0 0;'>{sub}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  PAGE: HOME
# ═══════════════════════════════════════════════════════
if st.session_state.page == "home":
    # Build particles JS
    particles_html = """
    <canvas id='particles-canvas' style='position:fixed;top:0;left:0;width:100%;height:100%;
        pointer-events:none;z-index:0;opacity:0.4;'></canvas>
    <script>
    (function(){
        const c = document.getElementById('particles-canvas');
        if(!c) return;
        const ctx = c.getContext('2d');
        c.width = window.innerWidth; c.height = window.innerHeight;
        const pts = Array.from({length:60},()=>({
            x: Math.random()*c.width, y: Math.random()*c.height,
            r: Math.random()*2+0.5,
            vx: (Math.random()-0.5)*0.4, vy: (Math.random()-0.5)*0.4,
            a: Math.random(),
            color: Math.random()>0.5 ? '#a29bfe' : '#fd79a8'
        }));
        function draw(){
            ctx.clearRect(0,0,c.width,c.height);
            pts.forEach(p=>{
                p.x+=p.vx; p.y+=p.vy; p.a+=0.01;
                if(p.x<0||p.x>c.width) p.vx*=-1;
                if(p.y<0||p.y>c.height) p.vy*=-1;
                ctx.beginPath();
                ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
                ctx.fillStyle = p.color;
                ctx.globalAlpha = 0.4+0.3*Math.sin(p.a);
                ctx.fill();
            });
            requestAnimationFrame(draw);
        }
        draw();
        window.addEventListener('resize',()=>{c.width=window.innerWidth;c.height=window.innerHeight;});
    })();
    </script>
    """
    st.components.v1.html(particles_html, height=0)

    # API badges
    api_html = ""
    for nm, ic, label in [("cerebras","🧠","Cerebras"),("groq","⚡","Groq"),("gemini","✨","Gemini"),
                           ("mistral","💫","Mistral"),("cohere","🌊","Cohere"),("openrouter","🌐","OpenRouter")]:
        cls = "api-pill-on" if nm in ai_clients else "api-pill-off"
        api_html += f"<span class='{cls}'>{ic} {label}</span>"

    st.markdown(f"""
    <div style='text-align:center;padding:80px 40px 40px;position:relative;z-index:1;'>
        <div style='font-size:90px;display:inline-block;margin-bottom:20px;
                    animation:logoPulse 3s ease-in-out infinite;
                    filter:drop-shadow(0 0 30px rgba(108,92,231,0.9));'>♾️</div>
        <h1 style='font-family:Syne,sans-serif;font-size:72px;font-weight:800;margin:0 0 12px;
                   background:linear-gradient(135deg,#fff 0%,#a29bfe 45%,#fd79a8 85%);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
                   letter-spacing:-3px;line-height:1;'>Somo-AI</h1>
        <p style='color:rgba(240,240,255,0.55);font-size:18px;font-weight:300;
                  letter-spacing:3px;text-transform:uppercase;margin:0 0 50px;'>
            Universal AI Platform · 6x Models · Vision + Generation
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature grid
    features = [
        ("📊","Excel Generator","AI jadvallar & formulalar"),
        ("📝","Word Hujjat","Professional dokumentlar"),
        ("💻","Kod Yozish","Python & web scripts"),
        ("🌐","HTML Sahifa","Zamonaviy web sahifalar"),
        ("📋","CSV Dataset","Katta ma'lumot to'plamlari"),
        ("🎨","Rasm Yaratish","AI image generation"),
        ("🔍","Rasm Tahlili","Vision & OCR"),
        ("📄","Hujjat Tahlili","PDF & DOCX tahlil"),
        ("🧠","Smart Chat","Har qanday savol"),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            page_map = {
                "📊":"excel","📝":"word","💻":"code","🌐":"html","📋":"csv",
                "🎨":"imggen","🔍":"imganalyze","📄":"analyze","🧠":"chat"
            }
            if st.button(f"{icon} {title}", key=f"home_feat_{i}", use_container_width=True):
                st.session_state.page = page_map.get(icon, "chat")
                st.rerun()
            st.markdown(f"<p style='text-align:center;color:rgba(240,240,255,0.4);font-size:12px;margin-top:-8px;'>{desc}</p>",
                       unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='text-align:center;padding:20px;'>
        <p style='color:rgba(240,240,255,0.3);font-size:12px;font-weight:600;margin-bottom:12px;
                  letter-spacing:2px;text-transform:uppercase;'>Ulangan AI Modellar</p>
        <div style='display:flex;justify-content:center;flex-wrap:wrap;gap:10px;'>{api_html}</div>
    </div>
    <div style='text-align:center;padding:30px;color:rgba(240,240,255,0.25);font-size:12px;'>
        Salom, <strong style='color:#a29bfe;'>{st.session_state.username}</strong> 👋 — Qanday yordam beray?
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  PAGE: CHAT
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "chat":
    page_header("💬","Chat AI","Aqlli suhbat — Excel, Word, Kod, Rasm va ko'proq")

    PERSONALITIES = {
        "Aqlli yordamchi":   "Sen Somo AI — aqlli, professional va foydali yordamchisan. Usmonov Sodiq tomonidan yaratilgan.",
        "Do'stona":          "Sen Somo AI — do'stona, samimiy va quvnoq yordamchisan.",
        "Rasmiy mutaxassis": "Sen Somo AI — rasmiy, aniq va professional mutaxassissan.",
        "Ijodkor yozuvchi":  "Sen Somo AI — ijodkor, original va kreativ yordamchisan.",
        "Texnik ekspert":    "Sen Somo AI — texnik, aniq va batafsil tushuntiruvchi ekspертsan."
    }

    # Messages container
    st.markdown('<div style="max-width:850px;margin:0 auto;padding:0 16px 140px;">', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("""
        <div style='text-align:center;padding:60px 20px;'>
            <div style='font-size:60px;margin-bottom:20px;animation:logoPulse 3s ease-in-out infinite;
                        display:inline-block;filter:drop-shadow(0 0 20px rgba(108,92,231,0.7));'>💬</div>
            <h2 style='font-family:Syne,sans-serif;font-size:28px;font-weight:700;color:#f0f0ff;margin:0 0 10px;'>
                Chatni boshlang!</h2>
            <p style='color:rgba(240,240,255,0.45);font-size:15px;'>
                Excel, Word, Kod, Rasm yoki oddiy savol — hammasi shu yerda 🚀
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Quick suggestions
        suggestions = [
            "📊 Oylik byudjet Excel yasab ber",
            "📝 Dasturchi uchun CV Word yoz",
            "💻 Telegram bot kodi yoz",
            "🎨 Futuristik shahar rasmi yarat",
            "🌐 Portfolio HTML sahifa yoz",
            "📋 100 ta mahsulot CSV yarat",
        ]
        cols = st.columns(3)
        for i, sug in enumerate(suggestions):
            with cols[i % 3]:
                if st.button(sug, key=f"sug_{i}", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":sug[2:].strip()})
                    st.rerun()

    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "file_data" in msg:
                fd = msg["file_data"]
                show_download(fd["bytes"], fd["name"], fd["mime"], fd["label"])
            if "image" in msg:
                img_data = base64.b64decode(msg["image"])
                st.image(img_data, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Image upload for vision
    with st.expander("📷 Rasm yuklash (tahlil uchun)"):
        chat_img = st.file_uploader("Rasm tanlang", type=["jpg","jpeg","png","gif","webp"], key="chat_img_upload")
        if chat_img:
            st.session_state.chat_image = chat_img.read()
            st.image(st.session_state.chat_image, width=200)
            st.success("✅ Rasm yuklandi. Savolingizni kiriting.")

    # Chat input
    if prompt := st.chat_input("💭 Xabar yuboring... (Excel, Word, Kod, Rasm yoki savol)"):
        # If image attached, force vision intent
        if st.session_state.chat_image:
            intent = "image_analyze"
        else:
            intent = detect_intent(prompt)

        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        save_to_db(st.session_state.username, "User", prompt)

        base_sys = PERSONALITIES.get(st.session_state.ai_personality, PERSONALITIES["Aqlli yordamchi"])

        with st.chat_message("assistant"):
            # Typing animation
            typing_placeholder = st.empty()
            typing_placeholder.markdown("""
            <div class='typing-dots'>
                <div class='typing-dot'></div>
                <div class='typing-dot'></div>
                <div class='typing-dot'></div>
                <span style='color:rgba(240,240,255,0.4);font-size:12px;margin-left:8px;'>Javob tayyorlanmoqda...</span>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.6)

            if intent == "excel":
                typing_placeholder.markdown("📊 **Excel fayl yaratilmoqda...**")
                fb, fn = generate_excel(prompt, st.session_state.temperature)
                typing_placeholder.empty()
                if fb and isinstance(fb, bytes):
                    rt = f"✅ **Excel fayl tayyor!** `{fn}`\n\nJadval tayyorlandim! Yuklab oling 👇"
                    fi = {"bytes":fb,"name":fn,
                          "mime":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                          "label":"Excel"}
                else:
                    rt = f"❌ Excel xatolik: {fn}"; fi = None
                st.markdown(rt)
                if fi: show_download(fi["bytes"],fi["name"],fi["mime"],fi["label"])
                md = {"role":"assistant","content":rt}
                if fi: md["file_data"] = fi
                st.session_state.messages.append(md)

            elif intent == "word":
                typing_placeholder.markdown("📝 **Word hujjat yaratilmoqda...**")
                fb, fn = generate_word(prompt, st.session_state.temperature)
                typing_placeholder.empty()
                if fb and isinstance(fb, bytes):
                    rt = f"✅ **Word hujjat tayyor!** `{fn}`\n\nProfessional hujjat tayyorlandim! 👇"
                    fi = {"bytes":fb,"name":fn,
                          "mime":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                          "label":"Word"}
                else:
                    rt = f"❌ Word xatolik: {fn}"; fi = None
                st.markdown(rt)
                if fi: show_download(fi["bytes"],fi["name"],fi["mime"],fi["label"])
                md = {"role":"assistant","content":rt}
                if fi: md["file_data"] = fi
                st.session_state.messages.append(md)

            elif intent == "code":
                typing_placeholder.markdown("💻 **Kod yozilmoqda...**")
                cb_, fn = generate_code(prompt, st.session_state.temperature)
                typing_placeholder.empty()
                ct = cb_.decode('utf-8')
                rt = f"✅ **Python kod tayyor!** `{fn}`\n\n```python\n{ct[:2000]}{'...' if len(ct)>2000 else ''}\n```"
                st.markdown(rt)
                st.download_button("⬇️ .py yuklab olish", cb_, fn, "text/x-python",
                                   use_container_width=True, type="primary")
                st.session_state.files_created += 1
                st.session_state.messages.append({"role":"assistant","content":rt})

            elif intent == "html":
                typing_placeholder.markdown("🌐 **HTML sahifa yaratilmoqda...**")
                hb, fn = generate_html(prompt, st.session_state.temperature)
                typing_placeholder.empty()
                ht = hb.decode('utf-8')
                rt = f"✅ **HTML sahifa tayyor!** `{fn}`\n\n```html\n{ht[:1200]}...\n```"
                st.markdown(rt)
                st.download_button("⬇️ HTML yuklab olish", hb, fn, "text/html",
                                   use_container_width=True, type="primary")
                st.session_state.files_created += 1
                st.session_state.messages.append({"role":"assistant","content":rt})

            elif intent == "csv":
                typing_placeholder.markdown("📋 **CSV yaratilmoqda...**")
                cb_, fn = generate_csv(prompt)
                typing_placeholder.empty()
                rt = f"✅ **CSV fayl tayyor!** `{fn}`"
                st.markdown(rt)
                st.download_button("⬇️ CSV yuklab olish", cb_, fn, "text/csv",
                                   use_container_width=True, type="primary")
                st.session_state.files_created += 1
                st.session_state.messages.append({"role":"assistant","content":rt})

            elif intent == "image_gen":
                typing_placeholder.markdown("🎨 **Rasm yaratilmoqda... ✨**")
                img_bytes, img_mime, img_source = generate_image(prompt)
                typing_placeholder.empty()
                if img_bytes:
                    img_b64 = base64.b64encode(img_bytes).decode()
                    source_label = {"pollinations":"Pollinations AI (bepul)","stability":"Stability AI","together":"Together AI (FLUX)"}.get(img_source, img_source)
                    rt = f"🎨 **Rasm tayyor!** ({source_label})\n\nPrompt: *{prompt}*"
                    st.markdown(rt)
                    st.image(img_bytes, use_container_width=True)
                    st.download_button("⬇️ Rasmni yuklab olish", img_bytes,
                                       f"somo_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                                       img_mime or "image/jpeg",
                                       use_container_width=True, type="primary")
                    st.session_state.files_created += 1
                    md = {"role":"assistant","content":rt,"image":img_b64}
                    st.session_state.messages.append(md)
                else:
                    rt = "❌ Rasm yaratib bo'lmadi. Internet ulanishini tekshiring."
                    st.markdown(rt)
                    st.session_state.messages.append({"role":"assistant","content":rt})

            elif intent == "image_analyze":
                img_data = st.session_state.chat_image
                if img_data:
                    typing_placeholder.markdown("🔍 **Rasm tahlil qilinmoqda...**")
                    analysis = analyze_image_with_ai(img_data, prompt)
                    typing_placeholder.empty()
                    rt = f"🔍 **Rasm Tahlili:**\n\n{analysis}"
                    st.markdown(rt)
                    st.session_state.chat_image = None
                    st.session_state.messages.append({"role":"assistant","content":rt})
                else:
                    typing_placeholder.empty()
                    rt = "📷 Rasm tahlili uchun avval rasm yuklang (yuqoridagi 📷 tugmani bosing)."
                    st.markdown(rt)
                    st.session_state.messages.append({"role":"assistant","content":rt})

            else:
                # Streaming-like text generation
                typing_placeholder.empty()
                msgs_to_send = [{"role":"system","content":f"""{base_sys}
Har doim aniq, tushunarli va foydali javob ber.
Javobingizni strukturalashtirilgan va o'qishga qulay qil.
Matematik formulalarni $ $ ichida yoz."""}]
                if st.session_state.uploaded_text:
                    msgs_to_send.append({"role":"system","content":
                        f"Yuklangan hujjat:\n{st.session_state.uploaded_text[:4000]}"})
                for m in st.session_state.messages[-16:]:
                    msgs_to_send.append({"role":m["role"],"content":m["content"]})

                response = call_ai(msgs_to_send, st.session_state.temperature)

                # Simulate streaming with word-by-word display
                words = response.split()
                stream_placeholder = st.empty()
                displayed = ""
                chunk_size = 3
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i+chunk_size])
                    displayed += chunk + " "
                    stream_placeholder.markdown(displayed + "▋")
                    time.sleep(0.025)
                stream_placeholder.markdown(response)

                st.session_state.messages.append({"role":"assistant","content":response})
                save_to_db("Somo AI","Assistant",response)

        st.session_state.total_msgs += 1
        st.rerun()

# ═══════════════════════════════════════════════════════
#  PAGE: EXCEL GENERATOR
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "excel":
    page_header("📊","Excel Generator","AI bilan professional Excel jadvallar yarating")

    examples = [
        "12 oylik moliyaviy byudjet: daromad, xarajat, sof foyda, formulalar",
        "100 ta mahsulot inventar: nomi, kategoriya, narxi, miqdori, jami",
        "Xodimlar ish haqi: ism, lavozim, maosh, soliq, sof to'lov",
        "Talabalar baholar: 5 ta fan, o'rtacha, reyting, davomad",
        "Haftalik ish jadvali: vazifalar, mas'ul, muddat, holat",
        "Savdo hisoboti: oylar, mahsulotlar, maqsad, haqiqiy, foiz",
        "Chiqimlar jadvali: kategoriya, reja, haqiqiy, farq",
        "KPI hisoboti: ko'rsatkichlar, maqsad, haqiqiy, baholash",
    ]
    st.markdown("#### 📋 Tez misollar:")
    c1, c2, c3, c4 = st.columns(4)
    for i, ex in enumerate(examples):
        with [c1,c2,c3,c4][i % 4]:
            if st.button(f"📋 {ex[:35]}...", key=f"ex_{i}", use_container_width=True):
                st.session_state.excel_prompt = ex

    st.markdown("---")
    ep = st.text_area("📝 Excel jadval tavsifi:", value=st.session_state.get("excel_prompt",""),
        placeholder="Masalan: 12 oylik byudjet jadvali, formulalar va ranglar bilan",
        height=120, key="excel_inp")
    c1, c2 = st.columns([3,1])
    with c2: temp = st.slider("Aniqlik", 0.0, 0.8, 0.2, 0.1, key="ex_temp")
    with c1: gen_btn = st.button("🚀 Excel Yaratish", use_container_width=True,
                                   type="primary", key="gen_exc")

    if gen_btn and ep:
        with st.spinner("📊 Yaratilmoqda..."):
            pr = st.progress(0)
            for i in [10,30,60,80]: time.sleep(0.25); pr.progress(i)
            fb, fn = generate_excel(ep, temp)
            pr.progress(100)
            if fb and isinstance(fb, bytes):
                st.success("✅ Excel fayl tayyor!")
                show_download(fb, fn,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","Excel")
            else:
                st.error(f"❌ Xatolik: {fn}")
    elif gen_btn:
        st.warning("⚠️ Jadval tavsifini kiriting!")

# ═══════════════════════════════════════════════════════
#  PAGE: WORD GENERATOR
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "word":
    page_header("📝","Word Generator","Professional hujjatlarni AI bilan yarating")

    we = [
        "Python dasturchi uchun professional rezyume, 3 yil tajriba",
        "IT kompaniya bilan hamkorlik taklifi maktubi",
        "Kvartira ijarasi shartnomasi standart shakl",
        "Ishga qabul qilish buyrug'i namunasi",
        "Kurs ishi: Sun'iy intellekt va machine learning",
        "Marketing strategiya hujjati 2026 yil",
        "Loyiha texnik topshirig'i (TOR)",
        "Biznes reja: IT startup, 1 yillik",
    ]
    st.markdown("#### 📄 Tez misollar:")
    c1, c2, c3, c4 = st.columns(4)
    for i, ex in enumerate(we):
        with [c1,c2,c3,c4][i % 4]:
            if st.button(f"📄 {ex[:32]}...", key=f"wex_{i}", use_container_width=True):
                st.session_state.word_prompt = ex

    st.markdown("---")
    wp = st.text_area("📝 Hujjat tavsifi:", value=st.session_state.get("word_prompt",""),
        placeholder="Masalan: Python dasturchi uchun professional rezyume",
        height=120, key="word_inp")
    gen_word = st.button("🚀 Word Yaratish", use_container_width=True,
                          type="primary", key="gen_word")
    if gen_word and wp:
        with st.spinner("📝 Yaratilmoqda..."):
            pr = st.progress(0)
            for i in [15,40,70,90]: time.sleep(0.3); pr.progress(i)
            fb, fn = generate_word(wp)
            pr.progress(100)
            if fb and isinstance(fb, bytes):
                st.success("✅ Word hujjat tayyor!")
                show_download(fb, fn,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document","Word")
            else:
                st.error(f"❌ Xatolik: {fn}")
    elif gen_word:
        st.warning("⚠️ Hujjat tavsifini kiriting!")

# ═══════════════════════════════════════════════════════
#  PAGE: CODE GENERATOR
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "code":
    page_header("💻","Kod Generator","Professional Python & web kodi — tayyor faylda")

    ce = [
        "Streamlit dashboard: savdo statistikasi, grafik",
        "FastAPI REST API: CRUD operatsiyalar, JWT auth",
        "Telegram bot: buyruqlar, inline keyboard, API",
        "Web scraper: requests, BeautifulSoup, CSV export",
        "ML model: sklearn, classification, confusion matrix",
        "File organizer: papkalarni turi bo'yicha tartibla",
        "Discord bot: prefix commands, embed messages",
        "Email bot: avtomatik yuborish, shablonlar",
    ]
    st.markdown("#### 💡 Tez misollar:")
    c1, c2, c3, c4 = st.columns(4)
    for i, ex in enumerate(ce):
        with [c1,c2,c3,c4][i % 4]:
            if st.button(f"💡 {ex[:30]}...", key=f"cex_{i}", use_container_width=True):
                st.session_state.code_prompt = ex

    st.markdown("---")
    cp = st.text_area("📝 Kod tavsifi:", value=st.session_state.get("code_prompt",""),
        placeholder="Masalan: Telegram bot, start komandasi, foydalanuvchi ma'lumotlarini saqlash",
        height=120, key="code_inp")
    c1, c2 = st.columns([3,1])
    with c2: ct = st.slider("Ijodkorlik", 0.0, 0.6, 0.1, 0.1, key="code_temp")
    gen_code_btn = st.button("🚀 Kod Yaratish", use_container_width=True,
                              type="primary", key="gen_code")
    if gen_code_btn and cp:
        with st.spinner("💻 Yozilmoqda..."):
            cb_, fn = generate_code(cp, ct)
            st.success("✅ Kod tayyor!")
            st.code(cb_.decode('utf-8'), language="python")
            st.download_button("⬇️ .py yuklab olish", cb_, fn, "text/x-python",
                               use_container_width=True, type="primary")
            st.session_state.files_created += 1
    elif gen_code_btn:
        st.warning("⚠️ Kod tavsifini kiriting!")

# ═══════════════════════════════════════════════════════
#  PAGE: HTML GENERATOR
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "html":
    page_header("🌐","HTML Generator","Chiroyli veb sahifalar — bitta faylda")

    he = [
        "Portfolio sahifa: dasturchi, dark theme, animatsiyalar",
        "Restaurant menu: chiroyli dizayn, kategoriyalar",
        "SaaS Landing Page: hero, features, pricing, CTA",
        "Dashboard UI: statistika kartalar, jadvallar",
        "Crypto tracker: real-time look, dark neon",
        "Blog sahifasi: zamonaviy, minimalist",
    ]
    c1, c2, c3 = st.columns(3)
    for i, ex in enumerate(he):
        with [c1,c2,c3][i % 3]:
            if st.button(f"🌐 {ex[:35]}...", key=f"hex_{i}", use_container_width=True):
                st.session_state.html_prompt = ex

    st.markdown("---")
    hp_ = st.text_area("📝 Sahifa tavsifi:", value=st.session_state.get("html_prompt",""),
        placeholder="Masalan: Zamonaviy portfolio, dark theme, CSS animatsiyalar, responsive",
        height=120, key="html_inp")
    gen_html_btn = st.button("🚀 HTML Yaratish", use_container_width=True,
                              type="primary", key="gen_html")
    if gen_html_btn and hp_:
        with st.spinner("🌐 Yaratilmoqda..."):
            hb, fn = generate_html(hp_, 0.5)
            ht = hb.decode('utf-8')
            st.success("✅ HTML sahifa tayyor!")
            with st.expander("📄 HTML kodini ko'rish"):
                st.code(ht[:4000]+("..." if len(ht)>4000 else ""), language="html")
            st.download_button("⬇️ HTML yuklab olish", hb, fn, "text/html",
                               use_container_width=True, type="primary")
            st.session_state.files_created += 1
    elif gen_html_btn:
        st.warning("⚠️ Sahifa tavsifini kiriting!")

# ═══════════════════════════════════════════════════════
#  PAGE: CSV GENERATOR
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "csv":
    page_header("📋","CSV Generator","Katta datasetlar — tezda tayyor")

    cse = [
        "100 ta mahsulot: nomi, narxi, kategoriya, miqdori, brend",
        "50 ta xodim: ism, lavozim, maosh, bo'lim, yosh",
        "200 ta talaba: ism, guruh, baholar, o'rtacha, davomad",
        "Dunyo mamlakatlari: nomi, poytaxti, aholi, hudud, YIM",
        "Top 100 dasturlash tillari: nomi, turi, yil, TIOBE",
        "E-commerce buyurtmalar: ID, mahsulot, miqdor, narx, sana",
    ]
    c1, c2, c3 = st.columns(3)
    for i, ex in enumerate(cse):
        with [c1,c2,c3][i % 3]:
            if st.button(f"📋 {ex[:35]}...", key=f"cse_{i}", use_container_width=True):
                st.session_state.csv_prompt = ex

    st.markdown("---")
    csvp = st.text_area("📝 Ma'lumotlar tavsifi:", value=st.session_state.get("csv_prompt",""),
        placeholder="Masalan: 100 ta O'zbekiston shahri: nomi, viloyat, aholi, maydon",
        height=120, key="csv_inp")
    gen_csv_btn = st.button("🚀 CSV Yaratish", use_container_width=True,
                             type="primary", key="gen_csv")
    if gen_csv_btn and csvp:
        with st.spinner("📋 Yaratilmoqda..."):
            cb_, fn = generate_csv(csvp)
            try:
                df = pd.read_csv(io.BytesIO(cb_))
                st.success(f"✅ CSV tayyor! {len(df)} satr, {len(df.columns)} ustun")
                st.dataframe(df.head(15), use_container_width=True)
            except:
                st.success("✅ CSV fayl tayyor!")
            st.download_button("⬇️ CSV yuklab olish", cb_, fn, "text/csv",
                               use_container_width=True, type="primary")
            st.session_state.files_created += 1
    elif gen_csv_btn:
        st.warning("⚠️ Ma'lumotlar tavsifini kiriting!")

# ═══════════════════════════════════════════════════════
#  PAGE: IMAGE GENERATION
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "imggen":
    page_header("🎨","Rasm Yaratish","AI bilan har qanday rasmni yarating — bepul!")

    st.markdown("""
    <div style='background:rgba(108,92,231,0.1);border:1px solid rgba(108,92,231,0.25);
                border-radius:14px;padding:14px 20px;margin-bottom:20px;'>
        <p style='margin:0;color:#a29bfe;font-size:13px;'>
            ✨ <strong>Pollinations.AI</strong> — Hech qanday API key shart emas! Bepul, cheksiz rasm yaratish.
            FLUX, DALL-E uslubida 1024×1024 rasmlar.
        </p>
    </div>
    """, unsafe_allow_html=True)

    img_examples = [
        ("🏙", "Futuristic neon city at night, cyberpunk style, rain reflections"),
        ("🤖", "Cute AI robot reading books, soft lighting, pastel colors"),
        ("🌌", "Galaxy spiral nebula, deep space, vibrant colors, 8k"),
        ("🐉", "Majestic dragon flying over mountains, fantasy art, detailed"),
        ("🎨", "Abstract art with geometric shapes, vivid colors, modern"),
        ("🏔", "Snowy mountain landscape, sunrise, golden hour, realistic"),
        ("🦁", "Majestic lion portrait, golden mane, dramatic lighting"),
        ("🌸", "Japanese cherry blossom garden, peaceful, watercolor style"),
    ]

    st.markdown("#### 💡 Tez promptlar:")
    c1, c2, c3, c4 = st.columns(4)
    for i, (ic, prompt_ex) in enumerate(img_examples):
        with [c1,c2,c3,c4][i % 4]:
            if st.button(f"{ic} {prompt_ex[:28]}...", key=f"img_ex_{i}", use_container_width=True):
                st.session_state.img_prompt = prompt_ex

    st.markdown("---")
    c1, c2 = st.columns([3,1])
    with c1:
        img_prompt = st.text_area("🎨 Rasm tavsifi (ingliz yoki o'zbek tilida):",
            value=st.session_state.get("img_prompt",""),
            placeholder="Masalan: Beautiful sunset over mountains, realistic, 8k quality",
            height=100, key="img_inp")
    with c2:
        st.markdown("#### 🎛 Sozlamalar")
        enhance_prompt = st.checkbox("✨ Auto-enhance", value=True)
        add_style = st.selectbox("Stil:", ["Auto","Realistic","Anime","Oil painting","Watercolor","Digital art","Pencil sketch"])

    gen_img_btn = st.button("🎨 Rasm Yaratish", use_container_width=True,
                             type="primary", key="gen_img")

    if gen_img_btn and img_prompt:
        # Enhance prompt
        final_prompt = img_prompt
        if enhance_prompt:
            style_suffixes = {
                "Realistic": ", ultra realistic, 8k, detailed, professional photography",
                "Anime": ", anime style, Studio Ghibli, detailed, vibrant colors",
                "Oil painting": ", oil painting style, textured, museum quality, artistic",
                "Watercolor": ", watercolor painting, soft colors, artistic, beautiful",
                "Digital art": ", digital art, concept art, detailed, vibrant",
                "Pencil sketch": ", pencil sketch, detailed, artistic drawing",
                "Auto": ", high quality, detailed, beautiful composition, professional"
            }
            final_prompt += style_suffixes.get(add_style, style_suffixes["Auto"])

        with st.spinner("🎨 Rasm yaratilmoqda... (30-60 soniya)"):
            # Progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            for i, msg_ in [(10,"🎨 Prompt tayyorlanmoqda..."),
                            (30,"✨ AI rasm chizmoqda..."),
                            (60,"🖼 Render qilinmoqda..."),
                            (85,"📥 Yuklab olinmoqda...")]:
                progress_bar.progress(i)
                status_text.markdown(f"<p style='color:rgba(240,240,255,0.5);font-size:13px;'>{msg_}</p>",
                                     unsafe_allow_html=True)
                time.sleep(0.3)

            img_bytes, img_mime, img_source = generate_image(final_prompt)
            progress_bar.progress(100)
            status_text.empty()

        if img_bytes:
            source_labels = {
                "pollinations": "Pollinations AI (bepul)",
                "stability": "Stability AI",
                "together": "Together AI (FLUX)"
            }
            src = source_labels.get(img_source, img_source)
            st.success(f"✅ Rasm tayyor! ({src})")

            c1, c2, c3 = st.columns([1,3,1])
            with c2:
                st.image(img_bytes, caption=img_prompt[:80], use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button("⬇️ JPG yuklab olish", img_bytes,
                                   f"somo_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                                   img_mime or "image/jpeg",
                                   use_container_width=True, type="primary")
            with col2:
                if st.button("🔄 Yangi variant", use_container_width=True):
                    st.rerun()
            st.session_state.files_created += 1

            # Show prompt info
            st.markdown(f"""
            <div style='background:rgba(108,92,231,0.08);border:1px solid rgba(108,92,231,0.2);
                        border-radius:12px;padding:12px 16px;margin-top:16px;'>
                <p style='margin:0;color:rgba(240,240,255,0.5);font-size:12px;'>
                    <strong style='color:#a29bfe;'>📝 Prompt:</strong> {final_prompt}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Rasm yaratib bo'lmadi. Internet ulanishini tekshiring.")
    elif gen_img_btn:
        st.warning("⚠️ Rasm tavsifini kiriting!")

    # Gallery section
    st.markdown("---")
    st.markdown("""
    <h3 style='font-family:Syne,sans-serif;color:#f0f0ff;'>💡 Yaxshi prompt yozish bo'yicha maslahatlar</h3>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **✅ Yaxshi promptlar:**
        - Batafsil tasvirlar bering
        - Uslubni ko'rsating (realistic, anime, oil painting)
        - Yorug'likni eslatmang (golden hour, dramatic lighting)
        - Sifatni ko'rsating (8k, ultra detailed, high quality)
        """)
    with col2:
        st.markdown("""
        **💡 Misol promptlar:**
        - `A cozy cafe in Tokyo rain, neon lights, cinematic`
        - `Portrait of a wise wizard, fantasy art, detailed`
        - `Abstract digital landscape, colorful, modern art`
        - `Baby dragon sleeping on a pile of books, cute`
        """)

# ═══════════════════════════════════════════════════════
#  PAGE: IMAGE ANALYSIS
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "imganalyze":
    page_header("🔍","Rasm Tahlili","AI bilan rasmlardagi ma'lumotlarni tahlil qiling")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("### 📷 Rasm Yuklash")
        uploaded_img = st.file_uploader("Rasm tanlang (JPG, PNG, GIF, WebP)",
                                         type=["jpg","jpeg","png","gif","webp"],
                                         key="analyze_img")
        if uploaded_img:
            img_bytes = uploaded_img.read()
            st.image(img_bytes, use_container_width=True)
            st.info(f"📊 {uploaded_img.name} — {len(img_bytes)//1024} KB")

            st.markdown("### ❓ Savollar")
            quick_qs = [
                "Bu rasmda nima bor?",
                "Rasmni batafsil tavsifla",
                "Rasmdagi matnni o'qi",
                "Bu nimaning rasmi?",
                "Rasmda qancha odam bor?",
                "Ranglarni tahlil qil",
                "Rasmni kayfiyatini ayt",
                "Texnik tafsilotlarni ko'rsat",
            ]
            for i, q in enumerate(quick_qs[:4]):
                if st.button(q, key=f"quick_q_{i}", use_container_width=True):
                    st.session_state.analyze_question = q
            for i, q in enumerate(quick_qs[4:]):
                if st.button(q, key=f"quick_q2_{i}", use_container_width=True):
                    st.session_state.analyze_question = q

    with c2:
        st.markdown("### 🧠 Tahlil Natijasi")
        if uploaded_img:
            custom_q = st.text_area("✍️ O'z savolingiz:",
                value=st.session_state.get("analyze_question",""),
                placeholder="Rasmda nima ko'ryapsiz? Nima so'raysiz?",
                height=100, key="analyze_q")
            analyze_btn = st.button("🔍 Rasmni Tahlil Qil",
                                     use_container_width=True, type="primary")
            if analyze_btn:
                with st.spinner("🔍 Tahlil qilinmoqda..."):
                    q = custom_q or "Bu rasmni batafsil tahlil qil. Nima ko'ryapsan?"
                    result = analyze_image_with_ai(img_bytes, q, uploaded_img.type)
                st.markdown(f"""
                <div style='background:var(--glass);border:1px solid var(--border);
                            border-radius:16px;padding:20px;'>
                    <h4 style='font-family:Syne,sans-serif;color:#a29bfe;margin:0 0 12px;'>
                        🔍 Tahlil Natijasi</h4>
                    <div style='color:#f0f0ff;line-height:1.7;'>{result}</div>
                </div>
                """, unsafe_allow_html=True)

                # Save result
                result_bytes = result.encode('utf-8')
                st.download_button("📥 Tahlilni yuklab olish", result_bytes,
                    f"image_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    "text/plain", use_container_width=True)
        else:
            st.markdown("""
            <div style='text-align:center;padding:60px 20px;color:rgba(240,240,255,0.3);'>
                <div style='font-size:60px;margin-bottom:16px;'>🖼</div>
                <p>Tahlil qilish uchun chap tarafdan rasm yuklang</p>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  PAGE: TEMPLATES
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "templates":
    page_header("⭐","Shablonlar Markazi","Tayyor shablonlar bilan tezlashtirib ishlang")

    TMPLS = {
        "💼 Biznes": [
            {"title":"💰 Moliyaviy Byudjet","prompt":"12 oylik moliyaviy byudjet Excel: daromad, xarajatlar, sof foyda, Excel formulalar, jami","type":"excel"},
            {"title":"📈 Savdo Hisoboti","prompt":"Oylik savdo hisoboti Excel: mahsulotlar bo'yicha, maqsad vs haqiqiy, foiz bajarilishi, grafik uchun","type":"excel"},
            {"title":"📋 Biznes Reja","prompt":"IT startup biznes reja Word: ijroiya xulosa, bozor tahlili, mahsulot tavsifi, moliyaviy prognoz","type":"word"},
            {"title":"🤝 Hamkorlik Xati","prompt":"Professional hamkorlik taklifi maktubi Word: kompaniya taqdimoti, xizmatlar, takliflar, imzo","type":"word"},
        ],
        "💻 Dasturlash": [
            {"title":"🤖 Telegram Bot","prompt":"Python Telegram bot aiogram v3: /start, /help komandalar, inline keyboard, handler, polling","type":"code"},
            {"title":"🌐 FastAPI CRUD","prompt":"FastAPI CRUD API: foydalanuvchilar, Pydantic models, SQLite, swagger docs, JWT auth","type":"code"},
            {"title":"📊 Data Dashboard","prompt":"Streamlit dashboard: CSV yuklab olish, filtrlash, Plotly grafiklari, statistika kartalar","type":"code"},
            {"title":"🌐 Portfolio Sayt","prompt":"Ultra zamonaviy portfolio web sayt: hero section, skills, projects, contact, dark neon theme, CSS animations","type":"html"},
        ],
        "📚 Ta'lim": [
            {"title":"📖 Dars Rejasi","prompt":"Python asoslari bo'yicha 45 daqiqalik dars rejasi Word: maqsadlar, kirish, nazariy, amaliy, xulosa","type":"word"},
            {"title":"📝 Test Savollari","prompt":"Python dasturlash bo'yicha 25 ta test savoli Excel: savol, 4 variant, to'g'ri javob, daraja","type":"excel"},
            {"title":"🎓 Baholar Jadvali","prompt":"30 ta talaba baholar jadvali Excel: ism, 6 fan, o'rtacha, reyting, davomad foizi, formulalar","type":"excel"},
            {"title":"📚 Kurs Ishi","prompt":"Kurs ishi Word: 'Machine Learning va Sun'iy Intellekt'. Kirish, 3 bob, xulosa, adabiyotlar, muqova","type":"word"},
        ],
        "👤 Shaxsiy": [
            {"title":"📄 Rezyume","prompt":"Python backend dasturchi professional rezyume Word: tajriba, texnik ko'nikmalar, ta'lim, loyihalar","type":"word"},
            {"title":"📅 Oylik Reja","prompt":"30 kunlik ish rejasi Excel: vazifalar, muddat, ustuvorlik, holat, ko'rsatkich foiz","type":"excel"},
            {"title":"💰 Shaxsiy Byudjet","prompt":"Shaxsiy oylik byudjet Excel: daromadlar, xarajatlar kategoriyalari, tejash, formulalar","type":"excel"},
            {"title":"🏋️ Sport Jadvali","prompt":"3 oylik sport mashg'ulotlari Excel: mashqlar, takroriylik, og'irlik, progres, haftalik hisobot","type":"excel"},
        ]
    }

    TC = {"excel":"#10b981","word":"#3b82f6","code":"#f59e0b","html":"#f43f5e"}
    TL = {"excel":"📊 Excel","word":"📝 Word","code":"💻 Kod","html":"🌐 HTML"}

    sel = st.selectbox("📁 Kategoriya:", list(TMPLS.keys()), key="tmpl_cat")
    st.markdown("---")

    cols2 = st.columns(2)
    for i, tmpl in enumerate(TMPLS[sel]):
        with cols2[i % 2]:
            col_hex = TC.get(tmpl["type"],"#6C5CE7")
            st.markdown(f"""
            <div style='background:var(--glass);border:1px solid var(--border);border-radius:18px;
                        padding:20px;margin-bottom:14px;transition:all 0.3s;'>
                <h3 style='color:#f0f0ff;margin:0 0 8px;font-family:Syne,sans-serif;font-size:16px;'>
                    {tmpl['title']}</h3>
                <span style='background:{col_hex}22;color:{col_hex};border:1px solid {col_hex}44;
                             padding:3px 12px;border-radius:12px;font-size:11px;font-weight:700;'>
                    {TL.get(tmpl["type"],"")}</span>
                <p style='color:rgba(240,240,255,0.45);font-size:12px;margin-top:10px;line-height:1.5;'>
                    {tmpl["prompt"][:90]}...</p>
            </div>""", unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                if st.button("🚀 Yaratish", key=f"tg_{sel}_{i}", use_container_width=True, type="primary"):
                    with st.spinner("⏳ Yaratilmoqda..."):
                        tt = tmpl["type"]
                        if tt == "excel":
                            fb, fn = generate_excel(tmpl["prompt"])
                            if fb and isinstance(fb, bytes):
                                show_download(fb,fn,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","Excel")
                        elif tt == "word":
                            fb, fn = generate_word(tmpl["prompt"])
                            if fb and isinstance(fb, bytes):
                                show_download(fb,fn,"application/vnd.openxmlformats-officedocument.wordprocessingml.document","Word")
                        elif tt == "code":
                            fb, fn = generate_code(tmpl["prompt"])
                            st.download_button("⬇️ .py",fb,fn,"text/x-python",key=f"dl_{sel}_{i}")
                            st.session_state.files_created += 1
                        elif tt == "html":
                            fb, fn = generate_html(tmpl["prompt"])
                            st.download_button("⬇️ HTML",fb,fn,"text/html",key=f"dl_{sel}_{i}")
                            st.session_state.files_created += 1
            with b2:
                if st.button("💬 Chatga", key=f"tc_{sel}_{i}", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":tmpl["prompt"]})
                    st.session_state.page = "chat"
                    st.rerun()

# ═══════════════════════════════════════════════════════
#  PAGE: DOCUMENT ANALYSIS
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "analyze":
    page_header("📄","Hujjat Tahlili","PDF va Word fayllarni AI bilan tahlil qiling")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📂 Fayl Yuklash")
        uploaded = st.file_uploader("PDF yoki DOCX faylni yuklang",
                                     type=["pdf","docx"], key="analyze_upload")
        if uploaded:
            with st.spinner("📄 O'qilmoqda..."):
                text = process_doc(uploaded)
                st.session_state.uploaded_text = text
            if text:
                st.success(f"✅ {uploaded.name}")
                st.markdown(f"""
                <div style='background:rgba(0,184,148,0.08);border:1px solid rgba(0,184,148,0.2);
                            border-radius:12px;padding:12px 16px;margin:10px 0;'>
                    📊 <strong style='color:#00b894;'>{len(text):,}</strong> belgi,
                    ~<strong style='color:#00b894;'>{len(text.split()):,}</strong> so'z
                </div>
                """, unsafe_allow_html=True)
                with st.expander("📄 Matnni ko'rish"):
                    st.text(text[:3000] + ("..." if len(text) > 3000 else ""))
            else:
                st.error("❌ Fayl o'qilmadi. Boshqa formatda yuklang.")

    with c2:
        st.markdown("### 🧠 Tahlil Amaliyotlari")
        if st.session_state.uploaded_text:
            actions = {
                "📝 Qisqa xulosa":    "Ushbu hujjatni 5-7 ta asosiy nuqta bilan qisqacha xulosasini yoz.",
                "🔑 Asosiy g'oyalar": "5-10 ta eng muhim g'oya va faktlarni raqamlangan ro'yxatda ko'rsat.",
                "❓ Savol-Javob":      "Hujjat bo'yicha 10 ta muhim savol va batafsil javoblarni tuzib ber.",
                "🌐 Tarjima (EN)":    "Hujjat mazmunini ingliz tiliga to'liq tarjima qil.",
                "📊 Statistika":      "Hujjatdagi barcha raqamlar, foizlar va statistikani jadval ko'rinishida ko'rsat.",
                "✅ Vazifalar":        "Hujjatdan amaliy vazifalar va keyingi qadamlarni chiqarib ber.",
            }
            cols_a = st.columns(2)
            for i, (act, prm) in enumerate(actions.items()):
                with cols_a[i % 2]:
                    if st.button(act, key=f"act_{i}", use_container_width=True):
                        with st.spinner("🤔 Tahlil qilinmoqda..."):
                            r = call_ai([
                                {"role":"system","content":"Sen hujjat tahlilchisan. Aniq va batafsil javob ber."},
                                {"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:5000]}\n\n{prm}"}
                            ])
                        st.markdown(f"**{act}**")
                        st.markdown(r)
                        st.download_button("📥 Yuklab olish",
                            r.encode(), f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            "text/plain", key=f"dl_act_{i}")

            st.markdown("---")
            cq = st.text_input("🔍 O'z savolingiz:", placeholder="Hujjat haqida savol bering...",
                               key="custom_question")
            if st.button("🔍 Qidirish", use_container_width=True, type="primary") and cq:
                with st.spinner("🤔 Qidirilmoqda..."):
                    r = call_ai([
                        {"role":"system","content":"Hujjat asosida aniq va batafsil javob ber."},
                        {"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:5000]}\n\nSavol: {cq}"}
                    ])
                st.markdown(r)
        else:
            st.markdown("""
            <div style='text-align:center;padding:50px;color:rgba(240,240,255,0.3);'>
                <div style='font-size:50px;margin-bottom:16px;'>📂</div>
                <p>Avval chap tarafdan PDF yoki DOCX yuklang</p>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  PAGE: HISTORY
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "history":
    page_header("📜","Chat Tarixi","Barcha suhbatlaringiz")

    if st.session_state.messages:
        user_msgs = [m for m in st.session_state.messages if m["role"]=="user"]
        ai_msgs   = [m for m in st.session_state.messages if m["role"]=="assistant"]

        st.markdown(f"""
        <div class='metric-row'>
            <div class='metric-card'><div class='metric-num'>💬{len(user_msgs)}</div><div class='metric-lbl'>Sizning</div></div>
            <div class='metric-card'><div class='metric-num'>🤖{len(ai_msgs)}</div><div class='metric-lbl'>AI javoblari</div></div>
            <div class='metric-card'><div class='metric-num'>📁{st.session_state.files_created}</div><div class='metric-lbl'>Fayllar</div></div>
            <div class='metric-card'><div class='metric-num'>📊{len(st.session_state.messages)}</div><div class='metric-lbl'>Jami</div></div>
        </div>
        """, unsafe_allow_html=True)

        srch = st.text_input("🔍 Qidirish:", placeholder="Xabar qidirish...", key="hist_search")
        show = st.session_state.messages
        if srch:
            show = [m for m in show if srch.lower() in m.get("content","").lower()]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("📥 JSON",
                json.dumps(st.session_state.messages,ensure_ascii=False,indent=2).encode(),
                f"chat_{datetime.now().strftime('%Y%m%d')}.json","application/json",
                use_container_width=True)
        with c2:
            txt_export = "\n\n".join([f"[{m['role'].upper()}]\n{m['content']}"
                                       for m in st.session_state.messages])
            st.download_button("📄 TXT",
                txt_export.encode(),
                f"chat_{datetime.now().strftime('%Y%m%d')}.txt","text/plain",
                use_container_width=True)
        with c3:
            if st.button("🗑 Tarixni tozalash", use_container_width=True, type="primary"):
                st.session_state.messages = []
                st.rerun()

        st.markdown("---")
        for msg in reversed(show[-60:]):
            bg    = "rgba(108,92,231,0.1)" if msg["role"]=="user" else "rgba(0,184,148,0.07)"
            bdr   = "rgba(108,92,231,0.4)" if msg["role"]=="user" else "rgba(0,184,148,0.3)"
            ic    = "👤" if msg["role"]=="user" else "🤖"
            st.markdown(f"""
            <div style='background:{bg};border-left:3px solid {bdr};
                        padding:14px 18px;border-radius:10px;margin:8px 0;'>
                <strong style='color:#a29bfe;font-size:13px;'>{ic} {msg["role"].title()}</strong>
                <p style='margin:6px 0 0;color:rgba(240,240,255,0.7);font-size:13px;line-height:1.5;'>
                    {msg["content"][:400]}{"..." if len(msg.get("content",""))>400 else ""}</p>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center;padding:60px;color:rgba(240,240,255,0.3);'>
            <div style='font-size:60px;margin-bottom:16px;'>💬</div>
            <p>Hali chat tarixi yo'q. Chat sahifasiga o'ting!</p>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  PAGE: FEEDBACK
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "feedback":
    page_header("💌","Fikr-Mulohazalar","Sizning fikringiz bizni yaxshiroq qiladi!")

    c1, c2 = st.columns([3, 2])
    with c1:
        with st.form("fb_form"):
            st.markdown("### ⭐ Baholang")
            rating = st.select_slider("Baho:", options=[1,2,3,4,5], value=5,
                                       format_func=lambda x: "⭐"*x)
            st.markdown(f"<p style='font-size:48px;text-align:center;'>"
                       f"{'⭐'*rating}</p>", unsafe_allow_html=True)
            category = st.selectbox("📂 Kategoriya:", [
                "Umumiy fikr","Xato haqida","Yangi funksiya taklifi",
                "Dizayn","Tezlik","AI sifati","Boshqa"])
            message  = st.text_area("✍️ Xabaringiz:", height=120,
                                     placeholder="Fikrlaringizni yozing...")
            email    = st.text_input("📧 Email (ixtiyoriy):")
            sub      = st.form_submit_button("📤 Yuborish",
                                              use_container_width=True, type="primary")
            if sub:
                if not message or len(message) < 10:
                    st.error("❌ Kamida 10 belgi!")
                elif fb_db:
                    try:
                        fb_db.append_row([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            st.session_state.username, rating, category,
                            message, email or "N/A", "Yangi"])
                        st.balloons()
                        st.markdown("<div class='toast'>✅ Rahmat! Fikringiz yuborildi. 🙏</div>",
                                    unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ {e}")
                else:
                    st.success("✅ Demo rejim — yuborildi!")

    with c2:
        st.markdown("### 📊 So'nggi fikrlar")
        if fb_db:
            try:
                all_fb = fb_db.get_all_records()
                if all_fb:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-num'>{len(all_fb)}</div>
                        <div class='metric-lbl'>Jami fikrlar</div>
                    </div>
                    """, unsafe_allow_html=True)
                    rl = [int(f.get('Rating',5)) for f in all_fb if f.get('Rating')]
                    if rl:
                        avg = sum(rl)/len(rl)
                        st.markdown(f"""
                        <div class='metric-card' style='margin-top:10px;'>
                            <div class='metric-num'>{avg:.1f}/5</div>
                            <div class='metric-lbl'>⭐ O'rtacha baho</div>
                        </div>
                        """, unsafe_allow_html=True)
                    for fb in all_fb[-5:]:
                        r_val = int(fb.get('Rating',5))
                        st.markdown(f"""
                        <div style='background:var(--glass);border:1px solid var(--border);
                                    border-radius:12px;padding:12px;margin:6px 0;'>
                            <strong style='color:#fdcb6e;'>{"⭐"*r_val}</strong>
                            <span style='color:#a29bfe;font-size:11px;'> — {fb.get("Username","")}</span>
                            <p style='margin:4px 0 0;font-size:12px;color:rgba(240,240,255,0.6);'>
                                {str(fb.get("Message",""))[:80]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
            except:
                st.info("Statistika yuklanmadi")

# ═══════════════════════════════════════════════════════
#  PAGE: PROFILE
# ═══════════════════════════════════════════════════════
elif st.session_state.page == "profile":
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(108,92,231,0.2),rgba(253,121,168,0.15));
                border:1px solid rgba(108,92,231,0.3);border-radius:24px;padding:40px;
                text-align:center;margin:20px;'>
        <div style='width:90px;height:90px;border-radius:50%;
                    background:linear-gradient(135deg,#6C5CE7,#fd79a8);
                    margin:0 auto 16px;line-height:90px;font-size:42px;font-weight:800;
                    color:white;font-family:Syne,sans-serif;
                    border:3px solid rgba(255,255,255,0.15);
                    box-shadow:0 0 30px rgba(108,92,231,0.5);'>
            {st.session_state.username[0].upper()}
        </div>
        <h2 style='font-family:Syne,sans-serif;font-size:28px;color:#f0f0ff;margin:0 0 6px;'>
            {st.session_state.username}</h2>
        <p style='color:rgba(240,240,255,0.4);font-size:14px;margin:0;'>🟢 Aktiv foydalanuvchi</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    sess_mins = (datetime.now()-st.session_state.login_time).seconds//60 if 'login_time' in st.session_state else 0
    level = len(st.session_state.messages)//5 + 1
    c1,c2,c3,c4 = st.columns(4)
    for col, (ic,val,lb) in zip([c1,c2,c3,c4],[
        ("💬",len(st.session_state.messages),"Xabarlar"),
        ("📁",st.session_state.files_created,"Fayllar"),
        ("⏱",sess_mins,"Daqiqa"),
        ("🔥",level,"Daraja"),
    ]):
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size:28px;'>{ic}</div>
                <div class='metric-num' style='font-size:26px;'>{val}</div>
                <div class='metric-lbl'>{lb}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # API status
    st.markdown("""<h3 style='font-family:Syne,sans-serif;color:#f0f0ff;'>🔗 API Holati</h3>""",
                unsafe_allow_html=True)
    API_INFO = [
        ("cerebras","🧠","Chat • Kod","cloud.cerebras.ai"),
        ("groq",    "⚡","Chat • Kod","groq.com/console"),
        ("gemini",  "✨","Vision • Excel","aistudio.google.com"),
        ("mistral", "💫","Chat • Word","console.mistral.ai"),
        ("cohere",  "🌊","Tahlil • RAG","cohere.com"),
        ("openrouter","🌐","HTML • Zaxira","openrouter.ai"),
    ]
    row_cols = st.columns(3)
    for i, (nm, ic, tasks, link) in enumerate(API_INFO):
        with row_cols[i % 3]:
            ok  = nm in ai_clients
            bg  = "rgba(0,184,148,0.08)" if ok else "rgba(214,48,49,0.06)"
            bdr = "rgba(0,184,148,0.3)"  if ok else "rgba(214,48,49,0.2)"
            er  = api_errors.get(nm,"")
            label = nm.title() if nm!="openrouter" else "OpenRouter"
            st.markdown(f"""
            <div style='background:{bg};border:1px solid {bdr};border-radius:14px;
                        padding:16px;text-align:center;margin-bottom:12px;'>
                <div style='font-size:26px;'>{ic}</div>
                <div style='font-weight:700;font-size:14px;color:#f0f0ff;'>{label}</div>
                <div style='font-size:11px;color:rgba(240,240,255,0.4);'>{tasks}</div>
                <div style='font-size:12px;margin-top:6px;font-weight:600;
                            color:{"#00b894" if ok else "#d63031"};'>
                    {"✅ Ulangan" if ok else "❌ Ulanmagan"}
                </div>
                {f'<div style="font-size:10px;color:#6C5CE7;">{link}</div>' if not ok else ""}
            </div>""", unsafe_allow_html=True)

    if st.button("🔄 API Qayta Ulanish", type="primary", key="prof_reconnect"):
        for k in ['ai_clients','api_errors']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    st.markdown("---")
    # Password change
    st.markdown("""<h3 style='font-family:Syne,sans-serif;color:#f0f0ff;'>🔑 Parol O'zgartirish</h3>""",
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        with st.form("change_pw_form"):
            op  = st.text_input("Eski parol", type="password")
            np_ = st.text_input("Yangi parol (min 6)", type="password")
            cp_ = st.text_input("Tasdiqlash", type="password")
            if st.form_submit_button("🔄 O'zgartirish", type="primary"):
                if len(np_) < 6:
                    st.error("❌ Min 6 belgi!")
                elif np_ != cp_:
                    st.error("❌ Parollar mos emas!")
                elif user_db:
                    try:
                        recs = user_db.get_all_records()
                        idx = next((i for i,r in enumerate(recs)
                                    if str(r['username'])==st.session_state.username
                                    and str(r['password'])==hash_pw(op)), None)
                        if idx is not None:
                            user_db.update_cell(idx+2, 2, hash_pw(np_))
                            st.success("✅ Parol o'zgartirildi!")
                        else:
                            st.error("❌ Eski parol noto'g'ri!")
                    except Exception as e:
                        st.error(f"❌ {e}")
    with c2:
        st.markdown(f"""
        <div class='glass-card'>
            <h4 style='color:#a29bfe;font-family:Syne,sans-serif;margin:0 0 14px;'>📊 Sessiya</h4>
            <p style='color:rgba(240,240,255,0.7);margin:6px 0;'>
                📅 Kirish: <strong>{st.session_state.login_time.strftime('%d.%m.%Y %H:%M') if 'login_time' in st.session_state else 'N/A'}</strong></p>
            <p style='color:rgba(240,240,255,0.7);margin:6px 0;'>
                ⏱ Sessiya: <strong>{sess_mins} daqiqa</strong></p>
            <p style='color:rgba(240,240,255,0.7);margin:6px 0;'>
                💬 Xabarlar: <strong>{len(st.session_state.messages)} ta</strong></p>
            <p style='color:rgba(240,240,255,0.7);margin:6px 0;'>
                📁 Fayllar: <strong>{st.session_state.files_created} ta</strong></p>
            <p style='color:rgba(240,240,255,0.7);margin:6px 0;'>
                🔗 AI Modellar: <strong>{len(ai_clients)}/6 ulangan</strong></p>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════
if st.session_state.page != "chat":
    st.markdown("""
    <div style='text-align:center;padding:50px 20px;margin-top:40px;
                border-top:1px solid rgba(255,255,255,0.06);'>
        <p style='font-family:Syne,sans-serif;font-size:22px;font-weight:700;margin:0 0 10px;
                  background:linear-gradient(135deg,#fff,#a29bfe,#fd79a8);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;'>
            ♾️ Somo AI Ultra Pro Max v5.0
        </p>
        <p style='color:rgba(240,240,255,0.3);font-size:13px;margin:8px 0;'>
            📊 Excel • 📝 Word • 💻 Kod • 🌐 HTML • 📋 CSV • 🎨 Rasm • 🔍 Vision • 🧠 Chat
        </p>
        <p style='color:rgba(240,240,255,0.2);font-size:12px;margin:6px 0;'>
            ⚡ Groq • ✨ Gemini • 🧠 Cerebras • 💫 Mistral • 🌊 Cohere • 🌐 OpenRouter
        </p>
        <p style='color:rgba(240,240,255,0.2);font-size:12px;margin:10px 0 0;'>
            👨‍💻 Yaratuvchi: <strong style='color:#a29bfe;'>Usmonov Sodiq</strong> &nbsp;|&nbsp;
            👨‍💻 Yordamchi: <strong style='color:#a29bfe;'>Davlatov Mironshoh</strong><br>
            © 2026 Somo AI Ultra Pro Max v5.0 — Barcha huquqlar himoyalangan
        </p>
    </div>
    """, unsafe_allow_html=True)
