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

    /* SIDEBAR - MUKAMMAL GRADIENT */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e0f2fe 0%, #bae6fd 100%) !important;
        border-right: 3px solid #7dd3fc;
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
        padding: 12px !important;
        margin: 5px 0 !important;
    }
    div[data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
        color: white !important;
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(14, 165, 233, 0.4);
    }

    /* DASHBOARD KARTALARI */
    .dashboard-container {
        display: flex;
        flex-wrap: wrap;
        gap: 25px;
        justify-content: center;
        margin-top: 30px;
        padding: 20px;
    }
    
    .card-box {
        background: white;
        border-radius: 20px;
        padding: 35px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 2px solid #e2e8f0;
        transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        flex: 1;
        min-width: 280px;
        max-width: 380px;
        cursor: pointer;
    }
    
    .card-box:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(14, 165, 233, 0.2);
        border-color: #0ea5e9;
    }

    /* 📱 MOBIL OPTIMIZATSIYA */
    @media (max-width: 768px) {
        .card-box {
            min-width: 150px !important;
            padding: 20px !important;
            margin-bottom: 15px !important;
        }
        .card-box h1 { font-size: 28px !important; }
        .card-box h3 { font-size: 17px !important; }
        .card-box p { font-size: 13px !important; }
        h1 { font-size: 26px !important; }
    }

    .gradient-text {
        background: linear-gradient(90deg, #0284c7, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        animation: gradient-shift 3s ease infinite;
    }
    
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Login Tablar */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 20px; 
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background: white;
        border-radius: 12px 12px 0 0;
        padding: 0 25px;
        border: 2px solid #e2e8f0;
        transition: 0.3s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #f1f5f9;
        border-color: #0ea5e9;
    }
    
    /* Chat xabarlari */
    .stChatMessage {
        background: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Input maydoni */
    .stChatInputContainer {
        border-top: 2px solid #e2e8f0;
        background: white;
        padding: 15px;
    }
    
    /* Statistika kartalari */
    .stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 15px;
        padding: 20px;
        border-left: 4px solid #0ea5e9;
        margin: 10px 0;
    }
    
    /* Loading animatsiya */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    </style>
""", unsafe_allow_html=True)

# --- 🔗 3. BAZA VA AI ALOQASI ---
@st.cache_resource
def get_connections():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds", 
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], 
            scope
        )
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        return ss.sheet1, ss.worksheet("ChatHistory")
    except Exception as e:
        st.error(f"❌ Baza bilan aloqa xatosi: {str(e)}")
        return None, None

user_db, chat_db = get_connections()

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"❌ AI bilan aloqa xatosi: {str(e)}")
    client = None

# --- 📂 4. FAYL TAHLILI (YAXSHILANGAN) ---
def process_doc(file):
    """PDF va DOCX fayllarni tahlil qilish"""
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
        else:
            return ""
    except Exception as e:
        st.error(f"❌ Fayl tahlili xatosi: {str(e)}")
        return ""

# --- 🔐 5. LOGIN, RO'YXATDAN O'TISH VA SESSION ---
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

def logout():
    """Tizimdan chiqish"""
    cookies["somo_user_session"] = ""
    cookies.save()
    st.session_state.clear()
    st.rerun()

# --- 🔒 LOGIN SAHIFASI ---
if not st.session_state.logged_in:
    st.markdown("""
        <h1 style='text-align:center; margin-top:60px; font-size: 48px;'>
            🌌 Somo AI <span class='gradient-text'>Infinity</span>
        </h1>
        <p style='text-align:center; color: #64748b; font-size: 18px; margin-bottom: 40px;'>
            Kelajak texnologiyalari bilan tanishing
        </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.2, 1, 0.2])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish"])
        
        with auth_tab1:
            with st.form("login_form"):
                u_in = st.text_input("👤 Username", placeholder="Username kiriting")
                p_in = st.text_input("🔑 Parol", type='password', placeholder="Parol kiriting")
                submitted = st.form_submit_button("🚀 Kirish", use_container_width=True)
                
                if submitted and u_in and p_in:
                    if user_db:
                        try:
                            recs = user_db.get_all_records()
                            hp = hashlib.sha256(p_in.encode()).hexdigest()
                            user = next((r for r in recs if str(r['username']) == u_in and str(r['password']) == hp), None)
                            
                            if user:
                                if str(user.get('status')).lower() == 'blocked':
                                    st.error("🚫 Sizning hisobingiz bloklangan! Admin bilan bog'laning.")
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
            with st.form("register_form"):
                nu = st.text_input("👤 Yangi Username", placeholder="Username tanlang")
                np = st.text_input("🔑 Yangi Parol", type='password', placeholder="Parol yarating")
                np_confirm = st.text_input("🔑 Parolni tasdiqlang", type='password', placeholder="Parolni qayta kiriting")
                submitted = st.form_submit_button("✨ Hisob yaratish", use_container_width=True)
                
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
                                st.error("❌ Bu username band! Boshqasini tanlang.")
                            else:
                                hp = hashlib.sha256(np.encode()).hexdigest()
                                user_db.append_row([nu, hp, "active", str(datetime.now())])
                                st.success("✅ Muvaffaqiyatli ro'yxatdan o'tdingiz! Endi Kirish bo'limiga o'ting.")
                        except Exception as e:
                            st.error(f"❌ Xatolik: {str(e)}")
    
    st.markdown("""
        <div style='text-align:center; margin-top:50px; color: #94a3b8;'>
            <p>© 2026 Somo AI | Yaratuvchi: Usmonov Sodiq</p>
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
        <div style='text-align: center; padding: 15px; margin-bottom: 20px;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #6366f1); width: 80px; height: 80px; border-radius: 50%; margin: 0 auto; line-height: 80px; font-size: 36px; color: white; font-weight: bold; border: 4px solid white; box-shadow: 0 5px 15px rgba(0,0,0,0.2);'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='margin-top: 15px; color: #0f172a;'>{st.session_state.username}</h3>
            <p style='color: #64748b; font-size: 14px;'>🟢 Onlayn</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Statistika
    st.markdown("### 📊 Statistika")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💬 Xabarlar", len(st.session_state.messages))
    with col2:
        if 'login_time' in st.session_state:
            session_duration = (datetime.now() - st.session_state.login_time).seconds // 60
            st.metric("⏱ Sessiya", f"{session_duration} daqiqa")
    
    st.markdown("---")
    
    # Chat boshqaruvi
    st.markdown("### 🎛 Boshqaruv")
    if st.button("🗑 Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.success("✅ Chat tozalandi!")
        st.rerun()
    
    if st.button("📥 Chatni yuklab olish", use_container_width=True):
        if st.session_state.messages:
            chat_export = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
            st.download_button(
                label="💾 JSON formatda",
                data=chat_export,
                file_name=f"somo_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

    st.markdown("---")
    
    # Fayl yuklash
    st.markdown("### 📂 Hujjatlar")
    f_up = st.file_uploader(
        "PDF yoki DOCX yuklang", 
        type=["pdf", "docx"], 
        label_visibility="collapsed"
    )
    f_txt = process_doc(f_up) if f_up else ""
    if f_up:
        st.success(f"✅ {f_up.name} yuklandi")
        st.info(f"📄 Hajmi: {len(f_txt)} ta belgi")

    st.markdown("---")
    
    # Model sozlamalari
    st.markdown("### ⚙️ Sozlamalar")
    temperature = st.slider("🌡 Ijodkorlik darajasi", 0.0, 1.0, 0.6, 0.1)
    st.caption("Pastroq - aniqroq, yuqoriroq - ijodiyroq")
    
    st.markdown("<br>"*5, unsafe_allow_html=True)
    
    if st.button("🚪 Tizimdan chiqish", use_container_width=True):
        logout()

# --- 🎨 DASHBOARD (XABARLAR BO'LMASA) ---
if not st.session_state.messages:
    st.markdown(f"""
        <h1 style='text-align: center; margin-bottom: 10px;'>
            Salom, <span class='gradient-text'>{st.session_state.username}</span>! 👋
        </h1>
        <p style='text-align: center; color: #64748b; font-size: 18px; margin-bottom: 30px;'>
            Bugun qanday yordam bera olaman?
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class='dashboard-container'>
            <div class='card-box'>
                <h1>🧠</h1>
                <h3>Aqlli Tahlil</h3>
                <p>Murakkab mantiq, matematika va muammolarni yechish</p>
            </div>
            <div class='card-box'>
                <h1>📄</h1>
                <h3>Hujjatlar</h3>
                <p>PDF va Word fayllarni tahlil qilish va xulosalar</p>
            </div>
            <div class='card-box'>
                <h1>🎨</h1>
                <h3>Ijodkorlik</h3>
                <p>G'oyalar, kod yozish va kreativ yechimlar</p>
            </div>
            <div class='card-box'>
                <h1>🌐</h1>
                <h3>Tillar</h3>
                <p>O'zbek, Ingliz, Rus va boshqa tillarda muloqot</p>
            </div>
            <div class='card-box'>
                <h1>💡</h1>
                <h3>Maslahatlar</h3>
                <p>Har qanday sohadagi professional maslahatlar</p>
            </div>
            <div class='card-box'>
                <h1>📚</h1>
                <h3>Ta'lim</h3>
                <p>Tushuntirish, o'qitish va bilim berish</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; color: #94a3b8;'>
            <p>💡 Maslahat: Pastdagi chat oynasiga savolingizni yozing yoki fayl yuklang</p>
        </div>
    """, unsafe_allow_html=True)

# --- 💬 CHAT TARIXI ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- ✍️ YANGI XABAR INPUT ---
if pr := st.chat_input("💭 Somo AI ga xabar yuboring..."):
    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # User xabarini qo'shish
    st.session_state.messages.append({"role": "user", "content": pr})
    with st.chat_message("user"):
        st.markdown(pr)
    
    # Bazaga saqlash
    if chat_db:
        try:
            chat_db.append_row([time_stamp, st.session_state.username, "User", pr])
        except:
            pass
    
    # AI javobi
    with st.chat_message("assistant"):
        with st.spinner("🤔 O'ylayapman..."):
            try:
                # System instruction
                sys_instr = f"""Sening isming Somo AI. Seni Usmonov Sodiq yaratgan. 
                Sen professional, samimiy va foydali yordamchi sun'iy intellektsан. 
                Har doim aniq, tushunarli va to'liq javoblar berasan.
                Matematika formulalarini LaTeX formatida ($...$) yoz.
                Kod yozishda eng yaxshi amaliyotlardan foydalangan.
                Foydalanuvchi bilan samimiy muloqot qil."""
                
                # Xabarlar tarixini tayyorlash
                msgs = [{"role": "system", "content": sys_instr}]
                
                # Fayl mazmuni qo'shish
                if f_txt:
                    msgs.append({
                        "role": "system", 
                        "content": f"Yuklangan hujjat mazmuni (birinchi 4000 ta belgi):\n\n{f_txt[:4000]}"
                    })
                
                # Oxirgi 15 ta xabarni qo'shish (xotira tejash uchun)
                for old in st.session_state.messages[-15:]:
                    msgs.append(old)
                
                # AI javobini olish
                if client:
                    response = client.chat.completions.create(
                        messages=msgs,
                        model="llama-3.3-70b-versatile",
                        temperature=temperature,
                        max_tokens=2048
                    )
                    
                    res = response.choices[0].message.content
                    
                    # Javobni ko'rsatish
                    st.markdown(res)
                    
                    # Sessiyaga saqlash
                    st.session_state.messages.append({"role": "assistant", "content": res})
                    st.session_state.total_messages += 1
                    
                    # Bazaga saqlash
                    if chat_db:
                        try:
                            chat_db.append_row([time_stamp, "Somo AI", "Assistant", res])
                        except:
                            pass
                else:
                    st.error("❌ AI xizmati ishlamayapti. Iltimos, keyinroq urinib ko'ring.")
                    
            except Exception as e:
                error_msg = f"❌ Xatolik yuz berdi: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# --- 📌 FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align:center; color: #94a3b8; padding: 20px; border-top: 1px solid #e2e8f0;'>
        <p style='margin: 5px 0;'>🌌 <strong>Somo AI Infinity</strong> | Powered by Groq & Llama 3.3</p>
        <p style='margin: 5px 0;'>👨‍💻 Yaratuvchi: <strong>Usmonov Sodiq</strong></p>
        <p style='margin: 5px 0; font-size: 12px;'>© 2026 Barcha huquqlar himoyalangan</p>
    </div>
""", unsafe_allow_html=True)
