import streamlit as st
import pandas as pd
import gspread
import hashlib
import docx2txt  # Word uchun yanada kuchliroq kutubxona
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime

# --- 🌌 DIZAYN ---
st.set_page_config(page_title="Somo AI | Universal Analyst", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #020617; color: #f1f5f9; }
    .stButton>button { background: linear-gradient(90deg, #2563eb, #7c3aed); color: white; border-radius: 12px; }
    .stChatMessage { border-radius: 15px; background: rgba(30, 41, 59, 0.7); border: 1px solid #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 BAZA ---
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

# --- 📁 KUCHAYTIRILGAN FAYL O'QUVCHI ---
def extract_content(file):
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'pdf':
            return "".join([p.extract_text() for p in PdfReader(file).pages])
        elif ext == 'docx':
            # docx2txt formulalarni va matnlarni aniqroq ajratadi
            return docx2txt.process(file)
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)
            return df.to_string()
    except Exception as e: return f"Xato: {e}"
    return ""

# --- 👤 LOGIN (Unique User) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    with t1:
        u, p = st.text_input("Username"), st.text_input("Parol", type='password')
        if st.button("Kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
            if user and user['status'] == 'active':
                st.session_state.logged_in, st.session_state.username = True, u
                st.session_state.messages = []
                st.rerun()
    with t2:
        nu, np = st.text_input("Yangi Username"), st.text_input("Yangi Parol", type='password')
        if st.button("Ro'yxatdan o'tish"):
            recs = user_sheet.get_all_records()
            if any(str(r['username']) == nu for r in recs): st.warning("Bu ism band!")
            elif nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("Tayyor! Kirishga o'ting.")
    st.stop()

# --- 💬 CHAT ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
if st.sidebar.button("🗑 Chatni tozalash"):
    st.session_state.messages = []
    st.rerun()

up_file = st.sidebar.file_uploader("📄 Fayl tahlili (PDF, Word, Excel, CSV)", type=["pdf", "docx", "xlsx", "csv"])

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Somo AI ga savol bering..."):
    # Admin panel uchun sarlavha
    if not st.session_state.messages: st.session_state.chat_title = prompt[:30]

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_instr = f"Sen Somo AI'san. Yaratuvching: Usmonov Sodiq. Foydalanuvchi: {st.session_state.username}. Har doim unga ismi bilan murojaat qil. Matematik misollarni qadamba-qadam yechib ber."
        
        context_msgs = [{"role": "system", "content": sys_instr}] + st.session_state.messages
        if up_file:
            f_text = extract_content(up_file)
            # Fayl mazmunini tizimli ravishda uzatish
            context_msgs.insert(1, {"role": "system", "content": f"Foydalanuvchi yuklagan hujjat mazmuni: {f_text}"})
        
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=context_msgs).choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        
        if chat_sheet:
            chat_sheet.append_row([st.session_state.chat_title, datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
