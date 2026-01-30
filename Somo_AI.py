import streamlit as st
import pandas as pd
import gspread
import hashlib
import mammoth
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime

# --- 🌌 ULTRA PREMIUM SPACE DESIGN ---
st.set_page_config(page_title="Somo AI | Elite Analyst", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top, #0f172a 0%, #020617 100%); color: #f1f5f9; }
    
    /* Glassmorphism xabarlar */
    .stChatMessage { 
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        background: rgba(30, 41, 59, 0.5) !important; backdrop-filter: blur(12px);
        margin-bottom: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    /* Tugmalar dizayni */
    .stButton>button { 
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); 
        color: white; border-radius: 12px; border: none; font-weight: 700; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 0 20px rgba(124, 58, 237, 0.6); }

    /* Matematik LaTeX ifodalarini chiroyli qilish */
    .katex { font-size: 1.2em !important; color: #60a5fa !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 BAZA FUNKSIYALARI ---
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
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'pdf': return "".join([p.extract_text() for p in PdfReader(file).pages])
        elif ext == 'docx': return mammoth.extract_raw_text(file).value
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)
            return df.head(15).to_string()
    except: return "Faylni o'qishda xato."
    return ""

# --- 👤 LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'chat_title' not in st.session_state: st.session_state.chat_title = "Yangi suhbat"

if not st.session_state.logged_in:
    st.markdown('<div style="text-align:center; padding-top:100px;"><h1>🌌 Somo AI Galaxy</h1></div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    with t1:
        u, p = st.text_input("Username"), st.text_input("Parol", type='password')
        if st.button("Tizimga kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
            if user and user['status'] == 'active':
                st.session_state.logged_in, st.session_state.username, st.session_state.messages = True, u, []
                st.rerun()
    with t2:
        nu, np = st.text_input("Yangi Username"), st.text_input("Yangi Parol", type='password')
        if st.button("Hisob yaratish"):
            if nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("Tayyor! Kirishga o'ting.")
    st.stop()

# --- 💬 CHAT INTERFEYS ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
up_file = st.sidebar.file_uploader("📄 Fayl tahlili", type=["pdf", "docx", "xlsx", "csv"])

if st.sidebar.button("🗑 Tozalash"):
    st.session_state.messages = []
    st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Savolingizni yozing..."):
    # Xatolikni oldini olish: sarlavhani darhol o'rnatamiz
    if not st.session_state.messages:
        st.session_state.chat_title = prompt[:30]

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        # LaTeX buyrug'i matematikani chiroyli qiladi
        sys_instr = f"""Sen Somo AI'san. Yaratuvchi: Usmonov Sodiq. 
        Matematik ifodalarni daraja va kasrlari bilan FAQAT LaTeX formatida yoz ($...$). 
        Masalan: $a^3 + \\frac{{8}}{{a^3}}$. Foydalanuvchi: {st.session_state.username}."""
        
        ctx = [{"role": "system", "content": sys_instr}] + st.session_state.messages
        if up_file:
            f_text = extract_content(up_file)
            ctx.insert(1, {"role": "system", "content": f"Hujjat: {f_text}"})
        
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        
        # ARXIVLASH (Xatosiz versiya)
        try:
            if chat_sheet:
                chat_sheet.append_row([st.session_state.chat_title, datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
        except: pass
