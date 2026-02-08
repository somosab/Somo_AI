import streamlit as st
import pandas as pd
import gspread
import hashlib
import mammoth
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# --- 🛰 1. SISTEMA SOZLAMALARI ---
st.set_page_config(page_title="Somo AI | Infinity", page_icon="🌌", layout="wide")

# Cookies - Sessiyani xavfsiz saqlash
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Sky_Secret_2026_Final"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. MUKAMMAL OCHIQ KO'K DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { background-color: #f0f9ff !important; }

    /* BURCHAKDAGI XATO YOZUVLARNI YO'QOTISH */
    [data-testid="stSidebarNav"] { display: none !important; }
    .st-emotion-cache-1vt458p { display: none !important; }
    
    /* CHAP BO'LIM (SIDEBAR) - TOZA OCHIQ KO'K */
    [data-testid="stSidebar"] {
        background-color: #bae6fd !important;
        border-right: 2px solid #7dd3fc;
    }
    
    /* Sidebar ichidagi barcha bloklar rangini tekislash */
    [data-testid="stSidebar"] section, 
    [data-testid="stSidebar"] .stVerticalBlock {
        background-color: #bae6fd !important;
    }
    
    /* Sidebar matnlari */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span {
        color: #0369a1 !important;
        font-weight: 700 !important;
    }

    /* TUGMALAR DIZAYNI */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 15px !important;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        width: 100% !important;
        transition: 0.3s all ease !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }
    
    div[data-testid="stSidebar"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(14, 165, 233, 0.3) !important;
    }

    /* FAYL YUKLASH MAYDONI */
    [data-testid="stFileUploader"] {
        background-color: #f0f9ff !important;
        border: 2px dashed #0ea5e9 !important;
        border-radius: 15px !important;
    }

    /* ASOSIY SAHIFA KARTALARI */
    .card-box {
        background: white;
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        border: 1px solid #e0f2fe;
        transition: 0.4s;
    }
    .card-box:hover { 
        transform: translateY(-10px); 
        border-color: #0ea5e9;
    }
    
    .gradient-text {
        background: linear-gradient(90deg, #0284c7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. BAZA VA AI BILAN ALOQA ---
@st.cache_resource
def get_connections():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        return ss.sheet1, ss.worksheet("ChatHistory")
    except:
        return None, None

user_db, chat_db = get_connections()
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 📂 4. FAYL TAHLILI FUNKSIYASI ---
def process_doc(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.extract_raw_text(file).value
    except: return ""
    return ""

# --- 🔐 5. LOGIN VA TIZIMDAN CHIQISH ---
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user:
        st.session_state.username = session_user
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

# Tizimdan chiqishni to'g'irlaydigan funksiya
def perform_logout():
    cookies["somo_user_session"] = ""
    cookies.save()
    st.session_state.clear()
    st.rerun()

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; margin-top:50px;'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        choice = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
        with choice[0]:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Parol", type='password', key="l_p")
            if st.button("Kirish 🚀", use_container_width=True):
                data = user_db.get_all_records()
                hp = hashlib.sha256(p.encode()).hexdigest()
                user = next((r for r in data if str(r['username']) == u and str(r['password']) == hp), None)
                if user:
                    st.session_state.username = u
                    st.session_state.logged_in = True
                    cookies["somo_user_session"] = u
                    cookies.save()
                    st.rerun()
                else: st.error("Xato: Ma'lumotlar noto'g'ri!")
        with choice[1]:
            nu = st.text_input("Yangi Username", key="r_u")
            np = st.text_input("Yangi Parol", type='password', key="r_p")
            if st.button("Ro'yxatdan o'tish ✨", use_container_width=True):
                if nu and np:
                    hp = hashlib.sha256(np.encode()).hexdigest()
                    user_db.append_row([nu, hp, "active", str(datetime.now())])
                    st.success("Muvaffaqiyatli! Endi Kirish bo'limiga o'ting.")
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR (TOZA VA MUKAMMAL)
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #6366f1); width: 80px; height: 80px; border-radius: 50%; margin: 0 auto; line-height: 80px; font-size: 35px; color: white; font-weight: bold; border: 3px solid white;'>
                {st.session_state.username[0].upper()}
            </div>
            <h2 style='color: #0369a1; margin-top: 10px;'>{st.session_state.username}</h2>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **HUJJATLAR TAHLILI**")
    f = st.file_uploader("Fayl", type=["pdf", "docx"], label_visibility="collapsed")
    txt_ctx = process_doc(f) if f else ""
    if f: st.success("✅ Hujjat yuklandi")

    st.markdown("<br>"*10, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish"):
        perform_logout()

# DASHBOARD
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center; margin-top: 30px;'>Xush kelibsiz, <span class='gradient-text'>{st.session_state.username}</span>! ✨</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Somo AI - Har qanday savolingizga javob beruvchi universal yordamchi.</p>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    with cols[0]: st.markdown('<div class="card-box"><h1>🧠</h1><h3>Aqlli Tahlil</h3><p>Murakkab matematika va mantiqiy savollar</p></div>', unsafe_allow_html=True)
    with cols[1]: st.markdown('<div class="card-box"><h1>📄</h1><h3>Hujjatlar</h3><p>PDF va Word fayllarni o\'qish va xulosalash</p></div>', unsafe_allow_html=True)
    with cols[2]: st.markdown('<div class="card-box"><h1>🎨</h1><h3>Ijodkorlik</h3><p>Kodlar, ssenariylar va biznes g\'oyalar</p></div>', unsafe_allow_html=True)

# CHAT KO'RSATISH
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# INPUT VA AI JAVOBI
if pr := st.chat_input("Somo AI ga savol bering..."):
    st.session_state.messages.append({"role": "user", "content": pr})
    with st.chat_message("user"): st.markdown(pr)

    with st.chat_message("assistant"):
        try:
            # System Prompt
            instr = f"Sening isming Somo AI. Yaratuvching: Usmonov Sodiq. Foydalanuvchi: {st.session_state.username}. Professional javob ber. Matematikani LaTeX ($...$) da yoz."
            
            msgs = [{"role": "system", "content": instr}]
            if txt_ctx: msgs.append({"role": "system", "content": f"Hujjat mazmuni: {txt_ctx[:4000]}"})
            
            # Xotira (Oxirgi 12 xabar)
            for old in st.session_state.messages[-12:]: msgs.append(old)
            
            res_box = st.empty()
            full_res = client.chat.completions.create(
                messages=msgs,
                model="llama-3.3-70b-versatile",
                temperature=0.6
            ).choices[0].message.content
            
            res_box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            if chat_db: chat_db.append_row([st.session_state.username, pr, full_res[:500], str(datetime.now())])
        except Exception as e:
            st.error(f"Xatolik: {str(e)}")
