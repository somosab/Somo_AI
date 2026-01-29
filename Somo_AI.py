import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from pypdf import PdfReader
import hashlib
from datetime import datetime

# --- DESIGN & CONFIG ---
st.set_page_config(page_title="Somo AI | Elite", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #020617 0%, #000000 100%); color: #f1f5f9; }
    [data-testid="stSidebar"] { background-color: rgba(2, 6, 23, 0.98); border-right: 1px solid #1e293b; }
    .stButton>button { 
        background: linear-gradient(90deg, #2563eb, #7c3aed); color: white; 
        border-radius: 12px; border: none; font-weight: 600; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 25px rgba(124, 58, 237, 0.5); transform: translateY(-2px); }
    .stChatMessage { border-radius: 15px; border: 1px solid #1e293b; background: rgba(15, 23, 42, 0.6); }
    .glass-card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); padding: 2rem; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- CONNECTIONS ---
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

# --- HELPERS ---
def get_ai_response(messages, lang, name):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    sys_instr = f"Sen Somo AI'san. Yaratuvching: Usmonov Sodiq. Foydalanuvchi: {name}. Til: {lang}. Doimo samimiy va aqlli javob ber."
    full_query = [{"role": "system", "content": sys_instr}] + messages
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=full_query).choices[0].message.content

def create_title(text):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user", "content":f"Short title for: {text}"}])
        return res.choices[0].message.content.strip()[:30]
    except: return "Suhbat"

# --- AUTH SYSTEM ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="glass-card"><h1>🌌 Somo AI Galaxy</h1><p>Usmonov Sodiq loyihasi</p></div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Parol", type='password', key="l_p")
        if st.button("Kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user_data = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
            if user_data:
                if user_data['status'] == 'active':
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.messages = []
                    st.rerun()
                else: st.error("Siz bloklangansiz!")
            else: st.error("Login yoki parol xato!")

    with t2:
        nu = st.text_input("Yangi Username", key="r_u")
        np = st.text_input("Yangi Parol", type='password', key="r_p")
        if st.button("Ro'yxatdan o'tish"):
            recs = user_sheet.get_all_records()
            # MANA BU YERDA TAKRORIY USERNAMENI TEKSHIRAMIZ:
            if any(str(r['username']) == nu for r in recs):
                st.warning(f"⚠️ '{nu}' nomli foydalanuvchi allaqachon mavjud! Boshqa nom tanlang.")
            elif nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("✅ Muvaffaqiyatli ro'yxatdan o'tdingiz! Endi Kirish bo'limiga o'ting.")
    st.stop()

# --- MAIN INTERFACE ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
if st.sidebar.button("🗑 Chatni tozalash"):
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("🚪 Chiqish"):
    st.session_state.logged_in = False
    st.rerun()

up_pdf = st.sidebar.file_uploader("📄 PDF Tahlil", type="pdf")

# Welcome Banner
if not st.session_state.messages:
    st.markdown(f'<div class="glass-card"><h2>Xush kelibsiz, {st.session_state.username}! 👋</h2><p>Men Somo AI, sizga yordam berishga tayyorman.</p></div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Xabaringizni yozing..."):
    if not st.session_state.messages:
        st.session_state.chat_title = create_title(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        context = list(st.session_state.messages)
        if up_pdf:
            pdf_txt = "".join([p.extract_text() for p in PdfReader(up_pdf).pages[:3]])
            context[-1]["content"] += f"\n\n[Hujjat]: {pdf_txt[:2000]}"
            
        res = get_ai_response(context, "O'zbekcha", st.session_state.username)
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        
        if chat_sheet:
            chat_sheet.append_row([st.session_state.get('chat_title', 'Suhbat'), datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
