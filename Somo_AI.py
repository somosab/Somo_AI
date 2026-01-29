import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from pypdf import PdfReader
import hashlib
from datetime import datetime

# --- ULTRA MODERN DESIGN (CSS) ---
st.set_page_config(page_title="Somo AI | Elite Analyst", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    /* Asosiy fon va matn ranglari */
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #f8fafc; }
    
    /* Sidebar dizayni */
    [data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.95); border-right: 1px solid #1e293b; }
    
    /* Tugmalar dizayni */
    .stButton>button { 
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%); 
        color: white; border-radius: 12px; border: none; font-weight: bold;
        transition: 0.3s all ease-in-out;
    }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(59, 130, 246, 0.6); }
    
    /* Chat xabarlari */
    .stChatMessage { border-radius: 20px; border: 1px solid #1e293b; background: rgba(30, 41, 59, 0.5); }
    
    /* Glassmorphism kartalari */
    .welcome-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 40px; border-radius: 30px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KONNEKTORLAR ---
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

# --- MULTILINGUAL (15 Tillar) ---
LANG_DICT = {
    "🇺🇿 O'zbekcha": {"w": "Xush kelibsiz", "s": "Savolingizni yozing...", "p": "PDF Tahlil", "l": "Chiqish", "c": "Tozalash", "reg": "Ro'yxatdan o'tish", "log": "Kirish"},
    "🇺🇸 English": {"w": "Welcome", "s": "Ask me anything...", "p": "PDF Analysis", "l": "Logout", "c": "Clear Chat", "reg": "Sign Up", "log": "Login"},
    "🇷🇺 Русский": {"w": "Добро пожаловать", "s": "Задайте вопрос...", "p": "PDF Анализ", "l": "Выход", "c": "Очистить", "reg": "Регистрация", "log": "Вход"},
    "🇹🇷 Türkçe": {"w": "Hoş geldiniz", "s": "Bir şey sor...", "p": "PDF Analizi", "l": "Çıkış", "c": "Temizle", "reg": "Kayıt Ol", "log": "Giriş"},
    "🇸🇦 العربية": {"w": "أهلاً بك", "s": "اسألني أي شيء...", "p": "تحليل PDF", "l": "خروج", "c": "مسح", "reg": "تسجيل", "log": "دخول"},
    # Boshqa tillar (Fransuz, Nemis, Yapon, Koreys va h.k.)
}

# --- FUNKSIYALAR ---
def get_ai_response(messages, lang, name):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    sys_prompt = f"Sen Somo AI'san. Yaratuvching: Usmonov Sodiq. Foydalanuvchi: {name}. Doimo ismi bilan murojaat qil. Til: {lang}. Sen juda aqllisan."
    full_msgs = [{"role": "system", "content": sys_prompt}] + messages
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=full_msgs).choices[0].message.content

def create_title(text):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user", "content":f"Title (max 3 words): {text}"}])
        return res.choices[0].message.content.strip()
    except: return "Yangi Suhbat"

# --- TIZIMGA KIRISH VA REGISTRATSIYA ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="welcome-card"><h1>🌌 Somo AI Galaxy</h1></div>', unsafe_allow_html=True)
    sel_lang = st.selectbox("🌐 Tilni tanlang / Choose Language", list(LANG_DICT.keys()))
    L = LANG_DICT[sel_lang]
    
    t1, t2 = st.tabs([f"🔑 {L['log']}", f"📝 {L['reg']}"])
    
    with t1:
        u = st.text_input("Username", key="u_login")
        p = st.text_input("Parol", type='password', key="p_login")
        if st.button(L['log']):
            users = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user_data = next((r for r in users if r['username'] == u and r['password'] == hp), None)
            if user_data and user_data['status'] == 'active':
                st.session_state.logged_in = True
                st.session_state.username = u
                st.session_state.messages = []
                st.rerun()
            else: st.error("Login xato yoki siz bloklangansiz!")

    with t2:
        nu = st.text_input("Yangi Username", key="u_reg")
        np = st.text_input("Yangi Parol", type='password', key="p_reg")
        if st.button(L['reg']):
            if nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("Tabriklaymiz! Endi Kirish bo'limiga o'ting.")
    st.stop()

# --- ASOSIY CHAT ---
L = LANG_DICT[st.sidebar.selectbox("🌐 Til", list(LANG_DICT.keys()))]
st.sidebar.markdown(f"### 👤 {st.session_state.username}")

if st.sidebar.button(f"🗑 {L['c']}"):
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button(f"🚪 {L['l']}"):
    st.session_state.logged_in = False
    st.rerun()

up_pdf = st.sidebar.file_uploader(L['p'], type="pdf")

# Welcome Banner
if not st.session_state.messages:
    st.markdown(f"""
        <div class="welcome-card">
            <h1 style="background: linear-gradient(90deg, #3b82f6, #9333ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Salom, {st.session_state.username}!
            </h1>
            <p>Men Somo AI - koinotdagi eng mukammal tahlilchi. Bugun nimalarni kashf etamiz?</p>
        </div>
    """, unsafe_allow_html=True)

# Chat ko'rsatish
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input(L['s']):
    if not st.session_state.messages:
        st.session_state.chat_title = create_title(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        context = list(st.session_state.messages)
        if up_pdf:
            reader = PdfReader(up_pdf) # pypdf integratsiyasi
            pdf_text = "".join([page.extract_text() for page in reader.pages[:3]])
            context[-1]["content"] += f"\n\n[PDF MA'LUMOTI]: {pdf_text[:2000]}"
        
        response = get_ai_response(context, "O'zbekcha", st.session_state.username)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Google Sheets saqlash (AI sarlavhasi bilan)
        if chat_sheet:
            chat_sheet.append_row([
                st.session_state.get('chat_title', 'Suhbat'), 
                datetime.now().strftime("%H:%M"), 
                st.session_state.username, 
                "AI", 
                prompt[:1000]
            ])
