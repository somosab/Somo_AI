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

/* DASHBOARD KARTALAR */
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
    .card-box { min-width:150px !important; padding:20px !important; margin-bottom:15px !important; }
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

/* TABLAR */
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

/* CHAT */
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

/* METRIC KARTA */
.metric-card {
    background:linear-gradient(135deg,#fff,#f0f9ff);
    border-radius:12px; padding:15px; text-align:center;
    border:2px solid #bae6fd; transition:0.3s;
}
.metric-card:hover {
    transform:translateY(-5px);
    box-shadow:0 10px 25px rgba(14,165,233,0.2);
}

/* UPLOAD ZONA */
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

/* FAYL BADGE */
.file-badge {
    display:inline-flex; align-items:center; gap:8px;
    background:linear-gradient(135deg,#e0f2fe,#ddd6fe);
    border:1px solid #7dd3fc; border-radius:20px;
    padding:6px 14px; font-size:13px; font-weight:600;
    color:#0284c7; margin:4px;
}

/* SUCCESS */
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

/* VISION BADGE */
.vision-badge {
    background:linear-gradient(135deg,#8b5cf6,#6366f1);
    color:white; padding:4px 12px; border-radius:20px;
    font-size:12px; font-weight:700;
    display:inline-block; margin-bottom:10px;
}

/* DOWNLOAD KARTA */
.download-card {
    background:linear-gradient(135deg,#f0fdf4,#dcfce7);
    border:2px solid #86efac; border-radius:15px;
    padding:20px; margin:10px 0;
    box-shadow:0 4px 15px rgba(16,185,129,0.15);
}

/* TEMPLATE KARTA */
.template-card {
    background:white; border-radius:15px; padding:25px;
    border:2px solid #e2e8f0; transition:0.3s; cursor:pointer;
}
.template-card:hover {
    transform:translateY(-8px);
    box-shadow:0 15px 35px rgba(99,102,241,0.2);
    border-color:#6366f1;
}

/* FEEDBACK */
.feedback-box {
    background:linear-gradient(145deg,#fff,#f8fafc);
    border-radius:20px; padding:30px; margin:20px 0;
    box-shadow:0 10px 30px rgba(0,0,0,0.08);
    border:2px solid #e2e8f0;
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
    }.get(f.type, "image/jpeg")

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
# 5. FAYL YARATISH VA YUKLAB BERISH (ASOSIY)
# ───────────────────────────────────────────────
def create_and_offer_files(ai_response, ts):
    """
    AI javobini tahlil qilib, tegishli fayllarni
    to'g'ridan-to'g'ri yaratib yuklab beradi.
    """
    ext_map = {
        "python":"py","py":"py","javascript":"js","js":"js",
        "typescript":"ts","ts":"ts","html":"html","css":"css",
        "json":"json","csv":"csv","sql":"sql","bash":"sh",
        "shell":"sh","sh":"sh","yaml":"yaml","xml":"xml",
        "markdown":"md","md":"md","jsx":"jsx","tsx":"tsx",
        "java":"java","cpp":"cpp","c":"c","rust":"rs",
        "go":"go","php":"php","ruby":"rb","swift":"swift",
        "kotlin":"kt","r":"r","svg":"svg","txt":"txt","text":"txt",
    }

    ts_safe = ts.replace(":","-").replace(" ","_")
    blocks  = extract_code_blocks(ai_response)

    # ── PIL RASM YARATISH ──────────────────────
    pil_blocks = [(l,c) for l,c in blocks if "PIL" in c or "ImageDraw" in c or "Image.new" in c]
    if pil_blocks:
        try:
            from PIL import Image, ImageDraw, ImageFont
            saved = {}
            orig_save = Image.Image.save

            def fake_save(self, fp, *args, **kwargs):
                buf = io.BytesIO()
                fmt = kwargs.get("format","PNG")
                orig_save(self, buf, format=fmt)
                buf.seek(0)
                key = fp if isinstance(fp, str) else f"rasm_{len(saved)}.png"
                saved[key] = buf.read()

            Image.Image.save = fake_save
            ns = {"Image":Image,"ImageDraw":ImageDraw,"ImageFont":ImageFont,"io":io}
            for _, code in pil_blocks:
                try:
                    exec(code.strip(), ns)
                except Exception:
                    pass
            Image.Image.save = orig_save

            if saved:
                st.markdown("""
                    <div class='download-card'>
                        <h4 style='color:#059669;margin:0 0 15px;'>
                            🖼 Yaratilgan rasm(lar)
                        </h4>
                """, unsafe_allow_html=True)
                for fname, data in saved.items():
                    clean = os.path.basename(fname)
                    if not clean.endswith((".png",".jpg",".jpeg",".bmp")):
                        clean += ".png"
                    st.image(data, caption=f"✅ {clean}", use_container_width=True)
                    st.download_button(
                        label=f"⬇️ {clean} yuklab olish",
                        data=data, file_name=clean, mime="image/png",
                        key=f"dl_img_{ts_safe}_{clean}",
                        use_container_width=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)
                return
        except Exception as e:
            pass

    # ── SVG RASM ──────────────────────────────
    svg_blocks = [(l,c) for l,c in blocks if l.lower()=="svg" or c.strip().startswith("<svg")]
    if svg_blocks:
        st.markdown("""
            <div class='download-card'>
                <h4 style='color:#059669;margin:0 0 15px;'>🎨 Yaratilgan SVG rasm</h4>
        """, unsafe_allow_html=True)
        for i,(_, code) in enumerate(svg_blocks):
            svg_clean = code.strip()
            st.markdown(svg_clean, unsafe_allow_html=True)
            fname = f"somo_rasm_{ts_safe}_{i}.svg"
            st.download_button(
                label=f"⬇️ {fname} yuklab olish",
                data=svg_clean.encode("utf-8"),
                file_name=fname, mime="image/svg+xml",
                key=f"dl_svg_{ts_safe}_{i}",
                use_container_width=True
            )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── HTML FAYL ─────────────────────────────
    html_blocks = [(l,c) for l,c in blocks if l.lower()=="html"]
    if html_blocks:
        st.markdown("""
            <div class='download-card'>
                <h4 style='color:#059669;margin:0 0 15px;'>🌐 Yaratilgan HTML fayl</h4>
        """, unsafe_allow_html=True)
        for i,(_, code) in enumerate(html_blocks):
            with st.expander(f"👁 HTML Preview #{i+1}", expanded=True):
                st.components.v1.html(code.strip(), height=400, scrolling=True)
            fname = f"somo_page_{ts_safe}_{i}.html"
            st.download_button(
                label=f"⬇️ {fname} yuklab olish",
                data=code.strip().encode("utf-8"),
                file_name=fname, mime="text/html",
                key=f"dl_html_{ts_safe}_{i}",
                use_container_width=True
            )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── CSV JADVAL ────────────────────────────
    csv_blocks = [(l,c) for l,c in blocks if l.lower()=="csv"]
    table_match = re.search(
        r"\|(.+\|)+\n(\|[-:| ]+\|)+\n((\|.+\|\n?)+)", ai_response
    )

    if csv_blocks or table_match:
        st.markdown("""
            <div class='download-card'>
                <h4 style='color:#059669;margin:0 0 15px;'>📊 Yaratilgan CSV jadval</h4>
        """, unsafe_allow_html=True)

        if csv_blocks:
            for i,(_, code) in enumerate(csv_blocks):
                fname = f"somo_jadval_{ts_safe}_{i}.csv"
                st.download_button(
                    label=f"⬇️ {fname} yuklab olish",
                    data=code.strip().encode("utf-8"),
                    file_name=fname, mime="text/csv",
                    key=f"dl_csv_block_{ts_safe}_{i}",
                    use_container_width=True
                )
        elif table_match:
            rows = []
            for line in table_match.group(0).strip().split("\n"):
                if "---" not in line:
                    cells = [c.strip() for c in line.strip("|").split("|")]
                    rows.append(cells)
            buf = io.StringIO()
            csv.writer(buf).writerows(rows)
            fname = f"somo_jadval_{ts_safe}.csv"
            st.download_button(
                label=f"⬇️ {fname} yuklab olish",
                data=buf.getvalue().encode("utf-8"),
                file_name=fname, mime="text/csv",
                key=f"dl_csv_table_{ts_safe}",
                use_container_width=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── BOSHQA KOD FAYLLAR ────────────────────
    other = [(l,c) for l,c in blocks
             if l.lower() not in ("svg","html","csv","")
             and "PIL" not in c and "ImageDraw" not in c]

    if other:
        st.markdown("""
            <div class='download-card'>
                <h4 style='color:#059669;margin:0 0 15px;'>💾 Tayyor fayllar</h4>
        """, unsafe_allow_html=True)
        cols = st.columns(min(len(other), 3))
        for i,(lang, code) in enumerate(other):
            ext   = ext_map.get(lang.strip().lower(), "txt")
            fname = f"somo_{ts_safe}_{i}.{ext}"
            with cols[i % len(cols)]:
                st.download_button(
                    label=f"{get_file_emoji(fname)} .{ext} yuklab olish",
                    data=code.strip().encode("utf-8"),
                    file_name=fname, mime="text/plain",
                    key=f"dl_code_{ts_safe}_{i}",
                    use_container_width=True
                )
        st.markdown("</div>", unsafe_allow_html=True)

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
                📎 Har qanday fayl &nbsp;|&nbsp; 💾 Fayl yaratish
            </p>
        </div>
    """, unsafe_allow_html=True)

    _, c2, _ = st.columns([0.25,1,0.25])
    with c2:
        t1, t2, t3 = st.tabs(["🔒 Kirish","✍️ Ro'yxatdan o'tish","ℹ️ Ma'lumot"])

        # KIRISH
        with t1:
            with st.form("login_form"):
                st.markdown("### 🔐 Hisobingizga kiring")
                u_in = st.text_input("👤 Username", placeholder="Username kiriting", key="lu")
                p_in = st.text_input("🔑 Parol", type="password", placeholder="Parol kiriting", key="lp")
                ca, cb = st.columns(2)
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
                                    cookies["somo_user_session"] = u_in; cookies.save()
                                st.success("✅ Muvaffaqiyatli!"); time.sleep(0.5); st.rerun()
                        else:
                            st.error("❌ Login yoki parol xato!")
                    except Exception as e:
                        st.error(f"❌ {e}")

        # RO'YXAT
        with t2:
            with st.form("reg_form"):
                st.markdown("### ✨ Yangi hisob yaratish")
                nu  = st.text_input("👤 Username", placeholder="Kamida 3 ta belgi", key="ru")
                np  = st.text_input("🔑 Parol", type="password", placeholder="Kamida 6 ta belgi", key="rp")
                npc = st.text_input("🔑 Tasdiqlang", type="password", placeholder="Qayta kiriting", key="rc")
                ag  = st.checkbox("Foydalanish shartlariga roziman")
                sub2 = st.form_submit_button("✨ Hisob yaratish", use_container_width=True)
                if sub2:
                    if not ag: st.error("❌ Shartlarga rozilik!")
                    elif not nu or not np: st.error("❌ Barcha maydonlar!")
                    elif len(nu)<3: st.error("❌ Username ≥ 3 belgi!")
                    elif len(np)<6: st.error("❌ Parol ≥ 6 belgi!")
                    elif np!=npc: st.error("❌ Parollar mos emas!")
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

        # MA'LUMOT
        with t3:
            st.markdown("""
                ### 🌟 Somo AI Infinity — Versiya 2.2 Pro

                | Funksiya | Tavsif |
                |---------|--------|
                | 🧠 **70B AI** | Llama 3.3 — kuchli, aniq javoblar |
                | 🖼 **Vision** | Rasm yuklang — AI tahlil qiladi |
                | 📎 **25+ format** | PDF, DOCX, kod, CSV, Excel... |
                | 💾 **Fayl yaratish** | Rasm, HTML, CSV, kod — yuklab olish |
                | 🎨 **SVG/HTML** | Preview bilan chiroyli ko'rsatish |
                | 🤖 **4 model** | Llama, Vision, Mixtral, Gemma |
                | 🎨 **Shablonlar** | Biznes, Dasturlash, Ta'lim |

                ---
                📧 support@somoai.uz
                👨‍💻 Yaratuvchi: Usmonov Sodiq | v2.2 Pro
            """)

    st.markdown("""
        <div style='text-align:center;margin-top:60px;color:#94a3b8;'>
            <p>🔒 Xavfsiz | 🌐 24/7 Onlayn</p>
            <p>© 2026 Somo AI | Barcha huquqlar himoyalangan</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ───────────────────────────────────────────────
# 9. SESSION STATE INICIALIZATSIYA
# ───────────────────────────────────────────────
defaults = {
    "messages":[],"total_messages":0,"current_page":"chat",
    "uploaded_file_text":"","uploaded_image":None,
    "uploaded_image_type":None,"attached_files":[]
}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ───────────────────────────────────────────────
# 10. SIDEBAR
# ───────────────────────────────────────────────
with st.sidebar:
    uname = st.session_state.username
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
    for label, page in [("💬 Chat","chat"),("🎨 Shablonlar","templates"),("💌 Fikr bildirish","feedback")]:
        if st.button(label, use_container_width=True, key=f"nav_{page}"):
            st.session_state.current_page = page; st.rerun()

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

    if st.session_state.current_page == "chat":
        st.markdown("### 🎛 Boshqaruv")
        if st.button("🗑 Chatni tozalash", use_container_width=True, key="clr"):
            for k in ["messages","uploaded_image","uploaded_image_type",
                      "uploaded_file_text","attached_files"]:
                st.session_state[k] = [] if k in ["messages","attached_files"] else (None if "image" in k else "")
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
            "⚖️ Muvozanatli" if temperature<0.7 else
            "🎨 Ijodiy"
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

# ════════════════ CHAT ════════════════
if st.session_state.current_page == "chat":

    # Dashboard
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
                    <h1 style='font-size:48px;margin-bottom:15px;'>🧠</h1>
                    <h3 style='color:#0f172a;margin-bottom:10px;'>Aqlli Tahlil</h3>
                    <p style='color:#64748b;line-height:1.6;'>
                        Murakkab mantiq, matematika va muammolarni professional yechish
                    </p>
                </div>
                <div class='card-box'>
                    <h1 style='font-size:48px;margin-bottom:15px;'>📎</h1>
                    <h3 style='color:#0f172a;margin-bottom:10px;'>Har Qanday Fayl</h3>
                    <p style='color:#64748b;line-height:1.6;'>
                        Rasm, PDF, kod, CSV, Excel — yuklang va tahlil qiling
                    </p>
                </div>
                <div class='card-box'>
                    <h1 style='font-size:48px;margin-bottom:15px;'>💾</h1>
                    <h3 style='color:#0f172a;margin-bottom:10px;'>Fayl Yaratish</h3>
                    <p style='color:#64748b;line-height:1.6;'>
                        Rasm, HTML, SVG, CSV, kod — AI yaratib darhol yuklab beradi
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background:linear-gradient(135deg,rgba(14,165,233,.1),rgba(99,102,241,.1));
                        padding:25px;border-radius:20px;margin:10px 0;'>
                <h3 style='color:#0f172a;margin-bottom:15px;text-align:center;'>
                    💡 Nima qila olaman?
                </h3>
                <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
                            gap:15px;text-align:left;'>
                    <div>
                        <strong style='color:#0284c7;'>🎨 Rasm yaratish</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            "Ko'k rangda landshaft rasmi yarat" → PNG yuklab olish
                        </p>
                    </div>
                    <div>
                        <strong style='color:#6366f1;'>🌐 HTML sahifa</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            "Portfolio sahifasi yarat" → Preview + yuklab olish
                        </p>
                    </div>
                    <div>
                        <strong style='color:#8b5cf6;'>📊 CSV/Excel</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            "Oylik xarajatlar jadval" → CSV yuklab olish
                        </p>
                    </div>
                    <div>
                        <strong style='color:#ec4899;'>🐍 Kod fayl</strong>
                        <p style='color:#64748b;margin:5px 0;font-size:14px;'>
                            "Python kalkulyator yoz" → .py yuklab olish
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Chat tarixi
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            content = m["content"]
            if isinstance(content, list):
                for p in content:
                    if isinstance(p,dict) and p.get("type")=="text":
                        st.markdown(p["text"])
            else:
                st.markdown(content)

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
        if st.button("🗑 Fayllarni tozalash", key="clr_files"):
            st.session_state.attached_files = []
            st.session_state.uploaded_image = None
            st.session_state.uploaded_image_type = None
            st.session_state.uploaded_file_text = ""
            st.rerun()

    # FAYL BIRIKTIRISH ZONA
    with st.expander("➕ Fayl biriktirish — rasm, PDF, kod, CSV va boshqalar", expanded=False):
        st.markdown("""
            <div class='upload-zone'>
                <p style='color:#0284c7;font-size:16px;margin:0;'>
                    📎 Istalgan faylni yuklang
                </p>
                <p style='color:#64748b;font-size:13px;margin:5px 0 0;'>
                    🖼 JPG/PNG/WEBP · 📄 PDF · 📝 DOCX · 🐍 Python ·
                    📊 CSV/Excel · 🌐 HTML/CSS · 🔧 JSON
                </p>
            </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Fayl", label_visibility="collapsed",
            type=["jpg","jpeg","png","webp","gif","pdf","docx","doc","txt","csv",
                  "xlsx","xls","json","yaml","xml","py","js","ts","jsx","tsx",
                  "html","css","md","java","cpp","c","go","rs","sh","svg","mp3","wav"],
            accept_multiple_files=True, key="mup"
        )

        if uploaded:
            for f in uploaded:
                if any(a["name"]==f.name for a in st.session_state.attached_files):
                    continue
                if is_image_file(f):
                    b64  = encode_image(f)
                    mtype = get_image_media_type(f)
                    st.session_state.uploaded_image      = b64
                    st.session_state.uploaded_image_type = mtype
                    st.image(f, caption=f"🖼 {f.name}", width=280)
                    st.session_state.attached_files.append(
                        {"name":f.name,"type":"image","data":b64,"media_type":mtype}
                    )
                    st.success(f"✅ Rasm: {f.name}")
                else:
                    txt = process_doc(f)
                    if txt:
                        st.session_state.uploaded_file_text += f"\n\n=== {f.name} ===\n{txt}"
                    st.session_state.attached_files.append(
                        {"name":f.name,"type":"document","text":txt or ""}
                    )
                    st.success(f"✅ Fayl: {f.name} ({len(txt):,} belgi)")

    # CHAT INPUT
    prompt = st.chat_input(
        "💭 Xabar yuboring...  |  ➕ fayl biriktirish — yuqoridagi tugma",
        key="ci"
    )

    if prompt:
        ts        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        has_image = bool(st.session_state.uploaded_image)

        # User content
        if has_image:
            user_content = [
                {"type":"image_url","image_url":{
                    "url":f"data:{st.session_state.uploaded_image_type};base64,{st.session_state.uploaded_image}"
                }},
                {"type":"text","text":prompt}
            ]
            names = ", ".join(f["name"] for f in st.session_state.attached_files)
            disp  = f"📎 *[{names}]* — {prompt}"
        else:
            user_content = prompt
            if st.session_state.attached_files:
                names = ", ".join(f["name"] for f in st.session_state.attached_files)
                disp  = f"📎 *[{names}]* — {prompt}"
            else:
                disp = prompt

        st.session_state.messages.append({"role":"user","content":disp})
        with st.chat_message("user"): st.markdown(disp)

        if chat_db:
            try: chat_db.append_row([ts, uname, "User", prompt])
            except Exception: pass

        # AI JAVOBI
        with st.chat_message("assistant"):
            with st.spinner("🤔 O'ylayapman..."):
                try:
                    sys_instr = (
                        "Sening isming Somo AI. Seni Usmonov Sodiq yaratgan. "
                        "Sen professional yordamchi sun'iy intellektsan. "
                        "Rasmlarni ko'rib tahlil qila olasan. "

                        "FAYL YARATISH QOIDASI (JUDA MUHIM): "
                        "Foydalanuvchi rasm, grafika, SVG, HTML sahifa, "
                        "CSS dizayn, CSV jadval, Excel, JSON, kod fayl "
                        "yoki boshqa kontent so'rasa — "
                        "FAQAT KOD BLOKI ICHIDA TO'LIQ TAYYOR MAZMUNNI YOZ. "
                        "Hech qachon 'siz buni qilishingiz mumkin' dema. "
                        "Balki O'ZING to'liq bajar va kod bloki ichida ber. "

                        "Rasm uchun: PIL bilan to'liq ishlaydi gan ```python blok yoz. "
                        "SVG uchun: ```svg blok ichida to'liq SVG kodi yoz. "
                        "HTML uchun: ```html blok ichida to'liq sahifa yoz. "
                        "CSV uchun: ```csv blok ichida to'liq jadval yoz. "
                        "Kod uchun: tegishli til blokida to'liq ishlaydigan kod yoz. "

                        "Matematikani LaTeX ($...$) da yoz. "
                        "Javoblarni o'qishga qulay va strukturalashtirilgan qil."
                    )

                    sel_model = st.session_state.get("mdl","llama-3.3-70b-versatile")
                    model     = "meta-llama/llama-4-scout-17b-16e-instruct" if has_image else sel_model

                    msgs = [{"role":"system","content":sys_instr}]

                    if st.session_state.uploaded_file_text:
                        msgs.append({
                            "role":"system",
                            "content":f"Yuklangan fayllar:\n\n{st.session_state.uploaded_file_text[:6000]}"
                        })

                    for old in st.session_state.messages[-20:]:
                        role = old["role"]
                        cont = old["content"]
                        if isinstance(cont, list):
                            txt = " ".join(p["text"] for p in cont if isinstance(p,dict) and p.get("type")=="text")
                            msgs.append({"role":role,"content":txt})
                        else:
                            msgs.append({"role":role,"content":cont})

                    if has_image:
                        msgs[-1] = {"role":"user","content":user_content}

                    if client:
                        resp = client.chat.completions.create(
                            messages=msgs, model=model,
                            temperature=temperature, max_tokens=4000
                        )
                        res = resp.choices[0].message.content
                        st.markdown(res)

                        # FAYLNI YARATIB YUKLAB BER
                        create_and_offer_files(res, ts)

                        st.session_state.messages.append({"role":"assistant","content":res})
                        st.session_state.total_messages += 1

                        if chat_db:
                            try: chat_db.append_row([ts,"Somo AI","Assistant",res])
                            except Exception: pass

                        # Fayllarni tozalash
                        if has_image or st.session_state.attached_files:
                            st.session_state.uploaded_image      = None
                            st.session_state.uploaded_image_type = None
                            st.session_state.attached_files      = []
                            st.session_state.uploaded_file_text  = ""
                    else:
                        st.error("❌ AI xizmati mavjud emas.")

                except Exception as e:
                    err = f"❌ Xatolik: {e}"
                    st.error(err)
                    st.session_state.messages.append({"role":"assistant","content":err})

# ════════════════ SHABLONLAR ════════════════
elif st.session_state.current_page == "templates":
    st.markdown("""
        <div style='text-align:center;margin:30px 0;'>
            <h1 style='font-size:42px;margin-bottom:15px;'>
                🎨 <span class='gradient-text'>Shablonlar Markazi</span>
            </h1>
            <p style='color:#64748b;font-size:18px;'>
                3 professional shablon bilan ishni tezlashtiring
            </p>
        </div>
    """, unsafe_allow_html=True)

    cat = st.selectbox("📁 Kategoriya:", list(TEMPLATES.keys()), key="tc")
    st.markdown(f"### {cat} shablonlari")
    st.markdown("---")

    for i, tmpl in enumerate(TEMPLATES[cat]):
        with st.expander(f"{tmpl['icon']} {tmpl['title']}", expanded=(i==0)):
            st.markdown(f"**📝 Tavsif:** {tmpl['description']}")
            st.code(tmpl["prompt"], language="text")
            c1,c2 = st.columns([3,1])
            with c1:
                if st.button("📋 Nusxalash", key=f"cp_{cat}_{i}", use_container_width=True):
                    st.success("✅ Chatga joylashtiring!")
            with c2:
                if st.button("🚀 Ishlatish", key=f"us_{cat}_{i}", use_container_width=True):
                    st.session_state.current_page = "chat"
                    st.session_state.messages.append({"role":"user","content":tmpl["prompt"]})
                    st.rerun()

    st.info("💡 [qavs ichidagi] joylarni o'z ma'lumotlaringiz bilan to'ldiring!")

# ════════════════ FEEDBACK ════════════════
elif st.session_state.current_page == "feedback":
    st.markdown("""
        <div style='text-align:center;margin:30px 0;'>
            <h1 style='font-size:42px;margin-bottom:15px;'>
                💌 <span class='gradient-text'>Fikr-Mulohazalar</span>
            </h1>
            <p style='color:#64748b;font-size:18px;'>Sizning fikringiz biz uchun muhim!</p>
        </div>
    """, unsafe_allow_html=True)

    _, fc2, _ = st.columns([0.1,1,0.1])
    with fc2:
        with st.form("fb_form"):
            st.markdown("### ⭐ Baholang")
            rating = st.select_slider(
                "Baho", [1,2,3,4,5], value=5,
                format_func=lambda x:"⭐"*x,
                label_visibility="collapsed"
            )
            st.markdown(
                f"<p style='text-align:center;font-size:48px;margin:20px 0;'>{'⭐'*rating}</p>",
                unsafe_allow_html=True
            )
            cat_fb = st.selectbox("📂 Kategoriya",
                ["Umumiy fikr","Xato haqida","Yangi funksiya taklifi","Savol","Boshqa"],
                key="fbc")
            msg_fb  = st.text_area("✍️ Xabaringiz", placeholder="Fikr-mulohazalaringiz...",
                                   height=150, key="fbm")
            email_fb = st.text_input("📧 Email (ixtiyoriy)", placeholder="email@example.com", key="fbe")
            sub_fb   = st.form_submit_button("📤 Yuborish", use_container_width=True, type="primary")

            if sub_fb:
                if not msg_fb: st.error("❌ Xabar yozing!")
                elif len(msg_fb)<10: st.error("❌ Kamida 10 ta belgi!")
                elif feedback_db:
                    try:
                        feedback_db.append_row([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            uname, rating, cat_fb, msg_fb,
                            email_fb or "N/A", "Yangi"
                        ])
                        st.balloons()
                        st.markdown("""
                            <div class='success-message'>
                                ✅ Rahmat! Fikringiz muvaffaqiyatli yuborildi.
                            </div>
                        """, unsafe_allow_html=True)
                        time.sleep(2); st.rerun()
                    except Exception as e: st.error(f"❌ {e}")
                else: st.error("❌ Baza mavjud emas!")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📊 Statistika")
    if feedback_db:
        try:
            all_fb = feedback_db.get_all_records()
            if len(all_fb)>1:
                fc1,fc2,fc3 = st.columns(3)
                rtgs = [int(f.get("Rating",0)) for f in all_fb[1:] if f.get("Rating")]
                with fc1: st.metric("📨 Jami", len(all_fb)-1)
                with fc2: st.metric("⭐ O'rtacha", f"{sum(rtgs)/len(rtgs):.1f}" if rtgs else "—")
                with fc3: st.metric("🆕 Yangilar", len([f for f in all_fb[-10:] if f.get("Status")=="Yangi"]))
            else:
                st.info("💬 Hali fikr-mulohazalar yo'q!")
        except Exception:
            st.warning("⚠️ Statistika yuklanmadi")

# ───────────────────────────────────────────────
# 12. FOOTER
# ───────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align:center;color:#94a3b8;padding:30px;
                border-top:2px solid #e2e8f0;
                background:linear-gradient(180deg,transparent,rgba(14,165,233,.05));'>
        <p style='margin:8px 0;font-size:18px;font-weight:600;'>
            🌌 <strong>Somo AI Infinity</strong>
        </p>
        <p style='margin:8px 0;color:#64748b;'>
            Powered by Groq · Llama 3.3 (70B) · LLaMA 4 Scout Vision
        </p>
        <p style='margin:8px 0;'>👨‍💻 Yaratuvchi: <strong>Usmonov Sodiq</strong></p>
        <p style='margin:8px 0;'>👨‍💻 Yordamchi: <strong>Davlatov Mironshoh</strong></p>
        <p style='margin:8px 0;font-size:13px;'>
            📧 support@somoai.uz | 🌐 www.somoai.uz
        </p>
        <p style='margin:15px 0 0;font-size:12px;color:#94a3b8;'>
            © 2026 Barcha huquqlar himoyalangan | Versiya 2.2 Pro
        </p>
    </div>
""", unsafe_allow_html=True)
