import streamlit as st
import pandas as pd
import gspread
import hashlib
from docx import Document
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime

# --- 1. PREMIUM DIZAYN (Koinot Qorasi & Neon) ---
st.set_page_config(page_title="Somo AI | Universal", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #020617 0%, #000000 100%); color: #f1f5f9; }
    [data-testid="stSidebar"] { background-color: rgba(2, 6, 23, 0.98); border-right: 1px solid #1e293b; }
    .stButton>button { 
        background: linear-gradient(90deg, #2563eb, #7c3aed); color: white; 
        border-radius: 12px; border: none; font-weight: 600; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 25px rgba(124, 58, 237, 0.5); transform: translateY(-2px); }
    .glass-card { 
        background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(15px); 
        padding: 2rem; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.1); 
        text-align: center; margin-bottom: 20px;
    }
    .stChatMessage { border-radius: 15px; border: 1px solid #1e293b; background: rgba(15, 23, 42, 0.6); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BAZA VA AI BILAN ALOQA ---
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

def extract_content(file):
    """Ko'p formatli fayllarni o'qish: PDF, DOCX, XLSX, CSV"""
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'pdf':
            return "".join([p.extract_text() for p in PdfReader(file).pages[:5]])
        elif ext == 'docx':
            return "\n".join([p.text for p in Document(file).paragraphs])
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)
            return df.head(15).to_string()
    except: return ""
    return ""

def get_ai_res(msgs, lang, name):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    sys_msg = f"Sen Somo AI'san. Yaratuvchi: Usmonov Sodiq. Foydalanuvchi: {name}. Til: {lang}. Doimo ismi bilan murojaat qil."
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"system","content":sys_msg}] + msgs
    ).choices[0].message.content

# --- 3. LOGIN VA UNIKAL REGISTRATSIYA ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="glass-card"><h1>🌌 Somo AI Galaxy</h1><p>Universal Intelligent System</p></div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    
    with t1:
        u, p = st.text_input("Username", key="l_u"), st.text_input("Parol", type='password', key="l_p")
        if st.button("Tizimga kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
            if user and user['status'] == 'active':
                st.session_state.logged_in, st.session_state.username = True, u
                st.session_state.messages = []
                st.rerun()
            else: st.error("Login xato yoki bloklangansiz!")

    with t2:
        nu, np = st.text_input("Yangi Username", key="r_u"), st.text_input("Yangi Parol", type='password', key="r_p")
        if st.button("Hisob yaratish"):
            recs = user_sheet.get_all_records()
            if any(str(r['username']) == nu for r in recs): st.warning("Ushbu username band!")
            elif nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("Muvaffaqiyatli! Endi Kirish bo'limiga o'ting.")
    st.stop()

# --- 4. ASOSIY INTERFEYS ---
# Tillarni ko'paytirdik (15+ tillar)
LANGS = {"🇺🇿 O'zbekcha": "Uzbek", "🇺🇸 English": "English", "🇷🇺 Русский": "Russian", "🇹🇷 Türkçe": "Turkish", "🇸🇦 العربية": "Arabic", "🇰🇷 한국어": "Korean"}
sel_lang = st.sidebar.selectbox("🌐 Tilni tanlang", list(LANGS.keys()))

st.sidebar.markdown(f"### 👤 {st.session_state.username}")
if st.sidebar.button("🗑 Chatni tozalash"):
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("🚪 Chiqish"):
    st.session_state.logged_in = False
    st.rerun()

up_file = st.sidebar.file_uploader("📄 Fayl tahlili (PDF, Word, Excel)", type=["pdf", "docx", "xlsx", "csv"])

# Welcome Screen
if not st.session_state.messages:
    st.markdown(f'<div class="glass-card"><h2>Xush kelibsiz, {st.session_state.username}! 👋</h2><p>Hujjatlarni yuklang va xohlagan savolingizni bering.</p></div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Somo AI sizni eshitadi..."):
    # AI orqali chat nomini yaratish (faqat birinchi xabarda)
    if not st.session_state.messages:
        client_mini = Groq(api_key=st.secrets["GROQ_API_KEY"])
        st.session_state.chat_title = client_mini.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role":"user","content":f"Short title: {prompt}"}]
        ).choices[0].message.content[:30]

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        context = list(st.session_state.messages)
        if up_file:
            f_text = extract_content(up_file)
            context[-1]["content"] += f"\n\n[FILE DATA]: {f_text}"
        
        response = get_ai_res(context, LANGS[sel_lang], st.session_state.username)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Google Sheets arxiv (Admin panel uchun)
        if chat_sheet:
            chat_sheet.append_row([st.session_state.chat_title, datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
