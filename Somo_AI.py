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

# Cookies manager sozlamasi
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. SOFT PREMIUM DESIGN (Ko'zni asrovchi & Rangli) ---
st.markdown("""
    <style>
    /* 1. ASOSIY FON - KO'ZNI OLMASLIGI UCHUN YUMSHOQ TUS */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
        color: #334155 !important;
    }
    
    /* 2. SIDEBAR - TO'Q PREMYERA (Fayl yozuvlari ko'rinishi uchun) */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: #e2e8f0 !important;
    }

    /* 3. FAYL YUKLASH JOYINI TUZATISH (MUHIM!) */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
    }
    [data-testid="stFileUploader"] section {
        background-color: transparent !important;
    }
    [data-testid="stFileUploader"] div, [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small {
        color: #cbd5e1 !important; /* Yozuvlarni oq-kulrang qilamiz */
    }
    button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid #475569 !important;
        color: #e2e8f0 !important;
    }

    /* 4. CHAT XABARLARI - YUMSHOQ VA QUVNOQ */
    .stChatMessage {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 18px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        padding: 15px;
        margin-bottom: 15px;
    }
    /* Foydalanuvchi xabari rangi (Yumshoq ko'k) */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%) !important;
        border: 1px solid #bae6fd !important;
    }

    /* 5. TUGMALAR - KREATIV RANGBARANGLIK */
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600;
        transition: 0.3s;
        box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(99, 102, 241, 0.5);
    }

    /* 6. INPUT MAYDONLARI */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* 7. DASHBOARD KARTALARI DIZAYNI (Eski miyya va yangi ranglar) */
    .dashboard-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid #f1f5f9;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    .dashboard-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 35px -5px rgba(0, 0, 0, 0.1);
    }
    /* Rangli chiziqcha (Tepasida) */
    .card-accent {
        height: 6px;
        width: 100%;
        position: absolute;
        top: 0;
        left: 0;
    }
    .blue-accent { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
    .purple-accent { background: linear-gradient(90deg, #8b5cf6, #d946ef); }
    .orange-accent { background: linear-gradient(90deg, #f59e0b, #f43f5e); }

    .icon-box {
        font-size: 3.5rem;
        margin-bottom: 15px;
        display: inline-block;
    }
    h3 { color: #1e293b !important; font-weight: 700 !important; }
    p { color: #64748b !important; }

    /* Sarlavha Gradienti */
    .gradient-text {
        background: linear-gradient(90deg, #2563eb, #7c3aed, #db2777);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. CORE CONNECTIONS (O'zgarmadi) ---
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
    except: return "Faylni tahlil qilishda xatolik."
    return ""

# --- 🔐 4. AUTHENTICATION (Soft Design) ---
if not st.session_state.logged_in:
    st.markdown("""
        <div style="text-align: center; margin-top: 60px; margin-bottom: 40px;">
            <h1 style="font-size: 3.5rem; font-weight: 800; color: #1e293b; letter-spacing: -1px;">
                Somo AI <span class="gradient-text">Infinity</span>
            </h1>
            <p style="color: #64748b; font-size: 1.2rem;">Kreativlik va Intellekt uyg'unligi.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        t1, t2 = st.tabs(["🔑 Kirish", "✨ Ro'yxatdan o'tish"])
        with t1:
            u = st.text_input("Login", placeholder="Ismingiz...")
            p = st.text_input("Parol", type='password', placeholder="••••••••")
            if st.button("Boshlash", use_container_width=True):
                recs = user_sheet.get_all_records()
                hp = hashlib.sha256(p.encode()).hexdigest()
                user = next((r for r in recs if str(r['username']) == u), None)
                if user and str(user['password']) == hp:
                    st.session_state.logged_in, st.session_state.username, st.session_state.messages = True, u, []
                    cookies["somo_user"] = u
                    cookies.save()
                    st.rerun()
                else: st.error("⚠️ Login yoki parol noto'g'ri!")
        with t2:
            nu, np = st.text_input("Yangi Login"), st.text_input("Yangi Parol", type='password')
            if st.button("Hisob yaratish", use_container_width=True):
                if nu and np:
                    user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                    st.success("🎉 Muvaffaqiyatli! Endi kirishingiz mumkin.")
    st.stop()

# --- 💬 5. SIDEBAR (TUZATILGAN) ---
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;">
    <div style="width: 70px; height: 70px; background: linear-gradient(135deg, #6366f1, #d946ef); border-radius: 50%; margin: 0 auto 10px auto; display: flex; align-items: center; justify-content: center; font-size: 28px; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);">👤</div>
    <h3 style="color: white !important; margin: 0;">{st.session_state.username}</h3>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🗑 Chatni tozalash", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("<br><strong style='color: #94a3b8; font-size: 0.9rem;'>📁 FAYL YUKLASH</strong>", unsafe_allow_html=True)
up_file = st.sidebar.file_uploader("Fayl", type=["pdf", "docx", "xlsx", "csv", "pptx"], label_visibility="collapsed")

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Chiqish", use_container_width=True):
    st.session_state.logged_in = False
    cookies["somo_user"] = ""
    cookies.save()
    st.rerun()

# --- ✨ KREATIV DASHBOARD (Miyya & Rangbaranglik) ---
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div style="text-align: center; padding: 40px 0 40px 0;">
            <h1 style="font-size: 3.8rem; font-weight: 900; line-height: 1.1; color: #1e293b;">
                Xush kelibsiz, <span class="gradient-text">{st.session_state.username}!</span>
            </h1>
            <p style="font-size: 1.3rem; color: #64748b; max-width: 650px; margin: 15px auto;">
                Somo AI — ilm va ijod chegaralarini kengaytirish uchun sizning shaxsiy yordamchingiz.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # KARTALAR (Eski ikonkalarni qaytardik, lekin dizayn yangi)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-accent blue-accent"></div>
            <div class="icon-box">🧠</div>
            <h3>Aqlli Tahlil</h3>
            <p>Matematika, fizika va murakkab muammolar uchun aniq yechimlar.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-accent purple-accent"></div>
            <div class="icon-box">📄</div>
            <h3>Hujjatlar</h3>
            <p>Katta hajmli fayllarni o'qish, tahlil qilish va qisqa xulosa berish.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-accent orange-accent"></div>
            <div class="icon-box">🎨</div>
            <h3>Kreativ Ijod</h3>
            <p>Ilhomlantiruvchi g'oyalar, ssenariylar va biznes rejalar yaratish.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# Chatni ko'rsatish
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Input maydoni
if prompt := st.chat_input("Nimani o'rganamiz yoki yaratamiz?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_msg = f"""Sening isming Somo AI. Yaratuvching: Usmonov Sodiq. 
        Foydalanuvchi: {st.session_state.username}. 
        Sen mukammal bilimga ega universal yordamchisan. 
        Javoblarni chiroyli formatda (Markdown, Table, LaTeX) ber."""
        
        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        if up_file:
            ctx.insert(1, {"role": "system", "content": f"Fayl: {extract_universal_content(up_file)}"})
        
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        try: chat_sheet.append_row([datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
        except: pass
