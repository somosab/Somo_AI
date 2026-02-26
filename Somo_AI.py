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
    from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                                  GradientFill)
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
    page_icon="🌌",
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
/* ── Base ── */
.stApp {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 40%, #ede9fe 100%) !important;
}
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 60%, #312e81 100%) !important;
    border-right: 3px solid #6366f1;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] section,
[data-testid="stSidebar"] .stVerticalBlock { background: transparent !important; }

div[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.07) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
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

/* ── Gradient text ── */
.grad {
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899, #f43f5e);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900;
    animation: gs 5s ease infinite;
}
@keyframes gs { 0%,100%{background-position:0%} 50%{background-position:100%} }

/* ── Hero card ── */
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
    position:absolute;
    top:-50%;left:-50%;
    width:200%;height:200%;
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

/* ── File badge ── */
.file-badge {
    display: inline-block;
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    padding: 8px 18px;
    border-radius: 25px;
    font-weight: 700;
    font-size: 14px;
    margin: 10px 0;
    box-shadow: 0 4px 15px rgba(16,185,129,0.4);
}
.xls-badge { background: linear-gradient(135deg, #10b981, #059669); }
.doc-badge { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.py-badge  { background: linear-gradient(135deg, #f59e0b, #d97706); }
.html-badge{ background: linear-gradient(135deg, #f43f5e, #e11d48); }
.csv-badge { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }

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
.stTabs [data-baseweb="tab"]:hover { border-color: #6366f1; }

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

/* ── Mobile ── */
@media(max-width:768px) {
    .hero { padding: 30px 20px; }
    .feat-card { padding: 20px 15px; }
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 3px; }

/* ── Tool buttons in main area ── */
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
# DB & AI CONNECTIONS
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

try:
    ai = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    ai = None

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
EXCEL_KEYWORDS = [
    "excel", "xlsx", "jadval", "table", "spreadsheet", "budget", "byudjet",
    "hisobot", "report", "moliya", "finance", "data table", "ma'lumotlar jadvali",
    "schedule", "jadval tuz", "ro'yxat", "list", "kassa", "daromad", "xarajat",
    "oylik", "salary", "ish haqi", "sotish", "sales", "inventory", "ombor",
    "statistika", "grafik", "chart", "formula", "hisoblash"
]
WORD_KEYWORDS = [
    "word", "docx", "hujjat", "document", "letter", "maktub", "rezyume",
    "resume", "cv", "shartnoma", "contract", "ariza", "application",
    "taqdimot matni", "hisobot yoz", "biznes reja", "business plan",
    "essay", "insho", "maqola", "article", "diplom", "referat", "kurs ishi"
]
CODE_KEYWORDS = [
    "python kodi", "write code", "kod yoz", "dastur yoz", "script",
    "function yoz", "class yoz", "program yaz", "bot yaz"
]
HTML_KEYWORDS = [
    "html", "website", "web page", "landing page", "veb sahifa", "html kod"
]
CSV_KEYWORDS = [
    "csv", "comma separated", "csv fayl"
]

def detect_intent(text):
    t = text.lower()
    if any(k in t for k in EXCEL_KEYWORDS):
        return "excel"
    if any(k in t for k in WORD_KEYWORDS):
        return "word"
    if any(k in t for k in HTML_KEYWORDS):
        return "html"
    if any(k in t for k in CSV_KEYWORDS):
        return "csv"
    if any(k in t for k in CODE_KEYWORDS):
        return "code"
    return "chat"

# ─────────────────────────────────────────────────────
# FILE GENERATORS
# ─────────────────────────────────────────────────────

def generate_excel(prompt, temperature=0.3):
    """AI yordamida Excel fayl yaratish"""
    if not HAS_OPENPYXL:
        return None, "openpyxl o'rnatilmagan"

    sys = """Sen Excel fayl strukturasini JSON formatida qaytaruvchi ekspертsan.
Foydalanuvchi so'rovi asosida FAQAT quyidagi JSON formatida javob ber, boshqa hech narsa yozma:
{
  "title": "Fayl nomi",
  "sheets": [
    {
      "name": "Varaq nomi",
      "headers": ["Ustun1", "Ustun2", "Ustun3"],
      "header_colors": ["4472C4", "4472C4", "4472C4"],
      "rows": [
        ["qiymat1", "qiymat2", "qiymat3"],
        ["qiymat1", "qiymat2", "=SUM(B2:B10)"]
      ],
      "column_widths": [20, 15, 15],
      "notes": "Qo'shimcha izoh"
    }
  ]
}
Muhim: 
- Haqiqiy va foydali ma'lumotlar bilan to'ldir (kamida 10-15 satr)
- Formulalar ishlat (SUM, AVERAGE, IF, va h.k.)
- Har bir varaq uchun header_colors hex kodda
- Faqat JSON qaytargi, markdown yoki izoh qo'shma"""

    raw = call_ai([
        {"role": "system", "content": sys},
        {"role": "user", "content": prompt}
    ], temperature=temperature, max_tokens=4000)

    # JSON ajratib olish
    raw = re.sub(r'```json|```', '', raw).strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        return None, "AI strukturani to'g'ri qaytarmadi"

    try:
        data = json.loads(match.group())
    except:
        try:
            data = json.loads(raw)
        except Exception as e:
            return None, f"JSON xatosi: {e}"

    # Excel yaratish
    wb = Workbook()
    wb.remove(wb.active)

    THEME_COLORS = [
        ("4F81BD", "DEEAF1"), ("70AD47", "E2EFDA"), ("FF0000", "FFE0E0"),
        ("7030A0", "EAD1FF"), ("FF6600", "FFE5CC"), ("0070C0", "CCE5FF")
    ]

    for si, sheet_data in enumerate(data.get("sheets", [])):
        ws = wb.create_sheet(title=sheet_data.get("name", f"Varaq{si+1}")[:30])
        headers = sheet_data.get("headers", [])
        hcolors = sheet_data.get("header_colors", [])
        col_widths = sheet_data.get("column_widths", [])
        rows_data = sheet_data.get("rows", [])

        theme_h, theme_r = THEME_COLORS[si % len(THEME_COLORS)]

        # Title row
        if "name" in sheet_data:
            ws.merge_cells(start_row=1, start_column=1,
                           end_row=1, end_column=max(len(headers),1))
            title_cell = ws.cell(row=1, column=1, value=sheet_data.get("name",""))
            title_cell.font = Font(bold=True, size=14, color="FFFFFF",
                                   name="Arial")
            title_cell.fill = PatternFill("solid", fgColor=theme_h)
            title_cell.alignment = Alignment(horizontal="center",
                                              vertical="center")
            ws.row_dimensions[1].height = 28

        # Headers
        if headers:
            for ci, h in enumerate(headers, 1):
                c = ws.cell(row=2, column=ci, value=h)
                hc = hcolors[ci-1] if ci-1 < len(hcolors) else theme_h
                c.font = Font(bold=True, size=11, color="FFFFFF", name="Arial")
                c.fill = PatternFill("solid", fgColor=hc)
                c.alignment = Alignment(horizontal="center", vertical="center",
                                        wrap_text=True)
                thin = Side(style="thin", color="FFFFFF")
                c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            ws.row_dimensions[2].height = 22

        # Data rows
        for ri, row in enumerate(rows_data, 3):
            row_color = "FFFFFF" if ri % 2 else theme_r
            for ci, val in enumerate(row, 1):
                c = ws.cell(row=ri, column=ci)
                if isinstance(val, str) and val.startswith("="):
                    c.value = val
                    c.font = Font(color="000000", name="Arial", size=10)
                else:
                    try:
                        c.value = float(val) if isinstance(val, str) and val.replace('.','',1).replace('-','',1).isdigit() else val
                    except:
                        c.value = val
                    c.font = Font(name="Arial", size=10)
                c.fill = PatternFill("solid", fgColor=row_color)
                thin2 = Side(style="thin", color="D0D0D0")
                c.border = Border(left=thin2, right=thin2,
                                   top=thin2, bottom=thin2)
                c.alignment = Alignment(vertical="center", wrap_text=True)
            ws.row_dimensions[ri].height = 18

        # Column widths
        for ci, w in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(ci)].width = max(w, 8)
        if not col_widths and headers:
            for ci in range(1, len(headers)+1):
                ws.column_dimensions[get_column_letter(ci)].width = 18

        # Freeze header
        ws.freeze_panes = "A3"

    if not wb.sheetnames:
        wb.create_sheet("Ma'lumotlar")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    fname = f"{data.get('title','somo_excel')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return buf.getvalue(), fname


def generate_word(prompt, temperature=0.4):
    """AI yordamida Word fayl yaratish"""
    if not HAS_DOCX:
        return None, "python-docx o'rnatilmagan"

    sys = """Sen Word hujjat strukturasini JSON formatida yaratuvchi ekspертsan.
Faqat quyidagi JSON formatida javob ber:
{
  "title": "Hujjat nomi",
  "sections": [
    {
      "type": "heading1",
      "text": "Asosiy sarlavha"
    },
    {
      "type": "heading2",
      "text": "Ikkinchi daraja sarlavha"
    },
    {
      "type": "paragraph",
      "text": "Matn..."
    },
    {
      "type": "bullet",
      "items": ["Element 1", "Element 2", "Element 3"]
    },
    {
      "type": "table",
      "headers": ["Ustun1", "Ustun2"],
      "rows": [["val1","val2"],["val3","val4"]]
    }
  ]
}
Haqiqiy, mazmunli va to'liq kontent yaratgin. Faqat JSON."""

    raw = call_ai([
        {"role": "system", "content": sys},
        {"role": "user", "content": prompt}
    ], temperature=temperature, max_tokens=4000)

    raw = re.sub(r'```json|```', '', raw).strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        return None, "Struktura xatosi"

    try:
        data = json.loads(match.group())
    except Exception as e:
        return None, f"JSON xatosi: {e}"

    doc = Document()

    # Stil sozlamalari
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    # Title
    title_para = doc.add_heading(data.get("title","Hujjat"), level=0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_para.runs[0]
    run.font.size = Pt(22)
    run.font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)

    # Sana
    date_p = doc.add_paragraph(f"Sana: {datetime.now().strftime('%d.%m.%Y')}")
    date_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    date_p.runs[0].font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    date_p.runs[0].font.size = Pt(10)
    doc.add_paragraph()

    for sec in data.get("sections", []):
        t = sec.get("type","paragraph")
        if t == "heading1":
            h = doc.add_heading(sec.get("text",""), level=1)
            h.runs[0].font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)
        elif t == "heading2":
            h = doc.add_heading(sec.get("text",""), level=2)
            h.runs[0].font.color.rgb = RGBColor(0x7C, 0x3A, 0xED)
        elif t == "paragraph":
            p = doc.add_paragraph(sec.get("text",""))
            p.paragraph_format.space_after = Pt(8)
        elif t == "bullet":
            for item in sec.get("items", []):
                doc.add_paragraph(item, style='List Bullet')
        elif t == "numbered":
            for item in sec.get("items", []):
                doc.add_paragraph(item, style='List Number')
        elif t == "table":
            headers = sec.get("headers", [])
            rows = sec.get("rows", [])
            if headers:
                tbl = doc.add_table(rows=1+len(rows), cols=len(headers))
                tbl.style = 'Table Grid'
                hrow = tbl.rows[0]
                for ci, h in enumerate(headers):
                    cell = hrow.cells[ci]
                    cell.text = h
                    cell.paragraphs[0].runs[0].font.bold = True
                    cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255,255,255)
                    from docx.oxml.ns import qn
                    from docx.oxml import OxmlElement
                    tc = cell._tc
                    tcPr = tc.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:val'), 'clear')
                    shd.set(qn('w:color'), 'auto')
                    shd.set(qn('w:fill'), '4F46E5')
                    tcPr.append(shd)
                for ri, row_d in enumerate(rows):
                    row_cells = tbl.rows[ri+1].cells
                    for ci, val in enumerate(row_d):
                        if ci < len(row_cells):
                            row_cells[ci].text = str(val)

        doc.add_paragraph()  # spacer

    # Footer
    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fp.text = f"© {datetime.now().year} Somo AI | {data.get('title','Hujjat')}"
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.runs[0].font.size = Pt(9)
    fp.runs[0].font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    fname = f"{data.get('title','somo_doc')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    return buf.getvalue(), fname


def generate_code(prompt, temperature=0.3):
    sys = """Sen professional dasturchi. Foydalanuvchi so'roviga faqat Python kodi bilan javob ber.
Kod to'liq, ishlaydigan, izohli va best practices bo'yicha bo'lsin.
FAQAT kod ber, tushuntirma yozma."""
    code = call_ai([
        {"role":"system","content":sys},
        {"role":"user","content":prompt}
    ], temperature=temperature, max_tokens=3000)
    # Clean code blocks
    code = re.sub(r'```python|```py|```', '', code).strip()
    fname = f"somo_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    return code.encode('utf-8'), fname


def generate_html(prompt, temperature=0.4):
    sys = """Sen professional web developer. Foydalanuvchi so'roviga to'liq, mukammal, chiroyli HTML/CSS/JS sahifa yarat.
FAQAT HTML kodi ber, boshqa narsa yozma. Inline CSS va JS ishlat."""
    html = call_ai([
        {"role":"system","content":sys},
        {"role":"user","content":prompt}
    ], temperature=temperature, max_tokens=4000)
    html = re.sub(r'```html|```', '', html).strip()
    fname = f"somo_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    return html.encode('utf-8'), fname


def generate_csv(prompt, temperature=0.3):
    sys = """Sen ma'lumotlar ekspersisan. Foydalanuvchi so'roviga asosan CSV format ma'lumot ber.
FAQAT CSV (vergul bilan ajratilgan) ma'lumot ber. Birinchi qator sarlavha bo'lsin.
Kamida 20 satr ma'lumot ber. Boshqa narsa yozma."""
    csv_data = call_ai([
        {"role":"system","content":sys},
        {"role":"user","content":prompt}
    ], temperature=temperature, max_tokens=3000)
    csv_data = re.sub(r'```csv|```', '', csv_data).strip()
    fname = f"somo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return csv_data.encode('utf-8'), fname

# ─────────────────────────────────────────────────────
# SESSION INIT
# ─────────────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user and user_db:
        try:
            recs = user_db.get_all_records()
            ud = next((r for r in recs if str(r['username'])==session_user), None)
            if ud and str(ud.get('status','')).lower()=='active':
                st.session_state.update({
                    'username': session_user,
                    'logged_in': True,
                    'login_time': datetime.now()
                })
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
# LOGIN PAGE
# ─────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("""
    <div class='hero'>
        <h1 style='font-size:52px;font-weight:900;margin:0;'>🌌 Somo AI</h1>
        <h2 style='font-weight:400;opacity:0.9;margin:10px 0;'>Ultra Pro Max</h2>
        <p style='opacity:0.8;font-size:18px;margin:15px 0;'>
            Excel • Word • Kod • HTML • CSV • Chat — Hammasini AI bilan yarating
        </p>
        <div style='display:flex;justify-content:center;gap:20px;flex-wrap:wrap;margin-top:20px;'>
            <span style='background:rgba(255,255,255,0.2);padding:6px 16px;border-radius:20px;font-size:14px;'>⚡ Llama 3.3 70B</span>
            <span style='background:rgba(255,255,255,0.2);padding:6px 16px;border-radius:20px;font-size:14px;'>📊 Excel Generator</span>
            <span style='background:rgba(255,255,255,0.2);padding:6px 16px;border-radius:20px;font-size:14px;'>📝 Word Generator</span>
            <span style='background:rgba(255,255,255,0.2);padding:6px 16px;border-radius:20px;font-size:14px;'>💻 Code Generator</span>
            <span style='background:rgba(255,255,255,0.2);padding:6px 16px;border-radius:20px;font-size:14px;'>🌐 HTML Generator</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        t1, t2, t3 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish", "ℹ️ Haqida"])

        with t1:
            with st.form("login"):
                st.markdown("### Hisobingizga kiring")
                u = st.text_input("👤 Username", key="lu")
                p = st.text_input("🔑 Parol", type="password", key="lp")
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
                st.markdown("### Yangi hisob")
                nu = st.text_input("👤 Username (min 3 belgi)", key="ru")
                np = st.text_input("🔑 Parol (min 6 belgi)", type="password", key="rp")
                nc = st.text_input("🔑 Tasdiqlash", type="password", key="rc")
                agree = st.checkbox("Shartlarga roziman")
                sub2 = st.form_submit_button("✨ Ro'yxatdan o'tish", use_container_width=True, type="primary")
                if sub2:
                    if not agree: st.error("❌ Shartlarga rozilik bering!")
                    elif len(nu)<3: st.error("❌ Username kamida 3 belgi!")
                    elif len(np)<6: st.error("❌ Parol kamida 6 belgi!")
                    elif np!=nc: st.error("❌ Parollar mos emas!")
                    elif user_db:
                        try:
                            recs = user_db.get_all_records()
                            if any(r['username']==nu for r in recs):
                                st.error("❌ Username band!")
                            else:
                                user_db.append_row([nu, hash_pw(np), "active", str(datetime.now())])
                                st.balloons()
                                st.success("🎉 Muvaffaqiyatli! Kirish bo'limiga o'ting.")
                        except Exception as e:
                            st.error(f"❌ {e}")

        with t3:
            st.markdown("""
### 🌌 Somo AI Ultra Pro Max — 20+ Funksiya

**📊 Fayl Generatorlari**
- Excel (xlsx) — jadvallar, formulalar, ranglar
- Word (docx) — hujjatlar, shartnomalar, rezyume
- Python kodi — to'liq ishlaydigan skriptlar
- HTML sahifalar — chiroyli veb sahifalar
- CSV ma'lumotlar — katta datasetlar

**🧠 AI Imkoniyatlar**
- Smart intent detection — so'rovni avtomatik tahlil
- Hujjat tahlili (PDF/DOCX)
- Ko'p tilli javoblar
- Ijodkorlik darajasi sozlamasi

**🎨 Shablonlar**
- Biznes reja, rezyume, maktublar
- Kod generatorlari
- Ta'lim materiallari

**📌 Boshqalar**
- Chat tarixi (JSON export)
- Foydalanuvchi profili
- Feedback tizimi
- Sessiya statistikasi

---
👨‍💻 **Yaratuvchi:** Usmonov Sodiq  
📅 **Versiya:** 3.0 Ultra (2026)
            """)

    st.markdown("""
    <div style='text-align:center;margin-top:50px;color:#94a3b8;'>
        <p>🔒 Ma'lumotlaringiz xavfsiz | ⚡ 24/7 Online | 🌐 AI Powered</p>
        <p style='font-size:13px;margin-top:10px;'>© 2026 Somo AI Ultra Pro Max</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────
# SESSION DEFAULTS
# ─────────────────────────────────────────────────────
defaults = {
    'messages': [],
    'total_msgs': 0,
    'page': 'chat',
    'uploaded_text': '',
    'temperature': 0.6,
    'files_created': 0,
    'ai_personality': 'Aqlli yordamchi'
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:20px;margin-bottom:20px;
                background:rgba(99,102,241,0.15);border-radius:16px;
                border:1px solid rgba(99,102,241,0.3);'>
        <div style='background:linear-gradient(135deg,#6366f1,#ec4899);
                    width:80px;height:80px;border-radius:50%;
                    margin:0 auto;line-height:80px;font-size:36px;
                    color:white;font-weight:900;border:4px solid rgba(255,255,255,0.3);'>
            {st.session_state.username[0].upper()}
        </div>
        <h3 style='margin:12px 0 4px;font-size:18px;'>{st.session_state.username}</h3>
        <span style='background:#10b981;color:white;padding:2px 12px;
                      border-radius:10px;font-size:12px;font-weight:600;'>● Aktiv</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧭 Navigatsiya")

    pages = [
        ("chat",      "💬 Chat AI"),
        ("excel",     "📊 Excel Generator"),
        ("word",      "📝 Word Generator"),
        ("code",      "💻 Kod Generator"),
        ("html",      "🌐 HTML Generator"),
        ("csv",       "📋 CSV Generator"),
        ("templates", "🎨 Shablonlar"),
        ("analyze",   "🔍 Hujjat Tahlili"),
        ("history",   "📜 Chat Tarixi"),
        ("feedback",  "💌 Fikr bildirish"),
        ("profile",   "👤 Profil"),
    ]

    for page_id, label in pages:
        is_active = st.session_state.page == page_id
        style = "primary" if is_active else "secondary"
        if st.button(label, use_container_width=True, key=f"nav_{page_id}", type=style):
            st.session_state.page = page_id
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Statistika")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""<div class='m-card'>
            <div class='m-num'>💬{len(st.session_state.messages)}</div>
            <div class='m-lbl'>Xabarlar</div></div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""<div class='m-card'>
            <div class='m-num'>📁{st.session_state.files_created}</div>
            <div class='m-lbl'>Fayllar</div></div>""", unsafe_allow_html=True)

    if 'login_time' in st.session_state:
        mins = (datetime.now()-st.session_state.login_time).seconds//60
        st.markdown(f"""<div class='m-card' style='margin-top:8px;'>
            <div class='m-num'>⏱{mins}</div>
            <div class='m-lbl'>Daqiqa online</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.session_state.page == "chat":
        st.markdown("### ⚙️ Chat Sozlamalari")
        st.session_state.temperature = st.slider(
            "🌡 Ijodkorlik", 0.0, 1.0, st.session_state.temperature, 0.1)
        st.session_state.ai_personality = st.selectbox(
            "🤖 AI uslubi",
            ["Aqlli yordamchi", "Do'stona", "Rasmiy mutaxassis",
             "Ijodkor yozuvchi", "Texnik ekspert"],
            index=0
        )
        if st.button("🗑 Chatni tozalash", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        if st.session_state.messages:
            data_export = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
            st.download_button("📥 Chat JSON", data_export.encode(),
                               f"chat_{datetime.now().strftime('%Y%m%d')}.json",
                               use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Chiqish", use_container_width=True, type="primary"):
        logout()

# ─────────────────────────────────────────────────────
# HELPERS FOR DOWNLOAD UI
# ─────────────────────────────────────────────────────
def show_file_download(file_bytes, fname, mime, badge_class, label):
    if file_bytes:
        st.session_state.files_created += 1
        st.markdown(f"<div class='notif'>✅ Fayl tayyor! Yuklab olish uchun tugmani bosing.</div>",
                    unsafe_allow_html=True)
        st.download_button(
            label=f"⬇️ {label} yuklab olish",
            data=file_bytes,
            file_name=fname,
            mime=mime,
            use_container_width=True,
            type="primary"
        )
        st.markdown(f"<p style='color:#64748b;font-size:13px;'>📁 Fayl nomi: <code>{fname}</code></p>",
                    unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# PAGE: CHAT
# ─────────────────────────────────────────────────────
if st.session_state.page == "chat":
    if not st.session_state.messages:
        st.markdown(f"""
        <div class='hero' style='padding:40px;margin-bottom:25px;'>
            <h1 style='font-size:38px;margin:0;'>Salom, {st.session_state.username}! 👋</h1>
            <p style='opacity:0.9;font-size:18px;margin:10px 0;'>
                Bugun sizga qanday yordam bera olaman?
            </p>
            <p style='opacity:0.7;font-size:14px;'>
                💡 Excel, Word, Kod, HTML yaratish so'rasangiz — fayl avtomatik tayyorlanadi!
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='feat-grid'>
            <div class='feat-card'>
                <span class='feat-icon'>📊</span>
                <div class='feat-title'>Excel Yaratish</div>
                <div class='feat-desc'>"Oylik byudjet jadvali yarating" — Excel fayl avtomatik yaratiladi</div>
            </div>
            <div class='feat-card'>
                <span class='feat-icon'>📝</span>
                <div class='feat-title'>Word Hujjat</div>
                <div class='feat-desc'>"Rezyume yozing" — professional Word fayl tayyorlanadi</div>
            </div>
            <div class='feat-card'>
                <span class='feat-icon'>💻</span>
                <div class='feat-title'>Kod Yozish</div>
                <div class='feat-desc'>"Python kodi yozing" — to'liq ishlaydigan .py fayl</div>
            </div>
            <div class='feat-card'>
                <span class='feat-icon'>🌐</span>
                <div class='feat-title'>HTML Sahifa</div>
                <div class='feat-desc'>"Landing page yarating" — tayyor HTML fayl</div>
            </div>
            <div class='feat-card'>
                <span class='feat-icon'>📋</span>
                <div class='feat-title'>CSV Ma'lumot</div>
                <div class='feat-desc'>"100 ta mahsulot CSV fayl" — katta dataset</div>
            </div>
            <div class='feat-card'>
                <span class='feat-icon'>🧠</span>
                <div class='feat-title'>Smart Chat</div>
                <div class='feat-desc'>Oddiy savollar uchun aniq va batafsil javoblar</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat tarixi
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "file_data" in msg:
                show_file_download(
                    msg["file_data"]["bytes"],
                    msg["file_data"]["name"],
                    msg["file_data"]["mime"],
                    msg["file_data"]["badge"],
                    msg["file_data"]["label"]
                )

    # Chat input
    if prompt := st.chat_input("💭 Xabar yuboring... (Excel, Word, Kod so'rang!)"):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        save_to_db(st.session_state.username, "User", prompt)

        intent = detect_intent(prompt)

        with st.chat_message("assistant"):
            personalities = {
                "Aqlli yordamchi": "Sen Somo AI — aqlli, professional va foydali yordamchisan. Usmonov Sodiq tomonidan yaratilgan.",
                "Do'stona": "Sen Somo AI — do'stona, samimiy va quvnoq yordamchisan.",
                "Rasmiy mutaxassis": "Sen Somo AI — rasmiy, aniq va professional mutaxassissan.",
                "Ijodkor yozuvchi": "Sen Somo AI — ijodkor, original va kreativ yordamchisan.",
                "Texnik ekspert": "Sen Somo AI — texnik, aniq va batafsil tushuntiruvchi ekspертsan."
            }
            base_sys = personalities.get(st.session_state.ai_personality, personalities["Aqlli yordamchi"])

            if intent == "excel":
                with st.spinner("📊 Excel fayl yaratilmoqda..."):
                    st.markdown("📊 **Excel fayl yaratilmoqda...** Iltimos kuting.")
                    file_bytes, fname = generate_excel(prompt, st.session_state.temperature)
                    if file_bytes and isinstance(file_bytes, bytes):
                        response_text = f"✅ Excel fayl muvaffaqiyatli yaratildi!\n\n📊 **{fname}** faylini yuklab olishingiz mumkin."
                        file_info = {"bytes":file_bytes,"name":fname,
                                     "mime":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                     "badge":"xls-badge","label":"Excel"}
                    else:
                        response_text = f"❌ Excel yaratishda xatolik: {fname}"
                        file_info = None
                    st.markdown(response_text)
                    if file_info:
                        show_file_download(file_info["bytes"],file_info["name"],
                                           file_info["mime"],file_info["badge"],file_info["label"])
                    msg_data = {"role":"assistant","content":response_text}
                    if file_info:
                        msg_data["file_data"] = file_info
                    st.session_state.messages.append(msg_data)

            elif intent == "word":
                with st.spinner("📝 Word hujjat yaratilmoqda..."):
                    st.markdown("📝 **Word hujjat yaratilmoqda...** Iltimos kuting.")
                    file_bytes, fname = generate_word(prompt, st.session_state.temperature)
                    if file_bytes and isinstance(file_bytes, bytes):
                        response_text = f"✅ Word hujjat muvaffaqiyatli yaratildi!\n\n📝 **{fname}** yuklab olishingiz mumkin."
                        file_info = {"bytes":file_bytes,"name":fname,
                                     "mime":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                     "badge":"doc-badge","label":"Word"}
                    else:
                        response_text = f"❌ Word yaratishda xatolik: {fname}"
                        file_info = None
                    st.markdown(response_text)
                    if file_info:
                        show_file_download(file_info["bytes"],file_info["name"],
                                           file_info["mime"],file_info["badge"],file_info["label"])
                    msg_data = {"role":"assistant","content":response_text}
                    if file_info:
                        msg_data["file_data"] = file_info
                    st.session_state.messages.append(msg_data)

            elif intent == "code":
                with st.spinner("💻 Kod yozilmoqda..."):
                    code_bytes, fname = generate_code(prompt, st.session_state.temperature)
                    code_text = code_bytes.decode('utf-8')
                    response_text = f"✅ Python kod tayyor!\n\n```python\n{code_text[:1500]}{'...' if len(code_text)>1500 else ''}\n```"
                    st.markdown(response_text)
                    st.download_button("⬇️ .py fayl yuklab olish", code_bytes, fname,
                                       "text/x-python", use_container_width=True, type="primary")
                    st.session_state.messages.append({"role":"assistant","content":response_text})

            elif intent == "html":
                with st.spinner("🌐 HTML sahifa yaratilmoqda..."):
                    html_bytes, fname = generate_html(prompt, st.session_state.temperature)
                    html_text = html_bytes.decode('utf-8')
                    response_text = f"✅ HTML sahifa tayyor!\n\n```html\n{html_text[:1000]}...\n```"
                    st.markdown(response_text)
                    st.download_button("⬇️ HTML yuklab olish", html_bytes, fname,
                                       "text/html", use_container_width=True, type="primary")
                    st.session_state.files_created += 1
                    st.session_state.messages.append({"role":"assistant","content":response_text})

            elif intent == "csv":
                with st.spinner("📋 CSV ma'lumot yaratilmoqda..."):
                    csv_bytes, fname = generate_csv(prompt, st.session_state.temperature)
                    response_text = f"✅ CSV fayl tayyor! **{fname}**"
                    st.markdown(response_text)
                    st.download_button("⬇️ CSV yuklab olish", csv_bytes, fname,
                                       "text/csv", use_container_width=True, type="primary")
                    st.session_state.files_created += 1
                    st.session_state.messages.append({"role":"assistant","content":response_text})

            else:
                # Normal chat
                with st.spinner("🤔 O'ylayapman..."):
                    sys_msg = f"""{base_sys}
Har doim aniq, tushunarli va foydali javob ber.
Matematika formulalarini LaTeX ($...$) formatida yoz.
Javobni strukturalashtirilgan va o'qishga qulay qil."""

                    msgs = [{"role":"system","content":sys_msg}]
                    if st.session_state.uploaded_text:
                        msgs.append({"role":"system","content":
                            f"Yuklangan hujjat:\n{st.session_state.uploaded_text[:4000]}"})
                    for m in st.session_state.messages[-16:]:
                        msgs.append({"role":m["role"],"content":m["content"]})

                    response = call_ai(msgs, st.session_state.temperature)
                    st.markdown(response)
                    st.session_state.messages.append({"role":"assistant","content":response})
                    save_to_db("Somo AI","Assistant",response)

        st.session_state.total_msgs += 1
        st.rerun()

# ─────────────────────────────────────────────────────
# PAGE: EXCEL GENERATOR (DEDICATED)
# ─────────────────────────────────────────────────────
elif st.session_state.page == "excel":
    st.markdown("""
    <div class='hero'>
        <h1 style='font-size:42px;'>📊 Excel Generator</h1>
        <p style='opacity:0.9;font-size:18px;'>Xohlagan jadvalni AI bilan yarating</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='feat-grid'>
        <div class='feat-card'><span class='feat-icon'>💰</span><div class='feat-title'>Byudjet Jadvali</div></div>
        <div class='feat-card'><span class='feat-icon'>📦</span><div class='feat-title'>Inventar Ro'yxati</div></div>
        <div class='feat-card'><span class='feat-icon'>👥</span><div class='feat-title'>Xodimlar Jadvali</div></div>
        <div class='feat-card'><span class='feat-icon'>📈</span><div class='feat-title'>Savdo Hisoboti</div></div>
        <div class='feat-card'><span class='feat-icon'>📅</span><div class='feat-title'>Ish Jadvali</div></div>
        <div class='feat-card'><span class='feat-icon'>🎓</span><div class='feat-title'>Talabalar Baholari</div></div>
    </div>
    """, unsafe_allow_html=True)

    examples = [
        "12 oylik moliyaviy byudjet jadvali: daromad, xarajat, foyda",
        "100 ta mahsulot inventar ro'yxati: nomi, miqdori, narxi, jami",
        "Xodimlar ish haqi jadvali: ism, lavozim, maosh, soliq, sof",
        "Talabalar baholar jadvali: 5 ta fan, o'rtacha baho, reyting",
        "Haftalik ish jadvali: xodimlar va vazifalar",
        "Savdo hisoboti: oylar, mahsulotlar, daromad, maqsad, foiz"
    ]

    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    for i, ex in enumerate(examples):
        with cols[i%3]:
            if st.button(f"📋 {ex[:40]}...", key=f"ex_{i}", use_container_width=True):
                st.session_state.excel_prompt = ex

    ex_prompt = st.text_area(
        "📝 Excel jadval tavsifi:",
        value=st.session_state.get("excel_prompt",""),
        placeholder="Masalan: 12 oylik byudjet jadvali, daromad va xarajatlar, formulalar bilan",
        height=120,
        key="excel_input"
    )

    c1, c2 = st.columns([3,1])
    with c2:
        temp = st.slider("Aniqlik", 0.0, 0.8, 0.2, 0.1, key="excel_temp")
    with c1:
        gen_btn = st.button("🚀 Excel Yaratish", use_container_width=True, type="primary", key="gen_excel")

    if gen_btn and ex_prompt:
        with st.spinner("📊 Excel yaratilmoqda... (10-30 soniya)"):
            progress = st.progress(0)
            for i in range(0, 80, 20):
                time.sleep(0.3)
                progress.progress(i)
            file_bytes, fname = generate_excel(ex_prompt, temp)
            progress.progress(100)

            if file_bytes and isinstance(file_bytes, bytes):
                st.success(f"✅ Excel fayl tayyor!")
                show_file_download(file_bytes, fname,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "xls-badge", "Excel")
            else:
                st.error(f"❌ Xatolik: {fname}")
    elif gen_btn:
        st.warning("⚠️ Jadval tavsifini kiriting!")

# ─────────────────────────────────────────────────────
# PAGE: WORD GENERATOR
# ─────────────────────────────────────────────────────
elif st.session_state.page == "word":
    st.markdown("""
    <div class='hero'>
        <h1 style='font-size:42px;'>📝 Word Generator</h1>
        <p style='opacity:0.9;font-size:18px;'>Professional hujjatlarni AI bilan yarating</p>
    </div>
    """, unsafe_allow_html=True)

    word_examples = [
        "Professional rezyume: dasturchi, 3 yil tajriba",
        "Biznes xat: hamkorlik taklifi",
        "Ijara shartnomasi: standart shakl",
        "Ishga qabul qilish buyrug'i",
        "Kurs ishi kirish qismi: sun'iy intellekt mavzusi",
        "Marketing strategiya hujjati"
    ]

    col1, col2, col3 = st.columns(3)
    cols_w = [col1, col2, col3]
    for i, ex in enumerate(word_examples):
        with cols_w[i%3]:
            if st.button(f"📄 {ex[:35]}...", key=f"wex_{i}", use_container_width=True):
                st.session_state.word_prompt = ex

    word_prompt = st.text_area(
        "📝 Hujjat tavsifi:",
        value=st.session_state.get("word_prompt",""),
        placeholder="Masalan: Python dasturchi uchun professional rezyume, 5 yil tajriba, AI loyihalari",
        height=120,
        key="word_input"
    )

    gen_word = st.button("🚀 Word Yaratish", use_container_width=True, type="primary", key="gen_word")

    if gen_word and word_prompt:
        with st.spinner("📝 Word hujjat yaratilmoqda..."):
            progress = st.progress(0)
            for i in range(0, 80, 25):
                time.sleep(0.3)
                progress.progress(i)
            file_bytes, fname = generate_word(word_prompt)
            progress.progress(100)
            if file_bytes and isinstance(file_bytes, bytes):
                st.success("✅ Word hujjat tayyor!")
                show_file_download(file_bytes, fname,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "doc-badge", "Word")
            else:
                st.error(f"❌ Xatolik: {fname}")
    elif gen_word:
        st.warning("⚠️ Hujjat tavsifini kiriting!")

# ─────────────────────────────────────────────────────
# PAGE: CODE GENERATOR
# ─────────────────────────────────────────────────────
elif st.session_state.page == "code":
    st.markdown("""
    <div class='hero'>
        <h1 style='font-size:42px;'>💻 Kod Generator</h1>
        <p style='opacity:0.9;font-size:18px;'>Professional Python kodi — tayyor faylda</p>
    </div>
    """, unsafe_allow_html=True)

    code_examples = [
        "Streamlit dashboard - savdo statistikasi",
        "FastAPI REST API - foydalanuvchi tizimi",
        "Telegram bot - xabar yuboruvchi",
        "Web scraper - narxlarni kuzatish",
        "Machine learning - tasniflovchi model",
        "File organizer - papkalarni tartiblovchi"
    ]

    col1, col2, col3 = st.columns(3)
    c3 = [col1, col2, col3]
    for i, ex in enumerate(code_examples):
        with c3[i%3]:
            if st.button(f"💡 {ex}", key=f"cex_{i}", use_container_width=True):
                st.session_state.code_prompt = ex

    code_prompt = st.text_area(
        "📝 Kod tavsifi:",
        value=st.session_state.get("code_prompt",""),
        placeholder="Masalan: Telegram bot yasang, foydalanuvchi xabar yuborsa avtomatik javob bersin",
        height=120,
        key="code_input"
    )

    c1, c2 = st.columns([3,1])
    with c2:
        code_temp = st.slider("Ijodkorlik", 0.0, 0.6, 0.1, 0.1, key="code_temp")

    gen_code = st.button("🚀 Kod Yaratish", use_container_width=True, type="primary", key="gen_code")

    if gen_code and code_prompt:
        with st.spinner("💻 Kod yozilmoqda..."):
            code_bytes, fname = generate_code(code_prompt, code_temp)
            code_text = code_bytes.decode('utf-8')
            st.success("✅ Kod tayyor!")
            st.code(code_text, language="python")
            st.download_button("⬇️ .py Fayl Yuklab Olish", code_bytes, fname,
                               "text/x-python", use_container_width=True, type="primary")
            st.session_state.files_created += 1
    elif gen_code:
        st.warning("⚠️ Kod tavsifini kiriting!")

# ─────────────────────────────────────────────────────
# PAGE: HTML GENERATOR
# ─────────────────────────────────────────────────────
elif st.session_state.page == "html":
    st.markdown("""
    <div class='hero'>
        <h1 style='font-size:42px;'>🌐 HTML Generator</h1>
        <p style='opacity:0.9;font-size:18px;'>Chiroyli veb sahifalar — bitta faylda</p>
    </div>
    """, unsafe_allow_html=True)

    html_examples = [
        "Portfolio sahifa - dasturchi uchun",
        "Restaurant menu - chiroyli dizayn",
        "Landing page - mahsulot reklamasi",
        "Dashboard - statistika ko'rsatish",
        "Login sahifa - modern UI",
        "Blog post sahifasi"
    ]

    col1, col2, col3 = st.columns(3)
    ch = [col1, col2, col3]
    for i, ex in enumerate(html_examples):
        with ch[i%3]:
            if st.button(f"🌐 {ex}", key=f"hex_{i}", use_container_width=True):
                st.session_state.html_prompt = ex

    html_prompt = st.text_area(
        "📝 Sahifa tavsifi:",
        value=st.session_state.get("html_prompt",""),
        placeholder="Masalan: Zamonaviy portfolio sahifasi, qorong'i tema, animatsiyalar bilan",
        height=120,
        key="html_input"
    )

    gen_html = st.button("🚀 HTML Yaratish", use_container_width=True, type="primary", key="gen_html")

    if gen_html and html_prompt:
        with st.spinner("🌐 HTML sahifa yaratilmoqda..."):
            html_bytes, fname = generate_html(html_prompt, 0.5)
            html_text = html_bytes.decode('utf-8')
            st.success("✅ HTML sahifa tayyor!")
            with st.expander("📄 HTML kodini ko'rish"):
                st.code(html_text[:3000]+"..." if len(html_text)>3000 else html_text, language="html")
            st.download_button("⬇️ HTML Yuklab Olish", html_bytes, fname,
                               "text/html", use_container_width=True, type="primary")
            st.markdown("""
            <div style='background:linear-gradient(135deg,#f0f9ff,#e0f2fe);
                        border-radius:12px;padding:15px;margin:10px 0;
                        border:2px solid #bae6fd;'>
                💡 <strong>Maslahat:</strong> Faylni brauzerda ochish uchun yuklab oling va ikki marta bosing.
            </div>
            """, unsafe_allow_html=True)
            st.session_state.files_created += 1
    elif gen_html:
        st.warning("⚠️ Sahifa tavsifini kiriting!")

# ─────────────────────────────────────────────────────
# PAGE: CSV GENERATOR
# ─────────────────────────────────────────────────────
elif st.session_state.page == "csv":
    st.markdown("""
    <div class='hero'>
        <h1 style='font-size:42px;'>📋 CSV Generator</h1>
        <p style='opacity:0.9;font-size:18px;'>Katta datasetlar — tezda tayyor</p>
    </div>
    """, unsafe_allow_html=True)

    csv_examples = [
        "100 ta mahsulot: nomi, narxi, kategoriyasi, miqdori",
        "50 ta xodim: ism, familiya, lavozim, maosh, bo'lim",
        "200 ta talaba: ism, guruh, baholar, o'rtacha",
        "Dunyo mamlakatlari: nomi, poytaxti, aholisi, YIM",
        "Top 100 dasturlash tillari: nomi, turi, yaratilgan yil",
        "E-commerce buyurtmalar: ID, mahsulot, miqdor, sana, holat"
    ]

    col1, col2, col3 = st.columns(3)
    cc = [col1, col2, col3]
    for i, ex in enumerate(csv_examples):
        with cc[i%3]:
            if st.button(f"📋 {ex[:35]}...", key=f"csv_ex_{i}", use_container_width=True):
                st.session_state.csv_prompt = ex

    csv_prompt = st.text_area(
        "📝 Ma'lumotlar tavsifi:",
        value=st.session_state.get("csv_prompt",""),
        placeholder="Masalan: 100 ta O'zbekiston shahri: nomi, viloyati, aholisi, maydoni",
        height=120,
        key="csv_input"
    )

    gen_csv = st.button("🚀 CSV Yaratish", use_container_width=True, type="primary", key="gen_csv")

    if gen_csv and csv_prompt:
        with st.spinner("📋 CSV ma'lumotlar yaratilmoqda..."):
            csv_bytes, fname = generate_csv(csv_prompt)
            try:
                df_preview = pd.read_csv(io.BytesIO(csv_bytes))
                st.success(f"✅ CSV tayyor! {len(df_preview)} satr, {len(df_preview.columns)} ustun")
                st.dataframe(df_preview.head(10), use_container_width=True)
            except:
                st.success("✅ CSV fayl tayyor!")
            st.download_button("⬇️ CSV Yuklab Olish", csv_bytes, fname,
                               "text/csv", use_container_width=True, type="primary")
            st.session_state.files_created += 1
    elif gen_csv:
        st.warning("⚠️ Ma'lumotlar tavsifini kiriting!")

# ─────────────────────────────────────────────────────
# PAGE: TEMPLATES
# ─────────────────────────────────────────────────────
elif st.session_state.page == "templates":
    st.markdown("""
    <div class='hero'>
        <h1 style='font-size:42px;'>🎨 Shablonlar Markazi</h1>
        <p style='opacity:0.9;font-size:18px;'>Tayyor shablonlar bilan ishlashni tezlashtiring</p>
    </div>
    """, unsafe_allow_html=True)

    TEMPLATES = {
        "📊 Biznes": [
            {"title":"💰 Oylik Byudjet","prompt":"12 oylik moliyaviy byudjet Excel jadvali: daromad manbalari, har oylik xarajatlar (ish haqi, ijara, kommunal, reklama), sof foyda, formulalar bilan","type":"excel"},
            {"title":"📈 Savdo Hisoboti","prompt":"Oylik savdo hisobot Excel: har bir mahsulot uchun maqsad va haqiqiy savdo, foiz bajarilishi, grafik uchun ma'lumotlar","type":"excel"},
            {"title":"📋 Biznes Reja","prompt":"Yangi IT kompaniya uchun to'liq biznes reja Word hujjati: ijroiya xulosa, bozor tahlili, raqobatchilar, moliyaviy prognoz, marketing strategiya","type":"word"},
            {"title":"🤝 Hamkorlik Xati","prompt":"Professional hamkorlik taklifi maktubi Word hujjat: kompaniya taqdimoti, taklif, shartlar, imzo qismi","type":"word"},
        ],
        "💻 Dasturlash": [
            {"title":"🤖 Telegram Bot","prompt":"To'liq ishlaydigan Python Telegram bot: start komandasi, echo funksiya, keyboard tugmalari, error handling, aiogram v3 bilan","type":"code"},
            {"title":"🌐 FastAPI CRUD","prompt":"FastAPI da to'liq CRUD API: foydalanuvchilar uchun create/read/update/delete, Pydantic modellari, swagger dokumentatsiya","type":"code"},
            {"title":"📊 Data Tahlil","prompt":"Pandas va matplotlib bilan ma'lumotlar tahlil skripti: CSV o'qish, tozalash, statistika, grafik chizish, hisobot yaratish","type":"code"},
            {"title":"🌐 Portfolio Sayt","prompt":"Zamonaviy web developer portfolio sahifasi: hero section, skills, projects, contact form, dark theme, smooth animations, professional dizayn","type":"html"},
        ],
        "📚 Ta'lim": [
            {"title":"📖 Dars Rejasi","prompt":"Informatika: Python dasturlash asoslari bo'yicha 45 daqiqalik dars rejasi Word hujjat: maqsadlar, kirish, asosiy qism, amaliy mashq, uyga vazifa","type":"word"},
            {"title":"📝 Test Savollari","prompt":"Python dasturlash asoslari bo'yicha 20 ta test savoli va javoblar Excel jadval: savol, 4 ta variant, to'g'ri javob, mavzu","type":"excel"},
            {"title":"🎓 Talabalar Jadvali","prompt":"30 ta talaba uchun baholar jadvali Excel: ism, 6 ta fan bahosi, o'rtacha baho, reyting, davomad foizi, formulalar","type":"excel"},
            {"title":"📚 Kurs Ishi","prompt":"Kurs ishi Word hujjati: mavzu - Zamonaviy sun'iy intellekt texnologiyalari. Kirish, 3 ta bob, xulosa, adabiyotlar ro'yxati, 20+ sahifa","type":"word"},
        ],
        "👤 Shaxsiy": [
            {"title":"📄 Rezyume","prompt":"Python backend dasturchi uchun professional rezyume Word hujjat: shaxsiy ma'lumot, tajriba, ko'nikmalar, ta'lim, portfolio, zamonaviy format","type":"word"},
            {"title":"📅 Haftalik Reja","prompt":"Haftalik vazifalar reja Excel: 7 kun, har kuni soatlar, vazifalar, ustuvorlik, holat, bajarilish foizi","type":"excel"},
            {"title":"💪 Sport Jadvali","prompt":"3 oylik sport mashg'ulotlari jadvali Excel: har kuni mashqlar, takroriylik, og'irlik, progres kuzatish","type":"excel"},
            {"title":"💰 Shaxsiy Byudjet","prompt":"Shaxsiy oylik byudjet Excel: daromadlar, majburiy xarajatlar, ixtiyoriy xarajatlar, jamg'arma maqsadi, formulalar","type":"excel"},
        ]
    }

    sel_cat = st.selectbox("📁 Kategoriya:", list(TEMPLATES.keys()), key="tmpl_cat")
    st.markdown("---")

    tmpl_cols = st.columns(2)
    for i, tmpl in enumerate(TEMPLATES[sel_cat]):
        with tmpl_cols[i%2]:
            with st.container():
                st.markdown(f"""
                <div style='background:white;border-radius:16px;padding:20px;
                            border:2px solid #e2e8f0;margin-bottom:15px;
                            box-shadow:0 4px 15px rgba(0,0,0,0.06);'>
                    <h3 style='color:#0f172a;margin:0 0 8px;'>{tmpl['title']}</h3>
                    <span style='background:{"#10b981" if tmpl["type"]=="excel" else "#3b82f6" if tmpl["type"]=="word" else "#f59e0b" if tmpl["type"]=="code" else "#f43f5e"};
                                 color:white;padding:3px 10px;border-radius:10px;font-size:12px;font-weight:600;'>
                        {"📊 Excel" if tmpl["type"]=="excel" else "📝 Word" if tmpl["type"]=="word" else "💻 Kod" if tmpl["type"]=="code" else "🌐 HTML"}
                    </span>
                    <p style='color:#64748b;font-size:13px;margin-top:10px;'>{tmpl["prompt"][:120]}...</p>
                </div>
                """, unsafe_allow_html=True)

                btn_cols = st.columns(2)
                with btn_cols[0]:
                    if st.button("🚀 Yaratish", key=f"tmpl_gen_{sel_cat}_{i}", use_container_width=True, type="primary"):
                        t_type = tmpl["type"]
                        with st.spinner(f"⏳ Yaratilmoqda..."):
                            if t_type == "excel":
                                fb, fn = generate_excel(tmpl["prompt"])
                                if fb and isinstance(fb, bytes):
                                    st.download_button(f"⬇️ Excel", fb, fn,
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key=f"dl_tmpl_{i}")
                                    st.session_state.files_created += 1
                            elif t_type == "word":
                                fb, fn = generate_word(tmpl["prompt"])
                                if fb and isinstance(fb, bytes):
                                    st.download_button(f"⬇️ Word", fb, fn,
                                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        key=f"dl_tmpl_{i}")
                                    st.session_state.files_created += 1
                            elif t_type == "code":
                                fb, fn = generate_code(tmpl["prompt"])
                                st.download_button(f"⬇️ .py", fb, fn, "text/x-python",
                                    key=f"dl_tmpl_{i}")
                                st.session_state.files_created += 1
                            elif t_type == "html":
                                fb, fn = generate_html(tmpl["prompt"])
                                st.download_button(f"⬇️ HTML", fb, fn, "text/html",
                                    key=f"dl_tmpl_{i}")
                                st.session_state.files_created += 1

                with btn_cols[1]:
                    if st.button("💬 Chatga", key=f"tmpl_chat_{sel_cat}_{i}", use_container_width=True):
                        st.session_state.messages.append({"role":"user","content":tmpl["prompt"]})
                        st.session_state.page = "chat"
                        st.rerun()

# ─────────────────────────────────────────────────────
# PAGE: ANALYZE
# ─────────────────────────────────────────────────────
elif st.session_state.page == "analyze":
    st.markdown("""
    <div class='hero'>
        <h1 style='font-size:42px;'>🔍 Hujjat Tahlili</h1>
        <p style='opacity:0.9;font-size:18px;'>PDF va Word fayllarni AI bilan tahlil qiling</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])

    with col1:
        st.markdown("### 📂 Fayl Yuklash")
        uploaded = st.file_uploader(
            "PDF yoki DOCX fayl",
            type=["pdf","docx"],
            key="analyze_upload"
        )

        if uploaded:
            with st.spinner("📄 Fayl o'qilmoqda..."):
                text = process_doc(uploaded)
                st.session_state.uploaded_text = text

            if text:
                st.success(f"✅ {uploaded.name}")
                st.info(f"📊 {len(text):,} belgi, ~{len(text.split()):,} so'z")
                with st.expander("📄 Matnni ko'rish"):
                    st.text(text[:2000] + ("..." if len(text)>2000 else ""))
            else:
                st.error("❌ Fayl o'qilmadi")

    with col2:
        st.markdown("### 🧠 Tahlil Amaliyotlari")

        if st.session_state.uploaded_text:
            actions = {
                "📝 Qisqa xulosa": "Ushbu hujjatni 3-5 ta asosiy band bilan qisqa xulosasini yoz.",
                "🔑 Asosiy g'oyalar": "Hujjatdagi 5-10 ta eng muhim g'oya va faktlarni ajratib chiqar.",
                "❓ Savol-Javob": "Hujjat bo'yicha 10 ta muhim savol va javoblarni tuzib ber.",
                "🌐 Inglizchaga tarjima": "Hujjat mazmunini ingliz tiliga tarjima qil.",
                "📊 Statistika ajratish": "Hujjatdagi barcha raqamlar, statistika va ma'lumotlarni jadval ko'rinishida ko'rsat.",
                "✅ Action items": "Hujjatdan amaliy vazifalar va keyingi qadamlarni ajratib ber."
            }

            for action, prompt in actions.items():
                if st.button(action, key=f"act_{action}", use_container_width=True):
                    with st.spinner("🤔 Tahlil qilinmoqda..."):
                        result = call_ai([
                            {"role":"system","content":"Sen hujjat tahlilchisan. Aniq va foydali javoblar ber."},
                            {"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:4000]}\n\n{prompt}"}
                        ])
                        st.markdown(f"### {action}")
                        st.markdown(result)

            # Custom savol
            st.markdown("---")
            custom_q = st.text_input("🔍 O'z savolingizni yozing:", key="custom_q")
            if st.button("🔍 Hujjatdan Qidirish", use_container_width=True, type="primary"):
                if custom_q:
                    with st.spinner("🤔 Qidirilmoqda..."):
                        result = call_ai([
                            {"role":"system","content":"Hujjat asosida aniq javob ber."},
                            {"role":"user","content":f"Hujjat:\n{st.session_state.uploaded_text[:4000]}\n\nSavol: {custom_q}"}
                        ])
                        st.markdown(result)
        else:
            st.info("👆 Avval chap tomonda fayl yuklang")
            st.markdown("""
            **Qo'llab-quvvatlanadigan formatlar:**
            - 📄 PDF fayllar
            - 📝 Word (.docx) fayllar

            **Tahlil imkoniyatlari:**
            - Qisqa xulosa
            - Asosiy g'oyalar
            - Savol-javob
            - Tarjima
            - Statistika ajratish
            - Custom savollar
            """)

# ─────────────────────────────────────────────────────
# PAGE: HISTORY
# ─────────────────────────────────────────────────────
elif st.session_state.page == "history":
    st.markdown("""
    <div class='hero'>
        <h1 style='font-size:42px;'>📜 Chat Tarixi</h1>
        <p style='opacity:0.9;font-size:18px;'>Barcha suhbatlaringiz</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.messages:
        col1, col2, col3 = st.columns(3)
        with col1:
            user_msgs = [m for m in st.session_state.messages if m["role"]=="user"]
            st.metric("👤 Sizning xabarlar", len(user_msgs))
        with col2:
            ai_msgs = [m for m in st.session_state.messages if m["role"]=="assistant"]
            st.metric("🤖 AI javoblar", len(ai_msgs))
        with col3:
            st.metric("📁 Yaratilgan fayllar", st.session_state.files_created)

        # Search
        search = st.text_input("🔍 Xabarlarda qidirish:", key="history_search")
        show_msgs = st.session_state.messages

        if search:
            show_msgs = [m for m in show_msgs if search.lower() in m.get("content","").lower()]
            st.info(f"🔍 '{search}' uchun {len(show_msgs)} ta natija topildi")

        # Export
        col1, col2 = st.columns(2)
        with col1:
            export_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
            st.download_button("📥 JSON Export", export_json.encode(),
                               f"chat_history_{datetime.now().strftime('%Y%m%d')}.json",
                               "application/json", use_container_width=True)
        with col2:
            # Text export
            text_export = "\n\n".join([
                f"[{m['role'].upper()}]\n{m['content']}"
                for m in st.session_state.messages
            ])
            st.download_button("📄 TXT Export", text_export.encode(),
                               f"chat_{datetime.now().strftime('%Y%m%d')}.txt",
                               "text/plain", use_container_width=True)

        st.markdown("---")

        # Show messages in reverse
        for msg in reversed(show_msgs[-50:]):
            role_icon = "👤" if msg["role"]=="user" else "🤖"
            bg = "#EEF2FF" if msg["role"]=="user" else "#F0FDF4"
            border = "#6366f1" if msg["role"]=="user" else "#10b981"
            st.markdown(f"""
            <div style='background:{bg};border-left:4px solid {border};
                        padding:12px 16px;border-radius:8px;margin:8px 0;'>
                <strong>{role_icon} {msg["role"].title()}</strong>
                <p style='margin:6px 0 0;color:#374151;font-size:14px;'>
                    {msg["content"][:300]}{"..." if len(msg.get("content",""))>300 else ""}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💬 Hali chat tarixi yo'q. Chat sahifasiga o'ting!")

# ─────────────────────────────────────────────────────
# PAGE: FEEDBACK
# ─────────────────────────────────────────────────────
elif st.session_state.page == "feedback":
    st.markdown("""
    <div class='hero'>
        <h1 style='font-size:42px;'>💌 Fikr-Mulohazalar</h1>
        <p style='opacity:0.9;font-size:18px;'>Sizning fikringiz bizni yaxshiroq qiladi!</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3,2])

    with col1:
        with st.form("feedback_form"):
            st.markdown("### ⭐ Baholang va Fikr Bildiring")
            rating = st.select_slider(
                "Baho:",
                options=[1,2,3,4,5],
                value=5,
                format_func=lambda x: "⭐"*x
            )
            st.markdown(f"<p style='font-size:48px;text-align:center;'>{'⭐'*rating}</p>",
                        unsafe_allow_html=True)
            category = st.selectbox("📂 Kategoriya:",
                ["Umumiy fikr","Xato haqida","Yangi funksiya taklifi",
                 "Dizayn haqida","Tezlik muammosi","Boshqa"])
            message = st.text_area("✍️ Xabaringiz:", height=130,
                                   placeholder="Fikr-mulohazalaringizni yozing...")
            email = st.text_input("📧 Email (ixtiyoriy):", placeholder="email@example.com")

            submitted = st.form_submit_button("📤 Yuborish", use_container_width=True, type="primary")

            if submitted:
                if not message or len(message)<10:
                    st.error("❌ Kamida 10 ta belgidan iborat xabar yozing!")
                elif fb_db:
                    try:
                        fb_db.append_row([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            st.session_state.username, rating, category,
                            message, email or "N/A", "Yangi"
                        ])
                        st.balloons()
                        st.markdown("""<div class='notif'>
                            ✅ Rahmat! Fikringiz muvaffaqiyatli yuborildi. 🙏
                        </div>""", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ {e}")

    with col2:
        st.markdown("### 📊 Statistika")
        if fb_db:
            try:
                all_fb = fb_db.get_all_records()
                if len(all_fb) > 0:
                    st.metric("📨 Jami fikrlar", len(all_fb))
                    ratings_list = [int(f.get('Rating',5)) for f in all_fb if f.get('Rating')]
                    if ratings_list:
                        avg = sum(ratings_list)/len(ratings_list)
                        st.metric("⭐ O'rtacha baho", f"{avg:.1f}/5")
                    st.markdown("---")
                    st.markdown("**📋 Oxirgi 5 ta fikr:**")
                    for fb in all_fb[-5:]:
                        st.markdown(f"""
                        <div style='background:#f8fafc;border-radius:8px;
                                    padding:10px;margin:5px 0;border:1px solid #e2e8f0;'>
                            <strong>{'⭐'*int(fb.get('Rating',5))}</strong>
                            <span style='color:#6366f1;font-size:13px;'> — {fb.get('Username','')}</span>
                            <p style='color:#374151;font-size:13px;margin:5px 0 0;'>
                                {str(fb.get('Message',''))[:80]}...
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            except:
                st.info("Statistika yuklanmadi")

# ─────────────────────────────────────────────────────
# PAGE: PROFILE
# ─────────────────────────────────────────────────────
elif st.session_state.page == "profile":
    st.markdown(f"""
    <div class='hero'>
        <div style='background:rgba(255,255,255,0.2);width:100px;height:100px;
                    border-radius:50%;margin:0 auto 20px;line-height:100px;
                    font-size:50px;font-weight:900;border:4px solid rgba(255,255,255,0.5);'>
            {st.session_state.username[0].upper()}
        </div>
        <h1 style='font-size:36px;margin:0;'>{st.session_state.username}</h1>
        <p style='opacity:0.8;margin:8px 0;'>🟢 Aktiv foydalanuvchi</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    stats = [
        ("💬", len(st.session_state.messages), "Xabarlar"),
        ("📁", st.session_state.files_created, "Fayllar"),
        ("⏱", (datetime.now()-st.session_state.login_time).seconds//60 if 'login_time' in st.session_state else 0, "Daqiqa"),
        ("🔥", len(st.session_state.messages)//5 + 1, "Daraja"),
    ]
    for col, (icon, val, lbl) in zip([col1,col2,col3,col4], stats):
        with col:
            st.markdown(f"""
            <div style='background:white;border-radius:16px;padding:25px;
                        text-align:center;border:2px solid #e0f2fe;
                        box-shadow:0 4px 15px rgba(0,0,0,0.06);'>
                <div style='font-size:36px;'>{icon}</div>
                <div style='font-size:32px;font-weight:900;color:#0f172a;'>{val}</div>
                <div style='color:#64748b;font-size:14px;'>{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Profil Sozlamalari")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔑 Parolni o'zgartirish")
        with st.form("change_pw"):
            old_pw = st.text_input("Eski parol", type="password")
            new_pw = st.text_input("Yangi parol (min 6 belgi)", type="password")
            conf_pw = st.text_input("Tasdiqlash", type="password")
            if st.form_submit_button("🔄 O'zgartirish", type="primary"):
                if len(new_pw)<6:
                    st.error("❌ Yangi parol kamida 6 belgi!")
                elif new_pw!=conf_pw:
                    st.error("❌ Parollar mos emas!")
                elif user_db:
                    try:
                        recs = user_db.get_all_records()
                        idx = next((i for i,r in enumerate(recs)
                                    if str(r['username'])==st.session_state.username
                                    and str(r['password'])==hash_pw(old_pw)), None)
                        if idx is not None:
                            user_db.update_cell(idx+2, 2, hash_pw(new_pw))
                            st.success("✅ Parol o'zgartirildi!")
                        else:
                            st.error("❌ Eski parol noto'g'ri!")
                    except Exception as e:
                        st.error(f"❌ {e}")

    with col2:
        st.markdown("#### 📊 Sessiya Ma'lumotlari")
        if 'login_time' in st.session_state:
            st.markdown(f"""
            <div style='background:white;border-radius:12px;padding:20px;border:2px solid #e0f2fe;'>
                <p><strong>📅 Kirish vaqti:</strong><br>{st.session_state.login_time.strftime('%d.%m.%Y %H:%M:%S')}</p>
                <p><strong>⏱ Sessiya davomiyligi:</strong><br>{(datetime.now()-st.session_state.login_time).seconds//60} daqiqa</p>
                <p><strong>💬 Ushbu sessiyada xabarlar:</strong><br>{len(st.session_state.messages)} ta</p>
                <p><strong>📁 Yaratilgan fayllar:</strong><br>{st.session_state.files_created} ta</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🎨 Ko'rinish Sozlamalari")
        ai_style = st.selectbox("🤖 AI uslubi:",
            ["Aqlli yordamchi","Do'stona","Rasmiy mutaxassis","Ijodkor","Texnik ekspert"],
            key="profile_ai_style")
        if st.button("💾 Saqlash", type="primary", key="save_profile"):
            st.session_state.ai_personality = ai_style
            st.success("✅ Saqlandi!")

# ─────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;color:#94a3b8;padding:40px 20px;
            border-top:2px solid #e2e8f0;margin-top:40px;
            background:linear-gradient(180deg,transparent,rgba(99,102,241,0.05));'>
    <p style='font-size:20px;font-weight:700;color:#0f172a;margin:0;'>
        🌌 Somo AI <span style='color:#6366f1;'>Ultra Pro Max</span>
    </p>
    <p style='margin:8px 0;color:#64748b;'>
        📊 Excel • 📝 Word • 💻 Kod • 🌐 HTML • 📋 CSV • 🧠 Chat
    </p>
    <p style='margin:8px 0;font-size:14px;'>
        ⚡ Groq + Llama 3.3 70B | 🚀 20+ Funksiya
    </p>
    <p style='margin:8px 0;font-size:14px;'>
        👨‍💻 Yaratuvchi: <strong>Usmonov Sodiq</strong> &nbsp;|&nbsp;
        👨‍💻 Yordamchi: <strong>Davlatov Mironshoh</strong>
    </p>
    <p style='margin:8px 0;font-size:12px;'>
        📧 support@somoai.uz &nbsp;|&nbsp; 🌐 www.somoai.uz
    </p>
    <p style='margin:15px 0 0;font-size:12px;'>
        © 2026 Somo AI Ultra Pro Max v3.0 — Barcha huquqlar himoyalangan
    </p>
</div>
""", unsafe_allow_html=True)
