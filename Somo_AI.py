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

# --- 🛰 LUXURY UNIVERSE DESIGN ---
st.set_page_config(page_title="Somo AI | Universal Infinity", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #000428, #004e92); color: #ffffff; }
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.8) !important; border-right: 1px solid #1e3a8a; }
    
    /* Neumorphism & Glassmorphism blend */
    .stChatMessage { 
        border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.15) !important; 
        background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(20px);
        margin: 15px 0; box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    
    /* 💎 Glow Buttons */
    .stButton>button { 
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); 
        color: white; border-radius: 15px; border: none; font-weight: 800;
        height: 55px; letter-spacing: 1px; transition: 0.5s ease;
    }
    .stButton>button:hover { 
        transform: scale(1.02); box-shadow: 0 0 30px rgba(0, 210, 255, 0.7); 
    }
    
    /* 📐 Math Presentation */
    .katex { font-size: 1.3em !important; color: #00f2fe !important; }
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

# --- 📂 ALL-IN-ONE FILE PARSER ---
def extract_universal_content(file):
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'pdf':
            return "".join([p.extract_text() for p in PdfReader(file).pages])
        elif ext == 'docx':
            return mammoth.extract_raw_text(file).value
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)
            return f"Jadval: {df.head(20).to_string()}"
        elif ext == 'pptx':
            prs = pptx.Presentation(file)
            return "\n".join([shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text")])
    except Exception as e: return f"Xato: {e}"
    return ""

# --- 🔐 AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; margin-top:100px;">🌌 Somo AI Infinity</h1>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "✍️ Ro'yxatdan o'tish"])
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
        nu, np = st.text_input("Yangi Login"), st.text_input("Yangi Parol", type='password')
        if st.button("Yaratish"):
            user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
            st.success("Muvaffaqiyatli!")
    st.stop()

# --- 💬 CHAT & MATH ENGINE ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
up_file = st.sidebar.file_uploader("📂 Faylni tahlil qilish (Word, PDF, Excel, PPTX)", type=["pdf", "docx", "xlsx", "csv", "pptx"])

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Savolingizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        # SYSTEM INSTRUCTION: Eng muhim qism - Matematika va Shaxsiyat
        sys_msg = f"""Sen Somo AI'san. Yaratuvching: Usmonov Sodiq. Foydalanuvchi: {st.session_state.username}.
        QOIDALAR:
        1. Matematik ifodalarni FAQAT LaTeX formatida yoz ($...$). 
           Misol: $a^3 + \\frac{{8}}{{a^3}} = 180$.
        2. Hujjat yuklansa, uning ichidagi barcha ma'lumotlarni tahlil qil.
        3. Javoblar professional, chiroyli va qadamba-qadam bo'lsin."""
        
        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        if up_file:
            f_text = extract_universal_content(up_file)
            ctx.insert(1, {"role": "system", "content": f"Hujjat mazmuni: {f_text}"})
        
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        
        # Admin Panel uchun saqlash
        try:
            chat_sheet.append_row([prompt[:30], datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
        except: pass
