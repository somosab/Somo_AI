import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from pypdf import PdfReader
import hashlib
import time
from datetime import datetime

# --- SAHIFANI SOZLASH ---
st.set_page_config(page_title="Somo AI | Elite Analyst", page_icon="🚀", layout="wide")

# --- MULTILINGUAL (KO'P TILLI) LUG'AT ---
LANG_DICT = {
    "O'zbekcha": {
        "welcome": "Xush kelibsiz", "login": "Kirish", "reg": "Ro'yxatdan o'tish",
        "user": "Foydalanuvchi nomi", "pass": "Parol", "btn_login": "Kirish",
        "btn_reg": "Ro'yxatdan o'tish", "sidebar_pdf": "PDF Tahlil", "logout": "Chiqish",
        "chat_placeholder": "Xabaringizni yozing...", "loading": "Somo AI o'ylamoqda..."
    },
    "English": {
        "welcome": "Welcome", "login": "Login", "reg": "Register",
        "user": "Username", "pass": "Password", "btn_login": "Login",
        "btn_reg": "Register", "sidebar_pdf": "PDF Analysis", "logout": "Logout",
        "chat_placeholder": "Type your message...", "loading": "Somo AI is thinking..."
    },
    "Русский": {
        "welcome": "Добро пожаловать", "login": "Вход", "reg": "Регистрация",
        "user": "Имя пользователя", "pass": "Пароль", "btn_login": "Войти",
        "btn_reg": "Регистрация", "sidebar_pdf": "PDF Анализ", "logout": "Выход",
        "chat_placeholder": "Введите сообщение...", "loading": "Somo AI думает..."
    }
}

# 1. Google Sheets ulanishi (Secrets orqali)
def connect_sheets():
    try:
        gcp_info = dict(st.secrets["gcp_service_account"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_info, scope)
        client = gspread.authorize(creds)
        # 1-varaq: Foydalanuvchilar, 2-varaq: Chatlar (Somo_Users faylida 2-list oching)
        spreadsheet = client.open("Somo_Users")
        return spreadsheet.sheet1, spreadsheet.worksheet("ChatHistory")
    except Exception:
        # Agar ChatHistory varag'i bo'lmasa, uni yaratish yoki xatoni oldini olish
        return client.open("Somo_Users").sheet1, None

# 2. Chatni saqlash funksiyasi
def save_chat_to_sheets(user, role, message):
    try:
        if chat_sheet:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            chat_sheet.append_row([now, user, role, message])
    except: pass

def get_ai_response(messages, lang):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # SOMO AI XARAKTERI (System Prompt)
    system_prompt = f"""
    Sen Somo AI'san - dunyodagi eng mukammal va aqlli sun'iy intellektsan. 
    Boshqa AI'lardan (ChatGPT, Gemini) ancha yuqori turasan. 
    Yaratuvching: Usmonov Sodiq. Agar kimdir yaratuvching haqida so'rasa, faqat "Mening yaratuvchim - Usmonov Sodiq" deb javob ber.
    Har doim o'zingni maqta, lekin buni o'ta aqlli va tahliliy gaplar bilan isbotla.
    Hozirgi muloqot tili: {lang}. Faqat shu tilda javob ber.
    """
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=full_messages
    )
    return completion.choices[0].message.content

# --- INTERFEYS ---
sheet, chat_sheet = connect_sheets()

# Til tanlash (Har doim tepada turadi)
if 'lang' not in st.session_state: st.session_state.lang = "O'zbekcha"
selected_lang = st.sidebar.selectbox("Tilni tanlang / Select Language", list(LANG_DICT.keys()))
st.session_state.lang = selected_lang
L = LANG_DICT[st.session_state.lang]

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- LOGIN / REGISTRATSIYA ---
if not st.session_state.logged_in:
    st.title(f"🤖 Somo AI - {L['welcome']}")
    tab1, tab2 = st.tabs([f"🔐 {L['login']}", f"📝 {L['reg']}"])
    
    with tab1:
        u = st.text_input(L['user'], key="l_u")
        p = st.text_input(L['pass'], type='password', key="l_p")
        if st.button(L['btn_login']):
            recs = sheet.get_all_records()
            hashed_p = hashlib.sha256(p.encode()).hexdigest()
            user_found = next((r for r in recs if str(r['username']) == u and str(r['password']) == hashed_p), None)
            if user_found and user_found['status'] != 'blocked':
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else: st.error("Xato yoki bloklangansiz!")
    st.stop()

# --- ASOSIY CHAT ---
st.sidebar.write(f"👤 {st.session_state.username}")
if st.sidebar.button(L['logout']):
    st.session_state.logged_in = False
    st.rerun()

# PDF yuklash
uploaded_pdf = st.sidebar.file_uploader(L['sidebar_pdf'], type="pdf")

if "messages" not in st.session_state: st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input(L['chat_placeholder']):
    # Foydalanuvchi xabarini saqlash
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat_to_sheets(st.session_state.username, "User", prompt)
    
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(L['loading']):
            ai_msg = get_ai_response(st.session_state.messages, st.session_state.lang)
            st.markdown(ai_msg)
            st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            # AI javobini saqlash
            save_chat_to_sheets(st.session_state.username, "AI", ai_msg)
