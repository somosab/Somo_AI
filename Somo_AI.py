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

# --- 🛰 1. CONFIGURATION ---
st.set_page_config(page_title="Somo AI | Universal Infinity", page_icon="🌌", layout="wide")

# Cookies setup
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. MUKAMMAL KONTRAST DIZAYN (BLACK & WHITE) ---
st.markdown("""
    <style>
    /* 1. ASOSIY FON - QOP-QORA VA HOVLI MOVIVIY */
    .stApp { 
        background-color: #000000 !important;
        background: radial-gradient(circle at center, #000000 0%, #0f172a 100%) !important; 
        color: #ffffff !important; 
    }
    
    /* 2. INPUT MAYDONLARI (LOGIN & PAROL) - QARAMA-QARSHI KONTRAST */
    /* Bu yerda Inputning foni OQ (White) qilinmoqda */
    div[data-baseweb="input"] {
        background-color: #ffffff !important; 
        border: 2px solid #38bdf8 !important; /* Chiroyli moviy hoshiya */
        border-radius: 12px !important; 
        height: 50px !important;
        width: 100% !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2); /* Yengil yog'du */
    }
    
    /* Input ichidagi yozuv QORA (Black) bo'ladi */
    input[type="text"], input[type="password"] {
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        background-color: transparent !important;
    }

    /* 3. CHAT INPUT (PASTDAGI YOZISH JOYI) */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    
    /* Chat yozish joyi foni OQ, yozuvi QORA */
    div[data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 15px !important;
    }
    
    /* Placeholder rangi (yozmasdan oldingi yozuv) */
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
    }

    /* 4. TUGMALAR VA TABLAR */
    .stButton>button { 
        background: linear-gradient(90deg, #ffffff 0%, #f1f5f9 100%) !important; 
        color: #000000 !important; 
        border: none !important; 
        border-radius: 10px !important; 
        font-weight: 800 !important; 
        height: 45px; 
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { 
        background: #38bdf8 !important; 
        color: #ffffff !important; 
        box-shadow: 0 0 20px #38bdf8; 
    }

    /* Tablarni sozlash */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent !important; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8 !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { color: #ffffff !important; border-bottom-color: #38bdf8 !important; }

    /* 5. SIDEBAR */
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        border-right: 1px solid #334155; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. CORE CONNECTIONS (O'ZGARISHSIZ) ---
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
    # Logo va Sarlavha
    st.markdown("""
        <div style="text-align: center; margin-top: 60px; margin-bottom: 40px;">
             <h1 style="color:#ffffff; font-size: 4rem; text-shadow: 0 0 20px #38bdf8;">🌌 Somo AI Infinity</h1>
             <p style="color:#94a3b8; font-size: 1.2rem;">Cheksiz imkoniyatlar sari qadam qo'ying</p>
        </div>
    """, unsafe_allow_html=True)

    t1, t2 = st.tabs(["🔑 TIZIMGA KIRISH", "📝 RO'YXATDAN O'TISH"])
    
    with t1:
        st.markdown("<br>", unsafe_allow_html=True)
        u = st.text_input("Foydalanuvchi nomi (Username)", key="login_u", placeholder="Loginni kiriting...")
        p = st.text_input("Maxfiy so'z (Parol)", type='password', key="login_p", placeholder="Parolni kiriting...")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("KIRISH", key="btn_login"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u), None)
            if user and str(user['password']) == hp:
                st.session_state.logged_in, st.session_state.username, st.session_state.messages = True, u, []
                cookies["somo_user"] = u
                cookies.save()
                st.rerun()
            else: st.error("⚠️ Login yoki parol xato!")

    with t2:
        st.markdown("<br>", unsafe_allow_html=True)
        nu = st.text_input("Yangi Login", key="reg_u", placeholder="O'ylab toping...")
        np = st.text_input("Yangi Parol", type='password', key="reg_p", placeholder="Kuchli parol...")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("HISOB YARATISH", key="btn_reg"):
            if nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("🎉 Muvaffaqiyatli! Kirish bo'limiga o'ting.")
    st.stop()

# --- 💬 5. MAIN APP (CHAT & DASHBOARD) ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
if st.sidebar.button("🗑 Yangi suhbat"):
    st.session_state.messages = []
    st.rerun()

up_file = st.sidebar.file_uploader("📂 Fayl yuklash", type=["pdf", "docx", "xlsx", "csv", "pptx"])

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Chiqish"):
    st.session_state.logged_in = False
    cookies["somo_user"] = ""
    cookies.save()
    st.rerun()

# Dashboard (Agar chat bo'sh bo'lsa)
if not st.session_state.messages:
    st.markdown(f"""
        <div style="text-align: center; padding: 50px 0;">
            <h1 style="font-size: 3.5rem; color: #ffffff; text-shadow: 0 0 10px #38bdf8;">Assalomu alaykum, {st.session_state.username}!</h1>
            <p style="color: #cbd5e1; font-size: 1.3rem; margin-top: 10px;">Bugun qanday muammoni hal qilamiz?</p>
        </div>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <div style="background: #ffffff; color: #000; padding: 25px; border-radius: 15px; width: 250px; text-align: center;">
                <h3 style="color:#000;">🧠 Tahlil</h3>
                <p>Matematika va fanlar.</p>
            </div>
            <div style="background: #ffffff; color: #000; padding: 25px; border-radius: 15px; width: 250px; text-align: center;">
                <h3 style="color:#000;">📑 Hujjat</h3>
                <p>Fayllar bilan ishlash.</p>
            </div>
            <div style="background: #ffffff; color: #000; padding: 25px; border-radius: 15px; width: 250px; text-align: center;">
                <h3 style="color:#000;">🎨 Ijod</h3>
                <p>Kreativ yechimlar.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Chat Xabarlari
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Chat Input (Pastki qism)
if prompt := st.chat_input("Savolingizni bu yerga yozing..."):
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
