import streamlit as st
import pandas as pd
import gspread
import hashlib
import mammoth
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime

# --- 1. PREMIUM GLASSMORPHISM DIZAYN ---
st.set_page_config(page_title="Somo AI | Elite Analyst", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    /* Asosiy fon */
    .stApp { 
        background: radial-gradient(circle at top right, #0f172a 0%, #020617 100%); 
        color: #f1f5f9; 
    }
    
    /* Xabarlar dizayni (Glassmorphism) */
    .stChatMessage { 
        border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        background: rgba(30, 41, 59, 0.4) !important; 
        backdrop-filter: blur(15px);
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: rgba(15, 23, 42, 0.98); 
        border-right: 1px solid #1e293b; 
    }
    
    /* Tugmalar */
    .stButton>button { 
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); 
        color: white; border-radius: 14px; border: none; font-weight: 700;
        height: 50px; transition: 0.5s; text-transform: uppercase;
    }
    .stButton>button:hover { 
        transform: scale(1.03); 
        box-shadow: 0 0 25px rgba(139, 92, 246, 0.5); 
    }
    
    /* Matematik LaTeX ifodalarini chiroyli qilish */
    .katex { font-size: 1.2em !important; color: #60a5fa !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BAZA VA FAYL SYSTEMASI ---
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

def read_file(file):
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'docx':
            # Mammoth Word ichidagi murakkab belgilarni eng yaxshi o'qiydi
            return mammoth.extract_raw_text(file).value
        elif ext == 'pdf':
            return "".join([p.extract_text() for p in PdfReader(file).pages])
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)
            return df.to_string()
    except Exception as e: return f"Fayl xatosi: {e}"
    return ""

# --- 3. LOGIN (Unique Registration) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div style="text-align:center; padding-top:50px;"><h1>🌌 Somo AI Galaxy</h1><p>Intelligence Redefined</p></div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔒 Kirish", "✍️ Ro'yxatdan o'tish"])
    
    with t1:
        u, p = st.text_input("Username", key="l_u"), st.text_input("Parol", type='password', key="l_p")
        if st.button("Kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
            if user and user['status'] == 'active':
                st.session_state.logged_in, st.session_state.username, st.session_state.messages = True, u, []
                st.rerun()
            else: st.error("Ma'lumotlar xato yoki bloklangansiz!")

    with t2:
        nu, np = st.text_input("Yangi Username", key="r_u"), st.text_input("Yangi Parol", type='password', key="r_p")
        if st.button("Hisobni yaratish"):
            recs = user_sheet.get_all_records()
            if any(str(r['username']) == nu for r in recs): st.warning("Bu ism band!")
            elif nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("Muvaffaqiyatli! Kirishga o'ting.")
    st.stop()

# --- 4. CHAT VA MATEMATIK TAHLIL ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
up_file = st.sidebar.file_uploader("📄 Fayl tahlili (Word, PDF, Excel)", type=["pdf", "docx", "xlsx", "csv"])

if st.sidebar.button("🗑 Chatni tozalash"):
    st.session_state.messages = []
    st.rerun()

# Xabarlarni ko'rsatish
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Somo AI sizni eshitadi..."):
    if not st.session_state.messages: st.session_state.chat_title = prompt[:30]

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        # SYSTEM PROMPT: Matematik LaTeX vizualizatsiyasi uchun eng muhim qadam
        sys_msg = f"""Sen Somo AI'san. Yaratuvching: Usmonov Sodiq. 
        Foydalanuvchi: {st.session_state.username}. 
        AMR: Matematik ifodalar, darajalar va kasrlarni FAQAT LaTeX formatida yoz. 
        Masalan: x^2 emas, $x^2$ deb yoz. a+2/a emas, $a + \\frac{{2}}{{a}}$ deb yoz. 
        Javoblaringni qadamba-qadam va tushunarli bayon qil."""
        
        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        if up_file:
            f_text = read_file(up_file)
            ctx.insert(1, {"role": "system", "content": f"Hujjat mazmuni: {f_text}"})
        
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        if chat_sheet:
            chat_sheet.append_row([st.session_state.chat_title, datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
