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
st.set_page_config(page_title="Somo AI | Universal Infinity", page_icon="🌌", layout="wide")

# Cookies - Sessiyani 30 kungacha eslab qolish
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Super_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. PREMIUM MOSLASHUVCHAN DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon va vidjetlarni tozalash */
    .stApp { background-color: #f8fafc !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* BURCHAKDAGI TEXTLARNI YO'QOTISH */
    .st-emotion-cache-1vt458p, .st-emotion-cache-k77z8z, .st-emotion-cache-12fmjuu { 
        font-size: 0px !important; 
    }

    /* SIDEBAR - MUKAMMAL OCHIQ KO'K */
    [data-testid="stSidebar"] {
        background-color: #e0f2fe !important;
        border-right: 2px solid #bae6fd;
    }
    [data-testid="stSidebar"] section, [data-testid="stSidebar"] .stVerticalBlock {
        background-color: #e0f2fe !important;
    }

    /* MATN VA TUGMALAR */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #0369a1 !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px !important;
        width: 100% !important;
        transition: 0.3s ease;
    }
    div[data-testid="stSidebar"] button:hover { transform: scale(1.02); }

    /* DASHBOARD KARTALARI - ADAPTIVE (MOBIL VA PC) */
    .dashboard-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        margin-top: 30px;
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
        transition: 0.4s ease;
    }
    
    /* 📱 MOBIL QURILMALAR UCHUN KICHRAYTIRISH */
    @media (max-width: 768px) {
        .card-box {
            padding: 15px !important;
            min-width: 140px !important;
            max-width: 45% !important;
        }
        .card-box h1 { font-size: 25px !important; }
        .card-box h3 { font-size: 16px !important; }
        .card-box p { font-size: 12px !important; }
        h1 { font-size: 22px !important; }
    }

    .gradient-text {
        background: linear-gradient(90deg, #0284c7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. SERVISLARNI ULANISH ---
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

# --- 📂 4. FAYL KONVERTER ---
def process_doc(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.extract_raw_text(file).value
    except: return ""
    return ""

# --- 🔐 5. LOGIN VA BLOKIROVKA TIZIMI ---
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user:
        # Bloklanganligini tekshirish
        recs = user_db.get_all_records()
        user_data = next((r for r in recs if r['username'] == session_user), None)
        if user_data and user_data.get('status') == 'active':
            st.session_state.username = session_user
            st.session_state.logged_in = True
        else:
            st.session_state.logged_in = False
            cookies["somo_user_session"] = "" # Agar bloklansa sessiyani o'chirish
    else:
        st.session_state.logged_in = False

def logout():
    cookies["somo_user_session"] = ""
    cookies.save()
    st.session_state.clear()
    st.rerun()

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; margin-top:50px;'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.1, 1, 0.1])
    with c2:
        tab1, tab2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
        with tab1:
            u_in = st.text_input("Username", key="l_u")
            p_in = st.text_input("Parol", type='password', key="l_p")
            if st.button("Kirish 🚀", use_container_width=True):
                recs = user_db.get_all_records()
                hp = hashlib.sha256(p_in.encode()).hexdigest()
                user = next((r for r in recs if str(r['username']) == u_in and str(r['password']) == hp), None)
                
                if user:
                    if user.get('status') == 'blocked':
                        st.error("🚫 Sizning hisobingiz bloklangan! Admin bilan bog'laning.")
                    else:
                        st.session_state.username = u_in
                        st.session_state.logged_in = True
                        cookies["somo_user_session"] = u_in
                        cookies.save()
                        st.rerun()
                else: st.error("❌ Login yoki parol xato!")
        with tab2:
            nu = st.text_input("Yangi Username", key="r_u")
            np = st.text_input("Yangi Parol", type='password', key="r_p")
            if st.button("Yaratish ✨", use_container_width=True):
                if nu and np:
                    hp = hashlib.sha256(np.encode()).hexdigest()
                    user_db.append_row([nu, hp, "active", str(datetime.now())])
                    st.success("✅ Hisob ochildi! Endi Kirish bo'limiga o'ting.")
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS ---
if "messages" not in st.session_state: st.session_state.messages = []

# SIDEBAR (OCHIQ KO'K VA TOZA)
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 10px;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #6366f1); width: 70px; height: 70px; border-radius: 50%; margin: 0 auto; line-height: 70px; font-size: 30px; color: white; font-weight: bold;'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='color: #0369a1;'>{st.session_state.username}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **HUJJATLAR TAHLILI**")
    f_up = st.file_uploader("Yuklash", type=["pdf", "docx"], label_visibility="collapsed")
    f_txt = process_doc(f_up) if f_up else ""
    if f_up: st.success("📄 Hujjat o'qildi")

    st.markdown("<br>"*8, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish"): logout()

# DASHBOARD (MOSLASHUVCHAN)
if not st.session_state.messages:
    st.markdown(f"<h2 style='text-align: center; margin-top: 20px;'>Salom, <span class='gradient-text'>{st.session_state.username}</span>! 👋</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='dashboard-container'>
            <div class='card-box'><h1>🧠</h1><h3>Aqlli Tahlil</h3><p>Murakkab mantiqiy savollar</p></div>
            <div class='card-box'><h1>📄</h1><h3>Hujjat</h3><p>PDF/Word tahlili</p></div>
            <div class='card-box'><h1>🎨</h1><h3>Ijod</h3><p>Yangi g'oyalar va kod</p></div>
        </div>
    """, unsafe_allow_html=True)

# CHAT VA AI MANTIQI
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if pr := st.chat_input("Somo AI ga xabar yuboring..."):
    st.session_state.messages.append({"role": "user", "content": pr})
    with st.chat_message("user"): st.markdown(pr)

    with st.chat_message("assistant"):
        try:
            # AI yo'riqnomasi
            sys_pr = f"Isming Somo AI. Yaratuvching Usmonov Sodiq. Professional va do'stona javob ber. Matematikani LaTeX ($...$) da yoz."
            
            msgs = [{"role": "system", "content": sys_pr}]
            if f_txt: msgs.append({"role": "system", "content": f"Hujjat mazmuni: {f_txt[:3500]}"})
            for old in st.session_state.messages[-12:]: msgs.append(old)
            
            # Groq AI chaqiruvi
            res = client.chat.completions.create(
                messages=msgs,
                model="llama-3.3-70b-versatile",
                temperature=0.6,
                max_tokens=2048
            ).choices[0].message.content
            
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            
            # Google Sheets chat tarixini saqlash
            if chat_db:
                chat_db.append_row([st.session_state.username, pr, res[:500], str(datetime.now())])
        except Exception as e:
            st.error(f"⚠️ Xatolik: {str(e)}")
