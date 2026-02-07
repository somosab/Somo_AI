import streamlit as st
import pandas as pd
import gspread
import hashlib
import mammoth
import pptx
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# --- 🛰 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Somo AI | Universal Infinity", page_icon="🌌", layout="wide")

# --- 🍪 COOKIES SETUP ---
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. MUKAMMAL DIZAYN (OQ YOZUV VA TO'Q FON) ---
st.markdown("""
    <style>
    /* 1. ASOSIY FON (Qora va to'q ko'k gradient) */
    .stApp { 
        background-color: #000000 !important;
        background: radial-gradient(circle at center, #000000 0%, #020617 100%) !important; 
        color: #ffffff !important; 
    }
    
    /* 2. INPUT MAYDONLARI SOZLAMASI */
    /* Input konteyneri (tashqi quti) */
    div[data-baseweb="input"] {
        background-color: #1e1e1e !important; /* To'q kulrang fon */
        border: 1px solid #334155 !important; /* Nozik hoshiya */
        border-radius: 10px !important; 
        height: 50px !important;
        width: 100% !important;
    }
    
    /* Input ichidagi yozuv (USER SO'RAGAN OQ RANG) */
    input[type="text"], input[type="password"] {
        color: #ffffff !important; /* Yozuv oppoq bo'ladi */
        -webkit-text-fill-color: #ffffff !important;
        font-size: 1.1rem !important;
        caret-color: #38bdf8 !important; /* Kursor rangi ko'k */
    }

    /* Input ustiga bosganda (Focus) */
    div[data-baseweb="input"]:focus-within {
        border-color: #38bdf8 !important; /* Bosganda ko'k yonadi */
        background-color: #262626 !important;
    }

    /* Label (Username, Parol so'zlari) */
    label[data-baseweb="label"] {
        color: #e2e8f0 !important; /* Ochiq kulrang */
        font-size: 1rem !important;
        font-weight: 500 !important;
    }

    /* 3. TABLAR DİZAYNI */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #f43f5e !important; 
        border-bottom: 2px solid #f43f5e !important;
    }

    /* 4. SIDEBAR */
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        border-right: 1px solid #1e293b; 
    }
    
    /* 5. TUGMALAR (KIRISH) */
    .stButton>button { 
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%); 
        color: #38bdf8; 
        border: 1px solid #38bdf8; 
        border-radius: 8px; 
        font-weight: 700; 
        height: 45px; 
        width: 100%;
        margin-top: 10px;
    }
    .stButton>button:hover { 
        background: #38bdf8; 
        color: #000000; 
        box-shadow: 0 0 15px #38bdf8; 
    }

    /* CHAT XABARLARI FONİ */
    .stChatMessage { 
        background: rgba(30, 41, 59, 0.4) !important; 
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 15px;
    }
    
    /* LOGOUT */
    .logout-btn>div>button { border-color: #f43f5e !important; color: #f43f5e !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. CORE CONNECTIONS ---
def connect_sheets():
    try:
        gcp_info = dict(st.secrets["gcp_service_account"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_info, scope)
        client = gspread.authorize(creds)
        ss = client.open("Somo_Users")
        return ss.sheet1, ss.worksheet("ChatHistory")
    except: return None, None

user_sheet, chat_sheet = connect_sheets()

# --- 🔄 AUTO-LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    saved_user = cookies.get("somo_user")
    if saved_user:
        st.session_state.logged_in = True
        st.session_state.username = saved_user
        st.session_state.messages = []
    else:
        st.session_state.logged_in = False

def extract_universal_content(file):
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'pdf': return "".join([p.extract_text() for p in PdfReader(file).pages])
        elif ext == 'docx': return mammoth.extract_raw_text(file).value
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)
            return f"Jadval: {df.to_string()}"
        elif ext == 'pptx':
            prs = pptx.Presentation(file)
            return "\n".join([s.text for sl in prs.slides for s in sl.shapes if hasattr(s, "text")])
    except: return "Xatolik."
    return ""

# --- 🔐 4. LOGIN INTERFACE ---
if not st.session_state.logged_in:
    st.markdown("""
        <div style="text-align: center; margin-top: 80px; margin-bottom: 50px;">
             <h1 style="color:#38bdf8; font-size: 3.5rem; font-weight: 800;">🌌 Somo AI Infinity</h1>
        </div>
    """, unsafe_allow_html=True)

    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    
    with t1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Parol", type='password', key="login_p")
        if st.button("Kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u), None)
            if user and str(user['password']) == hp:
                st.session_state.logged_in, st.session_state.username, st.session_state.messages = True, u, []
                cookies["somo_user"] = u
                cookies.save()
                st.rerun()
            else: st.error("⚠️ Username yoki parol xato!")

    with t2:
        nu = st.text_input("Yangi Username")
        np = st.text_input("Yangi Parol", type='password')
        if st.button("Hisob yaratish"):
            if nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("🎉 Hisob yaratildi! Endi kirish qismiga o'ting.")
    st.stop()

# --- 💬 5. MAIN APP ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
if st.sidebar.button("🗑 Chatni tozalash"):
    st.session_state.messages = []
    st.rerun()

up_file = st.sidebar.file_uploader("📂 Fayl yuklash", type=["pdf", "docx", "xlsx", "csv", "pptx"])

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="logout-btn">', unsafe_allow_html=True)
if st.sidebar.button("🚪 Tizimdan chiqish"):
    st.session_state.logged_in = False
    cookies["somo_user"] = ""
    cookies.save()
    st.rerun()
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Dashboard
if not st.session_state.messages:
    st.markdown(f"""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="font-size: 3rem; color: #38bdf8;">Assalomu alaykum, {st.session_state.username}! ✦</h1>
            <p style="color: #94a3b8; font-size: 1.2rem;">Somo AI bilan barcha sohalarda mukammallikka erishing.</p>
        </div>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <div style="border: 1px solid #38bdf8; padding: 20px; border-radius: 15px; width: 220px; text-align: center; background: rgba(56, 189, 248, 0.05);">
                <h4 style="color:#38bdf8;">🧠 Tahlil</h4>
                <p style="font-size: 0.8rem; color: #ccc;">Murakkab fanlar yechimi.</p>
            </div>
            <div style="border: 1px solid #818cf8; padding: 20px; border-radius: 15px; width: 220px; text-align: center; background: rgba(129, 140, 248, 0.05);">
                <h4 style="color:#818cf8;">📑 Hujjat</h4>
                <p style="font-size: 0.8rem; color: #ccc;">Fayllarni o'qish va tushunish.</p>
            </div>
            <div style="border: 1px solid #f43f5e; padding: 20px; border-radius: 15px; width: 220px; text-align: center; background: rgba(244, 63, 94, 0.05);">
                <h4 style="color:#f43f5e;">✍️ Ijod</h4>
                <p style="font-size: 0.8rem; color: #ccc;">Kreativ yozish va kodlash.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Savolingizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_msg = f"Isming Somo AI. Yaratuvchi: Usmonov Sodiq. Foydalanuvchi: {st.session_state.username}."
        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        if up_file:
            ctx.insert(1, {"role": "system", "content": f"Fayl: {extract_universal_content(up_file)}"})
        
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        try: chat_sheet.append_row([datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:200]])
        except: pass
