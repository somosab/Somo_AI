import streamlit as st
import google.generativeai as genai
import time

st.set_page_config(
    page_title="Somo AI | Aqlli Yordamchi",
    page_icon="✨",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp { background: #f8f9ff !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e8eaf6 !important;
    box-shadow: 2px 0 12px rgba(99,102,241,0.06);
}
[data-testid="stSidebar"] * { color: #1e1e2e !important; }
[data-testid="stSidebarNav"] { display: none !important; }

div[data-testid="stSidebar"] button {
    background: #f1f0ff !important;
    color: #4f46e5 !important;
    border: 1px solid #e0e0ff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
div[data-testid="stSidebar"] button:hover {
    background: #4f46e5 !important;
    color: white !important;
    border-color: transparent !important;
}

#MainMenu, footer, header { display: none !important; }

/* Chat xabarlari */
.stChatMessage {
    background: #ffffff !important;
    border: 1px solid #eef0ff !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.07) !important;
    padding: 14px 18px !important;
    margin: 8px 0 !important;
}

/* Foydalanuvchi xabari */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #eef2ff, #f5f0ff) !important;
    border-color: #ddd6fe !important;
}

/* ── ChatGPT uslubidagi input ── */
.stChatInputContainer {
    background: transparent !important;
    border: none !important;
    padding: 12px 0 20px !important;
}

[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1.5px solid #e0e0ff !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.10) !important;
    padding: 4px 8px !important;
    transition: all 0.2s !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.18) !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    color: #1e1e2e !important;
    font-size: 15px !important;
    padding: 12px 14px !important;
    resize: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #a0a0b0 !important;
}

/* Yuborish tugmasi */
[data-testid="stChatInput"] button {
    background: #6366f1 !important;
    border-radius: 10px !important;
    border: none !important;
    margin: 4px !important;
    width: 36px !important;
    height: 36px !important;
    transition: all 0.2s !important;
}
[data-testid="stChatInput"] button:hover {
    background: #4f46e5 !important;
    transform: scale(1.05) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: #f8f8ff !important;
    border: 1.5px solid #e0e0ff !important;
    border-radius: 10px !important;
    color: #1e1e2e !important;
}

label { color: #6b7280 !important; font-size: 13px !important; font-weight: 500 !important; }
p, span, li { color: #1e1e2e !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #c7d2fe; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #6366f1; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px 0 10px;">
        <div style="font-size:52px; margin-bottom:8px;">✨</div>
        <h2 style="font-size:22px; font-weight:700; color:#4f46e5 !important;
                   margin:0; letter-spacing:-0.5px;">Somo AI</h2>
        <p style="font-size:12px; color:#9ca3af !important; margin:4px 0 0;">
            Gemini · Aqlli yordamchi
        </p>
    </div>
    <hr style="border:none; border-top:1px solid #eef0ff; margin:12px 0;">
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:13px;font-weight:600;color:#6b7280 !important;margin-bottom:6px;'>⚙️ Sozlamalar</p>",
                unsafe_allow_html=True)

    # To'g'ri model nomlari
    model_name = st.selectbox("Model:", [
        "gemini-2.0-flash-001",
        "gemini-1.5-flash-001",
        "gemini-1.5-pro-001",
        "gemini-1.5-flash-8b",
    ], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🗑️ Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    msg_count = len(st.session_state.get("messages", []))
    st.markdown(f"""
    <div style="margin-top:20px; background:#f8f8ff; border:1px solid #eef0ff;
                border-radius:12px; padding:14px 16px;">
        <p style="font-size:11px; color:#9ca3af !important; margin:0 0 8px;
                  font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Sessiya</p>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:13px; color:#6b7280 !important;">💬 Xabarlar</span>
            <span style="font-size:15px; font-weight:700; color:#4f46e5 !important;">{msg_count}</span>
        </div>
    </div>
    <div style="margin-top:auto; padding-top:40px; text-align:center;">
        <p style="font-size:11px; color:#d1d5db !important;">© 2026 Somo AI</p>
    </div>
    """, unsafe_allow_html=True)

# ── Asosiy kontent ───────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:32px 0 16px;">
    <h1 style="font-size:30px; font-weight:700; color:#1e1e2e;
               letter-spacing:-0.8px; margin:0;">
        ✨ Somo <span style="color:#6366f1;">AI</span>
    </h1>
    <p style="font-size:14px; color:#9ca3af; margin:8px 0 0;">
        Savolingizni yozing — javob shu zahoti keladi
    </p>
</div>
""", unsafe_allow_html=True)

# ── API ──────────────────────────────────────────────
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("❌ GEMINI_API_KEY topilmadi.")
    st.code('GEMINI_API_KEY = "AIzaSy-xxxx"', language="toml")
    st.stop()

# ── Chat tarixi ──────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Bo'sh chat — yo'riqnoma kartalar
if not st.session_state.messages:
    st.markdown("""
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;
                max-width:500px; margin:10px auto 28px;">
        <div style="background:#fff; border:1px solid #eef0ff; border-radius:14px;
                    padding:16px; box-shadow:0 2px 8px rgba(99,102,241,0.06);">
            <span style="font-size:22px;">💡</span>
            <p style="font-size:13px; font-weight:600; color:#1e1e2e; margin:8px 0 2px;">Savol bering</p>
            <p style="font-size:12px; color:#9ca3af; margin:0;">Istalgan mavzu haqida</p>
        </div>
        <div style="background:#fff; border:1px solid #eef0ff; border-radius:14px;
                    padding:16px; box-shadow:0 2px 8px rgba(99,102,241,0.06);">
            <span style="font-size:22px;">✍️</span>
            <p style="font-size:13px; font-weight:600; color:#1e1e2e; margin:8px 0 2px;">Matn yozdiring</p>
            <p style="font-size:12px; color:#9ca3af; margin:0;">Maqola, xat, rezyume</p>
        </div>
        <div style="background:#fff; border:1px solid #eef0ff; border-radius:14px;
                    padding:16px; box-shadow:0 2px 8px rgba(99,102,241,0.06);">
            <span style="font-size:22px;">🔍</span>
            <p style="font-size:13px; font-weight:600; color:#1e1e2e; margin:8px 0 2px;">Tushuntirish</p>
            <p style="font-size:12px; color:#9ca3af; margin:0;">Murakkab mavzular</p>
        </div>
        <div style="background:#fff; border:1px solid #eef0ff; border-radius:14px;
                    padding:16px; box-shadow:0 2px 8px rgba(99,102,241,0.06);">
            <span style="font-size:22px;">💻</span>
            <p style="font-size:13px; font-weight:600; color:#1e1e2e; margin:8px 0 2px;">Kod yozdiring</p>
            <p style="font-size:12px; color:#9ca3af; margin:0;">Python, JS va boshqa</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Xabarlarni ko'rsatish
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat input ───────────────────────────────────────
if prompt := st.chat_input("Somo AI ga xabar yuboring..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            # Gemini chat tarixi
            history = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})

            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction="Sen Somo AI — o'zbek va rus tillarida gaplasha oladigan aqlli yordamchisan. Aniq, foydali va do'stona javob ber."
            )
            chat = model.start_chat(history=history)

            # ── STREAMING animatsiya ──
            response = chat.send_message(prompt, stream=True)

            for chunk in response:
                if chunk.text:
                    for char in chunk.text:
                        full_response += char
                        placeholder.markdown(full_response + "▌")
                        time.sleep(0.008)   # har bir harf uchun kechikish

            # Oxirgi render — kursor yo'q
            placeholder.markdown(full_response)

        except Exception as e:
            err = str(e)
            if "api_key" in err.lower() or "auth" in err.lower():
                full_response = "❌ API kalit noto'g'ri. GEMINI_API_KEY ni tekshiring."
            elif "not found" in err.lower() or "404" in err:
                full_response = f"❌ Model mavjud emas: `{model_name}`. Boshqasini tanlang."
            elif "quota" in err.lower() or "429" in err:
                full_response = "❌ API limitga yetdi. Keyinroq urinib ko'ring."
            else:
                full_response = f"❌ Xatolik: {err}"
            placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
