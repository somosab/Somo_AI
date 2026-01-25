import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from pypdf import PdfReader
import hashlib

# 1. Google Sheets ulanishi (Secrets orqali)
def connect_sheets():
    try:
        gcp_info = dict(st.secrets["gcp_service_account"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_info, scope)
        client = gspread.authorize(creds)
        return client.open("Somo_Users").sheet1
    except Exception as e:
        st.error(f"Ulanishda xato: {e}")
        return None

# 2. Yordamchi funksiyalar
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content: text += content
    return text

def get_ai_response(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

# --- INTERFEYS VA LOGIN MANTIQI ---
st.set_page_config(page_title="Somo AI", layout="centered")
sheet = connect_sheets()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Somo AI - Tizimga xush kelibsiz")
    
    # MANA SHU QISM RO'YXATDAN O'TISHNI QAYTARADI
    tab1, tab2 = st.tabs(["🔐 Kirish", "📝 Ro'yxatdan o'tish"])

    with tab2:
        new_user = st.text_input("Yangi foydalanuvchi nomi (Email/Username)")
        new_pass = st.text_input("Yangi parol", type='password', key="reg_pass")
        if st.button("Ro'yxatdan o'tish"):
            if new_user and new_pass:
                all_users = sheet.col_values(1)
                if new_user in all_users:
                    st.warning("Bu username band!")
                else:
                    # Google Sheets-ga: username, hashed_password, status
                    sheet.append_row([new_user, hash_password(new_pass), 'active'])
                    st.success("Tabriklaymiz! Ro'yxatdan o'tdingiz. Endi 'Kirish' bo'limiga o'ting.")
            else:
                st.error("Ma'lumotlarni to'ldiring!")

    with tab1:
        user = st.text_input("Username", key="login_user")
        pwd = st.text_input("Parol", type='password', key="login_pass")
        if st.button("Kirish"):
            records = sheet.get_all_records()
            hashed_input_pwd = hash_password(pwd)
            
            user_found = next((r for r in records if str(r['username']) == user and str(r['password']) == hashed_input_pwd), None)
            
            if user_found:
                if user_found['status'] == 'blocked':
                    st.error("Siz bloklangansiz! 🚫")
                else:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.rerun()
            else:
                st.error("Username yoki parol xato!")
    st.stop()

# --- CHAT QISMI ---
st.title(f"Xush kelibsiz, {st.session_state.username}! 👋")
# (Chat va PDF tahlil kodini davom ettirishingiz mumkin)
