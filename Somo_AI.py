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
st.set_page_config(page_title="Somo AI | Universal Infinity", page_icon="🌌", layout="wide")

# Cookies - Sessiyani eslab qolish (Bir marta kirish kifoya)
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026_Final_V3"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. PREMIUM ADAPTIVE DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { background-color: #f8fafc !important; }

    /* BURCHAKDAGI XATOLIKLARNI YO'QOTISH VA STANDART STRELKANI QAYTARISH */
    [data-testid="stSidebarNav"] { display: none !important; }
    .st-emotion-cache-1vt458p, .st-emotion-cache-k77z8z, .st-emotion-cache-12fmjuu { 
        font-size: 0px !important; 
        color: transparent !important;
    }

    /* SIDEBAR - MUKAMMAL OCHIQ KO'K GRADIENT */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e0f2fe 0%, #bae6fd 100%) !important;
        border-right: 2px solid #7dd3fc;
    }
    [data-testid="stSidebar"] section, [data-testid="stSidebar"] .stVerticalBlock {
        background: transparent !important;
    }

    /* SIDEBAR MATNLARI */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #0369a1 !important;
        font-weight: 700 !important;
        text-shadow: 0px 1px 2px rgba(255,255,255,0.5);
    }

    /* SIDEBAR TUGMALARI */
    div[data-testid="stSidebar"] button {
        background: white !important;
        color: #0284c7 !important;
        border: 2px solid #0ea5e9 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: 0.3s all ease;
    }
    div[data-testid="stSidebar"] button:hover {
        background: #0ea5e9 !important;
        color: white !important;
        transform: translateY(-2px);
    }

    /* DASHBOARD KARTALARI - PC VA MOBIL UCHUN MOSLASHUVCHAN */
    .dashboard-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: center;
        margin-top: 20px;
    }
    
    .card-box {
        background: white;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: 0.4s ease;
        flex: 1;
        min-width: 280px; /* PC da kattaroq */
        max-width: 350px;
    }

    /* 📱 MOBIL QURILMALAR UCHUN MAXSUS O'LCHAM */
    @media (max-width: 768px) {
        .card-box {
            min-width: 140px !important; /* Telefonda kichrayadi */
            padding: 15px !important;
            margin-bottom: 5px !important;
        }
        .card-box h1 { font-size: 22px !important; }
        .card-box h3 { font-size: 15px !important; }
        .card-box p { font-size: 11px !important; }
        .gradient-title { font-size: 24px !important; }
    }

    .gradient-text {
        background: linear-gradient(90deg, #0284c7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. SERVISLARNI ULANISH ---
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

# --- 📂 4. FAYL PROTSESSOR ---
def process_doc(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.extract_raw_text(file).value
    except: return ""
    return ""

# --- 🔐 5. LOGIN VA ADMIN BLOKIROVKA ---
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user:
        recs = user_db.get_all_records()
        user_data = next((r for r in recs if str(r['username']) == session_user), None)
        # Faqat status 'active' bo'lsa kiradi
        if user_data and str(user_data.get('status')).lower() == 'active':
            st.session_state.username = session_user
            st.session_state.logged_in = True
        else:
            st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

def logout():
    cookies["somo_user_session"] = ""
    cookies.save()
    st.session_state.clear()
    st.rerun()

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; margin-top:50px;' class='gradient-title'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.1, 1, 0.1])
    with c2:
        tabs = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish"])
        with tabs[0]:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Parol", type='password', key="l_p")
            if st.button("Kirish 🚀", use_container_width=True):
                recs = user_db.get_all_records()
                hp = hashlib.sha256(p.encode()).hexdigest()
                user = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
                if user:
                    if str(user.get('status')).lower() == 'blocked':
                        st.error("🚫 Sizning hisobingiz bloklangan! Admin bilan bog'laning.")
                    else:
                        st.session_state.username = u
                        st.session_state.logged_in = True
                        cookies["somo_user_session"] = u
                        cookies.save()
                        st.rerun()
                else: st.error("❌ Login yoki parol xato!")
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS ---
if "messages" not in st.session_state: st.session_state.messages = []

# SIDEBAR (TOZA VA MUKAMMAL)
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 10px;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #6366f1); width: 70px; height: 70px; border-radius: 50%; margin: 0 auto; line-height: 70px; font-size: 30px; color: white; font-weight: bold; border: 3px solid white;'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='margin-top: 10px;'>{st.session_state.username}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **HUJJATLAR BILAN ISHLASH**")
    f_up = st.file_uploader("Fayl tanlang", type=["pdf", "docx"], label_visibility="collapsed")
    f_txt = process_doc(f_up) if f_up else ""
    
    st.markdown("<br>"*10, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish"): logout()

# DASHBOARD (MOSLASHUVCHAN)
if not st.session_state.messages:
    st.markdown(f"<h2 style='text-align: center;'>Xush kelibsiz, <span class='gradient-text'>{st.session_state.username}</span>!</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div class='dashboard-container'>
            <div class='card-box'><h1>🧠</h1><h3>Aqlli Tahlil</h3><p>Mantiqiy savollar va hisob-kitoblar</p></div>
            <div class='card-box'><h1>📄</h1><h3>Hujjatlar</h3><p>Fayllarni o'qish va tahlil</p></div>
            <div class='card-box'><h1>🎨</h1><h3>Ijodkorlik</h3><p>Yangi g'oyalar va ssenariylar</p></div>
        </div>
    """, unsafe_allow_html=True)

# CHAT TARIXI
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# INPUT VA AI JAVOBI (CHAT HISTORY TARTIBI BILAN)
if pr := st.chat_input("Somo AI ga xabar yuboring..."):
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Foydalanuvchi xabari
    st.session_state.messages.append({"role": "user", "content": pr})
    with st.chat_message("user"): st.markdown(pr)
    if chat_db:
        # Rasm dagi tartib: Time | User | Role | Message
        chat_db.append_row([now_time, st.session_state.username, "User", pr])

    # 2. Assistant javobi
    with st.chat_message("assistant"):
        try:
            instr = f"Isming Somo AI. Yaratuvching Usmonov Sodiq. Professional javob ber. Matematikani LaTeX ($...$) da yoz."
            msgs = [{"role": "system", "content": instr}]
            if f_txt: msgs.append({"role": "system", "content": f"Hujjat mazmuni: {f_txt[:3500]}"})
            for old in st.session_state.messages[-12:]: msgs.append(old)
            
            res = client.chat.completions.create(
                messages=msgs,
                model="llama-3.3-70b-versatile",
                temperature=0.6
            ).choices[0].message.content
            
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            
            if chat_db:
                # Rasm dagi tartib: Time | User | Role | Message
                chat_db.append_row([now_time, "Somo AI", "Assistant", res])
        except Exception as e:
            st.error(f"Xatolik yuz berdi!")

