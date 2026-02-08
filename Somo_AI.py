import streamlit as st
import pandas as pd
import gspread
import hashlib
import mammoth
import json
import plotly.express as px
import plotly.graph_objects as go
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime, timedelta
from streamlit_cookies_manager import EncryptedCookieManager
import re
from collections import Counter
import base64
from io import BytesIO

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

# --- 🎨 2. PREMIUM VA MOSLASHUVCHAN DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { 
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%) !important;
    }

    /* BURCHAKDAGI MATNLARNI YO'QOTISH */
    [data-testid="stSidebarNav"] { display: none !important; }
    .st-emotion-cache-1vt458p, .st-emotion-cache-k77z8z, .st-emotion-cache-12fmjuu { 
        font-size: 0px !important; 
        color: transparent !important;
    }

    /* SIDEBAR - MUKAMMAL OCHIQ KO'K GRADIENT */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e0f2fe 0%, #bae6fd 100%) !important;
        border-right: 2px solid #7dd3fc;
    }
    [data-testid="stSidebar"] section, [data-testid="stSidebar"] .stVerticalBlock {
        background: transparent !important;
    }

    /* SIDEBAR TUGMALARI */
    div[data-testid="stSidebar"] button {
        background: white !important;
        color: #0284c7 !important;
        border: 2px solid #0ea5e9 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: 0.3s all ease;
        width: 100% !important;
    }
    div[data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(14, 165, 233, 0.3);
    }

    /* DASHBOARD KARTALARI */
    .dashboard-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        margin-top: 25px;
    }
    
    .card-box {
        background: white;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: 0.4s ease;
        flex: 1;
        min-width: 280px;
        max-width: 380px;
        cursor: pointer;
    }
    
    .card-box:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(14, 165, 233, 0.2);
        border-color: #0ea5e9;
    }

    /* 📱 MOBIL QURILMALAR UCHUN OPTIMIZATSIYA */
    @media (max-width: 768px) {
        .card-box {
            min-width: 150px !important;
            padding: 15px !important;
            margin-bottom: 10px !important;
        }
        .card-box h1 { font-size: 26px !important; }
        .card-box h3 { font-size: 16px !important; }
        .card-box p { font-size: 12px !important; }
        h1 { font-size: 24px !important; }
    }

    .gradient-text {
        background: linear-gradient(90deg, #0284c7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Login Tablarini chiroyli qilish */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f1f5f9;
        border-radius: 10px 10px 0 0;
        padding: 0 20px;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e0f2fe;
    }
    
    /* Chat xabarlari uchun animatsiya */
    .chat-message {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Statistika kartochkalari */
    .stat-card {
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(14, 165, 233, 0.3);
    }
    
    /* Code bloklari uchun */
    code {
        background-color: #f1f5f9 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        color: #6366f1 !important;
    }
    
    pre {
        background-color: #1e293b !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    
    /* Loading animatsiyasi */
    .stSpinner > div {
        border-color: #0ea5e9 transparent transparent transparent !important;
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
        return ss.sheet1, ss.worksheet("ChatHistory"), ss.worksheet("Analytics")
    except Exception as e:
        st.error(f"Bazaga ulanishda xato: {e}")
        return None, None, None

user_db, chat_db, analytics_db = get_connections()
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 📊 4. ANALYTICS VA STATISTIKA FUNKSIYALARI ---
def save_analytics(username, action, details=""):
    """Foydalanuvchi harakatlarini saqlash"""
    if analytics_db:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            analytics_db.append_row([timestamp, username, action, details])
        except:
            pass

def get_user_stats(username):
    """Foydalanuvchi statistikasini olish"""
    if not chat_db:
        return {"messages": 0, "documents": 0, "sessions": 0}
    
    try:
        all_records = chat_db.get_all_records()
        user_messages = [r for r in all_records if r.get('User') == username]
        
        return {
            "messages": len(user_messages),
            "documents": len([r for r in user_messages if "hujjat" in r.get('Message', '').lower()]),
            "sessions": len(set([r.get('Time', '').split()[0] for r in user_messages]))
        }
    except:
        return {"messages": 0, "documents": 0, "sessions": 0}

def analyze_chat_sentiment(messages):
    """Chat kayfiyatini tahlil qilish"""
    positive_words = ['ajoyib', 'yaxshi', 'zo\'r', 'mukammal', 'rahmat', 'good', 'great', 'excellent']
    negative_words = ['yomon', 'xato', 'muammo', 'noto\'g\'ri', 'bad', 'error', 'problem']
    
    text = " ".join([m['content'].lower() for m in messages])
    
    positive_count = sum([text.count(word) for word in positive_words])
    negative_count = sum([text.count(word) for word in negative_words])
    
    if positive_count > negative_count:
        return "😊 Ijobiy", positive_count
    elif negative_count > positive_count:
        return "😔 Salbiy", negative_count
    else:
        return "😐 Neytral", 0

def export_chat_history(messages, username):
    """Chatni eksport qilish (JSON, TXT, PDF)"""
    chat_text = f"Somo AI Chat History - {username}\n"
    chat_text += f"Eksport sanasi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    chat_text += "="*60 + "\n\n"
    
    for msg in messages:
        role = "👤 Siz" if msg['role'] == 'user' else "🤖 Somo AI"
        chat_text += f"{role}:\n{msg['content']}\n\n"
        chat_text += "-"*60 + "\n\n"
    
    return chat_text

# --- 📂 5. FAYL TAHLILI (KENGAYTIRILGAN) ---
def process_doc(file):
    """PDF va DOCX fayllarni tahlil qilish"""
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            
            # PDF meta ma'lumotlarini qo'shish
            metadata = reader.metadata
            meta_info = f"\n\n📋 Fayl ma'lumotlari:\n"
            meta_info += f"- Sahifalar: {len(reader.pages)}\n"
            if metadata.get('/Title'):
                meta_info += f"- Sarlavha: {metadata['/Title']}\n"
            if metadata.get('/Author'):
                meta_info += f"- Muallif: {metadata['/Author']}\n"
            
            return text + meta_info
            
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            result = mammoth.extract_raw_text(file)
            text = result.value
            
            # Statistika
            words = len(text.split())
            chars = len(text)
            
            meta_info = f"\n\n📋 Fayl ma'lumotlari:\n"
            meta_info += f"- So'zlar: {words}\n"
            meta_info += f"- Belgilar: {chars}\n"
            
            return text + meta_info
            
    except Exception as e:
        return f"⚠️ Faylni o'qishda xato: {str(e)}"
    
    return ""

def analyze_document(text):
    """Hujjatni chuqur tahlil qilish"""
    words = text.split()
    
    analysis = {
        "so'zlar_soni": len(words),
        "belgilar_soni": len(text),
        "paragraflar": text.count('\n\n') + 1,
        "eng_ko'p_so'z": Counter(words).most_common(10),
        "o'rtacha_so'z_uzunligi": sum(len(w) for w in words) / len(words) if words else 0
    }
    
    return analysis

# --- 🔐 6. LOGIN, RO'YXATDAN O'TISH VA ADMIN BLOK ---
if 'logged_in' not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user:
        recs = user_db.get_all_records()
        user_data = next((r for r in recs if str(r['username']) == session_user), None)
        if user_data and str(user_data.get('status')).lower() == 'active':
            st.session_state.username = session_user
            st.session_state.logged_in = True
            save_analytics(session_user, "Auto Login", "Cookie session")
        else:
            st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

def logout():
    save_analytics(st.session_state.username, "Logout")
    cookies["somo_user_session"] = ""
    cookies.save()
    st.session_state.clear()
    st.rerun()

def check_password_strength(password):
    """Parol kuchini tekshirish"""
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Kamida 8 ta belgi")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Katta harf")
    
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Kichik harf")
    
    if re.search(r'[0-9]', password):
        score += 1
    else:
        feedback.append("Raqam")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Maxsus belgi")
    
    strength = ["❌ Juda zaif", "⚠️ Zaif", "🟡 O'rtacha", "🟢 Yaxshi", "✅ Kuchli"][min(score, 4)]
    
    return strength, feedback

# --- LOGIN SAHIFASI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; margin-top:50px;'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: #64748b; font-size: 18px;'>Professional Sun'iy Intellekt Yordamchisi</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([0.1, 1, 0.1])
    with c2:
        auth_tab1, auth_tab2 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish"])
        
        with auth_tab1:
            u_in = st.text_input("👤 Username", key="login_u", placeholder="Username kiriting")
            p_in = st.text_input("🔑 Parol", type='password', key="login_p", placeholder="Parolni kiriting")
            
            col1, col2 = st.columns(2)
            with col1:
                remember_me = st.checkbox("Meni eslab qol", value=True)
            
            if st.button("🚀 Kirish", use_container_width=True, type="primary"):
                if not u_in or not p_in:
                    st.error("❌ Barcha maydonlarni to'ldiring!")
                else:
                    recs = user_db.get_all_records()
                    hp = hashlib.sha256(p_in.encode()).hexdigest()
                    user = next((r for r in recs if str(r['username']) == u_in and str(r['password']) == hp), None)
                    
                    if user:
                        if str(user.get('status')).lower() == 'blocked':
                            st.error("🚫 Sizning hisobingiz bloklangan! Admin bilan bog'laning.")
                        else:
                            st.session_state.username = u_in
                            st.session_state.logged_in = True
                            if remember_me:
                                cookies["somo_user_session"] = u_in
                                cookies.save()
                            save_analytics(u_in, "Login", "Successful")
                            st.success("✅ Muvaffaqiyatli kirdingiz!")
                            st.rerun()
                    else:
                        st.error("❌ Login yoki parol xato!")
                        save_analytics(u_in, "Failed Login", "Invalid credentials")
        
        with auth_tab2:
            nu = st.text_input("👤 Yangi Username", key="reg_u", placeholder="Username tanlang")
            np = st.text_input("🔑 Yangi Parol", type='password', key="reg_p", placeholder="Kuchli parol kiriting")
            
            # Parol kuchini ko'rsatish
            if np:
                strength, feedback = check_password_strength(np)
                st.info(f"Parol kuchi: {strength}")
                if feedback:
                    st.caption("Qo'shish kerak: " + ", ".join(feedback))
            
            nc = st.text_input("🔑 Parolni tasdiqlang", type='password', key="reg_c", placeholder="Parolni qayta kiriting")
            
            agree = st.checkbox("Men foydalanish shartlarini qabul qilaman")
            
            if st.button("✨ Hisob yaratish", use_container_width=True, type="primary"):
                if not nu or not np or not nc:
                    st.error("❌ Barcha maydonlarni to'ldiring!")
                elif np != nc:
                    st.error("❌ Parollar mos kelmadi!")
                elif not agree:
                    st.error("❌ Foydalanish shartlarini qabul qiling!")
                else:
                    recs = user_db.get_all_records()
                    if any(r['username'] == nu for r in recs):
                        st.error("❌ Bu username band!")
                    else:
                        hp = hashlib.sha256(np.encode()).hexdigest()
                        user_db.append_row([nu, hp, "active", str(datetime.now())])
                        save_analytics(nu, "Registration", "New user")
                        st.success("✅ Hisob yaratildi! Endi Kirish bo'limiga o'ting.")
                        st.balloons()
    
    # Footer
    st.markdown("<br>"*3, unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: #94a3b8;'>© 2026 Somo AI | Yaratuvchi: Usmonov Sodiq</p>", unsafe_allow_html=True)
    st.stop()

# --- 🚀 7. ASOSIY INTERFEYS ---
if "messages" not in st.session_state: 
    st.session_state.messages = []
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "🧠 Oddiy"
if "model" not in st.session_state:
    st.session_state.model = "llama-3.3-70b-versatile"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.6

# --- SIDEBAR ---
with st.sidebar:
    # User profili
    st.markdown(f"""
        <div style='text-align: center; padding: 10px;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #6366f1); width: 75px; height: 75px; border-radius: 50%; margin: 0 auto; line-height: 75px; font-size: 32px; color: white; font-weight: bold; border: 3px solid white; box-shadow: 0 5px 15px rgba(14, 165, 233, 0.3);'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='margin-top: 10px; color: #0f172a;'>{st.session_state.username}</h3>
            <p style='color: #64748b; font-size: 14px;'>Premium Foydalanuvchi</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Statistika
    stats = get_user_stats(st.session_state.username)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💬", stats['messages'], delta=None)
    with col2:
        st.metric("📄", stats['documents'], delta=None)
    with col3:
        st.metric("📅", stats['sessions'], delta=None)
    
    st.markdown("---")
    
    # Chat sozlamalari
    with st.expander("⚙️ Sozlamalar", expanded=False):
        st.session_state.model = st.selectbox(
            "Model tanlang:",
            ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
            index=0
        )
        
        st.session_state.temperature = st.slider(
            "Temperature (ijodkorlik darajasi):",
            0.0, 1.0, 0.6, 0.1
        )
        
        st.session_state.chat_mode = st.radio(
            "Chat rejimi:",
            ["🧠 Oddiy", "📚 Ta'limiy", "💼 Professional", "🎨 Ijodiy"],
            index=0
        )
    
    # Chat amaliyotlari
    st.markdown("### 🛠 Chat Amaliyotlari")
    
    if st.button("🗑 Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        save_analytics(st.session_state.username, "Clear Chat")
        st.rerun()
    
    if st.button("💾 Chatni saqlash", use_container_width=True):
        if st.session_state.messages:
            chat_export = export_chat_history(st.session_state.messages, st.session_state.username)
            st.download_button(
                label="📥 Yuklab olish (TXT)",
                data=chat_export,
                file_name=f"somo_chat_{st.session_state.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            save_analytics(st.session_state.username, "Export Chat")
        else:
            st.warning("Chat bo'sh!")
    
    # Sentiment analizi
    if st.session_state.messages:
        sentiment, count = analyze_chat_sentiment(st.session_state.messages)
        st.info(f"📊 Chat kayfiyati: {sentiment}")
    
    st.markdown("---")
    
    # Hujjatlar tahlili
    st.markdown("### 📂 Hujjatlar")
    f_up = st.file_uploader("Faylni tanlang", type=["pdf", "docx"], label_visibility="collapsed")
    f_txt = ""
    
    if f_up:
        with st.spinner("Fayl tahlil qilinmoqda..."):
            f_txt = process_doc(f_up)
            if f_txt:
                st.success("✅ Fayl yuklandi va tahlil qilindi!")
                
                # Hujjat statistikasi
                with st.expander("📊 Hujjat statistikasi"):
                    doc_analysis = analyze_document(f_txt)
                    st.write(f"**So'zlar:** {doc_analysis['so'zlar_soni']}")
                    st.write(f"**Belgilar:** {doc_analysis['belgilar_soni']}")
                    st.write(f"**Paragraflar:** {doc_analysis['paragraflar']}")
                    
                save_analytics(st.session_state.username, "Document Upload", f_up.name)
            else:
                st.error("❌ Faylni o'qib bo'lmadi")
    
    st.markdown("<br>"*8, unsafe_allow_html=True)
    
    # Tizimdan chiqish
    if st.button("🚪 Tizimdan chiqish", use_container_width=True, type="secondary"):
        logout()

# --- ASOSIY DASHBOARD ---
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center;'>Salom, <span class='gradient-text'>{st.session_state.username}</span>! 👋</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 18px;'>Bugun sizga qanday yordam bera olaman?</p>", unsafe_allow_html=True)
    
    # Qulaylik tugmalari
    st.markdown("### 🚀 Tezkor harakatlar")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Maqola yozish", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Menga professional maqola yozishda yordam ber"
            })
            st.rerun()
    
    with col2:
        if st.button("💻 Kod yozish", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Python dasturlashda yordam ber"
            })
            st.rerun()
    
    with col3:
        if st.button("🧮 Matematik tahlil", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Murakkab matematik masalani yechishda yordam ber"
            })
            st.rerun()
    
    with col4:
        if st.button("🌐 Tarjima qilish", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Matn tarjimasida yordam ber"
            })
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Dashboard kartochkalari
    st.markdown("""
        <div class='dashboard-container'>
            <div class='card-box'>
                <h1>🧠</h1>
                <h3>Aqlli Tahlil</h3>
                <p>Murakkab mantiq va matematik masalalarni yechish</p>
            </div>
            <div class='card-box'>
                <h1>📄</h1>
                <h3>Hujjatlar</h3>
                <p>PDF va Word fayllarni chuqur tahlil qilish</p>
            </div>
            <div class='card-box'>
                <h1>🎨</h1>
                <h3>Ijodkorlik</h3>
                <p>G'oyalar yaratish va mukammal kod yozish</p>
            </div>
            <div class='card-box'>
                <h1>🌍</h1>
                <h3>Ko'p tilli</h3>
                <p>50+ tilda professional muloqot</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Qo'shimcha ma'lumotlar
    st.markdown("<br>"*2, unsafe_allow_html=True)
    
    # Foydali maslahatlar
    with st.expander("💡 Foydali maslahatlar"):
        st.markdown("""
        **Somo AI bilan samarali ishlash:**
        - 📝 Aniq va batafsil savollar bering
        - 📄 Hujjatlarni yuklang va tahlil qildiring
        - 🔧 Sozlamalarda modelni o'zgartiring
        - 💾 Muhim chatlarni saqlashni unutmang
        - 🎯 Maxsus rejimlardan foydalaning
        """)
    
    # Yangiliklar
    with st.expander("🆕 So'nggi yangiliklar"):
        st.markdown("""
        - ✨ Yangi Llama 3.3 70B modeli
        - 📊 Chat statistikasi va sentiment analiz
        - 💾 Chatni eksport qilish funksiyasi
        - 🎨 Yangilangan UI/UX dizayni
        - ⚙️ Kengaytirilgan sozlamalar
        """)

# --- CHAT TARIXI ---
for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(m["content"], unsafe_allow_html=True)
        
        # Assistant javoblariga qo'shimcha tugmalar
        if m["role"] == "assistant" and i == len(st.session_state.messages) - 1:
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                if st.button("👍", key=f"like_{i}"):
                    save_analytics(st.session_state.username, "Liked Message", m["content"][:50])
                    st.toast("Rahmat!")
            with col2:
                if st.button("📋", key=f"copy_{i}"):
                    st.toast("Javob nusxalandi!")

# --- CHAT INPUT ---
if pr := st.chat_input("💬 Somo AI ga xabar yuboring..."):
    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # User xabari
    st.session_state.messages.append({"role": "user", "content": pr})
    with st.chat_message("user"):
        st.markdown(pr)
    
    if chat_db:
        chat_db.append_row([time_stamp, st.session_state.username, "User", pr])
    
    save_analytics(st.session_state.username, "Message Sent", pr[:50])
    
    # Assistant javobi
    with st.chat_message("assistant"):
        with st.spinner("O'ylayapman..."):
            try:
                # System instruction - chat rejimiga qarab
                mode_instructions = {
                    "🧠 Oddiy": "Professional va tushunarli javob ber.",
                    "📚 Ta'limiy": "Ta'limiy va batafsil tushuntirish ber. Misollar keltir.",
                    "💼 Professional": "Professional va rasmiy uslubda javob ber.",
                    "🎨 Ijodiy": "Ijodiy va qiziqarli yondashuvda javob ber."
                }
                
                base_instruction = (
                    f"Isming Somo AI. Yaratuvching Usmonov Sodiq. "
                    f"{mode_instructions[st.session_state.chat_mode]} "
                    f"Matematikani LaTeX ($...$) formatida yoz. "
                    f"Kod bloklarini markdown formatida taqdim et."
                )
                
                msgs = [{"role": "system", "content": base_instruction}]
                
                # Hujjat qo'shish
                if f_txt:
                    msgs.append({
                        "role": "system",
                        "content": f"📄 Yuklangan hujjat:\n{f_txt[:4000]}"
                    })
                
                # Xotira - oxirgi 15 ta xabar
                for old in st.session_state.messages[-15:]:
                    msgs.append(old)
                
                # API chaqiruvi
                response = client.chat.completions.create(
                    messages=msgs,
                    model=st.session_state.model,
                    temperature=st.session_state.temperature,
                    max_tokens=4096,
                    stream=False
                )
                
                res = response.choices[0].message.content
                
                # Javobni ko'rsatish
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
                
                # Bazaga saqlash
                if chat_db:
                    chat_db.append_row([time_stamp, "Somo AI", "Assistant", res[:500]])
                
                save_analytics(st.session_state.username, "Message Received", "AI Response")
                
            except Exception as e:
                error_msg = f"❌ Xatolik yuz berdi: {str(e)}"
                st.error(error_msg)
                save_analytics(st.session_state.username, "Error", str(e))

# --- FOOTER ---
st.markdown("<br>"*2, unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color: #94a3b8; font-size: 14px;'>"
    "© 2026 Somo AI Infinity | Powered by Groq & Llama 3.3 | Yaratuvchi: Usmonov Sodiq"
    "</p>", 
    unsafe_allow_html=True
)
