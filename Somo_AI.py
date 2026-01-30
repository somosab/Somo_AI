import streamlit as st
import pandas as pd
import gspread
import hashlib
from docx import Document
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime

# --- 🌌 PREMIUM SPACE DESIGN ---
st.set_page_config(page_title="Somo AI | Universal Analyst", page_icon="💎", layout="wide")
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

# --- 🔗 BAZA ULANISHI ---
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

# --- 📁 UNIVERSAL FILE PARSER ---
def extract_content(file):
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'pdf':
            return "".join([p.extract_text() for p in PdfReader(file).pages[:10]])
        elif ext == 'docx':
            return "\n".join([p.text for p in Document(file).paragraphs])
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)
            return f"Jadval sarlavhalari: {list(df.columns)}\nMa'lumotlar:\n{df.head(10).to_string()}"
    except Exception as e: return f"Faylni o'qishda xato: {e}"
    return ""

# --- 🔑 AUTH SYSTEM (UNIQUE USER) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="glass-card"><h1>🌌 Somo AI Galaxy</h1><p>Usmonov Sodiq Loyihasi</p></div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    
    with t1:
        u, p = st.text_input("Username", key="l_u"), st.text_input("Parol", type='password', key="l_p")
        if st.button("Kirish"):
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
        if st.button("Ro'yxatdan o'tish"):
            recs = user_sheet.get_all_records()
            if any(str(r['username']) == nu for r in recs): st.warning("Bu ism band!")
            elif nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("Muvaffaqiyatli! Kirish bo'limiga o'ting.")
    st.stop()

# --- 💬 MAIN CHAT INTERFACE ---
st.sidebar.markdown(f"### 👤 Foydalanuvchi: {st.session_state.username}")
sel_lang = st.sidebar.selectbox("🌐 Til", ["O'zbekcha", "English", "Русский", "Türkçe"])

if st.sidebar.button("🗑 Chatni tozalash"):
    st.session_state.messages = []
    st.rerun()

up_file = st.sidebar.file_uploader("📄 Fayl tahlili (PDF, Word, Excel, CSV)", type=["pdf", "docx", "xlsx", "csv"])

# Welcome
if not st.session_state.messages:
    st.markdown(f'<div class="glass-card"><h2>Xush kelibsiz, {st.session_state.username}! 👋</h2><p>Hujjatlarni yuklang va tahlilni boshlang.</p></div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Somo AI ga savol bering..."):
    # Sarlavha yaratish (Admin panel uchun)
    if not st.session_state.messages:
        try:
            temp_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            st.session_state.chat_title = temp_client.chat.completions.create(
                model="llama-3.1-8b-instant", messages=[{"role":"user","content":f"Short title: {prompt}"}]
            ).choices[0].message.content[:30]
        except: st.session_state.chat_title = "Yangi Suhbat"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_instr = f"Sen Somo AI'san. Yaratuvching: Usmonov Sodiq. Foydalanuvchi: {st.session_state.username}. Til: {sel_lang}."
        
        context_msgs = [{"role": "system", "content": sys_instr}] + st.session_state.messages
        if up_file:
            f_text = extract_content(up_file)
            context_msgs[-1]["content"] += f"\n\n[HUJJAT]: {f_text}"
        
        # Javob olish
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=context_msgs).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Bazaga saqlash
        if chat_sheet:
            chat_sheet.append_row([st.session_state.chat_title, datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
