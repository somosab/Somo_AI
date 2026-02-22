import streamlit as st
import streamlit.components.v1 as components
import gspread
import hashlib
import mammoth
import base64
import time
import json
import io
import csv
import re
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# ════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG
# ════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Somo AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

cookies = EncryptedCookieManager(
    password=st.secrets.get("COOKIE_PASSWORD", "SomoAI_v7_2026_ultra")
)
if not cookies.ready():
    st.stop()

# ════════════════════════════════════════════════════════════════
# 2. GLOBAL CSS — ChatGPT PIXEL-PERFECT
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── FONT ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Fira+Code:wght@400;500&display=swap');

/* ── ROOT VARIABLES (ChatGPT exact palette) ── */
:root {
  --c-bg:           #ffffff;
  --c-sidebar:      #f9f9f9;
  --c-sidebar-item: #ececec;
  --c-hover:        #ececec;
  --c-active:       #e3e3e3;
  --c-border:       #e5e5e5;
  --c-border2:      #d1d1d1;
  --c-input-bg:     #ffffff;
  --c-input-border: #d1d1d1;
  --c-user-bubble:  #f4f4f4;
  --c-text:         #0d0d0d;
  --c-text2:        #444444;
  --c-text3:        #6b6b6b;
  --c-text4:        #adadad;
  --c-green:        #10a37f;
  --c-send:         #0d0d0d;
  --c-send-dis:     #d1d1d1;
  --sb-w:           260px;
  --font:           'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --mono:           'Fira Code', 'Courier New', monospace;
  --r:              12px;
  --r2:             8px;
  --ease:           cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── RESET ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
  background: var(--c-bg) !important;
  color: var(--c-text) !important;
  font-family: var(--font) !important;
  font-size: 15px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header,
[data-testid="stSidebarNav"],
[data-testid="stDecoration"],
[data-testid="stToolbar"],
.st-emotion-cache-1vt458p,
.st-emotion-cache-k77z8z,
.st-emotion-cache-12fmjuu { display: none !important; }

/* ══════════════════════════════════════════
   SIDEBAR — ChatGPT f9f9f9 exact
   ══════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: var(--c-sidebar) !important;
  border-right: 1px solid var(--c-border) !important;
  width: var(--sb-w) !important;
  min-width: var(--sb-w) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 0 !important;
  background: transparent !important;
}
[data-testid="stSidebar"] section { background: transparent !important; }

/* All sidebar buttons */
div[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--c-text2) !important;
  border: none !important;
  border-radius: 6px !important;
  font-family: var(--font) !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  text-align: left !important;
  padding: 8px 12px !important;
  margin: 1px 0 !important;
  width: 100% !important;
  min-height: 36px !important;
  box-shadow: none !important;
  transition: background 0.12s !important;
  justify-content: flex-start !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--c-hover) !important;
  color: var(--c-text) !important;
  box-shadow: none !important;
  transform: none !important;
}
/* Primary button in sidebar (Yangi suhbat + Chiqish) */
div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: var(--c-send) !important;
  color: #ffffff !important;
  font-weight: 500 !important;
  border-radius: 6px !important;
}
div[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
  background: #2a2a2a !important;
}

/* ══════════════════════════════════════════
   MAIN AREA
   ══════════════════════════════════════════ */
.main .block-container {
  max-width: 680px !important;
  margin: 0 auto !important;
  padding: 0 16px 180px !important;
}

/* ══════════════════════════════════════════
   CHAT MESSAGES — ChatGPT layout
   ══════════════════════════════════════════ */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 18px 0 !important;
  margin: 0 !important;
  border-radius: 0 !important;
}

/* Message content text */
[data-testid="stChatMessageContent"] {
  font-family: var(--font) !important;
  font-size: 15px !important;
  line-height: 1.72 !important;
  color: var(--c-text) !important;
}
[data-testid="stChatMessageContent"] p {
  margin-bottom: 10px !important;
  color: var(--c-text) !important;
}
[data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0 !important; }

/* Code inline */
[data-testid="stChatMessageContent"] code {
  background: #f0f0f0 !important;
  color: #c7254e !important;
  font-family: var(--mono) !important;
  font-size: 13px !important;
  padding: 2px 5px !important;
  border-radius: 4px !important;
  border: none !important;
}
/* Code block */
[data-testid="stChatMessageContent"] pre {
  background: #f6f8fa !important;
  border: 1px solid var(--c-border) !important;
  border-radius: var(--r2) !important;
  padding: 14px 16px !important;
  overflow-x: auto !important;
  margin: 12px 0 !important;
  font-size: 13px !important;
}
[data-testid="stChatMessageContent"] pre code {
  background: transparent !important;
  color: #24292e !important;
  padding: 0 !important;
  border-radius: 0 !important;
}
/* Lists in messages */
[data-testid="stChatMessageContent"] ul,
[data-testid="stChatMessageContent"] ol {
  margin: 8px 0 8px 20px !important;
  color: var(--c-text) !important;
}
[data-testid="stChatMessageContent"] li { margin-bottom: 4px !important; }

/* ══════════════════════════════════════════
   CHAT INPUT BAR — ChatGPT oval style
   Oval input, + left, mic+send right
   ══════════════════════════════════════════ */
[data-testid="stChatInput"] {
  position: fixed !important;
  bottom: 0 !important;
  left: var(--sb-w) !important;
  right: 0 !important;
  background: linear-gradient(to top, #ffffff 75%, transparent) !important;
  padding: 14px 24px 22px !important;
  z-index: 999 !important;
  border: none !important;
  box-shadow: none !important;
}
[data-testid="stChatInput"] > div {
  max-width: 680px !important;
  margin: 0 auto !important;
}
[data-testid="stChatInput"] textarea {
  background: var(--c-input-bg) !important;
  color: var(--c-text) !important;
  border: 1px solid var(--c-input-border) !important;
  border-radius: 28px !important;
  font-family: var(--font) !important;
  font-size: 15px !important;
  line-height: 1.5 !important;
  padding: 14px 52px 14px 48px !important;
  resize: none !important;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.05), 0 2px 6px rgba(0,0,0,0.07) !important;
  transition: box-shadow 0.2s !important;
  min-height: 52px !important;
  max-height: 240px !important;
}
[data-testid="stChatInput"] textarea:focus {
  outline: none !important;
  border-color: var(--c-border2) !important;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.08), 0 3px 12px rgba(0,0,0,0.1) !important;
}
[data-testid="stChatInput"] textarea::placeholder {
  color: var(--c-text4) !important;
  font-weight: 300 !important;
}
/* Send button — round black */
[data-testid="stChatInput"] button {
  background: var(--c-send) !important;
  border-radius: 50% !important;
  width: 34px !important;
  height: 34px !important;
  min-height: 34px !important;
  border: none !important;
  color: #ffffff !important;
  box-shadow: none !important;
  transition: background 0.15s, transform 0.1s !important;
}
[data-testid="stChatInput"] button:hover {
  background: #2a2a2a !important;
  transform: scale(1.06) !important;
}
[data-testid="stChatInput"] button:disabled {
  background: var(--c-send-dis) !important;
  transform: none !important;
}

/* ══════════════════════════════════════════
   FORM INPUTS
   ══════════════════════════════════════════ */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
  background: var(--c-bg) !important;
  color: var(--c-text) !important;
  border: 1px solid var(--c-border2) !important;
  border-radius: var(--r2) !important;
  font-family: var(--font) !important;
  font-size: 14px !important;
  padding: 10px 14px !important;
  transition: border-color 0.15s, box-shadow 0.15s !important;
  box-shadow: none !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
  border-color: #aaaaaa !important;
  box-shadow: 0 0 0 2px rgba(0,0,0,0.05) !important;
  outline: none !important;
}
label,
.stTextInput label, .stTextArea label,
.stSelectbox label, .stSlider label,
.stFileUploader label, .stCheckbox label {
  color: var(--c-text2) !important;
  font-family: var(--font) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
}

/* ══════════════════════════════════════════
   SELECTBOX
   ══════════════════════════════════════════ */
.stSelectbox [data-baseweb="select"] > div {
  background: var(--c-bg) !important;
  border: 1px solid var(--c-border2) !important;
  border-radius: var(--r2) !important;
  color: var(--c-text) !important;
  font-family: var(--font) !important;
}
.stSelectbox [data-baseweb="popover"] ul {
  background: var(--c-bg) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: var(--r2) !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12) !important;
}
.stSelectbox [data-baseweb="popover"] li { color: var(--c-text) !important; }
.stSelectbox [data-baseweb="popover"] li:hover { background: var(--c-hover) !important; }

/* ══════════════════════════════════════════
   BUTTONS (main area)
   ══════════════════════════════════════════ */
.stButton > button {
  background: var(--c-bg) !important;
  color: var(--c-text) !important;
  border: 1px solid var(--c-border2) !important;
  border-radius: var(--r2) !important;
  font-family: var(--font) !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding: 8px 16px !important;
  box-shadow: none !important;
  transition: background 0.12s !important;
  cursor: pointer !important;
}
.stButton > button:hover {
  background: var(--c-hover) !important;
  border-color: #bbbbbb !important;
  box-shadow: none !important;
  transform: none !important;
}
.stButton > button[kind="primary"] {
  background: var(--c-send) !important;
  color: #ffffff !important;
  border-color: var(--c-send) !important;
}
.stButton > button[kind="primary"]:hover {
  background: #2a2a2a !important;
}

/* ══════════════════════════════════════════
   DOWNLOAD BUTTONS
   ══════════════════════════════════════════ */
.stDownloadButton > button {
  background: transparent !important;
  color: var(--c-green) !important;
  border: 1px solid rgba(16,163,127,0.35) !important;
  border-radius: var(--r2) !important;
  font-family: var(--font) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 7px 14px !important;
  box-shadow: none !important;
  transition: background 0.12s !important;
}
.stDownloadButton > button:hover {
  background: rgba(16,163,127,0.08) !important;
  box-shadow: none !important;
  transform: none !important;
}

/* ══════════════════════════════════════════
   FORM SUBMIT
   ══════════════════════════════════════════ */
[data-testid="stFormSubmitButton"] > button {
  background: var(--c-send) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: var(--r2) !important;
  font-family: var(--font) !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  padding: 11px 20px !important;
  width: 100% !important;
  box-shadow: none !important;
  transition: background 0.12s !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
  background: #2a2a2a !important;
  box-shadow: none !important;
  transform: none !important;
}

/* ══════════════════════════════════════════
   EXPANDER
   ══════════════════════════════════════════ */
.stExpander {
  background: #fafafa !important;
  border: 1px solid var(--c-border) !important;
  border-radius: var(--r) !important;
  margin-bottom: 6px !important;
  box-shadow: none !important;
}
.stExpander summary {
  color: var(--c-text2) !important;
  font-family: var(--font) !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  padding: 10px 14px !important;
}
.stExpander summary:hover { color: var(--c-text) !important; }
[data-testid="stExpanderDetails"] {
  background: #fafafa !important;
  padding: 10px 14px 14px !important;
}

/* ══════════════════════════════════════════
   TABS
   ══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--c-border) !important;
  gap: 0 !important; padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--c-text3) !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  font-family: var(--font) !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  padding: 10px 16px !important;
  box-shadow: none !important;
  margin: 0 !important;
  transition: color 0.12s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--c-text) !important; }
.stTabs [aria-selected="true"] {
  color: var(--c-text) !important;
  border-bottom-color: var(--c-text) !important;
  font-weight: 500 !important;
}

/* ══════════════════════════════════════════
   FILE UPLOADER
   ══════════════════════════════════════════ */
[data-testid="stFileUploader"] {
  background: #fafafa !important;
  border: 1.5px dashed var(--c-border2) !important;
  border-radius: var(--r) !important;
  padding: 16px !important;
  transition: border-color 0.15s !important;
}
[data-testid="stFileUploader"]:hover { border-color: #aaa !important; }

/* ══════════════════════════════════════════
   ALERTS
   ══════════════════════════════════════════ */
.stSuccess {
  background: #f0fdf4 !important;
  border-left: 3px solid #22c55e !important;
  color: #15803d !important;
  border-radius: var(--r2) !important;
}
.stError {
  background: #fef2f2 !important;
  border-left: 3px solid #ef4444 !important;
  color: #b91c1c !important;
  border-radius: var(--r2) !important;
}
.stWarning {
  background: #fffbeb !important;
  border-left: 3px solid #f59e0b !important;
  color: #b45309 !important;
  border-radius: var(--r2) !important;
}
.stInfo {
  background: #eff6ff !important;
  border-left: 3px solid #3b82f6 !important;
  color: #1d4ed8 !important;
  border-radius: var(--r2) !important;
}

/* ══════════════════════════════════════════
   MISC
   ══════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #dddddd; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #bbbbbb; }
.stSpinner > div { border-top-color: var(--c-text3) !important; }
hr { border: none !important; border-top: 1px solid var(--c-border) !important; margin: 10px 0 !important; }
[data-testid="stMetricValue"] { color: var(--c-text) !important; font-weight: 600 !important; font-size: 20px !important; }
[data-testid="stMetricLabel"] { color: var(--c-text3) !important; font-size: 11px !important; }
audio { border-radius: var(--r2); width: 100%; margin-top: 6px; }

/* ══════════════════════════════════════════
   CUSTOM COMPONENTS
   ══════════════════════════════════════════ */

/* ─ Sidebar header ─ */
.sb-top {
  padding: 12px 10px 6px;
  display: flex; align-items: center; justify-content: space-between;
}
.sb-logo {
  font-size: 14px; font-weight: 600;
  color: var(--c-text); display: flex; align-items: center; gap: 6px;
  letter-spacing: -.2px;
}
.sb-logo-dot { color: var(--c-green); }

/* ─ Sidebar chat history item ─ */
.sb-chat-item {
  display: block; padding: 8px 12px; font-size: 13px;
  color: var(--c-text2); border-radius: 6px; cursor: pointer;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  transition: background 0.12s;
}
.sb-chat-item:hover { background: var(--c-hover); color: var(--c-text); }
.sb-chat-item.active { background: var(--c-active); color: var(--c-text); }

/* ─ Sidebar section label ─ */
.sb-sec {
  font-size: 11px; font-weight: 600; letter-spacing: 0.6px;
  text-transform: uppercase; color: var(--c-text4);
  padding: 12px 14px 4px;
}
/* ─ Divider ─ */
.sb-div { height: 1px; background: var(--c-border); margin: 6px 8px; }

/* ─ Sidebar user ─ */
.sb-user {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 12px 14px;
}
.sb-av {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--c-green);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.sb-name { font-size: 13px; font-weight: 500; color: var(--c-text); }
.sb-plan { font-size: 11px; color: var(--c-text4); }

/* ─ Mini stat box ─ */
.sb-stat {
  background: var(--c-hover); border-radius: 6px;
  padding: 8px 10px; text-align: center;
}
.sb-stat-v { font-size: 18px; font-weight: 600; color: var(--c-text); }
.sb-stat-l { font-size: 10px; color: var(--c-text4); margin-top: 1px; }

/* ─ API pill ─ */
.xp {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 8px; border-radius: 20px;
  font-size: 11px; font-weight: 500; margin: 2px;
}
.xp-g  { background: #fff4ec; color: #c2410c; border: 1px solid #fdd6a5; }
.xp-gm { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }

/* ─ File chip ─ */
.xfc {
  display: inline-flex; align-items: center; gap: 5px;
  background: #f4f4f4; border: 1px solid var(--c-border2);
  border-radius: 20px; padding: 3px 10px;
  font-size: 12px; color: var(--c-text2); margin: 2px;
}

/* ─ Download card ─ */
.xdl {
  background: #fafafa; border: 1px solid var(--c-border);
  border-left: 3px solid var(--c-green);
  border-radius: var(--r2); padding: 12px 14px; margin: 8px 0;
}
.xdl-t { font-size: 12px; font-weight: 600; color: var(--c-green); margin-bottom: 8px; }

/* ─ HOME SCREEN — ChatGPT center layout ─ */
.home-center {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 60px 0 20px;
}
.home-title {
  font-size: 30px; font-weight: 600; color: var(--c-text);
  letter-spacing: -0.5px; text-align: center; margin-bottom: 28px;
}
/* 2x2 suggestion grid */
.sg-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 8px; width: 100%; margin: 0 0 16px;
}
.sg-card {
  background: var(--c-bg); border: 1px solid var(--c-border);
  border-radius: var(--r); padding: 14px 16px; cursor: pointer;
  transition: background 0.12s, border-color 0.12s; text-align: left;
}
.sg-card:hover { background: #f7f7f7; border-color: #c0c0c0; }
.sg-title { font-size: 13px; font-weight: 500; color: var(--c-text); margin-bottom: 2px; }
.sg-desc  { font-size: 12px; color: var(--c-text3); line-height: 1.4; }

/* ─ LOGIN ─ */
.login-wrap { max-width: 350px; margin: 64px auto; padding: 0 16px; }
.login-logo { font-size: 22px; font-weight: 600; color: var(--c-text); text-align: center; margin-bottom: 4px; }
.login-sub  { font-size: 14px; color: var(--c-text3); text-align: center; margin-bottom: 22px; }
.login-box  {
  background: var(--c-bg); border: 1px solid var(--c-border);
  border-radius: 14px; padding: 28px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05), 0 4px 20px rgba(0,0,0,0.07);
}

/* ─ Template card ─ */
.tpl-card {
  background: #fafafa; border: 1px solid var(--c-border);
  border-radius: var(--r); padding: 16px; margin-bottom: 8px;
}

/* ─ Page header ─ */
.pg-h { font-size: 26px; font-weight: 600; color: var(--c-text); text-align: center; padding: 36px 0 6px; letter-spacing: -0.4px; }
.pg-s { font-size: 14px; color: var(--c-text3); text-align: center; margin-bottom: 24px; }

/* ─ Footer ─ */
.foot {
  text-align: center; color: var(--c-text4); font-size: 12px;
  padding: 20px 0 10px; border-top: 1px solid var(--c-border);
  margin-top: 36px; line-height: 2;
}

/* ─ Paste notify toast ─ */
#somo-toast {
  position: fixed; bottom: 86px; left: 50%;
  transform: translateX(-50%) translateY(6px);
  background: #0d0d0d; color: #fff;
  padding: 8px 18px; border-radius: 20px;
  font-size: 13px; font-family: Inter, sans-serif;
  z-index: 9999; opacity: 0;
  transition: opacity 0.22s, transform 0.22s;
  pointer-events: none; white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}
#somo-toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }

/* ─ Mobile ─ */
@media (max-width: 768px) {
  :root { --sb-w: 0px; }
  .main .block-container { padding: 0 12px 160px !important; }
  [data-testid="stChatInput"] { left: 0 !important; padding: 10px 12px 16px !important; }
  .sg-grid { grid-template-columns: 1fr !important; }
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# 3. PASTE / DRAG-DROP JS HANDLER
# ════════════════════════════════════════════════════════════════
def paste_js():
    components.html("""
<div id="somo-toast">📋 Rasm clipboard'dan qo'shildi!</div>
<script>
(function(){
  function toast(msg){
    var el=document.getElementById('somo-toast');
    if(!el) return;
    el.textContent=msg;
    el.classList.add('show');
    setTimeout(function(){ el.classList.remove('show'); }, 2400);
  }
  // Paste (Ctrl+V)
  document.addEventListener('paste', function(e){
    var items=(e.clipboardData||window.clipboardData||{}).items;
    if(!items) return;
    for(var i=0;i<items.length;i++){
      if(items[i].type.indexOf('image')!==-1){
        var f=items[i].getAsFile();
        if(!f) continue;
        var r=new FileReader();
        r.onload=function(ev){
          sessionStorage.setItem('somo_paste_img', ev.target.result);
          sessionStorage.setItem('somo_paste_name','clipboard_'+Date.now()+'.png');
          toast('📋 Rasm clipboard\'dan qo\'shildi — fayl yuklang yoki Enter bosing!');
        };
        r.readAsDataURL(f);
        e.preventDefault();
        break;
      }
    }
  }, false);
  // Drag & Drop
  document.addEventListener('dragover', function(e){ e.preventDefault(); });
  document.addEventListener('drop', function(e){
    e.preventDefault();
    var files=e.dataTransfer.files;
    if(!files.length) return;
    var f=files[0];
    if(f.type.startsWith('image/')){
      var r=new FileReader();
      r.onload=function(ev){
        sessionStorage.setItem('somo_paste_img', ev.target.result);
        sessionStorage.setItem('somo_paste_name', f.name);
        toast('🖼 '+f.name+' qo\'shildi!');
      };
      r.readAsDataURL(f);
    }
  }, false);
})();
</script>
""", height=0)

# ════════════════════════════════════════════════════════════════
# 4. DB + AI CONNECTIONS
# ════════════════════════════════════════════════════════════════
@st.cache_resource
def get_db():
    try:
        sc=["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
        cr=ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], sc)
        gc=gspread.authorize(cr)
        ss=gc.open("Somo_Users")
        u=ss.sheet1
        ch=ss.worksheet("ChatHistory")
        try:   fb=ss.worksheet("Letters")
        except:
            fb=ss.add_worksheet("Letters",1000,10)
            fb.append_row(["Timestamp","Username","Rating","Category","Message","Email","Status"])
        return u,ch,fb
    except Exception as e:
        st.error(f"❌ DB: {e}"); return None,None,None

@st.cache_resource
def get_groq():
    try:    return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except: return None

@st.cache_resource
def get_gemini():
    try:
        import google.generativeai as genai
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel("gemini-2.0-flash")
    except: return None

user_db, chat_db, fb_db = get_db()
groq_cl   = get_groq()
gemini_md = get_gemini()

# ════════════════════════════════════════════════════════════════
# 5. UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════════
def ficon(name):
    e = name.lower().rsplit(".",1)[-1] if "." in name else ""
    return {"pdf":"📄","docx":"📝","doc":"📝","txt":"📃","csv":"📊","xlsx":"📊","xls":"📊",
            "json":"🔧","py":"🐍","js":"🟨","html":"🌐","css":"🎨","ts":"🔷","jsx":"⚛️",
            "tsx":"⚛️","java":"☕","cpp":"⚙️","c":"⚙️","go":"🐹","rs":"🦀","rb":"💎",
            "php":"🐘","swift":"🍎","kt":"📱","sql":"🗃","md":"📋","sh":"💻","svg":"🎨",
            "yaml":"🔧","xml":"🔧","png":"🖼","jpg":"🖼","jpeg":"🖼","webp":"🖼",
            "gif":"🎞","mp3":"🎵","wav":"🎵","m4a":"🎵"}.get(e,"📎")

def is_img(f):  return getattr(f,"type","") in ["image/jpeg","image/jpg","image/png","image/webp","image/gif"]
def is_pdf(f):  return getattr(f,"type","") == "application/pdf"
def is_docx(f): return "wordprocessingml" in getattr(f,"type","") or getattr(f,"name","").endswith((".docx",".doc"))

def img_mime(f):
    return {"image/jpeg":"image/jpeg","image/jpg":"image/jpeg","image/png":"image/png",
            "image/webp":"image/webp","image/gif":"image/gif"}.get(getattr(f,"type",""),"image/png")

def read_text(fb, name, mime=""):
    n=name.lower()
    try:
        if n.endswith(".csv") or mime=="text/csv":    return "CSV:\n"+fb.decode("utf-8","ignore")[:5000]
        if n.endswith(".json"):                        return "JSON:\n"+fb.decode("utf-8","ignore")[:5000]
        if n.endswith((".xlsx",".xls")):               return f"Excel fayl: {name}"
        if any(n.endswith(x) for x in [
            ".py",".js",".ts",".jsx",".tsx",".html",".css",".md",".txt",
            ".java",".cpp",".c",".go",".rs",".sh",".yaml",".xml",".sql",
            ".kt",".rb",".php",".swift",".r",".toml",".env",".gitignore"]):
            return fb.decode("utf-8","ignore")
    except: pass
    return ""

def cblocks(text):
    return re.findall(r"```(\w*)\n?(.*?)```", text, re.DOTALL)

# ════════════════════════════════════════════════════════════════
# 6. GEMINI READERS
# ════════════════════════════════════════════════════════════════
def gem_img(prompt, b64, mime="image/png"):
    if not gemini_md: return None
    try:
        raw=base64.b64decode(b64.split(",",1)[1] if "," in b64 else b64)
        return gemini_md.generate_content([prompt,{"mime_type":mime,"data":raw}]).text
    except: return None

def gem_pdf(prompt, fb):
    if not gemini_md: return None
    try:    return gemini_md.generate_content([prompt,{"mime_type":"application/pdf","data":fb}]).text
    except: return None

def gem_docx(prompt, fb):
    if not gemini_md: return None
    try:
        t=mammoth.extract_raw_text(io.BytesIO(fb)).value
        if t.strip():
            return gemini_md.generate_content([f"{prompt}\n\nHujjat:\n{t[:10000]}"]).text
    except: pass
    return None

# ════════════════════════════════════════════════════════════════
# 7. GROQ FUNCTIONS
# ════════════════════════════════════════════════════════════════
def groq_ask(msgs, mdl, temp=0.6, tok=4096):
    if not groq_cl: return "❌ Groq mavjud emas."
    try:
        r=groq_cl.chat.completions.create(messages=msgs,model=mdl,temperature=temp,max_tokens=tok)
        return r.choices[0].message.content
    except Exception as e: return f"❌ Groq: {e}"

def groq_stt(ab, fname="audio.wav"):
    if not groq_cl: return None
    try:
        t=groq_cl.audio.transcriptions.create(file=(fname,ab),model="whisper-large-v3")
        return t.text
    except: return None

# ════════════════════════════════════════════════════════════════
# 8. FILE CREATION ENGINE
# ════════════════════════════════════════════════════════════════
def mk_excel(text):
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        wb=openpyxl.Workbook(); ws=wb.active; ws.title="Somo AI"
        cm=re.search(r"```csv\n?(.*?)```",text,re.DOTALL)
        tm=re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+\n((\|.+\|\n?)+)",text)
        rows=[]
        if cm:   rows=list(csv.reader(io.StringIO(cm.group(1).strip())))
        elif tm:
            for l in tm.group(0).strip().split("\n"):
                if "---" not in l:
                    c=[x.strip() for x in l.strip("|").split("|")]
                    if any(c): rows.append(c)
        if not rows: return None
        hf=PatternFill("solid",fgColor="0D0D0D")
        hfnt=Font(bold=True,color="FFFFFF",size=11,name="Calibri")
        af=PatternFill("solid",fgColor="F9F9F9")
        bs=Side(style="thin",color="E5E5E5")
        brd=Border(left=bs,right=bs,top=bs,bottom=bs)
        al=Alignment(horizontal="center",vertical="center",wrap_text=True)
        for ri,row in enumerate(rows,1):
            for ci,val in enumerate(row,1):
                cell=ws.cell(ri,ci,val); cell.border=brd; cell.alignment=al
                if ri==1: cell.fill=hf; cell.font=hfnt
                elif ri%2==0: cell.fill=af; cell.font=Font(size=11,name="Calibri")
                else: cell.font=Font(size=11,name="Calibri")
        for col in ws.columns:
            ml=max((len(str(c.value or "")) for c in col),default=10)
            ws.column_dimensions[col[0].column_letter].width=min(ml+4,45)
        for row in ws.iter_rows(): ws.row_dimensions[row[0].row].height=22
        buf=io.BytesIO(); wb.save(buf); buf.seek(0); return buf.read()
    except: return None

def mk_pptx(text):
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN
        prs=Presentation(); prs.slide_width=Inches(13.33); prs.slide_height=Inches(7.5)
        W=RGBColor(0xFF,0xFF,0xFF); B=RGBColor(0x0D,0x0D,0x0D)
        G=RGBColor(0xF9,0xF9,0xF9); A=RGBColor(0x10,0xA3,0x7F)
        CL=[A,RGBColor(0x63,0x66,0xF1),RGBColor(0xF5,0x9E,0x0B),RGBColor(0xEC,0x48,0x99),RGBColor(0x06,0xB6,0xD4)]
        def R(sl,l,t,w,h,c):
            s=sl.shapes.add_shape(1,Inches(l),Inches(t),Inches(w),Inches(h))
            s.fill.solid(); s.fill.fore_color.rgb=c; s.line.fill.background(); return s
        def T(sl,txt,l,t,w,h,sz=20,bold=False,c=None,al=PP_ALIGN.LEFT,it=False):
            b=sl.shapes.add_textbox(Inches(l),Inches(t),Inches(w),Inches(h))
            f=b.text_frame; f.word_wrap=True; p=f.paragraphs[0]; p.alignment=al
            r=p.add_run(); r.text=txt; r.font.size=Pt(sz); r.font.bold=bold; r.font.italic=it
            r.font.color.rgb=c or B; return b
        lines=text.strip().split("\n"); slides=[]; cur={"title":"","bullets":[]}
        for ln in lines:
            ln=ln.strip()
            if not ln: continue
            if re.match(r"^#{1,3}\s+",ln):
                if cur["title"] or cur["bullets"]: slides.append(cur)
                cur={"title":re.sub(r"^#{1,3}\s+","",ln).strip(),"bullets":[]}
            elif re.match(r"^(\d+\.|[-*•►▸])\s+",ln):
                cur["bullets"].append(re.sub(r"^(\d+\.|[-*•►▸])\s+","",ln).strip())
            elif re.match(r"^\*\*(.+)\*\*$",ln):
                if cur["title"] or cur["bullets"]: slides.append(cur)
                cur={"title":re.sub(r"\*\*","",ln).strip(),"bullets":[]}
            elif not ln.startswith("```"): cur["bullets"].append(ln)
        if cur["title"] or cur["bullets"]: slides.append(cur)
        if len(slides)<2:
            chunks=[l.strip() for l in lines if l.strip() and not l.startswith("```")]
            slides=[{"title":chunks[0] if chunks else "Somo AI","bullets":chunks[1:3]}]
            for i in range(3,len(chunks),4):
                slides.append({"title":f"Qism {(i-3)//4+1}","bullets":chunks[i:i+4]})
        blank=prs.slide_layouts[6]
        # Title slide
        sl=prs.slides.add_slide(blank)
        R(sl,0,0,13.33,7.5,B); R(sl,0,0,.07,7.5,A)
        R(sl,0,5.85,13.33,1.65,RGBColor(0x1A,0x1A,0x1A))
        T(sl,slides[0]["title"] or "Somo AI",.5,1.7,12.3,2.5,sz=44,bold=True,c=W)
        sub=slides[0]["bullets"][0] if slides[0]["bullets"] else "Somo AI"
        T(sl,sub,.5,4.2,11.0,1.1,sz=22,c=RGBColor(0x9C,0xA3,0xAF),it=True)
        T(sl,"✦ Somo AI  ·  "+datetime.now().strftime("%Y"),.5,6.15,8.0,.55,sz=11,c=RGBColor(0x6B,0x72,0x80))
        # Content slides
        for idx,sd in enumerate(slides[1:],1):
            sl=prs.slides.add_slide(blank)
            ac=CL[idx%len(CL)]
            R(sl,0,0,13.33,7.5,G); R(sl,0,0,.07,7.5,ac)
            R(sl,.07,0,13.26,1.44,W); R(sl,.07,1.37,13.26,.05,ac)
            R(sl,11.95,.18,1.1,1.1,ac)
            T(sl,str(idx),12.0,.22,1.0,1.0,sz=28,bold=True,c=W,al=PP_ALIGN.CENTER)
            T(sl,sd["title"] or f"Slayd {idx}",.3,.18,11.5,1.1,sz=33,bold=True,c=B)
            buls=sd["bullets"][:7]
            if buls:
                y0=1.62; yst=min(.76,5.4/max(len(buls),1)); bh=yst*.88
                for bi,bul in enumerate(buls):
                    R(sl,.28,y0+bi*yst+.18,.08,.3,ac)
                    cl=re.sub(r"^\*\*(.+)\*\*",r"\1",bul)
                    ib=bul.startswith("**") and bul.endswith("**")
                    T(sl,cl,.5,y0+bi*yst,12.5,bh,sz=19,bold=ib,c=B)
            R(sl,0,7.2,13.33,.3,W)
            T(sl,"✦ Somo AI",.3,7.22,4.0,.25,sz=10,c=RGBColor(0x9C,0xA3,0xAF))
            T(sl,f"{idx}/{len(slides)-1}",12.0,7.22,1.0,.25,sz=10,c=RGBColor(0x9C,0xA3,0xAF),al=PP_ALIGN.RIGHT)
        # End slide
        sl=prs.slides.add_slide(blank)
        R(sl,0,0,13.33,7.5,B); R(sl,0,3.1,13.33,.06,A); R(sl,0,4.34,13.33,.06,A)
        T(sl,"✅ Taqdimot yakunlandi",.5,3.2,12.3,1.1,sz=40,bold=True,c=W,al=PP_ALIGN.CENTER)
        T(sl,"✦ Somo AI  ·  Groq + Gemini",.5,4.9,12.3,.7,sz=15,c=RGBColor(0x6B,0x72,0x80),al=PP_ALIGN.CENTER)
        buf=io.BytesIO(); prs.save(buf); buf.seek(0); return buf.read()
    except: return None

def mk_word(text):
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches
        doc=Document()
        for s in doc.sections:
            s.top_margin=s.bottom_margin=Inches(1)
            s.left_margin=s.right_margin=Inches(1.25)
        lines=text.strip().split("\n"); in_c=False; cbuf=[]
        for line in lines:
            s=line.strip()
            if s.startswith("```"):
                if not in_c: in_c=True; cbuf=[]
                else:
                    in_c=False; p=doc.add_paragraph()
                    p.paragraph_format.left_indent=Inches(.3)
                    r=p.add_run("\n".join(cbuf))
                    r.font.name="Courier New"; r.font.size=Pt(10)
                    r.font.color.rgb=RGBColor(0x10,0xA3,0x7F)
                continue
            if in_c: cbuf.append(line); continue
            if not s: doc.add_paragraph(); continue
            if   re.match(r"^# ",s):
                h=doc.add_heading(s[2:],1)
                if h.runs: h.runs[0].font.color.rgb=RGBColor(0x10,0xA3,0x7F)
            elif re.match(r"^## ",s):
                h=doc.add_heading(s[3:],2)
                if h.runs: h.runs[0].font.color.rgb=RGBColor(0x63,0x66,0xF1)
            elif re.match(r"^### ",s): doc.add_heading(s[4:],3)
            elif re.match(r"^[-*•►▸]\s+",s):
                p=doc.add_paragraph(style="List Bullet"); _fr(p,re.sub(r"^[-*•►▸]\s+","",s))
            elif re.match(r"^\d+\.\s+",s):
                p=doc.add_paragraph(style="List Number"); _fr(p,re.sub(r"^\d+\.\s+","",s))
            else: p=doc.add_paragraph(); _fr(p,s)
        buf=io.BytesIO(); doc.save(buf); buf.seek(0); return buf.read()
    except: return None

def _fr(p, text):
    from docx.shared import RGBColor
    for part in re.split(r"(\*\*.*?\*\*|\*.*?\*)",text):
        if part.startswith("**") and part.endswith("**"): r=p.add_run(part[2:-2]); r.bold=True
        elif part.startswith("*") and part.endswith("*"): r=p.add_run(part[1:-1]); r.italic=True
        else: p.add_run(part)

# ════════════════════════════════════════════════════════════════
# 9. SMART DOWNLOAD — only when EXPLICITLY requested
# ════════════════════════════════════════════════════════════════
def offer_dl(ai_text, user_msg, ts):
    ts_s=ts.replace(":","_").replace(" ","_")
    blks=cblocks(ai_text)
    up=user_msg.lower()

    # Keywords that MUST appear in USER message
    PK=["taqdimot","slayd","slide","presentation","pptx","powerpoint","prezentatsiya"]
    XK=["jadval","excel","xlsx","csv","statistika","ro'yxat","hisobot","список","таблица"]
    DK=["rezyume","resume","cv","hujjat","word","docx","xat","shartnoma","insho","referat","maqola","blog"]

    has_h=len(re.findall(r"^#{1,3}\s+",ai_text,re.MULTILINE))>=3
    has_t=bool(re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+",ai_text))
    has_c="```csv" in ai_text

    wp=any(k in up for k in PK)
    wx=any(k in up for k in XK) or (has_t and any(k in up for k in XK+["yarat","ko'rsat","ber"])) or has_c
    wd=any(k in up for k in DK) and not wp

    if wp:
        d=mk_pptx(ai_text)
        if d:
            st.markdown('<div class="xdl"><div class="xdl-t">📊 PowerPoint tayyor</div></div>',unsafe_allow_html=True)
            st.download_button("⬇️ PPTX yuklab olish",d,f"somo_{ts_s}.pptx",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                key=f"pp_{ts_s}",use_container_width=True)

    if wx:
        d=mk_excel(ai_text)
        if d:
            st.markdown('<div class="xdl"><div class="xdl-t">📊 Excel tayyor</div></div>',unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1: st.download_button("⬇️ Excel (.xlsx)",d,f"somo_{ts_s}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"xl_{ts_s}",use_container_width=True)
            rows=[]
            cm=re.search(r"```csv\n?(.*?)```",ai_text,re.DOTALL)
            tm=re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+\n((\|.+\|\n?)+)",ai_text)
            if cm: rows=list(csv.reader(io.StringIO(cm.group(1).strip())))
            elif tm:
                for l in tm.group(0).strip().split("\n"):
                    if "---" not in l:
                        c=[x.strip() for x in l.strip("|").split("|")]
                        if any(c): rows.append(c)
            if rows:
                cb=io.StringIO(); csv.writer(cb).writerows(rows)
                with c2: st.download_button("⬇️ CSV",cb.getvalue().encode(),f"somo_{ts_s}.csv","text/csv",
                    key=f"cv_{ts_s}",use_container_width=True)

    if wd:
        d=mk_word(ai_text)
        if d:
            st.markdown('<div class="xdl"><div class="xdl-t">📝 Word tayyor</div></div>',unsafe_allow_html=True)
            st.download_button("⬇️ Word (.docx)",d,f"somo_{ts_s}.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"wd_{ts_s}",use_container_width=True)

    # SVG
    for i,(_,svg) in enumerate([(l,c) for l,c in blks if l.lower()=="svg" or c.strip().startswith("<svg")]):
        st.markdown('<div class="xdl"><div class="xdl-t">🎨 SVG Rasm</div></div>',unsafe_allow_html=True)
        st.markdown(svg.strip(),unsafe_allow_html=True)
        st.download_button(f"⬇️ rasm_{i}.svg",svg.strip().encode(),f"somo_{ts_s}_{i}.svg","image/svg+xml",
            key=f"sv_{ts_s}_{i}",use_container_width=True)

    # HTML
    for i,(_,code) in enumerate([(l,c) for l,c in blks if l.lower()=="html"]):
        st.markdown('<div class="xdl"><div class="xdl-t">🌐 HTML Sahifa</div></div>',unsafe_allow_html=True)
        with st.expander("👁 Ko'rish",expanded=True):
            components.html(code.strip(),height=400,scrolling=True)
        st.download_button(f"⬇️ sahifa_{i}.html",code.strip().encode(),f"somo_{ts_s}_{i}.html","text/html",
            key=f"ht_{ts_s}_{i}",use_container_width=True)

    # Code files
    EXT={"python":"py","py":"py","javascript":"js","js":"js","typescript":"ts","ts":"ts",
         "css":"css","json":"json","sql":"sql","bash":"sh","shell":"sh","sh":"sh",
         "yaml":"yaml","xml":"xml","markdown":"md","md":"md","jsx":"jsx","tsx":"tsx",
         "java":"java","cpp":"cpp","c":"c","rust":"rs","go":"go","php":"php",
         "ruby":"rb","swift":"swift","kotlin":"kt","r":"r","txt":"txt"}
    others=[(l,c) for l,c in blks if l.lower() not in {"html","svg","csv",""}]
    if others:
        st.markdown('<div class="xdl"><div class="xdl-t">💾 Kod Fayllar</div></div>',unsafe_allow_html=True)
        cols=st.columns(min(len(others),3))
        for i,(lang,code) in enumerate(others):
            ext=EXT.get(lang.strip().lower(),"txt"); fname=f"somo_{ts_s}_{i}.{ext}"
            with cols[i%len(cols)]:
                st.download_button(f"{ficon(fname)} .{ext}",code.strip().encode(),fname,"text/plain",
                    key=f"cd_{ts_s}_{i}",use_container_width=True)

# ════════════════════════════════════════════════════════════════
# 10. TEMPLATES
# ════════════════════════════════════════════════════════════════
TMPLS={
    "💼 Biznes":[
        {"icon":"📊","title":"Biznes Reja","prompt":"[Kompaniya] uchun professional biznes reja:\n- Ijroiya xulosasi\n- Bozor tahlili\n- Marketing strategiyasi\n- Moliyaviy reja\n- 5 yillik prognoz"},
        {"icon":"📈","title":"Marketing Reja","prompt":"[Mahsulot] uchun digital marketing reja:\n- Target auditoriya\n- SMM\n- SEO\n- Byudjet\n- KPI"},
        {"icon":"📋","title":"SWOT Tahlil","prompt":"[Kompaniya] uchun batafsil SWOT tahlil jadvali yarat"},
        {"icon":"💼","title":"Taklifnoma","prompt":"[Mijoz] uchun professional taklifnoma:\n- Muammo\n- Yechim\n- Narxlar\n- Garantiya"},
    ],
    "💻 Dasturlash":[
        {"icon":"🐍","title":"Python","prompt":"Python'da [funksiya] kodi:\n- Type hints\n- Docstring\n- Error handling\n- Test"},
        {"icon":"🌐","title":"HTML Sahifa","prompt":"[Sahifa] uchun zamonaviy HTML/CSS/JS:\n- Responsive design\n- Animatsiyalar"},
        {"icon":"🗃","title":"SQL","prompt":"[Jadval] uchun SQL so'rovlar: SELECT, JOIN, GROUP BY, Indexes"},
        {"icon":"🔌","title":"API","prompt":"[Til]da [API] integratsiya: Auth, CRUD, Error handling, Docs"},
    ],
    "📚 Ta'lim":[
        {"icon":"📖","title":"Dars Rejasi","prompt":"[Mavzu] dars rejasi:\n- Maqsadlar\n- Kirish 10 daqiqa\n- Asosiy qism 30 daqiqa\n- Amaliy 15 daqiqa\n- Vazifa"},
        {"icon":"📝","title":"Test Savollar","prompt":"[Mavzu] bo'yicha 20 ta test: 4 variant, to'g'ri javob, qiyinlik darajasi"},
        {"icon":"🎯","title":"O'quv Dastur","prompt":"[Soha] 3 oylik o'quv dasturi: haftalik jadval, resurslar, baholash"},
    ],
    "✍️ Kontent":[
        {"icon":"📄","title":"Rezyume","prompt":"[Kasb] uchun professional CV:\n- Kasbiy maqsad\n- Tajriba\n- Ta'lim\n- Ko'nikmalar"},
        {"icon":"✉️","title":"Motivatsion Xat","prompt":"[Kompaniya] ga [Lavozim] uchun motivatsion xat yoz"},
        {"icon":"📰","title":"Blog Post","prompt":"[Mavzu] haqida blog post: sarlavha, kirish, asosiy qismlar, xulosa"},
        {"icon":"📣","title":"Ijtimoiy Tarmoq","prompt":"[Mahsulot] uchun Instagram, Telegram, LinkedIn postlari"},
    ],
}

# ════════════════════════════════════════════════════════════════
# 11. SESSION MANAGEMENT
# ════════════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    su=cookies.get("ss7")
    if su and user_db:
        try:
            recs=user_db.get_all_records()
            ud=next((r for r in recs if str(r.get("username",""))==su),None)
            if ud and str(ud.get("status","")).lower()=="active":
                st.session_state.update({"username":su,"logged_in":True,"login_time":datetime.now()})
            else: st.session_state.logged_in=False
        except: st.session_state.logged_in=False
    else: st.session_state.logged_in=False

def do_logout():
    try: cookies["ss7"]=""; cookies.save()
    except: pass
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.session_state.logged_in=False; st.rerun()

# ════════════════════════════════════════════════════════════════
# 12. LOGIN PAGE
# ════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    paste_js()
    st.markdown("""
    <div class="login-wrap">
        <div class="login-logo">✦ Somo AI</div>
        <div class="login-sub">Groq · Gemini · Whisper</div>
    </div>
    """, unsafe_allow_html=True)

    g_ok=groq_cl is not None; gm_ok=gemini_md is not None
    st.markdown(f"""
    <div style="display:flex;gap:8px;justify-content:center;margin-bottom:18px;flex-wrap:wrap;">
        <span class="xp xp-g">{'✅' if g_ok else '❌'} Groq Chat · Whisper</span>
        <span class="xp xp-gm">{'✅' if gm_ok else '❌'} Gemini Vision · PDF</span>
    </div>
    """, unsafe_allow_html=True)

    _,col,_=st.columns([1,1.1,1])
    with col:
        st.markdown('<div class="login-box">',unsafe_allow_html=True)
        t1,t2,t3=st.tabs(["Kirish","Ro'yxat","Haqida"])
        with t1:
            with st.form("lf"):
                u=st.text_input("",placeholder="Username",key="lu",label_visibility="collapsed")
                p=st.text_input("",type="password",placeholder="Parol",key="lp",label_visibility="collapsed")
                c1,c2=st.columns([3,1])
                with c1: sub=st.form_submit_button("Kirish",use_container_width=True)
                with c2: rem=st.checkbox("Eslab",value=True)
                if sub and u and p and user_db:
                    try:
                        recs=user_db.get_all_records()
                        hp=hashlib.sha256(p.encode()).hexdigest()
                        usr=next((r for r in recs if str(r.get("username",""))==u and str(r.get("password",""))==hp),None)
                        if usr:
                            if str(usr.get("status","")).lower()=="blocked": st.error("🚫 Hisob bloklangan")
                            else:
                                st.session_state.update({"username":u,"logged_in":True,"login_time":datetime.now()})
                                if rem: cookies["ss7"]=u; cookies.save()
                                st.rerun()
                        else: st.error("❌ Username yoki parol xato")
                    except Exception as e: st.error(f"❌ {e}")
        with t2:
            with st.form("rf"):
                nu=st.text_input("",placeholder="Username (≥3)",key="ru",label_visibility="collapsed")
                np=st.text_input("",type="password",placeholder="Parol (≥6)",key="rp",label_visibility="collapsed")
                nc=st.text_input("",type="password",placeholder="Qayta kiriting",key="rc",label_visibility="collapsed")
                ag=st.checkbox("Shartlarga roziman")
                s2=st.form_submit_button("Hisob yaratish",use_container_width=True)
                if s2:
                    if not ag: st.error("❌ Shartlarga rozilik kerak")
                    elif len(nu)<3: st.error("❌ Username ≥ 3")
                    elif len(np)<6: st.error("❌ Parol ≥ 6")
                    elif np!=nc: st.error("❌ Parollar mos emas")
                    elif user_db:
                        try:
                            recs=user_db.get_all_records()
                            if any(r.get("username")==nu for r in recs): st.error("❌ Username band")
                            else:
                                user_db.append_row([nu,hashlib.sha256(np.encode()).hexdigest(),"active",str(datetime.now())])
                                st.success("🎉 Hisob yaratildi!")
                        except Exception as e: st.error(f"❌ {e}")
        with t3:
            st.markdown("""
**✦ Somo AI v7.0**

| Engine | Vazifa |
|--------|--------|
| 🟠 Groq LLaMA 3.3 70B | Chat, kod, matn |
| 🔵 Gemini Flash 2.0 | Rasm, PDF, DOCX |
| 🎙 Whisper v3 | Audio → Matn |

**Ctrl+V** — rasmni paste qiling  
📧 support@somoai.uz
            """)
        st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="foot">© 2026 Somo AI</div>',unsafe_allow_html=True)
    st.stop()

# ════════════════════════════════════════════════════════════════
# 13. SESSION DEFAULTS
# ════════════════════════════════════════════════════════════════
for k,v in {"messages":[],"page":"chat","files":[],"chat_history":[]}.items():
    if k not in st.session_state: st.session_state[k]=v

uname=st.session_state.username
paste_js()

# ════════════════════════════════════════════════════════════════
# 14. SIDEBAR — ChatGPT exact layout
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo row
    st.markdown(f"""
    <div class="sb-top">
        <div class="sb-logo">✦ Somo <span class="sb-logo-dot">AI</span></div>
    </div>
    """, unsafe_allow_html=True)

    # New chat (primary black button)
    if st.button("✏️  Yangi suhbat", use_container_width=True, key="nc", type="primary"):
        st.session_state.messages=[]
        st.session_state.files=[]
        st.session_state.page="chat"
        st.rerun()

    # Navigation
    st.markdown('<div class="sb-sec">Sahifalar</div>', unsafe_allow_html=True)
    for icon,label,pg in [("💬","Chat","chat"),("🎨","Shablonlar","templates"),("💌","Fikrlar","feedback")]:
        if st.button(f"{icon}  {label}",use_container_width=True,key=f"np_{pg}"):
            st.session_state.page=pg; st.rerun()

    # Chat history (last 5 messages as history)
    if st.session_state.messages:
        st.markdown('<div class="sb-sec">Chatlar</div>', unsafe_allow_html=True)
        user_msgs=[m["content"] for m in st.session_state.messages if m["role"]=="user"]
        for i,msg in enumerate(user_msgs[-5:]):
            txt=msg[:32]+"..." if len(msg)>32 else msg
            st.markdown(f'<div class="sb-chat-item {"active" if i==len(user_msgs[-5:])-1 else ""}">{txt}</div>',
                        unsafe_allow_html=True)

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)

    # AI status
    st.markdown('<div class="sb-sec">AI Holati</div>', unsafe_allow_html=True)
    g_s="🟢" if groq_cl else "🔴"; gm_s="🟢" if gemini_md else "🔴"
    st.markdown(f"""
    <div style="padding:2px 6px;font-size:12px;color:#666;line-height:2.3;">
        {g_s} Groq — Chat · Whisper<br>
        {gm_s} Gemini — Vision · PDF · DOCX
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)

    # Settings
    if st.session_state.page=="chat":
        st.markdown('<div class="sb-sec">Sozlamalar</div>', unsafe_allow_html=True)
        temperature=st.slider("Ijodkorlik",0.0,1.0,0.6,0.05,key="temp")
        model=st.selectbox("Model",key="mdl",
            options=["llama-3.3-70b-versatile","mixtral-8x7b-32768","gemma2-9b-it","llama-3.1-8b-instant"],
            format_func=lambda x:{"llama-3.3-70b-versatile":"LLaMA 3.3 70B ⚡",
                "mixtral-8x7b-32768":"Mixtral 8x7B","gemma2-9b-it":"Gemma 2 9B",
                "llama-3.1-8b-instant":"LLaMA 3.1 8B"}.get(x,x))
        st.caption("🔵 Rasm/PDF/DOCX → Gemini avtomatik")

        # Stats
        dur=(datetime.now()-st.session_state.login_time).seconds//60 if "login_time" in st.session_state else 0
        c1,c2=st.columns(2)
        with c1: st.markdown(f'<div class="sb-stat"><div class="sb-stat-v">{len(st.session_state.messages)}</div><div class="sb-stat-l">Xabar</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="sb-stat"><div class="sb-stat-v">{dur}</div><div class="sb-stat-l">Daqiqa</div></div>',unsafe_allow_html=True)

        st.markdown("")
        if st.session_state.messages:
            st.download_button("📥 Saqlash",
                json.dumps(st.session_state.messages,ensure_ascii=False,indent=2),
                f"somo_{datetime.now().strftime('%Y%m%d_%H%M')}.json","application/json",
                use_container_width=True,key="dlch")
        if st.button("🗑  Tozalash",use_container_width=True,key="clr"):
            st.session_state.messages=[]; st.session_state.files=[]; st.rerun()

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)

    # User row (bottom like ChatGPT)
    st.markdown(f"""
    <div class="sb-user">
        <div class="sb-av">{uname[0].upper()}</div>
        <div>
            <div class="sb-name">{uname}</div>
            <div class="sb-plan">Free</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪  Chiqish",use_container_width=True,key="lo",type="primary"):
        do_logout()

# ════════════════════════════════════════════════════════════════
# 15. CHAT PAGE
# ════════════════════════════════════════════════════════════════
if st.session_state.page=="chat":

    # ─── HOME SCREEN (when no messages)
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="home-center">
            <div class="home-title">Bugun qanday yordam bera olaman?</div>
        </div>
        """, unsafe_allow_html=True)

        # 4 suggestion cards 2×2
        col1, col2 = st.columns(2)
        cards = [
            ("🖼 Rasm tahlil qil", "Ctrl+V yoki fayl yuklang — Gemini Vision ko'radi"),
            ("📄 PDF / DOCX o'qi", "Hujjat yuklang — jadval va rasmlar ham tahlil"),
            ("📊 Taqdimot yarat", "\"Taqdimot yarat\" yazib yuboring — PPTX tayyor"),
            ("💻 Kod yoz", "Python, JS, SQL yoki boshqa tilda kod yoz"),
        ]
        with col1:
            for title,desc in cards[:2]:
                st.markdown(f'<div class="sg-card"><div class="sg-title">{title}</div><div class="sg-desc">{desc}</div></div>', unsafe_allow_html=True)
        with col2:
            for title,desc in cards[2:]:
                st.markdown(f'<div class="sg-card"><div class="sg-title">{title}</div><div class="sg-desc">{desc}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Quick action chips
        quick=["📊 Biznes reja","📝 Rezyume yarat","🌐 HTML sahifa","🐍 Python kod","📈 Excel jadval","🎯 Taqdimot"]
        bc=st.columns(3)
        for i,q in enumerate(quick):
            with bc[i%3]:
                if st.button(q,key=f"qs_{i}",use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":q}); st.rerun()

    # ─── CHAT HISTORY
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            c=m["content"]
            if isinstance(c,list):
                for p in c:
                    if isinstance(p,dict) and p.get("type")=="text": st.markdown(p["text"])
            else: st.markdown(c)

    # ─── ATTACHED FILES BADGE
    if st.session_state.files:
        badges="".join(
            f'<span class="xfc">{ficon(f["name"])} {f["name"]}'
            f'{"&nbsp;<small style=\'color:#1d4ed8;\'>Gemini</small>" if f.get("gem") else ""}'
            f'</span>'
            for f in st.session_state.files
        )
        ca,cb=st.columns([5,1])
        with ca: st.markdown(f'<div style="margin:6px 0 2px;">{badges}</div>',unsafe_allow_html=True)
        with cb:
            if st.button("✕",key="clf",use_container_width=True):
                st.session_state.files=[]; st.rerun()

    # ─── FILE UPLOAD EXPANDER
    with st.expander("➕  Fayl biriktirish  ·  Ctrl+V  ·  Drag & Drop", expanded=False):
        up=st.file_uploader("",label_visibility="collapsed",
            type=["jpg","jpeg","png","webp","gif","pdf","docx","doc","txt","csv",
                  "xlsx","xls","json","yaml","xml","py","js","ts","jsx","tsx",
                  "html","css","md","java","cpp","c","go","rs","sh","svg",
                  "rb","php","swift","kt","r","sql","toml"],
            accept_multiple_files=True,key="fup")
        if up:
            for f in up:
                if any(a["name"]==f.name for a in st.session_state.files): continue
                f.seek(0); fb=f.read()
                if is_img(f):
                    b64=base64.b64encode(fb).decode()
                    st.image(fb,caption=f.name,width=220)
                    st.session_state.files.append({"name":f.name,"type":"image","bytes":fb,"data":b64,"media_type":img_mime(f),"gem":True})
                    st.success(f"✅ Gemini Vision: {f.name}")
                elif is_pdf(f):
                    st.session_state.files.append({"name":f.name,"type":"pdf","bytes":fb,"gem":True})
                    st.success(f"✅ Gemini PDF: {f.name} ({len(fb)//1024} KB)")
                elif is_docx(f):
                    st.session_state.files.append({"name":f.name,"type":"docx","bytes":fb,"gem":True})
                    st.success(f"✅ Gemini DOCX: {f.name}")
                else:
                    txt=read_text(fb,f.name,getattr(f,"type",""))
                    st.session_state.files.append({"name":f.name,"type":"text","text":txt,"gem":False})
                    st.success(f"✅ Groq: {f.name}")

    # ─── WHISPER EXPANDER
    with st.expander("🎙  Ovozli xabar — Groq Whisper", expanded=False):
        af=st.file_uploader("",label_visibility="collapsed",
            type=["wav","mp3","m4a","ogg","flac","webm"],key="aup")
        if af:
            st.audio(af)
            if st.button("🎙 Matnga aylantirish",use_container_width=True,key="wbtn"):
                with st.spinner("Whisper eshityapti..."):
                    txt=groq_stt(af.read(),af.name)
                    if txt: st.success("✅ Aniqlandi:"); st.info(txt); st.session_state["_w"]=txt
                    else: st.error("❌ Audio o'qilmadi")

    # ─── CHAT INPUT (Streamlit's built-in)
    prompt=st.chat_input("Xabar yuboring...",key="ci")

    if "_w" in st.session_state and st.session_state["_w"]:
        prompt=st.session_state.pop("_w")

    if prompt:
        ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        T=st.session_state.get("temp",0.6)
        M=st.session_state.get("mdl","llama-3.3-70b-versatile")

        gf=[f for f in st.session_state.files if f.get("gem")]
        tf=[f for f in st.session_state.files if not f.get("gem")]

        if st.session_state.files:
            names=", ".join(f["name"] for f in st.session_state.files)
            disp=f"📎 *[{names}]* — {prompt}"
        else: disp=prompt

        st.session_state.messages.append({"role":"user","content":disp})
        with st.chat_message("user"): st.markdown(disp)

        if chat_db:
            try: chat_db.append_row([ts,uname,"User",prompt[:500]])
            except: pass

        with st.chat_message("assistant"):
            final=None

            # GEMINI PATH
            if gf and gemini_md:
                st.markdown('<span class="xp xp-gm">🔵 Gemini</span>',unsafe_allow_html=True)
                with st.spinner("Gemini o'qiyapti..."):
                    parts=[]
                    for f in gf:
                        if   f["type"]=="image": r=gem_img(prompt,f["data"],f.get("media_type","image/png"))
                        elif f["type"]=="pdf":   r=gem_pdf(prompt,f["bytes"])
                        elif f["type"]=="docx":  r=gem_docx(prompt,f["bytes"])
                        else: r=None
                        if r: parts.append(f"**{f['name']}:**\n\n{r}")
                    if parts: final="\n\n---\n\n".join(parts)
                    else: st.warning("⚠️ Gemini javob bermadi, Groq ishlatilmoqda...")

            # GROQ PATH
            if not final:
                st.markdown('<span class="xp xp-g">🟠 Groq</span>',unsafe_allow_html=True)
                SYS=(
                    "Sening isming Somo AI. Seni Usmonov Sodiq yaratgan. "
                    "Sen foydali, professional, aniq yordamchi AI san. "
                    "LaTeX ($...$) faqat matematika uchun. "
                    "ASOSIY QOIDA: Oddiy savol → qisqa, aniq javob. "
                    "Taqdimot so'ralsa → ## sarlavhalar + bullet list. "
                    "Jadval so'ralsa → Markdown jadval yoki ```csv. "
                    "Hujjat/CV so'ralsa → to'liq formatlangan matn. "
                    "HTML so'ralsa → ```html blokida to'liq kod. "
                    "Kod so'ralsa → tegishli blokda ishlaydigan kod. "
                    "SO'RALMAGAN NARSANI HECH QACHON YARATMA!"
                )
                msgs=[{"role":"system","content":SYS}]
                if tf:
                    ctx="\n\n".join(f"=== {f['name']} ===\n{f.get('text','')[:4000]}" for f in tf if f.get("text"))
                    if ctx: msgs.append({"role":"system","content":f"Yuklangan fayllar:\n{ctx}"})
                for old in st.session_state.messages[-20:]:
                    r=old["role"]; c=old["content"]
                    if isinstance(c,list): c=" ".join(p.get("text","") for p in c if isinstance(p,dict))
                    msgs.append({"role":r,"content":c})
                with st.spinner("O'ylayapman..."):
                    final=groq_ask(msgs,M,T,4096)

            if final:
                st.markdown(final)
                offer_dl(final,prompt,ts)
                st.session_state.messages.append({"role":"assistant","content":final})
                if chat_db:
                    try: chat_db.append_row([ts,"Somo AI","Assistant",final[:500]])
                    except: pass

            st.session_state.files=[]

# ════════════════════════════════════════════════════════════════
# 16. TEMPLATES PAGE
# ════════════════════════════════════════════════════════════════
elif st.session_state.page=="templates":
    st.markdown('<div class="pg-h">🎨 Shablonlar</div>',unsafe_allow_html=True)
    st.markdown('<div class="pg-s">Tezkor boshlash uchun professional shablonlar</div>',unsafe_allow_html=True)

    cat=st.selectbox("",list(TMPLS.keys()),label_visibility="collapsed",key="tc")
    st.markdown(f"#### {cat}")
    st.markdown("---")

    items=TMPLS[cat]
    for i in range(0,len(items),2):
        cols=st.columns(2)
        for j,t in enumerate(items[i:i+2]):
            with cols[j]:
                st.markdown(f'<div class="tpl-card"><div style="font-size:20px;margin-bottom:6px;">{t["icon"]}</div><div style="font-size:14px;font-weight:600;margin-bottom:8px;">{t["title"]}</div></div>',unsafe_allow_html=True)
                st.code(t["prompt"],language="text")
                ca,cb=st.columns(2)
                with ca:
                    if st.button("📋",key=f"cp_{i}_{j}",use_container_width=True): st.success("✅ Ko'chirildi!")
                with cb:
                    if st.button("🚀 Ishlatish",key=f"us_{i}_{j}",use_container_width=True):
                        st.session_state.messages.append({"role":"user","content":t["prompt"]})
                        st.session_state.page="chat"; st.rerun()

    st.info("💡 [qavs] ichini o'z ma'lumotlaringiz bilan almashtiring")

# ════════════════════════════════════════════════════════════════
# 17. FEEDBACK PAGE
# ════════════════════════════════════════════════════════════════
elif st.session_state.page=="feedback":
    st.markdown('<div class="pg-h">💌 Fikr-Mulohaza</div>',unsafe_allow_html=True)
    st.markdown('<div class="pg-s">Sizning fikringiz Somo AI ni yaxshilaydi</div>',unsafe_allow_html=True)

    _,fc,_=st.columns([1,2,1])
    with fc:
        with st.form("ff"):
            rating=st.select_slider("Baho",[1,2,3,4,5],5,format_func=lambda x:"⭐"*x)
            st.markdown(f"<div style='text-align:center;font-size:34px;margin:8px 0;'>{'⭐'*rating}</div>",unsafe_allow_html=True)
            cf=st.selectbox("Kategoriya",["Umumiy","Xato","Yangi funksiya","Savol","Boshqa"])
            mf=st.text_area("Xabar",placeholder="Fikrlaringiz...",height=110)
            ef=st.text_input("Email (ixtiyoriy)",placeholder="email@example.com")
            sf=st.form_submit_button("Yuborish",use_container_width=True)
            if sf:
                if not mf or len(mf)<10: st.error("❌ Kamida 10 belgi kiriting")
                elif fb_db:
                    try:
                        fb_db.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),uname,rating,cf,mf,ef or "N/A","Yangi"])
                        st.balloons(); st.success("✅ Rahmat!"); time.sleep(1.5); st.rerun()
                    except Exception as e: st.error(f"❌ {e}")
                else: st.error("❌ Baza yo'q")

    st.markdown("---")
    st.markdown("#### Statistika")
    if fb_db:
        try:
            allfb=fb_db.get_all_records()
            if len(allfb)>1:
                c1,c2,c3=st.columns(3)
                rtgs=[int(f.get("Rating",0)) for f in allfb[1:] if f.get("Rating")]
                with c1: st.metric("📨 Jami",len(allfb)-1)
                with c2: st.metric("⭐ O'rtacha",f"{sum(rtgs)/len(rtgs):.1f}" if rtgs else "—")
                with c3: st.metric("🆕 Yangi",sum(1 for f in allfb[-20:] if f.get("Status")=="Yangi"))
            else: st.info("💬 Hali fikr yo'q")
        except: st.warning("⚠️ Yuklanmadi")

# ════════════════════════════════════════════════════════════════
# 18. FOOTER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="foot">
    ✦ Somo AI v7.0 &nbsp;·&nbsp;
    🟠 Groq LLaMA 3.3 &nbsp;·&nbsp;
    🔵 Gemini Flash 2.0 &nbsp;·&nbsp;
    🎙 Whisper v3<br>
    👨‍💻 Usmonov Sodiq &nbsp;·&nbsp; Davlatov Mironshoh<br>
    📧 support@somoai.uz &nbsp;·&nbsp; © 2026
</div>
""",unsafe_allow_html=True)
