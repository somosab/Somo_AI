import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from pypdf import PdfReader
import hashlib
from datetime import datetime

# --- SAHIFANI SOZLASH VA DIZAYN ---
st.set_page_config(page_title="Somo AI | Premium", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #1f2937; }
    .stButton>button { width: 100%; border-radius: 10px; background: linear-gradient(45deg, #1e40af, #3b82f6); color: white; border: none; }
    .stChatFloatingInputContainer { background-color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEETS ULANISHI ---
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

# --- FUNKSIYALAR ---
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_ai_response(messages, lang, name):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    # AI endi foydalanuvchiga ismi bilan murojaat qiladi
    sys_prompt = f"Sen Somo AI'san. Yaratuvching: Usmonov Sodiq. Foydalanuvchi ismi: {name}. Doimo unga ismi bilan murojaat qil. Til: {lang}."
    full_msgs = [{"role": "system", "content": sys_prompt}] + messages
    return client.chat.completions.create(model="llama-3.3-70b-versatile", messages=full_msgs).choices[0].message.content

def generate_title(text):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user", "content":f"Short title: {text}"}])
        return res.choices[0].message.content[:30]
    except: return "Suhbat"

# --- LOGIN VA REGISTRATSIYA ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("🤖 Somo AI - Tizimga kirish")
    tab1, tab2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    
    with tab1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Parol", type='password', key="l_p")
        if st.button("Kirish"):
            recs = user_sheet.get_all_records()
            user_data = next((r for r in recs if r['username'] == u and r['password'] == hash_pass(p)), None)
            if user_data:
                if user_data['status'] == 'active':
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
                else: st.error("Siz bloklangansiz!")
            else: st.error("Login yoki parol xato!")

    with tab2:
        new_u = st.text_input("Yangi Username", key="r_u")
        new_p = st.text_input("Yangi Parol", type='password', key="r_p")
        if st.button("Ro'yxatdan o'tish"):
            if new_u and new_p:
                user_sheet.append_row([new_u, hash_pass(new_p), "active"])
                st.success("Muvaffaqiyatli ro'yxatdan o'tdingiz! Endi Kirish bo'limiga o'ting.")
    st.stop()

# --- CHAT INTERFEYSI ---
st.sidebar.title(f"👤 {st.session_state.username}")

# CHATNI O'CHIRISH (Clear Chat) tugmasi
if st.sidebar.button("🗑 Chatni tozalash"):
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("🚪 Chiqish"):
    st.session_state.logged_in = False
    st.rerun()

# Xabarlarni ko'rsatish
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Savolingizni yozing..."):
    if not st.session_state.messages:
        st.session_state.current_title = generate_title(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        response = get_ai_response(st.session_state.messages, "O'zbekcha", st.session_state.username)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Bazaga saqlash
        if chat_sheet:
            chat_sheet.append_row([st.session_state.get('current_title', 'Suhbat'), datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
