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
import json

# --- 🛰 1. SISTEMA SOZLAMALARI ---
st.set_page_config(
    page_title="Somo AI | Universal Infinity", 
    page_icon="🌌", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cookies - Sessiyani 30 kungacha eslab qolish
cookies = EncryptedCookieManager(
    password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026_Final_PRO")
)
if not cookies.ready():
    st.stop()

# --- 🎨 2. PREMIUM DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Umumiy fon va font */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%) !important;
    }

    /* SIDEBAR YO'Q QILISH UCHUN YASHIRIN MATNLAR */
    [data-testid="stSidebarNav"] { display: none !important; }
    .st-emotion-cache-1vt458p, .st-emotion-cache-k77z8z, .st-emotion-cache-12fmjuu { 
        font-size: 0px !important; 
        color: transparent !important;
    }

    /* SIDEBAR - PREMIUM DARK GRADIENT */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        border-right: 3px solid #334155;
    }
    [data-testid="stSidebar"] section, [data-testid="stSidebar"] .stVerticalBlock {
        background: transparent !important;
    }

    /* SIDEBAR TUGMALARI - PREMIUM STYLE */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100% !important;
        padding: 14px 20px !important;
        margin: 8px 0 !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    div[data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
    }
    div[data-testid="stSidebar"] button:active {
        transform: translateY(-1px) scale(0.98);
    }

    /* DASHBOARD KARTALARI - 3TA PREMIUM KARTALAR */
    .dashboard-container {
        display: flex;
        flex-wrap: wrap;
        gap: 30px;
        justify-content: center;
        margin: 50px auto;
        max-width: 1400px;
        padding: 20px;
    }
    
    .premium-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 24px;
        padding: 50px 40px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        border: 2px solid #475569;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        flex: 1;
        min-width: 320px;
        max-width: 420px;
        position: relative;
        overflow: hidden;
    }
    
    .premium-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        opacity: 0;
        transition: opacity 0.5s ease;
        z-index: 1;
    }
    
    .premium-card:hover::before {
        opacity: 1;
    }
    
    .premium-card:hover {
        transform: translateY(-15px) scale(1.03);
        box-shadow: 0 30px 80px rgba(59, 130, 246, 0.4);
        border-color: #3b82f6;
    }
    
    .premium-card .card-icon {
        font-size: 80px;
        margin-bottom: 25px;
        filter: drop-shadow(0 4px 8px rgba(59, 130, 246, 0.3));
        position: relative;
        z-index: 2;
    }
    
    .premium-card h2 {
        color: #f1f5f9;
        font-size: 32px;
        font-weight: 800;
        margin: 20px 0 15px 0;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
        z-index: 2;
    }
    
    .premium-card p {
        color: #cbd5e1;
        font-size: 16px;
        line-height: 1.6;
        margin: 0;
        position: relative;
        z-index: 2;
    }

    /* 📱 MOBIL OPTIMIZATSIYA */
    @media (max-width: 768px) {
        .premium-card {
            min-width: 280px !important;
            padding: 35px 25px !important;
            margin-bottom: 20px !important;
        }
        .premium-card .card-icon { font-size: 60px !important; }
        .premium-card h2 { font-size: 26px !important; }
        .premium-card p { font-size: 14px !important; }
        .main-title { font-size: 36px !important; }
        .subtitle { font-size: 16px !important; }
    }

    /* GRADIENT TEXT ANIMATSIYA */
    .gradient-text {
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6, #60a5fa);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        animation: gradient-flow 4s ease infinite;
    }
    
    @keyframes gradient-flow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* LOGIN TABLAR - PREMIUM */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 15px; 
        background: transparent;
        border-bottom: 2px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background: linear-gradient(135deg, #1e293b, #334155);
        border-radius: 12px 12px 0 0;
        padding: 0 30px;
        border: 2px solid #475569;
        transition: all 0.3s ease;
        color: #94a3b8;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #334155, #475569);
        border-color: #3b82f6;
        color: #f1f5f9;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        border-color: #60a5fa;
    }
    
    /* CHAT XABARLARI - PREMIUM */
    .stChatMessage {
        background: linear-gradient(135deg, #1e293b, #334155) !important;
        border-radius: 18px !important;
        padding: 20px !important;
        margin: 15px 0 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        border: 1px solid #475569 !important;
    }
    
    .stChatMessage[data-testid="user-message"] {
        border-left: 4px solid #3b82f6 !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        border-left: 4px solid #8b5cf6 !important;
    }
    
    /* INPUT MAYDONI - PREMIUM */
    .stChatInputContainer {
        border-top: 2px solid #334155 !important;
        background: linear-gradient(135deg, #0f172a, #1e293b) !important;
        padding: 20px !important;
    }
    
    .stChatInput textarea {
        background: #1e293b !important;
        color: #f1f5f9 !important;
        border: 2px solid #475569 !important;
        border-radius: 14px !important;
        font-size: 16px !important;
        padding: 15px !important;
    }
    
    .stChatInput textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* METRICS - PREMIUM */
    [data-testid="stMetricValue"] {
        color: #60a5fa !important;
        font-size: 28px !important;
        font-weight: 800 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    
    /* TEXT INPUTS - PREMIUM */
    .stTextInput input {
        background: #1e293b !important;
        color: #f1f5f9 !important;
        border: 2px solid #475569 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        font-size: 15px !important;
    }
    
    .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* FORM SUBMIT BUTTON - PREMIUM */
    .stButton button[kind="primaryFormSubmit"] {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button[kind="primaryFormSubmit"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6) !important;
    }
    
    /* SLIDER - PREMIUM */
    .stSlider {
        padding: 10px 0;
    }
    
    /* FILE UPLOADER - PREMIUM */
    [data-testid="stFileUploader"] {
        background: #1e293b !important;
        border: 2px dashed #475569 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    /* SUCCESS/ERROR MESSAGES - PREMIUM */
    .stSuccess {
        background: linear-gradient(135deg, #065f46, #047857) !important;
        color: #d1fae5 !important;
        border-radius: 12px !important;
        border-left: 4px solid #10b981 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #7f1d1d, #991b1b) !important;
        color: #fecaca !important;
        border-radius: 12px !important;
        border-left: 4px solid #ef4444 !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #1e3a8a, #1e40af) !important;
        color: #dbeafe !important;
        border-radius: 12px !important;
        border-left: 4px solid #3b82f6 !important;
    }
    
    /* SCROLLBAR - PREMIUM */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
    }
    
    /* LOADING SPINNER */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 🔗 3. BAZA VA AI ALOQASI ---
@st.cache_resource
def get_connections():
    """Google Sheets bilan bog'lanish"""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        return ss.sheet1, ss.worksheet("ChatHistory")
    except Exception as e:
        st.error(f"❌ Baza xatosi: {str(e)}")
        return None, None

user_db, chat_db = get_connections()

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    client = None

# --- 📂 4. FAYL TAHLILI ---
def process_doc(file):
    """PDF va DOCX tahlil"""
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            return "\n".join(text)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            result = mammoth.extract_raw_text(file)
            return result.value
    except Exception as e:
        st.error(f"❌ Fayl xatosi: {str(e)}")
        return ""
    return ""

# --- 🔐 5. SESSION BOSHQARUVI ---
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user and user_db:
        try:
            recs = user_db.get_all_records()
            user_data = next((r for r in recs if str(r['username']) == session_user), None)
            if user_data and str(user_data.get('status')).lower() == 'active':
                st.session_state.username = session_user
                st.session_state.logged_in = True
                st.session_state.login_time = datetime.now()
            else:
                st.session_state.logged_in = False
        except:
            st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

def handle_logout():
    """Chiqish"""
    try:
        cookies["somo_user_session"] = ""
        cookies.save()
    except:
        pass
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.logged_in = False
    st.rerun()

# --- 🔒 LOGIN SAHIFASI ---
if not st.session_state.logged_in:
    st.markdown("""
        <div style='text-align:center; margin-top:80px;'>
            <h1 class='main-title' style='font-size: 56px; margin-bottom: 15px; color: #f1f5f9;'>
                🌌 Somo AI <span class='gradient-text'>Infinity</span>
            </h1>
            <p class='subtitle' style='color: #94a3b8; font-size: 20px; margin-bottom: 60px; font-weight: 500;'>
                Kelajak sun'iy intellekti bilan tanishing
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.25, 1, 0.25])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔐 Kirish", "✨ Ro'yxatdan o'tish"])
        
        with auth_tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                u_in = st.text_input("👤 Username", placeholder="Username kiriting", label_visibility="collapsed")
                p_in = st.text_input("🔑 Parol", type='password', placeholder="Parol kiriting", label_visibility="collapsed")
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("🚀 Kirish", use_container_width=True)
                
                if submitted and u_in and p_in:
                    if user_db:
                        try:
                            recs = user_db.get_all_records()
                            hp = hashlib.sha256(p_in.encode()).hexdigest()
                            user = next((r for r in recs if str(r['username']) == u_in and str(r['password']) == hp), None)
                            
                            if user:
                                if str(user.get('status')).lower() == 'blocked':
                                    st.error("🚫 Hisobingiz bloklangan! Admin bilan bog'laning.")
                                else:
                                    st.session_state.username = u_in
                                    st.session_state.logged_in = True
                                    st.session_state.login_time = datetime.now()
                                    cookies["somo_user_session"] = u_in
                                    cookies.save()
                                    st.success("✅ Muvaffaqiyatli kirish!")
                                    st.rerun()
                            else:
                                st.error("❌ Login yoki parol xato!")
                        except Exception as e:
                            st.error(f"❌ Xatolik: {str(e)}")
        
        with auth_tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("register_form"):
                nu = st.text_input("👤 Username", placeholder="Yangi username tanlang", label_visibility="collapsed")
                np = st.text_input("🔑 Parol", type='password', placeholder="Parol yarating (kamida 6 ta belgi)", label_visibility="collapsed")
                np_confirm = st.text_input("🔑 Tasdiqlash", type='password', placeholder="Parolni qayta kiriting", label_visibility="collapsed")
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("✨ Ro'yxatdan o'tish", use_container_width=True)
                
                if submitted:
                    if not nu or not np:
                        st.error("❌ Barcha maydonlarni to'ldiring!")
                    elif len(np) < 6:
                        st.error("❌ Parol kamida 6 ta belgidan iborat bo'lishi kerak!")
                    elif np != np_confirm:
                        st.error("❌ Parollar mos kelmadi!")
                    elif user_db:
                        try:
                            recs = user_db.get_all_records()
                            if any(r['username'] == nu for r in recs):
                                st.error("❌ Bu username allaqachon band!")
                            else:
                                hp = hashlib.sha256(np.encode()).hexdigest()
                                user_db.append_row([nu, hp, "active", str(datetime.now())])
                                st.success("✅ Muvaffaqiyatli! Endi 'Kirish' bo'limiga o'ting.")
                        except Exception as e:
                            st.error(f"❌ Xatolik: {str(e)}")
    
    st.markdown("""
        <div style='text-align:center; margin-top:80px; color: #64748b;'>
            <p style='font-size: 14px;'>© 2026 Somo AI Infinity • Yaratuvchi: Usmonov Sodiq</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_messages" not in st.session_state:
    st.session_state.total_messages = 0

# --- 📊 SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 20px; margin-bottom: 25px;'>
            <div style='background: linear-gradient(135deg, #3b82f6, #8b5cf6); width: 90px; height: 90px; border-radius: 50%; margin: 0 auto; line-height: 90px; font-size: 42px; color: white; font-weight: bold; border: 4px solid #1e293b; box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='margin-top: 18px; color: #f1f5f9; font-size: 22px; font-weight: 700;'>{st.session_state.username}</h3>
            <p style='color: #10b981; font-size: 14px; font-weight: 600; margin-top: 5px;'>● Onlayn</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h4 style='color: #cbd5e1; font-weight: 700; margin-bottom: 15px;'>📊 Statistika</h4>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💬 Xabarlar", len(st.session_state.messages))
    with col2:
        if 'login_time' in st.session_state:
            session_duration = (datetime.now() - st.session_state.login_time).seconds // 60
            st.metric("⏱ Sessiya", f"{session_duration} daq")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #cbd5e1; font-weight: 700; margin-bottom: 15px;'>🎛 Boshqaruv</h4>", unsafe_allow_html=True)
    
    if st.button("🗑 Chatni tozalash", use_container_width=True, key="clear_chat"):
        st.session_state.messages = []
        st.success("✅ Chat tozalandi!")
        st.rerun()
    
    if st.button("📥 Yuklab olish", use_container_width=True, key="download_chat"):
        if st.session_state.messages:
            chat_export = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
            st.download_button(
                label="💾 JSON formatda",
                data=chat_export,
                file_name=f"somo_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                key="download_json"
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #cbd5e1; font-weight: 700; margin-bottom: 15px;'>📂 Hujjatlar</h4>", unsafe_allow_html=True)
    f_up = st.file_uploader("PDF yoki DOCX yuklang", type=["pdf", "docx"], label_visibility="collapsed", key="file_uploader")
    f_txt = process_doc(f_up) if f_up else ""
    if f_up:
        st.success(f"✅ {f_up.name} yuklandi")
        st.info(f"📄 Hajmi: {len(f_txt):,} belgi")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #cbd5e1; font-weight: 700; margin-bottom: 15px;'>⚙️ Sozlamalar</h4>", unsafe_allow_html=True)
    temperature = st.slider("🌡 Ijodkorlik darajasi", 0.0, 1.0, 0.6, 0.1, key="temp_slider", help="Pastroq - aniqroq javoblar, Yuqoriroq - ijodiyroq javoblar")
    
    st.markdown("<br>"*6, unsafe_allow_html=True)
    
    if st.button("🚪 Tizimdan chiqish", use_container_width=True, key="logout_btn", type="primary"):
        handle_logout()

# --- 🎨 DASHBOARD (3TA PREMIUM KARTALAR) ---
if not st.session_state.messages:
    st.markdown(f"""
        <div style='text-align: center; margin: 60px 0 40px 0;'>
            <h1 style='font-size: 48px; margin-bottom: 15px; color: #f1f5f9;'>
                Salom, <span class='gradient-text'>{st.session_state.username}</span>! 👋
            </h1>
            <p style='color: #94a3b8; font-size: 20px; font-weight: 500;'>
                Bugun sizga qanday yordam bera olaman?
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class='dashboard-container'>
            <div class='premium-card'>
                <div class='card-icon'>🧠</div>
                <h2>Aqlli Tahlil</h2>
                <p>Murakkab mantiqiy masalalar, matematika va chuqur tahlillar. Professional darajada yechimlar.</p>
            </div>
            <div class='premium-card'>
                <div class='card-icon'>📄</div>
                <h2>Hujjatlar Tahlili</h2>
                <p>PDF va Word fayllarni tahlil qilish, xulosalar chiqarish va professional hisobotlar.</p>
            </div>
            <div class='premium-card'>
                <div class='card-icon'>💡</div>
                <h2>Kreativ Yechimlar</h2>
                <p>Kod yozish, dizayn g'oyalari, ijodiy loyihalar va innovatsion yondashuvlar.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; color: #64748b; font-size: 16px;'>
            <p>💡 <strong>Maslahat:</strong> Pastdagi chat oynasiga savolingizni yozing yoki hujjat yuklang</p>
        </div>
    """, unsafe_allow_html=True)

# --- 💬 CHAT TARIXI ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- ✍️ YANGI XABAR INPUT ---
if pr := st.chat_input("💭 Somo AI ga xabar yuboring..."):
    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    st.session_state.messages.append({"role": "user", "content": pr})
    with st.chat_message("user"):
        st.markdown(pr)
    
    if chat_db:
        try:
            chat_db.append_row([time_stamp, st.session_state.username, "User", pr])
        except:
            pass
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Tahlil qilyapman..."):
            try:
                sys_instr = """Sening isming Somo AI. Seni Usmonov Sodiq yaratgan. 
                Sen professional, samimiy va foydali yordamchi sun'iy intellektsан. 
                Har doim aniq, tushunarli va to'liq javoblar berasan.
                Matematika formulalarini LaTeX formatida ($...$) yoz.
                Kod yozishda eng yaxshi amaliyotlardan foydalangan.
                Foydalanuvchi bilan samimiy va professional muloqot qil.
                Javoblarni tartibli, strukturali va tushunish oson qilib ber."""
                
                msgs = [{"role": "system", "content": sys_instr}]
                
                if f_txt:
                    msgs.append({
                        "role": "system", 
                        "content": f"Yuklangan hujjat mazmuni (birinchi 4500 ta belgi):\n\n{f_txt[:4500]}"
                    })
                
                for old in st.session_state.messages[-15:]:
                    msgs.append(old)
                
                if client:
                    response = client.chat.completions.create(
                        messages=msgs,
                        model="llama-3.3-70b-versatile",
                        temperature=temperature,
                        max_tokens=2500
                    )
                    
                    res = response.choices[0].message.content
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                    st.session_state.total_messages += 1
                    
                    if chat_db:
                        try:
                            chat_db.append_row([time_stamp, "Somo AI", "Assistant", res])
                        except:
                            pass
                else:
                    st.error("❌ AI xizmati hozirda mavjud emas. Iltimos, keyinroq qayta urinib ko'ring.")
                    
            except Exception as e:
                error_msg = f"❌ Xatolik yuz berdi: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# --- 📌 FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align:center; color: #64748b; padding: 30px; border-top: 2px solid #334155; margin-top: 40px;'>
        <p style='margin: 8px 0; font-size: 16px; font-weight: 600;'>🌌 <strong style='color: #94a3b8;'>Somo AI Infinity</strong> | Powered by Groq & Llama 3.3</p>
        <p style='margin: 8px 0; font-size: 15px;'>👨‍💻 Yaratuvchi: <strong style='color: #94a3b8;'>Usmonov Sodiq</strong></p>
        <p style='margin: 8px 0; font-size: 13px;'>© 2026 Barcha huquqlar himoyalangan</p>
    </div>
""", unsafe_allow_html=True)
