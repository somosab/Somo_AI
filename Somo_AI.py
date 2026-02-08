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

# Cookies - Foydalanuvchini eslab qolish uchun (Telefon uchun muhim)
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. MUKAMMAL RESPONSIVE DIZAYN (SIDEBAR MUAMMOSI TUZATILDI) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { background-color: #f8fafc !important; }

    /* 1. SIDEBARNI TO'LIQ BOSHQARISH (MUHIM!) */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important; /* To'q ko'k/qora fon */
        border-right: 1px solid #1e293b;
    }
    
    /* Sidebar ichidagi barcha matnlarni majburiy oq qilish */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #f1f5f9 !important;
    }

    /* Sidebar Tugmalari (Chatni tozalash, Chiqish) - Oq dog'larni yo'qotish */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(90deg, #4f46e5, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        width: 100% !important;
        display: block !important;
    }
    div[data-testid="stSidebar"] button:hover {
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.6) !important;
        transform: translateY(-2px);
    }

    /* Fayl yuklash maydonini to'g'irlash (Dark Mode) */
    [data-testid="stFileUploader"] {
        background-color: #1e293b !important;
        border: 2px dashed #4f46e5 !important;
        border-radius: 15px !important;
        padding: 10px !important;
    }
    [data-testid="stFileUploader"] section { color: white !important; }
    [data-testid="stFileUploader"] button { 
        background-color: #334155 !important; 
        color: white !important;
        border: 1px solid #4f46e5 !important;
    }

    /* 2. DASHBOARD KARTALARI (RESPONSIVE) */
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
        padding: 35px;
        flex: 1 1 300px;
        max-width: 380px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: 0.4s ease;
    }
    .card:hover { transform: translateY(-10px); border-color: #6366f1; }
    .card-icon { font-size: 4rem; margin-bottom: 20px; }
    
    @media (max-width: 768px) {
        .card { flex: 1 1 100%; margin: 10px; }
        .stChatMessage { width: 95% !important; }
        h1 { font-size: 2rem !important; }
    }

    /* Chat matni uchun gradient */
    .text-gradient {
        background: linear-gradient(90deg, #4f46e5, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. CORE SERVICES (GROQ & DB) ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def connect_db():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        return ss.sheet1, ss.worksheet("ChatHistory")
    except: return None, None

user_db, chat_db = connect_db()

# --- 📂 4. FAYL TAHLILI FUNKSIYASI ---
def get_file_text(file):
    try:
        if file.type == "application/pdf":
            return " ".join([p.extract_text() for p in PdfReader(file).pages])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.convert_to_markdown(file).value
        elif file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            prs = pptx.Presentation(file)
            return " ".join([s.text for sl in prs.slides for s in sl.shapes if hasattr(s, "text")])
    except: return "Faylni o'qishda xatolik."
    return ""

# --- 🔐 5. AUTH LOGIC (COOKIES BILAN) ---
if 'logged_in' not in st.session_state:
    saved_user = cookies.get("somo_user_session")
    if saved_user:
        st.session_state.username = saved_user
        st.session_state.logged_in = True
    else: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🌌 Somo AI <span class='text-gradient'>Infinity</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        tab1, tab2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
        with tab1:
            u = st.text_input("Login")
            p = st.text_input("Parol", type='password')
            if st.button("Kirish", use_container_width=True):
                recs = user_db.get_all_records()
                hp = hashlib.sha256(p.encode()).hexdigest()
                user = next((r for r in recs if str(r['username']) == u), None)
                if user and str(user['password']) == hp:
                    st.session_state.username = u
                    st.session_state.logged_in = True
                    cookies["somo_user_session"] = u
                    cookies.save()
                    st.rerun()
                else: st.error("Xato!")
    st.stop()

# --- 🚀 6. MAIN INTERFACE ---
# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("📂 **FAYL TAHLILI**")
    f = st.file_uploader("Fayl", type=["pdf", "docx", "pptx"], label_visibility="collapsed")
    f_txt = get_file_text(f) if f else ""
    if f: st.success("Fayl yuklandi!")

    st.markdown("<br>"*12, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish"):
        cookies["somo_user_session"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()

# Dashboard
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(f"""
        <div style='text-align: center;'>
            <h1 style='font-size: 3rem;'>Xush kelibsiz, <span class='text-gradient'>{st.session_state.username}</span>!</h1>
            <p style='color: #64748b; font-size: 1.2rem;'>Infinity versiyasi: barcha funksiyalar bitta joyda.</p>
        </div>
        <div class="dashboard-container">
            <div class="card"><div class="card-icon">🧠</div><h3>Aqlli Tahlil</h3><p>Murakkab muammolar uchun aniq yechimlar.</p></div>
            <div class="card"><div class="card-icon">📄</div><h3>Hujjatlar</h3><p>Fayllarni o'qish va tahlil qilish.</p></div>
            <div class="card"><div class="card-icon">🎨</div><h3>Kreativlik</h3><p>Yangi g'oyalar va kontent yaratish.</p></div>
        </div>
    """, unsafe_allow_html=True)

# Chat Display & Input
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Savolingizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        ctx = f"\n\n[Fayl]: {f_txt[:2500]}" if f_txt else ""
        try:
            res = client.chat.completions.create(
                messages=[{"role": "user", "content": f"{prompt} {ctx}"}],
                model="llama-3.3-70b-versatile",
            ).choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            if chat_db: chat_db.append_row([st.session_state.username, prompt, res[:500], str(datetime.now())])
        except Exception as e: st.error("API xatolik berdi.")
