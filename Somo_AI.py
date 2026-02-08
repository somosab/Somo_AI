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
st.set_page_config(page_title="Somo AI | Infinity", page_icon="🌌", layout="wide")

# Cookies - Sessiyani saqlash uchun (Brauzer yopilsa ham chiqib ketmaydi)
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026_Secure"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. MUKAMMAL PREMIUM DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { background-color: #ffffff !important; }

    /* CHAP BO'LIM (SIDEBAR) - TO'Q KO'K VA ZAMONAVIY */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 2px solid #1e293b;
    }
    
    /* Sidebar ichidagi barcha elementlarni bir xil ko'k fonda saqlash */
    [data-testid="stSidebar"] section, [data-testid="stSidebar"] .stVerticalBlock {
        background-color: #0f172a !important;
    }
    
    /* Sidebar matnlari */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }

    /* TUGMALAR (Sidebar ichidagi) - Neon ko'k effektli */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        transition: 0.3s all ease !important;
        margin-bottom: 10px !important;
        width: 100% !important;
    }
    div[data-testid="stSidebar"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.5) !important;
        background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%) !important;
    }

    /* FAYL YUKLASH MAYDONI (Sidebar dizayniga moslash) */
    [data-testid="stFileUploader"] {
        background-color: #1e293b !important;
        border: 1px dashed #3b82f6 !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }
    [data-testid="stFileUploader"] section { color: white !important; }

    /* ASOSIY SAHIFA KARTALARI */
    .card-box {
        background: white;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
        transition: 0.3s;
    }
    .card-box:hover { transform: translateY(-8px); border-color: #3b82f6; }
    
    .gradient-text {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Chat xabarlari (Yumshoq burchaklar) */
    .stChatMessage { border-radius: 15px !important; margin-bottom: 10px !important; }
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

# --- 📂 4. FAYL KONVERTER (PDF va DOCX) ---
def process_doc(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.extract_raw_text(file).value
    except: return ""
    return ""

# --- 🔐 5. AVTOMATIK LOGIN VA RO'YXATDAN O'TISH ---
if 'logged_in' not in st.session_state:
    saved_user = cookies.get("somo_user_session")
    if saved_user:
        st.session_state.username = saved_user
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; margin-top:50px;'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        tab_login, tab_reg = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
        with tab_login:
            u = st.text_input("Username", key="l_user")
            p = st.text_input("Parol", type='password', key="l_pass")
            if st.button("Kirish 🚀", use_container_width=True):
                data = user_db.get_all_records()
                hp = hashlib.sha256(p.encode()).hexdigest()
                user = next((r for r in data if str(r['username']) == u and str(r['password']) == hp), None)
                if user:
                    st.session_state.username = u
                    st.session_state.logged_in = True
                    cookies["somo_user_session"] = u
                    cookies.save()
                    st.rerun()
                else: st.error("Username yoki parol noto'g'ri!")
        with tab_reg:
            nu = st.text_input("Yangi Username", key="r_user")
            np = st.text_input("Yangi Parol", type='password', key="r_pass")
            if st.button("Yaratish ✨", use_container_width=True):
                if nu and np:
                    hp = hashlib.sha256(np.encode()).hexdigest()
                    user_db.append_row([nu, hp, "active", str(datetime.now())])
                    st.success("Hisob yaratildi! Endi 'Kirish' bo'limiga o'ting.")
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS ---
if "messages" not in st.session_state: st.session_state.messages = []

# SIDEBAR SOZLAMALARI
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 15px;'>
            <div style='background: linear-gradient(135deg, #3b82f6, #8b5cf6); width: 80px; height: 80px; border-radius: 50%; margin: 0 auto; line-height: 80px; font-size: 35px; color: white; font-weight: bold; border: 3px solid #1e293b;'>
                {st.session_state.username[0].upper()}
            </div>
            <h2 style='color: white; margin-top: 15px;'>{st.session_state.username}</h2>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **FAYL TAHLILI**")
    uploaded_file = st.file_uploader("Faylni tanlang", type=["pdf", "docx"], label_visibility="collapsed")
    context_text = process_doc(uploaded_file) if uploaded_file else ""
    if uploaded_file: st.success("✅ Hujjat tayyor!")

    st.markdown("<br>"*10, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish"):
        cookies["somo_user_session"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()

# DASHBOARD (Agar chat bo'sh bo'lsa)
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center; margin-top: 30px;'>Xush kelibsiz, <span class='gradient-text'>{st.session_state.username}</span>! ✨</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Sizning universal intellektual yordamchingiz har doim xizmatingizda.</p>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    with cols[0]: st.markdown('<div class="card-box"><h1>🔬</h1><h3>Tahlil</h3><p>Murakkab hisob-kitoblar va mantiqiy savollar</p></div>', unsafe_allow_html=True)
    with cols[1]: st.markdown('<div class="card-box"><h1>📂</h1><h3>Hujjat</h3><p>Hujjatlarni tahlil qilish va xulosalash</p></div>', unsafe_allow_html=True)
    with cols[2]: st.markdown('<div class="card-box"><h1>💡</h1><h3>G\'oyalar</h3><p>Kreativ loyihalar va biznes ssenariylar</p></div>', unsafe_allow_html=True)

# CHATNI KO'RSATISH
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# CHAT INPUT VA AI JAVOBI
if prompt := st.chat_input("Somo AI ga savol bering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # AI uchun yo'riqnoma (System Prompt)
            sys_prompt = f"Sening isming Somo AI. Yaratuvching: Usmonov Sodiq. Foydalanuvchi: {st.session_state.username}. Har qanday sohada (matematika, dasturlash, adabiyot va h.k.) professional va tushunarli javob ber. Matematik formulalarni faqat LaTeX ($...$) formatida yoz."
            
            msgs = [{"role": "system", "content": sys_prompt}]
            
            # Agar hujjat yuklangan bo'lsa, uni AI xotirasiga qo'shish
            if context_text:
                msgs.append({"role": "system", "content": f"Foydalanuvchi yuklagan hujjat mazmuni: {context_text[:4000]}"})
            
            # Suhbat tarixini qo'shish (Xotira)
            for m in st.session_state.messages[-10:]:
                msgs.append(m)
            
            # AI dan javob olish
            res_area = st.empty()
            response = client.chat.completions.create(
                messages=msgs,
                model="llama-3.3-70b-versatile",
                temperature=0.6
            ).choices[0].message.content
            
            res_area.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Tarixni Google Sheets'ga yozish
            if chat_db:
                chat_db.append_row([st.session_state.username, prompt, response[:500], str(datetime.now())])
        except Exception as e:
            st.error(f"Xatolik: {str(e)}")
