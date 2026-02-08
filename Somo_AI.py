import streamlit as st
import pandas as pd
import gspread
import hashlib
import mammoth
import time
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# --- 🛰 1. SISTEMA VA COOKIE SOZLAMALARI ---
st.set_page_config(page_title="Somo AI | Universal Infinity", page_icon="🌌", layout="wide")

# Cookies - Sessiyani 30 kungacha eslab qolish uchun
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Super_Secret_Key_2026_Secure"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. PROFESSIONAL VA MOSLASHUVCHAN DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon va font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc !important; }

    /* BURCHAKDAGI "keyboard_double" VA BOSHQA XATOLARNI YO'QOTISH */
    [data-testid="stSidebarNav"], .st-emotion-cache-k77z8z, .st-emotion-cache-1vt458p, .st-emotion-cache-h5rgv8 { 
        display: none !important; 
    }
    
    /* SIDEBAR - MUKAMMAL OCHIQ KO'K */
    [data-testid="stSidebar"] {
        background-color: #e0f2fe !important;
        border-right: 1px solid #bae6fd;
    }
    [data-testid="stSidebar"] section, [data-testid="stSidebar"] .stVerticalBlock {
        background-color: #e0f2fe !important;
    }
    
    /* SIDEBAR MATNLARI */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #0369a1 !important;
        font-weight: 600 !important;
    }

    /* PREMIUM TUGMALAR */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-weight: 700 !important;
        transition: 0.3s all cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        box-shadow: 0 4px 6px -1px rgba(14, 165, 233, 0.2) !important;
    }
    div[data-testid="stSidebar"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(14, 165, 233, 0.4) !important;
    }

    /* ASOSIY SAHIFA KARTALARI - RESPONSIVE */
    .dashboard-card {
        background: white;
        border-radius: 24px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        border: 1px solid #f1f5f9;
        transition: 0.4s ease;
        height: 100%;
    }
    .dashboard-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(14, 165, 233, 0.08);
        border-color: #0ea5e9;
    }
    
    .gradient-title {
        background: linear-gradient(90deg, #0284c7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
    }

    /* 📱 MOBIL QURILMALAR UCHUN MAXSUS O'LCHAMLAR */
    @media (max-width: 768px) {
        .gradient-title { font-size: 1.8rem !important; }
        .dashboard-card { 
            padding: 15px !important; 
            margin-bottom: 10px !important; 
        }
        .dashboard-card h1 { font-size: 28px !important; }
        .dashboard-card h3 { font-size: 16px !important; }
        .dashboard-card p { font-size: 12px !important; }
        
        /* Chat inputini mobilga moslash */
        .stChatInputContainer { padding: 10px !important; }
    }

    /* Fayl yuklash maydoni */
    [data-testid="stFileUploader"] {
        background-color: #f0f9ff !important;
        border: 2px dashed #0ea5e9 !important;
        border-radius: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. SERVISLAR VA BAZA BILAN BOG'LANISH ---
@st.cache_resource
def connect_db():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        return ss.sheet1, ss.worksheet("ChatHistory")
    except Exception as e:
        st.error(f"Ma'lumotlar bazasi bilan ulanishda xatolik: {e}")
        return None, None

user_db, chat_db = connect_db()
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 📂 4. FAYLLARNI QAYTA ISHLASH ---
def extract_file_content(file):
    if not file: return ""
    try:
        if file.type == "application/pdf":
            pdf = PdfReader(file)
            return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.extract_raw_text(file).value
    except: return "Faylni o'qishda xatolik yuz berdi."
    return ""

# --- 🔐 5. LOGIN VA STATUSNI TEKSHIRISH ---
if 'logged_in' not in st.session_state:
    saved_user = cookies.get("somo_user_session")
    if saved_user:
        st.session_state.username = saved_user
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

# Foydalanuvchi statusini tekshirish (Bloklash mantiqi)
def check_user_status(username):
    if user_db:
        recs = user_db.get_all_records()
        user = next((r for r in recs if str(r['username']) == username), None)
        if user and str(user.get('status', '')).lower() == 'blocked':
            return False
    return True

# Tizimdan chiqish
def logout_user():
    cookies["somo_user_session"] = ""
    cookies.save()
    st.session_state.clear()
    st.rerun()

# KIRISH EKRANI
if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 class='gradient-title'>Somo AI Infinity</h1></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.1, 1, 0.1])
    with col2:
        tab_log, tab_reg = st.tabs(["🔒 Kirish", "📝 Ro'yxatdan o'tish"])
        with tab_log:
            u_input = st.text_input("Username", key="login_user")
            p_input = st.text_input("Parol", type='password', key="login_pass")
            if st.button("Tizimga kirish 🚀", use_container_width=True):
                recs = user_db.get_all_records()
                hp = hashlib.sha256(p_input.encode()).hexdigest()
                found = next((r for r in recs if str(r['username']) == u_input and str(r['password']) == hp), None)
                
                if found:
                    if str(found.get('status', '')).lower() == 'blocked':
                        st.error("🚫 Sizning hisobingiz bloklangan! Admin bilan bog'laning.")
                    else:
                        st.session_state.username = u_input
                        st.session_state.logged_in = True
                        cookies["somo_user_session"] = u_input
                        cookies.save()
                        st.rerun()
                else: st.error("⚠️ Username yoki parol noto'g'ri!")
        with tab_reg:
            nu = st.text_input("Yangi Username", key="reg_user")
            np = st.text_input("Yangi Parol", type='password', key="reg_pass")
            if st.button("Hisob yaratish ✨", use_container_width=True):
                if nu and np:
                    recs = user_db.get_all_records()
                    if any(str(r['username']) == nu for r in recs):
                        st.warning("Bu username band!")
                    else:
                        hp = hashlib.sha256(np.encode()).hexdigest()
                        user_db.append_row([nu, hp, "active", str(datetime.now())])
                        st.success("✅ Ro'yxatdan o'tdingiz! Kirish bo'limiga o'ting.")
    st.stop()

# HAR SAFAR LOGIN BO'LGANDA BLOKLANGANLIGINI TEKSHIRISH
if not check_user_status(st.session_state.username):
    st.warning("🚫 Sizning hisobingiz bloklandi. Tizimdan chiqarilasiz...")
    time.sleep(2)
    logout_user()

# --- 🚀 6. ASOSIY INTERFEYS (CHAT VA DASHBOARD) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR SOZLAMALARI
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #6366f1); width: 85px; height: 85px; border-radius: 50%; margin: 0 auto; line-height: 85px; font-size: 38px; color: white; font-weight: 900; border: 4px solid white; box-shadow: 0 10px 20px rgba(0,0,0,0.1);'>
                {st.session_state.username[0].upper()}
            </div>
            <h2 style='color: #0369a1; margin-top: 15px; font-size: 1.2rem;'>{st.session_state.username}</h2>
            <p style='color: #0ea5e9; font-size: 0.8rem;'>Foydalanuvchi: Active</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **HUJJAT TAHLILI**")
    uploaded_file = st.file_uploader("Faylni tanlang", type=["pdf", "docx"], label_visibility="collapsed")
    context_text = extract_file_content(uploaded_file)
    if uploaded_file: st.success("📄 Fayl o'qildi")

    st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish"):
        logout_user()

# DASHBOARD (Agar xabarlar bo'sh bo'lsa)
if not st.session_state.messages:
    st.markdown(f"<div style='text-align:center;'><h1 class='gradient-title'>Xush kelibsiz, {st.session_state.username}! ✨</h1></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748b;'>Sizning universal intellektual yordamchingiz har doim xizmatingizda.</p>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown('<div class="dashboard-card"><h1>🔬</h1><h3>Aqlli Tahlil</h3><p>Murakkab hisob-kitoblar va mantiqiy savollarga professional yechim.</p></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="dashboard-card"><h1>📂</h1><h3>Hujjatlar</h3><p>PDF va Word fayllarni tahlil qilish, xulosalash va tarjima qilish.</p></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<div class="dashboard-card"><h1>💡</h1><h3>Ijodkorlik</h3><p>Kreativ loyihalar, biznes ssenariylar va original g\'oyalar yaratish.</p></div>', unsafe_allow_html=True)

# CHAT TARIXINI KO'RSATISH
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# INPUT VA AI JAVOBI
if prompt := st.chat_input("Somo AI ga savol bering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # AI shaxsi va xotira
            sys_prompt = f"Sening isming Somo AI. Yaratuvching: Usmonov Sodiq. Foydalanuvchi: {st.session_state.username}. Har doim professional, do'stona va aniq javob ber. Matematik formulalarni LaTeX ($...$) formatida yoz."
            
            messages_payload = [{"role": "system", "content": sys_prompt}]
            if context_text:
                messages_payload.append({"role": "system", "content": f"Foydalanuvchi yuklagan hujjat mazmuni: {context_text[:4000]}"})
            
            # Oxirgi 12 ta xabarni xotira sifatida yuborish
            for m in st.session_state.messages[-12:]:
                messages_payload.append(m)
            
            res_area = st.empty()
            response = client.chat.completions.create(
                messages=messages_payload,
                model="llama-3.3-70b-versatile",
                temperature=0.6,
                max_tokens=2048
            ).choices[0].message.content
            
            res_area.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Google Sheets'ga chat tarixini saqlash
            if chat_db:
                chat_db.append_row([st.session_state.username, prompt, response[:500], str(datetime.now())])
        except Exception as e:
            st.error(f"Xatolik yuz berdi: {str(e)}")
