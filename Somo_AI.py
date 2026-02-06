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

# --- 🛰 UNIVERSAL PREMIUM & AUTO-DARK DESIGN ---
st.set_page_config(page_title="Somo AI | Universal Infinity", page_icon="🌌", layout="wide")

# Cookies manager sozlamasi
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# BRAUZERNI AVTOMATIK DARK REJIMGA MAJBURLASH VA INPUTLARNI TUZATISH
st.markdown("""
    <style>
    /* Umumiy fonni qora qilish */
    .stApp { 
        background: radial-gradient(circle at center, #000000 0%, #020617 100%) !important; 
        color: #ffffff !important; 
    }
    
    /* Brauzerni Dark mode-ga majburlash */
    :root { color-scheme: dark !important; }

    /* Login/Parol maydonlarini qora va matnni oq qilish */
    div[data-baseweb="input"] {
        background-color: #111827 !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;
    }
    input {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #1e293b; }
    
    .stChatMessage { 
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.05) !important; 
        background: rgba(15, 23, 42, 0.8) !important; backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%); 
        color: #38bdf8; border: 1px solid #38bdf8; border-radius: 12px; 
        font-weight: 700; transition: 0.4s; height: 45px; width: 100%;
    }
    .stButton>button:hover { 
        background: #38bdf8; color: #000000; box-shadow: 0 0 20px #38bdf8; 
    }
    .logout-btn>div>button { border-color: #f43f5e !important; color: #f43f5e !important; }
    .logout-btn>div>button:hover { background: #f43f5e !important; color: white !important; }
    .katex { color: #38bdf8 !important; font-size: 1.1em !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 CORE CONNECTIONS ---
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

# --- 🍪 AVTOMATIK KIRISH LOGIKASI ---
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

# --- 🔐 AUTHENTICATION ---
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:#38bdf8; margin-top:50px;">🌌 Somo AI Infinity</h1>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Parol", type='password')
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
        if st.button("Hisob yaratish"):
            if nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("🎉 Tayyor! Endi kirishga o'ting.")
    st.stop()

# --- 💬 SIDEBAR CONTROL ---
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

# --- ✨ CREATIVE UNIVERSAL DASHBOARD ---
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="font-size: 3rem; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Assalomu alaykum, {st.session_state.username}! ✨
            </h1>
            <p style="font-size: 1.2rem; color: #94a3b8;">Somo AI - har qanday savol va fayllar bilan ishlay oladigan universal yordamchi.</p>
            <div style="display: flex; justify-content: center; gap: 15px; margin-top: 30px;">
                <div style="background: rgba(56, 189, 248, 0.05); border: 1px solid #38bdf8; padding: 15px; border-radius: 12px; width: 200px;">
                    <h4 style="color:#38bdf8;">🧠 Aqlli Tahlil</h4>
                    <p style="font-size: 0.8rem;">Matematika, fizika, dasturlash va barcha fanlardan yordam beraman.</p>
                </div>
                <div style="background: rgba(129, 140, 248, 0.05); border: 1px solid #818cf8; padding: 15px; border-radius: 12px; width: 200px;">
                    <h4 style="color:#818cf8;">📑 Hujjatlar</h4>
                    <p style="font-size: 0.8rem;">PDF, Excel va Word fayllarni o'qiyman va tahlil qilaman.</p>
                </div>
                <div style="background: rgba(244, 63, 94, 0.05); border: 1px solid #f43f5e; padding: 15px; border-radius: 12px; width: 200px;">
                    <h4 style="color:#f43f5e;">✍️ Ijodkorlik</h4>
                    <p style="font-size: 0.8rem;">Sizga insho, kod va loyihalar yaratishda yordamlashaman.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Istalgan mavzuda savol bering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_msg = f"Sening isming Somo AI. Yaratuvching: Usmonov Sodiq. Foydalanuvchi: {st.session_state.username}. Sen universal AIsan. Matematikani LaTeX formatida yoz."
        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        if up_file: ctx.insert(1, {"role": "system", "content": f"Fayl: {extract_universal_content(up_file)}"})
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        try: chat_sheet.append_row([datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
        except: pass
