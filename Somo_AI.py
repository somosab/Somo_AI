import streamlit as st
import pandas as pd
import gspread
import hashlib
import mammoth
import pptx
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# --- 🛰 1. CONFIGURATION ---
st.set_page_config(page_title="Somo AI | Infinity", page_icon="🧠", layout="wide")

# Cookies - Foydalanuvchini eslab qolish uchun eng ishonchli usul
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. PROFESSIONAL RESPONSIVE DESIGN ---
st.markdown("""
    <style>
    /* Umumiy fon: Ko'zni charchatmaydigan Soft Slate */
    .stApp {
        background: #f8fafc !important;
    }
    
    /* SIDEBAR: Mobil va Desktopda bir xil tiniqlik */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        min-width: 250px !important;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    
    /* FAYL YUKLASH JOYI (Tuzatilgan) */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px dashed rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 5px;
    }
    [data-testid="stFileUploader"] label { color: #94a3b8 !important; }

    /* DASHBOARD KARTALARI: Telefonda 1 ta, Kompyuterda 3 ta ustun bo'ladi */
    .main-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        padding: 10px;
    }
    .dashboard-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        flex: 1 1 300px; /* Minimal 300px, agar joy qolmasa pastga tushadi */
        max-width: 350px;
        transition: 0.3s;
    }
    @media (max-width: 768px) {
        .dashboard-card {
            flex: 1 1 100%; /* Telefonda to'liq eniga yoyiladi */
            margin-bottom: 10px;
        }
        h1 { font-size: 2rem !important; }
    }
    
    .icon-box { font-size: 3rem; margin-bottom: 10px; }
    
    /* Gradient Matn */
    .gradient-text {
        background: linear-gradient(90deg, #6366f1, #d946ef);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Chat xabarlari */
    .stChatMessage {
        border-radius: 15px !important;
        border: 1px solid #e2e8f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. DATABASE & AUTH LOGIC ---
def connect_sheets():
    try:
        gcp_info = dict(st.secrets["gcp_service_account"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_info, scope)
        client = gspread.authorize(creds)
        ss = client.open("Somo_Users")
        return ss.sheet1, ss.worksheet("ChatHistory")
    except: return None, None

user_sheet, chat_sheet = connect_sheets()

# Foydalanuvchini aniqlash (Cookies orqali qayta tekshirish)
if 'username' not in st.session_state:
    saved_user = cookies.get("somo_user")
    if saved_user:
        st.session_state.username = saved_user
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

# --- 🔐 4. LOGIN INTERFACE ---
if not st.session_state.get('logged_in'):
    st.markdown("<h1 style='text-align:center;'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Kirish", "Ro'yxatdan o'tish"])
        with tab1:
            u = st.text_input("Login")
            p = st.text_input("Parol", type='password')
            if st.button("Kirish", use_container_width=True):
                recs = user_sheet.get_all_records()
                hp = hashlib.sha256(p.encode()).hexdigest()
                user = next((r for r in recs if str(r['username']) == u), None)
                if user and str(user['password']) == hp:
                    st.session_state.username = u
                    st.session_state.logged_in = True
                    cookies["somo_user"] = u
                    cookies.save()
                    st.rerun()
                else: st.error("Xato!")
        with tab2:
            nu = st.text_input("Yangi login")
            np = st.text_input("Yangi parol", type='password')
            if st.button("Yaratish", use_container_width=True):
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("Tayyor!")
    st.stop()

# --- 💬 5. MAIN APP ---
# Sidebar foydalanuvchi ma'lumotlari bilan
with st.sidebar:
    st.markdown(f"""
    <div style='text-align: center; padding: 10px;'>
        <div style='background: linear-gradient(45deg, #6366f1, #d946ef); width: 60px; height: 60px; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 24px;'>👤</div>
        <h2 style='color: white;'>{st.session_state.username}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑 Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("📁 **FAYL TAHLILI**")
    up_file = st.file_uploader("Yuklash", type=["pdf", "docx", "xlsx", "pptx"], label_visibility="collapsed")
    
    if st.button("🚪 Chiqish", use_container_width=True):
        cookies["somo_user"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()

# Dashboard (Faqat xabarlar bo'sh bo'lsa ko'rinadi)
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='color: #1e293b;'>Xush kelibsiz, <span class='gradient-text'>{st.session_state.username}</span>!</h1>
        <p style='color: #64748b;'>Bugun qanday muammoni hal qilamiz?</p>
    </div>
    <div class="main-container">
        <div class="dashboard-card">
            <div class="icon-box">🧠</div>
            <h3>Aqlli Tahlil</h3>
            <p>Matematika va murakkab muammolar yechimi.</p>
        </div>
        <div class="dashboard-card">
            <div class="icon-box">📄</div>
            <h3>Hujjatlar</h3>
            <p>Fayllarni tahlil qilish va xulosa chiqarish.</p>
        </div>
        <div class="dashboard-card">
            <div class="icon-box">🎨</div>
            <h3>Kreativlik</h3>
            <p>Yangi g'oyalar va kontent yaratish.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Chat qismi
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Xabaringizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        # Bu yerda Groq API chaqiruvi bo'ladi (oldingi koddagidek)
        # Namuna uchun:
        response = f"Sizga qanday yordam bera olaman, {st.session_state.username}?"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
