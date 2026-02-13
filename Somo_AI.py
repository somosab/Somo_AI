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
import time

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

st.markdown("""
    <style>
    /* Umumiy fon - Premium gradient */
    .stApp { 
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 50%, #ddd6fe 100%) !important;
    }

    /* BURCHAKDAGI MATNLARNI YO'QOTISH */
    [data-testid="stSidebarNav"] { display: none !important; }
    .st-emotion-cache-1vt458p, .st-emotion-cache-k77z8z, .st-emotion-cache-12fmjuu { 
        font-size: 0px !important; 
        color: transparent !important;
    }

    /* SIDEBAR - MUKAMMAL GRADIENT */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e0f2fe 0%, #bae6fd 50%, #c7d2fe 100%) !important;
        border-right: 3px solid #7dd3fc;
    }
    [data-testid="stSidebar"] section, [data-testid="stSidebar"] .stVerticalBlock {
        background: transparent !important;
    }

    /* SIDEBAR TUGMALARI - Premium ko'rinish */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        color: #0284c7 !important;
        border: 2px solid #0ea5e9 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100% !important;
        padding: 12px !important;
        margin: 5px 0 !important;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.15);
    }
    div[data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
        color: white !important;
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(14, 165, 233, 0.4);
    }

    /* DASHBOARD KARTALARI - 3D effekt */
    .dashboard-container {
        display: flex;
        flex-wrap: wrap;
        gap: 25px;
        justify-content: center;
        margin-top: 30px;
        padding: 20px;
    }
    
    .card-box {
        background: linear-gradient(145deg, #ffffff, #f1f5f9);
        border-radius: 20px;
        padding: 35px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08), 0 1px 8px rgba(0,0,0,0.05);
        border: 2px solid #e2e8f0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        flex: 1;
        min-width: 280px;
        max-width: 380px;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .card-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.1), transparent);
        transition: 0.5s;
    }
    
    .card-box:hover::before {
        left: 100%;
    }
    
    .card-box:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 20px 40px rgba(14, 165, 233, 0.25);
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

    /* Gradient matn - animatsiya bilan */
    .gradient-text {
        background: linear-gradient(90deg, #0284c7, #6366f1, #8b5cf6, #ec4899);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        animation: gradient-shift 4s ease infinite;
    }
    
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Login Tablar - Premium */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 20px; 
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border-radius: 12px 12px 0 0;
        padding: 0 25px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(145deg, #f1f5f9, #e2e8f0);
        border-color: #0ea5e9;
        transform: translateY(-2px);
    }
    
    /* Chat xabarlari - Premium */
    .stChatMessage {
        background: linear-gradient(145deg, #ffffff, #fafafa);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
    }
    
    /* Input maydoni - Premium */
    .stChatInputContainer {
        border-top: 2px solid #e2e8f0;
        background: linear-gradient(180deg, #ffffff, #f8fafc);
        padding: 15px;
        box-shadow: 0 -4px 15px rgba(0,0,0,0.05);
    }
    
    /* Statistika kartalari */
    .stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 15px;
        padding: 20px;
        border-left: 4px solid #0ea5e9;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Feedback forma */
    .feedback-box {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 2px solid #e2e8f0;
    }
    
    /* Yulduzlar reytingi */
    .star-rating {
        font-size: 32px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .star-rating:hover {
        transform: scale(1.2);
    }
    
    /* Loading animatsiya */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Success message */
    .success-message {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 15px 25px;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f0f9ff);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 2px solid #bae6fd;
        transition: 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(14, 165, 233, 0.2);
    }
    
    /* Templates section */
    .template-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    .template-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        border: 2px solid #e2e8f0;
        transition: 0.3s;
        cursor: pointer;
    }
    .template-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(99, 102, 241, 0.2);
        border-color: #6366f1;
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
        user_sheet = ss.sheet1
        chat_sheet = ss.worksheet("ChatHistory")
        
        # Feedback sheet yaratish (agar mavjud bo'lmasa)
        try:
            feedback_sheet = ss.worksheet("Letters")
        except:
            feedback_sheet = ss.add_worksheet(title="Letters", rows="1000", cols="10")
            feedback_sheet.append_row(["Timestamp", "Username", "Rating", "Category", "Message", "Email", "Status"])
        
        return user_sheet, chat_sheet, feedback_sheet
    except Exception as e:
        st.error(f"❌ Baza xatosi: {str(e)}")
        return None, None, None

user_db, chat_db, feedback_db = get_connections()

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
        st.warning(f"⚠️ Fayl o'qishda xatolik: {str(e)}")
        return ""
    return ""

# --- 🎯 5. SHABLONLAR BAZASI (3 TA KATEGORIYA) ---
TEMPLATES = {
    "Biznes": [
        {
            "title": "📊 Biznes Reja",
            "icon": "📊",
            "prompt": "Menga [kompaniya nomi] uchun professional biznes reja tuzing. Quyidagilarni kiriting:\n- Ijroiya xulosasi\n- Bozor tahlili\n- Marketing strategiyasi\n- Moliyaviy rejalar\n- 5 yillik prognoz",
            "description": "To'liq biznes reja yaratish"
        }
    ],
    "Dasturlash": [
        {
            "title": "💻 Kod Generator",
            "icon": "💻",
            "prompt": "[dasturlash tili]da [funksionallik] uchun kod yoz:\n- Clean code prinsiplari\n- Izohlar bilan\n- Error handling\n- Best practices\n- Test misollari",
            "description": "Har qanday tildagi kod"
        }
    ],
    "Ta'lim": [
        {
            "title": "📖 Dars Rejasi",
            "icon": "📖",
            "prompt": "[mavzu] bo'yicha to'liq dars rejasi tuzing:\n- O'quv maqsadlari\n- Kirish (10 daqiqa)\n- Asosiy qism (30 daqiqa)\n- Amaliy mashqlar (15 daqiqa)\n- Yakun (5 daqiqa)\n- Uyga vazifa",
            "description": "O'qituvchilar uchun"
        }
    ]
}

# --- 🔐 6. SESSION BOSHQARUVI ---
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
    """Tizimdan chiqish"""
    try:
        cookies["somo_user_session"] = ""
        cookies.save()
    except:
        pass
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.logged_in = False
    st.rerun()

# --- 🔒 7. LOGIN SAHIFASI ---
if not st.session_state.logged_in:
    # Header animatsiya bilan
    st.markdown("""
        <div style='text-align:center; margin-top:60px;'>
            <h1 style='font-size: 56px; margin-bottom: 10px;'>
                🌌 Somo AI <span class='gradient-text'>Infinity</span>
            </h1>
            <p style='color: #64748b; font-size: 20px; margin-bottom: 15px;'>
                Kelajak texnologiyalari bilan tanishing
            </p>
            <p style='color: #94a3b8; font-size: 16px;'>
                ⚡ 70B parametrli AI | 🚀 Real-time javoblar | 📄 Hujjat tahlili
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.25, 1, 0.25])
    with col2:
        auth_tab1, auth_tab2, auth_tab3 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish", "ℹ️ Ma'lumot"])
        
        with auth_tab1:
            with st.form("login_form"):
                st.markdown("### 🔐 Hisobingizga kiring")
                u_in = st.text_input("👤 Username", placeholder="Username kiriting", key="login_user")
                p_in = st.text_input("🔑 Parol", type='password', placeholder="Parol kiriting", key="login_pass")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submitted = st.form_submit_button("🚀 Kirish", use_container_width=True)
                with col_b:
                    remember = st.checkbox("✅ Eslab qolish", value=True)
                
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
                                    if remember:
                                        cookies["somo_user_session"] = u_in
                                        cookies.save()
                                    st.success("✅ Muvaffaqiyatli kirish!")
                                    time.sleep(0.5)
                                    st.rerun()
                            else:
                                st.error("❌ Login yoki parol xato!")
                        except Exception as e:
                            st.error(f"❌ Xatolik: {str(e)}")
        
        with auth_tab2:
            with st.form("register_form"):
                st.markdown("### ✨ Yangi hisob yaratish")
                nu = st.text_input("👤 Username", placeholder="Username tanlang (kamida 3 ta belgi)", key="reg_user")
                np = st.text_input("🔑 Parol", type='password', placeholder="Parol yarating (kamida 6 ta belgi)", key="reg_pass")
                np_confirm = st.text_input("🔑 Parolni tasdiqlang", type='password', placeholder="Parolni qayta kiriting", key="reg_pass_confirm")
                
                agree = st.checkbox("Men foydalanish shartlariga roziman")
                submitted = st.form_submit_button("✨ Hisob yaratish", use_container_width=True)
                
                if submitted:
                    if not agree:
                        st.error("❌ Foydalanish shartlariga rozilik bering!")
                    elif not nu or not np:
                        st.error("❌ Barcha maydonlarni to'ldiring!")
                    elif len(nu) < 3:
                        st.error("❌ Username kamida 3 ta belgidan iborat bo'lishi kerak!")
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
                                st.balloons()
                                st.success("🎉 Muvaffaqiyatli ro'yxatdan o'tdingiz! Endi Kirish bo'limiga o'ting.")
                        except Exception as e:
                            st.error(f"❌ Xatolik: {str(e)}")
        
        with auth_tab3:
            st.markdown("""
                ### 🌟 Somo AI Infinity haqida
                
                **Asosiy imkoniyatlar:**
                
                🧠 **Aqlli AI Yordamchi**
                - 70B parametrli Llama 3.3 model
                - Real-time javoblar
                - Ko'p tilda muloqot
                
                📄 **Hujjat Tahlili**
                - PDF va DOCX fayllarni tahlil qilish
                - Matnni umumlashtirish
                - Ma'lumot ajratib olish
                
                🎨 **Kreativlik Shablonlari**
                - 3 tayyor shablon
                - Biznes, Dasturlash, Ta'lim
                
                💬 **Chat Tarixi**
                - Barcha suhbatlar saqlanadi
                - Yuklab olish imkoniyati
                - Qidirish funksiyasi
                
                ⚙️ **Moslashtirilgan**
                - Ijodkorlik darajasi sozlamasi
                - Shaxsiy profil
                - Statistika
                
                ---
                
                📧 **Yordam:** support@somoai.uz  
                👨‍💻 **Yaratuvchi:** Usmonov Sodiq  
                📅 **Versiya:** 2.0 (2026)
            """)
    
    st.markdown("""
        <div style='text-align:center; margin-top:60px; color: #94a3b8;'>
            <p style='font-size: 14px;'>🔒 Ma'lumotlaringiz xavfsiz | 🌐 24/7 Onlayn</p>
            <p style='margin-top: 20px;'>© 2026 Somo AI | Barcha huquqlar himoyalangan</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- 🚀 8. ASOSIY INTERFEYS ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_messages" not in st.session_state:
    st.session_state.total_messages = 0
if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"

# --- 📊 9. SIDEBAR ---
with st.sidebar:
    # User profili - Premium dizayn
    st.markdown(f"""
        <div style='text-align: center; padding: 20px; margin-bottom: 25px; background: linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(99, 102, 241, 0.1)); border-radius: 20px;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #6366f1); width: 90px; height: 90px; border-radius: 50%; margin: 0 auto; line-height: 90px; font-size: 40px; color: white; font-weight: bold; border: 5px solid white; box-shadow: 0 8px 20px rgba(14, 165, 233, 0.3);'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='margin-top: 15px; color: #0f172a; font-size: 20px;'>{st.session_state.username}</h3>
            <p style='color: #10b981; font-size: 14px; font-weight: 600;'>🟢 Aktiv</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigatsiya tugmalari
    st.markdown("### 🧭 Navigatsiya")
    
    if st.button("💬 Chat", use_container_width=True, key="nav_chat"):
        st.session_state.current_page = "chat"
        st.rerun()
    
    if st.button("🎨 Shablonlar", use_container_width=True, key="nav_templates"):
        st.session_state.current_page = "templates"
        st.rerun()
    
    if st.button("💌 Fikr bildirish", use_container_width=True, key="nav_feedback"):
        st.session_state.current_page = "feedback"
        st.rerun()
    
    st.markdown("---")
    
    # Statistika
    st.markdown("### 📊 Statistika")
    
    # Metric cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class='metric-card'>
                <h4 style='color: #0284c7; margin: 0;'>💬</h4>
                <h2 style='margin: 5px 0; color: #0f172a;'>{}</h2>
                <p style='color: #64748b; margin: 0; font-size: 12px;'>Xabarlar</p>
            </div>
        """.format(len(st.session_state.messages)), unsafe_allow_html=True)
    
    with col2:
        if 'login_time' in st.session_state:
            session_duration = (datetime.now() - st.session_state.login_time).seconds // 60
            st.markdown("""
                <div class='metric-card'>
                    <h4 style='color: #6366f1; margin: 0;'>⏱</h4>
                    <h2 style='margin: 5px 0; color: #0f172a;'>{}</h2>
                    <p style='color: #64748b; margin: 0; font-size: 12px;'>Daqiqa</p>
                </div>
            """.format(session_duration), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Chat boshqaruvi (faqat chat sahifasida)
    if st.session_state.current_page == "chat":
        st.markdown("### 🎛 Boshqaruv")
        
        if st.button("🗑 Chatni tozalash", use_container_width=True, key="clear_chat"):
            st.session_state.messages = []
            st.success("✅ Chat tozalandi!")
            st.rerun()
        
        if st.session_state.messages:
            if st.button("📥 Yuklab olish", use_container_width=True, key="download_chat"):
                chat_export = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
                st.download_button(
                    label="💾 JSON formatda",
                    data=chat_export,
                    file_name=f"somo_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="download_json"
                )
    
        st.markdown("---")
        
        # Fayl yuklash
        st.markdown("### 📂 Hujjatlar")
        f_up = st.file_uploader(
            "PDF yoki DOCX", 
            type=["pdf", "docx"], 
            label_visibility="collapsed", 
            key="file_uploader",
            help="PDF yoki Word hujjatlarini tahlil qilish uchun yuklang"
        )
        
        if 'uploaded_file_text' not in st.session_state:
            st.session_state.uploaded_file_text = ""
        
        if f_up:
            with st.spinner("📄 Fayl tahlil qilinmoqda..."):
                f_txt = process_doc(f_up)
                st.session_state.uploaded_file_text = f_txt
            
            if f_txt:
                st.success(f"✅ {f_up.name}")
                st.info(f"📊 {len(f_txt):,} belgi tahlil qilindi")
            else:
                st.warning("⚠️ Fayl o'qilmadi")
        
        st.markdown("---")
        
        # Model sozlamalari
        st.markdown("### ⚙️ Sozlamalar")
        temperature = st.slider(
            "🌡 Ijodkorlik darajasi", 
            0.0, 1.0, 0.6, 0.1, 
            key="temp_slider",
            help="Past qiymat - aniqroq javoblar, yuqori qiymat - ijodiyroq javoblar"
        )
        
        if temperature < 0.3:
            st.caption("🎯 Aniq va faktlarga asoslangan")
        elif temperature < 0.7:
            st.caption("⚖️ Muvozanatli")
        else:
            st.caption("🎨 Ijodiy va noodatiy")
    
    st.markdown("<br>"*3, unsafe_allow_html=True)
    
    # Logout tugmasi
    if st.button("🚪 Tizimdan chiqish", use_container_width=True, key="logout_btn", type="primary"):
        handle_logout()

# --- 📄 10. SAHIFALAR ---

# CHAT SAHIFASI
if st.session_state.current_page == "chat":
    # Dashboard (xabarlar bo'lmasa)
    if not st.session_state.messages:
        st.markdown(f"""
            <div style='text-align: center; margin: 40px 0;'>
                <h1 style='font-size: 42px; margin-bottom: 15px;'>
                    Salom, <span class='gradient-text'>{st.session_state.username}</span>! 👋
                </h1>
                <p style='color: #64748b; font-size: 20px; margin-bottom: 40px;'>
                    Bugun sizga qanday yordam bera olaman?
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Premium dashboard cards - 3 ta
        st.markdown("""
            <div class='dashboard-container'>
                <div class='card-box'>
                    <h1 style='font-size: 48px; margin-bottom: 15px;'>🧠</h1>
                    <h3 style='color: #0f172a; margin-bottom: 10px;'>Aqlli Tahlil</h3>
                    <p style='color: #64748b; line-height: 1.6;'>Murakkab mantiq, matematika va muammolarni professional darajada yechish</p>
                </div>
                <div class='card-box'>
                    <h1 style='font-size: 48px; margin-bottom: 15px;'>📄</h1>
                    <h3 style='color: #0f172a; margin-bottom: 10px;'>Hujjatlar Tahlili</h3>
                    <p style='color: #64748b; line-height: 1.6;'>PDF va Word fayllarni tahlil qilish, umumlashtirish va xulosalar chiqarish</p>
                </div>
                <div class='card-box'>
                    <h1 style='font-size: 48px; margin-bottom: 15px;'>🎨</h1>
                    <h3 style='color: #0f172a; margin-bottom: 10px;'>Ijodkorlik</h3>
                    <p style='color: #64748b; line-height: 1.6;'>G'oyalar generatsiyasi, kod yozish va kreativ yechimlar ishlab chiqish</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Quick tips
        st.markdown("""
            <div style='text-align: center; background: linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(99, 102, 241, 0.1)); padding: 30px; border-radius: 20px; margin: 20px 0;'>
                <h3 style='color: #0f172a; margin-bottom: 20px;'>💡 Tezkor Maslahatlar</h3>
                <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; text-align: left;'>
                    <div>
                        <strong style='color: #0284c7;'>🎯 Aniq savol bering</strong>
                        <p style='color: #64748b; margin: 5px 0;'>Nima xohlayotganingizni batafsil yozing</p>
                    </div>
                    <div>
                        <strong style='color: #6366f1;'>📎 Fayl yuklang</strong>
                        <p style='color: #64748b; margin: 5px 0;'>PDF yoki DOCX tahlil qilish uchun</p>
                    </div>
                    <div>
                        <strong style='color: #8b5cf6;'>🎨 Shablonlardan foydalaning</strong>
                        <p style='color: #64748b; margin: 5px 0;'>Tayyor formatlar mavjud</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Chat tarixi
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    
    # Chat input
    if pr := st.chat_input("💭 Somo AI ga xabar yuboring...", key="chat_input"):
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
                    sys_instr = """Sening isming Somo AI. Seni Usmonov Sodiq yaratgan. 
                    Sen professional, samimiy va foydali yordamchi sun'iy intellektsан. 
                    Har doim aniq, tushunarli va to'liq javoblar berasan.
                    Matematika formulalarini LaTeX formatida ($...$) yoz.
                    Kod yozishda eng yaxshi amaliyotlardan foydalangan va izohlar qo'sh.
                    Foydalanuvchi bilan samimiy va do'stona muloqot qil.
                    Javoblaringni strukturalashtirilgan va o'qishga qulay qil."""
                    
                    # Xabarlar tarixini tayyorlash
                    msgs = [{"role": "system", "content": sys_instr}]
                    
                    # Fayl mazmuni qo'shish
                    if st.session_state.uploaded_file_text:
                        msgs.append({
                            "role": "system", 
                            "content": f"Yuklangan hujjat mazmuni (birinchi 4500 ta belgi):\n\n{st.session_state.uploaded_file_text[:4500]}"
                        })
                    
                    # Oxirgi 20 ta xabarni qo'shish
                    for old in st.session_state.messages[-20:]:
                        msgs.append(old)
                    
                    # AI javobini olish
                    if client:
                        response = client.chat.completions.create(
                            messages=msgs,
                            model="llama-3.3-70b-versatile",
                            temperature=temperature,
                            max_tokens=3000
                        )
                        
                        res = response.choices[0].message.content
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
                        st.error("❌ AI xizmati mavjud emas. Iltimos, keyinroq urinib ko'ring.")
                        
                except Exception as e:
                    error_msg = f"❌ Xatolik yuz berdi: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# SHABLONLAR SAHIFASI
elif st.session_state.current_page == "templates":
    st.markdown("""
        <div style='text-align: center; margin: 30px 0;'>
            <h1 style='font-size: 42px; margin-bottom: 15px;'>
                🎨 <span class='gradient-text'>Shablonlar Markazi</span>
            </h1>
            <p style='color: #64748b; font-size: 18px;'>
                3 professional shablon bilan ishni tezlashtiring
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Kategoriya tanlash
    selected_category = st.selectbox(
        "📁 Kategoriya tanlang:",
        options=list(TEMPLATES.keys()),
        key="template_category"
    )
    
    st.markdown(f"### {selected_category} shablonlari")
    st.markdown("---")
    
    # Shablonlarni ko'rsatish
    templates_in_category = TEMPLATES[selected_category]
    
    # Har bir shablon uchun karta
    for idx, template in enumerate(templates_in_category):
        with st.expander(f"{template['icon']} {template['title']}", expanded=(idx == 0)):
            st.markdown(f"**📝 Tavsif:** {template['description']}")
            st.markdown(f"**💡 Shablon:**")
            st.code(template['prompt'], language="text")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📋 Nusxalash", key=f"copy_{selected_category}_{idx}", use_container_width=True):
                    st.code(template['prompt'], language="text")
                    st.success("✅ Shablonni nusxalang va chatga joylashtiring!")
            with col2:
                if st.button(f"🚀 Ishlatish", key=f"use_{selected_category}_{idx}", use_container_width=True):
                    st.session_state.current_page = "chat"
                    st.session_state.messages.append({"role": "user", "content": template['prompt']})
                    st.rerun()
    
    # Qo'shimcha ma'lumot
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 **Maslahat:** Shablonni o'zingizga moslashtiring va aniqroq natijalar uchun [qavs ichidagi]larni to'ldiring!")

# FEEDBACK SAHIFASI
elif st.session_state.current_page == "feedback":
    st.markdown("""
        <div style='text-align: center; margin: 30px 0;'>
            <h1 style='font-size: 42px; margin-bottom: 15px;'>
                💌 <span class='gradient-text'>Fikr-Mulohazalar</span>
            </h1>
            <p style='color: #64748b; font-size: 18px;'>
                Sizning fikringiz biz uchun muhim!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.1, 1, 0.1])
    with col2:
        with st.form("feedback_form"):
            st.markdown("### ⭐ Baholang")
            
            # Rating yulduzlar
            rating = st.select_slider(
                "Somo AI xizmatini qanday baholaysiz?",
                options=[1, 2, 3, 4, 5],
                value=5,
                format_func=lambda x: "⭐" * x,
                label_visibility="collapsed"
            )
            
            st.markdown(f"<p style='text-align: center; font-size: 48px; margin: 20px 0;'>{'⭐' * rating}</p>", unsafe_allow_html=True)
            
            # Kategoriya
            category = st.selectbox(
                "📂 Kategoriya",
                ["Umumiy fikr", "Xato haqida xabar", "Yangi funksiya taklifi", "Savol", "Boshqa"],
                key="feedback_category"
            )
            
            # Xabar
            message = st.text_area(
                "✍️ Xabaringiz",
                placeholder="Sizning fikr-mulohazalaringiz...",
                height=150,
                key="feedback_message"
            )
            
            # Email (ixtiyoriy)
            email = st.text_input(
                "📧 Email (ixtiyoriy)",
                placeholder="email@example.com",
                key="feedback_email"
            )
            
            # Submit tugmasi
            submitted = st.form_submit_button("📤 Yuborish", use_container_width=True, type="primary")
            
            if submitted:
                if not message:
                    st.error("❌ Iltimos, xabar yozing!")
                elif len(message) < 10:
                    st.error("❌ Xabar kamida 10 ta belgidan iborat bo'lishi kerak!")
                elif feedback_db:
                    try:
                        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        feedback_db.append_row([
                            time_stamp,
                            st.session_state.username,
                            rating,
                            category,
                            message,
                            email if email else "N/A",
                            "Yangi"
                        ])
                        
                        st.balloons()
                        st.markdown("""
                            <div class='success-message'>
                                ✅ Rahmat! Sizning fikr-mulohazangiz muvaffaqiyatli yuborildi.
                            </div>
                        """, unsafe_allow_html=True)
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Xatolik: {str(e)}")
                else:
                    st.error("❌ Ma'lumotlar bazasi mavjud emas!")
    
    # Statistika
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📊 Umumiy Statistika")
    
    if feedback_db:
        try:
            all_feedback = feedback_db.get_all_records()
            
            if len(all_feedback) > 1:  # Header qatorini hisobga olmaslik
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📨 Jami Fikrlar", len(all_feedback) - 1)
                
                with col2:
                    ratings = [int(f.get('Rating', 0)) for f in all_feedback[1:] if f.get('Rating')]
                    avg_rating = sum(ratings) / len(ratings) if ratings else 0
                    st.metric("⭐ O'rtacha Baho", f"{avg_rating:.1f}")
                
                with col3:
                    recent = len([f for f in all_feedback[-10:] if f.get('Status') == 'Yangi'])
                    st.metric("🆕 Yangilar", recent)
            else:
                st.info("💬 Hali fikr-mulohazalar yo'q. Birinchi bo'lib yozing!")
        except:
            st.warning("⚠️ Statistika yuklanmadi")

# --- 📌 11. FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align:center; color: #94a3b8; padding: 30px; border-top: 2px solid #e2e8f0; background: linear-gradient(180deg, transparent, rgba(14, 165, 233, 0.05));'>
        <p style='margin: 8px 0; font-size: 18px; font-weight: 600;'>🌌 <strong>Somo AI Infinity</strong></p>
        <p style='margin: 8px 0; color: #64748b;'>Powered by Groq & Llama 3.3 (70B Parameters)</p>
        <p style='margin: 8px 0;'>👨‍💻 Yaratuvchi: <strong>Usmonov Sodiq</strong></p>
        <p style='margin: 8px 0; font-size: 13px;'>📧 support@somoai.uz | 🌐 www.somoai.uz</p>
        <p style='margin: 15px 0 0 0; font-size: 12px; color: #94a3b8;'>© 2026 Barcha huquqlar himoyalangan | Versiya 2.0</p>
    </div>
""", unsafe_allow_html=True)

