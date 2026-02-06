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

# --- 🎨 2. MUKAMMAL DARK INPUT DIZAYN (RASMDAGIDEK) ---
st.markdown("""
    <style>
    /* 1. ASOSIY FON */
    .stApp { 
        background-color: #000000 !important;
        background: radial-gradient(circle at center, #000000 0%, #020617 100%) !important; 
        color: #ffffff !important; 
    }
    
    /* 2. INPUT MAYDONLARI (RASMDAGI STYLE) */
    /* Input qutisi foni - to'q kulrang */
    div[data-baseweb="input"] {
        background-color: #262730 !important; /* Rasmdagi to'q kulrang fon */
        border: none !important; /* Hoshiyani olib tashlash */
        border-radius: 8px !important; /* Burchaklarni salgina egish */
        padding: 5px !important;
    }
    
    /* Input ichidagi yozuv rangi */
    input[type="text"], input[type="password"] {
        color: #ffffff !important;
        caret-color: #38bdf8 !important; /* Kursor rangi */
    }
    
    /* Input bosilganda (Focus) */
    div[data-baseweb="input"]:focus-within {
        background-color: #31333F !important;
        box-shadow: none !important;
        border: 1px solid #38bdf8 !important; /* Bosganda nozik ko'k chiziq */
    }

    /* 3. SIDEBAR */
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        border-right: 1px solid #1e293b; 
    }
    
    /* 4. TUGMALAR (KIRISH TUGMASI) */
    .stButton>button { 
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%); 
        color: #38bdf8; 
        border: 1px solid #38bdf8; 
        border-radius: 8px; 
        font-weight: 700; 
        height: 45px; 
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { 
        background: #38bdf8; 
        color: #000000; 
        box-shadow: 0 0 15px #38bdf8; 
    }

    /* 5. LEBELLAR (Username, Parol so'zlari) */
    label[data-baseweb="label"] {
        color: #9ca3af !important; /* Och kulrang yozuv */
        font-size: 0.9rem !important;
    }

    /* Tizimdan chiqish tugmasi */
    .logout-btn>div>button { border-color: #f43f5e !important; color: #f43f5e !important; }
    .logout-btn>div>button:hover { background: #f43f5e !important; color: white !important; }
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
            return f"Jadval ma'lumotlari: {df.to_string()}"
        elif ext == 'pptx':
            prs = pptx.Presentation(file)
            return "\n".join([s.text for sl in prs.slides for s in sl.shapes if hasattr(s, "text")])
    except: return "Faylni tahlil qilishda xatolik yuz berdi."
    return ""

# --- 🔐 4. LOGIN INTERFACE (RASMDAGI KO'RINISH) ---
if not st.session_state.logged_in:
    # Logo va Sarlavha
    st.markdown("""
        <div style="text-align: center; margin-top: 50px; margin-bottom: 30px;">
             <h1 style="color:#38bdf8; font-size: 3.5rem; display: inline-block;">🌌 Somo AI Infinity</h1>
        </div>
    """, unsafe_allow_html=True)

    # Kirish Formasi (Markazda joylashtirish uchun Columns)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
        
        with t1:
            u = st.text_input("Username", placeholder="Login kiriting...")
            p = st.text_input("Parol", type='password', placeholder="Parol kiriting...")
            st.markdown("<br>", unsafe_allow_html=True) # Bo'sh joy
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
            nu, np = st.text_input("Yangi Username"), st.text_input("Yangi Parol", type='password')
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Hisob yaratish"):
                if nu and np:
                    user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                    st.success("🎉 Tayyor! Endi kirishga o'ting.")
    st.stop()

# --- 🖥 5. DASHBOARD & CHAT ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
if st.sidebar.button("🗑 Chatni tozalash"):
    st.session_state.messages = []
    st.rerun()
    
up_file = st.sidebar.file_uploader("📂 Fayl (PDF, Word, Excel, PPTX)", type=["pdf", "docx", "xlsx", "csv", "pptx"])

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="logout-btn">', unsafe_allow_html=True)
if st.sidebar.button("🚪 Tizimdan chiqish"):
    st.session_state.logged_in = False
    cookies["somo_user"] = ""
    cookies.save()
    st.rerun()
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Dashboard Kartalari
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="font-size: 3rem; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Assalomu alaykum, {st.session_state.username}! ✨
            </h1>
            <p style="font-size: 1.2rem; color: #94a3b8;">Somo AI - har qanday savol va fayllar bilan ishlay oladigan universal yordamchi.</p>
            <div style="display: flex; justify-content: center; gap: 15px; margin-top: 30px; flex-wrap: wrap;">
                <div style="background: rgba(56, 189, 248, 0.05); border: 1px solid #38bdf8; padding: 15px; border-radius: 12px; width: 250px;">
                    <h4 style="color:#38bdf8;">🧠 Aqlli Tahlil</h4>
                    <p style="font-size: 0.8rem;">Matematika, fizika, dasturlash va har qanday fan bo'yicha yordam.</p>
                </div>
                <div style="background: rgba(129, 140, 248, 0.05); border: 1px solid #818cf8; padding: 15px; border-radius: 12px; width: 250px;">
                    <h4 style="color:#818cf8;">📑 Hujjatlar</h4>
                    <p style="font-size: 0.8rem;">Word, PDF, Excel va PPTX fayllarni o'qiyman va xulosa qilaman.</p>
                </div>
                <div style="background: rgba(244, 63, 94, 0.05); border: 1px solid #f43f5e; padding: 15px; border-radius: 12px; width: 250px;">
                    <h4 style="color:#f43f5e;">✍️ Ijodkorlik</h4>
                    <p style="font-size: 0.8rem;">Sizga insho, kod, she'r yoki biznes-reja yozishda yordamlashaman.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Chat Logikasi
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Istalgan mavzuda savol bering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_msg = f"""Sening isming Somo AI. Yaratuvching: Usmonov Sodiq. 
        Foydalanuvchi: {st.session_state.username}. 
        Sen universal AIsan. 
        Javoblaringni tushunarli va professional tilda yoz. 
        Agar matematik formula kelsa, uni LaTeX ($...$) formatida ko'rsat."""
        
        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        if up_file:
            ctx.insert(1, {"role": "system", "content": f"Fayl mazmuni: {extract_universal_content(up_file)}"})
        
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        try: chat_sheet.append_row([datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
        except: pass
