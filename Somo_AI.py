import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from pypdf import PdfReader
import hashlib
from datetime import datetime

# --- PREMIUM DIZAYN (CSS) ---
st.set_page_config(page_title="Somo AI | Ultimate Edition", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; }
    .chat-bubble { border-radius: 15px; padding: 15px; margin: 10px 0; border: 1px solid #334155; }
    .stButton>button { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border-radius: 8px; border: none; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4); }
    [data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.95); border-right: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKSIYALAR ---
def connect_sheets():
    try:
        gcp_info = dict(st.secrets["gcp_service_account"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_info, scope)
        client = gspread.authorize(creds)
        ss = client.open("Somo_Users")
        return ss.sheet1, ss.worksheet("ChatHistory")
    except: return None, None

def generate_chat_title(message):
    """AI xabarga qarab qisqa nom beradi"""
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": f"Ushbu gapdan 3-4 so'zlik sarlavha yasa: {message}"}]
    )
    return completion.choices[0].message.content.strip().replace('"', '')

def get_ai_response(messages, lang):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    sys_msg = f"Sen Somo AI'san. Yaratuvching: Usmonov Sodiq. Sen eng aqllisan. Til: {lang}."
    full_messages = [{"role": "system", "content": sys_msg}] + messages
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=full_messages).choices[0].message.content

# --- DATABASE VA LOGIN ---
user_sheet, chat_sheet = connect_sheets()

# Til tanlash lug'ati
LANGS = {
    "O'zbekcha": {"log": "Kirish", "reg": "Registratsiya", "user": "Foydalanuvchi", "pass": "Parol", "file": "PDF yuklash"},
    "English": {"log": "Login", "reg": "Register", "user": "Username", "pass": "Password", "file": "Upload PDF"}
}

if 'lang' not in st.session_state: st.session_state.lang = "O'zbekcha"
lang_choice = st.sidebar.selectbox("🌐 Language", list(LANGS.keys()))
st.session_state.lang = lang_choice
L = LANGS[st.session_state.lang]

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- TIZIMGA KIRISH ---
if not st.session_state.logged_in:
    st.title("🤖 Somo AI | Premium")
    t1, t2 = st.tabs([L['log'], L['reg']])
    with t1:
        u = st.text_input(L['user'], key="login_u")
        p = st.text_input(L['pass'], type='password', key="login_p")
        if st.button(L['log']):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            u_data = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
            if u_data and u_data['status'] == 'active':
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
    st.stop()

# --- ASOSIY CHAT ---
st.sidebar.title(f"✨ {st.session_state.username}")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

pdf_file = st.sidebar.file_uploader(L['file'], type="pdf")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.current_title = "Yangi Suhbat"

# Chatni ko'rsatish
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("..."):
    # Birinchi xabarda chat nomini yaratish
    if not st.session_state.messages:
        st.session_state.current_title = generate_chat_title(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        context = list(st.session_state.messages)
        if pdf_file:
            pdf_text = PdfReader(pdf_file).pages[0].extract_text() # pypdf ishlatildi
            context[-1]["content"] += f"\n[PDF]: {pdf_text[:2000]}"
            
        res = get_ai_response(context, st.session_state.lang)
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        
        # Google Sheets-ga saqlash (AI sarlavhasi bilan)
        if chat_sheet:
            chat_sheet.append_row([
                st.session_state.current_title, # AI yaratgan sarlavha
                datetime.now().strftime("%H:%M"), 
                st.session_state.username, 
                "User/AI", 
                prompt[:500]
            ])

st.sidebar.info(f"📍 Chat: {st.session_state.current_title}")
