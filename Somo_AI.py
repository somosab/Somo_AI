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

# ═══════════════════════════════════════════════════════════════
# 1. SAHIFA SOZLAMALARI
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Somo AI | Universal Infinity",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

cookies = EncryptedCookieManager(
    password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_2026_V4")
)
if not cookies.ready():
    st.stop()

# ═══════════════════════════════════════════════════════════════
# 2. CSS DIZAYN — GOOGLE GEMINI STYLE
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── ASOSIY FON ── */
.stApp {
    background: linear-gradient(135deg,#f8fafc 0%,#e0f2fe 50%,#ddd6fe 100%) !important;
}
[data-testid="stSidebarNav"] { display:none !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#e0f2fe,#bae6fd,#c7d2fe) !important;
    border-right: 3px solid #7dd3fc;
}
div[data-testid="stSidebar"] button {
    background: linear-gradient(135deg,#fff,#f8fafc) !important;
    color: #0284c7 !important;
    border: 2px solid #0ea5e9 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    transition: all 0.3s ease;
    width: 100% !important;
    padding: 12px !important;
    margin: 5px 0 !important;
}
div[data-testid="stSidebar"] button:hover {
    background: linear-gradient(135deg,#0ea5e9,#6366f1) !important;
    color: white !important;
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(14,165,233,.4);
}

/* ── DASHBOARD KARTALAR ── */
.card-box {
    background: linear-gradient(145deg,#fff,#f1f5f9);
    border-radius: 20px; padding: 28px; text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,.08);
    border: 2px solid #e2e8f0;
    transition: all .4s ease;
    cursor:pointer; position:relative; overflow:hidden;
}
.card-box::before {
    content:''; position:absolute; top:0; left:-100%;
    width:100%; height:100%;
    background:linear-gradient(90deg,transparent,rgba(14,165,233,.1),transparent);
    transition:.5s;
}
.card-box:hover::before { left:100%; }
.card-box:hover {
    transform: translateY(-12px) scale(1.02);
    box-shadow: 0 20px 40px rgba(14,165,233,.25);
    border-color: #0ea5e9;
}

/* ── GRADIENT MATN ── */
.gradient-text {
    background: linear-gradient(90deg,#0284c7,#6366f1,#8b5cf6,#ec4899);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    animation: gshift 4s ease infinite;
}
@keyframes gshift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}

/* ── CHAT MESSAGE ── */
.stChatMessage {
    background: linear-gradient(145deg,#fff,#fafafa);
    border-radius: 16px; padding: 16px; margin: 12px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,.06);
    border: 1px solid #e2e8f0;
}

/* ── METRIK ── */
.metric-card {
    background:linear-gradient(135deg,#fff,#f0f9ff);
    border-radius:12px;padding:14px;text-align:center;
    border:2px solid #bae6fd;transition:.3s;
}
.metric-card:hover{transform:translateY(-4px);box-shadow:0 10px 25px rgba(14,165,233,.2);}

/* ── UPLOAD ZONA (Drag & Drop) ── */
.upload-zone {
    border:2px dashed #0ea5e9; border-radius:16px;
    padding:20px; text-align:center;
    background:linear-gradient(135deg,rgba(14,165,233,.05),rgba(99,102,241,.05));
    margin:12px 0; transition:all .3s; cursor:pointer;
}
.upload-zone:hover {
    border-color:#6366f1;
    background:linear-gradient(135deg,rgba(14,165,233,.12),rgba(99,102,241,.12));
    transform:translateY(-2px);
}
.upload-zone.drag-over {
    border-color:#8b5cf6;
    background:linear-gradient(135deg,rgba(139,92,246,.15),rgba(99,102,241,.15));
}

/* ── FILE BADGE ── */
.file-badge {
    display:inline-flex;align-items:center;gap:6px;
    background:linear-gradient(135deg,#e0f2fe,#ddd6fe);
    border:1px solid #7dd3fc;border-radius:18px;
    padding:5px 12px;font-size:12px;font-weight:600;
    color:#0284c7;margin:3px;
}

/* ── DOWNLOAD KARTA ── */
.download-card {
    background:linear-gradient(135deg,#f0fdf4,#dcfce7);
    border:2px solid #86efac;border-radius:15px;
    padding:18px;margin:10px 0;
    box-shadow:0 4px 15px rgba(16,185,129,.15);
}

/* ── IMAGE KARTA ── */
.image-card {
    background:linear-gradient(135deg,#fdf4ff,#f3e8ff);
    border:2px solid #d8b4fe;border-radius:15px;
    padding:18px;margin:10px 0;
    box-shadow:0 4px 15px rgba(139,92,246,.15);
}

/* ── SUCCESS ── */
.success-msg {
    background:linear-gradient(135deg,#10b981,#059669);
    color:white;padding:14px 22px;border-radius:12px;
    text-align:center;font-weight:600;
    animation:slideIn .5s ease;
}
@keyframes slideIn{from{transform:translateY(-20px);opacity:0}to{transform:translateY(0);opacity:1}}

/* ── BADGE ── */
.badge {
    color:white;padding:3px 10px;border-radius:14px;
    font-size:11px;font-weight:700;display:inline-block;margin:2px;
}
.badge-groq{background:linear-gradient(135deg,#f97316,#ef4444);}
.badge-gemini{background:linear-gradient(135deg,#1d4ed8,#0ea5e9);}
.badge-purple{background:linear-gradient(135deg,#8b5cf6,#6366f1);}
.badge-flux{background:linear-gradient(135deg,#ec4899,#8b5cf6);}

/* ── INFO BOX ── */
.info-box {
    background:linear-gradient(135deg,rgba(14,165,233,.07),rgba(99,102,241,.07));
    border:1px solid #7dd3fc;border-radius:15px;
    padding:18px;margin:12px 0;
}

/* ── GOOGLE GEMINI STYLE INPUT CONTAINER ── */
.chat-input-container {
    position: fixed;
    bottom: 0;
    left: 240px;
    right: 0;
    background: white;
    border-top: 2px solid #e2e8f0;
    padding: 20px 40px;
    box-shadow: 0 -4px 20px rgba(0,0,0,.08);
    z-index: 1000;
}

/* ── CHAT AREA PADDING (for fixed input) ── */
.chat-area {
    padding-bottom: 140px !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{gap:15px;background:transparent;}
.stTabs [data-baseweb="tab"]{
    height:50px;background:linear-gradient(145deg,#fff,#f8fafc);
    border-radius:12px 12px 0 0;padding:0 20px;
    border:2px solid #e2e8f0;transition:all .3s;
}
.stTabs [data-baseweb="tab"]:hover{border-color:#0ea5e9;transform:translateY(-2px);}

/* ── MOBILE ── */
@media(max-width:768px){
    .card-box{min-width:150px !important;padding:18px !important;}
    .chat-input-container{left:0 !important;padding:15px 20px !important;}
}
</style>

<script>
// Ctrl+V va Drag & Drop uchun JavaScript
document.addEventListener('paste', function(e) {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            const blob = items[i].getAsFile();
            // Streamlit file_uploader trigger qilish
            console.log('Image pasted:', blob);
        }
    }
});

// Drag & Drop
const uploadZones = document.querySelectorAll('.upload-zone');
uploadZones.forEach(zone => {
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', () => {
        zone.classList.remove('drag-over');
    });
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        console.log('Files dropped:', e.dataTransfer.files);
    });
});
</script>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 3. BAZA VA AI KLIENTLAR
# ═══════════════════════════════════════════════════════════════
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
        u  = ss.sheet1
        c  = ss.worksheet("ChatHistory")
        try:
            f = ss.worksheet("Letters")
        except Exception:
            f = ss.add_worksheet("Letters", rows="1000", cols="10")
            f.append_row(["Timestamp","Username","Rating","Category","Message","Email","Status"])
        return u, c, f
    except Exception as e:
        st.error(f"❌ Baza: {e}")
        return None, None, None

user_db, chat_db, feedback_db = get_connections()

@st.cache_resource
def get_groq():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        return None

@st.cache_resource
def get_gemini():
    try:
        import google.generativeai as genai
        genai.configure(api_key=st.secrets.get("GEMINI_API_KEY"))
        return genai
    except Exception:
        return None

groq_client   = get_groq()
gemini_client = get_gemini()

# ═══════════════════════════════════════════════════════════════
# 4. GROQ MODELLARI
# ═══════════════════════════════════════════════════════════════
MODELS = {
    "llama-3.3-70b-versatile": {
        "label": "🧠 Llama 3.3 70B — Eng Kuchli",
        "vision": False,
        "desc": "Chuqur tahlil, murakkab savollar"
    },
    "meta-llama/llama-4-scout-17b-16e-instruct": {
        "label": "🖼 LLaMA 4 Scout — Vision",
        "vision": True,
        "desc": "Rasm yuklang — AI ko'radi"
    },
    "mixtral-8x7b-32768": {
        "label": "⚡ Mixtral 8x7B — Tez",
        "vision": False,
        "desc": "Tez va kuchli"
    },
    "gemma2-9b-it": {
        "label": "💡 Gemma 2 9B — Yengil",
        "vision": False,
        "desc": "Google yengil model"
    },
    "llama-3.1-8b-instant": {
        "label": "🚀 Llama 3.1 8B — Instant",
        "vision": False,
        "desc": "Eng tez javob"
    }
}
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# ═══════════════════════════════════════════════════════════════
# 5. YORDAMCHI FUNKSIYALAR
# ═══════════════════════════════════════════════════════════════
def sha256(t):
    return hashlib.sha256(t.encode()).hexdigest()

def get_file_emoji(name):
    e = name.lower().split(".")[-1] if "." in name else ""
    return {
        "pdf":"📄","docx":"📝","doc":"📝","txt":"📃","csv":"📊",
        "xlsx":"📊","xls":"📊","json":"🔧","py":"🐍","js":"🟨",
        "html":"🌐","css":"🎨","ts":"🔷","jsx":"⚛️","tsx":"⚛️",
        "java":"☕","cpp":"⚙️","c":"⚙️","png":"🖼","jpg":"🖼",
        "jpeg":"🖼","webp":"🖼","gif":"🎞","svg":"🎨","md":"📋",
    }.get(e, "📎")

def is_image_file(f):
    return f.type in ["image/jpeg","image/jpg","image/png","image/webp","image/gif"]

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
            r = PdfReader(file)
            return "\n".join([p.extract_text() for p in r.pages if p.extract_text()])
        elif "wordprocessingml" in file.type:
            return mammoth.extract_raw_text(file).value
        elif file.name.endswith((".txt",".md",".py",".js",".ts",".jsx",".tsx",
                                  ".html",".css",".java",".cpp",".c",".go",
                                  ".rs",".sh",".yaml",".xml",".sql",".rb",".php")):
            return file.read().decode("utf-8", errors="ignore")
        elif file.name.endswith(".csv"):
            return "CSV:\n" + file.read().decode("utf-8", errors="ignore")[:5000]
        elif file.name.endswith(".json"):
            return "JSON:\n" + file.read().decode("utf-8", errors="ignore")[:5000]
    except Exception as e:
        st.warning(f"⚠️ {file.name}: {e}")
    return ""

def extract_code_blocks(text):
    return re.findall(r"```(\w*)\n?(.*?)```", text, re.DOTALL)

def is_file_request(prompt):
    """Fayl yaratish so'rovi"""
    kw = [
        "fayl yarat","fayl qil","tayyorlab ber","yaratib ber","qilib ber",
        "taqdimot yarat","slayd yarat","excel yarat","jadval yarat",
        "word yarat","hujjat yarat","rezyume yoz","xat yaz","yozib ber",
        "kod yaz","script yoz","ariza yoz","maqola yoz","hisobot yaz",
    ]
    return any(k in prompt.lower() for k in kw)

def is_image_request(prompt):
    """
    Rasm yaratish so'rovini keng qamrovli aniqlash.
    'chizib ber', 'portret', 'ko'rinish' va boshqalar.
    """
    low = prompt.lower()

    # Aniq rasm so'zlari
    img_words = [
        "rasm","surat","portret","logo","banner","poster",
        "chizma","grafika","thumbnail","avatar","cover",
        "wallpaper","icon","image","picture","photo","art",
    ]

    # Harakat so'zlari
    act_words = [
        "yarat","chiz","tayyorla","qil","ber","ko'rsat","chiqar",
        "yoz","generate","create","draw","make","show","design",
    ]

    # To'g'ridan-to'g'ri trigger
    direct = [
        "rasm yarat","rasm chiz","rasm tayyorla","rasmini yarat",
        "chizib ber","chizib ko'rsat","portret yarat","portret chiz",
        "logo yarat","banner yarat","surat chiz","ko'rinishini chiz",
        "tasvirini yarat","rasmin ko'rsat","generate image","draw",
    ]

    if any(d in low for d in direct):
        return True

    has_img = any(w in low for w in img_words)
    has_act = any(a in low for a in act_words)
    if has_img and has_act:
        return True

    # Pattern: "X-ni chiz/yarat"
    patterns = [
        r"\w+ni chiz",r"\w+ni yarat",r"\w+ni ko[''`]rsat",
        r"chizib ber",r"yaratib ber",r"rasmini ber",
    ]
    for pat in patterns:
        if re.search(pat, low):
            return True

    return False

# ═══════════════════════════════════════════════════════════════
# 6. RASM YARATISH — TOGETHER AI FLUX SCHNELL (BEPUL!)
# ═══════════════════════════════════════════════════════════════
def translate_to_english(text):
    """O'zbek/Rus → Ingliz (rasm uchun yaxshi prompt)"""
    if not groq_client:
        return text
    try:
        r = groq_client.chat.completions.create(
            messages=[
                {"role":"system","content":(
                    "You are a translator. Translate the user text to English "
                    "as a vivid, detailed image generation prompt. "
                    "Add descriptive words for better image quality. "
                    "Output ONLY the English prompt, nothing else."
                )},
                {"role":"user","content":text}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3, max_tokens=180
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return text

def generate_image_flux(prompt_text):
    """
    Together AI FLUX Schnell — professional rasm yaratish.
    100% BEPUL (limit: 50 req/day per key).
    Returns: (bytes, error, eng_prompt)
    """
    try:
        from openai import OpenAI

        # TOGETHER_API_KEY mavjudligini tekshirish
        if "TOGETHER_API_KEY" not in st.secrets:
            return None, "❌ TOGETHER_API_KEY topilmadi. Secrets ga qo'shing!", ""

        client = OpenAI(
            api_key=st.secrets["TOGETHER_API_KEY"],
            base_url="https://api.together.xyz/v1"
        )

        # Promptni inglizchaga tarjima
        eng = translate_to_english(prompt_text)

        # Sifatli prompt
        enhanced = (
            f"{eng}. "
            "High quality, detailed, professional photography, "
            "4K resolution, sharp focus, vivid colors, masterpiece."
        )

        # FLUX Schnell — eng tez va bepul model
        response = client.images.generate(
            model="black-forest-labs/FLUX.1-schnell",
            prompt=enhanced,
            n=1,
            size="1024x1024"
        )

        if response.data and len(response.data) > 0:
            img_url = response.data[0].url
            
            # Rasmni yuklab olish
            import urllib.request
            with urllib.request.urlopen(img_url) as resp:
                img_bytes = resp.read()

            return img_bytes, None, eng
        
        return None, "Rasm yaratilmadi", eng

    except Exception as e:
        err = str(e)
        if "api" in err.lower() or "key" in err.lower():
            return None, "❌ TOGETHER_API_KEY noto'g'ri", ""
        if "quota" in err.lower() or "limit" in err.lower():
            return None, "⏳ Together API kunlik limit (50 rasm/kun)", ""
        if "content" in err.lower() or "safety" in err.lower():
            return None, "⚠️ Kontent xavfsizlik filtri blokladi", ""
        return None, f"❌ Together AI: {err}", ""

def generate_svg_fallback(prompt_text):
    """Groq orqali SVG (FLUX ishlamasa)"""
    if not groq_client:
        return None
    try:
        eng = translate_to_english(prompt_text)
        sys_p = (
            "You are an expert SVG artist. Create a beautiful, detailed SVG image. "
            "Output ONLY the complete SVG code in ```svg block, nothing else. "
            "Use vibrant colors, gradients, and professional design. "
            "viewBox='0 0 500 500'. Be creative and artistic!"
        )
        r = groq_client.chat.completions.create(
            messages=[
                {"role":"system","content":sys_p},
                {"role":"user","content":f"Create SVG: {eng}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.85, max_tokens=4000
        )
        res  = r.choices[0].message.content
        svgs = [c for l,c in extract_code_blocks(res)
                if l.lower()=="svg" or c.strip().startswith("<svg")]
        return svgs[0] if svgs else None
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════
# 7. EXCEL YARATISH
# ═══════════════════════════════════════════════════════════════
def make_excel(ai_text, ts):
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

        wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Somo AI"

        cm = re.search(r"```csv\n?(.*?)```", ai_text, re.DOTALL)
        tm = re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+\n((\|.+\|\n?)+)", ai_text)
        rows = []
        if cm:
            rows = list(csv.reader(io.StringIO(cm.group(1).strip())))
        elif tm:
            for line in tm.group(0).strip().split("\n"):
                if "---" not in line:
                    cells = [c.strip() for c in line.strip("|").split("|")]
                    if any(c for c in cells): rows.append(cells)
        if not rows: return None

        hf = PatternFill("solid", fgColor="1E40AF")
        hft= Font(bold=True, color="FFFFFF", size=12)
        af = PatternFill("solid", fgColor="EFF6FF")
        bd = Side(style="thin", color="93C5FD")
        br = Border(left=bd,right=bd,top=bd,bottom=bd)
        al = Alignment(horizontal="center",vertical="center",wrap_text=True)

        for ri, row in enumerate(rows, 1):
            for ci, val in enumerate(row, 1):
                cell = ws.cell(row=ri, column=ci, value=val)
                cell.border = br; cell.alignment = al
                if ri == 1:
                    cell.fill = hf; cell.font = hft
                elif ri % 2 == 0:
                    cell.fill = af; cell.font = Font(size=11)
                else:
                    cell.font = Font(size=11)

        for col in ws.columns:
            ml = max((len(str(c.value or "")) for c in col), default=8)
            ws.column_dimensions[col[0].column_letter].width = min(ml+4, 45)
        for row in ws.iter_rows():
            ws.row_dimensions[row[0].row].height = 25

        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
        return buf.read()
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════
# 8. POWERPOINT YARATISH
# ═══════════════════════════════════════════════════════════════
def make_pptx(ai_text, ts):
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN

        prs = Presentation()
        prs.slide_width  = Inches(13.33)
        prs.slide_height = Inches(7.5)

        CP=RGBColor(0x02,0x84,0xC7);CS=RGBColor(0x63,0x66,0xF1)
        CA=RGBColor(0x8B,0x5C,0xF6);CK=RGBColor(0xEC,0x48,0x99)
        CG=RGBColor(0x10,0xB9,0x81);CW=RGBColor(0xFF,0xFF,0xFF)
        CD=RGBColor(0x0F,0x17,0x2A);CL=RGBColor(0xF0,0xF9,0xFF)
        CY=RGBColor(0x94,0xA3,0xB8);CC=[CP,CS,CA,CK,CG]
        BL=prs.slide_layouts[6]

        def rect(sl,l,t,w,h,col):
            s=sl.shapes.add_shape(1,Inches(l),Inches(t),Inches(w),Inches(h))
            s.fill.solid();s.fill.fore_color.rgb=col;s.line.fill.background()
            return s

        def tb(sl,txt,l,t,w,h,sz=20,bold=False,col=None,align=PP_ALIGN.LEFT,italic=False):
            b=sl.shapes.add_textbox(Inches(l),Inches(t),Inches(w),Inches(h))
            tf=b.text_frame;tf.word_wrap=True;p=tf.paragraphs[0];p.alignment=align
            r=p.add_run();r.text=txt;r.font.size=Pt(sz);r.font.bold=bold
            r.font.italic=italic;r.font.color.rgb=col or CD
            return b

        lines=ai_text.strip().split("\n");slides_data=[];cur={"title":"","bullets":[]}
        for line in lines:
            s=line.strip()
            if not s:continue
            if re.match(r"^#{1,3}\s+",s):
                if cur["title"] or cur["bullets"]:slides_data.append(cur)
                cur={"title":re.sub(r"^#{1,3}\s+","",s),"bullets":[]}
            elif re.match(r"^\*\*(.+)\*\*$",s):
                if cur["title"] or cur["bullets"]:slides_data.append(cur)
                cur={"title":re.sub(r"\*\*","",s),"bullets":[]}
            elif re.match(r"^(\d+\.|[-*•►▸])\s+",s):
                cur["bullets"].append(re.sub(r"^(\d+\.|[-*•►▸])\s+","",s))
            elif not s.startswith("```"):
                cur["bullets"].append(s)
        if cur["title"] or cur["bullets"]:slides_data.append(cur)

        if len(slides_data)<2:
            slides_data=[];chunks=[l.strip() for l in lines if l.strip() and not l.startswith("```")]
            if chunks:
                slides_data.append({"title":chunks[0],"bullets":chunks[1:3]})
                for i in range(0,len(chunks[1:]),4):
                    blk=chunks[1:][i:i+4]
                    if blk:slides_data.append({"title":f"Qism {i//4+1}","bullets":blk})

        # Title slide
        sl=prs.slides.add_slide(BL)
        rect(sl,0,0,13.33,7.5,CD);rect(sl,0,0,13.33,3.8,CP)
        rect(sl,0,3.5,13.33,4.0,CS);rect(sl,0,3.28,13.33,.1,CW)
        rect(sl,10.5,.3,2.5,2.5,CA);rect(sl,.3,5.5,2.0,1.5,CK)
        tt=slides_data[0]["title"] if slides_data else "Somo AI"
        tb(sl,tt,.8,.9,12.0,2.2,44,True,CW,PP_ALIGN.CENTER)
        sub=(slides_data[0]["bullets"][0] if (slides_data and slides_data[0]["bullets"]) else "Powered by Somo AI")
        tb(sl,sub,.8,3.8,12.0,1.2,24,False,RGBColor(0xBA,0xE6,0xFD),PP_ALIGN.CENTER,True)
        tb(sl,"🌌 Somo AI Infinity",.5,6.82,6.0,.5,13,False,CY,PP_ALIGN.LEFT)
        tb(sl,datetime.now().strftime("%Y"),11.5,6.82,1.5,.5,13,False,CY,PP_ALIGN.RIGHT)

        # Content slides
        for si,sd in enumerate(slides_data[1:],1):
            sl=prs.slides.add_slide(BL);acc=CC[si%len(CC)]
            rect(sl,0,0,13.33,7.5,RGBColor(0xF8,0xFA,0xFC))
            rect(sl,0,0,.12,7.5,acc);rect(sl,.12,0,13.21,1.45,CL)
            rect(sl,.12,1.38,13.21,.07,acc);rect(sl,11.8,.15,1.05,1.05,acc)
            tb(sl,str(si),11.83,.18,.95,.95,28,True,CW,PP_ALIGN.CENTER)
            tb(sl,sd["title"] or f"Slayd {si}",.4,.18,11.2,1.1,30,True,CD)
            buls=sd["bullets"][:7]
            if buls:
                y0=1.6;step=min(.78,5.5/max(len(buls),1))
                for bi,bl in enumerate(buls):
                    rect(sl,.35,y0+bi*step+.18,.1,.3,acc)
                    clean=re.sub(r"^\*\*(.+)\*\*$",r"\1",bl)
                    ib=bl.startswith("**") and bl.endswith("**")
                    tb(sl,clean,.62,y0+bi*step,12.4,step*.9,19,ib,CD)
            rect(sl,0,7.18,13.33,.32,CL)
            tb(sl,"🌌 Somo AI",.3,7.2,5.0,.25,11,False,CY)
            tb(sl,f"{si}/{len(slides_data)-1}",12.0,7.2,1.0,.25,11,False,CY,PP_ALIGN.RIGHT)

        # Final slide
        sl=prs.slides.add_slide(BL)
        rect(sl,0,0,13.33,7.5,CD);rect(sl,0,2.5,13.33,2.5,CP)
        rect(sl,0,2.38,13.33,.1,CW);rect(sl,0,4.9,13.33,.1,CW)
        tb(sl,"✅ Taqdimot Yakunlandi!",.8,2.65,12.0,1.3,40,True,CW,PP_ALIGN.CENTER)
        tb(sl,"🌌 Somo AI  |  Groq + FLUX",.8,5.3,12.0,.8,17,False,CY,PP_ALIGN.CENTER)

        buf=io.BytesIO();prs.save(buf);buf.seek(0)
        return buf.read()
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════
# 9. WORD YARATISH
# ═══════════════════════════════════════════════════════════════
def make_word(ai_text, ts):
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches

        doc=Document()
        for sec in doc.sections:
            sec.top_margin=sec.bottom_margin=Inches(1)
            sec.left_margin=sec.right_margin=Inches(1.2)

        def fmt(para,text):
            parts=re.split(r"(\*\*.*?\*\*|\*.*?\*|`.*?`)",text)
            for pt in parts:
                if pt.startswith("**") and pt.endswith("**"):
                    r=para.add_run(pt[2:-2]);r.bold=True
                    r.font.color.rgb=RGBColor(0x0F,0x17,0x2A)
                elif pt.startswith("*") and pt.endswith("*"):
                    r=para.add_run(pt[1:-1]);r.italic=True
                elif pt.startswith("`") and pt.endswith("`"):
                    r=para.add_run(pt[1:-1])
                    r.font.name="Courier New"
                    r.font.color.rgb=RGBColor(0x1E,0x40,0xAF)
                else:
                    para.add_run(pt)

        lines=ai_text.strip().split("\n");in_code=False;code_buf=[]
        for line in lines:
            s=line.strip()
            if s.startswith("```"):
                if not in_code:
                    in_code=True;code_buf=[]
                else:
                    in_code=False
                    p=doc.add_paragraph();p.paragraph_format.left_indent=Inches(.4)
                    r=p.add_run("\n".join(code_buf))
                    r.font.name="Courier New";r.font.size=Pt(10)
                    r.font.color.rgb=RGBColor(0x1E,0x40,0xAF)
                continue
            if in_code:code_buf.append(line);continue
            if not s:doc.add_paragraph();continue
            if re.match(r"^# ",s):
                h=doc.add_heading(s[2:],level=1)
                h.runs[0].font.color.rgb=RGBColor(0x02,0x84,0xC7)
            elif re.match(r"^## ",s):
                h=doc.add_heading(s[3:],level=2)
                h.runs[0].font.color.rgb=RGBColor(0x63,0x66,0xF1)
            elif re.match(r"^### ",s):
                h=doc.add_heading(s[4:],level=3)
                h.runs[0].font.color.rgb=RGBColor(0x8B,0x5C,0xF6)
            elif re.match(r"^[-*•►▸]\s+",s):
                p=doc.add_paragraph(style="List Bullet")
                fmt(p,re.sub(r"^[-*•►▸]\s+","",s))
            elif re.match(r"^\d+\.\s+",s):
                p=doc.add_paragraph(style="List Number")
                fmt(p,re.sub(r"^\d+\.\s+","",s))
            else:
                p=doc.add_paragraph();fmt(p,s)

        buf=io.BytesIO();doc.save(buf);buf.seek(0)
        return buf.read()
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════
# 10. FAYL YARATIB YUKLAB BERISH ENGINE
# ═══════════════════════════════════════════════════════════════
def create_and_offer_files(ai_text, ts, orig_prompt):
    """FAQAT fayl so'ralsa ishga tushadi"""
    ts_s=ts.replace(":","-").replace(" ","_");blocks=extract_code_blocks(ai_text)
    low=orig_prompt.lower()

    ext_map={
        "python":"py","py":"py","javascript":"js","js":"js",
        "typescript":"ts","css":"css","json":"json","sql":"sql",
        "bash":"sh","shell":"sh","yaml":"yaml","xml":"xml",
        "markdown":"md","jsx":"jsx","tsx":"tsx","java":"java",
        "cpp":"cpp","c":"c","rust":"rs","go":"go","php":"php",
        "ruby":"rb","swift":"swift","kotlin":"kt","r":"r","txt":"txt",
    }

    # PPTX
    pptx_kw=["slayd","taqdimot","prezentatsiya","slide","presentation","pptx"]
    has_h=len(re.findall(r"^#{1,3}\s+",ai_text,re.MULTILINE))>=2
    if any(k in low for k in pptx_kw) or (has_h and is_file_request(orig_prompt)):
        data=make_pptx(ai_text,ts_s)
        if data:
            st.markdown("<div class='download-card'><h4 style='color:#059669;margin:0 0 8px;'>📊 Tayyor PowerPoint</h4></div>",unsafe_allow_html=True)
            st.download_button("⬇️ 📊 PPTX yuklab olish",data,file_name=f"somo_taqdimot_{ts_s}.pptx",
                               mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                               key=f"dl_pptx_{ts_s}",use_container_width=True)

    # EXCEL
    xlsx_kw=["jadval","excel","xlsx","hisobot","statistika","ro'yxat"]
    has_tbl=bool(re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+",ai_text))
    has_csv="```csv" in ai_text
    if any(k in low for k in xlsx_kw) or (has_tbl and is_file_request(orig_prompt)) or has_csv:
        data=make_excel(ai_text,ts_s)
        if data:
            st.markdown("<div class='download-card'><h4 style='color:#059669;margin:0 0 8px;'>📊 Tayyor Excel</h4></div>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                st.download_button("⬇️ 📊 Excel (.xlsx)",data,file_name=f"somo_jadval_{ts_s}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   key=f"dl_xlsx_{ts_s}",use_container_width=True)
            rows=[]
            cm=re.search(r"```csv\n?(.*?)```",ai_text,re.DOTALL)
            tm=re.search(r"\|(.+\|)+\n(\|[-:| ]+\|)+\n((\|.+\|\n?)+)",ai_text)
            if cm:rows=list(csv.reader(io.StringIO(cm.group(1).strip())))
            elif tm:
                for line in tm.group(0).strip().split("\n"):
                    if "---" not in line:
                        cells=[c.strip() for c in line.strip("|").split("|")]
                        if any(c for c in cells):rows.append(cells)
            if rows:
                buf=io.StringIO();csv.writer(buf).writerows(rows)
                with c2:
                    st.download_button("⬇️ 📋 CSV",buf.getvalue().encode("utf-8"),
                                       file_name=f"somo_jadval_{ts_s}.csv",mime="text/csv",
                                       key=f"dl_csv_{ts_s}",use_container_width=True)

    # WORD
    word_kw=["hujjat","word","docx","maqola","xat","rezyume","resume",
             "shartnoma","referat","insho","ariza","tavsif","biografiya"]
    pptx_tr=any(k in low for k in pptx_kw)
    if any(k in low for k in word_kw) and not pptx_tr:
        data=make_word(ai_text,ts_s)
        if data:
            st.markdown("<div class='download-card'><h4 style='color:#059669;margin:0 0 8px;'>📝 Tayyor Word</h4></div>",unsafe_allow_html=True)
            st.download_button("⬇️ 📝 Word (.docx)",data,file_name=f"somo_hujjat_{ts_s}.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                               key=f"dl_docx_{ts_s}",use_container_width=True)

    # SVG
    svg_bl=[(l,c) for l,c in blocks if l.lower()=="svg" or c.strip().startswith("<svg")]
    if svg_bl:
        st.markdown("<div class='image-card'><h4 style='color:#7c3aed;margin:0 0 8px;'>🎨 SVG Rasm</h4></div>",unsafe_allow_html=True)
        for i,(_,sv) in enumerate(svg_bl):
            st.markdown(sv.strip(),unsafe_allow_html=True)
            st.download_button(f"⬇️ rasm_{i}.svg",sv.strip().encode("utf-8"),
                               file_name=f"somo_rasm_{ts_s}_{i}.svg",mime="image/svg+xml",
                               key=f"dl_svg_{ts_s}_{i}",use_container_width=True)

    # HTML
    html_bl=[(l,c) for l,c in blocks if l.lower()=="html"]
    if html_bl:
        st.markdown("<div class='download-card'><h4 style='color:#059669;margin:0 0 8px;'>🌐 HTML</h4></div>",unsafe_allow_html=True)
        for i,(_,code) in enumerate(html_bl):
            with st.expander(f"👁 Preview #{i+1}",expanded=True):
                st.components.v1.html(code.strip(),height=380,scrolling=True)
            st.download_button(f"⬇️ sahifa_{i}.html",code.strip().encode("utf-8"),
                               file_name=f"somo_page_{ts_s}_{i}.html",mime="text/html",
                               key=f"dl_html_{ts_s}_{i}",use_container_width=True)

    # KOD
    skip={"html","svg","csv",""}
    code_other=[(l,c) for l,c in blocks if l.lower() not in skip]
    if code_other and is_file_request(orig_prompt):
        st.markdown("<div class='download-card'><h4 style='color:#059669;margin:0 0 8px;'>💾 Kod Fayllar</h4></div>",unsafe_allow_html=True)
        cols=st.columns(min(len(code_other),3))
        for i,(lang,code) in enumerate(code_other):
            ext=ext_map.get(lang.strip().lower(),"txt")
            fname=f"somo_{ts_s}_{i}.{ext}"
            with cols[i%len(cols)]:
                st.download_button(f"{get_file_emoji(fname)} .{ext}",code.strip().encode("utf-8"),
                                   file_name=fname,mime="text/plain",
                                   key=f"dl_code_{ts_s}_{i}",use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# 11. SHABLONLAR
# ═══════════════════════════════════════════════════════════════
TEMPLATES={
    "📊 Biznes":[
        {"icon":"📊","title":"Biznes Reja","desc":"To'liq biznes reja",
         "prompt":"[kompaniya] uchun biznes reja yaratib bering:\n## Ijroiya Xulosasi\n## Bozor Tahlili\n## Marketing\n## Moliya\n## Xulosa"},
        {"icon":"📈","title":"SWOT","desc":"SWOT tahlil + jadval",
         "prompt":"[kompaniya] uchun SWOT tahlil:\n## Kuchli\n## Zaif\n## Imkoniyatlar\n## Tahdidlar\n\nJadval shaklida"}
    ],
    "💻 Dasturlash":[
        {"icon":"💻","title":"Kod Generator","desc":"Har qanday tildagi kod",
         "prompt":"[til]da [funksiya] uchun to'liq kod yozib bering:\n- Ishlaydigan kod\n- Izohlar\n- Error handling"},
        {"icon":"🔍","title":"Kod Review","desc":"Kodni tahlil",
         "prompt":"Kodni tahlil qiling:\n```\n[KOD]\n```\n- Xatolar\n- Yaxshilashlar\n- Optimal versiya"}
    ],
    "🎨 Rasm":[
        {"icon":"🎨","title":"Fotorealistik Rasm","desc":"FLUX bilan haqiqiy rasm",
         "prompt":"[mavzu] ning professional fotosini yaratib ber"},
        {"icon":"🖼","title":"Portret","desc":"Odamlar portreti",
         "prompt":"[ism/tavsif] ning chiroyli portretini yaratib ber"}
    ]
}

# ═══════════════════════════════════════════════════════════════
# 12. SESSION BOSHQARUVI
# ═══════════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    su=cookies.get("somo_user_session")
    if su and user_db:
        try:
            recs=user_db.get_all_records()
            ud=next((r for r in recs if str(r["username"])==su),None)
            if ud and str(ud.get("status","")).lower()=="active":
                st.session_state.update({"username":su,"logged_in":True,"login_time":datetime.now()})
            else:
                st.session_state.logged_in=False
        except Exception:
            st.session_state.logged_in=False
    else:
        st.session_state.logged_in=False

def handle_logout():
    try:cookies["somo_user_session"]="";cookies.save()
    except Exception:pass
    for k in list(st.session_state.keys()):del st.session_state[k]
    st.session_state.logged_in=False
    st.rerun()

# ═══════════════════════════════════════════════════════════════
# 13. LOGIN SAHIFASI
# ═══════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
        <div style='text-align:center;margin-top:50px;'>
            <h1 style='font-size:54px;margin-bottom:10px;'>
                🌌 Somo AI <span class='gradient-text'>Infinity</span>
            </h1>
            <p style='color:#64748b;font-size:19px;margin-bottom:12px;'>
                Professional AI — Rasm, Fayl, Vision
            </p>
            <div style='display:flex;justify-content:center;gap:8px;flex-wrap:wrap;'>
                <span class='badge badge-groq'>⚡ Groq — Bepul</span>
                <span class='badge badge-flux'>🎨 FLUX — Bepul</span>
                <span class='badge badge-purple'>🖼 Vision</span>
                <span class='badge badge-gemini'>📊 PPTX/Excel/Word</span>
            </div>
        </div>
    """,unsafe_allow_html=True)

    _,c2,_=st.columns([.2,1,.2])
    with c2:
        t1,t2,t3=st.tabs(["🔒 Kirish","✍️ Ro'yxat","ℹ️ Ma'lumot"])

        with t1:
            with st.form("login_form"):
                st.markdown("### 🔐 Kirish")
                u_in=st.text_input("👤 Username",key="lu")
                p_in=st.text_input("🔑 Parol",type="password",key="lp")
                ca,cb=st.columns(2)
                with ca:sub=st.form_submit_button("🚀 Kirish",use_container_width=True)
                with cb:rem=st.checkbox("✅ Eslab qol",value=True)
                if sub and u_in and p_in and user_db:
                    try:
                        recs=user_db.get_all_records();hp=sha256(p_in)
                        usr=next((r for r in recs if str(r["username"])==u_in and str(r["password"])==hp),None)
                        if usr:
                            if str(usr.get("status","")).lower()=="blocked":
                                st.error("🚫 Bloklangan!")
                            else:
                                st.session_state.update({"username":u_in,"logged_in":True,"login_time":datetime.now()})
                                if rem:cookies["somo_user_session"]=u_in;cookies.save()
                                st.success("✅ OK!");time.sleep(.5);st.rerun()
                        else:
                            st.error("❌ Xato!")
                    except Exception as e:
                        st.error(f"❌ {e}")

        with t2:
            with st.form("reg_form"):
                st.markdown("### ✨ Ro'yxatdan o'tish")
                nu=st.text_input("👤 Username",key="ru")
                np=st.text_input("🔑 Parol",type="password",key="rp")
                npc=st.text_input("🔑 Tasdiq",type="password",key="rc")
                ag=st.checkbox("Roziman")
                sub2=st.form_submit_button("✨ Yaratish",use_container_width=True)
                if sub2:
                    if not ag:st.error("❌ Rozilik!")
                    elif not nu or not np:st.error("❌ Barcha maydon!")
                    elif len(nu)<3:st.error("❌ Username ≥3!")
                    elif len(np)<6:st.error("❌ Parol ≥6!")
                    elif np!=npc:st.error("❌ Mos emas!")
                    elif user_db:
                        try:
                            recs=user_db.get_all_records()
                            if any(r["username"]==nu for r in recs):
                                st.error("❌ Band!")
                            else:
                                user_db.append_row([nu,sha256(np),"active",str(datetime.now())])
                                st.balloons();st.success("🎉 OK!")
                        except Exception as e:
                            st.error(f"❌ {e}")

        with t3:
            st.markdown("""
                ### 🌟 Somo AI Infinity v4.0

                | | |
                |--|--|
                | **⚡ Groq** | 5 model — bepul, tez |
                | **🎨 FLUX** | Together AI — sifatli rasm |
                | **🖼 Vision** | LLaMA 4 Scout |
                | **📊 Fayllar** | PPTX, Excel, Word |
                | **🌐 Kod** | 20+ til |

                ---
                📧 support@somoai.uz
                👨‍💻 Usmonov Sodiq | 🤝 Davlatov Mironshoh
            """)

    st.markdown("<div style='text-align:center;margin-top:50px;color:#94a3b8;'><p>© 2026 Somo AI</p></div>",unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════
# 14. SESSION STATE
# ═══════════════════════════════════════════════════════════════
DEFAULTS={"messages":[],"total_messages":0,"current_page":"chat",
          "uploaded_file_text":"","uploaded_image":None,
          "uploaded_image_type":None,"attached_files":[]}
for k,v in DEFAULTS.items():
    if k not in st.session_state:st.session_state[k]=v

uname=st.session_state.username

# ═══════════════════════════════════════════════════════════════
# 15. SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
        <div style='text-align:center;padding:18px;margin-bottom:18px;
                    background:linear-gradient(135deg,rgba(14,165,233,.1),rgba(99,102,241,.1));
                    border-radius:18px;'>
            <div style='background:linear-gradient(135deg,#0ea5e9,#6366f1);
                        width:82px;height:82px;border-radius:50%;margin:0 auto;
                        line-height:82px;font-size:36px;color:white;font-weight:bold;
                        border:4px solid white;box-shadow:0 8px 20px rgba(14,165,233,.3);'>
                {uname[0].upper()}
            </div>
            <h3 style='margin-top:12px;color:#0f172a;font-size:18px;'>{uname}</h3>
            <p style='color:#10b981;font-size:13px;font-weight:600;margin:4px 0;'>🟢 Aktiv</p>
            <span class='badge badge-groq'>⚡ Groq</span>
            <span class='badge badge-flux'>🎨 FLUX</span>
        </div>
    """,unsafe_allow_html=True)

    st.markdown("### 🧭 Navigatsiya")
    for lbl,pg in [("💬 Chat","chat"),("🎨 Shablonlar","templates"),("💌 Fikr","feedback")]:
        if st.button(lbl,use_container_width=True,key=f"nav_{pg}"):
            st.session_state.current_page=pg;st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Statistika")
    c1,c2=st.columns(2)
    with c1:
        st.markdown(f"""
            <div class='metric-card'>
                <h4 style='color:#0284c7;margin:0;'>💬</h4>
                <h2 style='margin:5px 0;color:#0f172a;'>{len(st.session_state.messages)}</h2>
                <p style='color:#64748b;margin:0;font-size:11px;'>Xabar</p>
            </div>
        """,unsafe_allow_html=True)
    with c2:
        if "login_time" in st.session_state:
            dur=(datetime.now()-st.session_state.login_time).seconds//60
            st.markdown(f"""
                <div class='metric-card'>
                    <h4 style='color:#6366f1;margin:0;'>⏱</h4>
                    <h2 style='margin:5px 0;color:#0f172a;'>{dur}</h2>
                    <p style='color:#64748b;margin:0;font-size:11px;'>Daq</p>
                </div>
            """,unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.current_page=="chat":
        st.markdown("### 🎛 Boshqaruv")
        if st.button("🗑 Tozalash",use_container_width=True,key="clr"):
            for k,v in DEFAULTS.items():st.session_state[k]=v
            st.success("✅ OK!");st.rerun()

        if st.session_state.messages:
            if st.button("📥 Saqlash",use_container_width=True,key="dlch"):
                data=json.dumps(st.session_state.messages,ensure_ascii=False,indent=2)
                st.download_button("💾 JSON",data,file_name=f"somo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                   mime="application/json",use_container_width=True,key="dlj")

        st.markdown("---")
        st.markdown("### 🤖 Groq Model")
        model_key=st.selectbox("Model",key="mdl",label_visibility="collapsed",
                               options=list(MODELS.keys()),
                               format_func=lambda x:MODELS[x]["label"])
        st.caption(f"💡 {MODELS[model_key]['desc']}")
        if MODELS[model_key]["vision"]:
            st.markdown("<span class='badge badge-gemini'>🖼 Vision</span>",unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown("""
            <div style='background:#fdf4ff;border:1px solid #d8b4fe;
                        border-radius:10px;padding:10px;text-align:center;'>
                🎨 <strong>FLUX Schnell</strong><br>
                <small style='color:#7c3aed;'>Professional rasm yaratish</small>
            </div>
        """,unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ⚙️ Sozlamalar")
        temp=st.slider("🌡 Ijodkorlik",0.0,1.0,0.7,0.05,key="temp")
        st.caption("🎯 Aniq" if temp<0.3 else "⚖️ Balans" if temp<0.65 else "🎨 Ijodiy")

        max_tok=st.select_slider("📏 Uzunlik",key="maxtok",
                                  options=[1024,2048,4096,6000,8000],value=4096)
        st.caption(f"~{max_tok//4} so'z")

    st.markdown("<br>"*2,unsafe_allow_html=True)
    if st.button("🚪 Chiqish",use_container_width=True,key="logout",type="primary"):
        handle_logout()

# ═══════════════════════════════════════════════════════════════
# 16. CHAT SAHIFASI
# ═══════════════════════════════════════════════════════════════
if st.session_state.current_page=="chat":

    # Dashboard (bot messages bo'lsa ko'rinmaydi)
    if not st.session_state.messages:
        st.markdown(f"""
            <div style='text-align:center;margin:28px 0;'>
                <h1 style='font-size:40px;margin-bottom:12px;'>
                    Salom, <span class='gradient-text'>{uname}</span>! 👋
                </h1>
                <p style='color:#64748b;font-size:18px;margin-bottom:28px;'>
                    Qanday yordam bera olaman?
                </p>
            </div>
        """,unsafe_allow_html=True)

        # 4 ta karta
        cols=st.columns(4)
        cards=[
            ("🎨","Rasm Yaratish","FLUX Schnell — professional rasm"),
            ("📊","Fayl Yaratish","PPTX, Excel, Word"),
            ("🖼","Vision Tahlil","Rasm yuklang — AI ko'radi"),
            ("💻","Kod Yozish","20+ til, to'liq kod")
        ]
        for i,(icon,title,desc) in enumerate(cards):
            with cols[i]:
                st.markdown(f"""
                    <div class='card-box'>
                        <h1 style='font-size:40px;margin-bottom:10px;'>{icon}</h1>
                        <h3 style='color:#0f172a;margin-bottom:8px;font-size:16px;'>{title}</h3>
                        <p style='color:#64748b;line-height:1.5;font-size:13px;'>{desc}</p>
                    </div>
                """,unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown("""
            <div class='info-box'>
                <h4 style='color:#0f172a;margin:0 0 12px;text-align:center;'>💡 Misollar</h4>
                <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;'>
                    <div><b style='color:#ec4899;'>🎨 Rasm:</b>
                         <p style='color:#64748b;margin:3px 0;font-size:13px;'>"Ronaldoni chizib ber"</p></div>
                    <div><b style='color:#0ea5e9;'>📊 Fayl:</b>
                         <p style='color:#64748b;margin:3px 0;font-size:13px;'>"Biznes reja yaratib ber"</p></div>
                    <div><b style='color:#8b5cf6;'>🖼 Vision:</b>
                         <p style='color:#64748b;margin:3px 0;font-size:13px;'>Rasm yuklang + savol</p></div>
                    <div><b style='color:#10b981;'>💻 Kod:</b>
                         <p style='color:#64748b;margin:3px 0;font-size:13px;'>"Python kalkulyator yoz"</p></div>
                </div>
            </div>
        """,unsafe_allow_html=True)

    # Chat tarixi
    st.markdown("<div class='chat-area'>",unsafe_allow_html=True)
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            cont=m["content"]
            if isinstance(cont,list):
                for p in cont:
                    if isinstance(p,dict) and p.get("type")=="text":
                        st.markdown(p["text"])
            else:
                st.markdown(cont)
    st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("---")

    # Biriktirilgan fayllar (yuqorida ko'rsatish)
    if st.session_state.attached_files:
        badges="".join(
            f"<span class='file-badge'>{get_file_emoji(f['name'])} {f['name']}</span>"
            for f in st.session_state.attached_files
        )
        st.markdown(f"<div style='margin-bottom:10px;'><b>📎 Biriktirilgan:</b><br>{badges}</div>",
                    unsafe_allow_html=True)
        if st.button("🗑 Fayllarni tozalash",key="clf"):
            st.session_state.attached_files=[];st.session_state.uploaded_image=None
            st.session_state.uploaded_image_type=None;st.session_state.uploaded_file_text=""
            st.rerun()

    # Fayl yuklash zona (drag & drop, ctrl+v)
    with st.expander("➕ Fayl qo'shish — drag & drop yoki Ctrl+V",expanded=False):
        st.markdown("""
            <div class='upload-zone' id='upload-drop-zone'>
                <p style='color:#0284c7;font-size:15px;margin:0;'>
                    📎 Fayllarni bu yerga tashlang yoki Ctrl+V
                </p>
                <p style='color:#64748b;font-size:12px;margin:5px 0 0;'>
                    🖼 Rasm · 📄 PDF · 📝 DOCX · 🐍 Kod · 📊 CSV/Excel · 🌐 HTML
                </p>
            </div>
        """,unsafe_allow_html=True)

        uploaded=st.file_uploader("Fayl",label_visibility="collapsed",
                                   type=["jpg","jpeg","png","webp","gif","pdf","docx","doc","txt",
                                         "csv","xlsx","xls","json","yaml","xml","py","js","ts",
                                         "jsx","tsx","html","css","md","java","cpp","c","go",
                                         "rs","sh","svg","rb","php","kt","swift"],
                                   accept_multiple_files=True,key="mup")

        if uploaded:
            for f in uploaded:
                if any(a["name"]==f.name for a in st.session_state.attached_files):
                    continue
                if is_image_file(f):
                    b64=encode_image(f);mtype=get_image_media_type(f)
                    sel=st.session_state.get("mdl",DEFAULT_MODEL)
                    if not MODELS.get(sel,{}).get("vision",False):
                        st.warning("⚠️ Vision uchun 'LLaMA 4 Scout' tanlang!")
                    st.session_state.uploaded_image=b64;st.session_state.uploaded_image_type=mtype
                    st.image(f,caption=f"🖼 {f.name}",width=260)
                    st.session_state.attached_files.append({"name":f.name,"type":"image","data":b64,"media_type":mtype})
                    st.success(f"✅ {f.name}")
                else:
                    txt=process_doc(f)
                    if txt:st.session_state.uploaded_file_text+=f"\n\n=== {f.name} ===\n{txt}"
                    st.session_state.attached_files.append({"name":f.name,"type":"document","text":txt or ""})
                    st.success(f"✅ {f.name} ({len(txt):,} belgi)")

    # ═══ GOOGLE GEMINI STYLE INPUT (YUQORIDA) ═══
    st.markdown("<br>",unsafe_allow_html=True)
    
    # Container uchun 2 kolonna: input va tugmalar
    col_input, col_controls = st.columns([5, 1])
    
    with col_input:
        prompt = st.chat_input("💭 Xabar yuboring...", key="ci")
    
    with col_controls:
        # Model dropdown
        sel_model_display = st.selectbox(
            "Model",
            options=list(MODELS.keys()),
            format_func=lambda x: MODELS[x]["label"].split("—")[0].strip(),
            key="mdl_top",
            label_visibility="collapsed"
        )
        
        # Jo'natish tugmasi (chat_input ishlatiladi, shuning uchun bu faqat vizual)
        # Haqiqiy jo'natish chat_input orqali

    # ── CHAT INPUT PROCESSING ──
    if prompt:
        ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        has_image=bool(st.session_state.uploaded_image)
        sel_model=st.session_state.get("mdl",DEFAULT_MODEL)
        temperature=st.session_state.get("temp",0.7)
        max_tok=st.session_state.get("maxtok",4096)
        want_img=is_image_request(prompt)
        want_file=is_file_request(prompt)

        if has_image and not MODELS.get(sel_model,{}).get("vision",False):
            active_model="meta-llama/llama-4-scout-17b-16e-instruct"
        else:
            active_model=sel_model

        if has_image:
            user_content=[
                {"type":"image_url","image_url":{"url":f"data:{st.session_state.uploaded_image_type};base64,{st.session_state.uploaded_image}"}},
                {"type":"text","text":prompt}
            ]
            names=", ".join(f["name"] for f in st.session_state.attached_files)
            disp=f"📎 *[{names}]* — {prompt}"
        else:
            user_content=prompt
            if st.session_state.attached_files:
                names=", ".join(f["name"] for f in st.session_state.attached_files)
                disp=f"📎 *[{names}]* — {prompt}"
            else:
                disp=prompt

        st.session_state.messages.append({"role":"user","content":disp})
        with st.chat_message("user"):st.markdown(disp)

        if chat_db:
            try:chat_db.append_row([ts,uname,"User",prompt])
            except Exception:pass

        # ═══ AI JAVOBI ═══
        with st.chat_message("assistant"):

            # ── RASM YARATISH ──
            if want_img and not has_image:
                ts_s=ts.replace(":","-").replace(" ","_")

                # FLUX Schnell (Together AI)
                with st.spinner("🎨 FLUX Schnell rasm yaratyapti (15-30 sek)..."):
                    img_data,err,eng_prompt=generate_image_flux(prompt)

                if img_data:
                    st.markdown("<div class='image-card'><h4 style='color:#7c3aed;margin:0 0 10px;'>🎨 FLUX Schnell — Yaratilgan Rasm</h4></div>",unsafe_allow_html=True)
                    st.image(img_data,caption=f"✅ {prompt[:60]}",use_container_width=True)
                    if eng_prompt and eng_prompt.lower()!=prompt.lower():
                        st.caption(f"🔤 Inglizcha: *{eng_prompt[:80]}*")
                    c1,c2=st.columns(2)
                    with c1:
                        st.download_button("⬇️ 🖼 PNG",img_data,file_name=f"somo_rasm_{ts_s}.png",
                                           mime="image/png",key=f"dl_img_{ts_s}",use_container_width=True)
                    with c2:
                        st.download_button("⬇️ WebP",img_data,file_name=f"somo_rasm_{ts_s}.webp",
                                           mime="image/webp",key=f"dl_img_webp_{ts_s}",use_container_width=True)
                    st.caption("🎨 Powered by Together AI FLUX Schnell")
                    res="✅ Rasm yaratildi!"
                else:
                    st.warning(f"{err}\n\n🔄 SVG bilan...")
                    with st.spinner("🎨 SVG yaratilmoqda..."):
                        svg=generate_svg_fallback(prompt)
                    if svg:
                        st.markdown("<div class='image-card'><h4 style='color:#7c3aed;margin:0 0 8px;'>🎨 SVG</h4></div>",unsafe_allow_html=True)
                        st.markdown(svg,unsafe_allow_html=True)
                        st.download_button("⬇️ SVG",svg.encode("utf-8"),file_name=f"somo_rasm_{ts_s}.svg",
                                           mime="image/svg+xml",key=f"dl_svg_{ts_s}",use_container_width=True)
                        res="SVG yaratildi"
                    else:
                        res="Rasm yaratib bo'lmadi"
                        st.error(res)

                st.session_state.messages.append({"role":"assistant","content":res})
                st.session_state.total_messages+=1

            # ── MATN / FAYL ──
            else:
                with st.spinner(f"🤔 {MODELS[active_model]['label']}..."):
                    try:
                        sys_instr=(
                            "Sening isming Somo AI. Seni Usmonov Sodiq yaratgan. "
                            "Professional, foydali, samimiy yordamchisan. "
                            "Rasmlarni ko'rib tahlil qila olasan. LaTeX ($...$). "
                            "Javoblarni aniq, strukturali qil."
                        )
                        if want_file:
                            sys_instr+=(
                                " FAYL: Taqdimot → ## + bullet. Jadval → Markdown/csv. "
                                "Hujjat → to'liq matn. HTML → ```html. Kod → to'liq kod. "
                                "DOIM to'liq yoz!"
                            )

                        msgs=[{"role":"system","content":sys_instr}]
                        if st.session_state.uploaded_file_text:
                            msgs.append({"role":"system","content":f"Fayllar:\n\n{st.session_state.uploaded_file_text[:6000]}"})

                        for old in st.session_state.messages[-20:]:
                            role=old["role"];cont=old["content"]
                            if isinstance(cont,list):
                                txt=" ".join(p["text"] for p in cont if isinstance(p,dict) and p.get("type")=="text")
                                msgs.append({"role":role,"content":txt})
                            else:
                                msgs.append({"role":role,"content":cont})

                        if has_image:
                            msgs[-1]={"role":"user","content":user_content}

                        if groq_client:
                            resp=groq_client.chat.completions.create(
                                messages=msgs,model=active_model,
                                temperature=temperature,max_tokens=max_tok
                            )
                            res=resp.choices[0].message.content
                            st.markdown(res)
                            st.caption(f"⚡ {MODELS[active_model]['label']}")

                            if want_file:
                                create_and_offer_files(res,ts,prompt)

                            st.session_state.messages.append({"role":"assistant","content":res})
                            st.session_state.total_messages+=1

                            if chat_db:
                                try:chat_db.append_row([ts,"Somo AI","Assistant",res])
                                except Exception:pass

                            if has_image or st.session_state.attached_files:
                                st.session_state.uploaded_image=None
                                st.session_state.uploaded_image_type=None
                                st.session_state.attached_files=[]
                                st.session_state.uploaded_file_text=""
                        else:
                            st.error("❌ GROQ_API_KEY yo'q!")
                            st.info("💡 console.groq.com → API Keys")

                    except Exception as e:
                        err=f"❌ {e}"
                        st.error(err)
                        if "model" in str(e).lower():
                            st.info("💡 Boshqa model tanlang")
                        st.session_state.messages.append({"role":"assistant","content":err})

# ════════════════ SHABLONLAR ════════════════
elif st.session_state.current_page=="templates":
    st.markdown("""
        <div style='text-align:center;margin:28px 0;'>
            <h1 style='font-size:40px;margin-bottom:10px;'>
                🎨 <span class='gradient-text'>Shablonlar</span>
            </h1>
            <p style='color:#64748b;font-size:17px;'>Tayyor shablonlar</p>
        </div>
    """,unsafe_allow_html=True)

    cat=st.selectbox("📁 Kategoriya:",list(TEMPLATES.keys()),key="tc")
    st.markdown(f"### {cat}")
    st.markdown("---")

    for i,tmpl in enumerate(TEMPLATES[cat]):
        with st.expander(f"{tmpl['icon']} {tmpl['title']} — {tmpl['desc']}",expanded=(i==0)):
            st.code(tmpl["prompt"],language="text")
            c1,c2=st.columns([3,1])
            with c1:
                if st.button("📋 Nusxalash",key=f"cp_{cat}_{i}",use_container_width=True):
                    st.success("✅ Chatga ko'chiring!")
            with c2:
                if st.button("🚀 Ishlatish",key=f"us_{cat}_{i}",use_container_width=True):
                    st.session_state.current_page="chat"
                    st.session_state.messages.append({"role":"user","content":tmpl["prompt"]})
                    st.rerun()

# ════════════════ FEEDBACK ════════════════
elif st.session_state.current_page=="feedback":
    st.markdown("""
        <div style='text-align:center;margin:28px 0;'>
            <h1 style='font-size:40px;margin-bottom:10px;'>
                💌 <span class='gradient-text'>Fikr-Mulohazalar</span>
            </h1>
            <p style='color:#64748b;font-size:17px;'>Fikringiz muhim!</p>
        </div>
    """,unsafe_allow_html=True)

    _,fc,_=st.columns([.1,1,.1])
    with fc:
        with st.form("fb_form"):
            st.markdown("### ⭐ Baholang")
            rating=st.select_slider("Baho",[1,2,3,4,5],value=5,
                                    format_func=lambda x:"⭐"*x,label_visibility="collapsed")
            st.markdown(f"<p style='text-align:center;font-size:48px;margin:14px 0;'>{'⭐'*rating}</p>",
                        unsafe_allow_html=True)
            cat_fb=st.selectbox("📂 Kategoriya",["Umumiy","Xato","Yangi funksiya","Model","Savol","Boshqa"],key="fbc")
            msg_fb=st.text_area("✍️ Xabar",placeholder="Fikr...",height=130,key="fbm")
            eml_fb=st.text_input("📧 Email (ixtiyoriy)",key="fbe")
            sub_fb=st.form_submit_button("📤 Yuborish",use_container_width=True,type="primary")

            if sub_fb:
                if not msg_fb:st.error("❌ Xabar!")
                elif len(msg_fb)<10:st.error("❌ ≥10 belgi!")
                elif feedback_db:
                    try:
                        feedback_db.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                uname,rating,cat_fb,msg_fb,eml_fb or "N/A","Yangi"])
                        st.balloons()
                        st.markdown("<div class='success-msg'>✅ Rahmat! 🙏</div>",unsafe_allow_html=True)
                        time.sleep(2);st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

# ═══════════════════════════════════════════════════════════════
# 17. FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("<br><br>",unsafe_allow_html=True)
st.markdown("""
    <div style='text-align:center;color:#94a3b8;padding:28px;
                border-top:2px solid #e2e8f0;
                background:linear-gradient(180deg,transparent,rgba(14,165,233,.04));'>
        <p style='margin:8px 0;font-size:18px;font-weight:700;'>🌌 Somo AI Infinity</p>
        <p style='margin:6px 0;color:#64748b;'>
            <span class='badge badge-groq'>⚡ Groq</span>
            <span class='badge badge-flux'>🎨 FLUX</span>
        </p>
        <p style='margin:6px 0;font-size:13px;color:#64748b;'>
            Llama 3.3 70B · LLaMA 4 Scout · Mixtral · FLUX Schnell
        </p>
        <p style='margin:6px 0;'>
            👨‍💻 <strong>Usmonov Sodiq</strong> | 🤝 <strong>Davlatov Mironshoh</strong>
        </p>
        <p style='margin:12px 0 0;font-size:12px;'>
            © 2026 Somo AI | v4.0 Pro
        </p>
    </div>
""",unsafe_allow_html=True)
