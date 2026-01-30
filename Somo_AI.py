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

# --- 🌌 DEEP BLACK PREMIUM DESIGN ---
st.set_page_config(page_title="Somo AI | Elite Infinity", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #000000 0%, #020617 100%); color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #1e293b; }
    .stChatMessage { 
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.05); 
        background: rgba(15, 23, 42, 0.85) !important; backdrop-filter: blur(10px);
    }
    .stButton>button { 
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%); 
        color: #38bdf8; border: 1px solid #38bdf8; border-radius: 12px; font-weight: 700;
    }
    .stButton>button:hover { background: #38bdf8; color: #000000; box-shadow: 0 0 20px #38bdf8; }
    .katex { color: #38bdf8 !important; font-size: 1.2em !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 CONNECTION ---
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

def extract_content(file):
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'pdf': return "".join([p.extract_text() for p in PdfReader(file).pages])
        elif ext == 'docx': return mammoth.extract_raw_text(file).value
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)
            return df.head(30).to_string()
        elif ext == 'pptx':
            prs = pptx.Presentation(file)
            return "\n".join([s.text for sl in prs.slides for s in sl.shapes if hasattr(s, "text")])
    except: return "Faylni o'qishda xatolik."
    return ""

# --- 🔐 LOGIN SYSTEM (WITH ERROR ALERTS) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:#38bdf8;">🌌 Somo AI Infinity</h1>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Parol", type='password')
        if st.button("Kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u), None)
            
            if user:
                if str(user['password']) == hp:
                    if user['status'] == 'active':
                        # LOGIN MUVAFFIQIYATLI: Ismni saqlaymiz
                        st.session_state.logged_in = True
                        st.session_state.username = u 
                        st.session_state.messages = []
                        st.rerun()
                    else: st.error("❌ Hisobingiz bloklangan!")
                else: st.error("⚠️ Parol noto'g'ri!")
            else: st.error("🔍 Username topilmadi!")
    
    with t2:
        nu, np = st.text_input("Yangi Login"), st.text_input("Yangi Parol", type='password')
        if st.button("Hisob ochish"):
            if nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("🎉 Hisob yaratildi! Endi 'Kirish'ga o'ting.")
    st.stop()

# --- 💬 CHAT & PERSONALITY ENGINE ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
up_file = st.sidebar.file_uploader("📂 Fayl (Word, PDF, Excel, PPTX)", type=["pdf", "docx", "xlsx", "csv", "pptx"])

# --- ✨ KREATIV BOSH SAHIFA (WELCOME SCREEN) ---
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div style="text-align: center; padding: 50px 0;">
            <h1 style="font-size: 3.5rem; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Assalomu alaykum, {st.session_state.username}! ✨
            </h1>
            <p style="font-size: 1.5rem; color: #94a3b8;">Men Somo AI - sizning universal intellektual yordamchingizman.</p>
            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 30px;">
                <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid #38bdf8; padding: 20px; border-radius: 15px; width: 200px;">
                    <h4>📚 Ta'lim</h4>
                    <p style="font-size: 0.9rem;">Matematik misollarni LaTeX formatida yechaman.</p>
                </div>
                <div style="background: rgba(129, 140, 248, 0.1); border: 1px solid #818cf8; padding: 20px; border-radius: 15px; width: 200px;">
                    <h4>📂 Fayllar</h4>
                    <p style="font-size: 0.9rem;">PDF, Word, Excel va PPTX fayllarni tahlil qilaman.</p>
                </div>
                <div style="background: rgba(244, 63, 94, 0.1); border: 1px solid #f43f5e; padding: 20px; border-radius: 15px; width: 200px;">
                    <h4>👨‍💻 Creator</h4>
                    <p style="font-size: 0.9rem;">Yaratuvchim: Usmonov Sodiq.</p>
                </div>
            </div>
            <p style="margin-top: 40px; color: #64748b; font-style: italic;">Boshlash uchun pastga savol yozing yoki fayl yuklang...</p>
        </div>
    """, unsafe_allow_html=True)

# Chat xabarlarini ko'rsatish (agar xabarlar bo'lsa)
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])


        
        # 🧠 BU YERDA AI O'ZINI VA SIZNI TANIYDI
        sys_msg = f"""Sening isming Somo AI. 
        Sening yaratuvching (creator) - Usmonov Sodiq. 
        Hozir muloqot qilayotgan foydalanuvchining ismi: {user_name}. 
        Agar foydalanuvchi 'men kimman?' deb so'rasa, unga '{user_name} sizsiz' deb javob ber.
        Matematik misollarni FAQAT LaTeX ($...$) formatida yech. 
        Masalan: $a^2 + b^2 = c^2$.
        Sening maqsading foydalanuvchiga barcha fayllarni tahlil qilishda yordam berish."""

        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        
        if up_file:
            f_text = extract_content(up_file)
            ctx.insert(1, {"role": "system", "content": f"Foydalanuvchi yuklagan hujjat: {f_text}"})

        # Groq tahlili
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=ctx,
            temperature=0.7
        ).choices[0].message.content
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Baza uchun log (Admin Panel)
        try:
            chat_sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), st.session_state.username, "AI", prompt[:500]])
        except: pass

