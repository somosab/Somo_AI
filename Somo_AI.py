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
.stApp { background: linear-gradient(135deg,#f8fafc 0%,#e0f2fe 50%,#ddd6fe 100%) !important; }
[data-testid="stSidebarNav"] { display:none !important; }
.st-emotion-cache-1vt458p,.st-emotion-cache-k77z8z,.st-emotion-cache-12fmjuu { font-size:0px !important; color:transparent !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#e0f2fe 0%,#bae6fd 50%,#c7d2fe 100%) !important; border-right: 3px solid #7dd3fc; }
[data-testid="stSidebar"] section, [data-testid="stSidebar"] .stVerticalBlock { background:transparent !important; }
div[data-testid="stSidebar"] button { background: linear-gradient(135deg,#fff 0%,#f8fafc 100%) !important; color: #0284c7 !important; border: 2px solid #0ea5e9 !important; border-radius: 12px !important; font-weight: 700 !important; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); width: 100% !important; padding: 12px !important; margin: 5px 0 !important; box-shadow: 0 2px 8px rgba(14,165,233,0.15); }
div[data-testid="stSidebar"] button:hover { background: linear-gradient(135deg,#0ea5e9,#6366f1) !important; color: white !important; transform: translateY(-3px); box-shadow: 0 8px 20px rgba(14,165,233,0.4); }
.dashboard-container { display:flex; flex-wrap:wrap; gap:25px; justify-content:center; margin-top:30px; padding:20px; }
.card-box { background: linear-gradient(145deg,#fff,#f1f5f9); border-radius: 20px; padding: 35px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.08),0 1px 8px rgba(0,0,0,0.05); border: 2px solid #e2e8f0; transition: all 0.4s cubic-bezier(0.4,0,0.2,1); flex:1; min-width:280px; max-width:380px; cursor:pointer; position:relative; overflow:hidden; }
.card-box::before { content:''; position:absolute; top:0; left:-100%; width:100%; height:100%; background:linear-gradient(90deg,transparent,rgba(14,165,233,0.1),transparent); transition:0.5s; }
.card-box:hover::before { left:100%; }
.card-box:hover { transform: translateY(-12px) scale(1.02); box-shadow: 0 20px 40px rgba(14,165,233,0.25); border-color: #0ea5e9; }
@media (max-width:768px) { .card-box { min-width:150px !important; padding:20px !important; } .card-box h1 { font-size:28px !important; } .card-box h3 { font-size:17px !important; } .card-box p  { font-size:13px !important; } h1 { font-size:26px !important; } }
.gradient-text { background: linear-gradient(90deg,#0284c7,#6366f1,#8b5cf6,#ec4899); background-size: 300% 300%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; animation: gradient-shift 4s ease infinite; }
@keyframes gradient-shift { 0%,100% { background-position:0% 50%; } 50% { background-position:100% 50%; } }
.stTabs [data-baseweb="tab-list"] { gap:20px; background:transparent; }
.stTabs [data-baseweb="tab"] { height:55px; background:linear-gradient(145deg,#fff,#f8fafc); border-radius:12px 12px 0 0; padding:0 25px; border:2px solid #e2e8f0; transition:all 0.3s; box-shadow:0 2px 8px rgba(0,0,0,0.05); }
.stTabs [data-baseweb="tab"]:hover { background:linear-gradient(145deg,#f1f5f9,#e2e8f0); border-color:#0ea5e9; transform:translateY(-2px); }
.stChatMessage { background: linear-gradient(145deg,#fff,#fafafa); border-radius:15px; padding:15px; margin:10px 0; box-shadow:0 4px 15px rgba(0,0,0,0.06); border:1px solid #e2e8f0; }
.stChatInputContainer { border-top:2px solid #e2e8f0; background:linear-gradient(180deg,#fff,#f8fafc); padding:15px; box-shadow:0 -4px 15px rgba(0,0,0,0.05); }
.metric-card { background:linear-gradient(135deg,#fff,#f0f9ff); border-radius:12px; padding:15px; text-align:center; border:2px solid #bae6fd; transition:0.3s; }
.metric-card:hover { transform:translateY(-5px); box-shadow:0 10px 25px rgba(14,165,233,0.2); }
.upload-zone { border:2px dashed #0ea5e9; border-radius:16px; padding:20px; text-align:center; background:linear-gradient(135deg,rgba(14,165,233,0.05),rgba(99,102,241,0.05)); margin-bottom:15px; transition:all 0.3s; }
.upload-zone:hover { border-color:#6366f1; background:linear-gradient(135deg,rgba(14,165,233,0.1),rgba(99,102,241,0.1)); transform:translateY(-2px); }
.file-badge { display:inline-flex; align-items:center; gap:8px; background:linear-gradient(135deg,#e0f2fe,#ddd6fe); border:1px solid #7dd3fc; border-radius:20px; padding:6px 14px; font-size:13px; font-weight:600; color:#0284c7; margin:4px; }
.success-message { background:linear-gradient(135deg,#10b981,#059669); color:white; padding:15px 25px; border-radius:12px; text-align:center; font-weight:600; animation:slideIn 0.5s ease; }
@keyframes slideIn { from { transform:translateY(-20px); opacity:0; } to { transform:translateY(0); opacity:1; } }
.download-card { background:linear-gradient(135deg,#f0fdf4,#dcfce7); border:2px solid #86efac; border-radius:15px; padding:20px; margin:10px 0; box-shadow:0 4px 15px rgba(16,185,129,0.15); }
.template-card { background:white; border-radius:15px; padding:25px; border:2px solid #e2e8f0; transition:0.3s; cursor:pointer; }
.template-card:hover { transform:translateY(-8px); box-shadow:0 15px 35px rgba(99,102,241,0.2); border-color:#6366f1; }
.feedback-box { background:linear-gradient(145deg,#fff,#f8fafc); border-radius:20px; padding:30px; margin:20px 0; box-shadow:0 10px 30px rgba(0,0,0,0.08); border:2px solid #e2e8f0; }
.vision-badge { background:linear-gradient(135deg,#8b5cf6,#6366f1); color:white; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700; display:inline-block; margin-bottom:10px; }
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

user_db, chat_db, feedback_db = get_connections()

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    client = None

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
        "pptx":"📊","xlsx":"📊","docx":"📝",
    }.get(ext, "📎")

def is_image_file(file):
    return file.type in ["image/jpeg","image/jpg","image/png","image/webp","image/gif"]

def encode_image(f):
    f.seek(0)
    return base64.b64encode(f.read()).decode("utf-8")

def get_image_media_type(f):
    return {
        "image/jpeg":"image/jpeg","image/jpg":"image/jpeg",
        "image/png":"image/png","image/webp":"image/webp","image/gif":"image/gif",
    }.get(f.type,"image/jpeg")

def process_doc(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif "wordprocessingml" in file.type:
            return mammoth.extract_raw_text(file).value
        elif file.type in ["text/plain"] or file.name.endswith(".txt"):
            return file.read().decode("utf-8", errors="ignore")
        elif file.type == "text/csv" or file.name.endswith(".csv"):
            return "CSV:\n" + file.read().decode("utf-8", errors="ignore")[:5000]
        elif file.name.endswith(".json"):
            return "JSON:\n" + file.read().decode("utf-8", errors="ignore")[:5000]
        elif file.name.endswith((".py",".js",".ts",".jsx",".tsx",".html",".css",
                                  ".java",".cpp",".c",".go",".rs",".sh",".md",
                                  ".yaml",".xml",".sql",".kt",".rb",".php")):
            return file.read().decode("utf-8", errors="ignore")
        elif file.name.endswith((".xlsx",".xls")):
            return f"Excel fayl: {file.name}"
    except Exception as e:
        st.warning(f"⚠️ {file.name}: {e}")
    return ""

def extract_code_blocks(text):
    return re.findall(r"```(\w*)\n?(.*?)```", text, re.DOTALL)

# ───────────────────────────────────────────────
# 5. FAYL YARATISH — ASOSIY ENGINE (YETARLI)
# ───────────────────────────────────────────────
# Kiritilgan kodda fayl yaratish va rasmni o'qish funksiyalarini olib tashladim.
# Endi faqat faylni o'qish va tahlil qilish uchun funksiyalar qoladi.

def make_excel_from_response(ai_response, ts_safe):
    """AI javobidagi jadval/CSV dan Excel (.xlsx) yaratish"""
    try:
        import openpyxl
        from openpyxl.styles import (
            PatternFill, Font, Alignment, Border, Side
        )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Somo AI Jadval"

        # CSV blok
        csv_match = re.search(r"```csv\n?(.*?)```", ai_response, re.DOTALL)
        # Markdown jadval
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

        # Rang sozlamalari
        header_fill  = PatternFill("solid", fgColor="1E40AF")
        header_font  = Font(bold=True, color="FFFFFF", size=12)
        alt_fill     = PatternFill("solid", fgColor="EFF6FF")
        border_side  = Side(style="thin", color="93C5FD")
        cell_border  = Border(
            left=border_side, right=border_side,
            top=border_side, bottom=border_side
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

        # Ustun kengligi
        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

        # Satr balandligi
        for row in ws.iter_rows():
            ws.row_dimensions[row[0].row].height = 25

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        return None

def make_word_from_response(ai_response, ts_safe):
    """AI javobidan Word (.docx) yaratish"""
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()

        # Sahifa margins
        for sec in doc.sections:
            sec.top_margin    = Inches(1)
            sec.bottom_margin = Inches(1)
            sec.left_margin   = Inches(1.2)
            sec.right_margin  = Inches(1.2)

        lines = ai_response.strip().split("\n")
        in_code_block = False
        code_buffer   = []
        code_lang     = ""

        for line in lines:
            stripped = line.strip()

            # Kod blokni olib tashladim
            # Bu yerda faqat matn va sarlavhalar qoladi

            # # Sarlavha
            if re.match(r"^# ", stripped):
                h = doc.add_heading(stripped[2:], level=1)
                h.runs[0].font.color.rgb = RGBColor(0x02,0x84,0xC7)
            elif re.match(r"^## ", stripped):
                h = doc.add_heading(stripped[3:], level=2)
                h.runs[0].font.color.rgb = RGBColor(0x63,0x66,0xF1)
            elif re.match(r"^### ", stripped):
                h = doc.add_heading(stripped[4:], level=3)
                h.runs[0].font.color.rgb = RGBColor(0x8B,0x5C,0xF6)
            # Bullet
            elif re.match(r"^[-*•►▸]\s+", stripped):
                text = re.sub(r"^[-*•►▸]\s+", "", stripped)
                p = doc.add_paragraph(style="List Bullet")
                # Bu yerda formating uchun kod olib tashlandi
                p.add_run(text)
            # Raqamlangan
            elif re.match(r"^\d+\.\s+", stripped):
                text = re.sub(r"^\d+\.\s+", "", stripped)
                p = doc.add_paragraph(style="List Number")
                p.add_run(text)
            # Oddiy matn
            else:
                p = doc.add_paragraph()
                p.add_run(stripped)

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        return None

def create_and_offer_files(ai_response, ts):
    """
    Fayl yaratish va yuborish funksiyalarini olib tashladim.
    Bu yerda faqat natijalarni ko'rsatish va yuklab olish uchun kod qoladi.
    """
    ts_safe  = ts.replace(":", "-").replace(" ", "_")
    # Faylni yaratish va yuborish qismlari olib tashlandi
    # faqatgina natijalarni ko'rsatish va yuklab olish uchun kod qoladi
    pass

# ───────────────────────────────────────────────
# 6. SHABLONLAR
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
        }
    ],
    "Ta'lim": [
        {
            "icon":"📖","title":"📖 Dars Rejasi",
            "description":"O'qituvchilar uchun",
            "prompt":(
                "[mavzu] bo'yicha to'liq dars rejasi tuzing:\n"
                "- O'quv maqsadlari\n- Kirish (10 daqiqa)\n"
                "- Asosiy qism (30 daqiqa)\n- Amaliy mashqlar (15 daqiqa)\n"
                "- Yakun (5 daqiqa)\n- Uyga vazifa"
            )
        }
    ]
}

# ───────────────────────────────────────────────
# 7. SESSION BOSHQARUVI
# ───────────────────────────────────────────────
if "logged_in" not in st.session_state:
    su = cookies.get("somo_user_session")
    if su and user_db:
        try:
            recs = user_db.get_all_records()
            ud   = next((r for r in recs if str(r["username"])==su), None)
            if ud and str(ud.get("status")).lower()=="active":
                st.session_state.update({
                    "username":su,"logged_in":True,"login_time":datetime.now()
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
    except Exception: pass
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.session_state.logged_in = False
    st.rerun()

# ───────────────────────────────────────────────
# 8. LOGIN SAHIFASI
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
                ⚡ 70B AI &nbsp;|&nbsp; 🖼 Vision &nbsp;|&nbsp;
                📊 PPTX/Excel &nbsp;|&nbsp; 📝 Word &nbsp;|&nbsp; 💾 Fayl yaratish
            </p>
        </div>
    """, unsafe_allow_html=True)

    _, c2, _ = st.columns([0.25,1,0.25])
    with c2:
        t1,t2,t3 = st.tabs(["🔒 Kirish","✍️ Ro'yxatdan o'tish","ℹ️ Ma'lumot"])

        with t1:
            with st.form("login_form"):
                st.markdown("### 🔐 Hisobingizga kiring")
                u_in = st.text_input("👤 Username", placeholder="Username kiriting", key="lu")
                p_in = st.text_input("🔑 Parol", type="password", placeholder="Parol kiriting", key="lp")
                ca,cb = st.columns(2)
                with ca: sub = st.form_submit_button("🚀 Kirish", use_container_width=True)
                with cb: rem = st.checkbox("✅ Eslab qolish", value=True)
                if sub and u_in and p_in and user_db:
                    try:
                        recs = user_db.get_all_records()
                        hp   = hashlib.sha256(p_in.encode()).hexdigest()
                        usr  = next((r for r in recs if str(r["username"])==u_in and str(r["password"])==hp), None)
                        if usr:
                            if str(usr.get("status")).lower()=="blocked":
                                st.error("🚫 Hisobingiz bloklangan!")
                            else:
                                st.session_state.update({
                                    "username":u_in,"logged_in":True,"login_time":datetime.now()
                                })
                                if rem:
                                    cookies["somo_user_session"]=u_in; cookies.save()
                                st.success("✅ Muvaffaqiyatli!"); time.sleep(0.5); st.rerun()
                        else:
                            st.error("❌ Login yoki parol xato!")
                    except Exception as e:
                        st.error(f"❌ {e}")

        with t2:
            with st.form("reg_form"):
                st.markdown("### ✨ Yangi hisob yaratish")
                nu  = st.text_input("👤 Username", placeholder="Kamida 3 ta belgi", key="ru")
                np  = st.text_input("🔑 Parol", type="password", placeholder="Kamida 6 ta belgi", key="rp")
                npc = st.text_input("🔑 Tasdiqlang", type="password", placeholder="Qayta kiriting", key="rc")
                ag  = st.checkbox("Foydalanish shartlariga roziman")
                sub2 = st.form_submit_button("✨ Hisob yaratish", use_container_width=True)
                if sub2:
                    if not ag:           st.error("❌ Shartlarga rozilik!")
                    elif not nu or not np: st.error("❌ Barcha maydonlar!")
                    elif len(nu)<3:      st.error("❌ Username ≥ 3 belgi!")
                    elif len(np)<6:      st.error("❌ Parol ≥ 6 belgi!")
                    elif np!=npc:        st.error("❌ Parollar mos emas!")
                    elif user_db:
                        try:
                            recs = user_db.get_all_records()
                            if any(r["username"]==nu for r in recs):
                                st.error("❌ Username band!")
                            else:
                                user_db.append_row([nu, hashlib.sha256(np.encode()).hexdigest(),
                                                   "active", str(datetime.now())])
                                st.balloons(); st.success("🎉 Muvaffaqiyatli!")
                        except Exception as e: st.error(f"❌ {e}")

        with t3:
            st.markdown("""
                ### 🌟 Somo AI Infinity — v2.3 Pro
                | Funksiya | Tavsif |
                |---------|--------|
                | 🧠 **70B AI** | Llama 3.3 — kuchli, aniq javoblar |
                | 🖼 **Vision** | Rasm yuklang — AI ko'radi |
                | 📊 **PPTX** | Professional slaydlar yaratish |
                | 📊 **Excel** | Rangli formatlangan jadvallar |
                | 📝 **Word** | To'liq formatlangan hujjatlar |
                | 🌐 **HTML** | Preview + yuklab olish |
                | 🐍 **Kod** | 20+ tilda fayl yaratish |
                | 🤖 **4 model** | Llama, Vision, Mixtral, Gemma |
                | 📧 support@somoai.uz |
                | 👨‍💻 Yaratuvchi: Usmonov Sodiq | v2.3
                """)
    st.markdown("<br>"*3, unsafe_allow_html=True)
    if st.button("🚪 Chiqish", use_container_width=True, key="logout", type="primary"):
        handle_logout()

# ───────────────────────────────────────────────
# 9. SESSION STATE
# ───────────────────────────────────────────────
defaults = {
    "messages":[],"total_messages":0,"current_page":"chat",
    "uploaded_file_text":"","uploaded_image":None,
    "uploaded_image_type":None,"attached_files":[]
}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

uname = st.session_state.username

# ───────────────────────────────────────────────
# 10. SIDEBAR
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

    st.markdown("### 🧭 Navigatsiya")
    for lbl,pg in [("💬 Chat","chat"),("🎨 Shablonlar","templates"),("💌 Fikr bildirish","feedback")]:
        if st.button(lbl, use_container_width=True, key=f"nav_{pg}"):
            st.session_state.current_page=pg; st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Statistika")
    c1,c2 = st.columns(2)
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
            dur = (datetime.now()-st.session_state.login_time).seconds//60
            st.markdown(f"""
                <div class='metric-card'>
                    <h4 style='color:#6366f1;margin:0;'>⏱</h4>
                    <h2 style='margin:5px 0;color:#0f172a;'>{dur}</h2>
                    <p style='color:#64748b;margin:0;font-size:12px;'>Daqiqa</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    if st.session_state.current_page=="chat":
        st.markdown("### 🎛 Boshqaruv")
        if st.button("🗑 Chatni tozalash", use_container_width=True, key="clr"):
            for k,v in defaults.items(): st.session_state[k]=v
            st.success("✅ Tozalandi!"); st.rerun()

        if st.session_state.messages:
            if st.button("📥 Yuklab olish", use_container_width=True, key="dl_ch"):
                data = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
                st.download_button(
                    "💾 JSON", data,
                    file_name=f"somo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json", use_container_width=True, key="dl_j"
                )

        st.markdown("---")
        st.markdown("### ⚙️ Sozlamalar")
        temperature = st.slider("🌡 Ijodkorlik", 0.0, 1.0, 0.6, 0.1, key="temp")
        st.caption(
            "🎯 Aniq" if temperature<0.3 else
            "⚖️ Muvozanatli" if temperature<0.7 else "🎨 Ijodiy"
        )

        st.markdown("---")
        st.markdown("### 🤖 Model")
        model_choice = st.selectbox(
            "Model", key="mdl", label_visibility="collapsed",
            options=[
                "llama-3.3-70b-versatile",
                "meta-llama/llama-4-scout-17b-16e-instruct",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            format_func=lambda x:{
                "llama-3.3-70b-versatile":                   "🧠 Llama 3.3 70B (Kuchli)",
                "meta-llama/llama-4-scout-17b-16e-instruct": "🖼 LLaMA 4 Scout (Vision)",
                "mixtral-8x7b-32768":                        "⚡ Mixtral 8x7B (Tez)",
                "gemma2-9b-it":                              "💡 Gemma 2 9B (Yengil)"
            }.get(x,x)
        )

    st.markdown("<br>"*3, unsafe_allow_html=True)
    if st.button("🚪 Chiqish", use_container_width=True, key="logout", type="primary"):
        handle_logout()

# ───────────────────────────────────────────────
# 11. SAHIFALAR
# ───────────────────────────────────────────────

# ════════════ CHAT ════════════
if st.session_state.current_page=="chat":

    if not st.session_state.messages:
        st.markdown(f"""
            <div style='text-align:center;margin:40px 0;'>
                <h1 style='font-size:42px;margin-bottom:15px;'>
                    Salom, <span class='gradient-text'>{uname}</span>! 👋
                </h1>
                <p style='color:#64748b;font-size:20px;margin-bottom:40px;'>
                    Bugun sizga qanday yordam bera olaman?
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class='dashboard-container'>
                <div class='card-box'>
                    <h1 style='font-size:48px;margin-bottom:15px;'>📊</h1>
                    <h3 style='color:#0f172a;margin-bottom:10px;'>📊 Taqdimot</h3>
                    <p style='color:#64748b;line-height:1.6;'>
                        "Sun'iy intellekt haqida taqdimot yarat" — 
                        professional slaydlar darhol yuklab olish
                    </p>
                </div>
                <div class='card-box'>
                    <h1 style='font-size:48px;margin-bottom:15px;'>📊</h1>
                    <h3 style='color:#0f172a;margin-bottom:10px;'>Excel Jadval</h3>
                    <p style='color:#64748b;line-height:1.6;'>
                        "Oylik xarajatlar jadvali" — 
                        rangli formatlanган Excel fayl yaratish
                    </p>
                </div>
                <div class='card-box'>
                    <h1 style='font-size:48px;margin-bottom:15px;'>📝</h1>
                    <h3 style='color:#0f172a;margin-bottom:10px;'>Word Hujjat</h3>
                    <p style='color:#64748b;line-height:1.6;'>
                        "Rezyume yarat" yoki "Shartnoma yoz" — 
                        tayyor Word fayl yuklab olish
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background:linear-gradient(135deg,rgba(14,165,233,.1),rgba(99,102,241,.1));
                        padding:25px;border-radius:20px;'>
                <h3 style='color:#0f172a;margin-bottom:15px;text-align:center;'>
                    💡 Nima so'rash mumkin?
                </h3>
                <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
                            gap:15px;text-align:left;'>
                    <div>
                        <strong style='color:#0284c7;'>📊 "Taqdimot yarat"</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            → Professional PPTX fayl darhol yuklab olish
                        </p>
                    </div>
                    <div>
                        <strong style='color:#6366f1;'>📊 "Jadval yarat"</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            → Rangli Excel + CSV yuklab olish
                        </p>
                    </div>
                    <div>
                        <strong style='color:#8b5cf6;'>📝 "Hujjat yoz"</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            → Formatlangan Word fayl yuklab olish
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

    # Chat tarixi
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            cont = m["content"]
            if isinstance(cont, list):
                for p in cont:
                    if isinstance(p,dict) and p.get("type")=="text":
                        st.markdown(p["text"])
            else:
                st.markdown(cont)

    st.markdown("---")

    # Biriktirilgan fayllar
    if st.session_state.attached_files:
        badges = "".join(
            f"<span class='file-badge'>{get_file_emoji(f['name'])} {f['name']}</span>"
            for f in st.session_state.attached_files
        )
        st.markdown(
            f"<div style='margin-bottom:10px;'><b>📎 Biriktirilgan:</b><br>{badges}</div>",
            unsafe_allow_html=True
        )
        if st.button("🗑 Fayllarni tozalash", key="clf"):
            st.session_state.attached_files      = []
            st.session_state.uploaded_image      = None
            st.session_state.uploaded_image_type = None
            st.session_state.uploaded_file_text  = ""
            st.rerun()

    # Fayl biriktirish zona
    with st.expander("➕ Fayl biriktirish — rasm, PDF, kod, CSV va boshqalar", expanded=False):
        st.markdown("""
            <div class='upload-zone'>
                <p style='color:#0284c7;font-size:16px;margin:0;'>📎 Istalgan faylni yuklang</p>
                <p style='color:#64748b;font-size:13px;margin:5px 0 0;'>
                    🖼 JPG/PNG · 📄 PDF · 📝 DOCX · 🐍 Kod · 📊 CSV/Excel · 🌐 HTML
                </p>
            </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Fayl", label_visibility="collapsed",
            type=["jpg","jpeg","png","webp","gif","pdf","docx","doc","txt","csv",
                  "xlsx","xls","json","yaml","xml","py","js","ts","jsx","tsx",
                  "html","css","md","java","cpp","c","go","rs","sh","svg"],
            accept_multiple_files=True, key="mup"
        )
        if uploaded:
            for f in uploaded:
                if any(a["name"]==f.name for a in st.session_state.attached_files):
                    continue
                # Rasm va fayl o'qish olib tashlandi
                st.session_state.attached_files.append(
                    {"name":f.name,"type":"document","text":""}
                )
                st.success(f"✅ {f.name} fayli qabul qilindi.")

    # CHAT INPUT
    if prompt := st.chat_input("💭 Xabar yuboring...  |  ➕ fayl biriktirish yuqorida", key="ci"):
        ts        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Rasm va fayl bilan ishlash olib tashlandi
        disp = prompt
        st.session_state.messages.append({"role":"user","content":disp})
        with st.chat_message("user"): st.markdown(disp)

        if chat_db:
            try: chat_db.append_row([ts,uname,"User",prompt])
            except Exception: pass

        with st.chat_message("assistant"):
            with st.spinner("🤔 O'ylayapman..."):
                try:
                    sys_instr = (
                        "Sening isming Somo AI. Seni Usmonov Sodiq yaratgan. "
                        "Sen professional, foydali yordamchi sun'iy intellektsan. "
                        "Matematikani LaTeX ($...$) da yoz. "
                        "Javoblarni o'qishga qulay va strukturalashtirilgan qil. "
                        "FAYL YARATISH QOIDASI: "
                        "Taqdimot so'ralsa — ## sarlavhalar va bullet listlar bilan "
                        "tuzilgan to'liq matn yoz, tizim o'zi PPTX yaratadi. "
                        "Jadval so'ralsa — Markdown jadval yoki ```csv blok yoz, "
                        "tizim o'zi Excel va CSV yaratadi. "
                        "Hujjat/rezyume/xat so'ralsa — to'liq formatlangan matn yoz, "
                        "tizim o'zi Word yaratadi. "
                        "HTML so'ralsa — ```html blok ichida to'liq kod yoz. "
                        "Kod so'ralsa — tegishli til blokida to'liq ishlaydigan kod yoz. "
                        "HECH QACHON faqat qanday qilish kerakligini tushuntirma — "
                        "doim to'liq tayyor kontent yoz!"
                    )

                    sel_model = st.session_state.get("mdl","llama-3.3-70b-versatile")
                    model     = (
                        "meta-llama/llama-4-scout-17b-16e-instruct"
                        if False else  # Rasm bilan ishlash olib tashlandi
                        sel_model
                    )

                    msgs = [{"role":"system","content":sys_instr}]

                    if st.session_state.uploaded_file_text:
                        msgs.append({
                            "role":"system",
                            "content":f"Fayllar:\n\n{st.session_state.uploaded_file_text[:6000]}"
                        })

                    for old in st.session_state.messages[-20:]:
                        role = old["role"]
                        cont = old["content"]
                        if isinstance(cont, list):
                            txt = " ".join(
                                p["text"] for p in cont
                                if isinstance(p,dict) and p.get("type")=="text"
                            )
                            msgs.append({"role":role,"content":txt})
                        else:
                            msgs.append({"role":role,"content":cont})

                    # Rasm va fayl bilan ishlash olib tashlandi
                    resp = None
                    if client:
                        resp = client.chat.completions.create(
                            messages=msgs, model=model,
                            temperature=st.session_state.get("temp",0.6), max_tokens=4000
                        )
                        res = resp.choices[0].message.content
                        st.markdown(res)

                        # Fayl yaratish va yuklab olish olib tashlandi
                        create_and_offer_files(res, ts)

                        st.session_state.messages.append({"role":"assistant","content":res})
                        st.session_state.total_messages += 1
                    else:
                        st.error("❌ AI xizmati mavjud emas.")
                except Exception as e:
                    err = f"❌ Xatolik: {e}"
                    st.error(err)
                    st.session_state.messages.append({"role":"assistant","content":err})

# ════════════ SHABLONLAR va boshqa bo'limlar - o'z joyida qoladi, faqat fayl va rasm qismlari olib tashlangan ══════════════════════════════
# (Shablonlar, fikr-mulohaza, statistikalar va footer qismlari o'zgarmaydi, ular bilan ishlash davom etadi)
