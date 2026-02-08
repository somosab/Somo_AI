import streamlit as st
import pandas as pd
import gspread
import hashlib
import mammoth
import pptx
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# --- 🛰 1. SISTEMA SOZLAMALARI ---
st.set_page_config(page_title="Somo AI | Infinity", page_icon="🌌", layout="wide")

# Cookies - Sessiyani saqlash
cookies = EncryptedCookieManager(password=st.secrets.get("COOKIE_PASSWORD", "Somo_AI_Secret_Key_2026"))
if not cookies.ready():
    st.stop()

# --- 🎨 2. SIDEBAR VA LOGINNI "DAXSHAT" QILADIGAN CSS ---
st.markdown("""
    <style>
    /* Umumiy fon */
    .stApp { background-color: #ffffff !important; }

    /* CHAP BO'LIM (SIDEBAR) NI TO'LIQ QORA QILISH */
    [data-testid="stSidebar"] {
        background-color: #05070a !important;
        border-right: 2px solid #1e293b;
    }

    /* Sidebar ichidagi yozuvlar (Oq qilish) */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* TUGMALAR (Qizil ramkadagi xatoni tuzatish) */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #6d28d9 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px !important;
        width: 100% !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(109, 40, 217, 0.4) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="stSidebar"] button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(109, 40, 217, 0.6) !important;
    }

    /* FAYL YUKLASH MAYDONI (Oq dog'ni yo'qotish) */
    [data-testid="stFileUploader"] {
        background-color: #0f172a !important;
        border: 2px dashed #4f46e5 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    [data-testid="stFileUploader"] section { color: white !important; }

    /* ASOSIY SAHIFA KARTALARI */
    .card-box {
        background: white;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid #f1f5f9;
        transition: 0.3s;
    }
    .card-box:hover { transform: translateY(-10px); }
    
    .gradient-text {
        background: linear-gradient(90deg, #4f46e5, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 3. SERVISLARNI ULANISH ---
def get_connections():
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
        ss = gc.open("Somo_Users")
        return client, ss.sheet1, ss.worksheet("ChatHistory")
    except: return client, None, None

client, user_db, chat_db = get_connections()

# --- 📂 4. FAYL KONVERTER ---
def process_doc(file):
    try:
        if file.type == "application/pdf":
            return " ".join([p.extract_text() for p in PdfReader(file).pages])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return mammoth.convert_to_markdown(file).value
    except: return ""
    return ""

# --- 🔐 5. LOGIN BO'LIMI (100% ISHLAYDI) ---
if 'logged_in' not in st.session_state:
    saved = cookies.get("somo_user_session")
    if saved:
        st.session_state.username = saved
        st.session_state.logged_in = True
    else: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🌌 Somo AI <span class='gradient-text'>Infinity</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        choice = st.radio("Tanlang:", ["Kirish", "Ro'yxatdan o'tish"], horizontal=True)
        u = st.text_input("Username")
        p = st.text_input("Parol", type='password')
        
        if choice == "Kirish":
            if st.button("Kirish 🚀", use_container_width=True):
                data = user_db.get_all_records()
                hp = hashlib.sha256(p.encode()).hexdigest()
                user = next((r for r in data if str(r['username']) == u and str(r['password']) == hp), None)
                if user:
                    st.session_state.username = u
                    st.session_state.logged_in = True
                    cookies["somo_user_session"] = u
                    cookies.save()
                    st.rerun()
                else: st.error("Xato: Login yoki parol noto'g'ri!")
        else:
            if st.button("Yaratish ✨", use_container_width=True):
                if u and p:
                    hp = hashlib.sha256(p.encode()).hexdigest()
                    user_db.append_row([u, hp, "active", str(datetime.now())])
                    st.success("Muvaffaqiyatli! Kirish bo'limiga o'ting.")
    st.stop()

# --- 🚀 6. ASOSIY INTERFEYS ---
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 10px;'>
            <div style='background: #4f46e5; width: 60px; height: 60px; border-radius: 50%; margin: 0 auto; line-height: 60px; font-size: 25px; color: white;'>
                {st.session_state.username[0].upper()}
            </div>
            <h3 style='color: white;'>{st.session_state.username}</h3>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📂 **FAYL TAHLILI**")
    f = st.file_uploader("Yuklash", type=["pdf", "docx"], label_visibility="collapsed")
    txt = process_doc(f) if f else ""
    if f: st.success("Fayl tayyor!")

    st.markdown("<br>"*5, unsafe_allow_html=True)
    if st.button("🚪 Chiqish"):
        cookies["somo_user_session"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()

# Dashboard
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center;'>Xush kelibsiz, <span class='gradient-text'>{st.session_state.username}</span>!</h1>", unsafe_allow_html=True)
    cols = st.columns(3)
    with cols[0]: st.markdown('<div class="card-box"><h3>🧠</h3><h4>Tahlil</h4><p>Murakkab savollar yechimi</p></div>', unsafe_allow_html=True)
    with cols[1]: st.markdown('<div class="card-box"><h3>📄</h3><h4>Hujjat</h4><p>Fayllarni o\'qish</p></div>', unsafe_allow_html=True)
    with cols[2]: st.markdown('<div class="card-box"><h3>🎨</h3><h4>Ijod</h4><p>Yangi g\'oyalar</p></div>', unsafe_allow_html=True)

# Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Xabaringizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            full_p = f"{prompt}\n\n[Kontekst]: {txt[:2000]}" if txt else prompt
            res = client.chat.completions.create(messages=[{"role": "user", "content": full_p}], model="llama-3.3-70b-versatile").choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            if chat_db: chat_db.append_row([st.session_state.username, prompt, res[:500], str(datetime.now())])
        except: st.error("Xatolik yuz berdi.")
