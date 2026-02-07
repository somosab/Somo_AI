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

# --- 🎨 2. LIGHT PREMIUM DESIGN (OQ FON & MODERN KONTRAST) ---
st.markdown("""
    <style>
    /* ASOSIY FON - TOZA OQ */
    .stApp { 
        background-color: #ffffff !important; 
        color: #1e293b !important; 
    }
    
    /* SIDEBAR - MODERN TO'Q KO'K/QORA */
    [data-testid="stSidebar"] { 
        background-color: #0f172a !important; 
        border-right: 1px solid #e2e8f0; 
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* CHAT XABARLARI - YUMSHOQ RANGDA */
    .stChatMessage { 
        border-radius: 15px; 
        border: 1px solid #f1f5f9 !important; 
        background: #f8fafc !important; 
        color: #1e293b !important;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }

    /* INPUT MAYDONLARI (LOGIN & CHAT) */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
    }
    input { color: #1e293b !important; }

    /* TUGMALAR - PREMIUM GRADIENT */
    .stButton>button { 
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%) !important; 
        color: white !important; 
        border: none !important; 
        border-radius: 10px !important; 
        font-weight: 700; 
        transition: 0.3s; 
        height: 45px; 
    }
    .stButton>button:hover { 
        box-shadow: 0 5px 15px rgba(56, 189, 248, 0.4); 
        transform: translateY(-1px);
    }

    /* LATEX & FORMULALAR */
    .katex { color: #2563eb !important; font-size: 1.1em !important; }
    
    /* LOGIN SARIQ/QORA QISMLARNI TO'G'IRLASH */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent !important; }
    .stTabs [data-baseweb="tab"] { color: #64748b !important; }
    .stTabs [aria-selected="true"] { color: #38bdf8 !important; border-bottom-color: #38bdf8 !important; }
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
    except: return "Faylni tahlil qilishda xatolik."
    return ""

# --- 🔐 4. AUTHENTICATION ---
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:#1e293b; margin-top:50px;">🌌 Somo AI Infinity</h1>', unsafe_allow_html=True)
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
            else: st.error("⚠️ Xato!")
    with t2:
        nu, np = st.text_input("Yangi Username"), st.text_input("Yangi Parol", type='password')
        if st.button("Hisob yaratish"):
            if nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("🎉 Hisob yaratildi!")
    st.stop()

# --- 💬 5. MAIN INTERFACE ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
if st.sidebar.button("🗑 Chatni tozalash"):
    st.session_state.messages = []
    st.rerun()

up_file = st.sidebar.file_uploader("📂 Fayl yuklash", type=["pdf", "docx", "xlsx", "csv", "pptx"])
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Tizimdan chiqish"):
    st.session_state.logged_in = False
    cookies["somo_user"] = ""
    cookies.save()
    st.rerun()

# --- ✨ KREATIV DASHBOARD (Saqlab qolindi) ---
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="font-size: 3rem; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Assalomu alaykum, {st.session_state.username}! ✨
            </h1>
            <p style="font-size: 1.2rem; color: #64748b;">Somo AI - har qanday savol va fayllar bilan ishlay oladigan universal yordamchi.</p>
            <div style="display: flex; justify-content: center; gap: 15px; margin-top: 30px;">
                <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 15px; width: 220px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    <h4 style="color:#38bdf8;">🧠 Aqlli Tahlil</h4>
                    <p style="font-size: 0.85rem; color: #64748b;">Aniq va tabiiy fanlar bo'yicha yordam.</p>
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 15px; width: 220px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    <h4 style="color:#818cf8;">📑 Hujjatlar</h4>
                    <p style="font-size: 0.85rem; color: #64748b;">Hujjatlarni tahlil qilish va xulosa.</p>
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 15px; width: 220px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    <h4 style="color:#f43f5e;">✍️ Ijodkorlik</h4>
                    <p style="font-size: 0.85rem; color: #64748b;">Insho, kod va biznes-reja yaratish.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Chatni ko'rsatish
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Savolingizni bu yerga yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_msg = f"""Sening isming Somo AI. Yaratuvching: Usmonov Sodiq. 
        Foydalanuvchi: {st.session_state.username}. Sen universal AIsan. 
        Javoblarni professional tilda va Markdown formatida yoz."""
        
        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        if up_file:
            ctx.insert(1, {"role": "system", "content": f"Fayl: {extract_universal_content(up_file)}"})
        
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        try: chat_sheet.append_row([datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
        except: pass
