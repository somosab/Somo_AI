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

# --- 🎨 2. ULTIMATE CREATIVE LIGHT DESIGN (Aurora Glassmorphism) ---
st.markdown("""
    <style>
    /* 1. JONLI ORQA FON (AURORA EFFECT) */
    .stApp {
        background: radial-gradient(circle at 0% 0%, #f0f9ff 0%, #ffffff 50%, #fdf4ff 100%);
        background-attachment: fixed;
    }
    
    /* 2. SIDEBAR - PREMIUM DARK (Kontrast uchun) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
        box-shadow: 5px 0 15px rgba(0,0,0,0.1);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    /* 3. INPUT MAYDONLARI - MODERN SOYA BILAN */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2) !important;
        transform: translateY(-1px);
    }
    input { color: #0f172a !important; font-weight: 500 !important; }

    /* 4. CHAT XABARLARI - "FLOAT" EFFEKTI */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(148, 163, 184, 0.1);
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(148, 163, 184, 0.15);
    }
    
    /* User Message Style */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%) !important;
        border: 1px solid #bae6fd !important;
    }

    /* 5. TUGMALAR - KREATIV GRADIENT */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px 0 rgba(139, 92, 246, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 20px 0 rgba(139, 92, 246, 0.5);
    }

    /* 6. Dashboard Kartalari Uchun CSS Classlar */
    .dashboard-card {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        transition: all 0.4s ease;
        cursor: pointer;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        height: 100%;
    }
    .dashboard-card:hover {
        transform: translateY(-10px);
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 20px 40px rgba(56, 189, 248, 0.15);
        border-color: #38bdf8;
    }
    .icon-box {
        font-size: 3rem;
        margin-bottom: 15px;
        background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 7. Matn va Sarlavhalar */
    h1, h2, h3 {
        color: #0f172a !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .gradient-text {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. CORE CONNECTIONS (O'zgarishsiz) ---
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

# --- 🔐 4. AUTHENTICATION (Chiroyli UI bilan) ---
if not st.session_state.logged_in:
    # Kirish sahifasi uchun maxsus vertikal markazlash
    st.markdown("""
        <div style="text-align: center; margin-top: 50px; margin-bottom: 30px;">
            <h1 style="font-size: 4rem; margin-bottom: 10px;">🌌</h1>
            <h1 style="font-size: 3.5rem; font-weight: 800; color: #0f172a;">Somo AI <span class="gradient-text">Infinity</span></h1>
            <p style="color: #64748b; font-size: 1.2rem;">Kreativlik va Intellektning yangi darajasi.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        t1, t2 = st.tabs(["🔑 Tizimga kirish", "📝 Yangi hisob"])
        with t1:
            u = st.text_input("Foydalanuvchi nomi", placeholder="Login")
            p = st.text_input("Maxfiy parol", type='password', placeholder="••••••••")
            if st.button("Tizimga kirish", use_container_width=True):
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
            if st.button("Ro'yxatdan o'tish", use_container_width=True):
                if nu and np:
                    user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                    st.success("🎉 Hisob muvaffaqiyatli yaratildi!")
    st.stop()

# --- 💬 5. MAIN INTERFACE ---
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 20px 0;">
    <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #3b82f6, #ec4899); border-radius: 50%; margin: 0 auto 10px auto; display: flex; align-items: center; justify-content: center; font-size: 30px;">👤</div>
    <h3 style="color: white !important;">{st.session_state.username}</h3>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🗑 Chatni tozalash", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("### 📂 Fayl Tahlili")
up_file = st.sidebar.file_uploader("Faylni yuklang", type=["pdf", "docx", "xlsx", "csv", "pptx"], label_visibility="collapsed")

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Chiqish", use_container_width=True):
    st.session_state.logged_in = False
    cookies["somo_user"] = ""
    cookies.save()
    st.rerun()

# --- ✨ KREATIV DASHBOARD (Oq fonda porlaydigan) ---
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div style="text-align: center; padding: 50px 0 30px 0;">
            <h1 style="font-size: 4rem; font-weight: 900; line-height: 1.2;">
                Salom, <span class="gradient-text">{st.session_state.username}!</span>
            </h1>
            <p style="font-size: 1.4rem; color: #64748b; max-width: 700px; margin: 20px auto;">
                Somo AI — bu shunchaki chat emas. Bu sizning bilim va ijod olamidagi cheksiz imkoniyatingiz.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # KARTALAR (Interaktiv)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="dashboard-card">
            <div class="icon-box">🧬</div>
            <h3 style="color:#1e293b !important;">Super Tahlil</h3>
            <p style="color:#64748b;">Murakkab fanlar, matematika va kodlash bo'yicha aniq yechimlar.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="dashboard-card">
            <div class="icon-box">📂</div>
            <h3 style="color:#1e293b !important;">Hujjatlar</h3>
            <p style="color:#64748b;">PDF, Word va jadvallarni soniyalar ichida o'qib, tahlil qilib beraman.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="dashboard-card">
            <div class="icon-box">🎨</div>
            <h3 style="color:#1e293b !important;">Kreativ Ijod</h3>
            <p style="color:#64748b;">Bloglar, insholar, ssenariylar va biznes g'oyalar yaratish.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

# Chatni ko'rsatish
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Input maydoni
if prompt := st.chat_input("Savol yoki topshiriqni yozing..."):
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
