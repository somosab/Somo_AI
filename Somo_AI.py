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

# Cookies - Sessiyani saqlash (Avtomatik kirish uchun)
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Sky_Secret_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. OCHIQ KO'K PREMIUM DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { background-color: #f8fafc !important; }

    /* CHAP BO'LIM (SIDEBAR) - OCHIQ KO'K DIZAYN */
    [data-testid="stSidebar"] {
        background-color: #e0f2fe !important; /* Ochiq havorang / Sky Blue */
        border-right: 2px solid #bae6fd;
    }
    
    /* Sidebar ichidagi barcha elementlarni bir xil fonda saqlash */
    [data-testid="stSidebar"] section, [data-testid="stSidebar"] .stVerticalBlock {
        background-color: #e0f2fe !important;
    }
    
    /* Sidebar matnlari (To'q ko'k rangda, o'qishga qulay) */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #0369a1 !important;
        font-weight: 600 !important;
    }

    /* TUGMALAR (Sidebar ichidagi) - Moviy gradient */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-weight: 700 !important;
        transition: 0.3s all ease !important;
        margin-bottom: 10px !important;
        width: 100% !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    div[data-testid="stSidebar"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(14, 165, 233, 0.4) !important;
        background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%) !important;
    }

    /* FAYL YUKLASH MAYDONI (Ochiq ko'k fonga moslash) */
    [data-testid="stFileUploader"] {
        background-color: #f0f9ff !important;
        border: 2px dashed #7dd3fc !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }
    [data-testid="stFileUploader"] section { color: #0369a1 !important; }

    /* ASOSIY SAHIFA KARTALARI */
    .card-box {
        background: white;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: 0.3s;
    }
    .card-box:hover { transform: translateY(-8px); border-color: #0ea5e9; }
    
    .gradient-text {
        background: linear-gradient(90deg, #0ea5e9, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Chat input maydoni */
    .stChatInputContainer {
        border-radius: 15px !important;
        border: 1px solid #e2e8f0 !important;
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

# --- 🔐 5. LOGIN VA AVTOMATIK SESSYA ---
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
                else: st.error("⚠️ Username yoki parol noto'g'ri!")
        with tab_reg:
            nu = st.text_input("Yangi Username", key="r_user")
            np = st.text_input("Yangi Parol", type='password', key="r_pass")
            if st.button("Yaratish ✨", use_container_width=True):
                if nu and np:
                    hp = hashlib.sha256(np.encode()).hexdigest()
                    user_db.append_row([nu, hp, "active", str(datetime.now())])
                    st.success("✅ Hisob yaratildi! Endi 'Kirish' bo'limiga o'ting.")
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS ---
if "messages" not in st.session_state: st.session_state.messages = []

# SIDEBAR SOZLAMALARI (OCHIQ KO'K)
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 15px;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #6366f1); width: 80px; height: 80px; border-radius: 50%; margin: 0 auto; line-height: 80px; font-size: 35px; color: white; font-weight: bold; border: 4px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
                {st.session_state.username[0].upper()}
            </div>
            <h2 style='color: #0369a1; margin-top: 15px;'>{st.session_state.username}</h2>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **FAYL TAHLILI**")
    uploaded_file = st.file_uploader("Faylni tanlang", type=["pdf", "docx"], label_visibility="collapsed")
    context_text = process_doc(uploaded_file) if uploaded_file else ""
    if uploaded_file: st.success("📄 Hujjat o'qildi!")

    st.markdown("<br>"*12, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish"):
        cookies["somo_user_session"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()

# DASHBOARD
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center; margin-top: 30px;'>Xush kelibsiz, <span class='gradient-text'>{st.session_state.username}</span>! ✨</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Sizning shaxsiy intellektual yordamchingiz.</p>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    with cols[0]: st.markdown('<div class="card-box"><h1>🔬</h1><h3>Tahlil</h3><p>Murakkab mantiqiy savollar va hisob-kitoblar</p></div>', unsafe_allow_html=True)
    with cols[1]: st.markdown('<div class="card-box"><h1>📂</h1><h3>Hujjat</h3><p>PDF va Word fayllarni tahlil qilish</p></div>', unsafe_allow_html=True)
    with cols[2]: st.markdown('<div class="card-box"><h1>💡</h1><h3>Ijod</h3><p>G\'oyalar, kodlar va ssenariylar</p></div>', unsafe_allow_html=True)

# CHATNI KO'RSATISH
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# CHAT INPUT VA AI JAVOBI
if prompt := st.chat_input("Somo AI ga savol bering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # AI yo'riqnomasi
            sys_prompt = f"Sening isming Somo AI. Yaratuvching: Usmonov Sodiq. Foydalanuvchi: {st.session_state.username}. Har qanday sohada professional javob ber. Matematik formulalarni LaTeX ($...$) formatida yoz."
            
            msgs = [{"role": "system", "content": sys_prompt}]
            
            if context_text:
                msgs.append({"role": "system", "content": f"Foydalanuvchi yuklagan hujjat mazmuni: {context_text[:4000]}"})
            
            # Xotira (Oxirgi 10 ta xabar)
            for m in st.session_state.messages[-10:]:
                msgs.append(m)
            
            res_area = st.empty()
            response = client.chat.completions.create(
                messages=msgs,
                model="llama-3.3-70b-versatile",
                temperature=0.6
            ).choices[0].message.content
            
            res_area.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            if chat_db:
                chat_db.append_row([st.session_state.username, prompt, response[:500], str(datetime.now())])
        except Exception as e:
            st.error(f"⚠️ Texnik xatolik: {str(e)}")
