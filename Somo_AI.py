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
st.set_page_config(page_title="Somo AI | Infinity", page_icon="🧠", layout="wide")

# Cookies - Foydalanuvchini eslab qolish
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. MUKAMMAL CSS (SIDEBARNI QORA VA CHIROYLI QILISH) ---
st.markdown("""
    <style>
    /* 1. Asosiy fon oqish/yorqin */
    .stApp { background-color: #ffffff !important; }

    /* 2. SIDEBARNI TO'LIQ QORA QILISH */
    [data-testid="stSidebar"] {
        background-color: #0a0f1e !important; /* Chuqur qora-ko'k */
        border-right: 1px solid #1e293b;
    }

    /* Sidebar ichidagi barcha matnlarni OQ qilish */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }

    /* 3. TUGMALARNI QAYTA DIZAYN QILISH (Binafsha Gradient) */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        transition: all 0.3s ease !important;
        margin-top: 10px !important;
    }
    
    div[data-testid="stSidebar"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(168, 85, 247, 0.5) !important;
        filter: brightness(1.1);
    }

    /* 4. FAYL YUKLASH MAYDONI (Qora bo'limda ko'rinadigan qilish) */
    [data-testid="stFileUploader"] {
        background-color: #161e2d !important;
        border: 2px dashed #4f46e5 !important;
        border-radius: 14px !important;
        padding: 10px !important;
    }
    [data-testid="stFileUploader"] section {
        background-color: transparent !important;
        color: white !important;
    }
    [data-testid="stFileUploader"] div[role="button"] {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid #4f46e5 !important;
    }

    /* 5. ASOSIY SAHIFA DASHBOARD KARTALARI */
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 25px;
        justify-content: center;
        margin-top: 40px;
    }
    .modern-card {
        background: white;
        border-radius: 24px;
        padding: 35px;
        width: 320px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
        transition: 0.4s;
    }
    .modern-card:hover {
        transform: translateY(-12px);
        border-color: #6366f1;
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.1);
    }
    
    .text-gradient {
        background: linear-gradient(90deg, #4f46e5, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. CORE SERVICES (GROQ & GSHEETS) ---
def connect_services():
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        return client, ss.sheet1, ss.worksheet("ChatHistory")
    except: return client, None, None

client, user_db, chat_db = connect_services()

# --- 📂 4. FAYL TAHLILI ---
def parse_uploaded_file(file):
    try:
        if file.type == "application/pdf":
            return " ".join([p.extract_text() for p in PdfReader(file).pages])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.convert_to_markdown(file).value
        elif file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            prs = pptx.Presentation(file)
            return " ".join([s.text for sl in prs.slides for s in sl.shapes if hasattr(s, "text")])
    except: return ""
    return ""

# --- 🔐 5. LOGIN/REGISTRATION LOGIC ---
if 'logged_in' not in st.session_state:
    session = cookies.get("somo_infinity_auth")
    if session:
        st.session_state.username = session
        st.session_state.logged_in = True
    else: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🌌 Somo AI <span class='text-gradient'>Infinity</span></h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
        with t1:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Parol", type='password', key="l_p")
            if st.button("Tizimga kirish 🚀", use_container_width=True):
                data = user_db.get_all_records()
                hp = hashlib.sha256(p.encode()).hexdigest()
                user = next((r for r in data if str(r['username']) == u and str(r['password']) == hp), None)
                if user:
                    st.session_state.username = u
                    st.session_state.logged_in = True
                    cookies["somo_infinity_auth"] = u
                    cookies.save()
                    st.rerun()
                else: st.error("Xatolik: Login yoki parol noto'g'ri!")
        with t2:
            nu = st.text_input("Yangi Username", key="r_u")
            np = st.text_input("Yangi Parol", type='password', key="r_p")
            if st.button("Hisob yaratish ✨", use_container_width=True):
                if nu and np:
                    h_np = hashlib.sha256(np.encode()).hexdigest()
                    user_db.append_row([nu, h_np, "active", str(datetime.now())])
                    st.success("Hisob yaratildi! Endi 'Kirish' bo'limiga o'ting.")
    st.stop()

# --- 🚀 6. MAIN APP INTERFACE ---
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 25px;'>
            <div style='background: linear-gradient(45deg, #4f46e5, #ec4899); width: 75px; height: 75px; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 32px; color: white; font-weight: bold; border: 3px solid #1e293b;'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='margin-top:12px; font-size: 20px;'>{st.session_state.username}</h3>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **FAYL TAHLILI (PDF/DOCX)**")
    f_up = st.file_uploader("Faylni tanlang", type=["pdf", "docx", "pptx"], label_visibility="collapsed")
    f_content = parse_uploaded_file(f_up) if f_up else ""
    if f_up: st.success("Fayl muvaffaqiyatli yuklandi!")

    st.markdown("<br>"*10, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish"):
        cookies["somo_infinity_auth"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()

# Dashboard Content
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <h1 style='font-size: 3.5rem;'>Xush kelibsiz, <span class='text-gradient'>{st.session_state.username}</span>!</h1>
            <p style='color: #64748b; font-size: 1.3rem;'>Bugun qanday muammoni hal qilamiz?</p>
        </div>
        <div class="card-container">
            <div class="modern-card"><h2>🧠</h2><h3>Aqlli Tahlil</h3><p>Murakkab fanlar va kodlar bo'yicha aniq yechimlar.</p></div>
            <div class="modern-card"><h2>📄</h2><h3>Hujjatlar</h3><p>Fayllarni o'qish, tahlil qilish va xulosa chiqarish.</p></div>
            <div class="modern-card"><h2>🎨</h2><h3>Kreativlik</h3><p>Insholar, bloglar va biznes g'oyalar yaratish.</p></div>
        </div>
    """, unsafe_allow_html=True)

# Chat Log
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Savolingizni yoki topshiringizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        context = f"\n\n[Fayl]: {f_content[:3000]}" if f_content else ""
        try:
            res = client.chat.completions.create(
                messages=[{"role": "user", "content": f"{prompt} {context}"}],
                model="llama-3.3-70b-versatile",
            ).choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            if chat_db: chat_db.append_row([st.session_state.username, prompt, res[:500], str(datetime.now())])
        except: st.error("AI tizimida uzilish bo'ldi. Qayta urinib ko'ring.")
