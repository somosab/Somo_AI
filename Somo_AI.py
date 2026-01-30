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

# --- 🛰 PRESTIGE BLACK DESIGN ---
st.set_page_config(page_title="Somo AI | Universal Infinity", page_icon="💎", layout="wide")
st.markdown("""
    <style>
    .stApp { 
        background: radial-gradient(circle at center, #000000 0%, #020617 100%); 
        color: #ffffff; 
    }
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        border-right: 1px solid #1e293b; 
    }
    .stChatMessage { 
        border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.05) !important; 
        background: rgba(15, 23, 42, 0.8) !important; 
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%); 
        color: #38bdf8; border: 1px solid #38bdf8;
        border-radius: 12px; font-weight: 700; transition: 0.4s;
        height: 45px; width: 100%;
    }
    .stButton>button:hover { 
        background: #38bdf8; color: #000000;
        box-shadow: 0 0 20px #38bdf8; 
    }
    .katex { color: #38bdf8 !important; font-size: 1.2em !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔗 CORE CONNECTIONS ---
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

def extract_universal_content(file):
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'pdf': return "".join([p.extract_text() for p in PdfReader(file).pages])
        elif ext == 'docx': return mammoth.extract_raw_text(file).value
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)
            return f"Jadval ma'lumotlari: {df.head(30).to_string()}"
        elif ext == 'pptx':
            prs = pptx.Presentation(file)
            return "\n".join([s.text for sl in prs.slides for s in sl.shapes if hasattr(s, "text")])
    except: return "Faylni o'qishda xatolik yuz berdi."
    return ""

# --- 🔐 AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:#38bdf8; margin-top:50px;">🌌 Somo AI Infinity</h1>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Kirish", "📝 Ro'yxatdan o'tish"])
    
    with t1:
        u = st.text_input("Username", placeholder="Ismingiz...")
        p = st.text_input("Parol", type='password', placeholder="Parolingiz...")
        if st.button("Tizimga kirish"):
            recs = user_sheet.get_all_records()
            hp = hashlib.sha256(p.encode()).hexdigest()
            user = next((r for r in recs if str(r['username']) == u), None)
            
            if user:
                if str(user['password']) == hp:
                    if user['status'] == 'active':
                        st.session_state.logged_in, st.session_state.username, st.session_state.messages = True, u, []
                        st.rerun()
                    else: st.error("❌ Hisobingiz bloklangan!")
                else: st.error("⚠️ Parol noto'g'ri! Iltimos, qaytadan urinib ko'ring.")
            else: st.error("🔍 Bunday foydalanuvchi topilmadi!")

    with t2:
        nu, np = st.text_input("Yangi Username"), st.text_input("Yangi Parol", type='password')
        if st.button("Hisobni yaratish"):
            if nu and np:
                user_sheet.append_row([nu, hashlib.sha256(np.encode()).hexdigest(), "active"])
                st.success("🎉 Muvaffaqiyatli! Kirish bo'limiga o'ting.")
    st.stop()

# --- 💬 CHAT & PERSONALITY ENGINE ---
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
up_file = st.sidebar.file_uploader("📂 Fayl tahlili (PDF, Word, Excel, PPTX)", type=["pdf", "docx", "xlsx", "csv", "pptx"])

# --- ✨ KREATIV BOSH SAHIFA ---
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div style="text-align: center; padding: 50px 0;">
            <h1 style="font-size: 3rem; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Assalomu alaykum, {st.session_state.username}! ✨
            </h1>
            <p style="font-size: 1.2rem; color: #94a3b8;">Men Somo AI - sizning universal yordamchingizman.</p>
            <div style="display: flex; justify-content: center; gap: 15px; margin-top: 30px;">
                <div style="background: rgba(56, 189, 248, 0.05); border: 1px solid #38bdf8; padding: 15px; border-radius: 12px; width: 180px;">
                    <h4 style="color:#38bdf8;">📐 Matematika</h4>
                    <p style="font-size: 0.8rem;">Murakkab misollarni LaTeX formatida yechaman.</p>
                </div>
                <div style="background: rgba(129, 140, 248, 0.05); border: 1px solid #818cf8; padding: 15px; border-radius: 12px; width: 180px;">
                    <h4 style="color:#818cf8;">📂 Fayllar</h4>
                    <p style="font-size: 0.8rem;">Word, PDF, Excel va PPTX tahlil qilaman.</p>
                </div>
                <div style="background: rgba(244, 63, 94, 0.05); border: 1px solid #f43f5e; padding: 15px; border-radius: 12px; width: 180px;">
                    <h4 style="color:#f43f5e;">👨‍💻 Creator</h4>
                    <p style="font-size: 0.8rem;">Yaratuvchim: Usmonov Sodiq.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Xabarlarni ko'rsatish
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Somo AI ga savol bering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        user_current = st.session_state.username
        
        sys_msg = f"""Sening isming Somo AI. Yaratuvching: Usmonov Sodiq. 
        Hozirgi foydalanuvchi: {user_current}. 
        Agar senga foydalanuvchi 'men kimman?' deb murojaat qilsa, uning ismi {user_current} ekanini ayt.
        Matematik misollarni va formulalarni FAQAT LaTeX ($...$) formatida yoz. 
        Misol: $a^2 + \\frac{{b}}{{c}} = d$. 
        Yuklangan fayllarni diqqat bilan tahlil qil va foydalanuvchiga yordam ber."""

        ctx = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        if up_file:
            ctx.insert(1, {"role": "system", "content": f"Foydalanuvchi yuklagan fayl mazmuni: {extract_universal_content(up_file)}"})
        
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=ctx).choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        try:
            chat_sheet.append_row([datetime.now().strftime("%H:%M"), st.session_state.username, "AI", prompt[:500]])
        except: pass
