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

# Cookies - Sessiyani saqlash (Xavfsiz va barqaror)
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026_Secure"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. MUKAMMAL PREMIUM DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { background-color: #ffffff !important; }

    /* CHAP BO'LIM (SIDEBAR) - TO'LIQ QORA VA PREMIUM */
    [data-testid="stSidebar"] {
        background-color: #05070a !important;
        border-right: 1px solid #1e293b;
    }
    
    /* Sidebar ichidagi oq dog'larni va chiziqlarni yo'qotish */
    [data-testid="stSidebar"] section { background-color: #05070a !important; }
    
    /* TUGMALAR DIZAYNI */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        transition: 0.3s all ease !important;
        margin-bottom: 10px !important;
    }
    div[data-testid="stSidebar"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(79, 70, 229, 0.4) !important;
    }

    /* FAYL YUKLASH MAYDONI */
    [data-testid="stFileUploader"] {
        background-color: #0f172a !important;
        border: 1px dashed #4f46e5 !important;
        border-radius: 12px !important;
        padding: 10px !important;
        color: white !important;
    }

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
    .card-box:hover { transform: translateY(-5px); border-color: #4f46e5; }
    
    .gradient-text {
        background: linear-gradient(90deg, #4f46e5, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Chat xabarlari dizayni */
    .stChatMessage { border-radius: 15px !important; padding: 15px !important; }
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
    except Exception as e:
        return None, None

user_db, chat_db = get_connections()
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 📂 4. FAYL KONVERTER ---
def process_doc(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            result = mammoth.extract_raw_text(file)
            return result.value
    except: return ""
    return ""

# --- 🔐 5. LOGIN BO'LIMI (AVTOMATIK KIRISH BILAN) ---
if 'logged_in' not in st.session_state:
    saved_user = cookies.get("somo_user_session")
    if saved_user:
        st.session_state.username = saved_user
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        tab1, tab2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
        with tab1:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Parol", type='password', key="login_p")
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
                else: st.error("Xato: Login yoki parol noto'g'ri!")
        with tab2:
            nu = st.text_input("Yangi Username", key="reg_u")
            np = st.text_input("Yangi Parol", type='password', key="reg_p")
            if st.button("Yaratish ✨", use_container_width=True):
                if nu and np:
                    hp = hashlib.sha256(np.encode()).hexdigest()
                    user_db.append_row([nu, hp, "active", str(datetime.now())])
                    st.success("Muvaffaqiyatli! Endi kirish bo'limiga o'ting.")
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS ---
if "messages" not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 10px;'>
            <div style='background: linear-gradient(135deg, #4f46e5, #ec4899); width: 70px; height: 70px; border-radius: 50%; margin: 0 auto; line-height: 70px; font-size: 30px; color: white; font-weight: bold;'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='color: white; margin-top: 10px;'>{st.session_state.username}</h3>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **FAYL TAHLILI**")
    f = st.file_uploader("Yuklash", type=["pdf", "docx"], label_visibility="collapsed")
    file_content = process_doc(f) if f else ""
    if f: st.success("✅ Fayl yuklandi!")

    st.markdown("<br>"*8, unsafe_allow_html=True)
    if st.button("🚪 Tizimdan chiqish", use_container_width=True):
        cookies["somo_user_session"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()

# Dashboard (Agar xabarlar bo'lmasa ko'rinadi)
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center; margin-top: 50px;'>Xush kelibsiz, <span class='gradient-text'>{st.session_state.username}</span>! ✨</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.2rem;'>Somo AI - sizning universal intellektual yordamchingiz</p>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    with cols[0]: st.markdown('<div class="card-box"><h1>🧠</h1><h3>Tahlil</h3><p>Murakkab matematik va mantiqiy savollar yechimi</p></div>', unsafe_allow_html=True)
    with cols[1]: st.markdown('<div class="card-box"><h1>📄</h1><h3>Hujjat</h3><p>PDF va Word fayllarni o\'qish va xulosalash</p></div>', unsafe_allow_html=True)
    with cols[2]: st.markdown('<div class="card-box"><h1>🎨</h1><h3>Ijod</h3><p>Ssenariylar, kodlar va yangi kreativ g\'oyalar</p></div>', unsafe_allow_html=True)

# Chatni ko'rsatish
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Foydalanuvchi kiritishi
if prompt := st.chat_input("Somo AI dan so'rang..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Tizim xabari (System Prompt)
            system_instruction = f"Sening isming Somo AI. Yaratuvching Usmonov Sodiq. Foydalanuvchi ismi: {st.session_state.username}. Har doim tushunarli, foydali va professional javob ber. Matematik formulalarni LaTeX formatida yoz."
            
            messages_for_ai = [{"role": "system", "content": system_instruction}]
            
            # Agar fayl yuklangan bo'lsa, uni kontekstga qo'shish
            if file_content:
                messages_for_ai.append({"role": "system", "content": f"Yuklangan hujjat mazmuni: {file_content[:3000]}"})
            
            # Tarixni qo'shish (oxirgi 10 ta xabar)
            for m in st.session_state.messages[-10:]:
                messages_for_ai.append(m)
            
            # AI dan javob olish
            res_container = st.empty()
            response = client.chat.completions.create(
                messages=messages_for_ai,
                model="llama-3.3-70b-versatile",
                temperature=0.7
            ).choices[0].message.content
            
            res_container.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Chat tarixini bazaga yozish
            if chat_db:
                chat_db.append_row([st.session_state.username, prompt, response[:500], str(datetime.now())])
        except Exception as e:
            st.error(f"Xatolik yuz berdi: {str(e)}")
