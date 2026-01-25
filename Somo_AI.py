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
        # Google Sheets-dagi faylingiz nomi 'Somo_Users' ekanligini tekshiring
        return client.open("Somo_Users").sheet1
    except Exception as e:
        st.error(f"Google Sheets ulanishida xato: {e}")
        return None

# 2. PDF faylni o'qish funksiyasi
def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content:
            text += content
    return text

# 3. Groq AI javobini olish
def get_ai_response(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

# --- ASOSIY LOGIN VA CHAT LOGIKASI ---
st.set_page_config(page_title="Somo AI | Universal Analyst", layout="wide")
sheet = connect_sheets()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Somo AI - Tizimga kirish")
    user = st.text_input("Username")
    pwd = st.text_input("Parol", type='password')
    
    if st.button("Kirish") and sheet:
        records = sheet.get_all_records()
        hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest()
        
        user_found = next((r for r in records if r['username'] == user and str(r['password']) == hashed_pwd), None)
        
        if user_found:
            if user_found['status'] == 'blocked':
                st.error("Siz Sodiq tomonidan bloklangansiz! 🚫")
            else:
                st.session_state.logged_in = True
                st.session_state.username = user
                st.rerun()
        else:
            st.error("Username yoki parol xato!")
    st.stop()

# --- CHAT VA PDF TAHLIL QISMI ---
st.title(f"Xush kelibsiz, {st.session_state.username}! 🤖")

with st.sidebar:
    st.header("Hujjat yuklash")
    uploaded_pdf = st.file_uploader("PDF tahlil qilish", type="pdf")
    if st.button("Chiqish"):
        st.session_state.logged_in = False
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Avvalgi xabarlarni ko'rsatish
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Yangi xabar kiritish
if prompt := st.chat_input("Savolingizni yozing..."):
    pdf_context = ""
    if uploaded_pdf:
        pdf_context = f"\n\n[Yuklangan PDF mazmuni]: {read_pdf(uploaded_pdf)[:3000]}"
    
    full_prompt = prompt + pdf_context
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = get_ai_response(full_prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
