import streamlit as st
import gspread
import hashlib
import mammoth
import base64
import time
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

cookies = EncryptedCookieManager(
    password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026_Final_PRO")
)
if not cookies.ready():
    st.stop()

# --- 🎨 2. CSS DIZAYN ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 50%, #ddd6fe 100%) !important;
    }
    [data-testid="stSidebarNav"] { display: none !important; }
    .st-emotion-cache-1vt458p, .st-emotion-cache-k77z8z, .st-emotion-cache-12fmjuu {
        font-size: 0px !important;
        color: transparent !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e0f2fe 0%, #bae6fd 50%, #c7d2fe 100%) !important;
        border-right: 3px solid #7dd3fc;
    }
    [data-testid="stSidebar"] section, [data-testid="stSidebar"] .stVerticalBlock {
        background: transparent !important;
    }
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
    .card-box:hover::before { left: 100%; }
    .card-box:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 20px 40px rgba(14, 165, 233, 0.25);
        border-color: #0ea5e9;
    }
    @media (max-width: 768px) {
        .card-box {
            min-width: 150px !important;
            padding: 20px !important;
            margin-bottom: 15px !important;
        }
        .card-box h1 { font-size: 28px !important; }
        .card-box h3 { font-size: 17px !important; }
        .card-box p  { font-size: 13px !important; }
        h1 { font-size: 26px !important; }
    }
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
        50%       { background-position: 100% 50%; }
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; background: transparent; }
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
    .stChatMessage {
        background: linear-gradient(145deg, #ffffff, #fafafa);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
    }
    .stChatInputContainer {
        border-top: 2px solid #e2e8f0;
        background: linear-gradient(180deg, #ffffff, #f8fafc);
        padding: 15px;
        box-shadow: 0 -4px 15px rgba(0,0,0,0.05);
    }
    .stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 15px;
        padding: 20px;
        border-left: 4px solid #0ea5e9;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .feedback-box {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 2px solid #e2e8f0;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.5; }
    }
    .loading { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
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
        to   { transform: translateY(0);     opacity: 1; }
    }
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
    .vision-badge {
        background: linear-gradient(135deg, #8b5cf6, #6366f1);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
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
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], scope
        )
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        user_sheet = ss.sheet1
        chat_sheet = ss.worksheet("ChatHistory")
        try:
            feedback_sheet = ss.worksheet("Letters")
        except Exception:
            feedback_sheet = ss.add_worksheet(title="Letters", rows="1000", cols="10")
            feedback_sheet.append_row(
                ["Timestamp", "Username", "Rating", "Category", "Message", "Email", "Status"]
            )
        return user_sheet, chat_sheet, feedback_sheet
    except Exception as e:
        st.error(f"❌ Baza xatosi: {str(e)}")
        return None, None, None

user_db, chat_db, feedback_db = get_connections()

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    client = None

# --- 📂 4. FAYL TAHLILI ---
def process_doc(file):
    """PDF va DOCX tahlil"""
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            text = []
            for page in reader.pages:
                pt = page.extract_text()
                if pt:
                    text.append(pt)
            return "\n".join(text)
        elif "wordprocessingml" in file.type:
            return mammoth.extract_raw_text(file).value
    except Exception as e:
        st.warning(f"⚠️ Fayl o'qishda xatolik: {str(e)}")
    return ""

def encode_image(image_file):
    """Rasmni base64 ga aylantirish"""
    image_file.seek(0)
    return base64.b64encode(image_file.read()).decode("utf-8")

def get_image_media_type(file):
    """Rasm turini aniqlash"""
    type_map = {
        "image/jpeg": "image/jpeg",
        "image/jpg":  "image/jpeg",
        "image/png":  "image/png",
        "image/webp": "image/webp",
        "image/gif":  "image/gif",
    }
    return type_map.get(file.type, "image/jpeg")

# --- 🎯 5. SHABLONLAR ---
TEMPLATES = {
    "Biznes": [
        {
            "title": "📊 Biznes Reja",
            "icon": "📊",
            "prompt": (
                "Menga [kompaniya nomi] uchun professional biznes reja tuzing.\n"
                "- Ijroiya xulosasi\n"
                "- Bozor tahlili\n"
                "- Marketing strategiyasi\n"
                "- Moliyaviy rejalar\n"
                "- 5 yillik prognoz"
            ),
            "description": "To'liq biznes reja yaratish"
        }
    ],
    "Dasturlash": [
        {
            "title": "💻 Kod Generator",
            "icon": "💻",
            "prompt": (
                "[dasturlash tili]da [funksionallik] uchun kod yoz:\n"
                "- Clean code prinsiplari\n"
                "- Izohlar bilan\n"
                "- Error handling\n"
                "- Best practices\n"
                "- Test misollari"
            ),
            "description": "Har qanday tildagi kod"
        }
    ],
    "Ta'lim": [
        {
            "title": "📖 Dars Rejasi",
            "icon": "📖",
            "prompt": (
                "[mavzu] bo'yicha to'liq dars rejasi tuzing:\n"
                "- O'quv maqsadlari\n"
                "- Kirish (10 daqiqa)\n"
                "- Asosiy qism (30 daqiqa)\n"
                "- Amaliy mashqlar (15 daqiqa)\n"
                "- Yakun (5 daqiqa)\n"
                "- Uyga vazifa"
            ),
            "description": "O'qituvchilar uchun"
        }
    ]
}

# --- 🔐 6. SESSION BOSHQARUVI ---
if "logged_in" not in st.session_state:
    session_user = cookies.get("somo_user_session")
    if session_user and user_db:
        try:
            recs = user_db.get_all_records()
            ud = next((r for r in recs if str(r["username"]) == session_user), None)
            if ud and str(ud.get("status")).lower() == "active":
                st.session_state.username   = session_user
                st.session_state.logged_in  = True
                st.session_state.login_time = datetime.now()
            else:
                st.session_state.logged_in = False
        except Exception:
            st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

def handle_logout():
    """Tizimdan chiqish"""
    try:
        cookies["somo_user_session"] = ""
        cookies.save()
    except Exception:
        pass
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state.logged_in = False
    st.rerun()

# --- 🔒 7. LOGIN SAHIFASI ---
if not st.session_state.logged_in:
    st.markdown("""
        <div style='text-align:center; margin-top:60px;'>
            <h1 style='font-size:56px; margin-bottom:10px;'>
                🌌 Somo AI <span class='gradient-text'>Infinity</span>
            </h1>
            <p style='color:#64748b; font-size:20px; margin-bottom:15px;'>
                Kelajak texnologiyalari bilan tanishing
            </p>
            <p style='color:#94a3b8; font-size:16px;'>
                ⚡ 70B parametrli AI &nbsp;|&nbsp; 🖼 Vision (Rasm tahlili) &nbsp;|&nbsp; 📄 Hujjat tahlili
            </p>
        </div>
    """, unsafe_allow_html=True)

    _, col2, _ = st.columns([0.25, 1, 0.25])
    with col2:
        tab1, tab2, tab3 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish", "ℹ️ Ma'lumot"])

        # --- KIRISH ---
        with tab1:
            with st.form("login_form"):
                st.markdown("### 🔐 Hisobingizga kiring")
                u_in = st.text_input("👤 Username", placeholder="Username kiriting",  key="login_user")
                p_in = st.text_input("🔑 Parol",    type="password", placeholder="Parol kiriting", key="login_pass")
                ca, cb = st.columns(2)
                with ca:
                    submitted = st.form_submit_button("🚀 Kirish", use_container_width=True)
                with cb:
                    remember = st.checkbox("✅ Eslab qolish", value=True)

                if submitted and u_in and p_in:
                    if user_db:
                        try:
                            recs = user_db.get_all_records()
                            hp   = hashlib.sha256(p_in.encode()).hexdigest()
                            user = next(
                                (r for r in recs
                                 if str(r["username"]) == u_in and str(r["password"]) == hp),
                                None
                            )
                            if user:
                                if str(user.get("status")).lower() == "blocked":
                                    st.error("🚫 Hisobingiz bloklangan!")
                                else:
                                    st.session_state.username   = u_in
                                    st.session_state.logged_in  = True
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
                            st.error(f"❌ Xatolik: {e}")

        # --- RO'YXATDAN O'TISH ---
        with tab2:
            with st.form("register_form"):
                st.markdown("### ✨ Yangi hisob yaratish")
                nu  = st.text_input("👤 Username",          placeholder="Kamida 3 ta belgi",  key="reg_user")
                np  = st.text_input("🔑 Parol",             type="password", placeholder="Kamida 6 ta belgi", key="reg_pass")
                npc = st.text_input("🔑 Parolni tasdiqlang", type="password", placeholder="Qayta kiriting",    key="reg_pass_c")
                agree    = st.checkbox("Men foydalanish shartlariga roziman")
                sub_reg  = st.form_submit_button("✨ Hisob yaratish", use_container_width=True)

                if sub_reg:
                    if not agree:
                        st.error("❌ Foydalanish shartlariga rozilik bering!")
                    elif not nu or not np:
                        st.error("❌ Barcha maydonlarni to'ldiring!")
                    elif len(nu) < 3:
                        st.error("❌ Username kamida 3 ta belgi!")
                    elif len(np) < 6:
                        st.error("❌ Parol kamida 6 ta belgi!")
                    elif np != npc:
                        st.error("❌ Parollar mos kelmadi!")
                    elif user_db:
                        try:
                            recs = user_db.get_all_records()
                            if any(r["username"] == nu for r in recs):
                                st.error("❌ Bu username band!")
                            else:
                                hp = hashlib.sha256(np.encode()).hexdigest()
                                user_db.append_row([nu, hp, "active", str(datetime.now())])
                                st.balloons()
                                st.success("🎉 Ro'yxatdan o'tdingiz! Kirish bo'limiga o'ting.")
                        except Exception as e:
                            st.error(f"❌ Xatolik: {e}")

        # --- MA'LUMOT ---
        with tab3:
            st.markdown("""
                ### 🌟 Somo AI Infinity haqida

                🧠 **Aqlli AI Yordamchi**
                - 70B parametrli Llama 3.3 modeli
                - Real-time javoblar, ko'p tilda muloqot

                🖼 **Vision — Rasm Tahlili** *(YANGI!)*
                - JPG, PNG, WEBP rasmlarni ko'radi va tahlil qiladi
                - Matn, ob'ekt, grafik va jadvallarni aniqlaydi
                - Rasm haqida har qanday savolga javob beradi

                📄 **Hujjat Tahlili**
                - PDF va DOCX fayllarni tahlil qilish
                - Matnni umumlashtirish

                🎨 **Kreativlik Shablonlari**
                - 3 tayyor shablon: Biznes, Dasturlash, Ta'lim

                ⚙️ **Moslashtirilgan**
                - Ijodkorlik darajasi sozlamasi
                - Chat tarixi yuklab olish

                ---
                📧 **Yordam:** support@somoai.uz
                👨‍💻 **Yaratuvchi:** Usmonov Sodiq
                📅 **Versiya:** 2.1 Vision (2026)
            """)

    st.markdown("""
        <div style='text-align:center; margin-top:60px; color:#94a3b8;'>
            <p style='font-size:14px;'>🔒 Ma'lumotlaringiz xavfsiz | 🌐 24/7 Onlayn</p>
            <p style='margin-top:20px;'>© 2026 Somo AI | Barcha huquqlar himoyalangan</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- 🚀 8. SESSION STATE INICIALIZATSIYA ---
if "messages"        not in st.session_state: st.session_state.messages        = []
if "total_messages"  not in st.session_state: st.session_state.total_messages  = 0
if "current_page"    not in st.session_state: st.session_state.current_page    = "chat"
if "uploaded_file_text" not in st.session_state: st.session_state.uploaded_file_text = ""
if "uploaded_image"  not in st.session_state: st.session_state.uploaded_image  = None
if "uploaded_image_type" not in st.session_state: st.session_state.uploaded_image_type = None

# --- 📊 9. SIDEBAR ---
with st.sidebar:
    # Profil
    st.markdown(f"""
        <div style='text-align:center; padding:20px; margin-bottom:25px;
                    background:linear-gradient(135deg,rgba(14,165,233,.1),rgba(99,102,241,.1));
                    border-radius:20px;'>
            <div style='background:linear-gradient(135deg,#0ea5e9,#6366f1);
                        width:90px; height:90px; border-radius:50%; margin:0 auto;
                        line-height:90px; font-size:40px; color:white; font-weight:bold;
                        border:5px solid white; box-shadow:0 8px 20px rgba(14,165,233,.3);'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='margin-top:15px; color:#0f172a; font-size:20px;'>
                {st.session_state.username}
            </h3>
            <p style='color:#10b981; font-size:14px; font-weight:600;'>🟢 Aktiv</p>
        </div>
    """, unsafe_allow_html=True)

    # Navigatsiya
    st.markdown("### 🧭 Navigatsiya")
    if st.button("💬 Chat",          use_container_width=True, key="nav_chat"):
        st.session_state.current_page = "chat"
        st.rerun()
    if st.button("🎨 Shablonlar",    use_container_width=True, key="nav_templates"):
        st.session_state.current_page = "templates"
        st.rerun()
    if st.button("💌 Fikr bildirish", use_container_width=True, key="nav_feedback"):
        st.session_state.current_page = "feedback"
        st.rerun()

    st.markdown("---")

    # Statistika
    st.markdown("### 📊 Statistika")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
            <div class='metric-card'>
                <h4 style='color:#0284c7;margin:0;'>💬</h4>
                <h2 style='margin:5px 0;color:#0f172a;'>{}</h2>
                <p style='color:#64748b;margin:0;font-size:12px;'>Xabarlar</p>
            </div>
        """.format(len(st.session_state.messages)), unsafe_allow_html=True)
    with c2:
        if "login_time" in st.session_state:
            dur = (datetime.now() - st.session_state.login_time).seconds // 60
            st.markdown("""
                <div class='metric-card'>
                    <h4 style='color:#6366f1;margin:0;'>⏱</h4>
                    <h2 style='margin:5px 0;color:#0f172a;'>{}</h2>
                    <p style='color:#64748b;margin:0;font-size:12px;'>Daqiqa</p>
                </div>
            """.format(dur), unsafe_allow_html=True)

    st.markdown("---")

    # Chat sahifasi uchun qo'shimcha boshqaruv
    if st.session_state.current_page == "chat":
        st.markdown("### 🎛 Boshqaruv")

        if st.button("🗑 Chatni tozalash", use_container_width=True, key="clear_chat"):
            st.session_state.messages = []
            st.session_state.uploaded_image = None
            st.session_state.uploaded_image_type = None
            st.session_state.uploaded_file_text = ""
            st.success("✅ Chat tozalandi!")
            st.rerun()

        if st.session_state.messages:
            if st.button("📥 Yuklab olish", use_container_width=True, key="dl_chat"):
                data = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
                st.download_button(
                    label="💾 JSON formatda",
                    data=data,
                    file_name=f"somo_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_json"
                )

        st.markdown("---")

        # 🖼 RASM YUKLASH (VISION)
        st.markdown("### 🖼 Rasm Tahlili")
        st.markdown("<div class='vision-badge'>✨ Vision AI — YANGI!</div>", unsafe_allow_html=True)

        img_up = st.file_uploader(
            "Rasm yuklang",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            key="image_uploader",
            help="Rasm yuklang — AI uni ko'radi va tahlil qiladi"
        )

        if img_up:
            st.image(img_up, caption="📷 Yuklangan rasm", use_container_width=True)
            img_b64  = encode_image(img_up)
            img_type = get_image_media_type(img_up)
            st.session_state.uploaded_image      = img_b64
            st.session_state.uploaded_image_type = img_type
            st.success(f"✅ Rasm tayyor! Savol yozing.")
        elif st.session_state.uploaded_image:
            st.info("🖼 Rasm yuklangan — savol yozing!")

        if st.session_state.uploaded_image:
            if st.button("🗑 Rasmni o'chirish", use_container_width=True, key="clear_img"):
                st.session_state.uploaded_image      = None
                st.session_state.uploaded_image_type = None
                st.success("✅ Rasm o'chirildi!")
                st.rerun()

        st.markdown("---")

        # 📂 HUJJAT YUKLASH
        st.markdown("### 📂 Hujjatlar")
        f_up = st.file_uploader(
            "PDF yoki DOCX",
            type=["pdf", "docx"],
            label_visibility="collapsed",
            key="file_uploader",
            help="PDF yoki Word hujjatini tahlil qilish uchun yuklang"
        )
        if f_up:
            with st.spinner("📄 Tahlil qilinmoqda..."):
                f_txt = process_doc(f_up)
                st.session_state.uploaded_file_text = f_txt
            if f_txt:
                st.success(f"✅ {f_up.name}")
                st.info(f"📊 {len(f_txt):,} belgi")
            else:
                st.warning("⚠️ Fayl o'qilmadi")

        st.markdown("---")

        # Sozlamalar
        st.markdown("### ⚙️ Sozlamalar")
        temperature = st.slider(
            "🌡 Ijodkorlik darajasi",
            0.0, 1.0, 0.6, 0.1,
            key="temp_slider",
            help="Past — aniq, Yuqori — ijodiy"
        )
        if temperature < 0.3:
            st.caption("🎯 Aniq va faktlarga asoslangan")
        elif temperature < 0.7:
            st.caption("⚖️ Muvozanatli")
        else:
            st.caption("🎨 Ijodiy va noodatiy")

    st.markdown("<br>" * 3, unsafe_allow_html=True)

    if st.button("🚪 Tizimdan chiqish", use_container_width=True, key="logout_btn", type="primary"):
        handle_logout()

# ============================================================
# --- 📄 10. SAHIFALAR ---
# ============================================================

# ──────────────── CHAT SAHIFASI ────────────────
if st.session_state.current_page == "chat":

    # Dashboard (xabarlar bo'lmasa)
    if not st.session_state.messages:
        st.markdown(f"""
            <div style='text-align:center; margin:40px 0;'>
                <h1 style='font-size:42px; margin-bottom:15px;'>
                    Salom, <span class='gradient-text'>{st.session_state.username}</span>! 👋
                </h1>
                <p style='color:#64748b; font-size:20px; margin-bottom:40px;'>
                    Bugun sizga qanday yordam bera olaman?
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class='dashboard-container'>
                <div class='card-box'>
                    <h1 style='font-size:48px; margin-bottom:15px;'>🧠</h1>
                    <h3 style='color:#0f172a; margin-bottom:10px;'>Aqlli Tahlil</h3>
                    <p style='color:#64748b; line-height:1.6;'>
                        Murakkab mantiq, matematika va muammolarni professional darajada yechish
                    </p>
                </div>
                <div class='card-box'>
                    <h1 style='font-size:48px; margin-bottom:15px;'>🖼</h1>
                    <h3 style='color:#0f172a; margin-bottom:10px;'>Vision — Rasm Ko'rish</h3>
                    <p style='color:#64748b; line-height:1.6;'>
                        Rasm yuklang — AI uni tahlil qiladi, matn va ob'ektlarni aniqlaydi
                    </p>
                </div>
                <div class='card-box'>
                    <h1 style='font-size:48px; margin-bottom:15px;'>📄</h1>
                    <h3 style='color:#0f172a; margin-bottom:10px;'>Hujjatlar Tahlili</h3>
                    <p style='color:#64748b; line-height:1.6;'>
                        PDF va Word fayllarni tahlil qilish, umumlashtirish va xulosalar
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown("""
            <div style='background:linear-gradient(135deg,rgba(14,165,233,.1),rgba(99,102,241,.1));
                        padding:30px; border-radius:20px; margin:20px 0;'>
                <h3 style='color:#0f172a; margin-bottom:20px; text-align:center;'>💡 Tezkor Maslahatlar</h3>
                <div style='display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
                            gap:20px; text-align:left;'>
                    <div>
                        <strong style='color:#0284c7;'>🖼 Rasm yuklang</strong>
                        <p style='color:#64748b; margin:5px 0;'>
                            Sol paneldan rasm yuklang va savol bering — AI ko'radi!
                        </p>
                    </div>
                    <div>
                        <strong style='color:#6366f1;'>📎 Hujjat yuklang</strong>
                        <p style='color:#64748b; margin:5px 0;'>PDF yoki DOCX tahlil qilish uchun</p>
                    </div>
                    <div>
                        <strong style='color:#8b5cf6;'>🎨 Shablonlar</strong>
                        <p style='color:#64748b; margin:5px 0;'>Tayyor formatlar mavjud</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Chat tarixi ko'rsatish
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            if isinstance(m["content"], list):
                for part in m["content"]:
                    if part.get("type") == "text":
                        st.markdown(part["text"])
            else:
                st.markdown(m["content"])

    # Chat input
    if pr := st.chat_input("💭 Somo AI ga xabar yuboring...", key="chat_input"):
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        has_image  = bool(st.session_state.uploaded_image)

        # ── User xabari ──
        if has_image:
            user_content = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{st.session_state.uploaded_image_type};base64,"
                               f"{st.session_state.uploaded_image}"
                    }
                },
                {"type": "text", "text": pr}
            ]
            display_content = [{"type": "text", "text": f"🖼 *[Rasm yuklandi]* — {pr}"}]
        else:
            user_content    = pr
            display_content = pr

        st.session_state.messages.append({"role": "user", "content": display_content})
        with st.chat_message("user"):
            if has_image:
                st.markdown(f"🖼 *[Rasm yuklandi]* — {pr}")
            else:
                st.markdown(pr)

        # Bazaga saqlash
        if chat_db:
            try:
                chat_db.append_row([time_stamp, st.session_state.username, "User", pr])
            except Exception:
                pass

        # ── AI javobi ──
        with st.chat_message("assistant"):
            with st.spinner("🤔 O'ylayapman..."):
                try:
                    sys_instr = (
                        "Sening isming Somo AI. Seni Usmonov Sodiq yaratgan. "
                        "Sen professional, samimiy va foydali yordamchi sun'iy intellektsan. "
                        "Rasmlarni ko'rib tahlil qila olasan. "
                        "Har doim aniq, tushunarli va to'liq javoblar berasan. "
                        "Matematika formulalarini LaTeX ($...$) da yoz. "
                        "Kod yozishda eng yaxshi amaliyotlardan foydalangan va izohlar qo'sh. "
                        "Javoblarni strukturalashtirilgan va o'qishga qulay qil."
                    )

                    # Model tanlash: rasm bo'lsa — vision modeli
                    model = (
                        "meta-llama/llama-4-scout-17b-16e-instruct"
                        if has_image
                        else "llama-3.3-70b-versatile"
                    )

                    msgs = [{"role": "system", "content": sys_instr}]

                    # Hujjat mazmuni
                    if st.session_state.uploaded_file_text:
                        msgs.append({
                            "role": "system",
                            "content": (
                                "Yuklangan hujjat (birinchi 4500 belgi):\n\n"
                                + st.session_state.uploaded_file_text[:4500]
                            )
                        })

                    # Tariх — oxirgi 20 xabar
                    for old in st.session_state.messages[-20:]:
                        role    = old["role"]
                        content = old["content"]
                        # Display content (matnli) — rasmni qayta yubormаymiz
                        if isinstance(content, list):
                            text_parts = [p["text"] for p in content if p.get("type") == "text"]
                            msgs.append({"role": role, "content": " ".join(text_parts)})
                        else:
                            msgs.append({"role": role, "content": content})

                    # Hozirgi xabar: rasm bo'lsa multimodal
                    if has_image:
                        msgs[-1] = {"role": "user", "content": user_content}

                    if client:
                        resp = client.chat.completions.create(
                            messages=msgs,
                            model=model,
                            temperature=temperature,
                            max_tokens=3000
                        )
                        res = resp.choices[0].message.content
                        st.markdown(res)

                        st.session_state.messages.append({"role": "assistant", "content": res})
                        st.session_state.total_messages += 1

                        if chat_db:
                            try:
                                chat_db.append_row([time_stamp, "Somo AI", "Assistant", res])
                            except Exception:
                                pass

                        # Rasm bir marta ishlatilgandan keyin o'chirish
                        if has_image:
                            st.session_state.uploaded_image      = None
                            st.session_state.uploaded_image_type = None
                    else:
                        st.error("❌ AI xizmati mavjud emas.")

                except Exception as e:
                    err = f"❌ Xatolik: {str(e)}"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})

# ──────────────── SHABLONLAR SAHIFASI ────────────────
elif st.session_state.current_page == "templates":
    st.markdown("""
        <div style='text-align:center; margin:30px 0;'>
            <h1 style='font-size:42px; margin-bottom:15px;'>
                🎨 <span class='gradient-text'>Shablonlar Markazi</span>
            </h1>
            <p style='color:#64748b; font-size:18px;'>
                3 professional shablon bilan ishni tezlashtiring
            </p>
        </div>
    """, unsafe_allow_html=True)

    selected_cat = st.selectbox(
        "📁 Kategoriya tanlang:",
        options=list(TEMPLATES.keys()),
        key="template_category"
    )

    st.markdown(f"### {selected_cat} shablonlari")
    st.markdown("---")

    for idx, tmpl in enumerate(TEMPLATES[selected_cat]):
        with st.expander(f"{tmpl['icon']} {tmpl['title']}", expanded=(idx == 0)):
            st.markdown(f"**📝 Tavsif:** {tmpl['description']}")
            st.markdown("**💡 Shablon:**")
            st.code(tmpl["prompt"], language="text")
            c1, c2 = st.columns([3, 1])
            with c1:
                if st.button("📋 Nusxalash", key=f"copy_{selected_cat}_{idx}", use_container_width=True):
                    st.success("✅ Shablonni nusxalang va chatga joylashtiring!")
            with c2:
                if st.button("🚀 Ishlatish", key=f"use_{selected_cat}_{idx}", use_container_width=True):
                    st.session_state.current_page = "chat"
                    st.session_state.messages.append({"role": "user", "content": tmpl["prompt"]})
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 **Maslahat:** [qavs ichidagi] joylarni o'z ma'lumotlaringiz bilan to'ldiring!")

# ──────────────── FEEDBACK SAHIFASI ────────────────
elif st.session_state.current_page == "feedback":
    st.markdown("""
        <div style='text-align:center; margin:30px 0;'>
            <h1 style='font-size:42px; margin-bottom:15px;'>
                💌 <span class='gradient-text'>Fikr-Mulohazalar</span>
            </h1>
            <p style='color:#64748b; font-size:18px;'>Sizning fikringiz biz uchun muhim!</p>
        </div>
    """, unsafe_allow_html=True)

    _, col2, _ = st.columns([0.1, 1, 0.1])
    with col2:
        with st.form("feedback_form"):
            st.markdown("### ⭐ Baholang")
            rating = st.select_slider(
                "Baho",
                options=[1, 2, 3, 4, 5],
                value=5,
                format_func=lambda x: "⭐" * x,
                label_visibility="collapsed"
            )
            st.markdown(
                f"<p style='text-align:center;font-size:48px;margin:20px 0;'>{'⭐'*rating}</p>",
                unsafe_allow_html=True
            )
            category = st.selectbox(
                "📂 Kategoriya",
                ["Umumiy fikr", "Xato haqida xabar", "Yangi funksiya taklifi", "Savol", "Boshqa"],
                key="fb_cat"
            )
            message = st.text_area(
                "✍️ Xabaringiz",
                placeholder="Sizning fikr-mulohazalaringiz...",
                height=150,
                key="fb_msg"
            )
            email = st.text_input("📧 Email (ixtiyoriy)", placeholder="email@example.com", key="fb_email")
            sub_fb = st.form_submit_button("📤 Yuborish", use_container_width=True, type="primary")

            if sub_fb:
                if not message:
                    st.error("❌ Xabar yozing!")
                elif len(message) < 10:
                    st.error("❌ Xabar kamida 10 ta belgi!")
                elif feedback_db:
                    try:
                        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        feedback_db.append_row([
                            ts,
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
                                ✅ Rahmat! Fikringiz muvaffaqiyatli yuborildi.
                            </div>
                        """, unsafe_allow_html=True)
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Xatolik: {e}")
                else:
                    st.error("❌ Baza mavjud emas!")

    # Statistika
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📊 Umumiy Statistika")
    if feedback_db:
        try:
            all_fb = feedback_db.get_all_records()
            if len(all_fb) > 1:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("📨 Jami Fikrlar", len(all_fb) - 1)
                with c2:
                    rtgs = [int(f.get("Rating", 0)) for f in all_fb[1:] if f.get("Rating")]
                    avg  = sum(rtgs) / len(rtgs) if rtgs else 0
                    st.metric("⭐ O'rtacha Baho", f"{avg:.1f}")
                with c3:
                    new_cnt = len([f for f in all_fb[-10:] if f.get("Status") == "Yangi"])
                    st.metric("🆕 Yangilar", new_cnt)
            else:
                st.info("💬 Hali fikr-mulohazalar yo'q. Birinchi bo'lib yozing!")
        except Exception:
            st.warning("⚠️ Statistika yuklanmadi")

# --- 📌 11. FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align:center; color:#94a3b8; padding:30px;
                border-top:2px solid #e2e8f0;
                background:linear-gradient(180deg,transparent,rgba(14,165,233,.05));'>
        <p style='margin:8px 0; font-size:18px; font-weight:600;'>
            🌌 <strong>Somo AI Infinity</strong>
        </p>
        <p style='margin:8px 0; color:#64748b;'>
            Powered by Groq · Llama 3.3 (70B) · LLaMA 4 Scout Vision
        </p>
        <p style='margin:8px 0;'>👨‍💻 Yaratuvchi: <strong>Usmonov Sodiq</strong></p>
        <p style='margin:8px 0;'>👨‍💻 Yordamchi: <strong>Davlatov Mironshoh</strong></p>
        <p style='margin:8px 0; font-size:13px;'>
            📧 support@somoai.uz | 🌐 www.somoai.uz
        </p>
        <p style='margin:15px 0 0 0; font-size:12px; color:#94a3b8;'>
            © 2026 Barcha huquqlar himoyalangan | Versiya 2.1 Vision
        </p>
    </div>
""", unsafe_allow_html=True)
