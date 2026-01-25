import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from pypdf import PdfReader
import hashlib
import time

# --- SAHIFANI SOZLASH ---
st.set_page_config(
    page_title="Somo AI | Universal Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS DIZAYN (Interfeysni yanada chiroyli qilish uchun) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #1a73e8; color: white; border: none; }
    .stTextInput>div>div>input { border-radius: 10px; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 1. Google Sheets ulanishi (Secrets orqali)
def connect_sheets():
    try:
        gcp_info = dict(st.secrets["gcp_service_account"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_info, scope)
        client = gspread.authorize(creds)
        return client.open("Somo_Users").sheet1
    except Exception as e:
        st.error(f"Ma'lumotlar bazasiga ulanishda xato: {e}")
        return None

# 2. Xavfsizlik va PDF funksiyalari
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
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return completion.choices[0].message.content

# --- LOGIN VA REGISTRATSIYA TIZIMI ---
sheet = connect_sheets()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("🤖 Somo AI - Intellektual Tizim")
    tab1, tab2 = st.tabs(["🔐 Kirish", "📝 Ro'yxatdan o'tish"])

    with tab1:
        user = st.text_input("Username", key="l_user")
        pwd = st.text_input("Parol", type='password', key="l_pwd")
        if st.button("Tizimga kirish"):
            with st.spinner("Tekshirilmoqda..."):
                records = sheet.get_all_records()
                hashed_input = hash_password(pwd)
                user_found = next((r for r in records if str(r['username']) == user and str(r['password']) == hashed_input), None)
                
                if user_found:
                    if user_found['status'] == 'blocked':
                        st.error("Siz bloklangansiz! Admin bilan bog'laning. 🚫")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.username = user
                        st.success(f"Xush kelibsiz, {user}!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("Username yoki parol xato!")

    with tab2:
        new_user = st.text_input("Yangi Username yarating")
        new_pass = st.text_input("Yangi Parol yarating", type='password', key="r_pwd")
        if st.button("Ro'yxatdan o'tish"):
            if new_user and new_pass:
                all_users = sheet.col_values(1)
                if new_user in all_users:
                    st.warning("Bu username band. Boshqasini tanlang.")
                else:
                    sheet.append_row([new_user, hash_password(new_pass), 'active'])
                    st.success("Muvaffaqiyatli ro'yxatdan o'tdingiz! Endi 'Kirish' bo'limiga o'ting.")
            else:
                st.error("Hamma maydonlarni to'ldiring!")
    st.stop()

# --- ASOSIY INTERFEYS (KIRGANDAN SO'NG) ---
# Sidebar dizayni
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title(f"Salom, {st.session_state.username}!")
    st.divider()
    
    st.header("📄 PDF Tahlilchi")
    uploaded_pdf = st.file_uploader("PDF faylni shu yerga yuklang", type="pdf")
    if uploaded_pdf:
        st.success("PDF yuklandi!")
        if st.button("Chatni tozalash"):
            st.session_state.messages = []
            st.rerun()
            
    st.divider()
    if st.button("🚪 Chiqish"):
        st.session_state.logged_in = False
        st.rerun()

# Asosiy chat maydoni
st.markdown(f"### 🤖 Somo AI Chat | {st.session_state.username}")

# Chat tarixini ko'rsatish
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Foydalanuvchi xabari
if prompt := st.chat_input("Savolingizni yozing yoki PDF bo'yicha so'rang..."):
    # Foydalanuvchi xabarini qo'shish
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI javobini shakllantirish
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_context = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        
        # Agar PDF yuklangan bo'lsa, uning matnini AI-ga qo'shib yuboramiz
        if uploaded_pdf:
            pdf_text = read_pdf(uploaded_pdf)
            # Kontekstni faqat oxirgi savolga qo'shamiz (xotirani to'ldirmaslik uchun)
            full_context[-1]["content"] = f"Hujjat matni: {pdf_text[:6000]}\n\nFoydalanuvchi savoli: {prompt}"

        try:
            with st.spinner("Somo AI o'ylamoqda..."):
                response = get_ai_response(full_context)
                message_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"AI javob berishda xato qildi: {e}")
