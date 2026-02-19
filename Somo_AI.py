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

# ═══════════════════════════════════════════════════════════
# 1. PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Somo AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

cookies = EncryptedCookieManager(
    password=st.secrets.get("COOKIE_PASSWORD", "SomoAI_v5_Secret_2026")
)
if not cookies.ready():
    st.stop()

# ═══════════════════════════════════════════════════════════
# 2. CSS — ChatGPT Light Theme (exact match)
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:          #ffffff;
    --bg2:         #f9f9f9;
    --bg3:         #f0f0f0;
    --border:      #e5e5e5;
    --border2:     #d9d9d9;
    --text:        #0d0d0d;
    --text2:       #555;
    --text3:       #888;
    --accent:      #10a37f;
    --accent2:     #0d9068;
    --accent-bg:   rgba(16,163,127,.08);
    --sidebar-bg:  #f9f9f9;
    --sidebar-w:   260px;
    --radius:      12px;
    --radius-lg:   18px;
    --font:        'Inter', -apple-system, sans-serif;
    --mono:        'JetBrains Mono', monospace;
    --trans:       all .18s ease;
}

* { box-sizing: border-box; margin:0; padding:0; }

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 15px;
    line-height: 1.65;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stSidebarNav"],
.st-emotion-cache-1vt458p,
.st-emotion-cache-k77z8z,
.st-emotion-cache-12fmjuu,
[data-testid="stDecoration"] { display:none !important; }

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border) !important;
    width: var(--sidebar-w) !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; background: transparent !important; }
[data-testid="stSidebar"] section { background: transparent !important; }

/* Sidebar buttons */
div[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    color: var(--text2) !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    text-align: left !important;
    padding: 9px 14px !important;
    margin: 1px 0 !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: var(--trans) !important;
    justify-content: flex-start !important;
}
div[data-testid="stSidebar"] .stButton button:hover {
    background: var(--bg3) !important;
    color: var(--text) !important;
    transform: none !important;
}
div[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: var(--text) !important;
    color: #fff !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}
div[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
    background: #222 !important;
}

/* ─── MAIN ─── */
.main .block-container {
    max-width: 760px !important;
    margin: 0 auto !important;
    padding: 0 24px 140px !important;
}

/* ─── CHAT MESSAGES ─── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 20px 0 !important;
    border-bottom: 1px solid var(--border) !important;
    box-shadow: none !important;
}
[data-testid="stChatMessage"]:last-child { border-bottom: none !important; }

[data-testid="stChatMessageContent"] p {
    color: var(--text) !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
    margin-bottom: 8px !important;
}
[data-testid="stChatMessageContent"] code {
    background: var(--bg3) !important;
    color: #c7254e !important;
    font-family: var(--mono) !important;
    font-size: 13px !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stChatMessageContent"] pre {
    background: #f6f8fa !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 16px !important;
    overflow-x: auto !important;
}
[data-testid="stChatMessageContent"] pre code {
    background: transparent !important;
    border: none !important;
    color: #24292e !important;
    padding: 0 !important;
}

/* ─── CHAT INPUT — ChatGPT style ─── */
[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 0 !important;
    left: var(--sidebar-w) !important;
    right: 0 !important;
    background: var(--bg) !important;
    border-top: 1px solid var(--border) !important;
    padding: 14px 24px 18px !important;
    z-index: 1000 !important;
}
[data-testid="stChatInput"] > div {
    max-width: 720px !important;
    margin: 0 auto !important;
}
[data-testid="stChatInput"] textarea {
    background: var(--bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 26px !important;
    font-family: var(--font) !important;
    font-size: 15px !important;
    padding: 13px 50px 13px 48px !important;
    resize: none !important;
    box-shadow: 0 2px 8px rgba(0,0,0,.07) !important;
    transition: var(--trans) !important;
    min-height: 50px !important;
    max-height: 200px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--border2) !important;
    box-shadow: 0 2px 12px rgba(0,0,0,.12) !important;
    outline: none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--text3) !important; }
[data-testid="stChatInput"] button {
    background: var(--text) !important;
    border-radius: 50% !important;
    width: 34px !important; height: 34px !important;
    border: none !important;
    color: white !important;
    transition: var(--trans) !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] button:hover {
    background: #333 !important;
    transform: scale(1.05) !important;
}
[data-testid="stChatInput"] button:disabled {
    background: var(--border2) !important;
}

/* ─── INPUTS ─── */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background: var(--bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    font-family: var(--font) !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #aaa !important;
    box-shadow: 0 0 0 2px rgba(0,0,0,.06) !important;
    outline: none !important;
}
.stSelectbox [data-baseweb="select"] > div {
    background: var(--bg) !important;
    border-color: var(--border2) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
}

/* ─── LABELS ─── */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stSlider label,
.stFileUploader label, .stCheckbox label {
    color: var(--text2) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* ─── BUTTONS ─── */
.stButton button {
    background: var(--bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    font-family: var(--font) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    transition: var(--trans) !important;
    box-shadow: none !important;
}
.stButton button:hover {
    background: var(--bg3) !important;
    border-color: #bbb !important;
    transform: none !important;
}
.stButton button[kind="primary"] {
    background: var(--text) !important;
    color: #fff !important;
    border-color: var(--text) !important;
}
.stButton button[kind="primary"]:hover {
    background: #333 !important;
}

/* ─── DOWNLOAD ─── */
.stDownloadButton button {
    background: var(--accent-bg) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(16,163,127,.25) !important;
    border-radius: var(--radius) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
}
.stDownloadButton button:hover {
    background: rgba(16,163,127,.14) !important;
    transform: none !important;
}

/* ─── EXPANDER ─── */
.stExpander {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    margin-bottom: 6px !important;
}
.stExpander summary {
    color: var(--text2) !important;
    font-size: 14px !important;
    padding: 10px 16px !important;
}
[data-testid="stExpanderDetails"] {
    background: var(--bg2) !important;
    padding: 10px 16px 14px !important;
}

/* ─── TABS ─── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text3) !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 18px !important;
    box-shadow: none !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text) !important; }
.stTabs [aria-selected="true"] {
    color: var(--text) !important;
    border-bottom-color: var(--text) !important;
}

/* ─── FILE UPLOADER ─── */
[data-testid="stFileUploader"] {
    background: var(--bg2) !important;
    border: 1.5px dashed var(--border2) !important;
    border-radius: var(--radius) !important;
    padding: 16px !important;
}
[data-testid="stFileUploader"]:hover { border-color: #aaa !important; }

/* ─── ALERTS ─── */
.stSuccess { background: #f0fdf4 !important; border-left: 3px solid var(--accent) !important; color:#166534 !important; border-radius: var(--radius) !important; }
.stError   { background: #fef2f2 !important; border-left: 3px solid #ef4444 !important; color:#991b1b !important; border-radius: var(--radius) !important; }
.stWarning { background: #fffbeb !important; border-left: 3px solid #f59e0b !important; color:#92400e !important; border-radius: var(--radius) !important; }
.stInfo    { background: #eff6ff !important; border-left: 3px solid #3b82f6 !important; color:#1e40af !important; border-radius: var(--radius) !important; }

/* ─── CHECKBOX ─── */
.stCheckbox [data-baseweb="checkbox"] { color: var(--text2) !important; }

/* ─── SLIDER ─── */
.stSlider [role="slider"] { background: var(--text) !important; }

/* ─── FORM SUBMIT ─── */
[data-testid="stFormSubmitButton"] button {
    background: var(--text) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 11px 24px !important;
    border-radius: var(--radius) !important;
    width: 100%;
}
[data-testid="stFormSubmitButton"] button:hover { background: #333 !important; }

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background: #aaa; }

/* ─── METRIC ─── */
[data-testid="stMetricValue"] { color: var(--text) !important; font-size:22px !important; font-weight:600 !important; }
[data-testid="stMetricLabel"] { color: var(--text3) !important; font-size:11px !important; }

/* ─── CUSTOM CLASSES ─── */
.s-logo {
    font-size: 18px; font-weight: 600; color: var(--text);
    padding: 18px 16px 12px; border-bottom: 1px solid var(--border);
    letter-spacing: -.3px;
}
.s-logo span { color: var(--accent); }
.s-version { font-size: 10px; color: var(--text3); font-weight: 400; margin-left: 4px; }

.s-section {
    font-size: 10px; font-weight: 600; letter-spacing: .8px;
    text-transform: uppercase; color: var(--text3);
    padding: 14px 16px 4px;
}
.s-divider { height:1px; background: var(--border); margin: 6px 0; }

.s-user-row {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 16px 14px;
}
.s-avatar {
    width:30px; height:30px; border-radius:50%;
    background: linear-gradient(135deg,#10a37f,#6366f1);
    display:flex; align-items:center; justify-content:center;
    font-size:13px; font-weight:700; color:white; flex-shrink:0;
}
.s-uname { font-size:13px; color: var(--text); font-weight:500; }
.s-ustatus { font-size:11px; color: var(--accent); }

.s-stat {
    background: var(--bg3); border-radius: 10px; padding: 10px;
    text-align: center;
}
.s-stat-val { font-size:20px; font-weight:600; color: var(--text); }
.s-stat-lbl { font-size:10px; color: var(--text3); margin-top:1px; }

.api-pill {
    display:inline-flex; align-items:center; gap:4px;
    padding:2px 9px; border-radius:20px; font-size:11px; font-weight:600;
    margin:2px; letter-spacing:.2px;
}
.pill-g  { background:#fff7ed; color:#c2410c; border:1px solid #fed7aa; }
.pill-gm { background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; }
.pill-ok { background:#f0fdf4; color:#15803d; border:1px solid #bbf7d0; }

.file-chip {
    display:inline-flex; align-items:center; gap:5px;
    background:var(--bg3); border:1px solid var(--border2);
    border-radius:20px; padding:3px 11px; font-size:12px;
    color:var(--text2); margin:2px;
}

.dl-card {
    background:var(--bg2); border:1px solid var(--border);
    border-radius: var(--radius); padding:14px; margin:10px 0;
    border-left: 3px solid var(--accent);
}
.dl-title { font-size:12px; font-weight:600; color:var(--accent); margin-bottom:10px; }

.welcome-title {
    font-size:28px; font-weight:600; color:var(--text);
    text-align:center; margin:48px 0 8px; letter-spacing:-.5px;
}
.welcome-sub { font-size:15px; color:var(--text3); text-align:center; margin-bottom:32px; }

.q-grid {
    display:grid; grid-template-columns:1fr 1fr;
    gap:10px; margin: 24px 0;
}
.q-card {
    background:var(--bg2); border:1px solid var(--border);
    border-radius:var(--radius); padding:16px 18px;
    cursor:pointer; transition:var(--trans);
}
.q-card:hover { background:var(--bg3); border-color:#bbb; }
.q-card-title { font-size:13px; font-weight:500; color:var(--text); }
.q-card-desc  { font-size:12px; color:var(--text3); margin-top:3px; }

.login-wrap { max-width:380px; margin:60px auto; padding:0 16px; }
.login-title { font-size:24px; font-weight:600; color:var(--text); text-align:center; margin-bottom:6px; }
.login-sub   { font-size:14px; color:var(--text3); text-align:center; margin-bottom:28px; }
.login-card  {
    background:var(--bg); border:1px solid var(--border);
    border-radius:var(--radius-lg); padding:28px;
    box-shadow:0 2px 16px rgba(0,0,0,.07);
}

.tmpl-card {
    background:var(--bg2); border:1px solid var(--border);
    border-radius:var(--radius); padding:18px; margin-bottom:10px;
}

.footer-txt {
    text-align:center; color:var(--text3); font-size:12px;
    padding:32px 0 16px; border-top:1px solid var(--border);
    margin-top:48px; line-height:2;
}

@media (max-width:768px) {
    :root { --sidebar-w: 0px; }
    .main .block-container { padding: 0 12px 120px !important; }
    [data-testid="stChatInput"] { left:0 !important; padding:10px 12px 14px !important; }
    .q-grid { grid-template-columns: 1fr !important; }
}

.stSpinner > div { border-top-color: var(--accent) !important; }
hr { border-color: var(--border) !important; }
audio { border-radius:var(--radius); }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# 3. CTRL+V PASTE JS
# ═══════════════════════════════════════════════════════════
def inject_paste_js():
    components.html("""
<script>
(function() {
  function notify(msg) {
    var n = document.createElement('div');
    n.textContent = msg;
    n.style.cssText = [
      'position:fixed','bottom:80px','left:50%',
      'transform:translateX(-50%)','background:#0d0d0d','color:#fff',
      'padding:8px 18px','border-radius:20px','font-size:13px',
      'z-index:9999','font-family:Inter,sans-serif',
      'box-shadow:0 4px 12px rgba(0,0,0,.2)',
      'transition:opacity .3s'
    ].join(';');
    document.body.appendChild(n);
    setTimeout(function() { n.style.opacity='0'; setTimeout(function(){ n.remove(); },300); }, 2000);
  }

  document.addEventListener('paste', function(e) {
    var items = (e.clipboardData || window.clipboardData || {}).items;
    if (!items) return;
    for (var i=0; i<items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        var f = items[i].getAsFile();
        if (!f) continue;
        var r = new FileReader();
        r.onload = function(ev) {
          sessionStorage.setItem('somo_paste_img',  ev.target.result);
          sessionStorage.setItem('somo_paste_name', 'clipboard_' + Date.now() + '.png');
          notify('📋 Rasm qo\'shildi — yuborish uchun Enter bosing');
        };
        r.readAsDataURL(f);
        e.preventDefault();
        break;
      }
    }
  });

  document.addEventListener('dragover', function(e){ e.preventDefault(); });
  document.addEventListener('drop', function(e) {
    e.preventDefault();
    var files = e.dataTransfer.files;
    if (!files.length) return;
    var f = files[0];
    if (f.type.startsWith('image/')) {
      var r = new FileReader();
      r.onload = function(ev) {
        sessionStorage.setItem('somo_paste_img',  ev.target.result);
        sessionStorage.setItem('somo_paste_name', f.name);
        notify('🖼 ' + f.name + ' qo\'shildi');
      };
      r.readAsDataURL(f);
    }
  });
})();
</script>
""", height=0)

# ═══════════════════════════════════════════════════════════
# 4. CONNECTIONS
# ═══════════════════════════════════════════════════════════
@st.cache_resource
def get_db():
    try:
        scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        u  = ss.sheet1
        c  = ss.worksheet("ChatHistory")
        try:
            f = ss.worksheet("Letters")
        except:
            f = ss.add_worksheet("Letters", 1000, 10)
            f.append_row(["Timestamp","Username","Rating","Category","Message","Email","Status"])
        return u, c, f
    except Exception as e:
        st.error(f"❌ DB: {e}")
        return None, None, None

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

# ═══════════════════════════════════════════════════════════
# 5. HELPERS
# ═══════════════════════════════════════════════════════════
def emoji_for(name):
    ext = name.lower().rsplit(".",1)[-1] if "." in name else ""
    return {"pdf":"📄","docx":"📝","doc":"📝","txt":"📃","csv":"📊","xlsx":"📊",
            "xls":"📊","json":"🔧","py":"🐍","js":"🟨","html":"🌐","css":"🎨",
            "ts":"🔷","jsx":"⚛️","tsx":"⚛️","java":"☕","cpp":"⚙️","c":"⚙️",
            "png":"🖼","jpg":"🖼","jpeg":"🖼","webp":"🖼","gif":"🎞","svg":"🎨",
            "md":"📋","yaml":"🔧","xml":"🔧","sh":"💻","go":"🐹","rs":"🦀",
            "rb":"💎","php":"🐘","swift":"🍎","kt":"📱","sql":"🗃",
            "mp3":"🎵","wav":"🎵","m4a":"🎵"}.get(ext,"📎")

def is_img(f):  return getattr(f,"type","") in ["image/jpeg","image/jpg","image/png","image/webp","image/gif"]
def is_pdf(f):  return getattr(f,"type","") == "application/pdf"
def is_docx(f): return "wordprocessingml" in getattr(f,"type","") or getattr(f,"name","").endswith((".docx",".doc"))

def img_mime(f):
    return {"image/jpeg":"image/jpeg","image/jpg":"image/jpeg",
            "image/png":"image/png","image/webp":"image/webp",
            "image/gif":"image/gif"}.get(getattr(f,"type",""),"image/png")

def read_text_file(fbytes, name, mime=""):
    n = name.lower()
    try:
        if n.endswith(".csv") or mime=="text/csv":
            return "CSV:\n" + fbytes.decode("utf-8","ignore")[:5000]
        if n.endswith(".json"):
            return "JSON:\n" + fbytes.decode("utf-8","ignore")[:5000]
        if n.endswith((".xlsx",".xls")):
            return f"Excel fayl: {name}"
        if any(n.endswith(x) for x in [".py",".js",".ts",".jsx",".tsx",".html",".css",".md",
            ".txt",".java",".cpp",".c",".go",".rs",".sh",".yaml",".xml",".sql",
            ".kt",".rb",".php",".swift",".r",".toml",".gitignore",".env"]):
            return fbytes.decode("utf-8","ignore")
    except: pass
    return ""

def code_blocks(text):
    return re.findall(r"```(\w*)\n?(.*?)```", text, re.DOTALL)

# ═══════════════════════════════════════════════════════════
# 6. GEMINI READERS
# ═══════════════════════════════════════════════════════════
def gem_image(prompt, b64, mime="image/png"):
    if not gemini_md: return None
    try:
        raw = base64.b64decode(b64.split(",",1)[1] if "," in b64 else b64)
        return gemini_md.generate_content([prompt, {"mime_type":mime,"data":raw}]).text
    except: return None

def gem_pdf(prompt, fbytes):
    if not gemini_md: return None
    try:    return gemini_md.generate_content([prompt, {"mime_type":"application/pdf","data":fbytes}]).text
    except: return None

def gem_docx(prompt, fbytes):
    if not gemini_md: return None
    try:
        txt = mammoth.extract_raw_text(io.BytesIO(fbytes)).value
        if txt.strip():
            return gemini_md.generate_content([f"{prompt}\n\nHujjat:\n{txt[:10000]}"]).text
    except: pass
    return None

# ═══════════════════════════════════════════════════════════
# 7. GROQ FUNCTIONS
# ═══════════════════════════════════════════════════════════
def groq_ask(msgs, model, temp=0.6, max_tok=4096):
    if not groq_cl: return "❌ Groq mavjud emas."
    try:
        r = groq_cl.chat.completions.create(messages=msgs, model=model, temperature=temp, max_tokens=max_tok)
        return r.choices[0].message.content
    except Exception as e:
        return f"❌ Groq: {e}"

def groq_whisper(abytes, fname="audio.wav"):
    if not groq_cl: return None
    try:
        t = groq_cl.audio.transcriptions.create(file=(fname, abytes), model="whisper-large-v3")
        return t.text
    except: return None

# ═══════════════════════════════════════════════════════════
# 8. FILE BUILDERS
# ═══════════════════════════════════════════════════════════
def build_excel(text, ts):
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

        wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Somo AI"
        cm = re.search(r"```csv\n?(.*?)```", text, re.DOTALL)
        tm = re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+\n((\|.+\|\n?)+)", text)
        rows = []
        if cm:   rows = list(csv.reader(io.StringIO(cm.group(1).strip())))
        elif tm:
            for l in tm.group(0).strip().split("\n"):
                if "---" not in l:
                    c = [x.strip() for x in l.strip("|").split("|")]
                    if any(c): rows.append(c)
        if not rows: return None

        hf = PatternFill("solid", fgColor="0D0D0D")
        hfnt = Font(bold=True, color="FFFFFF", size=11, name="Calibri")
        af = PatternFill("solid", fgColor="F9F9F9")
        bs = Side(style="thin", color="E5E5E5")
        brd = Border(left=bs, right=bs, top=bs, bottom=bs)
        ca = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for ri, row in enumerate(rows, 1):
            for ci, val in enumerate(row, 1):
                cell = ws.cell(ri, ci, val)
                cell.border = brd; cell.alignment = ca
                if ri == 1:   cell.fill=hf; cell.font=hfnt
                elif ri%2==0: cell.fill=af; cell.font=Font(size=11,name="Calibri")
                else:         cell.font=Font(size=11,name="Calibri")

        for col in ws.columns:
            ml = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(ml+4, 45)
        for row in ws.iter_rows():
            ws.row_dimensions[row[0].row].height = 22

        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
        return buf.read()
    except: return None


def build_pptx(text, ts):
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN

        prs = Presentation()
        prs.slide_width  = Inches(13.33)
        prs.slide_height = Inches(7.5)

        WHITE = RGBColor(0xFF,0xFF,0xFF)
        BLACK = RGBColor(0x0D,0x0D,0x0D)
        GRAY  = RGBColor(0xF9,0xF9,0xF9)
        ACC   = RGBColor(0x10,0xA3,0x7F)
        COLS  = [ACC, RGBColor(0x63,0x66,0xF1), RGBColor(0xF5,0x9E,0x0B),
                 RGBColor(0xEC,0x48,0x99), RGBColor(0x06,0xB6,0xD4)]

        def R(sl, l,t,w,h, c):
            s = sl.shapes.add_shape(1, Inches(l),Inches(t),Inches(w),Inches(h))
            s.fill.solid(); s.fill.fore_color.rgb = c
            s.line.fill.background(); return s

        def T(sl, txt, l,t,w,h, sz=22, bold=False, c=None, al=PP_ALIGN.LEFT, it=False):
            b = sl.shapes.add_textbox(Inches(l),Inches(t),Inches(w),Inches(h))
            f = b.text_frame; f.word_wrap=True
            p = f.paragraphs[0]; p.alignment=al
            r = p.add_run(); r.text=txt
            r.font.size=Pt(sz); r.font.bold=bold; r.font.italic=it
            r.font.color.rgb = c or BLACK; return b

        lines = text.strip().split("\n")
        slides, cur = [], {"title":"","bullets":[]}
        for ln in lines:
            ln = ln.strip()
            if not ln: continue
            if re.match(r"^#{1,3}\s+", ln):
                if cur["title"] or cur["bullets"]: slides.append(cur)
                cur = {"title": re.sub(r"^#{1,3}\s+","",ln).strip(), "bullets":[]}
            elif re.match(r"^(\d+\.|[-*•►▸])\s+", ln):
                cur["bullets"].append(re.sub(r"^(\d+\.|[-*•►▸])\s+","",ln).strip())
            elif re.match(r"^\*\*(.+)\*\*$", ln):
                if cur["title"] or cur["bullets"]: slides.append(cur)
                cur = {"title": re.sub(r"\*\*","",ln).strip(), "bullets":[]}
            elif not ln.startswith("```"):
                cur["bullets"].append(ln)
        if cur["title"] or cur["bullets"]: slides.append(cur)

        if len(slides) < 2:
            chunks = [l.strip() for l in lines if l.strip() and not l.startswith("```")]
            slides = [{"title": chunks[0] if chunks else "Somo AI", "bullets": chunks[1:3]}]
            for i in range(3, len(chunks), 4):
                slides.append({"title":f"Qism {(i-3)//4+1}", "bullets":chunks[i:i+4]})

        blank = prs.slide_layouts[6]

        # Title
        sl = prs.slides.add_slide(blank)
        R(sl, 0,0,13.33,7.5, RGBColor(0x0D,0x0D,0x0D))
        R(sl, 0,0,.08,7.5, ACC)
        R(sl, 0,5.9,13.33,1.6, RGBColor(0x1A,0x1A,0x1A))
        T(sl, slides[0]["title"] or "Somo AI", .5,1.6,12.3,2.5, sz=44,bold=True,c=WHITE)
        sub = slides[0]["bullets"][0] if slides[0]["bullets"] else "Somo AI"
        T(sl, sub, .5,4.1,11.0,1.2, sz=22, c=RGBColor(0x9C,0xA3,0xAF), it=True)
        T(sl, "✦ Somo AI  ·  "+datetime.now().strftime("%Y"), .5,6.15,8.0,.55, sz=12, c=RGBColor(0x6B,0x72,0x80))

        # Content
        for idx, sd in enumerate(slides[1:], 1):
            sl  = prs.slides.add_slide(blank)
            acc = COLS[idx % len(COLS)]
            R(sl, 0,0,13.33,7.5, GRAY)
            R(sl, 0,0,.07,7.5, acc)
            R(sl, .07,0,13.26,1.45, WHITE)
            R(sl, .07,1.38,13.26,.05, acc)
            R(sl, 11.95,.18,1.1,1.1, acc)
            T(sl, str(idx), 12.0,.22,1.0,1.0, sz=28,bold=True,c=WHITE, al=PP_ALIGN.CENTER)
            T(sl, sd["title"] or f"Slayd {idx}", .3,.18,11.5,1.1, sz=33,bold=True,c=BLACK)

            buls = sd["bullets"][:7]
            if buls:
                y0    = 1.62
                ystep = min(.76, 5.4/max(len(buls),1))
                bh    = ystep*.88
                for bi, bul in enumerate(buls):
                    R(sl, .28, y0+bi*ystep+.18, .08,.3, acc)
                    clean = re.sub(r"^\*\*(.+)\*\*",r"\1", bul)
                    is_b  = bul.startswith("**") and bul.endswith("**")
                    T(sl, clean, .5,y0+bi*ystep,12.5,bh, sz=19,bold=is_b,c=BLACK)

            R(sl, 0,7.2,13.33,.3, WHITE)
            T(sl, "✦ Somo AI", .3,7.22,4.0,.25, sz=10, c=RGBColor(0x9C,0xA3,0xAF))
            T(sl, f"{idx}/{len(slides)-1}", 12.0,7.22,1.0,.25, sz=10, c=RGBColor(0x9C,0xA3,0xAF), al=PP_ALIGN.RIGHT)

        # End
        sl = prs.slides.add_slide(blank)
        R(sl, 0,0,13.33,7.5, RGBColor(0x0D,0x0D,0x0D))
        R(sl, 0,3.1,13.33,.06, ACC)
        R(sl, 0,4.34,13.33,.06, ACC)
        T(sl, "✅ Taqdimot yakunlandi", .5,3.2,12.3,1.1, sz=40,bold=True,c=WHITE, al=PP_ALIGN.CENTER)
        T(sl, "✦ Somo AI  ·  Groq + Gemini", .5,4.9,12.3,.7, sz=16, c=RGBColor(0x6B,0x72,0x80), al=PP_ALIGN.CENTER)

        buf = io.BytesIO(); prs.save(buf); buf.seek(0)
        return buf.read()
    except: return None


def build_word(text, ts):
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches

        doc = Document()
        for s in doc.sections:
            s.top_margin=s.bottom_margin=Inches(1)
            s.left_margin=s.right_margin=Inches(1.25)

        lines = text.strip().split("\n")
        in_code, code_buf = False, []
        for line in lines:
            s = line.strip()
            if s.startswith("```"):
                if not in_code:
                    in_code=True; code_buf=[]
                else:
                    in_code=False
                    p = doc.add_paragraph()
                    p.paragraph_format.left_indent = Inches(.3)
                    r = p.add_run("\n".join(code_buf))
                    r.font.name="Courier New"; r.font.size=Pt(10)
                    r.font.color.rgb=RGBColor(0x10,0xA3,0x7F)
                continue
            if in_code: code_buf.append(line); continue
            if not s: doc.add_paragraph(); continue
            if   re.match(r"^# ",s):
                h=doc.add_heading(s[2:],1)
                if h.runs: h.runs[0].font.color.rgb=RGBColor(0x10,0xA3,0x7F)
            elif re.match(r"^## ",s):
                h=doc.add_heading(s[3:],2)
                if h.runs: h.runs[0].font.color.rgb=RGBColor(0x63,0x66,0xF1)
            elif re.match(r"^### ",s):
                h=doc.add_heading(s[4:],3)
            elif re.match(r"^[-*•►▸]\s+",s):
                p=doc.add_paragraph(style="List Bullet")
                _frun(p, re.sub(r"^[-*•►▸]\s+","",s))
            elif re.match(r"^\d+\.\s+",s):
                p=doc.add_paragraph(style="List Number")
                _frun(p, re.sub(r"^\d+\.\s+","",s))
            else:
                p=doc.add_paragraph(); _frun(p,s)

        buf=io.BytesIO(); doc.save(buf); buf.seek(0)
        return buf.read()
    except: return None

def _frun(p, text):
    from docx.shared import RGBColor
    for part in re.split(r"(\*\*.*?\*\*|\*.*?\*)", text):
        if part.startswith("**") and part.endswith("**"):
            r=p.add_run(part[2:-2]); r.bold=True
            r.font.color.rgb=RGBColor(0x0D,0x0D,0x0D)
        elif part.startswith("*") and part.endswith("*"):
            r=p.add_run(part[1:-1]); r.italic=True
        else: p.add_run(part)

# ═══════════════════════════════════════════════════════════
# 9. SMART DOWNLOAD OFFER
# ─── FAQAT SO'RALGANDA chiqadi ───────────────────────────
# ═══════════════════════════════════════════════════════════
def offer_downloads(ai_text, user_prompt, ts):
    """
    Faylni faqat foydalanuvchi so'raganda taklif qiladi.
    'Salom', 'nima gap' kabi oddiy savollarda hech narsa chiqmaydi.
    """
    ts_safe = ts.replace(":","_").replace(" ","_")
    blks    = code_blocks(ai_text)
    up      = user_prompt.lower()
    at      = ai_text.lower()

    # ── Trigger detection ──
    PPTX_KW = ["taqdimot","slayd","slide","presentation","pptx","powerpoint","prezentatsiya"]
    XL_KW   = ["jadval","excel","xlsx","csv","statistika","ro'yxat","список","таблица"]
    DOC_KW  = ["rezyume","resume","cv","hujjat","word","docx","xat","shartnoma","insho","referat","maqola"]

    has_heads = len(re.findall(r"^#{1,3}\s+", ai_text, re.MULTILINE)) >= 3
    has_tbl   = bool(re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+", ai_text))
    has_csv   = "```csv" in ai_text

    want_pptx = any(k in up or k in at for k in PPTX_KW) or (has_heads and any(k in up for k in PPTX_KW))
    want_xl   = any(k in up for k in XL_KW) or has_tbl or has_csv
    want_doc  = any(k in up for k in DOC_KW) and not want_pptx

    # ── PPTX ──
    if want_pptx:
        data = build_pptx(ai_text, ts_safe)
        if data:
            st.markdown('<div class="dl-card"><div class="dl-title">📊 PowerPoint Taqdimot tayyor</div></div>', unsafe_allow_html=True)
            st.download_button("⬇️ PPTX yuklab olish", data, f"somo_{ts_safe}.pptx",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                key=f"p_{ts_safe}", use_container_width=True)

    # ── EXCEL ──
    if want_xl:
        data = build_excel(ai_text, ts_safe)
        if data:
            st.markdown('<div class="dl-card"><div class="dl-title">📊 Excel Jadval tayyor</div></div>', unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1:
                st.download_button("⬇️ Excel (.xlsx)", data, f"somo_{ts_safe}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"x_{ts_safe}", use_container_width=True)
            # CSV
            rows=[]
            cm=re.search(r"```csv\n?(.*?)```",ai_text,re.DOTALL)
            tm=re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+\n((\|.+\|\n?)+)",ai_text)
            if cm:   rows=list(csv.reader(io.StringIO(cm.group(1).strip())))
            elif tm:
                for l in tm.group(0).strip().split("\n"):
                    if "---" not in l:
                        c=[x.strip() for x in l.strip("|").split("|")]
                        if any(c): rows.append(c)
            if rows:
                cb=io.StringIO(); csv.writer(cb).writerows(rows)
                with c2:
                    st.download_button("⬇️ CSV", cb.getvalue().encode(), f"somo_{ts_safe}.csv", "text/csv",
                        key=f"c_{ts_safe}", use_container_width=True)

    # ── WORD ──
    if want_doc:
        data = build_word(ai_text, ts_safe)
        if data:
            st.markdown('<div class="dl-card"><div class="dl-title">📝 Word Hujjat tayyor</div></div>', unsafe_allow_html=True)
            st.download_button("⬇️ Word (.docx)", data, f"somo_{ts_safe}.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"d_{ts_safe}", use_container_width=True)

    # ── SVG ──
    svg_bl = [(l,c) for l,c in blks if l.lower()=="svg" or c.strip().startswith("<svg")]
    for i,(_,svg) in enumerate(svg_bl):
        st.markdown('<div class="dl-card"><div class="dl-title">🎨 SVG Rasm</div></div>', unsafe_allow_html=True)
        st.markdown(svg.strip(), unsafe_allow_html=True)
        st.download_button(f"⬇️ rasm_{i}.svg", svg.strip().encode(), f"somo_{ts_safe}_{i}.svg",
            "image/svg+xml", key=f"sv_{ts_safe}_{i}", use_container_width=True)

    # ── HTML ──
    html_bl = [(l,c) for l,c in blks if l.lower()=="html"]
    for i,(_,code) in enumerate(html_bl):
        st.markdown('<div class="dl-card"><div class="dl-title">🌐 HTML Sahifa</div></div>', unsafe_allow_html=True)
        with st.expander(f"👁 Ko'rish #{i+1}", expanded=True):
            components.html(code.strip(), height=400, scrolling=True)
        st.download_button(f"⬇️ sahifa_{i}.html", code.strip().encode(), f"somo_{ts_safe}_{i}.html",
            "text/html", key=f"h_{ts_safe}_{i}", use_container_width=True)

    # ── CODE FILES ──
    EXT = {"python":"py","py":"py","javascript":"js","js":"js","typescript":"ts","ts":"ts",
           "css":"css","json":"json","sql":"sql","bash":"sh","shell":"sh","sh":"sh",
           "yaml":"yaml","xml":"xml","markdown":"md","md":"md","jsx":"jsx","tsx":"tsx",
           "java":"java","cpp":"cpp","c":"c","rust":"rs","go":"go","php":"php",
           "ruby":"rb","swift":"swift","kotlin":"kt","r":"r","txt":"txt"}
    SKIP = {"html","svg","csv",""}
    others = [(l,c) for l,c in blks if l.lower() not in SKIP]
    if others:
        st.markdown('<div class="dl-card"><div class="dl-title">💾 Kod Fayllar</div></div>', unsafe_allow_html=True)
        cols = st.columns(min(len(others), 3))
        for i,(lang,code) in enumerate(others):
            ext  = EXT.get(lang.strip().lower(),"txt")
            fname= f"somo_{ts_safe}_{i}.{ext}"
            with cols[i%len(cols)]:
                st.download_button(f"{emoji_for(fname)} .{ext}", code.strip().encode(),
                    fname, "text/plain", key=f"cd_{ts_safe}_{i}", use_container_width=True)

# ═══════════════════════════════════════════════════════════
# 10. TEMPLATES
# ═══════════════════════════════════════════════════════════
TMPLS = {
    "💼 Biznes": [
        {"icon":"📊","title":"Biznes Reja","prompt":"[Kompaniya] uchun professional biznes reja:\n- Ijroiya xulosasi\n- Bozor tahlili\n- Marketing strategiyasi\n- Moliyaviy reja\n- 5 yillik prognoz"},
        {"icon":"📈","title":"Marketing Reja","prompt":"[Mahsulot] uchun digital marketing reja:\n- Target auditoriya\n- SMM\n- SEO\n- Byudjet\n- KPI"},
        {"icon":"📋","title":"SWOT Tahlil","prompt":"[Kompaniya] uchun SWOT tahlil jadvali yarat"},
        {"icon":"💼","title":"Taklifnoma","prompt":"[Mijoz] uchun professional taklifnoma:\n- Muammo\n- Yechim\n- Narxlar\n- Garantiya"},
    ],
    "💻 Dasturlash": [
        {"icon":"🐍","title":"Python","prompt":"Python'da [funksiya] kodi:\n- Type hints\n- Docstring\n- Error handling\n- Test"},
        {"icon":"🌐","title":"HTML Sahifa","prompt":"[Sahifa] uchun zamonaviy HTML/CSS/JS:\n- Responsive\n- Animatsiyalar"},
        {"icon":"🗃","title":"SQL","prompt":"[Jadval] uchun SQL so'rovlar: SELECT, JOIN, GROUP BY"},
        {"icon":"🔌","title":"API Kod","prompt":"[Til]da [API] integratsiya kodi: Auth, CRUD, Docs"},
    ],
    "📚 Ta'lim": [
        {"icon":"📖","title":"Dars Rejasi","prompt":"[Mavzu] dars rejasi:\n- Maqsadlar\n- Kirish\n- Asosiy qism\n- Amaliy\n- Vazifa"},
        {"icon":"📝","title":"Test Savollar","prompt":"[Mavzu] bo'yicha 20 ta test: 4 variant, to'g'ri javob"},
        {"icon":"🎯","title":"O'quv Reja","prompt":"[Soha] 3 oylik o'quv dasturi: haftalik jadval, resurslar"},
    ],
    "✍️ Kontent": [
        {"icon":"📄","title":"Rezyume","prompt":"[Kasb] uchun professional CV: maqsad, tajriba, ta'lim, ko'nikmalar"},
        {"icon":"✉️","title":"Motivatsion Xat","prompt":"[Kompaniya] ga [Lavozim] uchun motivatsion xat"},
        {"icon":"📰","title":"Blog Post","prompt":"[Mavzu] haqida blog post: sarlavha, kirish, asosiy, xulosa"},
    ],
}

# ═══════════════════════════════════════════════════════════
# 11. SESSION
# ═══════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    su = cookies.get("somo_s")
    if su and user_db:
        try:
            recs = user_db.get_all_records()
            ud   = next((r for r in recs if str(r.get("username",""))==su), None)
            if ud and str(ud.get("status","")).lower()=="active":
                st.session_state.update({"username":su,"logged_in":True,"login_time":datetime.now()})
            else: st.session_state.logged_in=False
        except: st.session_state.logged_in=False
    else: st.session_state.logged_in=False

def logout():
    try: cookies["somo_s"]=""; cookies.save()
    except: pass
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.session_state.logged_in=False; st.rerun()

# ═══════════════════════════════════════════════════════════
# 12. LOGIN PAGE
# ═══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    inject_paste_js()

    st.markdown("""
    <div class="login-wrap">
        <div class="login-title">✦ Somo AI</div>
        <div class="login-sub">Groq · Gemini · Whisper</div>
    </div>
    """, unsafe_allow_html=True)

    # Status pills
    g_ok  = groq_cl  is not None
    gm_ok = gemini_md is not None
    st.markdown(f"""
    <div style="display:flex;gap:8px;justify-content:center;margin-bottom:24px;flex-wrap:wrap;">
        <span class="api-pill {'pill-ok' if g_ok else 'pill-g'}">
            {'✅' if g_ok else '❌'} Groq — Chat · Whisper
        </span>
        <span class="api-pill {'pill-ok' if gm_ok else 'pill-gm'}">
            {'✅' if gm_ok else '❌'} Gemini — Vision · PDF
        </span>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["Kirish", "Ro'yxat", "Haqida"])

        with t1:
            with st.form("lf"):
                u = st.text_input("Username", placeholder="Username kiriting", key="lu")
                p = st.text_input("Parol", type="password", placeholder="Parol kiriting", key="lp")
                c1,c2 = st.columns([2,1])
                with c1: sub = st.form_submit_button("Kirish →", use_container_width=True)
                with c2: rem = st.checkbox("Eslab", value=True)
                if sub and u and p and user_db:
                    try:
                        recs = user_db.get_all_records()
                        hp   = hashlib.sha256(p.encode()).hexdigest()
                        usr  = next((r for r in recs if str(r.get("username",""))==u and str(r.get("password",""))==hp), None)
                        if usr:
                            if str(usr.get("status","")).lower()=="blocked":
                                st.error("🚫 Hisob bloklangan")
                            else:
                                st.session_state.update({"username":u,"logged_in":True,"login_time":datetime.now()})
                                if rem: cookies["somo_s"]=u; cookies.save()
                                st.rerun()
                        else: st.error("❌ Username yoki parol xato")
                    except Exception as e: st.error(f"❌ {e}")

        with t2:
            with st.form("rf"):
                nu = st.text_input("Username", placeholder="Kamida 3 belgi", key="ru")
                np = st.text_input("Parol", type="password", placeholder="Kamida 6 belgi", key="rp")
                nc = st.text_input("Tasdiqlash", type="password", placeholder="Qayta kiriting", key="rc")
                ag = st.checkbox("Foydalanish shartlariga roziman")
                s2 = st.form_submit_button("Hisob yaratish →", use_container_width=True)
                if s2:
                    if not ag:          st.error("❌ Shartlarga rozilik kerak")
                    elif len(nu)<3:     st.error("❌ Username ≥ 3 belgi")
                    elif len(np)<6:     st.error("❌ Parol ≥ 6 belgi")
                    elif np!=nc:        st.error("❌ Parollar mos emas")
                    elif user_db:
                        try:
                            recs=user_db.get_all_records()
                            if any(r.get("username")==nu for r in recs): st.error("❌ Username band")
                            else:
                                user_db.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active", str(datetime.now())])
                                st.success("🎉 Hisob yaratildi! Kiring.")
                        except Exception as e: st.error(f"❌ {e}")

        with t3:
            st.markdown("""
**✦ Somo AI v5.0**

| AI | Vazifa |
|----|--------|
| 🟠 **Groq 70B** | Chat, kod, hujjatlar |
| 🔵 **Gemini Flash** | Rasm, PDF, DOCX |
| 🎙 **Whisper** | Audio → Matn |

**Ctrl+V** — rasmni to'g'ridan qo'shing  
📧 support@somoai.uz
            """)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer-txt">© 2026 Somo AI · Barcha huquqlar himoyalangan</div>',
                unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════
# 13. SESSION DEFAULTS
# ═══════════════════════════════════════════════════════════
for k,v in {"messages":[],"current_page":"chat","attached":[],"total":0}.items():
    if k not in st.session_state: st.session_state[k]=v

uname = st.session_state.username
inject_paste_js()

# ═══════════════════════════════════════════════════════════
# 14. SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    # Logo
    st.markdown(f"""
    <div class="s-logo">✦ Somo <span>AI</span><span class="s-version">v5.0</span></div>
    """, unsafe_allow_html=True)

    # New chat
    if st.button("✦  Yangi suhbat", use_container_width=True, key="nc", type="primary"):
        st.session_state.messages  = []
        st.session_state.attached  = []
        st.session_state.current_page = "chat"
        st.rerun()

    # Nav
    st.markdown('<div class="s-section">Menyular</div>', unsafe_allow_html=True)
    for icon, label, pg in [("💬","Chat","chat"),("🎨","Shablonlar","templates"),("💌","Fikrlar","feedback")]:
        if st.button(f"{icon}  {label}", use_container_width=True, key=f"n_{pg}"):
            st.session_state.current_page=pg; st.rerun()

    st.markdown('<div class="s-divider"></div>', unsafe_allow_html=True)

    # API status
    st.markdown('<div class="s-section">AI Holati</div>', unsafe_allow_html=True)
    g_s  = "🟢" if groq_cl   else "🔴"
    gm_s = "🟢" if gemini_md else "🔴"
    st.markdown(f"""
    <div style="padding:0 4px;font-size:12px;color:#666;line-height:2.2;">
        {g_s} Groq — Chat · Whisper<br>
        {gm_s} Gemini — Vision · PDF · DOCX
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="s-divider"></div>', unsafe_allow_html=True)

    # Stats
    st.markdown('<div class="s-section">Statistika</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    dur = (datetime.now()-st.session_state.login_time).seconds//60 if "login_time" in st.session_state else 0
    with c1:
        st.markdown(f'<div class="s-stat"><div class="s-stat-val">{len(st.session_state.messages)}</div><div class="s-stat-lbl">Xabar</div></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="s-stat"><div class="s-stat-val">{dur}</div><div class="s-stat-lbl">Daqiqa</div></div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="s-divider"></div>', unsafe_allow_html=True)

    if st.session_state.current_page == "chat":
        st.markdown('<div class="s-section">Sozlamalar</div>', unsafe_allow_html=True)

        temperature = st.slider("Ijodkorlik", 0.0, 1.0, 0.6, 0.05, key="temp")
        model_choice = st.selectbox("Model", key="mdl",
            options=["llama-3.3-70b-versatile","mixtral-8x7b-32768","gemma2-9b-it","llama-3.1-8b-instant"],
            format_func=lambda x:{"llama-3.3-70b-versatile":"LLaMA 3.3 70B ⚡",
                "mixtral-8x7b-32768":"Mixtral 8x7B","gemma2-9b-it":"Gemma 2 9B",
                "llama-3.1-8b-instant":"LLaMA 3.1 8B (Tez)"}.get(x,x))
        st.caption("Rasm/PDF/DOCX → avtomatik Gemini")

        if st.session_state.messages:
            st.download_button("📥 Chat saqlash",
                json.dumps(st.session_state.messages, ensure_ascii=False, indent=2),
                f"somo_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                "application/json", use_container_width=True, key="dl_ch")

        if st.button("🗑  Tozalash", use_container_width=True, key="clr"):
            st.session_state.messages=[]; st.session_state.attached=[]; st.rerun()

    st.markdown('<div class="s-divider"></div>', unsafe_allow_html=True)

    # User
    st.markdown(f"""
    <div class="s-user-row">
        <div class="s-avatar">{uname[0].upper()}</div>
        <div>
            <div class="s-uname">{uname}</div>
            <div class="s-ustatus">● Aktiv</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪  Chiqish", use_container_width=True, key="lo", type="primary"):
        logout()

# ═══════════════════════════════════════════════════════════
# 15. CHAT PAGE
# ═══════════════════════════════════════════════════════════
if st.session_state.current_page == "chat":

    # Welcome
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="welcome-title">Salom, {uname} 👋</div>
        <div class="welcome-sub">Bugun qanday yordam bera olaman?</div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="q-grid">
            <div class="q-card">
                <div class="q-card-title">🖼 Rasm tahlil</div>
                <div class="q-card-desc">Ctrl+V yoki fayl yuklang — Gemini Vision</div>
            </div>
            <div class="q-card">
                <div class="q-card-title">📄 PDF / DOCX</div>
                <div class="q-card-desc">Hujjat yuklang — Gemini o'qiydi</div>
            </div>
            <div class="q-card">
                <div class="q-card-title">📊 Taqdimot</div>
                <div class="q-card-desc">"Taqdimot yarat" yazib yuboring</div>
            </div>
            <div class="q-card">
                <div class="q-card-title">💻 Kod</div>
                <div class="q-card-desc">Har qanday tilda kod, yuklab olish</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick chips
        quick = ["📊 Biznes reja","🌐 HTML sahifa","📝 Rezyume yarat",
                 "🐍 Python kod","📈 Excel jadval","🎯 Taqdimot yarat"]
        cols = st.columns(3)
        for i,q in enumerate(quick):
            with cols[i%3]:
                if st.button(q, key=f"qs_{i}", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":q})
                    st.rerun()

    # Chat history
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            c = m["content"]
            if isinstance(c, list):
                for p in c:
                    if isinstance(p,dict) and p.get("type")=="text": st.markdown(p["text"])
            else: st.markdown(c)

    # Attached files display
    if st.session_state.attached:
        badges = "".join(
            f'<span class="file-chip">{emoji_for(f["name"])} {f["name"]}'
            f'{"&nbsp;<small style=\'color:#2563eb\'>Gemini</small>" if f.get("gem") else ""}'
            f'</span>'
            for f in st.session_state.attached
        )
        ca, cb = st.columns([5,1])
        with ca: st.markdown(f'<div style="margin:6px 0;">{badges}</div>', unsafe_allow_html=True)
        with cb:
            if st.button("✕", key="clf", use_container_width=True):
                st.session_state.attached=[]; st.rerun()

    # File upload
    with st.expander("➕  Fayl biriktirish  ·  Ctrl+V  ·  Drag & Drop", expanded=False):
        up = st.file_uploader("Fayl", label_visibility="collapsed",
            type=["jpg","jpeg","png","webp","gif","pdf","docx","doc","txt","csv",
                  "xlsx","xls","json","yaml","xml","py","js","ts","jsx","tsx",
                  "html","css","md","java","cpp","c","go","rs","sh","svg",
                  "rb","php","swift","kt","r","sql","toml"],
            accept_multiple_files=True, key="fup")

        if up:
            for f in up:
                if any(a["name"]==f.name for a in st.session_state.attached): continue
                f.seek(0); fb=f.read()

                if is_img(f):
                    b64=base64.b64encode(fb).decode()
                    st.image(fb, caption=f.name, width=240)
                    st.session_state.attached.append({"name":f.name,"type":"image",
                        "bytes":fb,"data":b64,"media_type":img_mime(f),"gem":True})
                    st.success(f"✅ 🔵 Gemini Vision: {f.name}")
                elif is_pdf(f):
                    st.session_state.attached.append({"name":f.name,"type":"pdf","bytes":fb,"gem":True})
                    st.success(f"✅ 🔵 Gemini PDF: {f.name} ({len(fb)//1024} KB)")
                elif is_docx(f):
                    st.session_state.attached.append({"name":f.name,"type":"docx","bytes":fb,"gem":True})
                    st.success(f"✅ 🔵 Gemini DOCX: {f.name}")
                else:
                    txt=read_text_file(fb, f.name, getattr(f,"type",""))
                    st.session_state.attached.append({"name":f.name,"type":"text","text":txt,"gem":False})
                    st.success(f"✅ 🟠 Groq: {f.name}")

    # Whisper
    with st.expander("🎙  Ovozli xabar — Groq Whisper", expanded=False):
        af = st.file_uploader("Audio", label_visibility="collapsed",
            type=["wav","mp3","m4a","ogg","flac","webm"], key="aup")
        if af:
            st.audio(af)
            if st.button("🎙 Matnga aylantirish", use_container_width=True, key="wbtn"):
                with st.spinner("🎙 Whisper eshityapti..."):
                    txt = groq_whisper(af.read(), af.name)
                    if txt:
                        st.success("✅ Aniqlandi:")
                        st.info(txt)
                        st.session_state["_w"] = txt
                    else: st.error("❌ Audio o'qilmadi")

    # ── CHAT INPUT ──────────────────────────────────────
    prompt = st.chat_input("Xabar yuboring...", key="ci")

    if "_w" in st.session_state and st.session_state["_w"]:
        prompt = st.session_state.pop("_w")

    if prompt:
        ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        temp = st.session_state.get("temp", 0.6)
        mdl  = st.session_state.get("mdl", "llama-3.3-70b-versatile")

        gem_files  = [f for f in st.session_state.attached if f.get("gem")]
        text_files = [f for f in st.session_state.attached if not f.get("gem")]

        if st.session_state.attached:
            names = ", ".join(f["name"] for f in st.session_state.attached)
            disp  = f"📎 *[{names}]* — {prompt}"
        else:
            disp = prompt

        st.session_state.messages.append({"role":"user","content":disp})
        with st.chat_message("user"): st.markdown(disp)

        if chat_db:
            try: chat_db.append_row([ts, uname, "User", prompt[:500]])
            except: pass

        with st.chat_message("assistant"):
            final = None

            # GEMINI path
            if gem_files and gemini_md:
                st.markdown('<span class="api-pill pill-gm">🔵 Gemini</span>', unsafe_allow_html=True)
                with st.spinner("🔵 Gemini o'qiyapti..."):
                    parts=[]
                    for gf in gem_files:
                        if   gf["type"]=="image": r=gem_image(prompt, gf["data"], gf.get("media_type","image/png"))
                        elif gf["type"]=="pdf":   r=gem_pdf(prompt, gf["bytes"])
                        elif gf["type"]=="docx":  r=gem_docx(prompt, gf["bytes"])
                        else: r=None
                        if r: parts.append(f"**{gf['name']}:**\n\n{r}")
                    if parts: final="\n\n---\n\n".join(parts)
                    else: st.warning("⚠️ Gemini javob bermadi, Groq bilan davom etilmoqda...")

            # GROQ path
            if not final:
                st.markdown(f'<span class="api-pill pill-g">🟠 Groq</span>', unsafe_allow_html=True)

                SYS = (
                    "Sening isming Somo AI. Seni Usmonov Sodiq yaratgan. "
                    "Sen foydali, professional yordamchi sun'iy intellektsan. "
                    "Matematikani LaTeX ($...$) da yoz. "
                    "MUHIM — Fayllar faqat so'ralganda: "
                    "Taqdimot/slayd so'ralsa — ## sarlavhalar + bullet yoz. "
                    "Jadval so'ralsa — Markdown jadval yoki ```csv yoz. "
                    "Hujjat/rezyume so'ralsa — to'liq formatlangan matn yoz. "
                    "HTML so'ralsa — ```html blokida yoz. "
                    "ODDIY SAVOLLARGA oddiy, qisqa va aniq javob ber. "
                    "Hech qachon so'ralmagan narsani yaratma!"
                )
                msgs = [{"role":"system","content":SYS}]

                if text_files:
                    ctx = "\n\n".join(f"=== {f['name']} ===\n{f.get('text','')[:4000]}" for f in text_files if f.get("text"))
                    if ctx: msgs.append({"role":"system","content":f"Fayllar:\n{ctx}"})

                for old in st.session_state.messages[-20:]:
                    role=old["role"]; cont=old["content"]
                    if isinstance(cont,list):
                        cont=" ".join(p.get("text","") for p in cont if isinstance(p,dict))
                    msgs.append({"role":role,"content":cont})

                with st.spinner("O'ylayapman..."):
                    final = groq_ask(msgs, mdl, temp, 4096)

            if final:
                st.markdown(final)
                offer_downloads(final, prompt, ts)
                st.session_state.messages.append({"role":"assistant","content":final})
                st.session_state.total += 1
                if chat_db:
                    try: chat_db.append_row([ts,"Somo AI","Assistant",final[:500]])
                    except: pass

            st.session_state.attached=[]

# ═══════════════════════════════════════════════════════════
# 16. TEMPLATES
# ═══════════════════════════════════════════════════════════
elif st.session_state.current_page == "templates":
    st.markdown('<div class="welcome-title">✦ Shablonlar</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-sub">Professional shablonlar bilan tez boshlang</div>', unsafe_allow_html=True)
    st.markdown("")

    cat = st.selectbox("Kategoriya", list(TMPLS.keys()), label_visibility="collapsed", key="tc")
    st.markdown(f"#### {cat}")
    st.markdown('<div class="s-divider"></div>', unsafe_allow_html=True)

    items = TMPLS[cat]
    for i in range(0, len(items), 2):
        cols = st.columns(2)
        for j,t in enumerate(items[i:i+2]):
            with cols[j]:
                st.markdown(f"""
                <div class="tmpl-card">
                    <div style="font-size:22px;margin-bottom:8px;">{t['icon']}</div>
                    <div style="font-size:14px;font-weight:600;color:var(--text);margin-bottom:10px;">{t['title']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.code(t["prompt"], language="text")
                ca,cb = st.columns(2)
                with ca:
                    if st.button("📋", key=f"cp_{i}_{j}", use_container_width=True): st.success("✅ Ko'chirildi!")
                with cb:
                    if st.button("🚀 Ishlatish", key=f"us_{i}_{j}", use_container_width=True):
                        st.session_state.messages.append({"role":"user","content":t["prompt"]})
                        st.session_state.current_page="chat"; st.rerun()

    st.info("💡 [qavs] ichini o'z ma'lumotlaringiz bilan to'ldiring")

# ═══════════════════════════════════════════════════════════
# 17. FEEDBACK
# ═══════════════════════════════════════════════════════════
elif st.session_state.current_page == "feedback":
    st.markdown('<div class="welcome-title">✦ Fikr-Mulohaza</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-sub">Sizning fikringiz Somo AI ni yaxshilaydi</div>', unsafe_allow_html=True)
    st.markdown("")

    _, fc, _ = st.columns([1,2,1])
    with fc:
        with st.form("ff"):
            rating = st.select_slider("Baho",[1,2,3,4,5],5, format_func=lambda x:"⭐"*x)
            st.markdown(f"<div style='text-align:center;font-size:36px;margin:10px 0;'>{'⭐'*rating}</div>",
                        unsafe_allow_html=True)
            cat_f = st.selectbox("Kategoriya",["Umumiy","Xato","Yangi funksiya","Savol","Boshqa"])
            msg_f = st.text_area("Xabar", placeholder="Fikrlaringiz...", height=120)
            eml_f = st.text_input("Email (ixtiyoriy)", placeholder="email@example.com")
            sf    = st.form_submit_button("Yuborish →", use_container_width=True)
            if sf:
                if not msg_f or len(msg_f)<10: st.error("❌ Kamida 10 belgi kiriting")
                elif fb_db:
                    try:
                        fb_db.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            uname,rating,cat_f,msg_f,eml_f or "N/A","Yangi"])
                        st.balloons(); st.success("✅ Rahmat!"); time.sleep(1.5); st.rerun()
                    except Exception as e: st.error(f"❌ {e}")
                else: st.error("❌ Baza yo'q")

    st.markdown('<div class="s-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### Statistika")
    if fb_db:
        try:
            all_fb = fb_db.get_all_records()
            if len(all_fb)>1:
                c1,c2,c3 = st.columns(3)
                rtgs = [int(f.get("Rating",0)) for f in all_fb[1:] if f.get("Rating")]
                with c1: st.metric("📨 Jami", len(all_fb)-1)
                with c2: st.metric("⭐ O'rtacha", f"{sum(rtgs)/len(rtgs):.1f}" if rtgs else "—")
                with c3: st.metric("🆕 Yangi", sum(1 for f in all_fb[-20:] if f.get("Status")=="Yangi"))
            else: st.info("💬 Hali fikr yo'q")
        except: st.warning("⚠️ Yuklanmadi")

# ═══════════════════════════════════════════════════════════
# 18. FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="footer-txt">
    ✦ Somo AI v5.0 &nbsp;·&nbsp;
    🟠 Groq LLaMA 3.3 &nbsp;·&nbsp;
    🔵 Gemini Flash 2.0 &nbsp;·&nbsp;
    🎙 Whisper<br>
    👨‍💻 Usmonov Sodiq &nbsp;·&nbsp; Davlatov Mironshoh<br>
    📧 support@somoai.uz &nbsp;·&nbsp; © 2026
</div>
""", unsafe_allow_html=True)
