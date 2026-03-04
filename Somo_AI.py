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

# Optional imports with fallbacks
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
    from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side, GradientFill)
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

# ─────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Somo AI | Ultra Pro Max",
    page_icon="♾️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────
# COOKIES
# ─────────────────────────────────────────────────────
cookies = EncryptedCookieManager(
    password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Ultra_Pro_Max_2026")
)
if not cookies.ready():
    st.stop()

# ─────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #e8f4fd 0%, #e0e7ff 40%, #f3e8ff 100%) !important;
}
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
    border-right: 2px solid rgba(139,92,246,0.4);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] section,
[data-testid="stSidebar"] .stVerticalBlock { background: transparent !important; }

div[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.06) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s;
    width: 100% !important;
    padding: 10px !important;
    margin: 3px 0 !important;
    text-align: left !important;
}
div[data-testid="stSidebar"] button:hover {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border-color: transparent !important;
    transform: translateX(5px);
    box-shadow: 0 4px 15px rgba(99,102,241,0.4);
}

/* ── Login Hero ── */
.login-hero {
    background: linear-gradient(135deg, #c5d5f5 0%, #d5c5f5 35%, #e5c5f5 65%, #f0d5f8 100%);
    border-radius: 32px;
    padding: 60px 50px;
    color: #1a1a2e;
    margin-bottom: 30px;
    box-shadow: 0 30px 80px rgba(139,92,246,0.2);
    position: relative;
    overflow: hidden;
    min-height: 380px;
}

.login-hero::before {
    content: '';
    position: absolute;
    top: -100px; right: -100px;
    width: 450px; height: 450px;
    background: radial-gradient(circle, rgba(139,92,246,0.18) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.login-hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 20%;
    width: 350px; height: 350px;
    background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.brand-title {
    font-size: 56px;
    font-weight: 900;
    color: #1a1a2e;
    margin: 0 0 8px;
    letter-spacing: -2px;
    line-height: 1;
}
.brand-title span { color: #6366f1; }

.brand-sub {
    font-size: 19px;
    color: #4a4a6a;
    margin: 0 0 28px;
    font-weight: 400;
}

.feature-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
}

.pill {
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.25);
    color: #4f46e5;
    padding: 7px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}

/* Floating icons animation */
.float-icon {
    position: absolute;
    background: rgba(255,255,255,0.85);
    border-radius: 16px;
    padding: 10px 14px;
    font-size: 22px;
    box-shadow: 0 8px 25px rgba(139,92,246,0.2);
    backdrop-filter: blur(8px);
    z-index: 1;
}
.fi-1 { top: 12%; right: 8%;   animation: float1 3.0s ease-in-out infinite; }
.fi-2 { top: 38%; right: 22%;  animation: float1 3.5s ease-in-out infinite 0.5s; }
.fi-3 { top: 62%; right: 7%;   animation: float1 4.0s ease-in-out infinite 1.0s; }
.fi-4 { top: 20%; right: 33%;  animation: float1 3.2s ease-in-out infinite 0.8s; }
.fi-5 { top: 70%; right: 28%;  animation: float1 3.8s ease-in-out infinite 1.4s; }
.fi-6 { top: 48%; right: 42%;  animation: float1 2.8s ease-in-out infinite 0.3s; }

@keyframes float1 {
    0%,100% { transform: translateY(0px) rotate(0deg); }
    50%      { transform: translateY(-14px) rotate(4deg); }
}

/* ── API badges ── */
.api-badge-on {
    display:inline-block;
    background: linear-gradient(135deg,#10b981,#059669);
    color:white; padding:4px 12px; border-radius:20px;
    font-size:12px; font-weight:700; margin:3px;
}
.api-badge-off {
    display:inline-block;
    background: linear-gradient(135deg,#ef4444,#dc2626);
    color:white; padding:4px 12px; border-radius:20px;
    font-size:12px; font-weight:700; margin:3px;
}

/* ── Gradient text ── */
.grad {
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900;
    animation: gs 5s ease infinite;
}
@keyframes gs { 0%,100%{background-position:0%} 50%{background-position:100%} }

/* ── Hero card (inside app) ── */
.hero {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
    border-radius: 24px;
    padding: 50px 40px;
    text-align: center;
    color: white;
    margin-bottom: 30px;
    box-shadow: 0 20px 60px rgba(99,102,241,0.4);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content:'';
    position:absolute; top:-50%; left:-50%;
    width:200%; height:200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
    animation: rotate 20s linear infinite;
}
@keyframes rotate { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }

/* ── Feature cards ── */
.feat-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:20px; margin:20px 0; }
.feat-card {
    background: white;
    border-radius: 18px;
    padding: 28px 20px;
    text-align: center;
    border: 2px solid #e2e8f0;
    transition: all 0.3s cubic-bezier(.4,0,.2,1);
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}
.feat-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: #6366f1;
    box-shadow: 0 20px 40px rgba(99,102,241,0.2);
}
.feat-icon { font-size: 40px; margin-bottom: 12px; display: block; }
.feat-title { font-weight: 700; font-size: 16px; color: #0f172a; margin-bottom: 6px; }
.feat-desc { font-size: 13px; color: #64748b; line-height: 1.5; }

/* ── Chat messages ── */
.stChatMessage {
    background: white !important;
    border-radius: 16px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
    margin: 8px 0 !important;
}

/* ── Metric badge ── */
.m-card {
    background: white;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    border: 2px solid #e0f2fe;
    margin-bottom: 10px;
}
.m-num { font-size: 28px; font-weight: 900; color: #0f172a; }
.m-lbl { font-size: 12px; color: #64748b; margin-top: 4px; }

/* ── Notification ── */
.notif {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    padding: 12px 20px;
    border-radius: 12px;
    font-weight: 600;
    margin: 10px 0;
    animation: fadeIn 0.5s ease;
}
@keyframes fadeIn { from{opacity:0;transform:translateY(-10px)} to{opacity:1;transform:translateY(0)} }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: transparent; gap: 10px; }
.stTabs [data-baseweb="tab"] {
    background: white;
    border-radius: 10px 10px 0 0;
    border: 2px solid #e2e8f0;
    padding: 10px 20px;
    font-weight: 600;
    transition: 0.3s;
}

/* ── Mobile ── */
@media(max-width:768px) {
    .hero { padding: 30px 20px; }
    .login-hero { padding: 35px 20px; min-height: 260px; }
    .brand-title { font-size: 36px; }
    .float-icon { display: none; }
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 3px; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(99,102,241,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# DB CONNECTION
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
        st.error(f"❌ Baza xatosi: {e}")
        return None, None, None

user_db, chat_db, fb_db = get_connections()

# ─────────────────────────────────────────────────────
# MULTI-API INITIALIZATION (session_state — no cache!)
# ─────────────────────────────────────────────────────
def _get_secret(*keys):
    """Try multiple secret key formats"""
    for key in keys:
        try:
            val = st.secrets.get(key)
            if val:
                return str(val).strip()
        except:
            pass
        for section in ["api_keys", "keys", "secrets"]:
            try:
                val = st.secrets.get(section, {}).get(key)
                if val:
                    return str(val).strip()
            except:
                pass
    return None

def init_clients():
    clients = {}
    errors = {}

    # 1. GROQ
    try:
        k = _get_secret("GROQ_API_KEY", "groq_api_key", "GROQ")
        if k:
            from groq import Groq as GroqClient
            clients["groq"] = GroqClient(api_key=k)
        else:
            errors["groq"] = "API key topilmadi"
    except Exception as e:
        errors["groq"] = str(e)[:60]

    # 2. GEMINI
    try:
        k = _get_secret("GEMINI_API_KEY", "gemini_api_key", "GEMINI")
        if k:
            import google.generativeai as genai
            genai.configure(api_key=k)
            clients["gemini"] = genai.GenerativeModel("gemini-2.0-flash")
        else:
            errors["gemini"] = "API key topilmadi"
    except Exception as e:
        errors["gemini"] = str(e)[:60]

    # 3. COHERE
    try:
        k = _get_secret("COHERE_API_KEY", "cohere_api_key", "COHERE")
        if k:
            import cohere
            clients["cohere"] = cohere.Client(k)
        else:
            errors["cohere"] = "API key topilmadi"
    except Exception as e:
        errors["cohere"] = str(e)[:60]

    # 4. MISTRAL
    try:
        k = _get_secret("MISTRAL_API_KEY", "mistral_api_key", "MISTRAL")
        if k:
            from mistralai.client import MistralClient
            clients["mistral"] = MistralClient(api_key=k)
        else:
            errors["mistral"] = "API key topilmadi"
    except Exception as e:
        errors["mistral"] = str(e)[:60]

    return clients, errors

# Initialize in session_state (not cached — re-reads secrets each session)
if 'ai_clients' not in st.session_state:
    _c, _e = init_clients()
    st.session_state.ai_clients = _c
    st.session_state.api_errors = _e

ai_clients = st.session_state.ai_clients
api_errors  = st.session_state.api_errors

# ─────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

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

def _safe_provider():
    for p in ["groq","gemini","mistral","cohere"]:
        if p in ai_clients:
            return p
    return None

def call_ai(messages, temperature=0.6, max_tokens=3000, provider=None):
    if provider is None:
        provider = _safe_provider()

    # GROQ
    if provider == "groq" and "groq" in ai_clients:
        try:
            resp = ai_clients["groq"].chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=temperature,
                max_tokens=max_tokens
            )
            return resp.choices[0].message.content
        except:
            pass

    # GEMINI
    if provider == "gemini" and "gemini" in ai_clients:
        try:
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            resp = ai_clients["gemini"].generate_content(prompt)
            return resp.text
        except:
            pass

    # MISTRAL
    if provider == "mistral" and "mistral" in ai_clients:
        try:
            from mistralai.models.chat_completion import ChatMessage
            mc = ai_clients["mistral"]
            mm = [ChatMessage(role="user" if m["role"]=="system" else m["role"],
                              content=m["content"]) for m in messages]
            resp = mc.chat(model="mistral-large-latest", messages=mm,
                           temperature=temperature, max_tokens=max_tokens)
            return resp.choices[0].message.content
        except:
            pass

    # COHERE
    if provider == "cohere" and "cohere" in ai_clients:
        try:
            co = ai_clients["cohere"]
            sys_msg = next((m["content"] for m in messages if m["role"]=="system"), "")
            user_msg = next((m["content"] for m in reversed(messages) if m["role"]=="user"), "")
            resp = co.chat(model="command-r-plus", message=user_msg,
                           preamble=sys_msg, temperature=temperature, max_tokens=max_tokens)
            return resp.text
        except:
            pass

    # Fallback: try any available
    for p in ["groq","gemini","mistral","cohere"]:
        if p != provider and p in ai_clients:
            return call_ai(messages, temperature, max_tokens, provider=p)

    return "❌ Hech qanday AI ulanmagan. Streamlit Secrets'da API kalitlarni tekshiring."

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
            "report","moliya","finance","daromad","xarajat","oylik","salary","ish haqi",
            "sotish","sales","inventory","ombor","statistika","formula","hisoblash","ro'yxat"]
WORD_KW  = ["word","docx","hujjat","document","letter","maktub","rezyume","resume","cv",
            "shartnoma","contract","ariza","biznes reja","essay","insho","maqola","diplom","referat"]
CODE_KW  = ["python kodi","write code","kod yoz","dastur yoz","script","function yoz","bot yaz"]
HTML_KW  = ["html","website","web page","landing page","veb sahifa","html kod"]
CSV_KW   = ["csv","comma separated","csv fayl"]

def detect_intent(text):
    t = text.lower()
    if any(k in t for k in EXCEL_KW): return "excel"
    if any(k in t for k in WORD_KW):  return "word"
    if any(k in t for k in HTML_KW):  return "html"
    if any(k in t for k in CSV_KW):   return "csv"
    if any(k in t for k in CODE_KW):  return "code"
    return "chat"

# ─────────────────────────────────────────────────────
# FILE GENERATORS
# ─────────────────────────────────────────────────────
def generate_excel(prompt, temperature=0.3):
    if not HAS_OPENPYXL:
        return None, "openpyxl o'rnatilmagan"
    sys_p = """Sen Excel fayl strukturasini JSON formatida qaytaruvchi ekspертsan.
FAQAT quyidagi JSON formatida javob ber:
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
Kamida 10-15 satr, formulalar ishlat, faqat JSON."""

    raw = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                  temperature=temperature, max_tokens=4000)
    raw = re.sub(r'```json|```','',raw).strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match: return None, "AI strukturani to'g'ri qaytarmadi"
    try: data = json.loads(match.group())
    except:
        try: data = json.loads(raw)
        except Exception as e: return None, f"JSON xatosi: {e}"

    wb = Workbook()
    wb.remove(wb.active)
    THEMES = [("4F81BD","DEEAF1"),("70AD47","E2EFDA"),("7030A0","EAD1FF"),
              ("FF6600","FFE5CC"),("0070C0","CCE5FF"),("FF0000","FFE0E0")]

    for si, sd in enumerate(data.get("sheets",[])):
        ws = wb.create_sheet(title=sd.get("name",f"Varaq{si+1}")[:30])
        headers = sd.get("headers",[])
        hcolors = sd.get("header_colors",[])
        col_widths = sd.get("column_widths",[])
        rows_data = sd.get("rows",[])
        th, tr = THEMES[si % len(THEMES)]

        if "name" in sd:
            ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=max(len(headers),1))
            tc = ws.cell(row=1,column=1,value=sd.get("name",""))
            tc.font = Font(bold=True,size=14,color="FFFFFF",name="Arial")
            tc.fill = PatternFill("solid",fgColor=th)
            tc.alignment = Alignment(horizontal="center",vertical="center")
            ws.row_dimensions[1].height = 28

        if headers:
            for ci,h in enumerate(headers,1):
                c = ws.cell(row=2,column=ci,value=h)
                hc = hcolors[ci-1] if ci-1<len(hcolors) else th
                c.font = Font(bold=True,size=11,color="FFFFFF",name="Arial")
                c.fill = PatternFill("solid",fgColor=hc)
                c.alignment = Alignment(horizontal="center",vertical="center",wrap_text=True)
                s = Side(style="thin",color="FFFFFF")
                c.border = Border(left=s,right=s,top=s,bottom=s)
            ws.row_dimensions[2].height = 22

        for ri,row in enumerate(rows_data,3):
            rc = "FFFFFF" if ri%2 else tr
            for ci,val in enumerate(row,1):
                c = ws.cell(row=ri,column=ci)
                if isinstance(val,str) and val.startswith("="):
                    c.value = val
                    c.font = Font(color="000000",name="Arial",size=10)
                else:
                    try: c.value = float(val) if isinstance(val,str) and val.replace('.','',1).replace('-','',1).isdigit() else val
                    except: c.value = val
                    c.font = Font(name="Arial",size=10)
                c.fill = PatternFill("solid",fgColor=rc)
                s2 = Side(style="thin",color="D0D0D0")
                c.border = Border(left=s2,right=s2,top=s2,bottom=s2)
                c.alignment = Alignment(vertical="center",wrap_text=True)
            ws.row_dimensions[ri].height = 18

        for ci,w in enumerate(col_widths,1):
            ws.column_dimensions[get_column_letter(ci)].width = max(w,8)
        if not col_widths and headers:
            for ci in range(1,len(headers)+1):
                ws.column_dimensions[get_column_letter(ci)].width = 18
        ws.freeze_panes = "A3"

    if not wb.sheetnames: wb.create_sheet("Ma'lumotlar")
    buf = io.BytesIO()
    wb.save(buf); buf.seek(0)
    return buf.getvalue(), f"{data.get('title','somo_excel')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"


def generate_word(prompt, temperature=0.4):
    if not HAS_DOCX:
        return None, "python-docx o'rnatilmagan"
    sys_p = """Sen Word hujjat strukturasini JSON formatida yaratuvchi ekspертsan.
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
                  temperature=temperature, max_tokens=4000)
    raw = re.sub(r'```json|```','',raw).strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match: return None, "Struktura xatosi"
    try: data = json.loads(match.group())
    except Exception as e: return None, f"JSON xatosi: {e}"

    doc = Document()
    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal'].font.size = Pt(11)

    tp = doc.add_heading(data.get("title","Hujjat"), level=0)
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.runs[0].font.size = Pt(22)
    tp.runs[0].font.color.rgb = RGBColor(0x4F,0x46,0xE5)

    dp = doc.add_paragraph(f"Sana: {datetime.now().strftime('%d.%m.%Y')}")
    dp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    dp.runs[0].font.color.rgb = RGBColor(0x64,0x74,0x8B)
    dp.runs[0].font.size = Pt(10)
    doc.add_paragraph()

    for sec in data.get("sections",[]):
        t = sec.get("type","paragraph")
        if t == "heading1":
            h = doc.add_heading(sec.get("text",""), level=1)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x4F,0x46,0xE5)
        elif t == "heading2":
            h = doc.add_heading(sec.get("text",""), level=2)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x7C,0x3A,0xED)
        elif t == "paragraph":
            p = doc.add_paragraph(sec.get("text",""))
            p.paragraph_format.space_after = Pt(8)
        elif t == "bullet":
            for item in sec.get("items",[]): doc.add_paragraph(item, style='List Bullet')
        elif t == "numbered":
            for item in sec.get("items",[]): doc.add_paragraph(item, style='List Number')
        elif t == "table":
            hdrs = sec.get("headers",[])
            rows = sec.get("rows",[])
            if hdrs:
                tbl = doc.add_table(rows=1+len(rows), cols=len(hdrs))
                tbl.style = 'Table Grid'
                for ci,h in enumerate(hdrs):
                    cell = tbl.rows[0].cells[ci]
                    cell.text = h
                    cell.paragraphs[0].runs[0].font.bold = True
                    cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255,255,255)
                    from docx.oxml.ns import qn
                    from docx.oxml import OxmlElement
                    tcPr = cell._tc.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'),'4F46E5')
                    tcPr.append(shd)
                for ri,row_d in enumerate(rows):
                    for ci,val in enumerate(row_d):
                        if ci < len(tbl.rows[ri+1].cells):
                            tbl.rows[ri+1].cells[ci].text = str(val)
        doc.add_paragraph()

    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fp.text = f"© {datetime.now().year} Somo AI | {data.get('title','Hujjat')}"
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if fp.runs:
        fp.runs[0].font.size = Pt(9)
        fp.runs[0].font.color.rgb = RGBColor(0x94,0xA3,0xB8)

    buf = io.BytesIO()
    doc.save(buf); buf.seek(0)
    return buf.getvalue(), f"{data.get('title','somo_doc')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"


def generate_code(prompt, temperature=0.3):
    sys_p = "Sen professional dasturchi. FAQAT Python kodi ber, izohli, ishlaydigan. Tushuntirma yozma."
    code = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                   temperature=temperature, max_tokens=3000)
    code = re.sub(r'```python|```py|```','',code).strip()
    return code.encode('utf-8'), f"somo_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"


def generate_html(prompt, temperature=0.4):
    sys_p = "Sen professional web developer. To'liq HTML/CSS/JS sahifa yarat. FAQAT HTML kod. Inline CSS va JS."
    html = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                   temperature=temperature, max_tokens=4000)
    html = re.sub(r'```html|```','',html).strip()
    return html.encode('utf-8'), f"somo_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"


def generate_csv(prompt, temperature=0.3):
    sys_p = "Sen ma'lumotlar ekspersisan. FAQAT CSV format. Birinchi qator sarlavha. Kamida 20 satr."
    csv_data = call_ai([{"role":"system","content":sys_p},{"role":"user","content":prompt}],
                       temperature=temperature, max_tokens=3000)
    csv_data = re.sub(r'```csv|```','',csv_data).strip()
    return csv_data.encode('utf-8'), f"somo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# ─────────────────────────────────────────────────────
# SESSION INIT (cookie restore)
# ─────────────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user and user_db:
        try:
            recs = user_db.get_all_records()
            ud = next((r for r in recs if str(r['username'])==session_user), None)
            if ud and str(ud.get('status','')).lower()=='active':
                st.session_state.update({'username':session_user,'logged_in':True,'login_time':datetime.now()})
            else:
                st.session_state.logged_in = False
        except:
            st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

def logout():
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
# ★ LOGIN PAGE — NEW BEAUTIFUL DESIGN
# ─────────────────────────────────────────────────────
if not st.session_state.logged_in:

    # Build API status badges
    api_status_html = ""
    for name, icon in [("groq","⚡"),("gemini","✨"),("cohere","🌊"),("mistral","💫")]:
        cls = "api-badge-on" if name in ai_clients else "api-badge-off"
        api_status_html += f"<span class='{cls}'>{icon} {name.title()}</span>"

    # Hero Banner
    st.markdown(f"""
    <div class='login-hero'>
        <div style='position:relative;z-index:2;max-width:55%;'>
            <div style='font-size:52px;margin-bottom:12px;'>♾️</div>
            <h1 class='brand-title'>Somo<span>-AI</span></h1>
            <p class='brand-sub'>Universal AI Platform with 4x Models</p>
            <div class='feature-pills'>
                <span class='pill'>📊 Excel Generator</span>
                <span class='pill'>📝 Word Hujjat</span>
                <span class='pill'>💻 Kod Yozish</span>
                <span class='pill'>🌐 HTML Sahifa</span>
                <span class='pill'>🧠 Smart Chat</span>
                <span class='pill'>🔍 Hujjat Tahlili</span>
            </div>
            <div style='margin-top:22px;'>
                <p style='color:#4a4a6a;font-size:13px;font-weight:600;margin-bottom:8px;'>🔗 Ulangan AI Modellar:</p>
                {api_status_html}
            </div>
        </div>

        <!-- Animated floating icons -->
        <div class='float-icon fi-1'>📊</div>
        <div class='float-icon fi-2'>💻</div>
        <div class='float-icon fi-3'>📝</div>
        <div class='float-icon fi-4'>🌐</div>
        <div class='float-icon fi-5'>🧠</div>
        <div class='float-icon fi-6'>📋</div>
    </div>
    """, unsafe_allow_html=True)

    # Login / Register form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        t1, t2, t3 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish", "ℹ️ Haqida"])

        with t1:
            with st.form("login"):
                st.markdown("### 👋 Xush kelibsiz!")
                u = st.text_input("👤 Username", key="lu", placeholder="username kiriting")
                p = st.text_input("🔑 Parol", type="password", key="lp", placeholder="••••••••")
                c1, c2 = st.columns(2)
                with c1:
                    sub = st.form_submit_button("🚀 Kirish", use_container_width=True, type="primary")
                with c2:
                    rem = st.checkbox("Eslab qolish", value=True)
                if sub and u and p:
                    if user_db:
                        try:
                            recs = user_db.get_all_records()
                            hp = hash_pw(p)
                            user = next((r for r in recs if str(r['username'])==u and str(r['password'])==hp), None)
                            if user:
                                if str(user.get('status','')).lower()=='blocked':
                                    st.error("🚫 Hisob bloklangan!")
                                else:
                                    st.session_state.update({'username':u,'logged_in':True,'login_time':datetime.now()})
                                    if rem:
                                        cookies["somo_user_session"] = u
                                        cookies.save()
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
            with st.form("register"):
                st.markdown("### ✨ Yangi Hisob")
                nu = st.text_input("👤 Username (min 3 belgi)", key="ru")
                np_ = st.text_input("🔑 Parol (min 6 belgi)", type="password", key="rp")
                nc = st.text_input("🔑 Tasdiqlash", type="password", key="rc")
                agree = st.checkbox("Foydalanish shartlariga roziman ✅")
                sub2 = st.form_submit_button("🎉 Ro'yxatdan o'tish", use_container_width=True, type="primary")
                if sub2:
                    if not agree: st.error("❌ Shartlarga rozilik bering!")
                    elif len(nu)<3: st.error("❌ Username kamida 3 belgi!")
                    elif len(np_)<6: st.error("❌ Parol kamida 6 belgi!")
                    elif np_!=nc: st.error("❌ Parollar mos emas!")
                    elif user_db:
                        try:
                            recs = user_db.get_all_records()
                            if any(r['username']==nu for r in recs):
                                st.error("❌ Username band!")
                            else:
                                user_db.append_row([nu, hash_pw(np_), "active", str(datetime.now())])
                                st.balloons()
                                st.success("🎉 Muvaffaqiyatli! Kirish bo'limiga o'ting.")
                        except Exception as e:
                            st.error(f"❌ {e}")

        with t3:
            st.markdown("""
### 🌌 Somo AI Ultra Pro Max v4.0

**4 ta kuchli AI modeli:**
""")
            c1, c2 = st.columns(2)
            for col, (icon, name, desc, bg) in zip(
                [c1,c2,c1,c2],
                [("⚡","Groq + Llama 3.3","Eng tez javob","#f0f9ff"),
                 ("✨","Google Gemini","Multimodal AI","#fdf4ff"),
                 ("🌊","Cohere","RAG & Search","#fff7ed"),
                 ("💫","Mistral","Europa AI","#f0fdf4")]
            ):
                with col:
                    st.markdown(f"""
                    <div style='background:{bg};border-radius:12px;padding:12px;margin:5px 0;border:1px solid #e2e8f0;'>
                        <strong>{icon} {name}</strong><br>
                        <small style='color:#64748b;'>{desc}</small>
                    </div>""", unsafe_allow_html=True)
            st.markdown("""
---
📊 Excel • 📝 Word • 💻 Kod • 🌐 HTML • 📋 CSV • 🧠 Chat  
🔍 PDF/DOCX tahlili • 📜 Chat tarixi & Export

👨‍💻 **Yaratuvchi:** Usmonov Sodiq  
📅 **Versiya:** 4.0 Ultra (2026)
            """)

    st.markdown("""
    <div style='text-align:center;margin-top:40px;color:#94a3b8;'>
        <p>🔒 Xavfsiz &nbsp;|&nbsp; ⚡ 24/7 Online &nbsp;|&nbsp; ♾️ 4x AI Power</p>
        <p style='font-size:12px;'>© 2026 Somo AI Ultra Pro Max v4.0</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────
# SESSION DEFAULTS
# ─────────────────────────────────────────────────────
defaults = {
    'messages': [], 'total_msgs': 0, 'page': 'chat',
    'uploaded_text': '', 'temperature': 0.6,
    'files_created': 0, 'ai_personality': 'Aqlli yordamchi'
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:18px;margin-bottom:12px;
                background:rgba(99,102,241,0.12);border-radius:16px;
                border:1px solid rgba(99,102,241,0.25);'>
        <div style='background:linear-gradient(135deg,#6366f1,#ec4899);
                    width:68px;height:68px;border-radius:50%;
                    margin:0 auto;line-height:68px;font-size:30px;
                    color:white;font-weight:900;border:3px solid rgba(255,255,255,0.3);'>
            {st.session_state.username[0].upper()}
        </div>
        <h3 style='margin:10px 0 4px;font-size:16px;'>{st.session_state.username}</h3>
        <span style='background:#10b981;color:white;padding:2px 10px;
                      border-radius:10px;font-size:11px;font-weight:600;'>● Aktiv</span>
    </div>
    """, unsafe_allow_html=True)

    # API mini status
    api_n = len(ai_clients)
    status_color = "#10b981" if api_n >= 2 else "#f59e0b" if api_n == 1 else "#ef4444"
    st.markdown(f"""
    <div style='background:rgba(16,185,129,0.08);border-radius:10px;padding:8px 12px;
                border:1px solid rgba(16,185,129,0.2);margin-bottom:10px;'>
        <p style='margin:0;font-size:12px;font-weight:700;color:{status_color};'>
            🔗 AI Modellar: {api_n}/4 ulangan
        </p>
        <div style='margin-top:4px;font-size:11px;'>
    """, unsafe_allow_html=True)

    api_row = ""
    for nm, ic in [("groq","⚡"),("gemini","✨"),("cohere","🌊"),("mistral","💫")]:
        c = "#10b981" if nm in ai_clients else "#ef4444"
        api_row += f"<span style='color:{c};font-weight:600;margin-right:6px;'>{ic}{'✓' if nm in ai_clients else '✗'}</span>"
    st.markdown(api_row + "</div></div>", unsafe_allow_html=True)

    if st.button("🔄 API Qayta Ulanish", use_container_width=True, key="sb_reconnect"):
        for k in ['ai_clients','api_errors']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    st.markdown("### 🧭 Navigatsiya")
    pages = [
        ("chat","💬 Chat AI"),("excel","📊 Excel Generator"),
        ("word","📝 Word Generator"),("code","💻 Kod Generator"),
        ("html","🌐 HTML Generator"),("csv","📋 CSV Generator"),
        ("templates","🎨 Shablonlar"),("analyze","🔍 Hujjat Tahlili"),
        ("history","📜 Chat Tarixi"),("feedback","💌 Fikr bildirish"),
        ("profile","👤 Profil"),
    ]
    for pid, lbl in pages:
        t = "primary" if st.session_state.page == pid else "secondary"
        if st.button(lbl, use_container_width=True, key=f"nav_{pid}", type=t):
            st.session_state.page = pid
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Statistika")
    ca, cb = st.columns(2)
    with ca:
        st.markdown(f"""<div class='m-card'><div class='m-num'>💬{len(st.session_state.messages)}</div>
            <div class='m-lbl'>Xabarlar</div></div>""", unsafe_allow_html=True)
    with cb:
        st.markdown(f"""<div class='m-card'><div class='m-num'>📁{st.session_state.files_created}</div>
            <div class='m-lbl'>Fayllar</div></div>""", unsafe_allow_html=True)
    if 'login_time' in st.session_state:
        mins = (datetime.now()-st.session_state.login_time).seconds//60
        st.markdown(f"""<div class='m-card' style='margin-top:8px;'>
            <div class='m-num'>⏱{mins}</div><div class='m-lbl'>Daqiqa online</div></div>""",
            unsafe_allow_html=True)

    st.markdown("---")
    if st.session_state.page == "chat":
        st.markdown("### ⚙️ Chat Sozlamalari")
        st.session_state.temperature = st.slider("🌡 Ijodkorlik", 0.0, 1.0, st.session_state.temperature, 0.1)
        st.session_state.ai_personality = st.selectbox("🤖 AI uslubi",
            ["Aqlli yordamchi","Do'stona","Rasmiy mutaxassis","Ijodkor yozuvchi","Texnik ekspert"])
        if st.button("🗑 Chatni tozalash", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        if st.session_state.messages:
            st.download_button("📥 Chat JSON",
                json.dumps(st.session_state.messages, ensure_ascii=False, indent=2).encode(),
                f"chat_{datetime.now().strftime('%Y%m%d')}.json", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Chiqish", use_container_width=True, type="primary"):
        logout()

# ─────────────────────────────────────────────────────
# DOWNLOAD HELPER
# ─────────────────────────────────────────────────────
def show_file_download(file_bytes, fname, mime, badge_class, label):
    if file_bytes:
        st.session_state.files_created += 1
        st.markdown("<div class='notif'>✅ Fayl tayyor! Yuklab olish uchun tugmani bosing.</div>",
                    unsafe_allow_html=True)
        st.download_button(f"⬇️ {label} yuklab olish", data=file_bytes,
                           file_name=fname, mime=mime, use_container_width=True, type="primary")
        st.markdown(f"<p style='color:#64748b;font-size:13px;'>📁 <code>{fname}</code></p>",
                    unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# PAGE: CHAT
# ─────────────────────────────────────────────────────
if st.session_state.page == "chat":
    if not st.session_state.messages:
        st.markdown(f"""
        <div class='hero' style='padding:40px;margin-bottom:25px;'>
            <h1 style='font-size:36px;margin:0;'>Salom, {st.session_state.username}! 👋</h1>
            <p style='opacity:0.9;font-size:18px;margin:10px 0;'>Bugun sizga qanday yordam bera olaman?</p>
            <p style='opacity:0.7;font-size:14px;'>💡 Excel, Word, Kod, HTML so'rasangiz — fayl avtomatik tayyorlanadi!</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class='feat-grid'>
            <div class='feat-card'><span class='feat-icon'>📊</span><div class='feat-title'>Excel Yaratish</div>
                <div class='feat-desc'>"Oylik byudjet jadvali" — Excel fayl avtomatik</div></div>
            <div class='feat-card'><span class='feat-icon'>📝</span><div class='feat-title'>Word Hujjat</div>
                <div class='feat-desc'>"Rezyume yozing" — professional Word fayl</div></div>
            <div class='feat-card'><span class='feat-icon'>💻</span><div class='feat-title'>Kod Yozish</div>
                <div class='feat-desc'>"Python kodi yozing" — ishlaydigan .py fayl</div></div>
            <div class='feat-card'><span class='feat-icon'>🌐</span><div class='feat-title'>HTML Sahifa</div>
                <div class='feat-desc'>"Landing page" — tayyor HTML fayl</div></div>
            <div class='feat-card'><span class='feat-icon'>📋</span><div class='feat-title'>CSV Ma'lumot</div>
                <div class='feat-desc'>"100 ta mahsulot CSV" — katta dataset</div></div>
            <div class='feat-card'><span class='feat-icon'>🧠</span><div class='feat-title'>Smart Chat</div>
                <div class='feat-desc'>Har qanday savolga aniq javob</div></div>
        </div>""", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "file_data" in msg:
                show_file_download(msg["file_data"]["bytes"],msg["file_data"]["name"],
                                   msg["file_data"]["mime"],msg["file_data"]["badge"],msg["file_data"]["label"])

    if prompt := st.chat_input("💭 Xabar yuboring..."):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        save_to_db(st.session_state.username, "User", prompt)
        intent = detect_intent(prompt)

        PERSONALITIES = {
            "Aqlli yordamchi": "Sen Somo AI — aqlli, professional va foydali yordamchisan. Usmonov Sodiq tomonidan yaratilgan.",
            "Do'stona": "Sen Somo AI — do'stona, samimiy va quvnoq yordamchisan.",
            "Rasmiy mutaxassis": "Sen Somo AI — rasmiy, aniq va professional mutaxassissan.",
            "Ijodkor yozuvchi": "Sen Somo AI — ijodkor, original va kreativ yordamchisan.",
            "Texnik ekspert": "Sen Somo AI — texnik, aniq va batafsil tushuntiruvchi ekspертsan."
        }
        base_sys = PERSONALITIES.get(st.session_state.ai_personality, PERSONALITIES["Aqlli yordamchi"])

        with st.chat_message("assistant"):
            if intent == "excel":
                with st.spinner("📊 Excel yaratilmoqda..."):
                    st.markdown("📊 **Excel fayl yaratilmoqda...** Iltimos kuting.")
                    fb, fn = generate_excel(prompt, st.session_state.temperature)
                    if fb and isinstance(fb,bytes):
                        rt = f"✅ Excel fayl tayyor!\n\n📊 **{fn}**"
                        fi = {"bytes":fb,"name":fn,"mime":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","badge":"xls-badge","label":"Excel"}
                    else:
                        rt = f"❌ Excel xatolik: {fn}"; fi = None
                    st.markdown(rt)
                    if fi: show_file_download(fi["bytes"],fi["name"],fi["mime"],fi["badge"],fi["label"])
                    md = {"role":"assistant","content":rt}
                    if fi: md["file_data"] = fi
                    st.session_state.messages.append(md)

            elif intent == "word":
                with st.spinner("📝 Word yaratilmoqda..."):
                    st.markdown("📝 **Word hujjat yaratilmoqda...** Iltimos kuting.")
                    fb, fn = generate_word(prompt, st.session_state.temperature)
                    if fb and isinstance(fb,bytes):
                        rt = f"✅ Word hujjat tayyor!\n\n📝 **{fn}**"
                        fi = {"bytes":fb,"name":fn,"mime":"application/vnd.openxmlformats-officedocument.wordprocessingml.document","badge":"doc-badge","label":"Word"}
                    else:
                        rt = f"❌ Word xatolik: {fn}"; fi = None
                    st.markdown(rt)
                    if fi: show_file_download(fi["bytes"],fi["name"],fi["mime"],fi["badge"],fi["label"])
                    md = {"role":"assistant","content":rt}
                    if fi: md["file_data"] = fi
                    st.session_state.messages.append(md)

            elif intent == "code":
                with st.spinner("💻 Kod yozilmoqda..."):
                    cb_, fn = generate_code(prompt, st.session_state.temperature)
                    ct = cb_.decode('utf-8')
                    rt = f"✅ Python kod tayyor!\n\n```python\n{ct[:1500]}{'...' if len(ct)>1500 else ''}\n```"
                    st.markdown(rt)
                    st.download_button("⬇️ .py yuklab olish", cb_, fn, "text/x-python",
                                       use_container_width=True, type="primary")
                    st.session_state.messages.append({"role":"assistant","content":rt})

            elif intent == "html":
                with st.spinner("🌐 HTML yaratilmoqda..."):
                    hb, fn = generate_html(prompt, st.session_state.temperature)
                    ht = hb.decode('utf-8')
                    rt = f"✅ HTML sahifa tayyor!\n\n```html\n{ht[:1000]}...\n```"
                    st.markdown(rt)
                    st.download_button("⬇️ HTML yuklab olish", hb, fn, "text/html",
                                       use_container_width=True, type="primary")
                    st.session_state.files_created += 1
                    st.session_state.messages.append({"role":"assistant","content":rt})

            elif intent == "csv":
                with st.spinner("📋 CSV yaratilmoqda..."):
                    cb_, fn = generate_csv(prompt, st.session_state.temperature)
                    rt = f"✅ CSV fayl tayyor! **{fn}**"
                    st.markdown(rt)
                    st.download_button("⬇️ CSV yuklab olish", cb_, fn, "text/csv",
                                       use_container_width=True, type="primary")
                    st.session_state.files_created += 1
                    st.session_state.messages.append({"role":"assistant","content":rt})

            else:
                with st.spinner("🤔 O'ylayapman..."):
                    msgs_to_send = [{"role":"system","content":f"""{base_sys}
Har doim aniq, tushunarli va foydali javob ber.
Matematika formulalarini LaTeX ($...$) formatida yoz.
Javobni strukturalashtirilgan va o'qishga qulay qil."""}]
                    if st.session_state.uploaded_text:
                        msgs_to_send.append({"role":"system","content":
                            f"Yuklangan hujjat:\n{st.session_state.uploaded_text[:4000]}"})
                    for m in st.session_state.messages[-16:]:
                        msgs_to_send.append({"role":m["role"],"content":m["content"]})
                    response = call_ai(msgs_to_send, st.session_state.temperature)
                    st.markdown(response)
                    st.session_state.messages.append({"role":"assistant","content":response})
                    save_to_db("Somo AI","Assistant",response)

        st.session_state.total_msgs += 1
        st.rerun()

# ─────────────────────────────────────────────────────
# PAGE: EXCEL GENERATOR
# ─────────────────────────────────────────────────────
elif st.session_state.page == "excel":
    st.markdown("""<div class='hero'><h1 style='font-size:42px;'>📊 Excel Generator</h1>
        <p style='opacity:0.9;font-size:18px;'>Xohlagan jadvalni AI bilan yarating</p></div>""", unsafe_allow_html=True)
    examples = ["12 oylik moliyaviy byudjet jadvali: daromad, xarajat, foyda",
        "100 ta mahsulot inventar: nomi, miqdori, narxi, jami","Xodimlar ish haqi: ism, lavozim, maosh, soliq, sof",
        "Talabalar baholar jadvali: 5 ta fan, o'rtacha, reyting","Haftalik ish jadvali: xodimlar va vazifalar",
        "Savdo hisoboti: oylar, mahsulotlar, daromad, maqsad, foiz"]
    c1,c2,c3 = st.columns(3)
    for i,ex in enumerate(examples):
        with [c1,c2,c3][i%3]:
            if st.button(f"📋 {ex[:38]}...", key=f"ex_{i}", use_container_width=True):
                st.session_state.excel_prompt = ex
    ep = st.text_area("📝 Excel jadval tavsifi:", value=st.session_state.get("excel_prompt",""),
        placeholder="Masalan: 12 oylik byudjet, formulalar bilan", height=100, key="excel_input")
    c1,c2 = st.columns([3,1])
    with c2: temp = st.slider("Aniqlik",0.0,0.8,0.2,0.1,key="excel_temp")
    with c1: gen_btn = st.button("🚀 Excel Yaratish", use_container_width=True, type="primary", key="gen_excel")
    if gen_btn and ep:
        with st.spinner("📊 Yaratilmoqda..."):
            pr = st.progress(0)
            for i in range(0,80,20): time.sleep(0.3); pr.progress(i)
            fb, fn = generate_excel(ep, temp); pr.progress(100)
            if fb and isinstance(fb,bytes):
                st.success("✅ Excel fayl tayyor!")
                show_file_download(fb,fn,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","xls-badge","Excel")
            else: st.error(f"❌ Xatolik: {fn}")
    elif gen_btn: st.warning("⚠️ Jadval tavsifini kiriting!")

# ─────────────────────────────────────────────────────
# PAGE: WORD GENERATOR
# ─────────────────────────────────────────────────────
elif st.session_state.page == "word":
    st.markdown("""<div class='hero'><h1 style='font-size:42px;'>📝 Word Generator</h1>
        <p style='opacity:0.9;font-size:18px;'>Professional hujjatlarni AI bilan yarating</p></div>""", unsafe_allow_html=True)
    we = ["Professional rezyume: dasturchi, 3 yil tajriba","Biznes xat: hamkorlik taklifi",
          "Ijara shartnomasi: standart shakl","Ishga qabul qilish buyrug'i",
          "Kurs ishi: sun'iy intellekt mavzusi","Marketing strategiya hujjati"]
    c1,c2,c3 = st.columns(3)
    for i,ex in enumerate(we):
        with [c1,c2,c3][i%3]:
            if st.button(f"📄 {ex[:33]}...", key=f"wex_{i}", use_container_width=True):
                st.session_state.word_prompt = ex
    wp = st.text_area("📝 Hujjat tavsifi:", value=st.session_state.get("word_prompt",""),
        placeholder="Masalan: Python dasturchi uchun rezyume, 5 yil tajriba", height=100, key="word_input")
    gen_word = st.button("🚀 Word Yaratish", use_container_width=True, type="primary", key="gen_word")
    if gen_word and wp:
        with st.spinner("📝 Yaratilmoqda..."):
            pr = st.progress(0)
            for i in range(0,80,25): time.sleep(0.3); pr.progress(i)
            fb, fn = generate_word(wp); pr.progress(100)
            if fb and isinstance(fb,bytes):
                st.success("✅ Word hujjat tayyor!")
                show_file_download(fb,fn,"application/vnd.openxmlformats-officedocument.wordprocessingml.document","doc-badge","Word")
            else: st.error(f"❌ Xatolik: {fn}")
    elif gen_word: st.warning("⚠️ Hujjat tavsifini kiriting!")

# ─────────────────────────────────────────────────────
# PAGE: CODE GENERATOR
# ─────────────────────────────────────────────────────
elif st.session_state.page == "code":
    st.markdown("""<div class='hero'><h1 style='font-size:42px;'>💻 Kod Generator</h1>
        <p style='opacity:0.9;font-size:18px;'>Professional Python kodi — tayyor faylda</p></div>""", unsafe_allow_html=True)
    ce = ["Streamlit dashboard - savdo statistikasi","FastAPI REST API - foydalanuvchi tizimi",
          "Telegram bot - xabar yuboruvchi","Web scraper - narxlarni kuzatish",
          "Machine learning - tasniflovchi model","File organizer - papkalarni tartiblovchi"]
    c1,c2,c3 = st.columns(3)
    for i,ex in enumerate(ce):
        with [c1,c2,c3][i%3]:
            if st.button(f"💡 {ex}", key=f"cex_{i}", use_container_width=True):
                st.session_state.code_prompt = ex
    cp = st.text_area("📝 Kod tavsifi:", value=st.session_state.get("code_prompt",""),
        placeholder="Masalan: Telegram bot, foydalanuvchi xabar yuborsa avtomatik javob", height=100, key="code_input")
    c1,c2 = st.columns([3,1])
    with c2: ct = st.slider("Ijodkorlik",0.0,0.6,0.1,0.1,key="code_temp")
    gen_code = st.button("🚀 Kod Yaratish", use_container_width=True, type="primary", key="gen_code")
    if gen_code and cp:
        with st.spinner("💻 Yozilmoqda..."):
            cb_, fn = generate_code(cp, ct)
            st.success("✅ Kod tayyor!")
            st.code(cb_.decode('utf-8'), language="python")
            st.download_button("⬇️ .py yuklab olish", cb_, fn, "text/x-python",
                               use_container_width=True, type="primary")
            st.session_state.files_created += 1
    elif gen_code: st.warning("⚠️ Kod tavsifini kiriting!")

# ─────────────────────────────────────────────────────
# PAGE: HTML GENERATOR
# ─────────────────────────────────────────────────────
elif st.session_state.page == "html":
    st.markdown("""<div class='hero'><h1 style='font-size:42px;'>🌐 HTML Generator</h1>
        <p style='opacity:0.9;font-size:18px;'>Chiroyli veb sahifalar — bitta faylda</p></div>""", unsafe_allow_html=True)
    he = ["Portfolio sahifa - dasturchi uchun","Restaurant menu - chiroyli dizayn",
          "Landing page - mahsulot reklamasi","Dashboard - statistika ko'rsatish",
          "Login sahifa - modern UI","Blog post sahifasi"]
    c1,c2,c3 = st.columns(3)
    for i,ex in enumerate(he):
        with [c1,c2,c3][i%3]:
            if st.button(f"🌐 {ex}", key=f"hex_{i}", use_container_width=True):
                st.session_state.html_prompt = ex
    hp_ = st.text_area("📝 Sahifa tavsifi:", value=st.session_state.get("html_prompt",""),
        placeholder="Masalan: Zamonaviy portfolio, dark theme, animatsiyalar", height=100, key="html_input")
    gen_html = st.button("🚀 HTML Yaratish", use_container_width=True, type="primary", key="gen_html")
    if gen_html and hp_:
        with st.spinner("🌐 Yaratilmoqda..."):
            hb, fn = generate_html(hp_, 0.5)
            ht = hb.decode('utf-8')
            st.success("✅ HTML sahifa tayyor!")
            with st.expander("📄 HTML kodini ko'rish"):
                st.code(ht[:3000]+("..." if len(ht)>3000 else ""), language="html")
            st.download_button("⬇️ HTML yuklab olish", hb, fn, "text/html",
                               use_container_width=True, type="primary")
            st.session_state.files_created += 1
    elif gen_html: st.warning("⚠️ Sahifa tavsifini kiriting!")

# ─────────────────────────────────────────────────────
# PAGE: CSV GENERATOR
# ─────────────────────────────────────────────────────
elif st.session_state.page == "csv":
    st.markdown("""<div class='hero'><h1 style='font-size:42px;'>📋 CSV Generator</h1>
        <p style='opacity:0.9;font-size:18px;'>Katta datasetlar — tezda tayyor</p></div>""", unsafe_allow_html=True)
    cse = ["100 ta mahsulot: nomi, narxi, kategoriya, miqdori","50 ta xodim: ism, lavozim, maosh, bo'lim",
           "200 ta talaba: ism, guruh, baholar, o'rtacha","Dunyo mamlakatlari: nomi, poytaxti, aholi, YIM",
           "Top 100 dasturlash tillari: nomi, turi, yil","E-commerce buyurtmalar: ID, mahsulot, miqdor, sana"]
    c1,c2,c3 = st.columns(3)
    for i,ex in enumerate(cse):
        with [c1,c2,c3][i%3]:
            if st.button(f"📋 {ex[:33]}...", key=f"csv_ex_{i}", use_container_width=True):
                st.session_state.csv_prompt = ex
    csvp = st.text_area("📝 Ma'lumotlar tavsifi:", value=st.session_state.get("csv_prompt",""),
        placeholder="Masalan: 100 ta O'zbekiston shahri: nomi, viloyati, aholisi", height=100, key="csv_input")
    gen_csv = st.button("🚀 CSV Yaratish", use_container_width=True, type="primary", key="gen_csv")
    if gen_csv and csvp:
        with st.spinner("📋 Yaratilmoqda..."):
            cb_, fn = generate_csv(csvp)
            try:
                df = pd.read_csv(io.BytesIO(cb_))
                st.success(f"✅ CSV tayyor! {len(df)} satr, {len(df.columns)} ustun")
                st.dataframe(df.head(10), use_container_width=True)
            except: st.success("✅ CSV fayl tayyor!")
            st.download_button("⬇️ CSV yuklab olish", cb_, fn, "text/csv",
                               use_container_width=True, type="primary")
            st.session_state.files_created += 1
    elif gen_csv: st.warning("⚠️ Ma'lumotlar tavsifini kiriting!")

# ─────────────────────────────────────────────────────
# PAGE: TEMPLATES
# ─────────────────────────────────────────────────────
elif st.session_state.page == "templates":
    st.markdown("""<div class='hero'><h1 style='font-size:42px;'>🎨 Shablonlar Markazi</h1>
        <p style='opacity:0.9;font-size:18px;'>Tayyor shablonlar bilan tezlashtirib ishlang</p></div>""", unsafe_allow_html=True)
    TMPLS = {
        "📊 Biznes": [
            {"title":"💰 Oylik Byudjet","prompt":"12 oylik moliyaviy byudjet Excel: daromad, xarajatlar, sof foyda, formulalar","type":"excel"},
            {"title":"📈 Savdo Hisoboti","prompt":"Oylik savdo hisoboti Excel: mahsulotlar, maqsad vs haqiqiy, foiz bajarilishi","type":"excel"},
            {"title":"📋 Biznes Reja","prompt":"Yangi IT kompaniya biznes reja Word: ijroiya xulosa, bozor tahlili, moliyaviy prognoz","type":"word"},
            {"title":"🤝 Hamkorlik Xati","prompt":"Professional hamkorlik taklifi maktubi Word: kompaniya taqdimoti, taklif, shartlar","type":"word"},
        ],
        "💻 Dasturlash": [
            {"title":"🤖 Telegram Bot","prompt":"Python Telegram bot: start komandasi, keyboard, error handling, aiogram v3","type":"code"},
            {"title":"🌐 FastAPI CRUD","prompt":"FastAPI CRUD API: foydalanuvchilar, Pydantic, swagger dokumentatsiya","type":"code"},
            {"title":"📊 Data Tahlil","prompt":"Pandas va matplotlib: CSV o'qish, tozalash, statistika, grafik","type":"code"},
            {"title":"🌐 Portfolio Sayt","prompt":"Zamonaviy portfolio: hero, skills, projects, contact, dark theme, animations","type":"html"},
        ],
        "📚 Ta'lim": [
            {"title":"📖 Dars Rejasi","prompt":"Python asoslari 45 daqiqalik dars rejasi Word: maqsadlar, kirish, amaliy mashq","type":"word"},
            {"title":"📝 Test Savollari","prompt":"Python bo'yicha 20 ta test Excel: savol, 4 variant, to'g'ri javob","type":"excel"},
            {"title":"🎓 Baholar Jadvali","prompt":"30 ta talaba baholar jadvali: ism, 6 fan, o'rtacha, reyting, davomad","type":"excel"},
            {"title":"📚 Kurs Ishi","prompt":"Kurs ishi Word: Sun'iy intellekt. Kirish, 3 bob, xulosa, adabiyotlar","type":"word"},
        ],
        "👤 Shaxsiy": [
            {"title":"📄 Rezyume","prompt":"Python backend dasturchi professional rezyume Word: tajriba, ko'nikmalar, ta'lim","type":"word"},
            {"title":"📅 Haftalik Reja","prompt":"Haftalik vazifalar Excel: 7 kun, vazifalar, ustuvorlik, holat, foiz","type":"excel"},
            {"title":"💪 Sport Jadvali","prompt":"3 oylik sport mashg'ulotlari Excel: mashqlar, takroriylik, og'irlik, progres","type":"excel"},
            {"title":"💰 Shaxsiy Byudjet","prompt":"Shaxsiy oylik byudjet Excel: daromad, xarajatlar, jamg'arma, formulalar","type":"excel"},
        ]
    }
    TC = {"excel":"#10b981","word":"#3b82f6","code":"#f59e0b","html":"#f43f5e"}
    TL = {"excel":"📊 Excel","word":"📝 Word","code":"💻 Kod","html":"🌐 HTML"}
    sel = st.selectbox("📁 Kategoriya:", list(TMPLS.keys()), key="tmpl_cat")
    st.markdown("---")
    cols2 = st.columns(2)
    for i, tmpl in enumerate(TMPLS[sel]):
        with cols2[i%2]:
            st.markdown(f"""
            <div style='background:white;border-radius:16px;padding:18px;
                        border:2px solid #e2e8f0;margin-bottom:12px;box-shadow:0 4px 15px rgba(0,0,0,0.05);'>
                <h3 style='color:#0f172a;margin:0 0 6px;font-size:16px;'>{tmpl['title']}</h3>
                <span style='background:{TC.get(tmpl["type"],"#6366f1")};color:white;
                             padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600;'>
                    {TL.get(tmpl["type"],"🔧")}</span>
                <p style='color:#64748b;font-size:12px;margin-top:8px;'>{tmpl["prompt"][:90]}...</p>
            </div>""", unsafe_allow_html=True)
            b1,b2 = st.columns(2)
            with b1:
                if st.button("🚀 Yaratish", key=f"tg_{sel}_{i}", use_container_width=True, type="primary"):
                    with st.spinner("⏳ Yaratilmoqda..."):
                        tt = tmpl["type"]
                        if tt=="excel":
                            fb,fn = generate_excel(tmpl["prompt"])
                            if fb and isinstance(fb,bytes):
                                st.download_button("⬇️ Excel",fb,fn,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key=f"dl_{sel}_{i}")
                                st.session_state.files_created+=1
                        elif tt=="word":
                            fb,fn = generate_word(tmpl["prompt"])
                            if fb and isinstance(fb,bytes):
                                st.download_button("⬇️ Word",fb,fn,"application/vnd.openxmlformats-officedocument.wordprocessingml.document",key=f"dl_{sel}_{i}")
                                st.session_state.files_created+=1
                        elif tt=="code":
                            fb,fn = generate_code(tmpl["prompt"])
                            st.download_button("⬇️ .py",fb,fn,"text/x-python",key=f"dl_{sel}_{i}")
                            st.session_state.files_created+=1
                        elif tt=="html":
                            fb,fn = generate_html(tmpl["prompt"])
                            st.download_button("⬇️ HTML",fb,fn,"text/html",key=f"dl_{sel}_{i}")
                            st.session_state.files_created+=1
            with b2:
                if st.button("💬 Chatga", key=f"tc_{sel}_{i}", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":tmpl["prompt"]})
                    st.session_state.page = "chat"; st.rerun()

# ─────────────────────────────────────────────────────
# PAGE: ANALYZE
# ─────────────────────────────────────────────────────
elif st.session_state.page == "analyze":
    st.markdown("""<div class='hero'><h1 style='font-size:42px;'>🔍 Hujjat Tahlili</h1>
        <p style='opacity:0.9;font-size:18px;'>PDF va Word fayllarni AI bilan tahlil qiling</p></div>""", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### 📂 Fayl Yuklash")
        uploaded = st.file_uploader("PDF yoki DOCX", type=["pdf","docx"], key="analyze_upload")
        if uploaded:
            with st.spinner("📄 O'qilmoqda..."):
                text = process_doc(uploaded)
                st.session_state.uploaded_text = text
            if text:
                st.success(f"✅ {uploaded.name}")
                st.info(f"📊 {len(text):,} belgi, ~{len(text.split()):,} so'z")
                with st.expander("📄 Matnni ko'rish"):
                    st.text(text[:2000]+("..." if len(text)>2000 else ""))
            else: st.error("❌ Fayl o'qilmadi")
    with c2:
        st.markdown("### 🧠 Tahlil Amaliyotlari")
        if st.session_state.uploaded_text:
            actions = {"📝 Qisqa xulosa":"Ushbu hujjatni 3-5 band bilan qisqa xulosasini yoz.",
                "🔑 Asosiy g'oyalar":"5-10 ta eng muhim g'oya va faktlarni ajratib chiqar.",
                "❓ Savol-Javob":"Hujjat bo'yicha 10 ta muhim savol va javob tuzib ber.",
                "🌐 Tarjima":"Hujjat mazmunini ingliz tiliga tarjima qil.",
                "📊 Statistika":"Barcha raqamlar va statistikani jadval ko'rinishida ko'rsat.",
                "✅ Action items":"Amaliy vazifalar va keyingi qadamlarni ajratib ber."}
            for act, prm in actions.items():
                if st.button(act, key=f"act_{act}", use_container_width=True):
                    with st.spinner("🤔 Tahlil qilinmoqda..."):
                        r = call_ai([{"role":"system","content":"Sen hujjat tahlilchisan."},
                                     {"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:4000]}\n\n{prm}"}])
                        st.markdown(f"### {act}"); st.markdown(r)
            st.markdown("---")
            cq = st.text_input("🔍 O'z savolingiz:", key="custom_q")
            if st.button("🔍 Qidirish", use_container_width=True, type="primary") and cq:
                with st.spinner("🤔 Qidirilmoqda..."):
                    r = call_ai([{"role":"system","content":"Hujjat asosida aniq javob ber."},
                                 {"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:4000]}\n\nSavol: {cq}"}])
                    st.markdown(r)
        else: st.info("👆 Avval chap tomonda fayl yuklang")

# ─────────────────────────────────────────────────────
# PAGE: HISTORY
# ─────────────────────────────────────────────────────
elif st.session_state.page == "history":
    st.markdown("""<div class='hero'><h1 style='font-size:42px;'>📜 Chat Tarixi</h1>
        <p style='opacity:0.9;font-size:18px;'>Barcha suhbatlaringiz</p></div>""", unsafe_allow_html=True)
    if st.session_state.messages:
        c1,c2,c3 = st.columns(3)
        with c1: st.metric("👤 Sizning",len([m for m in st.session_state.messages if m["role"]=="user"]))
        with c2: st.metric("🤖 AI javoblar",len([m for m in st.session_state.messages if m["role"]=="assistant"]))
        with c3: st.metric("📁 Fayllar",st.session_state.files_created)
        srch = st.text_input("🔍 Qidirish:", key="history_search")
        show = st.session_state.messages
        if srch: show = [m for m in show if srch.lower() in m.get("content","").lower()]
        c1,c2 = st.columns(2)
        with c1:
            st.download_button("📥 JSON",json.dumps(st.session_state.messages,ensure_ascii=False,indent=2).encode(),
                               f"chat_{datetime.now().strftime('%Y%m%d')}.json","application/json",use_container_width=True)
        with c2:
            st.download_button("📄 TXT","\n\n".join([f"[{m['role'].upper()}]\n{m['content']}" for m in st.session_state.messages]).encode(),
                               f"chat_{datetime.now().strftime('%Y%m%d')}.txt","text/plain",use_container_width=True)
        st.markdown("---")
        for msg in reversed(show[-50:]):
            bg = "#EEF2FF" if msg["role"]=="user" else "#F0FDF4"
            bdr = "#6366f1" if msg["role"]=="user" else "#10b981"
            ic = "👤" if msg["role"]=="user" else "🤖"
            st.markdown(f"""<div style='background:{bg};border-left:4px solid {bdr};
                padding:12px 16px;border-radius:8px;margin:8px 0;'>
                <strong>{ic} {msg["role"].title()}</strong>
                <p style='margin:6px 0 0;color:#374151;font-size:14px;'>{msg["content"][:300]}{"..." if len(msg.get("content",""))>300 else ""}</p>
            </div>""", unsafe_allow_html=True)
    else: st.info("💬 Hali chat tarixi yo'q.")

# ─────────────────────────────────────────────────────
# PAGE: FEEDBACK
# ─────────────────────────────────────────────────────
elif st.session_state.page == "feedback":
    st.markdown("""<div class='hero'><h1 style='font-size:42px;'>💌 Fikr-Mulohazalar</h1>
        <p style='opacity:0.9;font-size:18px;'>Sizning fikringiz bizni yaxshiroq qiladi!</p></div>""", unsafe_allow_html=True)
    c1,c2 = st.columns([3,2])
    with c1:
        with st.form("feedback_form"):
            st.markdown("### ⭐ Baholang")
            rating = st.select_slider("Baho:", options=[1,2,3,4,5], value=5, format_func=lambda x:"⭐"*x)
            st.markdown(f"<p style='font-size:48px;text-align:center;'>{'⭐'*rating}</p>", unsafe_allow_html=True)
            category = st.selectbox("📂 Kategoriya:",["Umumiy fikr","Xato haqida","Yangi funksiya taklifi","Dizayn","Tezlik","Boshqa"])
            message = st.text_area("✍️ Xabaringiz:", height=120, placeholder="Fikr-mulohazalaringizni yozing...")
            email = st.text_input("📧 Email (ixtiyoriy):")
            sub = st.form_submit_button("📤 Yuborish", use_container_width=True, type="primary")
            if sub:
                if not message or len(message)<10: st.error("❌ Kamida 10 belgi!")
                elif fb_db:
                    try:
                        fb_db.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            st.session_state.username,rating,category,message,email or "N/A","Yangi"])
                        st.balloons()
                        st.markdown("<div class='notif'>✅ Rahmat! Fikringiz yuborildi. 🙏</div>", unsafe_allow_html=True)
                    except Exception as e: st.error(f"❌ {e}")
    with c2:
        st.markdown("### 📊 Statistika")
        if fb_db:
            try:
                aff = fb_db.get_all_records()
                if aff:
                    st.metric("📨 Jami", len(aff))
                    rl = [int(f.get('Rating',5)) for f in aff if f.get('Rating')]
                    if rl: st.metric("⭐ O'rtacha", f"{sum(rl)/len(rl):.1f}/5")
                    for fb in aff[-5:]:
                        st.markdown(f"""<div style='background:#f8fafc;border-radius:8px;padding:10px;margin:4px 0;border:1px solid #e2e8f0;'>
                            <strong>{'⭐'*int(fb.get('Rating',5))}</strong> <span style='color:#6366f1;font-size:12px;'>— {fb.get('Username','')}</span>
                            <p style='margin:4px 0 0;font-size:12px;color:#374151;'>{str(fb.get('Message',''))[:70]}...</p>
                        </div>""", unsafe_allow_html=True)
            except: st.info("Statistika yuklanmadi")

# ─────────────────────────────────────────────────────
# PAGE: PROFILE
# ─────────────────────────────────────────────────────
elif st.session_state.page == "profile":
    st.markdown(f"""<div class='hero'>
        <div style='background:rgba(255,255,255,0.2);width:90px;height:90px;border-radius:50%;
                    margin:0 auto 15px;line-height:90px;font-size:44px;font-weight:900;border:4px solid rgba(255,255,255,0.5);'>
            {st.session_state.username[0].upper()}</div>
        <h1 style='font-size:34px;margin:0;'>{st.session_state.username}</h1>
        <p style='opacity:0.8;margin:8px 0;'>🟢 Aktiv foydalanuvchi</p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    for col,(ic,val,lb) in zip([c1,c2,c3,c4],[
        ("💬",len(st.session_state.messages),"Xabarlar"),
        ("📁",st.session_state.files_created,"Fayllar"),
        ("⏱",(datetime.now()-st.session_state.login_time).seconds//60 if 'login_time' in st.session_state else 0,"Daqiqa"),
        ("🔥",len(st.session_state.messages)//5+1,"Daraja")
    ]):
        with col:
            st.markdown(f"""<div style='background:white;border-radius:16px;padding:22px;text-align:center;
                border:2px solid #e0f2fe;box-shadow:0 4px 15px rgba(0,0,0,0.05);'>
                <div style='font-size:32px;'>{ic}</div>
                <div style='font-size:28px;font-weight:900;color:#0f172a;'>{val}</div>
                <div style='color:#64748b;font-size:13px;'>{lb}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔗 API Holati")
    apic = st.columns(4)
    for i,(nm,ic,cl) in enumerate([("groq","⚡","#6366f1"),("gemini","✨","#8b5cf6"),("cohere","🌊","#3b82f6"),("mistral","💫","#10b981")]):
        with apic[i]:
            ok = nm in ai_clients
            bg = "#f0fdf4" if ok else "#fef2f2"
            bdr = "#86efac" if ok else "#fca5a5"
            er = api_errors.get(nm,"")
            st.markdown(f"""<div style='background:{bg};border:2px solid {bdr};border-radius:12px;padding:14px;text-align:center;'>
                <div style='font-size:26px;'>{ic}</div>
                <div style='font-weight:700;font-size:14px;'>{nm.title()}</div>
                <div style='font-size:11px;margin-top:3px;'>{"✅ Ulangan" if ok else "❌ Ulanmagan"}</div>
                {f"<div style='font-size:9px;color:#ef4444;margin-top:3px;'>{er[:35]}</div>" if er else ""}
            </div>""", unsafe_allow_html=True)

    if st.button("🔄 API Qayta Ulanish", type="primary", key="prof_reconnect"):
        for k in ['ai_clients','api_errors']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### 🔑 Parol O'zgartirish")
        with st.form("change_pw"):
            op = st.text_input("Eski parol", type="password")
            np_ = st.text_input("Yangi parol (min 6)", type="password")
            cp_ = st.text_input("Tasdiqlash", type="password")
            if st.form_submit_button("🔄 O'zgartirish", type="primary"):
                if len(np_)<6: st.error("❌ Min 6 belgi!")
                elif np_!=cp_: st.error("❌ Parollar mos emas!")
                elif user_db:
                    try:
                        recs = user_db.get_all_records()
                        idx = next((i for i,r in enumerate(recs) if str(r['username'])==st.session_state.username and str(r['password'])==hash_pw(op)), None)
                        if idx is not None:
                            user_db.update_cell(idx+2,2,hash_pw(np_))
                            st.success("✅ Parol o'zgartirildi!")
                        else: st.error("❌ Eski parol noto'g'ri!")
                    except Exception as e: st.error(f"❌ {e}")
    with c2:
        st.markdown("#### 📊 Sessiya Ma'lumotlari")
        if 'login_time' in st.session_state:
            st.markdown(f"""<div style='background:white;border-radius:12px;padding:18px;border:2px solid #e0f2fe;'>
                <p><strong>📅 Kirish:</strong><br>{st.session_state.login_time.strftime('%d.%m.%Y %H:%M')}</p>
                <p><strong>⏱ Sessiya:</strong><br>{(datetime.now()-st.session_state.login_time).seconds//60} daqiqa</p>
                <p><strong>💬 Xabarlar:</strong><br>{len(st.session_state.messages)} ta</p>
                <p><strong>📁 Fayllar:</strong><br>{st.session_state.files_created} ta</p>
                <p><strong>🔗 Ulangan AI:</strong><br>{len(ai_clients)}/4 model</p>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;color:#94a3b8;padding:40px 20px;
            border-top:2px solid #e2e8f0;margin-top:40px;
            background:linear-gradient(180deg,transparent,rgba(99,102,241,0.05));'>
    <p style='font-size:20px;font-weight:700;color:#0f172a;margin:0;'>
        ♾️ Somo AI <span style='color:#6366f1;'>Ultra Pro Max</span>
    </p>
    <p style='margin:8px 0;color:#64748b;'>
        📊 Excel • 📝 Word • 💻 Kod • 🌐 HTML • 📋 CSV • 🧠 Chat
    </p>
    <p style='margin:6px 0;font-size:14px;'>
        ⚡ Groq • ✨ Gemini • 🌊 Cohere • 💫 Mistral — 4x AI Power
    </p>
    <p style='margin:6px 0;font-size:14px;'>
        👨‍💻 Yaratuvchi: <strong>Usmonov Sodiq</strong> &nbsp;|&nbsp;
        👨‍💻 Yordamchi: <strong>Davlatov Mironshoh</strong>
    </p>
    <p style='margin:10px 0 0;font-size:12px;'>
        © 2026 Somo AI Ultra Pro Max v4.0 — Barcha huquqlar himoyalangan
    </p>
</div>
""", unsafe_allow_html=True)
