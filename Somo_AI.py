import streamlit as st
import pandas as pd
import gspread
import hashlib
import mammoth  # Word formulalari uchun eng yaxshisi
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime

# --- 🌌 ULTRA PREMIUM DESIGN ---
st.set_page_config(page_title="Somo AI | Elite Analyst", layout="wide")
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #020617 0%, #000000 100%); color: #f1f5f9; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: rgba(2, 6, 23, 0.98); border-right: 1px solid #1e293b; }
    
    /* Glassmorphism Messages */
    .stChatMessage { 
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); 
        background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px;
    }
    
    /* Gradient Buttons */
    .stButton>button { 
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); 
        color: white; border-radius: 12px; border: none; font-weight: 700;
        height: 45px; transition: 0.4s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(139, 92, 246, 0.4); }
    
    /* Math text enhancement */
    .katex { font-size: 1.1em !important; color: #60a5fa !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 BAZA VA FUNKSIYALAR ---
def connect_sheets():
    try:
        gcp_info = dict(st.secrets["gcp_service_account"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_info, scope)
        return gspread.authorize(creds).open("Somo_Users").sheet1, gspread.authorize(creds).open("Somo_Users").worksheet("ChatHistory")
    except: return None, None

user_sheet, chat_sheet = connect_sheets()

def extract_word(file):
    # Mammoth formulalarni saqlab qolishga harakat qiladi
    result = mammoth.extract_raw_text(file)
    return result.value

# --- 👤 AUTH TIZIMI ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div style="text-align:center; padding: 50px;"><h1>🌌 Somo AI Galaxy</h1></div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Registratsiya"])
    with t1:
        u, p = st.text_input("Username"), st.text_input("Parol", type='password')
        if st.button("Kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
            if user and user['status'] == 'active':
                st.session_state.logged_in, st.session_state.username, st.session_state.messages = True, u, []
                st.rerun()
    # (Registratsiya qismi o'zgarishsiz qoladi)
    st.stop()

# --- 💬 CHAT ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
up_file = st.sidebar.file_uploader("📄 Hujjat (PDF, Word, Excel)", type=["pdf", "docx", "xlsx", "csv"])

if st.sidebar.button("🗑 Chatni tozalash"):
    st.session_state.messages = []
    st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Somo AI ga savol bering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        # SYSTEM PROMPT: Eng muhimi - LaTeX ishlatish buyrug'i
        sys_instr = f"""Sen Somo AI'san. Yaratuvching: Usmonov Sodiq. 
        Matematik ifodalar, kasrlar va darajalarni FAQAT LaTeX formatida yoz (masalan: $x^2$, $\\frac{{a}}{{b}}$). 
        Foydalanuvchi: {st.session_state.username}. Javobing chiroyli va qadamba-qadam bo'lsin."""
        
        ctx = [{"role": "system", "content": sys_instr}] + st.session_state.messages
        if up_file:
            text = extract_word(up_file) if up_file.name.endswith('docx') else ""
            ctx.insert(1, {"role": "system", "content": f"Hujjat mazmuni: {text}"})
        
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        
        if chat_sheet:
            chat_sheet.append_row(["Suhbat", datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
