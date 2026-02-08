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
st.set_page_config(page_title="Somo AI | Infinity", page_icon="🌌 ", layout="wide")

# Cookies - Sessiyani saqlash (Avtomatik kirish va chiqish mantiqi uchun)
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Sky_Secret_2026_Perfect"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. MUKAMMAL OCHIQ KO'K PREMIUM DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { background-color: #f0f9ff !important; }

    /* CHAP BO'LIM (SIDEBAR) - MUKAMMAL OCHIQ KO'K */
    [data-testid="stSidebar"] {
        background-color: #bae6fd !important; /* Sky Blue */
        border-right: 2px solid #7dd3fc;
    }
    
    /* Sidebar ichidagi barcha bloklarni bir xil rangga bo'yash (Oq dog'larni yo'qotish) */
    [data-testid="stSidebar"] section, 
    [data-testid="stSidebar"] .stVerticalBlock,
    [data-testid="stSidebar"] .stMarkdown {
        background-color: #bae6fd !important;
    }
    
    /* Sidebar matnlari - To'q moviy kontras */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span {
        color: #0369a1 !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif;
    }

    /* TUGMALAR DIZAYNI (Sidebar) */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 15px !important;
        padding: 12px 20px !important;
        font-weight: 700 !important;
        transition: 0.4s all ease !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.2) !important;
    }
    
    div[data-testid="stSidebar"] button:hover {
        transform: scale(1.03) !important;
        background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%) !important;
        box-shadow: 0 8px 20px rgba(14, 165, 233, 0.4) !important;
    }

    /* FAYL YUKLASH MAYDONI */
    [data-testid="stFileUploader"] {
        background-color: #f0f9ff !important;
        border: 2px dashed #0ea5e9 !important;
        border-radius: 15px !important;
        padding: 10px !important;
    }

    /* ASOSIY SAHIFA KARTALARI */
    .card-box {
        background: white;
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        border: 1px solid #e0f2fe;
        transition: 0.4s;
    }
    .card-box:hover { 
        transform: translateY(-10px); 
        border-color: #0ea5e9;
        box-shadow: 0 20px 40px rgba(14, 165, 233, 0.1);
    }
    
    .gradient-text {
        background: linear-gradient(90deg, #0284c7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
    }

    /* Chat xabarlari */
    .stChatMessage {
        background-color: white !important;
        border-radius: 20px !important;
        border: 1px solid #e0f2fe !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.02) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. SERVISLARNI ULANISH (GOOGLE SHEETS & GROQ) ---
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

# --- 📂 4. MUKAMMAL FAYL PROTSESSOR ---
def process_doc(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                content = page.extract_text()
                if content: text += content + "\n"
            return text
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.extract_raw_text(file).value
    except Exception as e:
        return f"Xatolik: {str(e)}"
    return ""

# --- 🔐 5. LOGIN VA SESSYA BOSHQARUVI ---
if 'logged_in' not in st.session_state:
    # Cookie'dan foydalanuvchini tekshirish
    session_user = cookies.get("somo_user_session")
    if session_user:
        st.session_state.username = session_user
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

# TIZIMDAN CHIQISH FUNKSIYASI (TO'G'RILANGAN)
def logout():
    cookies["somo_user_session"] = ""
    cookies.save()
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.messages = []
    st.rerun()

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; margin-top:50px;'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        tab1, tab2 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish"])
        with tab1:
            u_in = st.text_input("Username", key="login_u")
            p_in = st.text_input("Parol", type='password', key="login_p")
            if st.button("Tizimga kirish 🚀", use_container_width=True):
                recs = user_db.get_all_records()
                hp = hashlib.sha256(p_in.encode()).hexdigest()
                found = next((r for r in recs if str(r['username']) == u_in and str(r['password']) == hp), None)
                if found:
                    st.session_state.username = u_in
                    st.session_state.logged_in = True
                    cookies["somo_user_session"] = u_in
                    cookies.save()
                    st.rerun()
                else: st.error("❌ Username yoki parol noto'g'ri!")
        with tab2:
            nu_in = st.text_input("Yangi Username", key="reg_u")
            np_in = st.text_input("Yangi Parol", type='password', key="reg_p")
            if st.button("Hisob yaratish ✨", use_container_width=True):
                if nu_in and np_in:
                    h_pass = hashlib.sha256(np_in.encode()).hexdigest()
                    user_db.append_row([nu_in, h_pass, "active", str(datetime.now())])
                    st.success("✅ Hisob yaratildi! Endi 'Kirish' bo'limiga o'ting.")
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS (LOGGED IN) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR (OCHIQ KO'K)
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #6366f1); width: 90px; height: 90px; border-radius: 50%; margin: 0 auto; line-height: 90px; font-size: 40px; color: white; font-weight: bold; border: 4px solid white; box-shadow: 0 10px 20px rgba(0,0,0,0.1);'>
                {st.session_state.username[0].upper()}
            </div>
            <h2 style='color: #0369a1; margin-top: 15px;'>{st.session_state.username}</h2>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **HUJJATLAR BILAN ISHLASH**")
    f_up = st.file_uploader("PDF yoki Word yuklang", type=["pdf", "docx"], label_visibility="collapsed")
    f_content = process_doc(f_up) if f_up else ""
    if f_up: st.success("✅ Hujjat tahlil qilindi!")

    # Sidebar pastki qismi - Logout
    st.markdown("<div style='height: 25vh;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish"):
        logout()

# DASHBOARD (ASOSIY OYNA)
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center; margin-top: 30px;'>Xush kelibsiz, <span class='gradient-text'>{st.session_state.username}</span>! ✨</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.1rem;'>Somo AI - Har qanday savolingizga javob beruvchi universal yordamchi.</p>", unsafe_allow_html=True)
    
    c_tab1, c_tab2, c_tab3 = st.columns(3)
    with c_tab1: st.markdown('<div class="card-box"><h1>🧠</h1><h3>Aqlli Tahlil</h3><p>Murakkab matematika va mantiqiy masalalar yechimi</p></div>', unsafe_allow_html=True)
    with c_tab2: st.markdown('<div class="card-box"><h1>📄</h1><h3>Hujjatlar</h3><p>PDF va Word fayllarni o\'qish, tarjima va xulosa</p></div>', unsafe_allow_html=True)
    with c_tab3: st.markdown('<div class="card-box"><h1>🎨</h1><h3>Ijodkorlik</h3><p>Ssenariylar, kodlar, she\'rlar va biznes g\'oyalar</p></div>', unsafe_allow_html=True)

# CHAT TARIXI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# INPUT VA AI JAVOBI
if prompt := st.chat_input("Somo AI ga xabar yuboring..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # System Prompt - Somo AI shaxsi
            s_msg = f"Sening isming Somo AI. Yaratuvching: Usmonov Sodiq. Foydalanuvchi: {st.session_state.username}. Har qanday sohada professional, do'stona va aniq javob ber. Matematikani yaxshi bilasan, formulalarni LaTeX ($...$) formatida yoz."
            
            ctx = [{"role": "system", "content": s_msg}]
            
            # Fayl mazmunini qo'shish
            if f_content:
                ctx.append({"role": "system", "content": f"Foydalanuvchi yuklagan hujjat: {f_content[:4000]}"})
            
            # Chat tarixi (oxirgi 12 ta xabar)
            for old_m in st.session_state.messages[-12:]:
                ctx.append(old_m)
            
            # Groq orqali javob olish
            r_box = st.empty()
            ai_res = client.chat.completions.create(
                messages=ctx,
                model="llama-3.3-70b-versatile",
                temperature=0.6,
                max_tokens=2048
            ).choices[0].message.content
            
            r_box.markdown(ai_res)
            st.session_state.messages.append({"role": "assistant", "content": ai_res})
            
            # Google Sheets'ga yozish
            if chat_db:
                chat_db.append_row([st.session_state.username, prompt, ai_res[:400], str(datetime.now())])
        except Exception as e:
            st.error(f"⚠️ Aloqa xatosi: {str(e)}")
