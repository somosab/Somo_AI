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
    from streamlit_cookies_manager import EncryptedCookieManager
    HAS_COOKIES = True
except: HAS_COOKIES = False

# ── PAGE CONFIG ──────────────────────────────────────
st.set_page_config(
    page_title="Somo AI",
    page_icon="♾️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── COOKIES ─────────────────────────────────────────
if HAS_COOKIES:
    cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD","Somo_AI_2026_XYZ"))
    if not cookies.ready():
        st.stop()
else:
    cookies = {}

# ═══════════════════════════════════════════════════
# GLOBAL CSS
# ═══════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

:root {
  --p:    #6C5CE7;
  --p2:   #a29bfe;
  --acc:  #fd79a8;
  --acc2: #00cec9;
  --bg:   #0b0b18;
  --bg2:  #12121f;
  --gl:   rgba(255,255,255,0.05);
  --bd:   rgba(255,255,255,0.09);
  --tx:   #eeeeff;
  --txm:  rgba(238,238,255,0.45);
  --ok:   #00b894;
  --err:  #d63031;
}

* { font-family:'DM Sans',sans-serif; box-sizing:border-box; margin:0; padding:0; }

.stApp {
  background: var(--bg) !important;
  background-image:
    radial-gradient(ellipse 70% 50% at 15% 10%, rgba(108,92,231,.14) 0%, transparent 65%),
    radial-gradient(ellipse 55% 45% at 85% 85%, rgba(253,121,168,.10) 0%, transparent 60%) !important;
}

/* hide defaults */
[data-testid="stSidebarNav"], #MainMenu, footer, header { display:none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: rgba(11,11,24,.97) !important;
  border-right: 1px solid var(--bd) !important;
  backdrop-filter: blur(20px);
  width: 260px !important;
}
[data-testid="stSidebar"] * { color: var(--tx) !important; }
[data-testid="stSidebar"] section { background:transparent !important; }

div[data-testid="stSidebar"] button {
  background: var(--gl) !important;
  border: 1px solid var(--bd) !important;
  border-radius: 12px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  color: var(--tx) !important;
  padding: 10px 14px !important;
  margin: 2px 0 !important;
  width: 100% !important;
  text-align: left !important;
  transition: all .22s !important;
}
div[data-testid="stSidebar"] button:hover {
  background: linear-gradient(135deg,var(--p),var(--p2)) !important;
  border-color: transparent !important;
  transform: translateX(5px) !important;
  box-shadow: 0 4px 18px rgba(108,92,231,.4) !important;
}

/* ── Main ── */
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Login ── */
.login-outer {
  min-height:100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:40px 20px;
}
.login-box {
  width:100%; max-width:440px;
  background: var(--gl);
  border: 1px solid var(--bd);
  border-radius: 28px;
  padding: 44px 40px;
  backdrop-filter: blur(20px);
  box-shadow: 0 30px 80px rgba(0,0,0,.5);
}
.login-logo {
  text-align:center;
  margin-bottom:28px;
}
.login-logo .ico {
  font-size:64px;
  display:block;
  animation: logoPulse 3s ease-in-out infinite;
  filter: drop-shadow(0 0 24px rgba(108,92,231,.9));
}
.login-logo h1 {
  font-family:'Syne',sans-serif;
  font-size:40px; font-weight:800;
  background: linear-gradient(135deg,#fff 0%,var(--p2) 45%,var(--acc) 85%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  letter-spacing:-1.5px; line-height:1;
  margin-top:8px;
}
.login-logo p { color:var(--txm); font-size:13px; margin-top:6px; letter-spacing:2px; text-transform:uppercase; }
@keyframes logoPulse {
  0%,100%{transform:scale(1) rotate(0deg); filter:drop-shadow(0 0 24px rgba(108,92,231,.9));}
  50%     {transform:scale(1.07) rotate(4deg); filter:drop-shadow(0 0 40px rgba(253,121,168,.9));}
}

/* ── Chat layout ── */
.chat-wrap {
  display:flex;
  flex-direction:column;
  height:100vh;
  overflow:hidden;
}
.chat-topbar {
  display:flex;
  align-items:center;
  gap:14px;
  padding:14px 24px;
  background: rgba(11,11,24,.9);
  border-bottom: 1px solid var(--bd);
  backdrop-filter: blur(20px);
  flex-shrink:0;
  z-index:99;
}
.topbar-logo {
  font-size:28px;
  filter: drop-shadow(0 0 10px rgba(108,92,231,.8));
  animation: logoPulse 3s ease-in-out infinite;
}
.topbar-title {
  font-family:'Syne',sans-serif;
  font-size:20px; font-weight:700;
  background: linear-gradient(135deg,#fff,var(--p2),var(--acc));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.topbar-sub { font-size:12px; color:var(--txm); }
.topbar-right { margin-left:auto; display:flex; align-items:center; gap:10px; }

/* ── Messages ── */
.msgs-area {
  flex:1;
  overflow-y:auto;
  padding:24px 0 20px;
  scroll-behavior:smooth;
}
.msgs-inner {
  max-width:820px;
  margin:0 auto;
  padding:0 20px;
}

/* message bubbles */
.msg-row { display:flex; gap:10px; margin-bottom:18px; align-items:flex-start; }
.msg-row.user { flex-direction:row-reverse; }

.msg-avatar {
  width:34px; height:34px; border-radius:50%; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-size:15px; font-weight:700; font-family:'Syne',sans-serif;
}
.msg-avatar.ai  { background:linear-gradient(135deg,var(--p),var(--acc)); color:white; }
.msg-avatar.usr { background:linear-gradient(135deg,var(--acc2),var(--p2)); color:white; }

.msg-bubble {
  max-width:72%;
  padding:13px 17px;
  border-radius:18px;
  font-size:14px; line-height:1.65;
  color:var(--tx);
}
.msg-bubble.ai  {
  background:var(--gl);
  border:1px solid var(--bd);
  border-top-left-radius:4px;
}
.msg-bubble.usr {
  background:rgba(108,92,231,.18);
  border:1px solid rgba(108,92,231,.3);
  border-top-right-radius:4px;
}
.msg-bubble code {
  background:rgba(108,92,231,.2);
  color:var(--p2);
  border-radius:5px;
  padding:1px 5px;
  font-size:13px;
}
.msg-bubble pre {
  background:rgba(0,0,0,.4);
  border:1px solid var(--bd);
  border-radius:10px;
  padding:12px;
  overflow-x:auto;
  margin-top:8px;
}
.msg-bubble p { margin-bottom:8px; }
.msg-bubble p:last-child { margin-bottom:0; }

/* ── Typing dots ── */
.typing-dots {
  display:inline-flex; gap:5px; align-items:center;
  padding:13px 17px;
  background:var(--gl); border:1px solid var(--bd);
  border-radius:18px; border-top-left-radius:4px;
}
.td {
  width:7px; height:7px; border-radius:50%;
  animation:tdBounce 1.3s ease-in-out infinite;
}
.td1{background:var(--p2);}
.td2{background:var(--acc); animation-delay:.18s;}
.td3{background:var(--acc2); animation-delay:.36s;}
@keyframes tdBounce {
  0%,80%,100%{transform:translateY(0) scale(.7);opacity:.5;}
  40%{transform:translateY(-8px) scale(1);opacity:1;}
}

/* ── Stream cursor ── */
.scursor::after {
  content:'▋';
  animation:blink .75s infinite;
  color:var(--p2);
}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0;}}

/* ── Input bar ── */
.input-bar {
  flex-shrink:0;
  padding:14px 20px;
  background: rgba(11,11,24,.95);
  border-top:1px solid var(--bd);
  backdrop-filter:blur(20px);
}
.input-inner { max-width:820px; margin:0 auto; }

/* ── Streamlit chat input override ── */
[data-testid="stChatInput"] textarea {
  background: rgba(255,255,255,.05) !important;
  border: 1px solid var(--bd) !important;
  border-radius: 14px !important;
  color: var(--tx) !important;
  font-size:14px !important;
}
[data-testid="stChatInput"] textarea:focus {
  border-color: var(--p) !important;
  box-shadow: 0 0 0 3px rgba(108,92,231,.2) !important;
}
.stChatInputContainer {
  background:rgba(11,11,24,.95) !important;
  border-top:1px solid var(--bd) !important;
  padding:14px 20px !important;
  backdrop-filter:blur(20px) !important;
}

/* ── stChatMessage overrides (fallback) ── */
.stChatMessage {
  background:var(--gl) !important;
  border:1px solid var(--bd) !important;
  border-radius:18px !important;
  color:var(--tx) !important;
}
.stChatMessage p, .stChatMessage * { color:var(--tx) !important; }

/* ── Buttons ── */
.stButton>button {
  background:linear-gradient(135deg,var(--p),var(--p2)) !important;
  color:#fff !important; border:none !important;
  border-radius:11px !important; font-weight:600 !important;
  transition:all .25s !important;
}
.stButton>button:hover {
  transform:translateY(-2px) !important;
  box-shadow:0 8px 22px rgba(108,92,231,.45) !important;
}
.stDownloadButton>button {
  background:linear-gradient(135deg,var(--ok),var(--acc2)) !important;
  color:#fff !important; border:none !important; border-radius:11px !important; font-weight:700 !important;
}

/* ── Inputs ── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea {
  background:var(--gl) !important; border:1px solid var(--bd) !important;
  border-radius:11px !important; color:var(--tx) !important;
}
.stSelectbox>div>div { background:var(--gl) !important; border:1px solid var(--bd) !important; border-radius:11px !important; color:var(--tx) !important; }
label { color:var(--txm) !important; }
p,li,span { color:var(--tx) !important; }
h1,h2,h3,h4,h5 { font-family:'Syne',sans-serif !important; color:var(--tx) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background:var(--gl) !important; border:1px solid var(--bd) !important;
  border-radius:12px !important; padding:4px !important; gap:3px !important;
}
.stTabs [data-baseweb="tab"] {
  background:transparent !important; border-radius:9px !important;
  color:var(--txm) !important; border:none !important; font-weight:500 !important; padding:9px 16px !important;
}
.stTabs [aria-selected="true"] {
  background:linear-gradient(135deg,var(--p),var(--p2)) !important; color:#fff !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background:var(--gl) !important; border:2px dashed var(--bd) !important;
  border-radius:14px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--p);border-radius:2px;}

/* ── Sidebar user card ── */
.sb-user {
  text-align:center; padding:18px 14px; margin-bottom:14px;
  background:var(--gl); border:1px solid var(--bd); border-radius:16px;
}
.sb-av {
  width:54px; height:54px; border-radius:50%;
  background:linear-gradient(135deg,var(--p),var(--acc));
  font-family:'Syne',sans-serif; font-size:24px; font-weight:800;
  color:#fff; line-height:54px; margin:0 auto 8px;
  box-shadow:0 0 20px rgba(108,92,231,.5);
}
.sb-name{font-size:14px;font-weight:700;}
.sb-badge{
  display:inline-block; background:rgba(0,184,148,.12);
  border:1px solid rgba(0,184,148,.3); color:var(--ok) !important;
  padding:2px 10px; border-radius:20px; font-size:10px; font-weight:700; margin-top:4px;
}

/* ── Welcome cards ── */
.welcome-grid {
  display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
  gap:12px; margin-top:20px;
}
.w-card {
  background:var(--gl); border:1px solid var(--bd);
  border-radius:16px; padding:18px 14px; text-align:center;
  cursor:pointer; transition:all .28s;
}
.w-card:hover {
  border-color:var(--p); transform:translateY(-5px);
  box-shadow:0 15px 35px rgba(108,92,231,.25);
  background:rgba(108,92,231,.1);
}
.w-icon{font-size:30px;display:block;margin-bottom:8px;}
.w-title{font-size:12px;font-weight:600;color:var(--tx);}
.w-desc{font-size:11px;color:var(--txm);margin-top:3px;line-height:1.4;}

/* ── api badges ── */
.api-on{display:inline-block;background:rgba(0,184,148,.12);border:1px solid rgba(0,184,148,.3);
  color:var(--ok)!important;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600;margin:2px;}
.api-off{display:inline-block;background:rgba(214,48,49,.08);border:1px solid rgba(214,48,49,.2);
  color:var(--err)!important;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600;margin:2px;}

/* ── Toast ── */
.toast{
  background:linear-gradient(135deg,rgba(108,92,231,.85),rgba(253,121,168,.85));
  color:#fff;padding:12px 18px;border-radius:12px;font-weight:600;font-size:13px;
  border:1px solid rgba(255,255,255,.12);backdrop-filter:blur(10px);
  animation:fadeSlide .35s ease; margin:8px 0;
}
@keyframes fadeSlide{from{opacity:0;transform:translateY(-8px);}to{opacity:1;transform:translateY(0);}}

/* ── Slider ── */
.stSlider>div>div{color:var(--tx)!important;}

/* ── Mobile ── */
@media(max-width:600px){
  .msg-bubble{max-width:88%;}
  .login-box{padding:32px 22px;}
  .login-logo h1{font-size:32px;}
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# DB
# ═══════════════════════════════════════════════════
@st.cache_resource
def get_db():
    try:
        scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"],scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        us = ss.sheet1
        cs = ss.worksheet("ChatHistory")
        try: fb = ss.worksheet("Letters")
        except:
            fb = ss.add_worksheet("Letters",1000,10)
            fb.append_row(["Time","User","Rating","Cat","Msg","Email","Status"])
        return us, cs, fb
    except:
        return None, None, None

user_db, chat_db, fb_db = get_db()

# ═══════════════════════════════════════════════════
# API CLIENTS
# ═══════════════════════════════════════════════════
def _sec(*keys):
    for k in keys:
        for kk in [k, k.lower()]:
            try:
                v = st.secrets[kk]
                if v: return str(v).strip()
            except: pass
            for sec in ["api_keys","keys","secrets","env"]:
                try:
                    v = st.secrets[sec][kk]
                    if v: return str(v).strip()
                except: pass
        v = os.environ.get(k) or os.environ.get(k.lower())
        if v: return v.strip()
    return None

def init_clients():
    c, e = {}, {}
    # Groq
    try:
        k = _sec("GROQ_API_KEY")
        if k:
            from groq import Groq
            c["groq"] = Groq(api_key=k)
        else: e["groq"]="GROQ_API_KEY yo'q"
    except Exception as ex: e["groq"]=str(ex)[:60]
    # Cerebras
    try:
        k = _sec("CEREBRAS_API_KEY")
        if k:
            from cerebras.cloud.sdk import Cerebras
            c["cerebras"] = Cerebras(api_key=k)
        else: e["cerebras"]="CEREBRAS_API_KEY yo'q"
    except Exception as ex: e["cerebras"]=str(ex)[:60]
    # Gemini
    try:
        k = _sec("GEMINI_API_KEY")
        if k:
            import google.generativeai as genai
            genai.configure(api_key=k)
            c["gemini"] = genai.GenerativeModel("gemini-2.0-flash")
            c["gemini_vision"] = genai.GenerativeModel("gemini-2.0-flash")
        else: e["gemini"]="GEMINI_API_KEY yo'q"
    except Exception as ex: e["gemini"]=str(ex)[:60]
    # Mistral
    try:
        k = _sec("MISTRAL_API_KEY")
        if k:
            try:
                from mistralai import Mistral as _M
                c["mistral"] = _M(api_key=k)
            except ImportError:
                from mistralai.client import MistralClient as _MC
                c["mistral"] = _MC(api_key=k)
        else: e["mistral"]="MISTRAL_API_KEY yo'q"
    except Exception as ex: e["mistral"]=str(ex)[:60]
    # Cohere
    try:
        k = _sec("COHERE_API_KEY")
        if k:
            import cohere
            c["cohere"] = cohere.Client(k)
        else: e["cohere"]="COHERE_API_KEY yo'q"
    except Exception as ex: e["cohere"]=str(ex)[:60]
    # OpenRouter
    try:
        k = _sec("OPENROUTER_API_KEY")
        if k:
            try:
                from openai import OpenAI
                c["openrouter"] = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=k)
            except ImportError:
                c["openrouter"] = {"type":"req","key":k}
            c["or_key"] = k
        else: e["openrouter"]="OPENROUTER_API_KEY yo'q"
    except Exception as ex: e["openrouter"]=str(ex)[:60]
    # Stability (rasm)
    try:
        k = _sec("STABILITY_API_KEY","STABILITY_KEY")
        if k: c["stability"]=k
    except: pass
    # Together (rasm)
    try:
        k = _sec("TOGETHER_API_KEY")
        if k: c["together"]=k
    except: pass
    return c, e

if "ai_c" not in st.session_state:
    _c, _e = init_clients()
    st.session_state.ai_c = _c
    st.session_state.ai_e = _e

AC = st.session_state.ai_c
AE = st.session_state.ai_e

# ═══════════════════════════════════════════════════
# AI CALL
# ═══════════════════════════════════════════════════
PMAP = {
    "chat":  ["cerebras","groq","mistral","cohere","gemini","openrouter"],
    "code":  ["cerebras","groq","mistral","openrouter","gemini"],
    "excel": ["gemini","mistral","groq","cerebras","openrouter"],
    "word":  ["gemini","mistral","groq","cerebras","openrouter"],
    "html":  ["openrouter","cerebras","groq","mistral","gemini"],
    "csv":   ["cerebras","groq","mistral","gemini","openrouter"],
}

def best(task="chat"):
    for p in PMAP.get(task,["groq","gemini"]):
        if p in AC: return p
    for p in ["cerebras","groq","gemini","mistral","cohere","openrouter"]:
        if p in AC: return p
    return None

def call_ai(messages, temp=0.6, max_tok=3500, provider=None):
    if not provider: provider = best()

    def _cerebras(m,t,k):
        r = AC["cerebras"].chat.completions.create(messages=m,model="llama-3.3-70b",temperature=min(t,1.0),max_tokens=k)
        return r.choices[0].message.content
    def _groq(m,t,k):
        r = AC["groq"].chat.completions.create(messages=m,model="llama-3.3-70b-versatile",temperature=t,max_tokens=k)
        return r.choices[0].message.content
    def _gemini(m,t,k):
        parts = [f"[{x['role'].upper()}]: {x['content']}" for x in m]
        return AC["gemini"].generate_content("\n\n".join(parts)).text
    def _mistral(m,t,k):
        cl = AC["mistral"]
        try:
            r = cl.chat.complete(model="mistral-small-latest",messages=m,temperature=t,max_tokens=k)
        except AttributeError:
            from mistralai.models.chat_completion import ChatMessage
            mm=[ChatMessage(role=x["role"] if x["role"]!="system" else "user",content=x["content"]) for x in m]
            r = cl.chat(model="mistral-small-latest",messages=mm,temperature=t,max_tokens=k)
        return r.choices[0].message.content
    def _cohere(m,t,k):
        sys_=next((x["content"] for x in m if x["role"]=="system"),"")
        usr=next((x["content"] for x in reversed(m) if x["role"]=="user"),"")
        return AC["cohere"].chat(model="command-r-plus",message=usr,preamble=sys_,temperature=t,max_tokens=k).text
    def _or(m,t,k):
        cl=AC["openrouter"]
        if isinstance(cl,dict):
            r=requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization":f"Bearer {cl['key']}","Content-Type":"application/json"},
                json={"model":"meta-llama/llama-3.1-8b-instruct:free","messages":m,"temperature":t,"max_tokens":k},timeout=30)
            r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]
        r=cl.chat.completions.create(model="meta-llama/llama-3.1-8b-instruct:free",messages=m,temperature=t,max_tokens=k,
            extra_headers={"HTTP-Referer":"https://somo-ai.streamlit.app","X-Title":"Somo AI"})
        return r.choices[0].message.content

    CALLERS = {"cerebras":_cerebras,"groq":_groq,"gemini":_gemini,"mistral":_mistral,"cohere":_cohere,"openrouter":_or}

    if provider and provider in AC and provider in CALLERS:
        try: return CALLERS[provider](messages,temp,max_tok)
        except: pass
    for p,fn in CALLERS.items():
        if p!=provider and p in AC:
            try: return fn(messages,temp,max_tok)
            except: continue
    return "❌ Hech qanday AI ulanmagan! Streamlit Secrets'ga GROQ_API_KEY yoki GEMINI_API_KEY qo'shing."

# ═══════════════════════════════════════════════════
# IMAGE GENERATION (Pollinations — API keysiz, bepul)
# ═══════════════════════════════════════════════════
def gen_image(prompt):
    try:
        enc = requests.utils.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{enc}?width=1024&height=1024&nologo=true&enhance=true&seed={int(time.time())}"
        r = requests.get(url, timeout=70)
        if r.status_code==200 and len(r.content)>5000:
            return r.content,"image/jpeg"
    except: pass
    if "stability" in AC:
        try:
            r=requests.post("https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={"Authorization":f"Bearer {AC['stability']}","Content-Type":"application/json"},
                json={"text_prompts":[{"text":prompt,"weight":1}],"cfg_scale":7,"height":1024,"width":1024,"steps":30,"samples":1},timeout=60)
            if r.status_code==200:
                return base64.b64decode(r.json()["artifacts"][0]["base64"]),"image/png"
        except: pass
    return None,None

# ═══════════════════════════════════════════════════
# IMAGE ANALYSIS
# ═══════════════════════════════════════════════════
def analyze_image(img_bytes, question, mime="image/jpeg"):
    if "gemini_vision" in AC:
        try:
            import PIL.Image
            img = PIL.Image.open(io.BytesIO(img_bytes))
            r = AC["gemini_vision"].generate_content([question or "Bu rasmni batafsil tahlil qil.", img])
            return r.text
        except: pass
    if "openrouter" in AC and "or_key" in AC:
        try:
            b64 = base64.b64encode(img_bytes).decode()
            cl = AC["openrouter"]
            if not isinstance(cl,dict):
                r=cl.chat.completions.create(model="google/gemini-2.0-flash-thinking-exp:free",
                    messages=[{"role":"user","content":[
                        {"type":"image_url","image_url":{"url":f"data:{mime};base64,{b64}"}},
                        {"type":"text","text":question or "Rasmni tahlil qil"}]}],max_tokens=1500)
                return r.choices[0].message.content
        except: pass
    if "groq" in AC:
        try:
            b64=base64.b64encode(img_bytes).decode()
            r=AC["groq"].chat.completions.create(model="llava-v1.5-7b-4096-preview",
                messages=[{"role":"user","content":[
                    {"type":"image_url","image_url":{"url":f"data:{mime};base64,{b64}"}},
                    {"type":"text","text":question or "Rasmni tahlil qil"}]}],max_tokens=1500)
            return r.choices[0].message.content
        except: pass
    return "❌ Rasm tahlili uchun Gemini yoki OpenRouter API keyi kerak."

# ═══════════════════════════════════════════════════
# FILE GENERATORS
# ═══════════════════════════════════════════════════
def gen_excel(prompt, temp=0.25):
    if not HAS_OPENPYXL: return None,"openpyxl o'rnatilmagan"
    sys_p="""Faqat JSON qaytarasan:
{"title":"..","sheets":[{"name":"..","headers":[".."],"header_colors":["4472C4"],"rows":[["..","..","=SUM(B3:B20)"]],"column_widths":[18]}]}
Kamida 12 satr, formulalar ishlat. Hech qanday izoh yozma."""
    raw=call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],temp,4500,best("excel"))
    raw=re.sub(r'```json|```','',raw).strip()
    m=re.search(r'\{.*\}',raw,re.DOTALL)
    if not m: return None,"AI JSON qaytarmadi"
    try: d=json.loads(m.group())
    except:
        try: d=json.loads(raw)
        except Exception as ex: return None,f"JSON: {ex}"
    wb=Workbook(); wb.remove(wb.active)
    TH=[("4F81BD","DEEAF1"),("70AD47","E2EFDA"),("6C5CE7","E8E3FF"),("FF6600","FFE5CC"),("0070C0","CCE5FF")]
    for si,sd in enumerate(d.get("sheets",[])):
        ws=wb.create_sheet(title=sd.get("name",f"Varaq{si+1}")[:30])
        hdrs=sd.get("headers",[]); hcols=sd.get("header_colors",[]); cwidths=sd.get("column_widths",[])
        rows_=sd.get("rows",[]); th,tr=TH[si%len(TH)]
        if sd.get("name"):
            ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=max(len(hdrs),1))
            tc=ws.cell(row=1,column=1,value=sd.get("name",""))
            tc.font=Font(bold=True,size=14,color="FFFFFF",name="Calibri")
            tc.fill=PatternFill("solid",fgColor=th)
            tc.alignment=Alignment(horizontal="center",vertical="center")
            ws.row_dimensions[1].height=28
        for ci,h in enumerate(hdrs,1):
            c=ws.cell(row=2,column=ci,value=h)
            hc=hcols[ci-1] if ci-1<len(hcols) else th
            c.font=Font(bold=True,size=11,color="FFFFFF",name="Calibri")
            c.fill=PatternFill("solid",fgColor=hc)
            c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
            s=Side(style="thin",color="FFFFFF"); c.border=Border(left=s,right=s,top=s,bottom=s)
        ws.row_dimensions[2].height=22
        for ri,row in enumerate(rows_,3):
            rc="FFFFFF" if ri%2 else tr
            for ci,val in enumerate(row,1):
                cc=ws.cell(row=ri,column=ci)
                if isinstance(val,str) and val.startswith("="):
                    cc.value=val; cc.font=Font(color="0B5394",name="Calibri",size=10,bold=True)
                else:
                    try: cc.value=float(val) if isinstance(val,str) and re.match(r'^-?\d+\.?\d*$',str(val).strip()) else val
                    except: cc.value=val
                    cc.font=Font(name="Calibri",size=10)
                cc.fill=PatternFill("solid",fgColor=rc)
                s2=Side(style="thin",color="D0D0D0"); cc.border=Border(left=s2,right=s2,top=s2,bottom=s2)
                cc.alignment=Alignment(vertical="center",wrap_text=True)
            ws.row_dimensions[ri].height=19
        for ci,w in enumerate(cwidths,1): ws.column_dimensions[get_column_letter(ci)].width=max(w,8)
        if not cwidths and hdrs:
            for ci in range(1,len(hdrs)+1): ws.column_dimensions[get_column_letter(ci)].width=18
        ws.freeze_panes="A3"
    if not wb.sheetnames: wb.create_sheet("Sheet1")
    buf=io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf.getvalue(), f"{d.get('title','excel')}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

def gen_word(prompt, temp=0.4):
    if not HAS_DOCX: return None,"python-docx o'rnatilmagan"
    sys_p="""Faqat JSON:
{"title":"..","sections":[{"type":"heading1","text":".."},{"type":"paragraph","text":".."},{"type":"bullet","items":[".."]},{"type":"table","headers":[".."],"rows":[[".."]]}]}
To'liq mazmunli. Faqat JSON."""
    raw=call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],temp,4500,best("word"))
    raw=re.sub(r'```json|```','',raw).strip()
    m=re.search(r'\{.*\}',raw,re.DOTALL)
    if not m: return None,"JSON topilmadi"
    try: d=json.loads(m.group())
    except Exception as ex: return None,f"JSON: {ex}"
    doc=Document()
    doc.styles['Normal'].font.name='Calibri'; doc.styles['Normal'].font.size=Pt(11)
    for sec in doc.sections: sec.top_margin=Cm(2.5); sec.bottom_margin=Cm(2.5); sec.left_margin=Cm(3); sec.right_margin=Cm(2)
    tp=doc.add_heading(d.get("title","Hujjat"),level=0); tp.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for run in tp.runs: run.font.size=Pt(22); run.font.color.rgb=RGBColor(0x6C,0x5C,0xE7)
    dp=doc.add_paragraph(f"Sana: {datetime.now().strftime('%d.%m.%Y')}"); dp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    if dp.runs: dp.runs[0].font.color.rgb=RGBColor(0x64,0x74,0x8B); dp.runs[0].font.size=Pt(10)
    doc.add_paragraph()
    for sec in d.get("sections",[]):
        t=sec.get("type","paragraph")
        if t=="heading1":
            h=doc.add_heading(sec.get("text",""),level=1)
            for r in h.runs: r.font.color.rgb=RGBColor(0x6C,0x5C,0xE7)
        elif t=="heading2":
            h=doc.add_heading(sec.get("text",""),level=2)
            for r in h.runs: r.font.color.rgb=RGBColor(0xA2,0x9B,0xFE)
        elif t=="paragraph":
            p=doc.add_paragraph(sec.get("text","")); p.paragraph_format.space_after=Pt(8)
        elif t=="bullet":
            for item in sec.get("items",[]): doc.add_paragraph(item,style='List Bullet')
        elif t=="numbered":
            for item in sec.get("items",[]): doc.add_paragraph(item,style='List Number')
        elif t=="table":
            hdrs=sec.get("headers",[]); rows_=sec.get("rows",[])
            if hdrs:
                tbl=doc.add_table(rows=1+len(rows_),cols=len(hdrs)); tbl.style='Table Grid'
                for ci,h_ in enumerate(hdrs):
                    cell=tbl.rows[0].cells[ci]; cell.text=h_
                    if cell.paragraphs[0].runs:
                        cell.paragraphs[0].runs[0].font.bold=True
                        cell.paragraphs[0].runs[0].font.color.rgb=RGBColor(255,255,255)
                    from docx.oxml.ns import qn; from docx.oxml import OxmlElement
                    tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd')
                    shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'),'6C5CE7')
                    tcPr.append(shd)
                for ri,row_ in enumerate(rows_):
                    for ci,val in enumerate(row_):
                        if ci<len(tbl.rows[ri+1].cells): tbl.rows[ri+1].cells[ci].text=str(val)
        doc.add_paragraph()
    ft=doc.sections[0].footer.paragraphs[0]; ft.text=f"© {datetime.now().year} Somo AI | {d.get('title','')}"
    ft.alignment=WD_ALIGN_PARAGRAPH.CENTER
    if ft.runs: ft.runs[0].font.size=Pt(9); ft.runs[0].font.color.rgb=RGBColor(0x94,0xA3,0xB8)
    buf=io.BytesIO(); doc.save(buf); buf.seek(0)
    return buf.getvalue(), f"{d.get('title','word')}_{datetime.now().strftime('%Y%m%d_%H%M')}.docx"

def gen_code(prompt, temp=0.15):
    sys_p="Sen professional Python dasturchi. FAQAT kod ber. Izohli, ishlaydigan Python kodi. Tushuntirma yozma."
    code=call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],temp,4000,best("code"))
    code=re.sub(r'```python|```py|```','',code).strip()
    return code.encode('utf-8'), f"somo_{datetime.now().strftime('%Y%m%d_%H%M')}.py"

def gen_html(prompt, temp=0.5):
    sys_p="Sen professional web developer. To'liq HTML/CSS/JS sahifa yarat. Dark theme, animatsiyalar. FAQAT HTML."
    html=call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],temp,5000,best("html"))
    html=re.sub(r'```html|```','',html).strip()
    return html.encode('utf-8'), f"somo_{datetime.now().strftime('%Y%m%d_%H%M')}.html"

def gen_csv(prompt, temp=0.25):
    sys_p="Sen ma'lumotlar ekspersisan. FAQAT CSV. Birinchi qator sarlavha. Kamida 20 satr. Faqat CSV."
    csv_=call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],temp,3000,best("csv"))
    csv_=re.sub(r'```csv|```','',csv_).strip()
    return csv_.encode('utf-8'), f"somo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

# ═══════════════════════════════════════════════════
# INTENT DETECTION
# ═══════════════════════════════════════════════════
EXL=["excel","xlsx","jadval","table","spreadsheet","budget","byudjet","hisobot","report",
     "moliya","daromad","xarajat","oylik","salary","sotish","sales","inventory","formula","ro'yxat list"]
WRD=["word","docx","hujjat","document","letter","maktub","rezyume","resume","cv","shartnoma",
     "contract","ariza","biznes reja","essay","maqola","diplom","referat"]
COD=["python kodi","write code","kod yoz","dastur yoz","script","function yoz","bot yaz",
     "python script","kodni yoz","python program"]
HTM=["html","website","web page","landing page","veb sahifa","html kod","web sayt","webpage"]
CSV_=["csv","comma separated","csv fayl","dataset yarat"]
IMG_G=["rasm yarat","rasm chiz","draw","create image","generate image","paint","surat yarat",
       "rasmini yarat","tasvirini yarat","image create","rasm gen"]
IMG_A=["rasmni tahlil","rasmni ko'r","rasmda nima","bu rasmda","rasmni tushuntir",
       "analyze image","describe image","rasmni o'qi","image analyze","rasmni ayt"]

def intent(txt):
    t=txt.lower()
    if any(k in t for k in IMG_G): return "img_gen"
    if any(k in t for k in IMG_A): return "img_analyze"
    if any(k in t for k in EXL):   return "excel"
    if any(k in t for k in WRD):   return "word"
    if any(k in t for k in HTM):   return "html"
    if any(k in t for k in CSV_):  return "csv"
    if any(k in t for k in COD):   return "code"
    return "chat"

# ═══════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def save_chat(user,role,content):
    if chat_db:
        try: chat_db.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),user,role,content[:500]])
        except: pass

def process_doc(file):
    try:
        if file.type=="application/pdf" and HAS_PDF:
            return "\n".join(p.extract_text() or "" for p in PdfReader(file).pages)
        elif "wordprocessingml" in file.type and HAS_MAMMOTH:
            return mammoth.extract_raw_text(file).value
    except: pass
    return ""

# ═══════════════════════════════════════════════════
# SESSION — restore
# ═══════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    su = cookies.get("somo_sess") if HAS_COOKIES else None
    if su and user_db:
        try:
            recs=user_db.get_all_records()
            ud=next((r for r in recs if str(r['username'])==su),None)
            if ud and str(ud.get('status','')).lower()=='active':
                st.session_state.update({"username":su,"logged_in":True,"login_time":datetime.now()})
            else: st.session_state.logged_in=False
        except: st.session_state.logged_in=False
    else: st.session_state.logged_in=False

def logout():
    if HAS_COOKIES:
        try: cookies["somo_sess"]=""; cookies.save()
        except: pass
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.session_state.logged_in=False; st.rerun()

# ═══════════════════════════════════════════════════
# ★ LOGIN PAGE
# ═══════════════════════════════════════════════════
if not st.session_state.logged_in:
    api_badges=""
    for nm,ic,lbl in [("cerebras","🧠","Cerebras"),("groq","⚡","Groq"),("gemini","✨","Gemini"),
                       ("mistral","💫","Mistral"),("cohere","🌊","Cohere"),("openrouter","🌐","OpenRouter")]:
        api_badges+=f"<span class='{'api-on' if nm in AC else 'api-off'}'>{ic} {lbl}</span>"

    # Particle canvas (background)
    st.components.v1.html("""
    <canvas id='pc' style='position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;'></canvas>
    <script>
    const c=document.getElementById('pc'),ctx=c.getContext('2d');
    c.width=window.innerWidth;c.height=window.innerHeight;
    const pts=Array.from({length:55},()=>({
      x:Math.random()*c.width,y:Math.random()*c.height,
      r:Math.random()*1.8+.4,vx:(Math.random()-.5)*.35,vy:(Math.random()-.5)*.35,
      a:Math.random(),col:Math.random()>.5?'#a29bfe':'#fd79a8'
    }));
    function draw(){
      ctx.clearRect(0,0,c.width,c.height);
      pts.forEach(p=>{
        p.x+=p.vx;p.y+=p.vy;p.a+=.008;
        if(p.x<0||p.x>c.width)p.vx*=-1;
        if(p.y<0||p.y>c.height)p.vy*=-1;
        ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fillStyle=p.col;ctx.globalAlpha=.35+.25*Math.sin(p.a);ctx.fill();
      });
      requestAnimationFrame(draw);
    }
    draw();
    window.addEventListener('resize',()=>{c.width=window.innerWidth;c.height=window.innerHeight;});
    </script>
    """, height=0)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(f"""
        <div class='login-logo' style='margin-top:40px;'>
            <span class='ico'>♾️</span>
            <h1>Somo-AI</h1>
            <p>Universal AI Platform · v5.0</p>
            <div style='margin-top:16px;'>{api_badges}</div>
        </div>
        """, unsafe_allow_html=True)

        t1, t2 = st.tabs(["🔒 Kirish", "✍️ Ro'yxat"])
        with t1:
            with st.form("lf"):
                u=st.text_input("👤 Username",placeholder="username")
                p=st.text_input("🔑 Parol",type="password",placeholder="••••••••")
                rem=st.checkbox("Eslab qolish",value=True)
                sub=st.form_submit_button("🚀 Kirish",use_container_width=True,type="primary")
                if sub and u and p:
                    if user_db:
                        try:
                            recs=user_db.get_all_records()
                            user=next((r for r in recs if str(r['username'])==u and str(r['password'])==hash_pw(p)),None)
                            if user:
                                if str(user.get('status','')).lower()=='blocked': st.error("🚫 Bloklangan!")
                                else:
                                    st.session_state.update({"username":u,"logged_in":True,"login_time":datetime.now()})
                                    if rem and HAS_COOKIES:
                                        try: cookies["somo_sess"]=u; cookies.save()
                                        except: pass
                                    st.success("✅ Muvaffaqiyatli!"); time.sleep(0.4); st.rerun()
                            else: st.error("❌ Login yoki parol xato!")
                        except Exception as ex: st.error(f"❌ {ex}")
                    else: st.error("❌ Baza ulanmagan")

        with t2:
            with st.form("rf"):
                nu=st.text_input("👤 Username (min 3)")
                np_=st.text_input("🔑 Parol (min 6)",type="password")
                nc=st.text_input("🔑 Tasdiqlash",type="password")
                ag=st.checkbox("Shartlarga roziman ✅")
                sub2=st.form_submit_button("🎉 Ro'yxat",use_container_width=True,type="primary")
                if sub2:
                    if not ag: st.error("❌ Shartlarga rozilik!")
                    elif len(nu)<3: st.error("❌ Min 3 belgi!")
                    elif len(np_)<6: st.error("❌ Min 6 belgi!")
                    elif np_!=nc: st.error("❌ Parollar mos emas!")
                    elif user_db:
                        try:
                            recs=user_db.get_all_records()
                            if any(r['username']==nu for r in recs): st.error("❌ Username band!")
                            else:
                                user_db.append_row([nu,hash_pw(np_),"active",str(datetime.now())])
                                st.balloons(); st.success("🎉 Muvaffaqiyatli!")
                        except Exception as ex: st.error(f"❌ {ex}")

        st.markdown("<p style='text-align:center;color:rgba(238,238,255,0.2);font-size:11px;margin-top:20px;'>© 2026 Somo AI Ultra Pro Max v5.0</p>",
                    unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════
# DEFAULTS
# ═══════════════════════════════════════════════════
for k,v in [("messages",[]),("temperature",0.65),("personality","Aqlli yordamchi"),
            ("files_n",0),("uploaded_text",""),("pending_img",None)]:
    if k not in st.session_state: st.session_state[k]=v

# ═══════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════
with st.sidebar:
    uname = st.session_state.username
    st.markdown(f"""
    <div class='sb-user'>
        <div class='sb-av'>{uname[0].upper()}</div>
        <div class='sb-name'>{uname}</div>
        <div class='sb-badge'>● Aktiv</div>
    </div>
    """, unsafe_allow_html=True)

    # API status
    api_n=[k for k in AC if k not in ["gemini_vision","or_key","stability","together"]]
    col=("#00b894" if len(api_n)>=3 else "#fdcb6e" if len(api_n)>=1 else "#d63031")
    row=""
    for nm,ic in [("cerebras","🧠"),("groq","⚡"),("gemini","✨"),("mistral","💫"),("cohere","🌊"),("openrouter","🌐")]:
        c2=("#00b894" if nm in AC else "#d63031")
        row+=f"<span style='color:{c2};font-size:10px;font-weight:600;margin-right:4px;'>{ic}{'✓' if nm in AC else '✗'}</span>"
    st.markdown(f"""
    <div style='background:rgba(0,184,148,.07);border:1px solid rgba(0,184,148,.18);
                border-radius:11px;padding:9px 12px;margin-bottom:12px;'>
        <span style='color:{col};font-size:12px;font-weight:700;'>🔗 {len(api_n)}/6 AI ulangan</span>
        <div style='margin-top:5px;'>{row}</div>
    </div>""",unsafe_allow_html=True)

    if st.button("🔄 Qayta ulanish",use_container_width=True,key="sb_rc"):
        for k in ["ai_c","ai_e"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Chat sozlamalari")
    st.session_state.temperature=st.slider("🌡 Ijodkorlik",0.0,1.0,st.session_state.temperature,0.05)
    st.session_state.personality=st.selectbox("🤖 Uslub",[
        "Aqlli yordamchi","Do'stona","Rasmiy mutaxassis","Ijodkor","Texnik ekspert"])

    st.markdown("---")
    st.markdown("### 📊 Statistika")
    ca,cb=st.columns(2)
    with ca:
        st.markdown(f"<div style='background:var(--gl);border:1px solid var(--bd);border-radius:11px;padding:11px;text-align:center;'>"
                    f"<div style='font-family:Syne,sans-serif;font-size:20px;font-weight:800;"
                    f"background:linear-gradient(135deg,#a29bfe,#fd79a8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;'>"
                    f"💬{len(st.session_state.messages)}</div>"
                    f"<div style='font-size:11px;color:var(--txm);'>Xabarlar</div></div>",unsafe_allow_html=True)
    with cb:
        st.markdown(f"<div style='background:var(--gl);border:1px solid var(--bd);border-radius:11px;padding:11px;text-align:center;'>"
                    f"<div style='font-family:Syne,sans-serif;font-size:20px;font-weight:800;"
                    f"background:linear-gradient(135deg,#a29bfe,#fd79a8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;'>"
                    f"📁{st.session_state.files_n}</div>"
                    f"<div style='font-size:11px;color:var(--txm);'>Fayllar</div></div>",unsafe_allow_html=True)
    if "login_time" in st.session_state:
        mins=(datetime.now()-st.session_state.login_time).seconds//60
        st.markdown(f"<div style='background:var(--gl);border:1px solid var(--bd);border-radius:11px;padding:11px;text-align:center;margin-top:8px;'>"
                    f"<div style='font-family:Syne,sans-serif;font-size:20px;font-weight:800;"
                    f"background:linear-gradient(135deg,#a29bfe,#fd79a8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;'>"
                    f"⏱{mins}</div>"
                    f"<div style='font-size:11px;color:var(--txm);'>Daqiqa</div></div>",unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑 Chatni tozalash",use_container_width=True):
        st.session_state.messages=[]; st.rerun()
    if st.session_state.messages:
        st.download_button("📥 Chat export",
            json.dumps(st.session_state.messages,ensure_ascii=False,indent=2).encode(),
            f"chat_{datetime.now().strftime('%Y%m%d')}.json",use_container_width=True)

    # Doc upload for analysis
    st.markdown("---")
    st.markdown("### 📄 Hujjat yuklash")
    doc_up=st.file_uploader("PDF / DOCX",type=["pdf","docx"],key="doc_up")
    if doc_up:
        with st.spinner("O'qilmoqda..."):
            txt=process_doc(doc_up)
            st.session_state.uploaded_text=txt
        if txt:
            st.success(f"✅ {len(txt):,} belgi o'qildi")
        else:
            st.error("❌ O'qilmadi")

    # Image upload for vision
    st.markdown("### 🖼 Rasm yuklash")
    img_up=st.file_uploader("Rasm (tahlil uchun)",type=["jpg","jpeg","png","webp"],key="img_up")
    if img_up:
        st.session_state.pending_img=img_up.read()
        st.image(st.session_state.pending_img,use_container_width=True)
        st.success("✅ Rasm yuklandi")

    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("🚪 Chiqish",use_container_width=True,type="primary"):
        logout()

# ═══════════════════════════════════════════════════
# PERSONALITIES
# ═══════════════════════════════════════════════════
PERS={
    "Aqlli yordamchi":  "Sen Somo AI — aqlli, professional va foydali yordamchisan. Usmonov Sodiq tomonidan yaratilgan.",
    "Do'stona":         "Sen Somo AI — do'stona, samimiy va quvnoq yordamchisan.",
    "Rasmiy mutaxassis":"Sen Somo AI — rasmiy, aniq va professional mutaxassissan.",
    "Ijodkor":          "Sen Somo AI — ijodkor, original va kreativ yordamchisan.",
    "Texnik ekspert":   "Sen Somo AI — texnik, batafsil tushuntiruvchi ekspертsan.",
}

# ═══════════════════════════════════════════════════
# TOP BAR
# ═══════════════════════════════════════════════════
api_n_count = len([k for k in AC if k not in ["gemini_vision","or_key","stability","together"]])
st.markdown(f"""
<div style='display:flex;align-items:center;gap:14px;padding:14px 24px;
            background:rgba(11,11,24,.92);border-bottom:1px solid rgba(255,255,255,.08);
            backdrop-filter:blur(20px);position:sticky;top:0;z-index:99;'>
    <span style='font-size:30px;animation:logoPulse 3s ease-in-out infinite;
                 filter:drop-shadow(0 0 12px rgba(108,92,231,.8));'>♾️</span>
    <div>
        <div style='font-family:Syne,sans-serif;font-size:19px;font-weight:700;
                    background:linear-gradient(135deg,#fff,#a29bfe,#fd79a8);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;'>
            Somo AI</div>
        <div style='font-size:11px;color:rgba(238,238,255,.4);'>
            {st.session_state.username} · {api_n_count}/6 AI · Excel • Word • Kod • HTML • Rasm • Vision
        </div>
    </div>
    <div style='margin-left:auto;display:flex;align-items:center;gap:8px;'>
        <span style='width:8px;height:8px;border-radius:50%;background:#00b894;display:inline-block;
                     box-shadow:0 0 8px #00b894;'></span>
        <span style='font-size:12px;color:rgba(238,238,255,.5);'>Online</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# WELCOME (empty chat)
# ═══════════════════════════════════════════════════
if not st.session_state.messages:
    st.markdown(f"""
    <div style='text-align:center;padding:50px 20px 20px;'>
        <div style='font-size:56px;display:inline-block;margin-bottom:14px;
                    animation:logoPulse 3s ease-in-out infinite;
                    filter:drop-shadow(0 0 24px rgba(108,92,231,.9));'>♾️</div>
        <h2 style='font-family:Syne,sans-serif;font-size:28px;font-weight:700;
                   background:linear-gradient(135deg,#fff,#a29bfe,#fd79a8);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
                   margin:0 0 8px;'>
            Salom, {st.session_state.username}! 👋</h2>
        <p style='color:rgba(238,238,255,.4);font-size:14px;margin:0;'>
            Pastdagi chat orqali hamma narsani so'rang — fayl, rasm, kod va ko'proq!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick suggestion cards
    suggestions=[
        ("📊","Excel jadval","Oylik byudjet jadvali"),
        ("📝","Word hujjat","Dasturchi uchun CV"),
        ("💻","Python kod","Telegram bot yoz"),
        ("🎨","Rasm yaratish","Futuristik shahar rasmi"),
        ("🌐","HTML sahifa","Portfolio web sayt"),
        ("📋","CSV dataset","100 ta mahsulot"),
        ("🔍","Rasm tahlili","Rasmni tahlil qil"),
        ("🧠","Smart chat","Har qanday savol"),
    ]
    c1,c2,c3,c4=st.columns(4)
    cols=[c1,c2,c3,c4]
    for i,(ic,title,desc) in enumerate(suggestions):
        with cols[i%4]:
            if st.button(f"{ic} {title}",key=f"sug_{i}",use_container_width=True):
                # Put as first message
                sample_prompts={
                    "Excel jadval":"12 oylik moliyaviy byudjet Excel jadvali yasab ber",
                    "Word hujjat":"Python dasturchi uchun professional rezyume Word hujjati yaz",
                    "Python kod":"Telegram bot kodi yoz: /start, /help komandalar",
                    "Rasm yaratish":"Futuristik neon shahar tungi ko'rinishi rasm yarat",
                    "HTML sahifa":"Zamonaviy portfolio HTML sahifa yoz dark theme",
                    "CSV dataset":"100 ta mahsulot CSV: nomi, narxi, kategoriya",
                    "Rasm tahlili":"Rasmni tahlil qil (chap paneldan rasm yuklang)",
                    "Smart chat":"Salom! Bugun qanday yordam bera olasan?",
                }
                st.session_state.messages.append({"role":"user","content":sample_prompts.get(title,title)})
                st.rerun()
            st.markdown(f"<p style='text-align:center;color:rgba(238,238,255,.3);font-size:11px;margin-top:-6px;'>{desc}</p>",
                        unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# DISPLAY MESSAGES
# ═══════════════════════════════════════════════════
st.markdown('<div style="max-width:840px;margin:0 auto;padding:16px 20px 140px;">',unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "dl" in msg:
            dl=msg["dl"]
            st.download_button(f"⬇️ {dl['label']} yuklab olish",
                data=dl["bytes"],file_name=dl["name"],mime=dl["mime"],
                use_container_width=True,type="primary",key=f"dl_{id(msg)}")
        if "img" in msg:
            st.image(base64.b64decode(msg["img"]),use_container_width=True)

st.markdown("</div>",unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# CHAT INPUT & PROCESSING
# ═══════════════════════════════════════════════════
if prompt := st.chat_input("💭 Xabar yuboring... (Excel, Word, Kod, Rasm, Savol — hammasi shu yerda)"):

    # If pending image → force vision
    if st.session_state.pending_img:
        it = "img_analyze"
    else:
        it = intent(prompt)

    # Add user message
    st.session_state.messages.append({"role":"user","content":prompt})
    save_chat(st.session_state.username,"User",prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    # ── AI RESPONSE ──
    with st.chat_message("assistant"):

        # Typing animation placeholder
        typing_ph = st.empty()
        typing_ph.markdown("""
        <div class='typing-dots'>
            <div class='td td1'></div>
            <div class='td td2'></div>
            <div class='td td3'></div>
            <span style='color:rgba(238,238,255,.35);font-size:12px;margin-left:8px;'>
                Javob tayyorlanmoqda...</span>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.55)

        response_text = ""
        file_data = None
        img_b64 = None

        # ── EXCEL ──
        if it == "excel":
            typing_ph.markdown("📊 **Excel yaratilmoqda...**")
            fb, fn = gen_excel(prompt, st.session_state.temperature)
            typing_ph.empty()
            if fb and isinstance(fb,bytes):
                response_text = f"✅ **Excel fayl tayyor!** `{fn}`\n\nJadval yaratildi, yuklab oling 👇"
                file_data = {"bytes":fb,"name":fn,
                    "mime":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "label":"Excel"}
            else:
                response_text = f"❌ Xatolik: {fn}"

        # ── WORD ──
        elif it == "word":
            typing_ph.markdown("📝 **Word hujjat yaratilmoqda...**")
            fb, fn = gen_word(prompt, st.session_state.temperature)
            typing_ph.empty()
            if fb and isinstance(fb,bytes):
                response_text = f"✅ **Word hujjat tayyor!** `{fn}`\n\nProfessional hujjat tayyorlandi 👇"
                file_data = {"bytes":fb,"name":fn,
                    "mime":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "label":"Word"}
            else:
                response_text = f"❌ Xatolik: {fn}"

        # ── CODE ──
        elif it == "code":
            typing_ph.markdown("💻 **Kod yozilmoqda...**")
            cb_, fn = gen_code(prompt, st.session_state.temperature)
            typing_ph.empty()
            ct = cb_.decode("utf-8")
            response_text = f"✅ **Python kod tayyor!** `{fn}`\n\n```python\n{ct[:2200]}{'...' if len(ct)>2200 else ''}\n```"
            file_data = {"bytes":cb_,"name":fn,"mime":"text/x-python","label":".py faylni"}
            st.session_state.files_n += 1

        # ── HTML ──
        elif it == "html":
            typing_ph.markdown("🌐 **HTML sahifa yaratilmoqda...**")
            hb, fn = gen_html(prompt, st.session_state.temperature)
            typing_ph.empty()
            ht = hb.decode("utf-8")
            response_text = f"✅ **HTML sahifa tayyor!** `{fn}`\n\n```html\n{ht[:1200]}...\n```"
            file_data = {"bytes":hb,"name":fn,"mime":"text/html","label":"HTML faylni"}
            st.session_state.files_n += 1

        # ── CSV ──
        elif it == "csv":
            typing_ph.markdown("📋 **CSV yaratilmoqda...**")
            cb_, fn = gen_csv(prompt)
            typing_ph.empty()
            response_text = f"✅ **CSV fayl tayyor!** `{fn}`"
            file_data = {"bytes":cb_,"name":fn,"mime":"text/csv","label":"CSV faylni"}
            st.session_state.files_n += 1

        # ── IMAGE GENERATION ──
        elif it == "img_gen":
            typing_ph.markdown("🎨 **Rasm yaratilmoqda... (30-60 soniya)**")
            img_bytes, img_mime = gen_image(prompt)
            typing_ph.empty()
            if img_bytes:
                img_b64 = base64.b64encode(img_bytes).decode()
                response_text = f"🎨 **Rasm tayyor!** *(Pollinations AI)*\n\n*Prompt: {prompt[:80]}*"
                file_data = {"bytes":img_bytes,
                    "name":f"somo_img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                    "mime":img_mime or "image/jpeg","label":"Rasmni"}
                st.session_state.files_n += 1
            else:
                response_text = "❌ Rasm yaratib bo'lmadi. Internet ulanishini tekshiring."

        # ── IMAGE ANALYSIS ──
        elif it == "img_analyze":
            img_data = st.session_state.pending_img
            if img_data:
                typing_ph.markdown("🔍 **Rasm tahlil qilinmoqda...**")
                analysis = analyze_image(img_data, prompt)
                typing_ph.empty()
                response_text = f"🔍 **Rasm Tahlili:**\n\n{analysis}"
                st.session_state.pending_img = None
            else:
                typing_ph.empty()
                response_text = "📷 Rasm tahlili uchun **chap paneldan rasm yuklang**, so'ng savol bering."

        # ── CHAT (with streaming effect) ──
        else:
            typing_ph.empty()
            sys_msg = PERS.get(st.session_state.personality, PERS["Aqlli yordamchi"])
            msgs_ = [{"role":"system","content":f"""{sys_msg}
Aniq, tushunarli va foydali javob ber. Strukturali yoz."""}]
            if st.session_state.uploaded_text:
                msgs_.append({"role":"system","content":
                    f"Yuklangan hujjat:\n{st.session_state.uploaded_text[:4500]}"})
            for m in st.session_state.messages[-18:]:
                msgs_.append({"role":m["role"],"content":m["content"]})

            full_response = call_ai(msgs_, st.session_state.temperature)

            # ── STREAMING ANIMATION ──
            stream_ph = st.empty()
            displayed = ""
            words = full_response.split(" ")
            # Chunk size varies to look natural
            i = 0
            while i < len(words):
                chunk_size = 2 if len(words[i]) > 8 else 3
                chunk = " ".join(words[i:i+chunk_size])
                displayed += chunk + " "
                stream_ph.markdown(displayed + "▋")
                time.sleep(0.022)
                i += chunk_size
            # Final clean render
            stream_ph.markdown(full_response)
            response_text = full_response
            save_chat("Somo AI","Assistant",full_response)

        # ── Render non-streamed responses ──
        if it != "chat":
            typing_ph.empty()
            stream_ph2 = st.empty()
            words2 = response_text.split(" ")
            displayed2 = ""
            i = 0
            while i < len(words2):
                chunk_size = 3
                chunk = " ".join(words2[i:i+chunk_size])
                displayed2 += chunk + " "
                stream_ph2.markdown(displayed2 + "▋")
                time.sleep(0.018)
                i += chunk_size
            stream_ph2.markdown(response_text)

            # Show image if generated
            if img_b64:
                st.image(base64.b64decode(img_b64), use_container_width=True)

            # Show download button
            if file_data:
                st.download_button(f"⬇️ {file_data['label']} yuklab olish",
                    data=file_data["bytes"],file_name=file_data["name"],
                    mime=file_data["mime"],use_container_width=True,type="primary")
                if it not in ["code","html","csv"]:
                    st.session_state.files_n += 1

        # ── Save to session ──
        msg_to_save = {"role":"assistant","content":response_text}
        if file_data and it not in ["code","html","csv"]:
            msg_to_save["dl"] = file_data
        if img_b64:
            msg_to_save["img"] = img_b64
        st.session_state.messages.append(msg_to_save)

    st.rerun()
