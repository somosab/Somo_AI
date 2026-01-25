import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from pypdf import PdfReader
import hashlib

# 1. Google Sheets ulanishi (Secrets orqali)
def connect_sheets():
    try:
        # Secrets-dagi [gcp_service_account] bo'limini olish
        gcp_info = dict(st.secrets["gcp_service_account"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_info, scope)
        client = gspread.authorize(creds)
        return client.open("Somo_Users").sheet1
    except Exception as e:
        st.error(f"Baza bilan ulanishda xato: {e}")
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

def get_ai_response(messages):
    # Secrets-dagi Groq API kalitidan foydalanish
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return completion.choices[0].message.content

# --- INTERFEYS VA LOGIN MANTIQI ---
st.set_page_config(page_title="Somo AI", page_icon="🤖", layout="wide")
sheet = connect_sheets()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Somo AI - Tizimga kirish")
    tab1, tab2 = st.tabs(["🔐 Kirish", "📝 Ro'yxatdan o'tish"])

    with tab2:
        new_user = st.text_input("Username yarating")
        new_pass = st.text_input("Parol yarating", type='password', key="reg_p")
        if st.button("Ro'yxatdan o'tish"):
            if new_user and new_pass:
                all_users = sheet.col_values(1)
                if new_user in all_users:
                    st.warning("Bu username band!")
                else:
                    sheet.append_row([new_user, hash_password(new_pass), 'active'])
                    st.success("Muvaffaqiyatli ro'yxatdan o'tdingiz! Kirish bo'limiga o'ting.")
    
    with tab1:
        user = st.text_input("Username", key="log_u")
        pwd = st.text_input("Parol", type='password', key="log_p")
        if st.button("Kirish"):
            records = sheet.get_all_records()
            hashed_input = hash_password(pwd)
            user_found = next((r for r in records if str(r['username']) == user and str(r['password']) == hashed_input), None)
            
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

# --- AGAR KIRGAN BO'LSA, QUYIDAGI QISM ISHLAYDI ---
st.title(f"Xush kelibsiz, {st.session_state.username}! 👋")

# Sidebar - Sozlamalar va Fayl yuklash
with st.sidebar:
    st.header("Hujjatlar")
    uploaded_pdf = st.file_uploader("PDF tahlil qilish uchun", type="pdf")
    if st.button("Chiqish"):
        st.session_state.logged_in = False
        st.rerun()

# Chat tarixi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Xabarlarni ko'rsatish
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Savol kiritish
if prompt := st.chat_input("Savolingizni yozing..."):
    # Xabarni foydalanuvchi nomidan qo'shish
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # PDF mazmunini qo'shish (agar yuklangan bo'lsa)
    context_msg = prompt
    if uploaded_pdf:
        with st.spinner("PDF o'qilmoqda..."):
            pdf_text = read_pdf(uploaded_pdf)
            context_msg = f"Quyidagi PDF mazmuni bo'yicha javob ber: {pdf_text[:5000]}\n\nSavol: {prompt}"

    # AI javobini olish
    with st.chat_message("assistant"):
        with st.spinner("Somo AI o'ylamoqda..."):
            # Chat tarixini AI-ga yuborish
            ai_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            ai_messages.append({"role": "user", "content": context_msg})
            
            response = get_ai_response(ai_messages)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
