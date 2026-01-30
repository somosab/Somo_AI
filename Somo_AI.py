import streamlit as st
import pandas as pd
import gspread
import hashlib
import mammoth
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime

# --- 1. LUXURY SPACE DESIGN ---
st.set_page_config(page_title="Somo AI | Elite Analyst", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    /* Asosiy fon va shriftlar */
    .stApp { 
        background: radial-gradient(circle at top, #0f172a 0%, #020617 100%); 
        color: #f1f5f9; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Sidebar dizayni */
    [data-testid="stSidebar"] { 
        background-color: rgba(15, 23, 42, 0.95); 
        border-right: 1px solid rgba(255, 255, 255, 0.1); 
    }
    
    /* Chat xabarlari (Glassmorphism) */
    .stChatMessage { 
        border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        background: rgba(30, 41, 59, 0.5) !important; 
        backdrop-filter: blur(12px);
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Tugmalar dizayni */
    .stButton>button { 
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); 
        color: white; 
        border-radius: 12px; 
        border: none; 
        font-weight: 700;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 0 20px rgba(124, 58, 237, 0.6); 
    }
    
    /* Matematik matnlar uchun maxsus rang */
    .katex { color: #60a5fa !important; font-size: 1.15em !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BAZA VA FAYL FUNKSIYALARI ---
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
        if ext == 'pdf':
            return "".join([p.extract_text() for p in PdfReader(file).pages])
        elif ext == 'docx':
            # Mammoth kutubxonasi Worddagi belgilarni saqlab qoladi
            result = mammoth.extract_raw_text(file)
            return result.value
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)
            return df.head(20).to_string()
    except Exception as e: return f"Faylni o'qishda xato: {e}"
    return ""

# --- 3. LOGIN TIZIMI ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div style="text-align:center; padding-top:100px;"><h1>🌌 Somo AI Galaxy</h1><p>Intelligence without limits</p></div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Parol", type='password')
        if st.button("Tizimga kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
            if user and user['status'] == 'active':
                st.session_state.logged_in, st.session_state.username = True, u
                st.session_state.messages = []
                st.rerun()
            else: st.error("Login xato yoki hisobingiz bloklangan!")

    with t2:
        nu = st.text_input("Yangi Username")
        np = st.text_input("Yangi Parol", type='password')
        if st.button("Hisob yaratish"):
            recs = user_sheet.get_all_records()
            if any(str(r['username']) == nu for r in recs): st.warning("Bu ism band!")
            elif nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("Tabriklaymiz! Endi kirish bo'limiga o'ting.")
    st.stop()

# --- 4. ASOSIY CHAT ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
sel_lang = st.sidebar.selectbox("🌐 Muloqot tili", ["O'zbekcha", "English", "Русский"])

if st.sidebar.button("🗑 Chatni tozalash"):
    st.session_state.messages = []
    st.rerun()

up_file = st.sidebar.file_uploader("📄 Fayl tahlili (PDF, Word, Excel, CSV)", type=["pdf", "docx", "xlsx", "csv"])

# Ekranni tozalash va xabarlarni chiqarish
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Savolingizni bu yerga yozing..."):
    # Sarlavha (Title) yaratish
    if not st.session_state.messages: st.session_state.chat_title = prompt[:30]

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        # SMART AI SYSTEM INSTRUCTION
        sys_instr = f"""Sen Somo AI'san. Yaratuvching: Usmonov Sodiq. 
        Foydalanuvchi: {st.session_state.username}. Til: {sel_lang}.
        DIQQAT: Matematik formulalarni va amallarni FAQAT LaTeX formatida yoz (masalan: $x^2$, $\\frac{{a}}{{b}}$). 
        Hujjat yuklansa, uni tahlil qil va savollarga javob ber."""
        
        context_msgs = [{"role": "system", "content": sys_instr}] + st.session_state.messages
        
        if up_file:
            f_content = extract_content(up_file)
            context_msgs.insert(1, {"role": "system", "content": f"Yuklangan hujjat mazmuni: {f_content}"})
        
        # Javob olish
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=context_msgs).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Arxivlash
        if chat_sheet:
            chat_sheet.append_row([st.session_state.chat_title, datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
