import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from pypdf import PdfReader
import hashlib
from datetime import datetime

# --- KOSMIK QORA DIZAYN ---
st.set_page_config(page_title="Somo AI | Elite", page_icon="🚀", layout="wide")
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #111827 0%, #000000 100%); color: #e5e7eb; }
    .stChatMessage { border-radius: 20px; border: 1px solid #1f2937; background: #111827; }
    .stButton>button { background: linear-gradient(45deg, #4f46e5, #9333ea); border: none; color: white; border-radius: 12px; height: 3em; transition: 0.4s; }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(79, 70, 229, 0.4); }
    [data-testid="stSidebar"] { background-color: #030712; border-right: 1px solid #1f2937; }
    .welcome-card { background: rgba(31, 41, 55, 0.5); padding: 30px; border-radius: 20px; border: 1px solid #374151; text-align: center; margin-top: 50px; }
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
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        # Xatoni oldini olish uchun barqaror model ishlatamiz
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Ushbu xabarga 3 ta so'zdan iborat sarlavha ber: {message}"}]
        )
        return completion.choices[0].message.content.strip().replace('"', '')
    except: return "Yangi Suhbat"

def get_ai_response(messages, lang):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    sys_prompt = f"Sen Somo AI'san. Yaratuvching: Usmonov Sodiq. Sen dunyoda yagonasan. Javob tili: {lang}."
    full_msgs = [{"role": "system", "content": sys_prompt}] + messages
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=full_msgs).choices[0].message.content

# --- MULTILINGUAL (12+ tillar) ---
LANG_DICT = {
    "🇺🇿 O'zbekcha": {"w": "Xush kelibsiz", "s": "Savolingizni yozing...", "p": "PDF yuklang", "l": "Chiqish"},
    "🇺🇸 English": {"w": "Welcome", "s": "Ask me anything...", "p": "Upload PDF", "l": "Logout"},
    "🇷🇺 Русский": {"w": "Добро пожаловать", "s": "Задайте вопрос...", "p": "Загрузить PDF", "l": "Выйти"},
    "🇹🇷 Türkçe": {"w": "Hoş geldiniz", "s": "Bir şey sor...", "p": "PDF Yükle", "l": "Çıkış"},
    "🇩🇪 Deutsch": {"w": "Willkommen", "s": "Frag mich was...", "p": "PDF Hochladen", "l": "Abmelden"},
    "🇫🇷 Français": {"w": "Bienvenue", "s": "Posez une question...", "p": "Charger PDF", "l": "Quitter"},
    "🇸🇦 العربية": {"w": "أهلاً بك", "s": "اسألني أي شيء...", "p": "تحميل PDF", "l": "تسجيل الخروج"},
    "🇰🇷 한국어": {"w": "환영합니다", "s": "무엇이든 물어보세요...", "p": "PDF 업로드", "l": "로그아웃"},
    "🇯🇵 日本語": {"w": "ようこそ", "s": "何でも聞いてください...", "p": "PDFアップロード", "l": "ログアウト"},
    "🇨🇳 中文": {"w": "欢迎", "s": "问我任何事...", "p": "上传PDF", "l": "登出"}
}

# Sidebar sozlamalari
sel_lang_key = st.sidebar.selectbox("🌐 Tilni tanlang / Select Language", list(LANG_DICT.keys()))
L = LANG_DICT[sel_lang_key]

user_sheet, chat_sheet = connect_sheets()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- LOGIN (Faqat username va parol so'raladi) ---
if not st.session_state.logged_in:
    st.title(f"🚀 Somo AI | {sel_lang_key}")
    u = st.text_input("Username")
    p = st.text_input("Parol", type='password')
    if st.button("Kirish"):
        recs = user_sheet.get_all_records()
        hp = hashlib.sha256(p.encode()).hexdigest()
        user_data = next((r for r in recs if str(r['username']) == u and str(r['password']) == hp), None)
        if user_data and user_data['status'] == 'active':
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.messages = []
            st.rerun()
    st.stop()

# --- ASOSIY INTERFEYS ---
st.sidebar.markdown(f"### ✨ {st.session_state.username}")
if st.sidebar.button(L['l']):
    st.session_state.logged_in = False
    st.rerun()

up_pdf = st.sidebar.file_uploader(L['p'], type="pdf")

# KREATIV SALOMLASHISH EKRANI
if not st.session_state.messages:
    st.markdown(f"""
        <div class="welcome-card">
            <h1>🚀 {L['w']}, {st.session_state.username}!</h1>
            <p style="font-size: 1.2em;">Men Somo AI - Usmonov Sodiq tomonidan yaratilgan koinotdagi eng aqlli intellektman.</p>
            <p>Bugun qanday buyuk ishlarni amalga oshiramiz?</p>
            <div style="display: flex; justify-content: center; gap: 10px; margin-top: 20px;">
                <code style="color: #9333ea;">#Tahlil</code> <code style="color: #4f46e5;">#PDF_O'qish</code> <code style="color: #10b981;">#Sodiq_Genius</code>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Chat ko'rsatish
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input(L['s']):
    if not st.session_state.messages:
        st.session_state.current_title = generate_chat_title(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        context = list(st.session_state.messages)
        if up_pdf:
            pdf_txt = PdfReader(up_pdf).pages[0].extract_text()
            context[-1]["content"] += f"\n[DOC]: {pdf_txt[:3000]}"
            
        res = get_ai_response(context, sel_lang_key)
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        
        # Sheets-ga saqlash
        if chat_sheet:
            chat_sheet.append_row([st.session_state.get('current_title', 'Suhbat'), datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])

st.sidebar.caption(f"📍 {st.session_state.get('current_title', '')}")
