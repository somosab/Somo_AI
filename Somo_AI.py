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
import json

# --- 🛰 1. SISTEMA SOZLAMALARI ---
st.set_page_config(
    page_title="Somo AI | Universal Infinity", 
    page_icon="🌌", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cookies - Sessiyani eslab qolish uchun
cookies = EncryptedCookieManager(
    password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026_Final_PRO")
)
if not cookies.ready():
    st.stop()

# --- 🎨 2. PREMIUM DIZAYN (CSS) ---
st.markdown("""
    <style>
    .stApp { background: #f8fafc !important; }

    /* SIDEBAR VA BURCHAKDAGI XATOLIKLARNI TOZALASH */
    [data-testid="stSidebarNav"] { display: none !important; }
    .st-emotion-cache-1vt458p, .st-emotion-cache-k77z8z, .st-emotion-cache-12fmjuu { 
        font-size: 0px !important; 
        color: transparent !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e0f2fe 0%, #bae6fd 100%) !important;
        border-right: 3px solid #7dd3fc;
    }

    /* DASHBOARD KARTALARI */
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
        flex: 1;
        min-width: 250px;
        max-width: 350px;
    }

    /* MOBIL MOSLASHUVCHANLIK */
    @media (max-width: 768px) {
        .card-box { min-width: 140px !important; padding: 15px !important; }
        .card-box h1 { font-size: 24px !important; }
        .card-box h3 { font-size: 15px !important; }
    }

    .gradient-text {
        background: linear-gradient(90deg, #0284c7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
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

# --- 🔐 5. LOGIN VA SESSYA BOSHQARUVI ---
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user and user_db:
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

# --- 🔒 LOGIN / REGISTER OYNASI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; margin-top:50px;'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.2, 1, 0.2])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish"])
        
        with auth_tab1:
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Parol", type='password')
                if st.form_submit_button("Kirish 🚀", use_container_width=True):
                    recs = user_db.get_all_records()
                    hp = hashlib.sha256(p.encode()).hexdigest()
                    user = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
                    if user:
                        if str(user.get('status')).lower() == 'blocked':
                            st.error("🚫 Bloklangansiz!")
                        else:
                            st.session_state.username = u
                            st.session_state.logged_in = True
                            cookies["somo_user_session"] = u
                            cookies.save()
                            st.rerun()
                    else: st.error("❌ Xato!")
        
        with auth_tab2:
            with st.form("reg_form"):
                nu = st.text_input("Yangi Username")
                np = st.text_input("Yangi Parol", type='password')
                if st.form_submit_button("Ro'yxatdan o'tish ✨", use_container_width=True):
                    recs = user_db.get_all_records()
                    if any(r['username'] == nu for r in recs):
                        st.error("Username band!")
                    else:
                        hp = hashlib.sha256(np.encode()).hexdigest()
                        user_db.append_row([nu, hp, "active", str(datetime.now())])
                        st.success("✅ Tayyor! Kirish bo'limiga o'ting.")
    st.stop()

# --- 🚀 6. ASOSIY CHAT INTERFEYSI ---
if "messages" not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    if st.button("🗑 Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("📂 **HUJJAT TAHLILI**")
    f_up = st.file_uploader("Fayl", type=["pdf", "docx"], label_visibility="collapsed")
    f_txt = process_doc(f_up) if f_up else ""
    
    st.markdown("<br>"*10, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish", use_container_width=True):
        logout()

# DASHBOARD
if not st.session_state.messages:
    st.markdown(f"<h2 style='text-align: center;'>Xush kelibsiz, <span class='gradient-text'>{st.session_state.username}</span>!</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div class='dashboard-container'>
            <div class='card-box'><h1>🧠</h1><h3>Tahlil</h3><p>Mantiqiy savollar</p></div>
            <div class='card-box'><h1>📄</h1><h3>Hujjat</h3><p>Fayllarni o'qish</p></div>
            <div class='card-box'><h1>🎨</h1><h3>Ijod</h3><p>Yangi g'oyalar</p></div>
        </div>
    """, unsafe_allow_html=True)

# CHAT TARIXI KO'RSATISH
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# INPUT VA BAZAGA SAQLASH (Time | User | Role | Message)
if pr := st.chat_input("Xabar yozing..."):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # User xabari
    st.session_state.messages.append({"role": "user", "content": pr})
    with st.chat_message("user"): st.markdown(pr)
    if chat_db:
        chat_db.append_row([time_now, st.session_state.username, "User", pr])

    # Assistant javobi
    with st.chat_message("assistant"):
        try:
            msgs = [{"role": "system", "content": "Sening isming Somo AI. Yaratuvching Usmonov Sodiq."}]
            if f_txt: msgs.append({"role": "system", "content": f"Hujjat: {f_txt[:3000]}"})
            for old in st.session_state.messages[-10:]: msgs.append(old)
            
            res = client.chat.completions.create(
                messages=msgs,
                model="llama-3.3-70b-versatile",
                temperature=0.6
            ).choices[0].message.content
            
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            if chat_db:
                chat_db.append_row([time_now, "Somo AI", "Assistant", res])
        except:
            st.error("Aloqa xatosi!")
