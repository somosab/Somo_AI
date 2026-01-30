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

# --- 🛰 MAXIMAL BLACK DESIGN ---
st.set_page_config(page_title="Somo AI | Deep Space", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    /* Fonni butunlay qora va to'q ko'k gradiyent qildik */
    .stApp { 
        background: radial-gradient(circle at center, #000000 0%, #020617 100%); 
        color: #ffffff; 
    }
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        border-right: 1px solid #1e293b; 
    }
    
    /* Xabarlar dizayni (Glassmorphism qora fonda) */
    .stChatMessage { 
        border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.05) !important; 
        background: rgba(15, 23, 42, 0.8) !important; 
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }
    
    /* Neon tugmalar */
    .stButton>button { 
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%); 
        color: #38bdf8; border: 1px solid #38bdf8;
        border-radius: 10px; font-weight: 700; transition: 0.4s;
    }
    .stButton>button:hover { 
        background: #38bdf8; color: #000000;
        box-shadow: 0 0 20px #38bdf8; 
    }
    
    /* Matematik LaTeX rangi */
    .katex { color: #38bdf8 !important; }
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

def extract_universal_content(file):
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'pdf': return "".join([p.extract_text() for p in PdfReader(file).pages])
        elif ext == 'docx': return mammoth.extract_raw_text(file).value
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)
            return df.head(20).to_string()
        elif ext == 'pptx':
            prs = pptx.Presentation(file)
            return "\n".join([shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text")])
    except: return "Faylni o'qishda xatolik yuz berdi."
    return ""

# --- 🔐 AUTHENTICATION (Xato parolni ogohlantirish bilan) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:#38bdf8;">🌌 Somo AI Infinity</h1>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    
    with t1:
        u = st.text_input("Username", placeholder="Ismingizni yozing")
        p = st.text_input("Parol", type='password', placeholder="Parolingizni kiriting")
        if st.button("Kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u), None)
            
            if user:
                if str(user['password']) == hp:
                    if user['status'] == 'active':
                        st.session_state.logged_in, st.session_state.username, st.session_state.messages = True, u, []
                        st.rerun()
                    else: st.error("❌ Hisobingiz bloklangan!")
                else: st.error("⚠️ Parol noto'g'ri! Iltimos, qaytadan urinib ko'ring.")
            else: st.error("🔍 Bunday foydalanuvchi topilmadi!")

    with t2:
        nu, np = st.text_input("Yangi Username"), st.text_input("Yangi Parol", type='password')
        if st.button("Hisob ochish"):
            if nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("🎉 Muvaffaqiyatli! Endi kirish bo'limiga o'ting.")
    st.stop()

# --- 💬 CHAT INTERFEYS ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
up_file = st.sidebar.file_uploader("📂 Fayllarni tahlil qilish", type=["pdf", "docx", "xlsx", "csv", "pptx"])

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Somo AI ga savol bering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_msg = f"""Sen Somo AI'san. Yaratuvchi: Usmonov Sodiq. 
        Matematikani FAQAT LaTeX formatida yoz ($...$). 
        Masalan, a+2/a misolini $a + \\frac{{2}}{{a}}$ kabi ko'rsat.
        Foydalanuvchi: {st.session_state.username}."""
        
        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        if up_file:
            ctx.insert(1, {"role": "system", "content": f"Fayl: {extract_universal_content(up_file)}"})
        
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        
        try:
            chat_sheet.append_row([prompt[:30], datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
        except: pass
