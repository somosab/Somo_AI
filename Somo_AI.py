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

# Cookies - Foydalanuvchini eslab qolish (Refresh bo'lganda chiqib ketmaslik uchun)
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. MUKAMMAL CSS (SIDEBAR VA LOGINNI TO'G'IRLASH) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { background-color: #f8fafc !important; }

    /* SIDEBARNI TO'LIQ BOSHQARISH */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important; 
        min-width: 300px !important;
    }

    /* Sidebar ichidagi barcha oq dog'larni yo'qotish (Majburiy rang berish) */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    /* TUGMALAR: Oq bo'lib qolgan tugmalarni binafsha qilish */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-weight: 700 !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        margin-top: 10px !important;
    }
    div[data-testid="stSidebar"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4) !important;
    }

    /* FAYL YUKLASH (Drag and Drop) maydonini to'g'irlash */
    [data-testid="stFileUploader"] {
        background-color: #1e293b !important;
        border: 2px dashed #6366f1 !important;
        border-radius: 15px !important;
        padding: 15px !important;
    }
    [data-testid="stFileUploader"] section { color: white !important; }
    [data-testid="stFileUploader"] button { 
        background-color: #334155 !important; 
        color: white !important;
        border: 1px solid #6366f1 !important;
    }

    /* DASHBOARD KARTALARI */
    .dashboard-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        margin-top: 30px;
    }
    .card {
        background: white;
        border-radius: 25px;
        padding: 30px;
        flex: 1 1 300px;
        max-width: 380px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: 0.4s ease;
    }
    .card:hover { transform: translateY(-10px); border-color: #6366f1; }
    
    .text-gradient {
        background: linear-gradient(90deg, #4f46e5, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. CORE SERVICES (GROQ & DATABASE) ---
def init_services():
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        return client, ss.sheet1, ss.worksheet("ChatHistory")
    except:
        return client, None, None

client, user_db, chat_db = init_services()

# --- 📂 4. FAYL TAHLILI FUNKSIYASI ---
def get_file_content(file):
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

# --- 🔐 5. LOGIN VA REGISTRATSIYA BO'LIMI (TO'LIQ) ---
if 'logged_in' not in st.session_state:
    saved_user = cookies.get("somo_session_v2")
    if saved_user:
        st.session_state.username = saved_user
        st.session_state.logged_in = True
    else: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🌌 Somo AI <span class='text-gradient'>Infinity</span></h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.8, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Kirish", "✍️ Ro'yxatdan o'tish"])
        
        with tab1:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Parol", type='password', key="login_p")
            if st.button("Tizimga kirish", use_container_width=True):
                users = user_db.get_all_records()
                hashed_p = hashlib.sha256(p.encode()).hexdigest()
                found = next((r for r in users if str(r['username']) == u and str(r['password']) == hashed_p), None)
                if found:
                    st.session_state.username = u
                    st.session_state.logged_in = True
                    cookies["somo_session_v2"] = u
                    cookies.save()
                    st.rerun()
                else: st.error("Login yoki parol noto'g'ri!")
        
        with tab2:
            nu = st.text_input("Yangi Username", key="reg_u")
            np = st.text_input("Yangi Parol", type='password', key="reg_p")
            cp = st.text_input("Parolni tasdiqlang", type='password', key="reg_cp")
            if st.button("Hisob yaratish", use_container_width=True):
                if np == cp and nu:
                    hashed_np = hashlib.sha256(np.encode()).hexdigest()
                    user_db.append_row([nu, hashed_np, "active", str(datetime.now())])
                    st.success("Muvaffaqiyatli! Endi Kirish bo'limiga o'ting.")
                else: st.warning("Ma'lumotlar xato yoki bo'sh!")
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS (MUKAMMAL SIDEBAR BILAN) ---
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <div style='background: linear-gradient(45deg, #6366f1, #a855f7); width: 80px; height: 80px; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 35px; color: white;'>
                {st.session_state.username[0].upper()}
            </div>
            <h2 style='margin-top:15px; color: white !important;'>{st.session_state.username}</h2>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **FAYL TAHLILI (PDF/DOCX)**")
    uploaded_file = st.file_uploader("Faylni shu yerga tashlang", type=["pdf", "docx", "pptx"], label_visibility="collapsed")
    
    file_text = ""
    if uploaded_file:
        file_text = get_file_content(uploaded_file)
        st.success("Fayl o'qildi ✅")

    st.markdown("<br>"*10, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish"):
        cookies["somo_session_v2"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()

# --- 💬 7. CHAT LOGIKASI ---
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(f"""
        <div style='text-align: center;'>
            <h1 style='font-size: 3.5rem;'>Xush kelibsiz, <span class='text-gradient'>{st.session_state.username}</span>!</h1>
            <p style='color: #64748b; font-size: 1.2rem;'>Infinity versiyasi bilan barcha chegaralarni yengib o'ting.</p>
        </div>
        <div class="dashboard-container">
            <div class="card"><h3>🧠 Aqlli Tahlil</h3><p>Murakkab muammolar va fanlar bo'yicha eng aniq yechimlar.</p></div>
            <div class="card"><h3>📄 Hujjatlar</h3><p>Yuklangan fayllarni soniyalar ichida tushunish va tahlil qilish.</p></div>
            <div class="card"><h3>🎨 Kreativlik</h3><p>Bloglar, insholar va yangi g'oyalar uchun mukammal manba.</p></div>
        </div>
    """, unsafe_allow_html=True)

# Chat ko'rinishi
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Savolingizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        context = f"\n\n[Fayl mazmuni]: {file_text[:3000]}" if file_text else ""
        full_query = f"Foydalanuvchi: {st.session_state.username}. {context}\nSavol: {prompt}"
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": full_query}],
                model="llama-3.3-70b-versatile",
            ).choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            if chat_db: chat_db.append_row([st.session_state.username, prompt, response[:500], str(datetime.now())])
        except: st.error("AI bilan bog'lanishda xatolik yuz berdi.")
