import streamlit as st
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

# ───────────────────────────────────────────────
# 1. SAHIFA SOZLAMALARI
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="Somo AI | Universal Infinity",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

cookies = EncryptedCookieManager(
    password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026_Final_PRO")
)
if not cookies.ready():
    st.stop()

# ───────────────────────────────────────────────
# 2. CSS DIZAYN
# ───────────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#f8fafc 0%,#e0f2fe 50%,#ddd6fe 100%) !important;
}
[data-testid="stSidebarNav"] { display:none !important; }
.st-emotion-cache-1vt458p,.st-emotion-cache-k77z8z,.st-emotion-cache-12fmjuu {
    font-size:0px !important; color:transparent !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#e0f2fe 0%,#bae6fd 50%,#c7d2fe 100%) !important;
    border-right: 3px solid #7dd3fc;
}
[data-testid="stSidebar"] section,
[data-testid="stSidebar"] .stVerticalBlock { background:transparent !important; }
div[data-testid="stSidebar"] button {
    background: linear-gradient(135deg,#fff 0%,#f8fafc 100%) !important;
    color: #0284c7 !important;
    border: 2px solid #0ea5e9 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    width: 100% !important;
    padding: 12px !important;
    margin: 5px 0 !important;
    box-shadow: 0 2px 8px rgba(14,165,233,0.15);
}
div[data-testid="stSidebar"] button:hover {
    background: linear-gradient(135deg,#0ea5e9,#6366f1) !important;
    color: white !important;
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(14,165,233,0.4);
}
.dashboard-container {
    display:flex; flex-wrap:wrap; gap:25px;
    justify-content:center; margin-top:30px; padding:20px;
}
.card-box {
    background: linear-gradient(145deg,#fff,#f1f5f9);
    border-radius: 20px; padding: 35px; text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08),0 1px 8px rgba(0,0,0,0.05);
    border: 2px solid #e2e8f0;
    transition: all 0.4s cubic-bezier(0.4,0,0.2,1);
    flex:1; min-width:280px; max-width:380px;
    cursor:pointer; position:relative; overflow:hidden;
}
.card-box::before {
    content:''; position:absolute; top:0; left:-100%;
    width:100%; height:100%;
    background:linear-gradient(90deg,transparent,rgba(14,165,233,0.1),transparent);
    transition:0.5s;
}
.card-box:hover::before { left:100%; }
.card-box:hover {
    transform: translateY(-12px) scale(1.02);
    box-shadow: 0 20px 40px rgba(14,165,233,0.25);
    border-color: #0ea5e9;
}
@media (max-width:768px) {
    .card-box { min-width:150px !important; padding:20px !important; }
    .card-box h1 { font-size:28px !important; }
    .card-box h3 { font-size:17px !important; }
    .card-box p  { font-size:13px !important; }
    h1 { font-size:26px !important; }
}
.gradient-text {
    background: linear-gradient(90deg,#0284c7,#6366f1,#8b5cf6,#ec4899);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    animation: gradient-shift 4s ease infinite;
}
@keyframes gradient-shift {
    0%,100% { background-position:0% 50%; }
    50%      { background-position:100% 50%; }
}
.stTabs [data-baseweb="tab-list"] { gap:20px; background:transparent; }
.stTabs [data-baseweb="tab"] {
    height:55px; background:linear-gradient(145deg,#fff,#f8fafc);
    border-radius:12px 12px 0 0; padding:0 25px;
    border:2px solid #e2e8f0; transition:all 0.3s;
    box-shadow:0 2px 8px rgba(0,0,0,0.05);
}
.stTabs [data-baseweb="tab"]:hover {
    background:linear-gradient(145deg,#f1f5f9,#e2e8f0);
    border-color:#0ea5e9; transform:translateY(-2px);
}
.stChatMessage {
    background: linear-gradient(145deg,#fff,#fafafa);
    border-radius:15px; padding:15px; margin:10px 0;
    box-shadow:0 4px 15px rgba(0,0,0,0.06);
    border:1px solid #e2e8f0;
}
.stChatInputContainer {
    border-top:2px solid #e2e8f0;
    background:linear-gradient(180deg,#fff,#f8fafc);
    padding:15px; box-shadow:0 -4px 15px rgba(0,0,0,0.05);
}
.metric-card {
    background:linear-gradient(135deg,#fff,#f0f9ff);
    border-radius:12px; padding:15px; text-align:center;
    border:2px solid #bae6fd; transition:0.3s;
}
.metric-card:hover {
    transform:translateY(-5px);
    box-shadow:0 10px 25px rgba(14,165,233,0.2);
}
.upload-zone {
    border:2px dashed #0ea5e9; border-radius:16px;
    padding:20px; text-align:center;
    background:linear-gradient(135deg,rgba(14,165,233,0.05),rgba(99,102,241,0.05));
    margin-bottom:15px; transition:all 0.3s;
}
.upload-zone:hover {
    border-color:#6366f1;
    background:linear-gradient(135deg,rgba(14,165,233,0.1),rgba(99,102,241,0.1));
    transform:translateY(-2px);
}
.file-badge {
    display:inline-flex; align-items:center; gap:8px;
    background:linear-gradient(135deg,#e0f2fe,#ddd6fe);
    border:1px solid #7dd3fc; border-radius:20px;
    padding:6px 14px; font-size:13px; font-weight:600;
    color:#0284c7; margin:4px;
}
.success-message {
    background:linear-gradient(135deg,#10b981,#059669);
    color:white; padding:15px 25px; border-radius:12px;
    text-align:center; font-weight:600;
    animation:slideIn 0.5s ease;
}
@keyframes slideIn {
    from { transform:translateY(-20px); opacity:0; }
    to   { transform:translateY(0);     opacity:1; }
}
.download-card {
    background:linear-gradient(135deg,#f0fdf4,#dcfce7);
    border:2px solid #86efac; border-radius:15px;
    padding:20px; margin:10px 0;
    box-shadow:0 4px 15px rgba(16,185,129,0.15);
}
.template-card {
    background:white; border-radius:15px; padding:25px;
    border:2px solid #e2e8f0; transition:0.3s; cursor:pointer;
}
.template-card:hover {
    transform:translateY(-8px);
    box-shadow:0 15px 35px rgba(99,102,241,0.2);
    border-color:#6366f1;
}
.feedback-box {
    background:linear-gradient(145deg,#fff,#f8fafc);
    border-radius:20px; padding:30px; margin:20px 0;
    box-shadow:0 10px 30px rgba(0,0,0,0.08);
    border:2px solid #e2e8f0;
}
.vision-badge {
    background:linear-gradient(135deg,#8b5cf6,#6366f1);
    color:white; padding:4px 12px; border-radius:20px;
    font-size:12px; font-weight:700;
    display:inline-block; margin-bottom:10px;
}
.api-badge {
    display:inline-flex; align-items:center; gap:6px;
    padding:4px 12px; border-radius:20px;
    font-size:12px; font-weight:700; margin:2px;
}
.api-groq {
    background:linear-gradient(135deg,#f97316,#ea580c);
    color:white;
}
.api-gemini {
    background:linear-gradient(135deg,#4285f4,#0f9d58);
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────
# 3. BAZA VA AI ALOQASI
# ───────────────────────────────────────────────
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
            fb_sheet.append_row(
                ["Timestamp","Username","Rating","Category","Message","Email","Status"]
            )
        return user_sheet, chat_sheet, fb_sheet
    except Exception as e:
        st.error(f"❌ Baza xatosi: {e}")
        return None, None, None

@st.cache_resource
def get_groq_client():
    """Groq client — chat uchun"""
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        return None

@st.cache_resource
def get_gemini_model():
    """Gemini — rasm + fayl o'qish uchun"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel("gemini-2.0-flash")
    except Exception as e:
        return None

user_db, chat_db, feedback_db = get_connections()
groq_client = get_groq_client()
gemini_model = get_gemini_model()

# ───────────────────────────────────────────────
# 4. YORDAMCHI FUNKSIYALAR
# ───────────────────────────────────────────────
def get_file_emoji(filename):
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    return {
        "pdf":"📄","docx":"📝","doc":"📝","txt":"📃","csv":"📊",
        "xlsx":"📊","xls":"📊","json":"🔧","py":"🐍","js":"🟨",
        "html":"🌐","css":"🎨","ts":"🔷","jsx":"⚛️","tsx":"⚛️",
        "java":"☕","cpp":"⚙️","c":"⚙️","mp3":"🎵","wav":"🎵",
        "png":"🖼","jpg":"🖼","jpeg":"🖼","webp":"🖼","gif":"🎞",
        "zip":"📦","rar":"📦","svg":"🎨","md":"📋",
        "yaml":"🔧","xml":"🔧","sh":"💻","go":"🐹","rs":"🦀",
        "pptx":"📊","rb":"💎","php":"🐘","swift":"🍎","kt":"📱",
    }.get(ext, "📎")

def is_image_file(file):
    return file.type in ["image/jpeg","image/jpg","image/png","image/webp","image/gif"]

def is_pdf_file(file):
    return file.type == "application/pdf"

def is_docx_file(file):
    return "wordprocessingml" in file.type or file.name.endswith((".docx",".doc"))

def encode_image_b64(f):
    f.seek(0)
    return base64.b64encode(f.read()).decode("utf-8")

def get_image_media_type(f):
    return {
        "image/jpeg":"image/jpeg","image/jpg":"image/jpeg",
        "image/png":"image/png","image/webp":"image/webp","image/gif":"image/gif",
    }.get(f.type,"image/jpeg")

# ── GEMINI FILE READER ────────────────────────
def gemini_read_image(prompt, b64_image, media_type="image/jpeg"):
    """Rasm → Gemini Vision"""
    if not gemini_model:
        return None
    try:
        import google.generativeai as genai
        image_part = {
            "mime_type": media_type,
            "data": base64.b64decode(b64_image)
        }
        response = gemini_model.generate_content([prompt, image_part])
        return response.text
    except Exception as e:
        return None

def gemini_read_pdf(prompt, file_bytes):
    """PDF → Gemini native PDF reader"""
    if not gemini_model:
        return None
    try:
        import google.generativeai as genai
        pdf_part = {
            "mime_type": "application/pdf",
            "data": file_bytes
        }
        response = gemini_model.generate_content([prompt, pdf_part])
        return response.text
    except Exception as e:
        return None

def gemini_read_docx(prompt, file_bytes, filename):
    """DOCX → matn chiqarib Gemini'ga berish"""
    if not gemini_model:
        return None
    try:
        import google.generativeai as genai
        # mammoth bilan matn chiqarish
        text = mammoth.extract_raw_text(io.BytesIO(file_bytes)).value
        if text:
            response = gemini_model.generate_content(
                [f"{prompt}\n\nHujjat matni:\n{text[:8000]}"]
            )
            return response.text
        return None
    except Exception as e:
        return None

def process_doc_local(file):
    """Kod fayllar va CSV uchun lokal o'qish (Groq uchun)"""
    try:
        if file.name.endswith(".csv") or file.type == "text/csv":
            return "CSV:\n" + file.read().decode("utf-8", errors="ignore")[:5000]
        elif file.name.endswith(".json"):
            return "JSON:\n" + file.read().decode("utf-8", errors="ignore")[:5000]
        elif file.name.endswith((".py",".js",".ts",".jsx",".tsx",".html",".css",
                                  ".java",".cpp",".c",".go",".rs",".sh",".md",
                                  ".yaml",".xml",".sql",".kt",".rb",".php",
                                  ".swift",".txt",".r")):
            return file.read().decode("utf-8", errors="ignore")
        elif file.name.endswith((".xlsx",".xls")):
            return f"Excel fayl: {file.name}"
    except Exception as e:
        st.warning(f"⚠️ {file.name}: {e}")
    return ""

def extract_code_blocks(text):
    return re.findall(r"```(\w*)\n?(.*?)```", text, re.DOTALL)

# ───────────────────────────────────────────────
# 5. GROQ CHAT FUNKSIYASI
# ───────────────────────────────────────────────
def groq_chat(messages, model, temperature=0.6, max_tokens=4000):
    """Groq orqali oddiy chat"""
    if not groq_client:
        return "❌ Groq AI xizmati mavjud emas."
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
    """Groq Whisper — audio → matn"""
    if not groq_client:
        return None
    try:
        transcription = groq_client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model="whisper-large-v3",
            language="uz"
        )
        return transcription.text
    except Exception as e:
        return None

# ───────────────────────────────────────────────
# 6. FAYL YARATISH ENGINE
# ───────────────────────────────────────────────
def make_excel_from_response(ai_response, ts_safe):
    """AI javobidagi jadval/CSV dan Excel (.xlsx) yaratish"""
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Somo AI Jadval"

        csv_match   = re.search(r"```csv\n?(.*?)```", ai_response, re.DOTALL)
        table_match = re.search(
            r"\|(.+\|)+\n(\|[-:| ]+\|)+\n((\|.+\|\n?)+)", ai_response
        )

        rows = []
        if csv_match:
            reader = csv.reader(io.StringIO(csv_match.group(1).strip()))
            rows   = list(reader)
        elif table_match:
            for line in table_match.group(0).strip().split("\n"):
                if "---" not in line:
                    cells = [c.strip() for c in line.strip("|").split("|")]
                    if any(c for c in cells):
                        rows.append(cells)

        if not rows:
            return None

        header_fill  = PatternFill("solid", fgColor="1E40AF")
        header_font  = Font(bold=True, color="FFFFFF", size=12)
        alt_fill     = PatternFill("solid", fgColor="EFF6FF")
        border_side  = Side(style="thin", color="93C5FD")
        cell_border  = Border(
            left=border_side, right=border_side,
            top=border_side,  bottom=border_side
        )
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r_idx, row in enumerate(rows, 1):
            for c_idx, val in enumerate(row, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                cell.border    = cell_border
                cell.alignment = center_align
                if r_idx == 1:
                    cell.fill = header_fill
                    cell.font = header_font
                elif r_idx % 2 == 0:
                    cell.fill = alt_fill
                    cell.font = Font(size=11)
                else:
                    cell.font = Font(size=11)

        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)
        for row in ws.iter_rows():
            ws.row_dimensions[row[0].row].height = 25

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None


def make_pptx_from_response(ai_response, ts_safe):
    """AI javobidan PowerPoint (.pptx) yaratish"""
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN

        prs = Presentation()
        prs.slide_width  = Inches(13.33)
        prs.slide_height = Inches(7.5)

        PRIMARY   = RGBColor(0x02, 0x84, 0xC7)
        SECONDARY = RGBColor(0x63, 0x66, 0xF1)
        WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
        DARK      = RGBColor(0x0F, 0x17, 0x2A)
        LIGHT_BG  = RGBColor(0xF0, 0xF9, 0xFF)
        ACCENT    = RGBColor(0x8B, 0x5C, 0xF6)

        def add_rect(slide, l, t, w, h, color):
            shape = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
            shape.fill.solid()
            shape.fill.fore_color.rgb = color
            shape.line.fill.background()
            return shape

        def add_textbox(slide, text, l, t, w, h,
                        size=24, bold=False, color=None,
                        align=PP_ALIGN.LEFT, italic=False):
            txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
            tf  = txb.text_frame
            tf.word_wrap = True
            p   = tf.paragraphs[0]
            p.alignment = align
            run = p.add_run()
            run.text = text
            run.font.size   = Pt(size)
            run.font.bold   = bold
            run.font.italic = italic
            run.font.color.rgb = color or DARK
            return txb

        lines = ai_response.strip().split("\n")
        slides_data = []
        current = {"title": "", "bullets": [], "type": "content"}

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if re.match(r"^#{1,3}\s+", line):
                if current["title"] or current["bullets"]:
                    slides_data.append(current)
                title_text = re.sub(r"^#{1,3}\s+", "", line).strip()
                current = {"title": title_text, "bullets": [], "type": "content"}
            elif re.match(r"^(\d+\.|[-*•►▸])\s+", line):
                bullet = re.sub(r"^(\d+\.|[-*•►▸])\s+", "", line).strip()
                current["bullets"].append(bullet)
            elif re.match(r"^\*\*(.+)\*\*$", line):
                bold_text = re.sub(r"\*\*", "", line).strip()
                if current["title"] or current["bullets"]:
                    slides_data.append(current)
                current = {"title": bold_text, "bullets": [], "type": "content"}
            else:
                if line and not line.startswith("```"):
                    current["bullets"].append(line)

        if current["title"] or current["bullets"]:
            slides_data.append(current)

        if len(slides_data) < 2:
            slides_data = []
            chunks = [l.strip() for l in lines if l.strip() and not l.startswith("```")]
            title  = chunks[0] if chunks else "Somo AI"
            rest   = chunks[1:]
            slides_data.append({"title": title, "bullets": rest[:3], "type": "title"})
            for i in range(0, len(rest), 4):
                block = rest[i:i+4]
                if block:
                    slides_data.append({
                        "title": f"Qism {i//4+1}",
                        "bullets": block,
                        "type": "content"
                    })

        # ── TITLE SLAYD ──────────────────────────────
        first = slides_data[0]
        blank = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank)

        add_rect(slide, 0, 0, 13.33, 7.5,  RGBColor(0x0F,0x17,0x2A))
        add_rect(slide, 0, 0, 13.33, 3.8,  PRIMARY)
        add_rect(slide, 0, 3.5, 13.33, 4.0, SECONDARY)
        add_rect(slide, 0, 3.3, 13.33, 0.1, WHITE)
        add_rect(slide, 10.5, 0.3, 2.5, 2.5, ACCENT)
        add_rect(slide, 0.3, 5.5, 2.0, 1.5, RGBColor(0xEC,0x48,0x99))

        add_textbox(
            slide, first["title"] or "Somo AI Taqdimot",
            0.8, 1.0, 12.0, 2.0,
            size=44, bold=True, color=WHITE, align=PP_ALIGN.CENTER
        )
        subtitle = first["bullets"][0] if first["bullets"] else "Powered by Somo AI"
        add_textbox(
            slide, subtitle,
            0.8, 3.8, 12.0, 1.2,
            size=24, color=RGBColor(0xBA,0xE6,0xFD),
            align=PP_ALIGN.CENTER, italic=True
        )
        add_textbox(
            slide, "🌌 Somo AI Infinity",
            0.5, 6.8, 5.0, 0.5,
            size=14, color=RGBColor(0x94,0xA3,0xB8), align=PP_ALIGN.LEFT
        )
        add_textbox(
            slide, datetime.now().strftime("%Y"),
            11.0, 6.8, 2.0, 0.5,
            size=14, color=RGBColor(0x94,0xA3,0xB8), align=PP_ALIGN.RIGHT
        )

        # ── KONTENT SLAYDLAR ─────────────────────────
        colors_cycle = [PRIMARY, SECONDARY, ACCENT,
                        RGBColor(0xEC,0x48,0x99), RGBColor(0x10,0xB9,0x81)]

        for s_idx, sdata in enumerate(slides_data[1:], 1):
            slide = prs.slides.add_slide(blank)
            accent_color = colors_cycle[s_idx % len(colors_cycle)]

            add_rect(slide, 0, 0, 13.33, 7.5, RGBColor(0xF8,0xFA,0xFC))
            add_rect(slide, 0, 0, 0.12, 7.5, accent_color)
            add_rect(slide, 0.12, 0, 13.21, 1.4, LIGHT_BG)
            add_rect(slide, 0.12, 1.3, 13.21, 0.07, accent_color)
            add_rect(slide, 11.8, 0.15, 1.0, 1.0, accent_color)
            add_textbox(
                slide, str(s_idx),
                11.85, 0.18, 0.9, 0.9,
                size=28, bold=True, color=WHITE, align=PP_ALIGN.CENTER
            )
            add_textbox(
                slide, sdata["title"] or f"Slayd {s_idx}",
                0.4, 0.15, 11.2, 1.1,
                size=32, bold=True, color=DARK, align=PP_ALIGN.LEFT
            )

            bullets = sdata["bullets"][:7]
            if bullets:
                y_start = 1.6
                y_step  = min(0.78, (5.5 / max(len(bullets), 1)))
                box_h   = y_step * 0.85

                for b_idx, bullet in enumerate(bullets):
                    add_rect(slide, 0.35, y_start + b_idx*y_step + 0.15, 0.1, 0.35, accent_color)
                    bullet_clean = re.sub(r"^\*\*(.+)\*\*", r"\1", bullet).strip()
                    is_bold      = bullet.startswith("**") and bullet.endswith("**")
                    add_textbox(
                        slide, bullet_clean,
                        0.6, y_start + b_idx*y_step,
                        12.4, box_h,
                        size=20, bold=is_bold, color=DARK, align=PP_ALIGN.LEFT
                    )

            add_rect(slide, 0, 7.15, 13.33, 0.35, LIGHT_BG)
            add_textbox(
                slide, "🌌 Somo AI Infinity",
                0.3, 7.18, 4.0, 0.25,
                size=11, color=RGBColor(0x94,0xA3,0xB8), align=PP_ALIGN.LEFT
            )
            add_textbox(
                slide, f"{s_idx}/{len(slides_data)-1}",
                12.0, 7.18, 1.0, 0.25,
                size=11, color=RGBColor(0x94,0xA3,0xB8), align=PP_ALIGN.RIGHT
            )

        # ── YAKUNIY SLAYD ─────────────────────────────
        slide = prs.slides.add_slide(blank)
        add_rect(slide, 0, 0, 13.33, 7.5, RGBColor(0x0F,0x17,0x2A))
        add_rect(slide, 0, 2.5, 13.33, 2.5, PRIMARY)
        add_rect(slide, 0, 2.4, 13.33, 0.08, WHITE)
        add_rect(slide, 0, 4.9, 13.33, 0.08, WHITE)
        add_textbox(
            slide, "✅ Taqdimot Yakunlandi!",
            0.8, 2.7, 12.0, 1.2,
            size=42, bold=True, color=WHITE, align=PP_ALIGN.CENTER
        )
        add_textbox(
            slide, "🌌 Somo AI Infinity | Powered by Groq & Gemini",
            0.8, 5.3, 12.0, 0.8,
            size=18, color=RGBColor(0x94,0xA3,0xB8), align=PP_ALIGN.CENTER
        )

        buf = io.BytesIO()
        prs.save(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None


def make_word_from_response(ai_response, ts_safe):
    """AI javobidan Word (.docx) yaratish"""
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches

        doc = Document()
        for sec in doc.sections:
            sec.top_margin    = Inches(1)
            sec.bottom_margin = Inches(1)
            sec.left_margin   = Inches(1.2)
            sec.right_margin  = Inches(1.2)

        lines = ai_response.strip().split("\n")
        in_code_block = False
        code_buffer   = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_buffer   = []
                else:
                    in_code_block = False
                    p = doc.add_paragraph()
                    p.paragraph_format.left_indent  = Inches(0.4)
                    p.paragraph_format.space_before = Pt(6)
                    p.paragraph_format.space_after  = Pt(6)
                    run = p.add_run("\n".join(code_buffer))
                    run.font.name  = "Courier New"
                    run.font.size  = Pt(10)
                    run.font.color.rgb = RGBColor(0x1E,0x40,0xAF)
                continue

            if in_code_block:
                code_buffer.append(line)
                continue

            if not stripped:
                doc.add_paragraph()
                continue

            if re.match(r"^# ", stripped):
                h = doc.add_heading(stripped[2:], level=1)
                if h.runs: h.runs[0].font.color.rgb = RGBColor(0x02,0x84,0xC7)
            elif re.match(r"^## ", stripped):
                h = doc.add_heading(stripped[3:], level=2)
                if h.runs: h.runs[0].font.color.rgb = RGBColor(0x63,0x66,0xF1)
            elif re.match(r"^### ", stripped):
                h = doc.add_heading(stripped[4:], level=3)
                if h.runs: h.runs[0].font.color.rgb = RGBColor(0x8B,0x5C,0xF6)
            elif re.match(r"^[-*•►▸]\s+", stripped):
                text = re.sub(r"^[-*•►▸]\s+", "", stripped)
                p = doc.add_paragraph(style="List Bullet")
                _add_formatted_run_doc(p, text)
            elif re.match(r"^\d+\.\s+", stripped):
                text = re.sub(r"^\d+\.\s+", "", stripped)
                p = doc.add_paragraph(style="List Number")
                _add_formatted_run_doc(p, text)
            else:
                p = doc.add_paragraph()
                _add_formatted_run_doc(p, stripped)

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None


def _add_formatted_run_doc(paragraph, text):
    """Bold va italic matnni qayta ishlash"""
    from docx.shared import RGBColor
    parts = re.split(r"(\*\*.*?\*\*|\*.*?\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
            run.font.color.rgb = RGBColor(0x0F,0x17,0x2A)
        elif part.startswith("*") and part.endswith("*"):
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        else:
            paragraph.add_run(part)


def create_and_offer_files(ai_response, ts):
    """AI javobini tahlil qilib tegishli faylni yaratadi"""
    ts_safe        = ts.replace(":","-").replace(" ","_")
    blocks         = extract_code_blocks(ai_response)
    response_lower = ai_response.lower()

    # ── 1. PPTX ──────────────────────────────────
    pptx_triggers = ["slayd","taqdimot","prezentatsiya","slide","presentation","powerpoint","pptx"]
    has_headings  = len(re.findall(r"^#{1,3}\s+", ai_response, re.MULTILINE)) >= 3
    wants_pptx    = any(t in response_lower for t in pptx_triggers) or has_headings

    if wants_pptx:
        pptx_data = make_pptx_from_response(ai_response, ts_safe)
        if pptx_data:
            st.markdown("""
                <div class='download-card'>
                    <h4 style='color:#059669;margin:0 0 12px;'>📊 Tayyor PowerPoint Taqdimot</h4>
                    <p style='color:#065f46;font-size:14px;margin:0;'>Professional dizaynli slaydlar!</p>
                </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="⬇️ 📊 PPTX Taqdimot yuklab olish",
                data=pptx_data,
                file_name=f"somo_taqdimot_{ts_safe}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                key=f"dl_pptx_{ts_safe}",
                use_container_width=True
            )

    # ── 2. EXCEL ─────────────────────────────────
    xlsx_triggers = ["jadval","excel","xlsx","table","csv","statistika","ro'yxat","hisobot"]
    has_table     = bool(re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+", ai_response))
    has_csv_bl    = bool(re.search(r"```csv", ai_response))
    wants_xlsx    = any(t in response_lower for t in xlsx_triggers) or has_table or has_csv_bl

    if wants_xlsx:
        xlsx_data = make_excel_from_response(ai_response, ts_safe)
        if xlsx_data:
            st.markdown("""
                <div class='download-card'>
                    <h4 style='color:#059669;margin:0 0 12px;'>📊 Tayyor Excel Jadval</h4>
                </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    label="⬇️ 📊 Excel (.xlsx) yuklab olish",
                    data=xlsx_data,
                    file_name=f"somo_jadval_{ts_safe}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_xlsx_{ts_safe}",
                    use_container_width=True
                )
            # CSV ham
            csv_buf     = io.StringIO()
            csv_match   = re.search(r"```csv\n?(.*?)```", ai_response, re.DOTALL)
            table_match = re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+\n((\|.+\|\n?)+)", ai_response)
            rows = []
            if csv_match:
                rows = list(csv.reader(io.StringIO(csv_match.group(1).strip())))
            elif table_match:
                for line in table_match.group(0).strip().split("\n"):
                    if "---" not in line:
                        cells = [c.strip() for c in line.strip("|").split("|")]
                        if any(c for c in cells):
                            rows.append(cells)
            if rows:
                csv.writer(csv_buf).writerows(rows)
                with c2:
                    st.download_button(
                        label="⬇️ 📋 CSV yuklab olish",
                        data=csv_buf.getvalue().encode("utf-8"),
                        file_name=f"somo_jadval_{ts_safe}.csv",
                        mime="text/csv",
                        key=f"dl_csv_{ts_safe}",
                        use_container_width=True
                    )

    # ── 3. WORD ──────────────────────────────────
    docx_triggers = ["hujjat","word","docx","maqola","xat","rezyume","resume",
                     "shartnoma","tavsif","insho","referat","hisobot"]
    wants_docx = any(t in response_lower for t in docx_triggers)

    if wants_docx and not wants_pptx:
        docx_data = make_word_from_response(ai_response, ts_safe)
        if docx_data:
            st.markdown("""
                <div class='download-card'>
                    <h4 style='color:#059669;margin:0 0 12px;'>📝 Tayyor Word Hujjat</h4>
                </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="⬇️ 📝 Word (.docx) yuklab olish",
                data=docx_data,
                file_name=f"somo_hujjat_{ts_safe}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"dl_docx_{ts_safe}",
                use_container_width=True
            )

    # ── 4. SVG ───────────────────────────────────
    svg_blocks = [
        (l, c) for l, c in blocks
        if l.lower() == "svg" or c.strip().startswith("<svg")
    ]
    if svg_blocks:
        st.markdown("""
            <div class='download-card'>
                <h4 style='color:#059669;margin:0 0 12px;'>🎨 SVG Vektor Rasm</h4>
            </div>
        """, unsafe_allow_html=True)
        for i, (_, svg) in enumerate(svg_blocks):
            st.markdown(svg.strip(), unsafe_allow_html=True)
            st.download_button(
                label=f"⬇️ rasm_{i}.svg yuklab olish",
                data=svg.strip().encode("utf-8"),
                file_name=f"somo_rasm_{ts_safe}_{i}.svg",
                mime="image/svg+xml",
                key=f"dl_svg_{ts_safe}_{i}",
                use_container_width=True
            )

    # ── 5. HTML ──────────────────────────────────
    html_blocks = [(l, c) for l, c in blocks if l.lower() == "html"]
    if html_blocks:
        st.markdown("""
            <div class='download-card'>
                <h4 style='color:#059669;margin:0 0 12px;'>🌐 HTML Sahifa</h4>
            </div>
        """, unsafe_allow_html=True)
        for i, (_, code) in enumerate(html_blocks):
            with st.expander(f"👁 HTML Preview #{i+1}", expanded=True):
                st.components.v1.html(code.strip(), height=400, scrolling=True)
            st.download_button(
                label=f"⬇️ sahifa_{i}.html yuklab olish",
                data=code.strip().encode("utf-8"),
                file_name=f"somo_page_{ts_safe}_{i}.html",
                mime="text/html",
                key=f"dl_html_{ts_safe}_{i}",
                use_container_width=True
            )

    # ── 6. KOD FAYLLAR ───────────────────────────
    ext_map = {
        "python":"py","py":"py","javascript":"js","js":"js",
        "typescript":"ts","ts":"ts","css":"css","json":"json",
        "sql":"sql","bash":"sh","shell":"sh","sh":"sh",
        "yaml":"yaml","xml":"xml","markdown":"md","md":"md",
        "jsx":"jsx","tsx":"tsx","java":"java","cpp":"cpp",
        "c":"c","rust":"rs","go":"go","php":"php","ruby":"rb",
        "swift":"swift","kotlin":"kt","r":"r","txt":"txt","text":"txt",
    }
    skip = {"html","svg","csv",""}
    code_blocks_other = [
        (l, c) for l, c in blocks
        if l.lower() not in skip
    ]
    if code_blocks_other:
        st.markdown("""
            <div class='download-card'>
                <h4 style='color:#059669;margin:0 0 12px;'>💾 Tayyor Kod Fayllar</h4>
            </div>
        """, unsafe_allow_html=True)
        cols = st.columns(min(len(code_blocks_other), 3))
        for i, (lang, code) in enumerate(code_blocks_other):
            ext   = ext_map.get(lang.strip().lower(), "txt")
            fname = f"somo_{ts_safe}_{i}.{ext}"
            with cols[i % len(cols)]:
                st.download_button(
                    label=f"{get_file_emoji(fname)} .{ext} yuklab olish",
                    data=code.strip().encode("utf-8"),
                    file_name=fname,
                    mime="text/plain",
                    key=f"dl_code_{ts_safe}_{i}",
                    use_container_width=True
                )

# ───────────────────────────────────────────────
# 7. SHABLONLAR
# ───────────────────────────────────────────────
TEMPLATES = {
    "Biznes": [
        {
            "icon":"📊","title":"📊 Biznes Reja",
            "description":"To'liq biznes reja yaratish",
            "prompt":(
                "Menga [kompaniya nomi] uchun professional biznes reja tuzing.\n"
                "- Ijroiya xulosasi\n- Bozor tahlili\n"
                "- Marketing strategiyasi\n- Moliyaviy rejalar\n- 5 yillik prognoz"
            )
        },
        {
            "icon":"📈","title":"📈 Marketing Strategiya",
            "description":"Digital marketing reja",
            "prompt":(
                "[mahsulot/xizmat] uchun to'liq digital marketing strategiya:\n"
                "- Target auditoriya\n- SMM rejasi\n- SEO strategiya\n"
                "- Reklama byudjeti\n- KPI ko'rsatkichlari\n- Oylik reja"
            )
        },
        {
            "icon":"💼","title":"💼 Taklifnoma",
            "description":"Professional biznes taklif",
            "prompt":(
                "[mijoz nomi] uchun professional taklifnoma yoz:\n"
                "- Muammo tahlili\n- Bizning yechim\n- Narxlar\n"
                "- Garantiya\n- Aloqa ma'lumotlari"
            )
        }
    ],
    "Dasturlash": [
        {
            "icon":"💻","title":"💻 Kod Generator",
            "description":"Har qanday tildagi kod",
            "prompt":(
                "[dasturlash tili]da [funksionallik] uchun kod yoz:\n"
                "- Clean code prinsiplari\n- Izohlar bilan\n"
                "- Error handling\n- Best practices\n- Test misollari"
            )
        },
        {
            "icon":"🌐","title":"🌐 Veb Sahifa",
            "description":"HTML/CSS/JS sahifa",
            "prompt":(
                "Professional [sahifa turi] uchun HTML sahifa yarat:\n"
                "- Responsive dizayn\n- Zamonaviy CSS\n"
                "- Animatsiyalar\n- Mobile-friendly"
            )
        },
        {
            "icon":"🔌","title":"🔌 API Integratsiya",
            "description":"REST API kod",
            "prompt":(
                "[dasturlash tili]da [API nomi] bilan integratsiya kodi:\n"
                "- Authentication\n- CRUD operatsiyalar\n"
                "- Error handling\n- Rate limiting\n- Dokumentatsiya"
            )
        }
    ],
    "Ta'lim": [
        {
            "icon":"📖","title":"📖 Dars Rejasi",
            "description":"O'qituvchilar uchun",
            "prompt":(
                "[mavzu] bo'yicha to'liq dars rejasi:\n"
                "- O'quv maqsadlari\n- Kirish (10 daqiqa)\n"
                "- Asosiy qism (30 daqiqa)\n- Amaliy mashqlar\n"
                "- Yakun\n- Uyga vazifa"
            )
        },
        {
            "icon":"📝","title":"📝 Test Savollar",
            "description":"Mavzu bo'yicha testlar",
            "prompt":(
                "[mavzu] bo'yicha 20 ta test savol tuz:\n"
                "- 4 variant javob\n- To'g'ri javob belgisi\n"
                "- Qiyinlik darajasi: oson/o'rta/qiyin\n- Tushuntirish"
            )
        },
        {
            "icon":"🎯","title":"🎯 O'quv Reja",
            "description":"Kurs dasturi yaratish",
            "prompt":(
                "[soha] bo'yicha 3 oylik o'quv dasturi:\n"
                "- Haftalik jadval\n- Har bir modul maqsadi\n"
                "- Kerakli resurslar\n- Baholash mezonlari"
            )
        }
    ],
    "Shaxsiy": [
        {
            "icon":"📄","title":"📄 Rezyume",
            "description":"Professional CV",
            "prompt":(
                "[kasb] uchun professional rezyume yarat:\n"
                "- Shaxsiy ma'lumotlar\n- Kasbiy maqsad\n"
                "- Ish tajribasi\n- Ta'lim\n- Ko'nikmalar\n- Sertifikatlar"
            )
        },
        {
            "icon":"✉️","title":"✉️ Motivatsion Xat",
            "description":"Cover letter yozish",
            "prompt":(
                "[kompaniya] ga [lavozim] uchun motivatsion xat:\n"
                "- Qiziqish sabablari\n- Tajribam\n"
                "- Kompaniyaga qo'shim\n- Xulosa"
            )
        }
    ]
}

# ───────────────────────────────────────────────
# 8. SESSION BOSHQARUVI
# ───────────────────────────────────────────────
if "logged_in" not in st.session_state:
    su = cookies.get("somo_user_session")
    if su and user_db:
        try:
            recs = user_db.get_all_records()
            ud   = next((r for r in recs if str(r["username"]) == su), None)
            if ud and str(ud.get("status","")).lower() == "active":
                st.session_state.update({
                    "username": su,
                    "logged_in": True,
                    "login_time": datetime.now(),
                    "cached_user": ud
                })
            else:
                st.session_state.logged_in = False
        except Exception:
            st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

def handle_logout():
    try:
        cookies["somo_user_session"] = ""; cookies.save()
    except Exception:
        pass
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state.logged_in = False
    st.rerun()

# ───────────────────────────────────────────────
# 9. LOGIN SAHIFASI
# ───────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("""
        <div style='text-align:center;margin-top:60px;'>
            <h1 style='font-size:56px;margin-bottom:10px;'>
                🌌 Somo AI <span class='gradient-text'>Infinity</span>
            </h1>
            <p style='color:#64748b;font-size:20px;margin-bottom:15px;'>
                Kelajak texnologiyalari bilan tanishing
            </p>
            <p style='color:#94a3b8;font-size:16px;'>
                ⚡ Groq 70B Chat &nbsp;|&nbsp;
                🖼 Gemini Vision &nbsp;|&nbsp;
                📄 Gemini PDF &nbsp;|&nbsp;
                📊 PPTX/Excel &nbsp;|&nbsp;
                📝 Word
            </p>
        </div>
    """, unsafe_allow_html=True)

    # API holati ko'rsatish
    col_g, col_gem = st.columns(2)
    with col_g:
        status_groq = "✅ Ulangan" if groq_client else "❌ Ulanmagan"
        color_groq  = "#10b981" if groq_client else "#ef4444"
        st.markdown(f"""
            <div style='text-align:center;padding:10px;background:#fff;border-radius:10px;
                        border:2px solid {color_groq};margin:5px;'>
                <b style='color:{color_groq};'>🟠 Groq AI — {status_groq}</b>
                <p style='color:#64748b;font-size:12px;margin:0;'>Chat & Whisper</p>
            </div>
        """, unsafe_allow_html=True)
    with col_gem:
        status_gem = "✅ Ulangan" if gemini_model else "❌ Ulanmagan"
        color_gem  = "#10b981" if gemini_model else "#ef4444"
        st.markdown(f"""
            <div style='text-align:center;padding:10px;background:#fff;border-radius:10px;
                        border:2px solid {color_gem};margin:5px;'>
                <b style='color:{color_gem};'>🔵 Gemini AI — {status_gem}</b>
                <p style='color:#64748b;font-size:12px;margin:0;'>Vision & PDF Reader</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, c2, _ = st.columns([0.25, 1, 0.25])
    with c2:
        t1, t2, t3 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish", "ℹ️ Ma'lumot"])

        with t1:
            with st.form("login_form"):
                st.markdown("### 🔐 Hisobingizga kiring")
                u_in = st.text_input("👤 Username", placeholder="Username kiriting", key="login_u")
                p_in = st.text_input("🔑 Parol", type="password", placeholder="Parol kiriting", key="login_p")
                ca, cb = st.columns(2)
                with ca: sub = st.form_submit_button("🚀 Kirish", use_container_width=True)
                with cb: rem = st.checkbox("✅ Eslab qolish", value=True)
                if sub and u_in and p_in and user_db:
                    try:
                        recs = user_db.get_all_records()
                        hp   = hashlib.sha256(p_in.encode()).hexdigest()
                        usr  = next((r for r in recs if str(r["username"]) == u_in and str(r["password"]) == hp), None)
                        if usr:
                            if str(usr.get("status","")).lower() == "blocked":
                                st.error("🚫 Hisobingiz bloklangan!")
                            else:
                                st.session_state.update({
                                    "username": u_in,
                                    "logged_in": True,
                                    "login_time": datetime.now(),
                                    "cached_user": usr
                                })
                                if rem:
                                    cookies["somo_user_session"] = u_in
                                    cookies.save()
                                st.success("✅ Muvaffaqiyatli!")
                                time.sleep(0.5)
                                st.rerun()
                        else:
                            st.error("❌ Login yoki parol xato!")
                    except Exception as e:
                        st.error(f"❌ {e}")

        with t2:
            with st.form("reg_form"):
                st.markdown("### ✨ Yangi hisob yaratish")
                nu  = st.text_input("👤 Username", placeholder="Kamida 3 ta belgi", key="reg_u")
                np  = st.text_input("🔑 Parol", type="password", placeholder="Kamida 6 ta belgi", key="reg_p")
                npc = st.text_input("🔑 Tasdiqlang", type="password", placeholder="Qayta kiriting", key="reg_c")
                ag  = st.checkbox("Foydalanish shartlariga roziman")
                sub2 = st.form_submit_button("✨ Hisob yaratish", use_container_width=True)
                if sub2:
                    if not ag:            st.error("❌ Shartlarga rozilik!")
                    elif not nu or not np: st.error("❌ Barcha maydonlar!")
                    elif len(nu) < 3:    st.error("❌ Username ≥ 3 belgi!")
                    elif len(np) < 6:    st.error("❌ Parol ≥ 6 belgi!")
                    elif np != npc:      st.error("❌ Parollar mos emas!")
                    elif user_db:
                        try:
                            recs = user_db.get_all_records()
                            if any(r["username"] == nu for r in recs):
                                st.error("❌ Username band!")
                            else:
                                user_db.append_row([
                                    nu,
                                    hashlib.sha256(np.encode()).hexdigest(),
                                    "active",
                                    str(datetime.now())
                                ])
                                st.balloons()
                                st.success("🎉 Hisob yaratildi! Endi kirishingiz mumkin.")
                        except Exception as e:
                            st.error(f"❌ {e}")

        with t3:
            st.markdown("""
                ### 🌟 Somo AI Infinity — v3.0 Pro

                #### 🤖 AI Arxitektura
                | Funksiya | AI Engine | Sabab |
                |---------|-----------|-------|
                | 💬 Chat | **Groq LLaMA 3.3 70B** | Eng tez, bepul |
                | 🖼 Rasm tahlil | **Gemini Flash** | Dunyodagi eng yaxshi vision |
                | 📄 PDF o'qish | **Gemini Flash** | Native PDF, jadval+rasm ko'radi |
                | 📝 DOCX o'qish | **Gemini Flash** | Formatlash saqlanadi |
                | 📊 PPTX yaratish | **Lokal** | Python-pptx |
                | 📊 Excel yaratish | **Lokal** | Openpyxl |
                | 📝 Word yaratish | **Lokal** | Python-docx |

                ---
                📧 support@somoai.uz | 👨‍💻 Usmonov Sodiq | v3.0
            """)

    st.markdown("""
        <div style='text-align:center;margin-top:60px;color:#94a3b8;'>
            <p>🔒 Xavfsiz | 🌐 24/7 Onlayn</p>
            <p>© 2026 Somo AI | Barcha huquqlar himoyalangan</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ───────────────────────────────────────────────
# 10. SESSION STATE DEFAULTS
# ───────────────────────────────────────────────
defaults = {
    "messages": [],
    "total_messages": 0,
    "current_page": "chat",
    "attached_files": [],          # {name, type, data/text, media_type, bytes}
    "pending_files": []            # gemini uchun tayyor fayllar
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

uname = st.session_state.username

# ───────────────────────────────────────────────
# 11. SIDEBAR
# ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
        <div style='text-align:center;padding:20px;margin-bottom:25px;
                    background:linear-gradient(135deg,rgba(14,165,233,.1),rgba(99,102,241,.1));
                    border-radius:20px;'>
            <div style='background:linear-gradient(135deg,#0ea5e9,#6366f1);
                        width:90px;height:90px;border-radius:50%;margin:0 auto;
                        line-height:90px;font-size:40px;color:white;font-weight:bold;
                        border:5px solid white;box-shadow:0 8px 20px rgba(14,165,233,.3);'>
                {uname[0].upper()}
            </div>
            <h3 style='margin-top:15px;color:#0f172a;font-size:20px;'>{uname}</h3>
            <p style='color:#10b981;font-size:14px;font-weight:600;'>🟢 Aktiv</p>
        </div>
    """, unsafe_allow_html=True)

    # AI holati
    st.markdown("### 🤖 AI Holati")
    g_ok  = "✅" if groq_client  else "❌"
    gm_ok = "✅" if gemini_model else "❌"
    st.markdown(f"""
        <div style='background:white;border-radius:10px;padding:10px;font-size:13px;'>
            <div>{g_ok} <b>Groq</b> — Chat</div>
            <div>{gm_ok} <b>Gemini</b> — Vision, PDF, DOCX</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧭 Navigatsiya")
    for lbl, pg in [
        ("💬 Chat", "chat"),
        ("🎨 Shablonlar", "templates"),
        ("💌 Fikr bildirish", "feedback")
    ]:
        if st.button(lbl, use_container_width=True, key=f"nav_{pg}"):
            st.session_state.current_page = pg
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Statistika")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
            <div class='metric-card'>
                <h4 style='color:#0284c7;margin:0;'>💬</h4>
                <h2 style='margin:5px 0;color:#0f172a;'>{len(st.session_state.messages)}</h2>
                <p style='color:#64748b;margin:0;font-size:12px;'>Xabarlar</p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        if "login_time" in st.session_state:
            dur = (datetime.now() - st.session_state.login_time).seconds // 60
            st.markdown(f"""
                <div class='metric-card'>
                    <h4 style='color:#6366f1;margin:0;'>⏱</h4>
                    <h2 style='margin:5px 0;color:#0f172a;'>{dur}</h2>
                    <p style='color:#64748b;margin:0;font-size:12px;'>Daqiqa</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.current_page == "chat":
        st.markdown("### 🎛 Boshqaruv")
        if st.button("🗑 Chatni tozalash", use_container_width=True, key="clr"):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.success("✅ Tozalandi!")
            st.rerun()

        if st.session_state.messages:
            chat_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
            st.download_button(
                "📥 Chat yuklab olish",
                chat_json,
                file_name=f"somo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                key="dl_chat_json"
            )

        st.markdown("---")
        st.markdown("### ⚙️ Sozlamalar")
        temperature = st.slider("🌡 Ijodkorlik", 0.0, 1.0, 0.6, 0.1, key="temp")
        st.caption(
            "🎯 Aniq" if temperature < 0.3 else
            "⚖️ Muvozanatli" if temperature < 0.7 else "🎨 Ijodiy"
        )

        st.markdown("---")
        st.markdown("### 🤖 Chat Modeli")
        model_choice = st.selectbox(
            "Model", key="mdl", label_visibility="collapsed",
            options=[
                "llama-3.3-70b-versatile",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
                "llama-3.1-8b-instant"
            ],
            format_func=lambda x: {
                "llama-3.3-70b-versatile": "🧠 Llama 3.3 70B (Kuchli)",
                "mixtral-8x7b-32768":      "⚡ Mixtral 8x7B (Tez)",
                "gemma2-9b-it":            "💡 Gemma 2 9B (Yengil)",
                "llama-3.1-8b-instant":    "⚡ Llama 3.1 8B (Eng tez)"
            }.get(x, x)
        )
        st.caption("📄 Rasm/PDF → avtomatik Gemini")

    st.markdown("<br>" * 2, unsafe_allow_html=True)
    if st.button("🚪 Chiqish", use_container_width=True, key="logout", type="primary"):
        handle_logout()

# ───────────────────────────────────────────────
# 12. SAHIFALAR
# ───────────────────────────────────────────────

# ════════════ CHAT SAHIFASI ════════════
if st.session_state.current_page == "chat":

    if not st.session_state.messages:
        st.markdown(f"""
            <div style='text-align:center;margin:40px 0;'>
                <h1 style='font-size:42px;margin-bottom:15px;'>
                    Salom, <span class='gradient-text'>{uname}</span>! 👋
                </h1>
                <p style='color:#64748b;font-size:20px;margin-bottom:10px;'>
                    Bugun sizga qanday yordam bera olaman?
                </p>
                <div style='display:inline-flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-bottom:30px;'>
                    <span class='api-badge api-groq'>🟠 Groq — Chat</span>
                    <span class='api-badge api-gemini'>🔵 Gemini — Vision & PDF</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class='dashboard-container'>
                <div class='card-box'>
                    <h1 style='font-size:48px;margin-bottom:15px;'>🖼</h1>
                    <h3 style='color:#0f172a;margin-bottom:10px;'>Gemini Vision</h3>
                    <p style='color:#64748b;line-height:1.6;'>
                        Rasm yuklang — Gemini AI ko'radi va tahlil qiladi.
                        Jadval, matn, formula, grafik — hammasi!
                    </p>
                </div>
                <div class='card-box'>
                    <h1 style='font-size:48px;margin-bottom:15px;'>📄</h1>
                    <h3 style='color:#0f172a;margin-bottom:10px;'>Gemini PDF/DOCX</h3>
                    <p style='color:#64748b;line-height:1.6;'>
                        PDF yoki Word fayl yuklang — Gemini to'liq o'qiydi,
                        jadval va rasmlari bilan birga tushunadi.
                    </p>
                </div>
                <div class='card-box'>
                    <h1 style='font-size:48px;margin-bottom:15px;'>⚡</h1>
                    <h3 style='color:#0f172a;margin-bottom:10px;'>Groq Chat</h3>
                    <p style='color:#64748b;line-height:1.6;'>
                        70B model bilan tezkor suhbat, kod yozish,
                        taqdimot va hujjat yaratish.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background:linear-gradient(135deg,rgba(14,165,233,.1),rgba(99,102,241,.1));
                        padding:25px;border-radius:20px;'>
                <h3 style='color:#0f172a;margin-bottom:15px;text-align:center;'>
                    💡 Nima qila olaman?
                </h3>
                <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
                            gap:15px;'>
                    <div>
                        <strong style='color:#4285f4;'>🖼 Rasm yuklang</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            → Gemini ko'rib tahlil qiladi
                        </p>
                    </div>
                    <div>
                        <strong style='color:#0f9d58;'>📄 PDF/DOCX yuklang</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            → Gemini native o'qiydi
                        </p>
                    </div>
                    <div>
                        <strong style='color:#f97316;'>📊 "Taqdimot yarat"</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            → Professional PPTX yuklab olish
                        </p>
                    </div>
                    <div>
                        <strong style='color:#6366f1;'>📊 "Jadval yarat"</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            → Excel + CSV yuklab olish
                        </p>
                    </div>
                    <div>
                        <strong style='color:#8b5cf6;'>📝 "Hujjat yoz"</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            → Formatlangan Word yuklab olish
                        </p>
                    </div>
                    <div>
                        <strong style='color:#ec4899;'>🌐 "Veb sahifa yarat"</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            → HTML preview + yuklab olish
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Chat tarixi ko'rsatish
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            cont = m["content"]
            if isinstance(cont, list):
                for p in cont:
                    if isinstance(p, dict) and p.get("type") == "text":
                        st.markdown(p["text"])
            else:
                st.markdown(cont)

    st.markdown("---")

    # Biriktirilgan fayllar
    if st.session_state.attached_files:
        badges = "".join(
            f"<span class='file-badge'>{get_file_emoji(f['name'])} {f['name']}"
            f"{'<span style=\"font-size:10px;opacity:.7;\"> 🔵Gemini</span>' if f.get('use_gemini') else ''}"
            f"</span>"
            for f in st.session_state.attached_files
        )
        st.markdown(
            f"<div style='margin-bottom:10px;'><b>📎 Biriktirilgan:</b><br>{badges}</div>",
            unsafe_allow_html=True
        )
        if st.button("🗑 Fayllarni tozalash", key="clf"):
            st.session_state.attached_files = []
            st.rerun()

    # Fayl biriktirish
    with st.expander("➕ Fayl biriktirish — rasm, PDF, DOCX, kod, CSV", expanded=False):
        st.markdown("""
            <div class='upload-zone'>
                <p style='color:#0284c7;font-size:16px;margin:0;'>📎 Istalgan faylni yuklang</p>
                <p style='color:#64748b;font-size:13px;margin:5px 0 0;'>
                    🖼 JPG/PNG (Gemini Vision) ·
                    📄 PDF (Gemini PDF) ·
                    📝 DOCX (Gemini DOCX) ·
                    🐍 Kod (Groq) ·
                    📊 CSV/Excel (Groq)
                </p>
            </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Fayl", label_visibility="collapsed",
            type=[
                "jpg","jpeg","png","webp","gif",
                "pdf","docx","doc","txt","csv",
                "xlsx","xls","json","yaml","xml",
                "py","js","ts","jsx","tsx","html","css",
                "md","java","cpp","c","go","rs","sh","svg",
                "rb","php","swift","kt","r","sql"
            ],
            accept_multiple_files=True,
            key="multi_upload"
        )

        if uploaded:
            for f in uploaded:
                if any(a["name"] == f.name for a in st.session_state.attached_files):
                    continue

                f.seek(0)
                file_bytes = f.read()

                if is_image_file(f):
                    b64   = base64.b64encode(file_bytes).decode("utf-8")
                    mtype = get_image_media_type(f)
                    st.image(file_bytes, caption=f"🖼 {f.name}", width=280)
                    st.session_state.attached_files.append({
                        "name":       f.name,
                        "type":       "image",
                        "bytes":      file_bytes,
                        "data":       b64,
                        "media_type": mtype,
                        "use_gemini": True
                    })
                    st.success(f"✅ 🔵 Gemini Vision: {f.name}")

                elif is_pdf_file(f):
                    st.session_state.attached_files.append({
                        "name":       f.name,
                        "type":       "pdf",
                        "bytes":      file_bytes,
                        "use_gemini": True
                    })
                    size_kb = len(file_bytes) // 1024
                    st.success(f"✅ 🔵 Gemini PDF: {f.name} ({size_kb} KB)")

                elif is_docx_file(f):
                    st.session_state.attached_files.append({
                        "name":       f.name,
                        "type":       "docx",
                        "bytes":      file_bytes,
                        "use_gemini": True
                    })
                    st.success(f"✅ 🔵 Gemini DOCX: {f.name}")

                else:
                    # Kod, CSV, JSON va boshqalar → Groq uchun matn
                    f_io = io.BytesIO(file_bytes)
                    f_io.name = f.name
                    f_io.type = f.type
                    txt = process_doc_local(f_io)
                    st.session_state.attached_files.append({
                        "name":       f.name,
                        "type":       "text",
                        "text":       txt or "",
                        "use_gemini": False
                    })
                    st.success(f"✅ 🟠 Groq: {f.name} ({len(txt):,} belgi)")

    # ── CHATGPT USLUBIDA INPUT ───────────────────
    st.markdown("""
        <style>
        /* Streamlit default chat input va footer yashirish */
        [data-testid="stChatInput"] { display: none !important; }
        footer { display: none !important; }
        #MainMenu { display: none !important; }

        /* Custom chat input konteyner */
        .custom-chat-wrapper {
            position: fixed;
            bottom: 0; left: 0; right: 0;
            z-index: 9999;
            display: flex;
            justify-content: center;
            padding: 16px 20px 20px;
            background: linear-gradient(to top, #f8fafc 80%, transparent);
        }
        .custom-chat-inner {
            width: 100%;
            max-width: 800px;
            background: #ffffff;
            border: 1.5px solid #e2e8f0;
            border-radius: 18px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.10);
            display: flex;
            align-items: flex-end;
            gap: 10px;
            padding: 10px 14px;
            transition: box-shadow 0.2s, border-color 0.2s;
        }
        .custom-chat-inner:focus-within {
            border-color: #0ea5e9;
            box-shadow: 0 4px 32px rgba(14,165,233,0.18);
        }
        .custom-chat-inner textarea {
            flex: 1;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            resize: none;
            font-size: 15px;
            line-height: 1.6;
            background: transparent;
            color: #0f172a;
            min-height: 24px;
            max-height: 160px;
            font-family: inherit;
            padding: 2px 0;
        }
        .custom-chat-inner textarea::placeholder { color: #94a3b8; }
        .send-btn {
            background: linear-gradient(135deg, #0ea5e9, #6366f1);
            border: none;
            border-radius: 12px;
            width: 40px; height: 40px;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer;
            flex-shrink: 0;
            transition: all 0.2s;
            color: white;
            font-size: 18px;
        }
        .send-btn:hover {
            transform: scale(1.08);
            box-shadow: 0 4px 14px rgba(14,165,233,0.4);
        }
        .send-btn:disabled {
            background: #e2e8f0;
            cursor: not-allowed;
            transform: none;
        }
        /* Chat content bottom padding */
        .main .block-container { padding-bottom: 120px !important; }
        </style>
    """, unsafe_allow_html=True)

    # Input state
    if "chat_input_value" not in st.session_state:
        st.session_state.chat_input_value = ""

    # Custom input form
    with st.form("custom_chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([12, 1])
        with col_input:
            typed = st.text_area(
                "Xabar",
                placeholder="💭 Xabar yuboring...",
                label_visibility="collapsed",
                key="custom_input_area",
                height=56,
            )
        with col_btn:
            st.markdown("<div style='padding-top:8px;'>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "➤",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

    user_input = typed.strip() if submitted and typed and typed.strip() else None

    if user_input:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Fayl turlari ajratish
        gemini_files = [f for f in st.session_state.attached_files if f.get("use_gemini")]
        groq_texts   = [f for f in st.session_state.attached_files if not f.get("use_gemini")]

        has_gemini_file = bool(gemini_files)
        has_groq_text   = bool(groq_texts)

        # Display xabari
        if st.session_state.attached_files:
            names = ", ".join(f["name"] for f in st.session_state.attached_files)
            disp  = f"📎 *[{names}]* — {user_input}"
        else:
            disp = user_input

        st.session_state.messages.append({"role": "user", "content": disp})
        with st.chat_message("user"):
            st.markdown(disp)

        if chat_db:
            try:
                chat_db.append_row([ts, uname, "User", user_input])
            except Exception:
                pass

        with st.chat_message("assistant"):

            # ── GEMINI yo'li (rasm, PDF, DOCX) ──────────
            if has_gemini_file and gemini_model:
                api_label = "🔵 Gemini AI"
                file_types = [f["type"] for f in gemini_files]
                label_str  = " + ".join(set(file_types))
                st.markdown(f"<span class='api-badge api-gemini'>{api_label} — {label_str}</span>",
                            unsafe_allow_html=True)

                with st.spinner(f"🔵 Gemini o'qiyapti..."):
                    gemini_results = []
                    for gf in gemini_files:
                        if gf["type"] == "image":
                            res = gemini_read_image(user_input, gf["data"], gf.get("media_type","image/jpeg"))
                        elif gf["type"] == "pdf":
                            res = gemini_read_pdf(user_input, gf["bytes"])
                        elif gf["type"] == "docx":
                            res = gemini_read_docx(user_input, gf["bytes"], gf["name"])
                        else:
                            res = None

                        if res:
                            gemini_results.append(f"**📄 {gf['name']}:**\n{res}")

                    if gemini_results:
                        final_response = "\n\n---\n\n".join(gemini_results)
                    else:
                        # Gemini ishlamasa Groq bilan fallback
                        st.warning("⚠️ Gemini javob bermadi, Groq bilan urinib ko'rilmoqda...")
                        final_response = None

                if final_response:
                    st.markdown(final_response)
                    create_and_offer_files(final_response, ts)
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
                    st.session_state.total_messages += 1

                    # Groq matnlari ham bor bo'lsa, alohida Groq javob
                    if has_groq_text:
                        groq_context = "\n\n".join(
                            f"=== {f['name']} ===\n{f['text'][:3000]}"
                            for f in groq_texts if f.get("text")
                        )
                        groq_msgs = [
                            {"role": "system", "content":
                                "Sen Somo AI. Yuqoridagi Gemini tahlilini va quyidagi fayl matnlarini "
                                "hisobga olib javob ber."},
                            {"role": "system", "content": f"Fayl matnlari:\n{groq_context}"},
                            {"role": "user",   "content": f"{user_input}\n\nGemini tahlili:\n{final_response}"}
                        ]
                        model = st.session_state.get("mdl", "llama-3.3-70b-versatile")
                        gr_res = groq_chat(groq_msgs, model, temperature, max_tokens=3000)
                        st.markdown("---")
                        st.markdown(f"<span class='api-badge api-groq'>🟠 Groq — Qo'shimcha tahlil</span>",
                                    unsafe_allow_html=True)
                        st.markdown(gr_res)
                        create_and_offer_files(gr_res, ts + "_2")
                        st.session_state.messages.append({"role": "assistant", "content": gr_res})
                else:
                    # Gemini ishlamadi — to'liq Groq fallback
                    has_gemini_file = False

            # ── GROQ yo'li (chat + kod + CSV) ────────────
            if not has_gemini_file or not gemini_model:
                st.markdown(f"<span class='api-badge api-groq'>🟠 Groq LLaMA — Chat</span>",
                            unsafe_allow_html=True)
                temperature = st.session_state.get("temp", 0.6)

                with st.spinner("🤔 O'ylayapman..."):
                    sys_instr = (
                        "Sening isming Somo AI. Seni Usmonov Sodiq yaratgan. "
                        "Sen professional, foydali yordamchi sun'iy intellektsan. "
                        "Matematikani LaTeX ($...$) da yoz. "
                        "Javoblarni o'qishga qulay va strukturalashtirilgan qil. "
                        "FAYL YARATISH QOIDASI: "
                        "Taqdimot so'ralsa — ## sarlavhalar va bullet listlar bilan tuzilgan to'liq matn yoz. "
                        "Jadval so'ralsa — Markdown jadval yoki ```csv blok yoz. "
                        "Hujjat/rezyume/xat so'ralsa — to'liq formatlangan matn yoz. "
                        "HTML so'ralsa — ```html blok ichida to'liq kod yoz. "
                        "Kod so'ralsa — tegishli til blokida to'liq ishlaydigan kod yoz. "
                        "HECH QACHON faqat tushuntirma — doim to'liq tayyor kontent yoz!"
                    )

                    msgs = [{"role": "system", "content": sys_instr}]

                    # Groq fayl matnlari
                    if has_groq_text:
                        groq_context = "\n\n".join(
                            f"=== {f['name']} ===\n{f['text'][:3000]}"
                            for f in groq_texts if f.get("text")
                        )
                        msgs.append({
                            "role": "system",
                            "content": f"Yuklangan fayllar:\n\n{groq_context}"
                        })

                    # Chat tarixi (oxirgi 20 ta)
                    for old in st.session_state.messages[-20:]:
                        role = old["role"]
                        cont = old["content"]
                        if isinstance(cont, list):
                            txt = " ".join(
                                p["text"] for p in cont
                                if isinstance(p, dict) and p.get("type") == "text"
                            )
                            msgs.append({"role": role, "content": txt})
                        else:
                            msgs.append({"role": role, "content": cont})

                    model = st.session_state.get("mdl", "llama-3.3-70b-versatile")
                    temperature = st.session_state.get("temp", 0.6)
                    res = groq_chat(msgs, model, temperature, max_tokens=4000)

                st.markdown(res)
                create_and_offer_files(res, ts)
                st.session_state.messages.append({"role": "assistant", "content": res})
                st.session_state.total_messages += 1

                if chat_db:
                    try:
                        chat_db.append_row([ts, "Somo AI", "Assistant", res[:500]])
                    except Exception:
                        pass

            # Fayllarni tozalash
            st.session_state.attached_files = []

# ════════════ SHABLONLAR ════════════
elif st.session_state.current_page == "templates":
    st.markdown("""
        <div style='text-align:center;margin:30px 0;'>
            <h1 style='font-size:42px;margin-bottom:15px;'>
                🎨 <span class='gradient-text'>Shablonlar Markazi</span>
            </h1>
            <p style='color:#64748b;font-size:18px;'>
                Professional shablonlar bilan ishni tezlashtiring
            </p>
        </div>
    """, unsafe_allow_html=True)

    cat = st.selectbox("📁 Kategoriya:", list(TEMPLATES.keys()), key="tmpl_cat")
    st.markdown(f"### {cat} shablonlari")
    st.markdown("---")

    cols = st.columns(min(len(TEMPLATES[cat]), 2))
    for i, tmpl in enumerate(TEMPLATES[cat]):
        with cols[i % 2]:
            with st.expander(f"{tmpl['icon']} {tmpl['title']}", expanded=(i == 0)):
                st.markdown(f"**📝 Tavsif:** {tmpl['description']}")
                st.code(tmpl["prompt"], language="text")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("📋 Ko'chirish", key=f"cp_{cat}_{i}", use_container_width=True):
                        st.success("✅ Chatga joylashtiring!")
                with c2:
                    if st.button("🚀 Ishlatish", key=f"us_{cat}_{i}", use_container_width=True):
                        st.session_state.current_page = "chat"
                        st.session_state.messages.append({
                            "role": "user",
                            "content": tmpl["prompt"]
                        })
                        st.rerun()

    st.info("💡 [qavs ichidagi] joylarni o'z ma'lumotlaringiz bilan to'ldiring!")

# ════════════ FEEDBACK ════════════
elif st.session_state.current_page == "feedback":
    st.markdown("""
        <div style='text-align:center;margin:30px 0;'>
            <h1 style='font-size:42px;margin-bottom:15px;'>
                💌 <span class='gradient-text'>Fikr-Mulohazalar</span>
            </h1>
            <p style='color:#64748b;font-size:18px;'>Sizning fikringiz biz uchun muhim!</p>
        </div>
    """, unsafe_allow_html=True)

    _, fc, _ = st.columns([0.1, 1, 0.1])
    with fc:
        with st.form("fb_form"):
            st.markdown("### ⭐ Baholang")
            rating = st.select_slider(
                "Baho", [1, 2, 3, 4, 5], value=5,
                format_func=lambda x: "⭐" * x,
                label_visibility="collapsed"
            )
            st.markdown(
                f"<p style='text-align:center;font-size:48px;margin:20px 0;'>{'⭐' * rating}</p>",
                unsafe_allow_html=True
            )
            cat_fb = st.selectbox(
                "📂 Kategoriya",
                ["Umumiy fikr", "Xato haqida", "Yangi funksiya", "Savol", "Boshqa"],
                key="fbc"
            )
            msg_fb = st.text_area(
                "✍️ Xabar",
                placeholder="Fikrlaringiz...",
                height=150,
                key="fbm"
            )
            eml_fb = st.text_input(
                "📧 Email (ixtiyoriy)",
                placeholder="email@example.com",
                key="fbe"
            )
            sub_fb = st.form_submit_button(
                "📤 Yuborish",
                use_container_width=True,
                type="primary"
            )

            if sub_fb:
                if not msg_fb:
                    st.error("❌ Xabar yozing!")
                elif len(msg_fb) < 10:
                    st.error("❌ Kamida 10 ta belgi!")
                elif feedback_db:
                    try:
                        feedback_db.append_row([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            uname, rating, cat_fb, msg_fb,
                            eml_fb or "N/A", "Yangi"
                        ])
                        st.balloons()
                        st.markdown("""
                            <div class='success-message'>
                                ✅ Rahmat! Fikringiz yuborildi.
                            </div>
                        """, unsafe_allow_html=True)
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")
                else:
                    st.error("❌ Baza mavjud emas!")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📊 Statistika")
    if feedback_db:
        try:
            all_fb = feedback_db.get_all_records()
            if len(all_fb) > 1:
                fc1, fc2, fc3 = st.columns(3)
                rtgs = [int(f.get("Rating", 0)) for f in all_fb[1:] if f.get("Rating")]
                with fc1:
                    st.metric("📨 Jami", len(all_fb) - 1)
                with fc2:
                    avg = f"{sum(rtgs)/len(rtgs):.1f}" if rtgs else "—"
                    st.metric("⭐ O'rtacha", avg)
                with fc3:
                    yangi = len([f for f in all_fb[-10:] if f.get("Status") == "Yangi"])
                    st.metric("🆕 Yangilar", yangi)
            else:
                st.info("💬 Hali fikr-mulohazalar yo'q!")
        except Exception:
            st.warning("⚠️ Statistika yuklanmadi")

# ───────────────────────────────────────────────
# 13. FOOTER
# ───────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align:center;color:#94a3b8;padding:30px;
                border-top:2px solid #e2e8f0;
                background:linear-gradient(180deg,transparent,rgba(14,165,233,.05));'>
        <p style='margin:8px 0;font-size:18px;font-weight:600;'>
            🌌 <strong>Somo AI Infinity</strong> — v3.0 Pro
        </p>
        <p style='margin:8px 0;color:#64748b;'>
            🟠 Groq (Chat + Whisper) · 🔵 Gemini Flash (Vision + PDF + DOCX)
        </p>
        <p style='margin:8px 0;'>👨‍💻 Yaratuvchi: <strong>Usmonov Sodiq</strong></p>
        <p style='margin:8px 0;'>👨‍💻 Yordamchi: <strong>Davlatov Mironshoh</strong></p>
        <p style='margin:8px 0;font-size:13px;'>
            📧 support@somoai.uz | 🌐 www.somoai.uz
        </p>
        <p style='margin:15px 0 0;font-size:12px;color:#94a3b8;'>
            © 2026 Barcha huquqlar himoyalangan | Versiya 3.0 Pro
        </p>
    </div>
""", unsafe_allow_html=True)
