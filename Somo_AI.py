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

# --- 🎨 2. MUKAMMAL INFINITY DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* 1. MAJBURIY DARK REJIM */
    :root { color-scheme: dark !important; }
    
    /* 2. ASOSIY FON (RADIAL GRADIENT) */
    .stApp { 
        background: radial-gradient(circle at center, #000000 0%, #020617 100%) !important; 
        color: #ffffff !important; 
    }
    
    /* 3. INPUT MAYDONLARI (OQ FONNI YO'QOTISH VA TO'Q QILISH) */
    div[data-baseweb="input"], [data-testid="stTextInput"] div, [data-testid="stForm"] {
        background-color: #0f172a !important; /* To'q ko'k-qora */
        border: 1px solid rgba(56, 189, 248, 0.3) !important; /* Neon havorang hoshiya */
        border-radius: 12px !important;
        color: white !important;
    }
    input {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #38bdf8 !important;
    }
    
    /* 4. SIDEBAR (QOP-QORA) */
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        border-right: 1px solid #1e293b; 
    }
    
    /* 5. TUGMALAR (NEON EFFEKT) */
    .stButton>button { 
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%); 
        color: #38bdf8; 
        border: 1px solid #38bdf8; 
        border-radius: 10px; 
        font-weight: 600; 
        transition: all 0.3s ease;
        height: 45px; width: 100%;
    }
    .stButton>button:hover { 
        background: #38bdf8; 
        color: #000000; 
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.6); 
    }

    /* 6. CHAT XABARLARI (GLASSMORPHISM) */
    .stChatMessage { 
        background: rgba(30, 41, 59, 0.7) !important; 
        border: 1px solid rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(10px);
        border-radius: 15px;
        margin-bottom: 10px;
    }
    
    /* 7. MATH FORMULALAR RANGI */
    .katex { color: #38bdf8 !important; font-size: 1.1em !important; }

    /* Tizimdan chiqish tugmasi (Qizil) */
    .logout-btn>div>button { border-color: #f43f5e !important; color: #f43f5e !important; }
    .logout-btn>div>button:hover { background: #f43f5e !important; color: white !important; box-shadow: 0 0 15px rgba(244, 63, 94, 0.6); }
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

# --- 🔐 4. LOGIN INTERFACE ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 style="text-align:center; color:#38bdf8; margin-top:80px; font-size: 3rem;">🌌 Somo AI Infinity</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#94a3b8; margin-bottom: 30px;">Universal aqlli yordamchi tizimi</p>', unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
        with t1:
            u = st.text_input("Username", key="login_user")
            p = st.text_input("Parol", type='password', key="login_pass")
            if st.button("Kirish", use_container_width=True):
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
            if st.button("Hisob yaratish", use_container_width=True):
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

# Dashboard Kartalari (HTML)
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div style="text-align: center; padding: 20px 0 40px 0;">
            <h1 style="font-size: 3.5rem; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;">
                Assalomu alaykum, {st.session_state.username}! ✦
            </h1>
            <p style="font-size: 1.2rem; color: #64748b;">Somo AI - Sizning shaxsiy universal yordamchingiz.</p>
        </div>
        
        <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-bottom: 40px;">
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #38bdf8; padding: 20px; border-radius: 16px; width: 250px; text-align: center; box-shadow: 0 4px 20px rgba(56, 189, 248, 0.1);">
                <h3 style="color:#38bdf8; margin-bottom: 10px;">🧠 Aqlli Tahlil</h3>
                <p style="font-size: 0.9rem; color: #cbd5e1;">Matematika, IT, Fizika va har qanday murakkab fanlar bo'yicha yordam.</p>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #818cf8; padding: 20px; border-radius: 16px; width: 250px; text-align: center; box-shadow: 0 4px 20px rgba(129, 140, 248, 0.1);">
                <h3 style="color:#818cf8; margin-bottom: 10px;">📑 Hujjatlar</h3>
                <p style="font-size: 0.9rem; color: #cbd5e1;">PDF, Word, Excel fayllarni o'qib, ular bo'yicha savol-javob qilaman.</p>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #f43f5e; padding: 20px; border-radius: 16px; width: 250px; text-align: center; box-shadow: 0 4px 20px rgba(244, 63, 94, 0.1);">
                <h3 style="color:#f43f5e; margin-bottom: 10px;">✍️ Ijodkorlik</h3>
                <p style="font-size: 0.9rem; color: #cbd5e1;">Rejalar, maqolalar, kodlar va kreativ g'oyalar yaratishda yordamchi.</p>
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
        Agar matematik formula kelsa, uni LaTeX formatida ko'rsat."""
        
        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        if up_file:
            ctx.insert(1, {"role": "system", "content": f"Fayl: {extract_universal_content(up_file)}"})
        
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        try: chat_sheet.append_row([datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
        except: pass
