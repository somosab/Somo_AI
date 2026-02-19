import streamlit as st
import streamlit.components.v1 as components
import gspread
import hashlib
import mammoth
import base64
import time
import json
import io
import os
import csv
import re
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# ═══════════════════════════════════════════════════════════
# 1. SAHIFA SOZLAMALARI
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Somo AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

cookies = EncryptedCookieManager(
    password=st.secrets.get("COOKIE_PASSWORD", "SomoAI_v4_Ultra_Secret_2026")
)
if not cookies.ready():
    st.stop()

# ═══════════════════════════════════════════════════════════
# 2. GLOBAL CSS — ChatGPT-like Dark Theme
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Söhne:wght@300;400;500;600&family=Söhne+Mono&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── ROOT ── */
:root {
    --bg-primary:    #212121;
    --bg-secondary:  #2f2f2f;
    --bg-tertiary:   #3a3a3a;
    --bg-hover:      #404040;
    --bg-input:      #2f2f2f;
    --border:        #4a4a4a;
    --border-light:  #383838;
    --text-primary:  #ececec;
    --text-secondary:#b4b4b4;
    --text-muted:    #8e8ea0;
    --accent:        #10a37f;
    --accent-hover:  #0d9068;
    --accent-soft:   rgba(16,163,127,0.15);
    --user-bubble:   #2f2f2f;
    --ai-bubble:     transparent;
    --danger:        #ef4444;
    --warning:       #f59e0b;
    --radius-sm:     6px;
    --radius-md:     12px;
    --radius-lg:     18px;
    --radius-xl:     24px;
    --shadow-sm:     0 1px 3px rgba(0,0,0,.4);
    --shadow-md:     0 4px 16px rgba(0,0,0,.5);
    --shadow-lg:     0 8px 32px rgba(0,0,0,.6);
    --font-main:     'DM Sans', -apple-system, sans-serif;
    --font-mono:     'JetBrains Mono', 'Courier New', monospace;
    --sidebar-w:     260px;
    --transition:    all .2s cubic-bezier(.4,0,.2,1);
}

/* ── BASE ── */
* { box-sizing: border-box; }
html, body, .stApp {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-main) !important;
    font-size: 15px;
    line-height: 1.6;
}

/* ── HIDE STREAMLIT DEFAULT ── */
#MainMenu, footer, header,
[data-testid="stSidebarNav"],
.st-emotion-cache-1vt458p,
.st-emotion-cache-k77z8z,
.st-emotion-cache-12fmjuu { display:none !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #171717 !important;
    border-right: 1px solid var(--border-light) !important;
    width: var(--sidebar-w) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    background: #171717 !important;
}
[data-testid="stSidebar"] section { background: transparent !important; }

/* ── SIDEBAR BUTTONS ── */
div[data-testid="stSidebar"] button {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-main) !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    text-align: left !important;
    padding: 10px 12px !important;
    margin: 1px 0 !important;
    width: 100% !important;
    transition: var(--transition) !important;
    box-shadow: none !important;
}
div[data-testid="stSidebar"] button:hover {
    background: var(--bg-hover) !important;
    color: var(--text-primary) !important;
    transform: none !important;
}
div[data-testid="stSidebar"] button[kind="primary"] {
    background: var(--accent) !important;
    color: white !important;
}
div[data-testid="stSidebar"] button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
}

/* ── MAIN CONTENT ── */
.main .block-container {
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 0 20px 120px !important;
}

/* ── CHAT MESSAGES ── */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 20px 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
}
[data-testid="stChatMessage"] {
    padding: 16px 0 !important;
    border-bottom: 1px solid var(--border-light) !important;
}
[data-testid="stChatMessage"]:last-child {
    border-bottom: none !important;
}
[data-testid="stChatMessageContent"] p {
    color: var(--text-primary) !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
    margin: 0 0 8px !important;
}
[data-testid="stChatMessageContent"] code {
    background: var(--bg-tertiary) !important;
    color: #e2b96e !important;
    font-family: var(--font-mono) !important;
    font-size: 13px !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stChatMessageContent"] pre {
    background: #1a1a1a !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 16px !important;
    overflow-x: auto !important;
}
[data-testid="stChatMessageContent"] pre code {
    background: transparent !important;
    border: none !important;
    color: #abb2bf !important;
    padding: 0 !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 0 !important;
    left: var(--sidebar-w) !important;
    right: 0 !important;
    background: var(--bg-primary) !important;
    border-top: 1px solid var(--border-light) !important;
    padding: 16px 24px 20px !important;
    z-index: 999 !important;
}
[data-testid="stChatInput"] textarea {
    background: var(--bg-input) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-xl) !important;
    font-family: var(--font-main) !important;
    font-size: 15px !important;
    padding: 14px 52px 14px 20px !important;
    resize: none !important;
    transition: var(--transition) !important;
    max-height: 200px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    outline: none !important;
    box-shadow: 0 0 0 2px var(--accent-soft) !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
}
[data-testid="stChatInput"] button {
    background: var(--accent) !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    border: none !important;
    color: white !important;
    transition: var(--transition) !important;
}
[data-testid="stChatInput"] button:hover {
    background: var(--accent-hover) !important;
    transform: scale(1.05) !important;
}

/* ── INPUTS, SELECTS, TEXTAREAS ── */
.stTextInput input, .stTextArea textarea,
.stSelectbox select, .stNumberInput input {
    background: var(--bg-input) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    font-family: var(--font-main) !important;
    font-size: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-soft) !important;
}
.stSelectbox [data-baseweb="select"] > div {
    background: var(--bg-input) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-md) !important;
}

/* ── LABELS ── */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stSlider label,
.stFileUploader label, .stCheckbox label {
    color: var(--text-secondary) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* ── BUTTONS ── */
.stButton button {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    font-family: var(--font-main) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    transition: var(--transition) !important;
    box-shadow: none !important;
}
.stButton button:hover {
    background: var(--bg-hover) !important;
    border-color: var(--text-muted) !important;
    transform: none !important;
}
.stButton button[kind="primary"] {
    background: var(--accent) !important;
    color: white !important;
    border-color: var(--accent) !important;
}
.stButton button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
}

/* ── DOWNLOAD BUTTONS ── */
.stDownloadButton button {
    background: var(--accent-soft) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(16,163,127,.3) !important;
    border-radius: var(--radius-md) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    transition: var(--transition) !important;
}
.stDownloadButton button:hover {
    background: rgba(16,163,127,.25) !important;
}

/* ── EXPANDER ── */
.stExpander {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    margin-bottom: 8px !important;
}
.stExpander summary {
    color: var(--text-secondary) !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
}
.stExpander summary:hover { color: var(--text-primary) !important; }
[data-testid="stExpanderDetails"] {
    background: var(--bg-secondary) !important;
    padding: 12px 16px !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border-light) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 12px 20px !important;
    transition: var(--transition) !important;
    box-shadow: none !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-primary) !important; }
.stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: var(--bg-secondary) !important;
    border: 1px dashed var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 20px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* ── METRICS ── */
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 24px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 12px !important;
}

/* ── ALERTS / INFO / SUCCESS ── */
.stAlert {
    background: var(--bg-secondary) !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
}
.stSuccess { border-left: 3px solid var(--accent) !important; }
.stError   { border-left: 3px solid var(--danger) !important; }
.stWarning { border-left: 3px solid var(--warning) !important; }
.stInfo    { border-left: 3px solid #60a5fa !important; }

/* ── SLIDER ── */
.stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
    background: var(--accent) !important;
    color: white !important;
}

/* ── CHECKBOX ── */
.stCheckbox [data-baseweb="checkbox"] [data-checked="true"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
}

/* ── SELECT SLIDER ── */
.stSelectSlider [data-baseweb="slider"] [role="slider"] {
    background: var(--accent) !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── CUSTOM COMPONENTS ── */
.somo-header {
    text-align: center;
    padding: 48px 24px 32px;
}
.somo-logo {
    font-size: 48px;
    font-weight: 300;
    color: var(--text-primary);
    letter-spacing: -1px;
    margin-bottom: 8px;
}
.somo-logo span { color: var(--accent); }
.somo-tagline {
    color: var(--text-muted);
    font-size: 16px;
    font-weight: 300;
}

.api-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .3px;
    margin: 2px;
}
.pill-groq   { background: rgba(249,115,22,.15); color: #fb923c; border: 1px solid rgba(249,115,22,.3); }
.pill-gemini { background: rgba(66,133,244,.15);  color: #60a5fa; border: 1px solid rgba(66,133,244,.3); }
.pill-ok     { background: rgba(16,163,127,.15);  color: var(--accent); border: 1px solid rgba(16,163,127,.3); }
.pill-err    { background: rgba(239,68,68,.15);   color: #f87171; border: 1px solid rgba(239,68,68,.3); }

.greeting-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin: 32px 0;
}
.greeting-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 20px;
    cursor: pointer;
    transition: var(--transition);
}
.greeting-card:hover {
    background: var(--bg-tertiary);
    border-color: var(--accent);
    transform: translateY(-2px);
}
.greeting-card-icon { font-size: 24px; margin-bottom: 10px; }
.greeting-card-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
}
.greeting-card-desc {
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.5;
}

.sidebar-section {
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .8px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 16px 0 4px;
}
.sidebar-divider {
    height: 1px;
    background: var(--border-light);
    margin: 8px 12px;
}

.file-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    color: var(--text-secondary);
    margin: 3px;
    transition: var(--transition);
}
.file-chip:hover { border-color: var(--accent); }

.dl-card {
    background: var(--bg-secondary);
    border: 1px solid rgba(16,163,127,.3);
    border-radius: var(--radius-md);
    padding: 16px;
    margin: 12px 0;
}
.dl-card-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--accent);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.model-badge {
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 11px;
    color: var(--text-muted);
    float: right;
}

.paste-zone {
    background: var(--bg-secondary);
    border: 2px dashed var(--border);
    border-radius: var(--radius-lg);
    padding: 24px;
    text-align: center;
    transition: var(--transition);
    cursor: pointer;
    position: relative;
}
.paste-zone.drag-over {
    border-color: var(--accent);
    background: var(--accent-soft);
}
.paste-zone-text { color: var(--text-muted); font-size: 14px; }
.paste-zone-hint { color: var(--text-muted); font-size: 12px; margin-top: 4px; opacity: .7; }

.metric-mini {
    background: var(--bg-secondary);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 12px;
    text-align: center;
}
.metric-mini-val { font-size: 22px; font-weight: 600; color: var(--text-primary); }
.metric-mini-lbl { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

.template-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 8px 14px;
    font-size: 13px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: var(--transition);
    margin: 4px;
    white-space: nowrap;
}
.template-chip:hover {
    background: var(--bg-hover);
    border-color: var(--accent);
    color: var(--text-primary);
}

.login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 40px 20px;
}
.login-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 32px;
}

.avatar {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #10a37f, #6366f1);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 700; color: white;
    flex-shrink: 0;
}

/* ── PASTE NOTIFICATION ── */
#paste-notify {
    position: fixed;
    bottom: 90px;
    left: 50%;
    transform: translateX(-50%) translateY(20px);
    background: var(--bg-tertiary);
    border: 1px solid var(--accent);
    border-radius: var(--radius-md);
    padding: 10px 20px;
    font-size: 13px;
    color: var(--accent);
    z-index: 9999;
    opacity: 0;
    transition: all .3s ease;
    pointer-events: none;
}
#paste-notify.show {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
}

/* ── MOBILE ── */
@media (max-width: 768px) {
    :root { --sidebar-w: 0px; }
    .main .block-container { padding: 0 12px 100px !important; }
    [data-testid="stChatInput"] { left: 0 !important; }
    .greeting-grid { grid-template-columns: 1fr 1fr !important; }
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── PROGRESS ── */
.stProgress > div > div { background: var(--accent) !important; }

/* ── FORM SUBMIT ── */
[data-testid="stFormSubmitButton"] button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px 24px !important;
    border-radius: var(--radius-md) !important;
    width: 100%;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: var(--accent-hover) !important;
}

/* Audio player */
audio { filter: invert(1); border-radius: var(--radius-md); }

/* Divider */
hr { border-color: var(--border-light) !important; margin: 16px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# 3. CTRL+V PASTE — JS INJECTION
# ═══════════════════════════════════════════════════════════
def inject_paste_handler():
    """
    Ctrl+V bosilganda clipboard'dan rasm yoki faylni ushlab
    Streamlit session'ga yozadi (base64 orqali hidden input).
    """
    components.html("""
<div id="paste-notify">📋 Rasm clipboard dan qo'shildi!</div>
<input type="hidden" id="paste-data-input" />

<script>
(function() {
    // Notify helper
    function showNotify(msg) {
        var el = document.getElementById('paste-notify');
        if (!el) return;
        el.textContent = msg;
        el.classList.add('show');
        setTimeout(function() { el.classList.remove('show'); }, 2500);
    }

    // Listen paste anywhere on page
    document.addEventListener('paste', function(e) {
        var items = (e.clipboardData || window.clipboardData).items;
        if (!items) return;

        for (var i = 0; i < items.length; i++) {
            var item = items[i];

            // Image
            if (item.type.indexOf('image') !== -1) {
                var file = item.getAsFile();
                if (!file) continue;
                var reader = new FileReader();
                reader.onload = (function(f, t) {
                    return function(ev) {
                        var b64 = ev.target.result; // data:image/png;base64,...
                        // Send to Streamlit via query param trick
                        var url = new URL(window.location.href);
                        url.searchParams.set('_paste_img', encodeURIComponent(b64.substring(0, 50)));
                        // Store in sessionStorage for Streamlit component to read
                        sessionStorage.setItem('somo_paste_image', b64);
                        sessionStorage.setItem('somo_paste_type', t);
                        sessionStorage.setItem('somo_paste_name', 'clipboard_' + Date.now() + '.png');
                        showNotify('🖼 Rasm clipboard dan qo\\'shildi!');

                        // Trigger streamlit re-read by clicking hidden button
                        var btn = window.parent.document.querySelector('[data-testid="stBaseButton-secondary"][aria-label="paste_trigger"]');
                        if (btn) btn.click();
                    };
                })(file, item.type);
                reader.readAsDataURL(file);
                e.preventDefault();
                break;
            }

            // Text (url or code)
            if (item.type === 'text/plain') {
                // let browser handle normal text paste in textarea
            }
        }
    }, false);

    // Drag & drop support on paste zone
    document.addEventListener('dragover', function(e) { e.preventDefault(); });
    document.addEventListener('drop', function(e) {
        e.preventDefault();
        var files = e.dataTransfer.files;
        if (!files.length) return;
        var file = files[0];
        if (file.type.startsWith('image/')) {
            var reader = new FileReader();
            reader.onload = function(ev) {
                sessionStorage.setItem('somo_paste_image', ev.target.result);
                sessionStorage.setItem('somo_paste_type', file.type);
                sessionStorage.setItem('somo_paste_name', file.name);
                showNotify('🖼 Rasm qo\\'shildi: ' + file.name);
            };
            reader.readAsDataURL(file);
        }
    });
})();
</script>
""", height=0)

# ═══════════════════════════════════════════════════════════
# 4. BAZA VA AI ULANISH
# ═══════════════════════════════════════════════════════════
@st.cache_resource
def get_connections():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], scope
        )
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        user_sheet = ss.sheet1
        chat_sheet = ss.worksheet("ChatHistory")
        try:
            fb_sheet = ss.worksheet("Letters")
        except Exception:
            fb_sheet = ss.add_worksheet(title="Letters", rows="1000", cols="10")
            fb_sheet.append_row(["Timestamp","Username","Rating","Category","Message","Email","Status"])
        return user_sheet, chat_sheet, fb_sheet
    except Exception as e:
        st.error(f"❌ Baza xatosi: {e}")
        return None, None, None

@st.cache_resource
def get_groq_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        return None

@st.cache_resource
def get_gemini():
    try:
        import google.generativeai as genai
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel("gemini-2.0-flash")
    except Exception:
        return None

user_db, chat_db, feedback_db = get_connections()
groq_client  = get_groq_client()
gemini_model = get_gemini()

# ═══════════════════════════════════════════════════════════
# 5. YORDAMCHI FUNKSIYALAR
# ═══════════════════════════════════════════════════════════
def get_file_emoji(filename):
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    return {
        "pdf":"📄","docx":"📝","doc":"📝","txt":"📃","csv":"📊",
        "xlsx":"📊","xls":"📊","json":"🔧","py":"🐍","js":"🟨",
        "html":"🌐","css":"🎨","ts":"🔷","jsx":"⚛️","tsx":"⚛️",
        "java":"☕","cpp":"⚙️","c":"⚙️","png":"🖼","jpg":"🖼",
        "jpeg":"🖼","webp":"🖼","gif":"🎞","svg":"🎨","md":"📋",
        "yaml":"🔧","xml":"🔧","sh":"💻","go":"🐹","rs":"🦀",
        "rb":"💎","php":"🐘","swift":"🍎","kt":"📱","sql":"🗃",
        "mp3":"🎵","wav":"🎵","m4a":"🎵","ogg":"🎵",
    }.get(ext, "📎")

def is_image_file(f):
    return getattr(f, "type", "") in ["image/jpeg","image/jpg","image/png","image/webp","image/gif"]

def is_pdf_file(f):
    return getattr(f, "type", "") == "application/pdf"

def is_docx_file(f):
    return "wordprocessingml" in getattr(f, "type", "") or \
           getattr(f, "name", "").endswith((".docx", ".doc"))

def get_image_media_type(f):
    return {
        "image/jpeg":"image/jpeg","image/jpg":"image/jpeg",
        "image/png":"image/png","image/webp":"image/webp","image/gif":"image/gif",
    }.get(getattr(f, "type", ""), "image/png")

def process_text_file(file_bytes, filename, mime=""):
    """Kod, CSV, JSON uchun lokal matn chiqarish"""
    try:
        name_lower = filename.lower()
        if name_lower.endswith(".csv") or mime == "text/csv":
            return "CSV fayl:\n" + file_bytes.decode("utf-8", errors="ignore")[:6000]
        elif name_lower.endswith(".json"):
            return "JSON:\n" + file_bytes.decode("utf-8", errors="ignore")[:6000]
        elif name_lower.endswith(".xlsx") or name_lower.endswith(".xls"):
            return f"Excel fayl: {filename}"
        elif any(name_lower.endswith(ext) for ext in [
            ".py",".js",".ts",".jsx",".tsx",".html",".css",".md",".txt",
            ".java",".cpp",".c",".go",".rs",".sh",".yaml",".xml",".sql",
            ".kt",".rb",".php",".swift",".r",".toml",".env",".gitignore"
        ]):
            return file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        pass
    return ""

def extract_code_blocks(text):
    return re.findall(r"```(\w*)\n?(.*?)```", text, re.DOTALL)

# ═══════════════════════════════════════════════════════════
# 6. GEMINI READERS
# ═══════════════════════════════════════════════════════════
def gemini_read_image(prompt, b64_str, media_type="image/png"):
    if not gemini_model:
        return None
    try:
        import google.generativeai as genai
        raw = base64.b64decode(b64_str) if not b64_str.startswith("data:") else \
              base64.b64decode(b64_str.split(",", 1)[1])
        part = {"mime_type": media_type, "data": raw}
        resp = gemini_model.generate_content([prompt, part])
        return resp.text
    except Exception as e:
        return None

def gemini_read_pdf(prompt, file_bytes):
    if not gemini_model:
        return None
    try:
        part = {"mime_type": "application/pdf", "data": file_bytes}
        resp = gemini_model.generate_content([prompt, part])
        return resp.text
    except Exception:
        return None

def gemini_read_docx(prompt, file_bytes):
    if not gemini_model:
        return None
    try:
        text = mammoth.extract_raw_text(io.BytesIO(file_bytes)).value
        if text.strip():
            resp = gemini_model.generate_content(
                [f"{prompt}\n\nHujjat matni:\n{text[:10000]}"]
            )
            return resp.text
    except Exception:
        pass
    return None

# ═══════════════════════════════════════════════════════════
# 7. GROQ FUNCTIONS
# ═══════════════════════════════════════════════════════════
def groq_chat(messages, model, temperature=0.6, max_tokens=4096):
    if not groq_client:
        return "❌ Groq AI mavjud emas."
    try:
        resp = groq_client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ Groq xatosi: {e}"

def groq_whisper(audio_bytes, filename="audio.wav"):
    if not groq_client:
        return None
    try:
        transcription = groq_client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model="whisper-large-v3",
        )
        return transcription.text
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════
# 8. FILE CREATION ENGINE
# ═══════════════════════════════════════════════════════════
def make_excel(ai_response, ts_safe):
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Somo AI"

        csv_match   = re.search(r"```csv\n?(.*?)```", ai_response, re.DOTALL)
        table_match = re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+\n((\|.+\|\n?)+)", ai_response)

        rows = []
        if csv_match:
            rows = list(csv.reader(io.StringIO(csv_match.group(1).strip())))
        elif table_match:
            for line in table_match.group(0).strip().split("\n"):
                if "---" not in line:
                    cells = [c.strip() for c in line.strip("|").split("|")]
                    if any(cells):
                        rows.append(cells)
        if not rows:
            return None

        hdr_fill = PatternFill("solid", fgColor="10A37F")
        hdr_font = Font(bold=True, color="FFFFFF", size=12, name="Calibri")
        alt_fill = PatternFill("solid", fgColor="F0FDF9")
        b_side   = Side(style="thin", color="D1FAE5")
        b_all    = Border(left=b_side, right=b_side, top=b_side, bottom=b_side)
        center   = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r_i, row in enumerate(rows, 1):
            for c_i, val in enumerate(row, 1):
                cell = ws.cell(row=r_i, column=c_i, value=val)
                cell.border    = b_all
                cell.alignment = center
                if r_i == 1:
                    cell.fill = hdr_fill
                    cell.font = hdr_font
                else:
                    cell.fill = alt_fill if r_i % 2 == 0 else PatternFill()
                    cell.font = Font(size=11, name="Calibri")

        for col in ws.columns:
            ml = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(ml + 4, 45)
        for row in ws.iter_rows():
            ws.row_dimensions[row[0].row].height = 24

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None


def make_pptx(ai_response, ts_safe):
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN

        prs = Presentation()
        prs.slide_width  = Inches(13.33)
        prs.slide_height = Inches(7.5)

        C_DARK   = RGBColor(0x1A, 0x1A, 0x2E)
        C_GREEN  = RGBColor(0x10, 0xA3, 0x7F)
        C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
        C_GRAY   = RGBColor(0xEC, 0xEC, 0xEC)
        C_ACCENT = RGBColor(0x63, 0x66, 0xF1)
        C_BG     = RGBColor(0xF8, 0xFD, 0xFC)

        COLORS = [C_GREEN, C_ACCENT, RGBColor(0xF5,0x9E,0x0B),
                  RGBColor(0xEC,0x48,0x99), RGBColor(0x06,0xB6,0xD4)]

        def rect(sl, l, t, w, h, c):
            s = sl.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
            s.fill.solid(); s.fill.fore_color.rgb = c
            s.line.fill.background()
            return s

        def tb(sl, txt, l, t, w, h, sz=22, bold=False, c=None, align=PP_ALIGN.LEFT, italic=False):
            b = sl.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
            f = b.text_frame; f.word_wrap = True
            p = f.paragraphs[0]; p.alignment = align
            r = p.add_run(); r.text = txt
            r.font.size = Pt(sz); r.font.bold = bold; r.font.italic = italic
            r.font.color.rgb = c or C_DARK
            return b

        # Parse slides
        lines = ai_response.strip().split("\n")
        slides_data, cur = [], {"title": "", "bullets": []}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if re.match(r"^#{1,3}\s+", line):
                if cur["title"] or cur["bullets"]:
                    slides_data.append(cur)
                cur = {"title": re.sub(r"^#{1,3}\s+", "", line).strip(), "bullets": []}
            elif re.match(r"^(\d+\.|[-*•►▸])\s+", line):
                cur["bullets"].append(re.sub(r"^(\d+\.|[-*•►▸])\s+", "", line).strip())
            elif re.match(r"^\*\*(.+)\*\*$", line):
                if cur["title"] or cur["bullets"]:
                    slides_data.append(cur)
                cur = {"title": re.sub(r"\*\*", "", line).strip(), "bullets": []}
            elif not line.startswith("```"):
                cur["bullets"].append(line)
        if cur["title"] or cur["bullets"]:
            slides_data.append(cur)

        if len(slides_data) < 2:
            chunks = [l.strip() for l in lines if l.strip() and not l.startswith("```")]
            slides_data = [{"title": chunks[0] if chunks else "Somo AI", "bullets": chunks[1:3]}]
            rest = chunks[3:]
            for i in range(0, len(rest), 4):
                block = rest[i:i+4]
                if block:
                    slides_data.append({"title": f"Qism {i//4+1}", "bullets": block})

        blank = prs.slide_layouts[6]

        # Title slide
        first = slides_data[0]
        sl = prs.slides.add_slide(blank)
        rect(sl, 0, 0, 13.33, 7.5, C_DARK)
        rect(sl, 0, 0, 0.08, 7.5, C_GREEN)
        rect(sl, 0, 5.8, 13.33, 1.7, RGBColor(0x11,0x11,0x22))
        rect(sl, 11.5, 0.3, 1.6, 1.6, C_GREEN)
        rect(sl, 0.3, 1.0, 8.0, 0.06, C_GREEN)
        tb(sl, "✦", 11.55, 0.35, 1.5, 1.5, sz=40, bold=True, c=C_DARK, align=PP_ALIGN.CENTER)
        tb(sl, first["title"] or "Somo AI", 0.5, 1.5, 12.3, 2.5, sz=46, bold=True, c=C_WHITE, align=PP_ALIGN.LEFT)
        subtitle = first["bullets"][0] if first["bullets"] else "Powered by Somo AI"
        tb(sl, subtitle, 0.5, 4.0, 11.0, 1.2, sz=22, c=RGBColor(0x94,0xA3,0xB8), italic=True)
        tb(sl, "SOMO AI  ·  " + datetime.now().strftime("%Y"), 0.5, 6.1, 8.0, 0.6, sz=13, c=RGBColor(0x6B,0x72,0x80))

        # Content slides
        for idx, sd in enumerate(slides_data[1:], 1):
            sl   = prs.slides.add_slide(blank)
            acc  = COLORS[idx % len(COLORS)]
            rect(sl, 0, 0, 13.33, 7.5, C_BG)
            rect(sl, 0, 0, 0.08, 7.5, acc)
            rect(sl, 0.08, 0, 13.25, 1.5, RGBColor(0xF0,0xFD,0xFA))
            rect(sl, 0.08, 1.42, 13.25, 0.05, acc)
            rect(sl, 12.0, 0.2, 1.1, 1.1, acc)
            tb(sl, str(idx), 12.05, 0.23, 1.0, 1.0, sz=30, bold=True, c=C_WHITE, align=PP_ALIGN.CENTER)
            tb(sl, sd["title"] or f"Slayd {idx}", 0.3, 0.18, 11.5, 1.2, sz=34, bold=True, c=C_DARK)

            bullets = sd["bullets"][:7]
            if bullets:
                y0    = 1.65
                ystep = min(0.76, 5.4 / max(len(bullets), 1))
                bh    = ystep * 0.88
                for bi, bul in enumerate(bullets):
                    rect(sl, 0.28, y0 + bi*ystep + 0.18, 0.09, 0.32, acc)
                    clean  = re.sub(r"^\*\*(.+)\*\*", r"\1", bul)
                    is_b   = bul.startswith("**") and bul.endswith("**")
                    tb(sl, clean, 0.52, y0 + bi*ystep, 12.5, bh, sz=20, bold=is_b, c=C_DARK)

            rect(sl, 0, 7.18, 13.33, 0.32, RGBColor(0xF0,0xFD,0xFA))
            tb(sl, "✦ Somo AI", 0.3, 7.2, 4.0, 0.25, sz=11, c=RGBColor(0x9C,0xA3,0xAF))
            tb(sl, f"{idx}/{len(slides_data)-1}", 12.0, 7.2, 1.0, 0.25, sz=11, c=RGBColor(0x9C,0xA3,0xAF), align=PP_ALIGN.RIGHT)

        # End slide
        sl = prs.slides.add_slide(blank)
        rect(sl, 0, 0, 13.33, 7.5, C_DARK)
        rect(sl, 0, 3.0, 13.33, 0.06, C_GREEN)
        rect(sl, 0, 4.44, 13.33, 0.06, C_GREEN)
        tb(sl, "✅ Taqdimot yakunlandi", 0.5, 3.15, 12.3, 1.2, sz=42, bold=True, c=C_WHITE, align=PP_ALIGN.CENTER)
        tb(sl, "✦ Somo AI  ·  Groq + Gemini", 0.5, 5.0, 12.3, 0.7, sz=18, c=RGBColor(0x6B,0x72,0x80), align=PP_ALIGN.CENTER)

        buf = io.BytesIO()
        prs.save(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None


def make_word(ai_response, ts_safe):
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches

        doc = Document()
        for sec in doc.sections:
            sec.top_margin    = Inches(1)
            sec.bottom_margin = Inches(1)
            sec.left_margin   = Inches(1.25)
            sec.right_margin  = Inches(1.25)

        lines = ai_response.strip().split("\n")
        in_code, code_buf = False, []

        for line in lines:
            s = line.strip()
            if s.startswith("```"):
                if not in_code:
                    in_code = True; code_buf = []
                else:
                    in_code = False
                    p = doc.add_paragraph()
                    p.paragraph_format.left_indent = Inches(0.3)
                    run = p.add_run("\n".join(code_buf))
                    run.font.name = "Courier New"; run.font.size = Pt(10)
                    run.font.color.rgb = RGBColor(0x10,0xA3,0x7F)
                continue
            if in_code:
                code_buf.append(line); continue
            if not s:
                doc.add_paragraph(); continue

            if   re.match(r"^# ",   s):
                h = doc.add_heading(s[2:], 1)
                if h.runs: h.runs[0].font.color.rgb = RGBColor(0x10,0xA3,0x7F)
            elif re.match(r"^## ",  s):
                h = doc.add_heading(s[3:], 2)
                if h.runs: h.runs[0].font.color.rgb = RGBColor(0x63,0x66,0xF1)
            elif re.match(r"^### ", s):
                h = doc.add_heading(s[4:], 3)
                if h.runs: h.runs[0].font.color.rgb = RGBColor(0x8B,0x5C,0xF6)
            elif re.match(r"^[-*•►▸]\s+", s):
                p = doc.add_paragraph(style="List Bullet")
                _fmt_run(p, re.sub(r"^[-*•►▸]\s+", "", s))
            elif re.match(r"^\d+\.\s+", s):
                p = doc.add_paragraph(style="List Number")
                _fmt_run(p, re.sub(r"^\d+\.\s+", "", s))
            else:
                p = doc.add_paragraph(); _fmt_run(p, s)

        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        return buf.read()
    except Exception:
        return None


def _fmt_run(paragraph, text):
    from docx.shared import RGBColor
    for part in re.split(r"(\*\*.*?\*\*|\*.*?\*)", text):
        if part.startswith("**") and part.endswith("**"):
            r = paragraph.add_run(part[2:-2]); r.bold = True
            r.font.color.rgb = RGBColor(0x0F,0x17,0x2A)
        elif part.startswith("*") and part.endswith("*"):
            r = paragraph.add_run(part[1:-1]); r.italic = True
        else:
            paragraph.add_run(part)


def offer_downloads(ai_response, ts):
    """AI javobiga ko'ra yuklab olish tugmalarini chiqarish"""
    ts_safe = ts.replace(":", "-").replace(" ", "_")
    blocks  = extract_code_blocks(ai_response)
    rl      = ai_response.lower()

    # ── PPTX
    pptx_kw   = ["slayd","taqdimot","prezentatsiya","slide","presentation","powerpoint","pptx"]
    has_heads = len(re.findall(r"^#{1,3}\s+", ai_response, re.MULTILINE)) >= 3
    if any(k in rl for k in pptx_kw) or has_heads:
        data = make_pptx(ai_response, ts_safe)
        if data:
            st.markdown('<div class="dl-card"><div class="dl-card-title">📊 PowerPoint Taqdimot</div></div>',
                        unsafe_allow_html=True)
            st.download_button("⬇️ PPTX yuklab olish", data,
                               f"somo_{ts_safe}.pptx",
                               "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                               key=f"pptx_{ts_safe}", use_container_width=True)

    # ── EXCEL
    xl_kw     = ["jadval","excel","xlsx","table","csv","statistika","ro'yxat","hisobot","список"]
    has_tbl   = bool(re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+", ai_response))
    has_csv   = bool(re.search(r"```csv", ai_response))
    if any(k in rl for k in xl_kw) or has_tbl or has_csv:
        data = make_excel(ai_response, ts_safe)
        if data:
            st.markdown('<div class="dl-card"><div class="dl-card-title">📊 Excel Jadval</div></div>',
                        unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("⬇️ Excel (.xlsx)", data,
                                   f"somo_{ts_safe}.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   key=f"xl_{ts_safe}", use_container_width=True)
            # CSV
            rows = []
            cm = re.search(r"```csv\n?(.*?)```", ai_response, re.DOTALL)
            tm = re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+\n((\|.+\|\n?)+)", ai_response)
            if cm:
                rows = list(csv.reader(io.StringIO(cm.group(1).strip())))
            elif tm:
                for l in tm.group(0).strip().split("\n"):
                    if "---" not in l:
                        cells = [c.strip() for c in l.strip("|").split("|")]
                        if any(cells): rows.append(cells)
            if rows:
                cb = io.StringIO()
                csv.writer(cb).writerows(rows)
                with c2:
                    st.download_button("⬇️ CSV", cb.getvalue().encode(),
                                       f"somo_{ts_safe}.csv", "text/csv",
                                       key=f"csv_{ts_safe}", use_container_width=True)

    # ── WORD
    doc_kw = ["hujjat","word","docx","maqola","xat","rezyume","resume",
              "shartnoma","tavsif","insho","referat","hisobot"]
    pptx_kw_check = ["slayd","taqdimot","prezentatsiya","slide","presentation"]
    if any(k in rl for k in doc_kw) and not any(k in rl for k in pptx_kw_check):
        data = make_word(ai_response, ts_safe)
        if data:
            st.markdown('<div class="dl-card"><div class="dl-card-title">📝 Word Hujjat</div></div>',
                        unsafe_allow_html=True)
            st.download_button("⬇️ Word (.docx)", data,
                               f"somo_{ts_safe}.docx",
                               "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                               key=f"docx_{ts_safe}", use_container_width=True)

    # ── SVG
    svg_bl = [(l, c) for l, c in blocks if l.lower() == "svg" or c.strip().startswith("<svg")]
    for i, (_, svg) in enumerate(svg_bl):
        st.markdown('<div class="dl-card"><div class="dl-card-title">🎨 SVG Rasm</div></div>',
                    unsafe_allow_html=True)
        st.markdown(svg.strip(), unsafe_allow_html=True)
        st.download_button(f"⬇️ rasm_{i}.svg", svg.strip().encode(),
                           f"somo_{ts_safe}_{i}.svg", "image/svg+xml",
                           key=f"svg_{ts_safe}_{i}", use_container_width=True)

    # ── HTML
    html_bl = [(l, c) for l, c in blocks if l.lower() == "html"]
    for i, (_, code) in enumerate(html_bl):
        st.markdown('<div class="dl-card"><div class="dl-card-title">🌐 HTML Sahifa</div></div>',
                    unsafe_allow_html=True)
        with st.expander(f"👁 HTML ko'rish #{i+1}", expanded=True):
            components.html(code.strip(), height=420, scrolling=True)
        st.download_button(f"⬇️ sahifa_{i}.html", code.strip().encode(),
                           f"somo_{ts_safe}_{i}.html", "text/html",
                           key=f"html_{ts_safe}_{i}", use_container_width=True)

    # ── CODE
    ext_map = {
        "python":"py","py":"py","javascript":"js","js":"js",
        "typescript":"ts","ts":"ts","css":"css","json":"json",
        "sql":"sql","bash":"sh","shell":"sh","sh":"sh",
        "yaml":"yaml","xml":"xml","markdown":"md","md":"md",
        "jsx":"jsx","tsx":"tsx","java":"java","cpp":"cpp",
        "c":"c","rust":"rs","go":"go","php":"php","ruby":"rb",
        "swift":"swift","kotlin":"kt","r":"r","txt":"txt",
    }
    skip = {"html","svg","csv",""}
    code_others = [(l, c) for l, c in blocks if l.lower() not in skip]
    if code_others:
        st.markdown('<div class="dl-card"><div class="dl-card-title">💾 Kod Fayllar</div></div>',
                    unsafe_allow_html=True)
        cols = st.columns(min(len(code_others), 3))
        for i, (lang, code) in enumerate(code_others):
            ext   = ext_map.get(lang.strip().lower(), "txt")
            fname = f"somo_{ts_safe}_{i}.{ext}"
            with cols[i % len(cols)]:
                st.download_button(
                    f"{get_file_emoji(fname)} .{ext}",
                    code.strip().encode(), fname, "text/plain",
                    key=f"code_{ts_safe}_{i}", use_container_width=True
                )

# ═══════════════════════════════════════════════════════════
# 9. TEMPLATES
# ═══════════════════════════════════════════════════════════
TEMPLATES = {
    "💼 Biznes": [
        {"icon":"📊","title":"Biznes Reja","prompt":"[kompaniya] uchun professional biznes reja:\n- Ijroiya xulosasi\n- Bozor tahlili\n- Marketing strategiyasi\n- Moliyaviy reja\n- 5 yillik prognoz"},
        {"icon":"📈","title":"Marketing Reja","prompt":"[mahsulot] uchun digital marketing strategiya:\n- Target auditoriya\n- SMM rejasi\n- SEO strategiya\n- Byudjet\n- KPI"},
        {"icon":"💼","title":"Taklifnoma","prompt":"[mijoz] uchun biznes taklifnoma:\n- Muammo\n- Yechim\n- Narxlar\n- Garantiya\n- Aloqa"},
        {"icon":"📋","title":"SWOT Tahlil","prompt":"[kompaniya/loyiha] uchun batafsil SWOT tahlil jadvalini yarat"},
    ],
    "💻 Dasturlash": [
        {"icon":"🐍","title":"Python Kod","prompt":"Python'da [funksiya] uchun kod yoz:\n- Type hints\n- Docstring\n- Error handling\n- Test misollari"},
        {"icon":"🌐","title":"Veb Sahifa","prompt":"[sahifa nomi] uchun zamonaviy HTML/CSS/JS sahifa:\n- Responsive\n- Dark mode\n- Animatsiyalar"},
        {"icon":"🔌","title":"API Integratsiya","prompt":"[til]da [API] bilan integratsiya:\n- Auth\n- CRUD\n- Error handling\n- Docs"},
        {"icon":"🗃","title":"SQL So'rovlar","prompt":"[jadval strukturasi] uchun SQL so'rovlar:\n- SELECT\n- JOIN\n- Aggregation\n- Indexes"},
    ],
    "📚 Ta'lim": [
        {"icon":"📖","title":"Dars Rejasi","prompt":"[mavzu] bo'yicha dars rejasi:\n- Maqsadlar\n- Kirish 10 daqiqa\n- Asosiy qism 30 daqiqa\n- Amaliy 15 daqiqa\n- Vazifa"},
        {"icon":"📝","title":"Test Savollar","prompt":"[mavzu] bo'yicha 20 ta test savol:\n- 4 variant\n- To'g'ri javob\n- Qiyinlik darajasi"},
        {"icon":"🎯","title":"O'quv Reja","prompt":"[soha] bo'yicha 3 oylik o'quv dasturi:\n- Haftalik jadval\n- Resurslar\n- Baholash"},
    ],
    "✍️ Kontent": [
        {"icon":"📄","title":"Rezyume","prompt":"[kasb] uchun professional CV:\n- Kasbiy maqsad\n- Tajriba\n- Ta'lim\n- Ko'nikmalar\n- Sertifikatlar"},
        {"icon":"✉️","title":"Motivatsion Xat","prompt":"[kompaniya] ga [lavozim] uchun motivatsion xat"},
        {"icon":"📰","title":"Blog Post","prompt":"[mavzu] haqida SEO optimizatsiya qilingan blog post:\n- Sarlavha\n- Kirish\n- Asosiy qismlar\n- Xulosa"},
        {"icon":"📣","title":"Ijtimoiy Tarmoq","prompt":"[mahsulot/xizmat] uchun Instagram, Telegram va LinkedIn uchun post matnlari"},
    ],
}

# ═══════════════════════════════════════════════════════════
# 10. SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    su = cookies.get("somo_session")
    if su and user_db:
        try:
            recs = user_db.get_all_records()
            ud   = next((r for r in recs if str(r.get("username","")) == su), None)
            if ud and str(ud.get("status","")).lower() == "active":
                st.session_state.update({
                    "username":   su,
                    "logged_in":  True,
                    "login_time": datetime.now(),
                })
            else:
                st.session_state.logged_in = False
        except Exception:
            st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

def do_logout():
    try:
        cookies["somo_session"] = ""; cookies.save()
    except Exception:
        pass
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state.logged_in = False
    st.rerun()

# ═══════════════════════════════════════════════════════════
# 11. LOGIN PAGE
# ═══════════════════════════════════════════════════════════
if not st.session_state.logged_in:

    # Inject paste handler (for login page too)
    inject_paste_handler()

    st.markdown("""
    <div style="text-align:center; padding: 60px 20px 32px;">
        <div style="font-size:40px; margin-bottom:8px; font-weight:300; color:#ececec; letter-spacing:-1px;">
            ✦ Somo <span style="color:#10a37f;">AI</span>
        </div>
        <div style="color:#8e8ea0; font-size:15px; font-weight:300;">
            Groq + Gemini · Kelajak texnologiyalari
        </div>
    </div>
    """, unsafe_allow_html=True)

    # API status
    g_st  = ("✅ Ulangan", "#10a37f") if groq_client  else ("❌ Xato", "#ef4444")
    gm_st = ("✅ Ulangan", "#10a37f") if gemini_model else ("❌ Xato", "#ef4444")
    st.markdown(f"""
    <div style="display:flex; gap:12px; justify-content:center; margin-bottom:32px; flex-wrap:wrap;">
        <div style="background:#2f2f2f; border:1px solid #3a3a3a; border-radius:10px;
                    padding:10px 20px; text-align:center; min-width:160px;">
            <div style="font-size:12px; color:#8e8ea0; margin-bottom:4px;">🟠 Groq AI</div>
            <div style="font-size:13px; font-weight:600; color:{g_st[1]};">{g_st[0]}</div>
            <div style="font-size:11px; color:#6b7280;">Chat · Whisper</div>
        </div>
        <div style="background:#2f2f2f; border:1px solid #3a3a3a; border-radius:10px;
                    padding:10px 20px; text-align:center; min-width:160px;">
            <div style="font-size:12px; color:#8e8ea0; margin-bottom:4px;">🔵 Gemini Flash</div>
            <div style="font-size:13px; font-weight:600; color:{gm_st[1]};">{gm_st[0]}</div>
            <div style="font-size:11px; color:#6b7280;">Vision · PDF · DOCX</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        t1, t2, t3 = st.tabs(["Kirish", "Ro'yxat", "Haqida"])

        with t1:
            with st.form("lf"):
                st.markdown("#### Hisobingizga kiring")
                u = st.text_input("Username", placeholder="Username", label_visibility="collapsed", key="l_u")
                p = st.text_input("Parol", type="password", placeholder="Parol", label_visibility="collapsed", key="l_p")
                c1, c2 = st.columns([2, 1])
                with c1: sub = st.form_submit_button("Kirish →", use_container_width=True)
                with c2: rem = st.checkbox("Eslab", value=True)
                if sub and u and p and user_db:
                    try:
                        recs = user_db.get_all_records()
                        hp   = hashlib.sha256(p.encode()).hexdigest()
                        usr  = next((r for r in recs if str(r.get("username","")) == u and str(r.get("password","")) == hp), None)
                        if usr:
                            if str(usr.get("status","")).lower() == "blocked":
                                st.error("🚫 Hisob bloklangan")
                            else:
                                st.session_state.update({"username": u, "logged_in": True, "login_time": datetime.now()})
                                if rem:
                                    cookies["somo_session"] = u; cookies.save()
                                st.rerun()
                        else:
                            st.error("❌ Noto'g'ri ma'lumotlar")
                    except Exception as e:
                        st.error(f"❌ {e}")

        with t2:
            with st.form("rf"):
                st.markdown("#### Yangi hisob")
                nu  = st.text_input("Username", placeholder="Username (≥3)", label_visibility="collapsed", key="r_u")
                np  = st.text_input("Parol", type="password", placeholder="Parol (≥6)", label_visibility="collapsed", key="r_p")
                nc  = st.text_input("Tasdiqlash", type="password", placeholder="Qayta kiriting", label_visibility="collapsed", key="r_c")
                ag  = st.checkbox("Shartlarga roziman")
                s2  = st.form_submit_button("Hisob yaratish →", use_container_width=True)
                if s2:
                    if not ag:          st.error("❌ Shartlar")
                    elif len(nu) < 3:   st.error("❌ Username ≥ 3")
                    elif len(np) < 6:   st.error("❌ Parol ≥ 6")
                    elif np != nc:      st.error("❌ Parollar mos emas")
                    elif user_db:
                        try:
                            recs = user_db.get_all_records()
                            if any(r.get("username") == nu for r in recs):
                                st.error("❌ Username band")
                            else:
                                user_db.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active", str(datetime.now())])
                                st.success("🎉 Hisob yaratildi!")
                        except Exception as e:
                            st.error(f"❌ {e}")

        with t3:
            st.markdown("""
**✦ Somo AI v4.0 Ultra**

| AI | Vazifa |
|----|--------|
| 🟠 **Groq LLaMA 3.3 70B** | Chat, kod, hujjatlar |
| 🔵 **Gemini Flash 2.0** | Rasm, PDF, DOCX o'qish |
| 🎙 **Groq Whisper** | Audio → Matn |

**Ctrl+V** — clipboard'dan rasm qo'shish  
**Drag & Drop** — fayl tashlash  

📧 support@somoai.uz | v4.0
            """)

    st.markdown("""
    <div style="text-align:center; padding:40px 0 20px; color:#6b7280; font-size:13px;">
        © 2026 Somo AI · Barcha huquqlar himoyalangan
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════
# 12. SESSION STATE DEFAULTS
# ═══════════════════════════════════════════════════════════
DEFAULTS = {
    "messages":       [],
    "current_page":   "chat",
    "attached_files": [],   # {name, type, bytes/text/data, media_type, use_gemini}
    "total_msgs":     0,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

uname = st.session_state.username

# ═══════════════════════════════════════════════════════════
# 13. SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:

    # Logo
    st.markdown(f"""
    <div style="padding:20px 16px 12px; border-bottom:1px solid #2a2a2a;">
        <div style="font-size:20px; font-weight:600; color:#ececec; letter-spacing:-.5px;">
            ✦ Somo <span style="color:#10a37f;">AI</span>
        </div>
        <div style="font-size:11px; color:#6b7280; margin-top:2px;">v4.0 Ultra</div>
    </div>
    """, unsafe_allow_html=True)

    # New chat
    if st.button("✦  Yangi suhbat", use_container_width=True, key="new_chat"):
        st.session_state.messages       = []
        st.session_state.attached_files = []
        st.session_state.current_page   = "chat"
        st.rerun()

    # Nav
    st.markdown('<div class="sidebar-section">MENYULAR</div>', unsafe_allow_html=True)
    nav_items = [
        ("💬", "Chat",       "chat"),
        ("🎨", "Shablonlar", "templates"),
        ("💌", "Fikrlar",    "feedback"),
    ]
    for icon, label, pg in nav_items:
        active = "color:#10a37f !important; background:#1a2e29 !important;" if st.session_state.current_page == pg else ""
        if st.button(f"{icon}  {label}", use_container_width=True, key=f"nav_{pg}"):
            st.session_state.current_page = pg
            st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # AI Status
    st.markdown('<div class="sidebar-section">AI HOLATI</div>', unsafe_allow_html=True)
    g_ok  = "🟢" if groq_client  else "🔴"
    gm_ok = "🟢" if gemini_model else "🔴"
    st.markdown(f"""
    <div style="padding:0 4px; font-size:12px; color:#8e8ea0; line-height:2;">
        {g_ok} Groq — Chat · Whisper<br>
        {gm_ok} Gemini — Vision · PDF · DOCX
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Stats
    st.markdown('<div class="sidebar-section">STATISTIKA</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="metric-mini">
            <div class="metric-mini-val">{len(st.session_state.messages)}</div>
            <div class="metric-mini-lbl">Xabar</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        dur = (datetime.now() - st.session_state.login_time).seconds // 60 \
              if "login_time" in st.session_state else 0
        st.markdown(f"""
        <div class="metric-mini">
            <div class="metric-mini-val">{dur}</div>
            <div class="metric-mini-lbl">Daqiqa</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    if st.session_state.current_page == "chat":
        st.markdown('<div class="sidebar-section">SOZLAMALAR</div>', unsafe_allow_html=True)

        temperature = st.slider("Ijodkorlik", 0.0, 1.0, 0.6, 0.05, key="temp",
                                label_visibility="visible")

        model_choice = st.selectbox("Chat modeli", key="mdl", label_visibility="visible",
            options=["llama-3.3-70b-versatile","mixtral-8x7b-32768","gemma2-9b-it","llama-3.1-8b-instant"],
            format_func=lambda x: {
                "llama-3.3-70b-versatile": "LLaMA 3.3 70B ⚡",
                "mixtral-8x7b-32768":      "Mixtral 8x7B",
                "gemma2-9b-it":            "Gemma 2 9B",
                "llama-3.1-8b-instant":    "LLaMA 3.1 8B (Tez)",
            }.get(x, x)
        )

        if st.session_state.messages:
            st.download_button(
                "📥 Chat saqlash",
                json.dumps(st.session_state.messages, ensure_ascii=False, indent=2),
                f"somo_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                "application/json", use_container_width=True, key="dl_chat"
            )

        if st.button("🗑  Chatni tozalash", use_container_width=True, key="clr_chat"):
            st.session_state.messages       = []
            st.session_state.attached_files = []
            st.rerun()

    # User + Logout
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="padding: 8px 4px; display:flex; align-items:center; gap:10px;">
        <div style="width:32px; height:32px; background:linear-gradient(135deg,#10a37f,#6366f1);
                    border-radius:50%; display:flex; align-items:center; justify-content:center;
                    font-size:14px; font-weight:700; color:white; flex-shrink:0;">
            {uname[0].upper()}
        </div>
        <div>
            <div style="font-size:13px; color:#ececec; font-weight:500;">{uname}</div>
            <div style="font-size:11px; color:#10a37f;">● Aktiv</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪  Chiqish", use_container_width=True, key="logout", type="primary"):
        do_logout()

# ═══════════════════════════════════════════════════════════
# 14. PASTE HANDLER INJECTION (main area)
# ═══════════════════════════════════════════════════════════
inject_paste_handler()

# ═══════════════════════════════════════════════════════════
# 15. CHAT PAGE
# ═══════════════════════════════════════════════════════════
if st.session_state.current_page == "chat":

    # ── Welcome screen
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="somo-header">
            <div class="somo-logo">Salom, <span>{uname}</span> ✦</div>
            <div class="somo-tagline">Bugun sizga qanday yordam bera olaman?</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="greeting-grid">
            <div class="greeting-card">
                <div class="greeting-card-icon">🖼</div>
                <div class="greeting-card-title">Rasm tahlil</div>
                <div class="greeting-card-desc">Rasm yuklang yoki Ctrl+V bosing — Gemini Vision ko'radi</div>
            </div>
            <div class="greeting-card">
                <div class="greeting-card-icon">📄</div>
                <div class="greeting-card-title">PDF / DOCX</div>
                <div class="greeting-card-desc">Hujjat yuklang — Gemini jadval va rasmlarni ham tushunadi</div>
            </div>
            <div class="greeting-card">
                <div class="greeting-card-icon">📊</div>
                <div class="greeting-card-title">Taqdimot yarat</div>
                <div class="greeting-card-desc">"Taqdimot yarat" yazib yuboring — PPTX darhol tayyor</div>
            </div>
            <div class="greeting-card">
                <div class="greeting-card-icon">💻</div>
                <div class="greeting-card-title">Kod yoz</div>
                <div class="greeting-card-desc">Har qanday tilda kod, fayl sifatida yuklab olish</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick template chips
        st.markdown("""
        <div style="margin:8px 0 24px;">
            <div style="font-size:12px; color:#6b7280; margin-bottom:10px; letter-spacing:.5px;">TEZKOR SHABLONLAR</div>
        </div>
        """, unsafe_allow_html=True)

        quick = [
            "📊 Biznes reja tuz",
            "🌐 Landing page HTML",
            "📝 Rezyume yarat",
            "🐍 Python skript yoz",
            "📈 Excel jadval",
            "🎯 Taqdimot yarat",
        ]
        cols = st.columns(3)
        for i, q in enumerate(quick):
            with cols[i % 3]:
                if st.button(q, key=f"quick_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": q})
                    st.rerun()

    # ── Chat history
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            cont = m["content"]
            if isinstance(cont, list):
                for p in cont:
                    if isinstance(p, dict) and p.get("type") == "text":
                        st.markdown(p["text"])
            else:
                st.markdown(cont)

    # ── Attached files display
    if st.session_state.attached_files:
        badges = "".join(
            f'<span class="file-chip">{get_file_emoji(f["name"])} {f["name"]}'
            f'{"&nbsp;<span style=\'color:#60a5fa;font-size:10px;\'>Gemini</span>" if f.get("use_gemini") else ""}'
            f'</span>'
            for f in st.session_state.attached_files
        )
        c1, c2 = st.columns([6, 1])
        with c1:
            st.markdown(f'<div style="margin:8px 0 4px;">{badges}</div>', unsafe_allow_html=True)
        with c2:
            if st.button("✕ Tozala", key="clf_files", use_container_width=True):
                st.session_state.attached_files = []
                st.rerun()

    # ── File upload zone
    with st.expander("➕  Fayl biriktirish  ·  Ctrl+V rasm  ·  Drag & Drop", expanded=False):
        st.markdown("""
        <div class="paste-zone" id="main-drop-zone">
            <div class="greeting-card-icon">📎</div>
            <div class="paste-zone-text">Fayl yuklang yoki shu yerga tashlang</div>
            <div class="paste-zone-hint">Rasm: Ctrl+V bilan ham qo'shishingiz mumkin</div>
        </div>
        """, unsafe_allow_html=True)

        up_files = st.file_uploader(
            "Fayl tanlash",
            label_visibility="collapsed",
            type=["jpg","jpeg","png","webp","gif","pdf","docx","doc",
                  "txt","csv","xlsx","xls","json","yaml","xml","py","js",
                  "ts","jsx","tsx","html","css","md","java","cpp","c","go",
                  "rs","sh","svg","rb","php","swift","kt","r","sql","toml"],
            accept_multiple_files=True,
            key="file_uploader_main"
        )

        if up_files:
            for f in up_files:
                if any(a["name"] == f.name for a in st.session_state.attached_files):
                    continue
                f.seek(0)
                fbytes = f.read()

                if is_image_file(f):
                    b64   = base64.b64encode(fbytes).decode()
                    mtype = get_image_media_type(f)
                    st.image(fbytes, caption=f"🖼 {f.name}", width=260)
                    st.session_state.attached_files.append({
                        "name": f.name, "type": "image",
                        "bytes": fbytes, "data": b64, "media_type": mtype,
                        "use_gemini": True
                    })
                    st.success(f"✅ 🔵 Gemini Vision: {f.name}")

                elif is_pdf_file(f):
                    st.session_state.attached_files.append({
                        "name": f.name, "type": "pdf",
                        "bytes": fbytes, "use_gemini": True
                    })
                    st.success(f"✅ 🔵 Gemini PDF: {f.name} ({len(fbytes)//1024} KB)")

                elif is_docx_file(f):
                    st.session_state.attached_files.append({
                        "name": f.name, "type": "docx",
                        "bytes": fbytes, "use_gemini": True
                    })
                    st.success(f"✅ 🔵 Gemini DOCX: {f.name}")

                else:
                    txt = process_text_file(fbytes, f.name, getattr(f, "type", ""))
                    st.session_state.attached_files.append({
                        "name": f.name, "type": "text",
                        "text": txt, "use_gemini": False
                    })
                    st.success(f"✅ 🟠 Groq: {f.name}")

    # ── Audio (Whisper)
    with st.expander("🎙  Ovozli xabar — Groq Whisper", expanded=False):
        a_file = st.file_uploader("Audio", label_visibility="collapsed",
                                  type=["wav","mp3","m4a","ogg","flac","webm"],
                                  key="audio_up")
        if a_file:
            st.audio(a_file)
            if st.button("🎙 Matnga aylantirish", use_container_width=True, key="whisper_btn"):
                with st.spinner("🎙 Whisper eshityapti..."):
                    txt = groq_whisper(a_file.read(), a_file.name)
                    if txt:
                        st.success(f"✅ Natija:")
                        st.info(txt)
                        st.session_state["_whisper"] = txt
                    else:
                        st.error("❌ Audio o'qilmadi")

    # ── CHAT INPUT
    prompt = st.chat_input("✦ Xabar yuboring...", key="chat_in")

    if "_whisper" in st.session_state and st.session_state["_whisper"]:
        prompt = st.session_state.pop("_whisper")

    if prompt:
        ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        temp = st.session_state.get("temp", 0.6)
        mdl  = st.session_state.get("mdl", "llama-3.3-70b-versatile")

        gemini_files = [f for f in st.session_state.attached_files if f.get("use_gemini")]
        groq_texts   = [f for f in st.session_state.attached_files if not f.get("use_gemini")]

        # Display user message
        if st.session_state.attached_files:
            names = ", ".join(f["name"] for f in st.session_state.attached_files)
            disp  = f"📎 *[{names}]* — {prompt}"
        else:
            disp = prompt

        st.session_state.messages.append({"role": "user", "content": disp})
        with st.chat_message("user"):
            st.markdown(disp)

        # Log
        if chat_db:
            try: chat_db.append_row([ts, uname, "User", prompt[:500]])
            except Exception: pass

        # ── AI Response
        with st.chat_message("assistant"):

            final_res = None

            # ── GEMINI path (image / pdf / docx)
            if gemini_files and gemini_model:
                tag = "🔵 Gemini"
                st.markdown(f'<span class="api-pill pill-gemini">{tag}</span>', unsafe_allow_html=True)
                with st.spinner("🔵 Gemini o'qiyapti..."):
                    parts = []
                    for gf in gemini_files:
                        if gf["type"] == "image":
                            r = gemini_read_image(prompt, gf["data"], gf.get("media_type", "image/png"))
                        elif gf["type"] == "pdf":
                            r = gemini_read_pdf(prompt, gf["bytes"])
                        elif gf["type"] == "docx":
                            r = gemini_read_docx(prompt, gf["bytes"])
                        else:
                            r = None
                        if r:
                            parts.append(f"**📄 {gf['name']}:**\n\n{r}")

                    if parts:
                        final_res = "\n\n---\n\n".join(parts)
                    else:
                        st.warning("⚠️ Gemini javob bermadi, Groq bilan urinilmoqda...")

            # ── GROQ path (chat + code + text files)
            if not final_res:
                st.markdown(f'<span class="api-pill pill-groq">🟠 Groq {mdl.split("-")[0].upper()}</span>',
                            unsafe_allow_html=True)

                SYS = (
                    "Sening isming Somo AI. Seni Usmonov Sodiq yaratgan. "
                    "Sen professional, foydali yordamchi sun'iy intellektsan. "
                    "Matematikani LaTeX ($...$) da yoz. Javoblarni tuzilgan holda yoz. "
                    "FAYL YARATISH: "
                    "Taqdimot/slayd — ## sarlavhalar + bullet listlar yoz (PPTX avtomatik). "
                    "Jadval/statistika — Markdown jadval yoki ```csv yoz (Excel avtomatik). "
                    "Hujjat/rezyume/xat — to'liq formatlangan matn yoz (Word avtomatik). "
                    "HTML — ```html blokida to'liq kod yoz. "
                    "Kod — tegishli blokda to'liq ishlaydigan kod yoz. "
                    "Hech qachon faqat tushuntirma yozma — DOIM to'liq kontent yoz!"
                )
                msgs = [{"role": "system", "content": SYS}]

                if groq_texts:
                    ctx = "\n\n".join(
                        f"=== {f['name']} ===\n{f.get('text','')[:4000]}"
                        for f in groq_texts if f.get("text")
                    )
                    if ctx:
                        msgs.append({"role": "system", "content": f"Yuklangan fayllar:\n\n{ctx}"})

                for old in st.session_state.messages[-24:]:
                    role = old["role"]
                    cont = old["content"]
                    if isinstance(cont, list):
                        cont = " ".join(p.get("text","") for p in cont if isinstance(p, dict) and p.get("type")=="text")
                    msgs.append({"role": role, "content": cont})

                with st.spinner("✦ O'ylayapman..."):
                    final_res = groq_chat(msgs, mdl, temp, max_tokens=4096)

            # Show response
            if final_res:
                st.markdown(final_res)
                offer_downloads(final_res, ts)
                st.session_state.messages.append({"role": "assistant", "content": final_res})
                st.session_state.total_msgs += 1

                # Also add Groq analysis if gemini was used and there are text files too
                if gemini_files and groq_texts and groq_client:
                    ctx = "\n\n".join(f"=== {f['name']} ===\n{f.get('text','')[:3000]}" for f in groq_texts)
                    extra_msgs = [
                        {"role": "system", "content": "Gemini tahlilini va fayl matnlarini hisobga olib qo'shimcha tahlil ber."},
                        {"role": "system", "content": f"Fayl:\n{ctx}"},
                        {"role": "user",   "content": f"{prompt}\n\nGemini natijasi:\n{final_res}"}
                    ]
                    with st.spinner("🟠 Groq qo'shimcha tahlil..."):
                        extra = groq_chat(extra_msgs, mdl, temp, 2048)
                    if extra and not extra.startswith("❌"):
                        st.markdown("---")
                        st.markdown(f'<span class="api-pill pill-groq">🟠 Groq qo\'shimcha tahlil</span>', unsafe_allow_html=True)
                        st.markdown(extra)

                if chat_db:
                    try: chat_db.append_row([ts, "Somo AI", "Assistant", final_res[:500]])
                    except Exception: pass

            st.session_state.attached_files = []

# ═══════════════════════════════════════════════════════════
# 16. TEMPLATES PAGE
# ═══════════════════════════════════════════════════════════
elif st.session_state.current_page == "templates":

    st.markdown("""
    <div class="somo-header">
        <div class="somo-logo">✦ <span>Shablonlar</span></div>
        <div class="somo-tagline">Tezkor ishni boshlash uchun professional shablonlar</div>
    </div>
    """, unsafe_allow_html=True)

    cat = st.selectbox("Kategoriya", list(TEMPLATES.keys()), label_visibility="collapsed", key="tcat")

    st.markdown(f"#### {cat}")
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    items = TEMPLATES[cat]
    cols  = st.columns(2)
    for i, t in enumerate(items):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:#2f2f2f; border:1px solid #3a3a3a; border-radius:14px;
                        padding:20px; margin-bottom:12px;">
                <div style="font-size:24px; margin-bottom:8px;">{t['icon']}</div>
                <div style="font-size:15px; font-weight:600; color:#ececec; margin-bottom:8px;">{t['title']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.code(t["prompt"], language="text")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📋 Ko'chirish", key=f"cp_{cat}_{i}", use_container_width=True):
                    st.success("✅ Chatga joylashtiring!")
            with c2:
                if st.button("🚀 Ishlatish", key=f"use_{cat}_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": t["prompt"]})
                    st.session_state.current_page = "chat"
                    st.rerun()

    st.info("💡 [qavs] ichini o'z ma'lumotlaringiz bilan to'ldiring")

# ═══════════════════════════════════════════════════════════
# 17. FEEDBACK PAGE
# ═══════════════════════════════════════════════════════════
elif st.session_state.current_page == "feedback":

    st.markdown("""
    <div class="somo-header">
        <div class="somo-logo">✦ <span>Fikr-Mulohaza</span></div>
        <div class="somo-tagline">Sizning fikringiz Somo AI'ni yaxshilaydi</div>
    </div>
    """, unsafe_allow_html=True)

    _, fc, _ = st.columns([1, 2, 1])
    with fc:
        with st.form("fbf"):
            rating = st.select_slider("Baho", [1,2,3,4,5], value=5,
                                      format_func=lambda x: "⭐"*x)
            st.markdown(f"<div style='text-align:center;font-size:40px;margin:12px 0;'>{'⭐'*rating}</div>",
                        unsafe_allow_html=True)
            cat_fb = st.selectbox("Kategoriya",
                ["Umumiy fikr","Xato haqida","Yangi funksiya","Savol","Boshqa"])
            msg_fb = st.text_area("Xabar", placeholder="Fikrlaringiz...", height=130)
            eml_fb = st.text_input("Email (ixtiyoriy)", placeholder="email@example.com")
            sub_fb = st.form_submit_button("Yuborish →", use_container_width=True)

            if sub_fb:
                if not msg_fb or len(msg_fb) < 10:
                    st.error("❌ Kamida 10 ta belgi kiriting")
                elif feedback_db:
                    try:
                        feedback_db.append_row([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            uname, rating, cat_fb, msg_fb, eml_fb or "N/A", "Yangi"
                        ])
                        st.balloons()
                        st.success("✅ Rahmat! Fikringiz yuborildi.")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")
                else:
                    st.error("❌ Baza mavjud emas")

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### Statistika")
    if feedback_db:
        try:
            all_fb = feedback_db.get_all_records()
            if len(all_fb) > 1:
                c1, c2, c3 = st.columns(3)
                rtgs = [int(f.get("Rating",0)) for f in all_fb[1:] if f.get("Rating")]
                with c1: st.metric("📨 Jami", len(all_fb)-1)
                with c2: st.metric("⭐ O'rtacha", f"{sum(rtgs)/len(rtgs):.1f}" if rtgs else "—")
                with c3: st.metric("🆕 Yangi", sum(1 for f in all_fb[-20:] if f.get("Status")=="Yangi"))
            else:
                st.info("💬 Hali fikr yo'q")
        except Exception:
            st.warning("⚠️ Statistika yuklanmadi")

# ═══════════════════════════════════════════════════════════
# 18. FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center; padding:40px 0 20px; border-top:1px solid #2a2a2a;
            margin-top:60px; color:#6b7280; font-size:12px; line-height:2;">
    <div style="font-size:16px; font-weight:600; color:#ececec; margin-bottom:8px;">
        ✦ Somo AI — v4.0 Ultra
    </div>
    🟠 Groq LLaMA 3.3 · 🔵 Gemini Flash 2.0 · 🎙 Whisper<br>
    👨‍💻 Usmonov Sodiq · Davlatov Mironshoh<br>
    📧 support@somoai.uz<br>
    © 2026 Barcha huquqlar himoyalangan
</div>
""", unsafe_allow_html=True)
