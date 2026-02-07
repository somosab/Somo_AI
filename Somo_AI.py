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

# --- 🛰 UNIVERSAL PREMIUM DESIGN ---
st.set_page_config(page_title="Somo AI | Universal Infinity", page_icon="🌌", layout="wide")

# Cookies manager sozlamasi
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 MUKAMMAL KONTRAST STYLING ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { 
        background: radial-gradient(circle at center, #000000 0%, #020617 100%) !important; 
        color: #ffffff !important; 
    }

    /* Sidebar dizayni */
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        border-right: 1px solid #1e293b; 
    }

    /* INPUT MAYDONLARI - OQ FON, QORA YOZUV (Mukammal Kontrast) */
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 2px solid #38bdf8 !important;
    }
    
    input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 600 !important;
    }

    /* CHAT INPUT (Pastdagi savol yozish joyi) */
    .stChatInputContainer textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 12px !important;
    }

    /* CHAT XABARLARI */
    .stChatMessage { 
        border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        background: rgba(15, 23, 42, 0.6) !important; 
        backdrop-filter: blur(15px);
        margin-bottom: 15px;
        padding: 15px;
    }

    /* TUGMALAR */
    .stButton>button { 
        background: #ffffff !important; 
        color: #000000 !important; 
        border: 2px solid #38bdf8 !important; 
        border-radius: 12px !important; 
        font-weight: 700; 
        transition: 0.4s; 
        height: 48px;
    }
    .stButton>button:hover { 
        background: #38bdf8 !important; 
        color: #ffffff !important; 
        box-shadow: 0 0 25px #38bdf8; 
    }

    /* Formula va Matn ranglari */
    .katex { color: #38bdf8 !important; font-size: 1.15em !important; }
    h1, h2, h3 { color: #ffffff !important; }
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

# --- 🍪 AUTO-LOGIN LOGIKASI ---
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
    st.markdown('<h1 style="text-align:center; color:#ffffff; font-size: 3.5rem; margin-top:50px;">🌌 Somo AI Infinity</h1>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    with t1:
        u = st.text_input("Username", placeholder="Ismingizni kiriting...")
        p = st.text_input("Parol", type='password', placeholder="Maxfiy kod...")
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
        nu, np = st.text_input("Yangi Username", key="reg_u"), st.text_input("Yangi Parol", type='password', key="reg_p")
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
if st.sidebar.button("🚪 Tizimdan chiqish"):
    st.session_state.logged_in = False
    cookies["somo_user"] = ""
    cookies.save()
    st.rerun()

# --- ✨ DASHBOARD ---
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="font-size: 3.5rem; background: linear-gradient(90deg, #38bdf8, #ffffff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Assalomu alaykum, {st.session_state.username}! ✨
            </h1>
            <p style="font-size: 1.3rem; color: #94a3b8;">Somo AI - Mukammallikka yo'l.</p>
            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 40px;">
                <div style="background: #ffffff; color: #000; padding: 25px; border-radius: 20px; width: 230px; box-shadow: 0 10px 30px rgba(56,189,248,0.3);">
                    <h3 style="color:#000 !important;">🧠 Aqlli Tahlil</h3>
                    <p style="font-size: 0.9rem;">Ilmiy va texnik muammolar yechimi.</p>
                </div>
                <div style="background: #ffffff; color: #000; padding: 25px; border-radius: 20px; width: 230px; box-shadow: 0 10px 30px rgba(56,189,248,0.3);">
                    <h3 style="color:#000 !important;">📑 Hujjatlar</h3>
                    <p style="font-size: 0.9rem;">Fayllardan ma'lumot olish.</p>
                </div>
                <div style="background: #ffffff; color: #000; padding: 25px; border-radius: 20px; width: 230px; box-shadow: 0 10px 30px rgba(56,189,248,0.3);">
                    <h3 style="color:#000 !important;">✍️ Ijodkorlik</h3>
                    <p style="font-size: 0.9rem;">Kod, insho va rejalar yaratish.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Chatni ko'rsatish
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Istalgan mavzuda savol bering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_msg = f"""Sening isming Somo AI. Yaratuvching: Usmonov Sodiq. 
        Foydalanuvchi: {st.session_state.username}. 
        Sen universal AIsan. Matematika, dasturlash, til, tarix va boshqa barcha sohalarda professional yordam berasan.
        Javoblaringni tushunarli va chiroyli formatda (Markdown, LaTeX) yoz."""
        
        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        if up_file:
            ctx.insert(1, {"role": "system", "content": f"Yuklangan fayl: {extract_universal_content(up_file)}"})
        
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        try: chat_sheet.append_row([datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
        except: pass
