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

# --- 🛰 1. SISTEMA SOZLAMALARI ---
st.set_page_config(page_title="Somo AI | Infinity", page_icon="🌌", layout="wide")

# Cookies - Foydalanuvchini eslab qolish uchun
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. MUKAMMAL CSS (Hamma xatolar shu yerda tuzatildi) ---
st.markdown("""
    <style>
    /* 1. Umumiy Fon */
    .stApp { background-color: #f8fafc !important; }

    /* 2. SIDEBARNI TO'LIQ "REANIMATSIYA" QILISH */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important; /* To'q ko'k qora fon */
        min-width: 300px !important;
    }

    /* Sidebar ichidagi har qanday yozuvni oq qilish */
    [data-testid="stSidebar"] section, 
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* 3. SIDEBAR TUGMALARI (Oq bo'lib qolgan tugmalarni to'g'irlash) */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        width: 100% !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 10px !important;
        text-transform: none !important;
    }
    div[data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4) !important;
        transform: translateY(-2px) !important;
    }

    /* 4. FAYL YUKLASH MAYDONI (Oq dog'ni yo'qotish) */
    [data-testid="stFileUploader"] {
        background-color: #1e293b !important; /* To'qroq kulrang/ko'k */
        border: 2px dashed #4f46e5 !important;
        border-radius: 15px !important;
        padding: 10px !important;
        color: white !important;
    }
    [data-testid="stFileUploader"] section {
        background-color: transparent !important;
        color: white !important;
    }
    /* "Browse files" tugmasini ichida to'g'irlash */
    [data-testid="stFileUploader"] button {
        background-color: #334155 !important;
        color: #f1f5f9 !important;
        border: 1px solid #475569 !important;
        width: auto !important;
    }

    /* 5. ASOSIY SAHIFA DASHBOARD KARTALARI */
    .dashboard-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        margin-top: 40px;
    }
    .feature-card {
        background: white;
        border-radius: 24px;
        padding: 30px;
        flex: 1 1 320px;
        max-width: 400px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px -10px rgba(79, 70, 229, 0.15);
        border-color: #6366f1;
    }
    .card-icon { font-size: 3.5rem; margin-bottom: 20px; display: block; }
    
    @media (max-width: 768px) {
        .feature-card { flex: 1 1 100%; margin: 10px; }
        h1 { font-size: 2.2rem !important; }
    }

    /* Matnlar uchun gradient */
    .text-gradient {
        background: linear-gradient(90deg, #4f46e5, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. DATABASE & CONNECTIVITY ---
def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def connect_to_gsheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        return ss.sheet1, ss.worksheet("ChatHistory")
    except: return None, None

user_db, chat_db = connect_to_gsheets()
client = get_groq_client()

# --- 📂 4. FAYL O'QISH (Kengaytirilgan) ---
def parse_file(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            return " ".join([p.extract_text() for p in PdfReader(uploaded_file).pages])
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.convert_to_markdown(uploaded_file).value
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            prs = pptx.Presentation(uploaded_file)
            return " ".join([sh.text for sl in prs.slides for sh in sl.shapes if hasattr(sh, "text")])
    except: return "Faylni tahlil qilib bo'lmadi."
    return ""

# --- 🔐 5. AUTHENTICATION (Cookies bilan mukammallashtirilgan) ---
if 'logged_in' not in st.session_state:
    user_session = cookies.get("somo_user_session")
    if user_session:
        st.session_state.username = user_session
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🌌 Somo AI <span class='text-gradient'>Infinity</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.8, 1])
    with c2:
        auth_tab1, auth_tab2 = st.tabs(["🔑 Tizimga kirish", "📝 Ro'yxatdan o'tish"])
        with auth_tab1:
            u_login = st.text_input("Login", key="main_u")
            p_login = st.text_input("Parol", type='password', key="main_p")
            if st.button("Kirish 🚀", use_container_width=True):
                data = user_db.get_all_records()
                hashed_pw = hashlib.sha256(p_login.encode()).hexdigest()
                user_found = next((r for r in data if str(r['username']) == u_login and str(r['password']) == hashed_pw), None)
                if user_found:
                    st.session_state.username = u_login
                    st.session_state.logged_in = True
                    cookies["somo_user_session"] = u_login
                    cookies.save()
                    st.rerun()
                else: st.error("Login yoki parol noto'g'ri!")
        with auth_tab2:
            st.info("Yangi hisob yaratish uchun ma'lumotlarni kiriting.")
            # ... (Ro'yxatdan o'tish logikasi shu yerda)
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS ---

# Sidebar dizayni
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 20px;'>
            <div style='background: linear-gradient(45deg, #4f46e5, #ec4899); width: 70px; height: 70px; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 30px; color: white; font-weight: bold;'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='margin-top: 10px;'>{st.session_state.username}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Tugma endi binafsha gradientda, yaqqol ko'rinadi
    if st.button("🗑 Chatni tozalash", key="clear_btn"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<hr style='border-color: #1e293b;'>", unsafe_allow_html=True)
    st.markdown("📂 **FAYL TAHLILI (PDF/DOCX)**")
    
    # Fayl yuklash qismi endi to'q ko'k fonda, oq yozuvda
    file_up = st.file_uploader("Yuklash", type=["pdf", "docx", "pptx"], label_visibility="collapsed")
    context_text = parse_file(file_up) if file_up else ""
    if file_up: st.success("Fayl tayyor!")

    st.markdown("<br>"*8, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish", key="logout_btn"):
        cookies["somo_user_session"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()

# Dashboard
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <h1 style='font-size: 3.5rem;'>Xush kelibsiz, <span class='text-gradient'>{st.session_state.username}</span>!</h1>
            <p style='color: #64748b; font-size: 1.3rem; max-width: 700px; margin: 0 auto;'>Somo AI Infinity — ilm va ijod chegaralarini kengaytirish uchun sizning shaxsiy yordamchingiz.</p>
        </div>
        <div class="dashboard-grid">
            <div class="feature-card">
                <span class="card-icon">🧠</span>
                <h3 style="color: #1e293b;">Aqlli Tahlil</h3>
                <p style="color: #64748b;">Matematika, fizika va dasturlash bo'yicha murakkab savollarga aniq yechimlar.</p>
            </div>
            <div class="feature-card">
                <span class="card-icon">📄</span>
                <h3 style="color: #1e293b;">Hujjatlar</h3>
                <p style="color: #64748b;">Katta hajmli fayllarni o'qish, tahlil qilish va qisqacha mazmunini chiqarish.</p>
            </div>
            <div class="feature-card">
                <span class="card-icon">🎨</span>
                <h3 style="color: #1e293b;">Kreativlik</h3>
                <p style="color: #64748b;">Insholar, ssenariylar va biznes rejalar yaratishda ilhom manbai.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Chat Logika
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Savol yoki topshiriqni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        full_p = f"Foydalanuvchi: {st.session_state.username}\n{f'[Fayl tahlili]: {context_text[:3000]}' if context_text else ''}\nSavol: {prompt}"
        try:
            resp = client.chat.completions.create(
                messages=[{"role": "user", "content": full_p}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
            ).choices[0].message.content
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})
            if chat_db: chat_db.append_row([st.session_state.username, prompt, resp[:500], str(datetime.now())])
        except Exception as e: st.error("Tizimda kichik xatolik (API). Qayta urinib ko'ring.")
