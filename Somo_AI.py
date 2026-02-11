import streamlit as st
import pandas as pd
import gspread
import hashlib
import mammoth
import json
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

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

# --- 🎨 2. PREMIUM VA MUKAMMAL DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { 
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%) !important;
    }
    
    /* Sidebar menyusini yashirish va bezash */
    [data-testid="stSidebarNav"] { display: none !important; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 2px solid #334155;
    }

    /* Sidebar ichidagi matnlar */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h3 {
        color: #f1f5f9 !important;
    }

    /* Kartalar dizayni */
    .dashboard-container {
        display: flex;
        flex-wrap: wrap;
        gap: 30px;
        justify-content: center;
        margin-top: 40px;
        padding: 20px;
    }
    
    .card-box {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        flex: 1;
        min-width: 300px;
        max-width: 400px;
        backdrop-filter: blur(10px);
    }
    
    .card-box:hover {
        transform: translateY(-15px) scale(1.02);
        box-shadow: 0 25px 50px rgba(14, 165, 233, 0.3);
        background: white;
    }

    .card-box h1 { font-size: 50px; margin-bottom: 10px; }
    .card-box h3 { color: #0f172a; font-weight: 800; }
    .card-box p { color: #64748b; font-size: 15px; }

    /* Gradient matn */
    .gradient-text {
        background: linear-gradient(90deg, #0ea5e9, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
    }

    /* Tugmalar */
    div.stButton > button {
        border-radius: 12px;
        font-weight: 600;
        transition: 0.3s all ease;
    }
    
    /* Fikr bildirish tugmasi maxsus */
    .feedback-btn button {
        background: #10b981 !important;
        color: white !important;
        border: none !important;
    }

    /* Mobil moslashuv */
    @media (max-width: 768px) {
        .card-box { min-width: 100% !important; margin-bottom: 20px; }
        h1 { font-size: 32px !important; }
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
        
        # Varaqlarni tekshirish va olish
        u_sheet = ss.sheet1
        c_sheet = ss.worksheet("ChatHistory")
        
        # Letters varag'ini olish yoki yaratish
        try:
            l_sheet = ss.worksheet("Letters")
        except:
            l_sheet = ss.add_worksheet(title="Letters", rows="100", cols="20")
            l_sheet.append_row(["Time", "User", "Feedback"])
            
        return u_sheet, c_sheet, l_sheet
    except Exception as e:
        st.error(f"Baza xatosi: {str(e)}")
        return None, None, None

user_db, chat_db, letter_db = get_connections()

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    client = None

# --- 📂 4. FUNKSIYALAR ---
def process_doc(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.extract_raw_text(file).value
    except: return ""
    return ""

def handle_logout():
    cookies["somo_user_session"] = ""
    cookies.save()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- 🔐 5. SESSION VA LOGIN ---
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user and user_db:
        try:
            recs = user_db.get_all_records()
            user_data = next((r for r in recs if str(r['username']) == session_user), None)
            if user_data and str(user_data.get('status')).lower() == 'active':
                st.session_state.username = session_user
                st.session_state.logged_in = True
            else: st.session_state.logged_in = False
        except: st.session_state.logged_in = False
    else: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; margin-top:60px;'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.2, 1, 0.2])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish"])
        with tab1:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Parol", type='password')
                if st.form_submit_button("Kirish 🚀", use_container_width=True):
                    recs = user_db.get_all_records()
                    hp = hashlib.sha256(p.encode()).hexdigest()
                    user = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
                    if user:
                        st.session_state.username = u
                        st.session_state.logged_in = True
                        cookies["somo_user_session"] = u
                        cookies.save()
                        st.rerun()
                    else: st.error("Xato!")
        with tab2:
            with st.form("reg"):
                nu = st.text_input("Yangi Username")
                np = st.text_input("Yangi Parol", type='password')
                if st.form_submit_button("Ro'yxatdan o'tish ✨", use_container_width=True):
                    recs = user_db.get_all_records()
                    if any(r['username'] == nu for r in recs): st.error("Username band!")
                    else:
                        hp = hashlib.sha256(np.encode()).hexdigest()
                        user_db.append_row([nu, hp, "active", str(datetime.now())])
                        st.success("Tayyor! Kirishga o'ting.")
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS ---
if "messages" not in st.session_state: st.session_state.messages = []

# SIDEBAR
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <div style='background: white; width: 60px; height: 60px; border-radius: 50%; margin: 0 auto; color: #0f172a; line-height: 60px; font-size: 24px; font-weight: bold;'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='margin-top:10px;'>{st.session_state.username}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🗑 Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # FEEDBACK SECTION (Siz aytgan Letters qismi)
    st.markdown("---")
    st.markdown("### 📩 Fikr-mulohaza")
    with st.expander("Fikr qoldirish"):
        fb_text = st.text_area("Xabaringizni yozing...", key="feedback_input")
        if st.button("Yuborish 📨", use_container_width=True):
            if fb_text and letter_db:
                letter_db.append_row([str(datetime.now()), st.session_state.username, fb_text])
                st.success("Rahmat! Fikringiz qabul qilindi.")

    st.markdown("---")
    st.markdown("### 📂 Hujjat Tahlili")
    f_up = st.file_uploader("PDF/DOCX", type=["pdf", "docx"], label_visibility="collapsed")
    f_txt = process_doc(f_up) if f_up else ""
    
    st.markdown("<br>"*5, unsafe_allow_html=True)
    if st.button("🚪 Chiqish", use_container_width=True, type="primary"):
        handle_logout()

# DASHBOARD (3 ta kreativ karta)
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center;'>Xush kelibsiz, <span class='gradient-text'>{st.session_state.username}</span>!</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div class='dashboard-container'>
            <div class='card-box'>
                <h1>🧠</h1>
                <h3>Universal Intellekt</h3>
                <p>Murakkab mantiqiy savollar va tahlillarga javob olshingiz mumkin.</p>
            </div>
            <div class='card-box'>
                <h1>📄</h1>
                <h3>Hujjatlar bilan ishlash</h3>
                <p>Hujjatlarni yuklang va ularni Somo AI orqali tahlil qildiring.</p>
            </div>
            <div class='card-box'>
                <h1>🎨</h1>
                <h3>Kreativ Yechimlar</h3>
                <p>Kod yozish, g'oyalar yaratish va ijodiy yondashuvlar markazi.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# CHAT OYNASI
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# INPUT VA SAQLASH
if pr := st.chat_input("Somo AI ga xabar yozing..."):
    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # User xabari
    st.session_state.messages.append({"role": "user", "content": pr})
    with st.chat_message("user"): st.markdown(pr)
    if chat_db:
        chat_db.append_row([time_stamp, st.session_state.username, "User", pr])
    
    # AI javobi
    with st.chat_message("assistant"):
        with st.spinner("Somo AI o'ylamoqda..."):
            try:
                msgs = [{"role": "system", "content": "Sening isming Somo AI. Usmonov Sodiq yaratgan professional yordamchisan. Matematikani LaTeXda yoz."}]
                if f_txt: msgs.append({"role": "system", "content": f"Hujjat: {f_txt[:3500]}"})
                for old in st.session_state.messages[-10:]: msgs.append(old)
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=msgs,
                    temperature=0.7
                ).choices[0].message.content
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                if chat_db:
                    chat_db.append_row([time_stamp, "Somo AI", "Assistant", response])
            except:
                st.error("Xatolik yuz berdi!")

# FOOTER
st.markdown("<br><hr><center>Somo AI Infinity © 2026 | By Usmonov Sodiq</center>", unsafe_allow_html=True)
