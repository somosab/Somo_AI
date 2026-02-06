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

# --- 🎨 2. MUKAMMAL FULL-WIDTH DARK DIZAYN (RASMDAGIDEK) ---
st.markdown("""
    <style>
    /* 1. ASOSIY FON */
    .stApp { 
        background-color: #000000 !important;
        background: radial-gradient(circle at center, #000000 0%, #020617 100%) !important; 
        color: #ffffff !important; 
    }
    
    /* 2. INPUT MAYDONLARI (RASMDAGIDEK UZUN VA TO'Q) */
    div[data-baseweb="input"] {
        background-color: #1e1e1e !important; /* To'q kulrang-qora fon */
        border: none !important; 
        border-radius: 8px !important; 
        height: 45px !important;
        width: 100% !important;
    }
    
    input {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Tablarni rasmdagidek sozlash */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #64748b !important;
        padding: 0px 20px !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #f43f5e !important; 
        border-bottom: 2px solid #f43f5e !important;
    }

    /* 3. SIDEBAR */
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        border-right: 1px solid #1e293b; 
    }
    
    /* 4. TUGMALAR (KIRISH TUGMASI - KICHIK VA KO'K) */
    .stButton>button { 
        background-color: #1e293b !important;
        color: #38bdf8 !important; 
        border: 1px solid #38bdf8 !important; 
        border-radius: 8px !important; 
        width: 100px !important;
        height: 38px !important;
        font-weight: 500 !important;
    }
    .stButton>button:hover {
        background-color: #38bdf8 !important;
        color: #000000 !important;
    }

    /* CHAT XABARLARI */
    .stChatMessage { 
        background: rgba(30, 41, 59, 0.5) !important; 
        border-radius: 15px;
    }

    /* LOGOUT TUGMASI */
    .logout-btn>div>button { border-color: #f43f5e !important; color: #f43f5e !important; width: 100% !important; }
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
    except: return "Xatolik yuz berdi."
    return ""

# --- 🔐 4. LOGIN INTERFACE (RASMDAGIDEK FULL-WIDTH) ---
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:#38bdf8; margin-top:80px; font-size: 3.5rem;">🌌 Somo AI Infinity</h1>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    
    with t1:
        u = st.text_input("Username", key="log_u")
        p = st.text_input("Parol", type='password', key="log_p")
        if st.button("Kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u), None)
            if user and str(user['password']) == hp:
                st.session_state.logged_in, st.session_state.username, st.session_state.messages = True, u, []
                cookies["somo_user"] = u
                cookies.save()
                st.rerun()
            else: st.error("⚠️ Username yoki parol noto'g'ri!")
            
    with t2:
        nu = st.text_input("Yangi Username", key="reg_u")
        np = st.text_input("Yangi Parol", type='password', key="reg_p")
        if st.button("Yaratish"):
            if nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("🎉 Hisob yaratildi!")
    st.stop()

# --- 💬 5. MAIN DASHBOARD & CHAT ---
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

# Dashboard Kartalari
if not st.session_state.messages:
    st.markdown(f"""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="font-size: 3.5rem; color: #38bdf8;">Assalomu alaykum, {st.session_state.username}! ✦</h1>
            <p style="color: #94a3b8; font-size: 1.2rem;">Somo AI bilan barcha sohalarda mukammallikka erishing.</p>
        </div>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <div style="border: 1px solid #38bdf8; padding: 20px; border-radius: 15px; width: 200px; text-align: center;">
                <h4 style="color:#38bdf8;">🧠 Tahlil</h4>
                <p style="font-size: 0.8rem;">Murakkab fanlar yechimi.</p>
            </div>
            <div style="border: 1px solid #818cf8; padding: 20px; border-radius: 15px; width: 200px; text-align: center;">
                <h4 style="color:#818cf8;">📑 Hujjat</h4>
                <p style="font-size: 0.8rem;">Fayllarni tahlil qilish.</p>
            </div>
            <div style="border: 1px solid #f43f5e; padding: 20px; border-radius: 15px; width: 200px; text-align: center;">
                <h4 style="color:#f43f5e;">✍️ Ijod</h4>
                <p style="font-size: 0.8rem;">Kreativ yechimlar.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Chat Logikasi
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
