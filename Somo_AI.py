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

# Cookies - Sessiyani 30 kungacha eslab qolish (Login har safar shart emas)
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026_Final_PRO"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. PREMIUM VA MOSLASHUVCHAN DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { background-color: #f8fafc !important; }

    /* BURCHAKDAGI MATNLARNI YO'QOTISH (Strelka o'z joyida qoladi) */
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

    /* SIDEBAR TUGMALARI */
    div[data-testid="stSidebar"] button {
        background: white !important;
        color: #0284c7 !important;
        border: 2px solid #0ea5e9 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: 0.3s all ease;
        width: 100% !important;
    }
    div[data-testid="stSidebar"] button:hover {
        background: #0ea5e9 !important;
        color: white !important;
        transform: translateY(-2px);
    }

    /* DASHBOARD KARTALARI - PC VA MOBIL UCHUN */
    .dashboard-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        margin-top: 25px;
    }
    
    .card-box {
        background: white;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: 0.4s ease;
        flex: 1;
        min-width: 280px;
        max-width: 380px;
    }

    /* 📱 MOBIL QURILMALAR UCHUN OPTIMIZATSIYA */
    @media (max-width: 768px) {
        .card-box {
            min-width: 150px !important;
            padding: 15px !important;
            margin-bottom: 10px !important;
        }
        .card-box h1 { font-size: 26px !important; }
        .card-box h3 { font-size: 16px !important; }
        .card-box p { font-size: 12px !important; }
        h1 { font-size: 24px !important; }
    }

    .gradient-text {
        background: linear-gradient(90deg, #0284c7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Login Tablarini chiroyli qilish */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f1f5f9;
        border-radius: 10px 10px 0 0;
        padding: 0 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. BAZA VA AI ALOQASI ---
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

# --- 📂 4. FAYL TAHLILI ---
def process_doc(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.extract_raw_text(file).value
    except: return ""
    return ""

# --- 🔐 5. LOGIN, RO'YXATDAN O'TISH VA ADMIN BLOK ---
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user:
        recs = user_db.get_all_records()
        user_data = next((r for r in recs if str(r['username']) == session_user), None)
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
    st.markdown("<h1 style='text-align:center; margin-top:50px;'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.1, 1, 0.1])
    with c2:
        # Ro'yxatdan o'tish bo'limi shu yerda (Tabs orqali)
        auth_tab1, auth_tab2 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish"])
        
        with auth_tab1:
            u_in = st.text_input("Username", key="login_u")
            p_in = st.text_input("Parol", type='password', key="login_p")
            if st.button("Kirish 🚀", use_container_width=True):
                recs = user_db.get_all_records()
                hp = hashlib.sha256(p_in.encode()).hexdigest()
                user = next((r for r in recs if str(r['username']) == u_in and str(r['password']) == hp), None)
                if user:
                    if str(user.get('status')).lower() == 'blocked':
                        st.error("🚫 Sizning hisobingiz bloklangan! Admin bilan bog'laning.")
                    else:
                        st.session_state.username = u_in
                        st.session_state.logged_in = True
                        cookies["somo_user_session"] = u_in
                        cookies.save()
                        st.rerun()
                else: st.error("❌ Login yoki parol xato!")
        
        with auth_tab2:
            nu = st.text_input("Yangi Username", key="reg_u")
            np = st.text_input("Yangi Parol", type='password', key="reg_p")
            if st.button("Hisob yaratish ✨", use_container_width=True):
                if nu and np:
                    recs = user_db.get_all_records()
                    if any(r['username'] == nu for r in recs):
                        st.error("Bu username band!")
                    else:
                        hp = hashlib.sha256(np.encode()).hexdigest()
                        user_db.append_row([nu, hp, "active", str(datetime.now())])
                        st.success("✅ Muvaffaqiyatli! Endi Kirish bo'limiga o'ting.")
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS ---
if "messages" not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 10px;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #6366f1); width: 75px; height: 75px; border-radius: 50%; margin: 0 auto; line-height: 75px; font-size: 32px; color: white; font-weight: bold; border: 3px solid white;'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='margin-top: 10px;'>{st.session_state.username}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **HUJJATLAR TAHLILI**")
    f_up = st.file_uploader("Faylni tanlang", type=["pdf", "docx"], label_visibility="collapsed")
    f_txt = process_doc(f_up) if f_up else ""
    if f_up: st.success("📄 Hujjat yuklandi")

    st.markdown("<br>"*10, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish"): logout()

# DASHBOARD (MOSLASHUVCHAN)
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center;'>Salom, <span class='gradient-text'>{st.session_state.username}</span>! 👋</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div class='dashboard-container'>
            <div class='card-box'><h1>🧠</h1><h3>Aqlli Tahlil</h3><p>Murakkab mantiq va matematika</p></div>
            <div class='card-box'><h1>📄</h1><h3>Hujjatlar</h3><p>PDF va Word tahlili</p></div>
            <div class='card-box'><h1>🎨</h1><h3>Ijodkorlik</h3><p>G'oyalar va mukammal kodlar</p></div>
        </div>
    """, unsafe_allow_html=True)

# CHAT TARIXI KO'RSATISH
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# INPUT VA BAZAGA SAQLASH (TARTIB: Time, User, Role, Message)
if pr := st.chat_input("Somo AI ga xabar yuboring..."):
    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. User xabari
    st.session_state.messages.append({"role": "user", "content": pr})
    with st.chat_message("user"): st.markdown(pr)
    if chat_db:
        chat_db.append_row([time_stamp, st.session_state.username, "User", pr])

    # 2. Assistant javobi
    with st.chat_message("assistant"):
        try:
            sys_instr = f"Isming Somo AI. Yaratuvching Usmonov Sodiq. Professional javob ber. Matematikani LaTeX ($...$) da yoz."
            msgs = [{"role": "system", "content": sys_instr}]
            if f_txt: msgs.append({"role": "system", "content": f"Hujjat: {f_txt[:3500]}"})
            for old in st.session_state.messages[-12:]: msgs.append(old)
            
            res = client.chat.completions.create(
                messages=msgs,
                model="llama-3.3-70b-versatile",
                temperature=0.6
            ).choices[0].message.content
            
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            
            if chat_db:
                chat_db.append_row([time_stamp, "Somo AI", "Assistant", res])
        except Exception as e:
            st.error("Aloqa xatosi!")
