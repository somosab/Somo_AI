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

# --- 🎨 2. MUKAMMAL RESPONSIVE DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { background-color: #f8fafc !important; }

    /* SIDEBARNI TO'G'IRLASH: Yozuvlar va tugmalar muammosiz */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * { color: #f1f5f9 !important; }
    
    /* Sidebar Tugmalari */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(90deg, #4f46e5, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        transition: 0.3s !important;
    }
    div[data-testid="stSidebar"] button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
    }

    /* Fayl yuklash qismi - Dark Mode */
    [data-testid="stFileUploader"] {
        background-color: #1e293b !important;
        border: 2px dashed #4f46e5 !important;
        border-radius: 15px !important;
        padding: 15px !important;
    }
    [data-testid="stFileUploader"] section { color: white !important; }

    /* DASHBOARD KARTALARI: Telefonda 1 ta, Kompyuterda 3 ta */
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
    .card:hover { transform: translateY(-10px); }
    .card-icon { font-size: 4rem; margin-bottom: 15px; }
    
    @media (max-width: 768px) {
        .card { flex: 1 1 100%; margin: 0 10px; }
        .stChatMessage { width: 95% !important; }
    }

    /* Gradient Matnlar */
    .text-gradient {
        background: linear-gradient(90deg, #4f46e5, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. DATABASE & SERVICES ---
def init_groq():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def connect_db():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        ss = client.open("Somo_Users")
        return ss.sheet1, ss.worksheet("ChatHistory")
    except Exception as e:
        return None, None

user_db, chat_db = connect_db()
client = init_groq()

# --- 📂 4. FAYL TAHLILI FUNKSIYALARI ---
def extract_text(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        return " ".join([page.extract_text() for page in reader.pages])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        result = mammoth.convert_to_markdown(file)
        return result.value
    elif file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        prs = pptx.Presentation(file)
        return " ".join([shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text")])
    return ""

# --- 🔐 5. AUTHENTICATION (COOKIES BILAN) ---
if 'logged_in' not in st.session_state:
    saved_user = cookies.get("somo_user_session")
    if saved_user:
        st.session_state.username = saved_user
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>🌌 Somo AI <span class='text-gradient'>Infinity</span></h1>", unsafe_allow_html=True)
        auth_tab1, auth_tab2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
        
        with auth_tab1:
            u = st.text_input("Login", key="l_u")
            p = st.text_input("Parol", type='password', key="l_p")
            if st.button("Tizimga kirish", use_container_width=True):
                recs = user_db.get_all_records()
                hp = hashlib.sha256(p.encode()).hexdigest()
                user = next((r for r in recs if str(r['username']) == u), None)
                if user and str(user['password']) == hp:
                    st.session_state.username = u
                    st.session_state.logged_in = True
                    cookies["somo_user_session"] = u
                    cookies.save()
                    st.rerun()
                else: st.error("Login yoki parol xato!")
        
        with auth_tab2:
            nu = st.text_input("Yangi Login", key="r_u")
            np = st.text_input("Yangi Parol", type='password', key="r_p")
            if st.button("Hisob yaratish", use_container_width=True):
                user_db.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active", str(datetime.now())])
                st.success("Muvaffaqiyatli! Endi kirish bo'limiga o'ting.")
    st.stop()

# --- 🚀 6. MAIN APPLICATION INTERFACE ---

# Sidebar
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <div style='background: linear-gradient(45deg, #4f46e5, #ec4899); width: 80px; height: 80px; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 35px;'>👤</div>
            <h2 style='margin-top:10px;'>{st.session_state.username}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑 Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("📁 **FAYL TAHLILI**")
    uploaded_file = st.file_uploader("Fayl yuklang", type=["pdf", "docx", "pptx"], label_visibility="collapsed")
    
    file_content = ""
    if uploaded_file:
        file_content = extract_text(uploaded_file)
        st.success("Fayl o'qildi!")

    st.markdown("<br>"*10, unsafe_allow_html=True)
    if st.button("🚪 Chiqish", use_container_width=True):
        cookies["somo_user_session"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()

# Dashboard logic
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(f"""
        <div style='text-align: center;'>
            <h1 style='font-size: 3rem;'>Xush kelibsiz, <span class='text-gradient'>{st.session_state.username}</span>!</h1>
            <p style='color: #64748b; font-size: 1.2rem;'>Infinity versiyasi bilan barcha chegaralarni yengib o'ting.</p>
        </div>
        <div class="dashboard-container">
            <div class="card"><div class="card-icon">🧠</div><h3>Aqlli Tahlil</h3><p>Murakkab muammolar va fanlar bo'yicha eng aniq yechimlar.</p></div>
            <div class="card"><div class="card-icon">📄</div><h3>Hujjatlar</h3><p>Yuklangan fayllarni soniyalar ichida tushunish va savol berish.</p></div>
            <div class="card"><div class="card-icon">🎨</div><h3>Kreativlik</h3><p>Bloglar, insholar va biznes rejalar uchun g'oyalar manbai.</p></div>
        </div>
    """, unsafe_allow_html=True)

# Chat History Display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Savolingizni yoki topshirig'ingizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Fayl mazmuni bo'lsa, uni promptga qo'shish
        context = f"\n\n[Fayl mazmuni]: {file_content[:2000]}" if file_content else ""
        
        full_prompt = f"Foydalanuvchi: {st.session_state.username}. {context}\nSavol: {prompt}"
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": full_prompt}],
                model="llama-3.3-70b-versatile",
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Google Sheetsga yozish (Log uchun)
            if chat_db:
                chat_db.append_row([st.session_state.username, prompt, response[:500], str(datetime.now())])
        except Exception as e:
            st.error(f"Xatolik: {str(e)}")
