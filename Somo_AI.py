import streamlit as st
from cerebras.cloud.sdk import Cerebras
import time
import json
from datetime import datetime

st.set_page_config(
    page_title="Somo AI | Aqlli Yordamchi",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #f8f9ff !important; }

/* ── Sidebar toggle tugmasi DOIM ko'rinsin ── */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: #ffffff !important;
    border: 1px solid #e0e0ff !important;
    border-radius: 0 10px 10px 0 !important;
    box-shadow: 2px 0 8px rgba(99,102,241,0.15) !important;
    z-index: 999 !important;
}
[data-testid="collapsedControl"] svg { color: #6366f1 !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e8eaf6 !important;
    box-shadow: 2px 0 12px rgba(99,102,241,0.06) !important;
    min-width: 260px !important;
}
[data-testid="stSidebar"] * { color: #1e1e2e !important; }
[data-testid="stSidebarNav"] { display: none !important; }

div[data-testid="stSidebar"] button {
    background: #f1f0ff !important; color: #4f46e5 !important;
    border: 1px solid #e0e0ff !important; border-radius: 10px !important;
    font-weight: 600 !important; transition: all 0.2s !important;
}
div[data-testid="stSidebar"] button:hover {
    background: #4f46e5 !important; color: white !important;
    border-color: transparent !important;
}

#MainMenu, footer, header { display: none !important; }

/* Asosiy kontent kengligi */
.main .block-container {
    max-width: 780px !important;
    margin: 0 auto !important;
    padding: 0 20px !important;
}

/* Chat */
.stChatMessage {
    background: #ffffff !important;
    border: 1px solid #eef0ff !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.07) !important;
    padding: 14px 18px !important;
    margin: 8px 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #eef2ff, #f5f0ff) !important;
    border-color: #ddd6fe !important;
}

/* Input */
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
    transition: all 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.18) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important; border: none !important;
    color: #1e1e2e !important; font-size: 15px !important; padding: 12px 14px !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #a0a0b0 !important; }
[data-testid="stChatInput"] button {
    background: #6366f1 !important; border-radius: 10px !important;
    border: none !important; margin: 4px !important; transition: all 0.2s !important;
}
[data-testid="stChatInput"] button:hover {
    background: #4f46e5 !important; transform: scale(1.05) !important;
}

.stSelectbox > div > div {
    background: #f8f8ff !important; border: 1.5px solid #e0e0ff !important;
    border-radius: 10px !important;
}

label { color: #6b7280 !important; font-size: 13px !important; font-weight: 500 !important; }
p, span, li { color: #1e1e2e !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #c7d2fe; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #6366f1; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════
CREATOR_PASSWORD = st.secrets.get("CREATOR_PASSWORD", "somo2026")

SYSTEM_PROMPT = """Sen Somo AI — o'zbek va rus tillarida gaplasha oladigan aqlli, madaniyatli va foydali yordamchisan.

QOIDALAR:
- Har doim hurmatli va madaniyatli bo'l
- Haqorat, so'kinish yoki nojo'ya so'zlar HECH QACHON ishlatma
- Agar foydalanuvchi haqorat qilsa, muloyimlik bilan murojaat qil
- Aniq, qisqa va foydali javob ber
- O'zbek yoki rus tilida so'rasalar — o'sha tilda javob ber"""

CURRENT_FEATURES = """
Somo AI hozirgi funksiyalari:
- Cerebras AI (llama-3.3-70b / llama3.1-8b) bilan chat
- Animatsiyali streaming javoblar
- Model tanlash
- Chat tarixi tozalash
- Yaratuvchi paneli (parol himoyali)
- Madaniyatli javob tizimi

Texnologiya: Python + Streamlit + Cerebras API
Auditoriya: O'zbek va rus tilida so'zlashuvchilar
"""

# ══════════════════════════════════════════════
# CLIENT
# ══════════════════════════════════════════════
@st.cache_resource
def get_client():
    return Cerebras(api_key=st.secrets["CEREBRAS_API_KEY"])

try:
    client = get_client()
except Exception:
    st.error("❌ CEREBRAS_API_KEY topilmadi.")
    st.code('CEREBRAS_API_KEY = "csk-xxxx"\nCREATOR_PASSWORD = "parolingiz"', language="toml")
    st.stop()

def ask_ai(prompt, system=SYSTEM_PROMPT, max_tokens=2000):
    for model in ["llama-3.3-70b", "llama3.1-8b"]:
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                stream=False, max_tokens=max_tokens,
            )
            return r.choices[0].message.content
        except Exception as e:
            if "404" in str(e) or "not_found" in str(e):
                continue
            return f"Xatolik: {e}"
    return "Model javob bermadi."

# ══════════════════════════════════════════════
# SUGGESTIONS
# ══════════════════════════════════════════════
def generate_suggestions(chat_history):
    user_msgs = [m["content"] for m in chat_history if m["role"] == "user"]
    ctx = ""
    if user_msgs:
        ctx = f"\nFoydalanuvchilar so'ragan mavzular:\n" + "\n".join([f"- {m[:80]}" for m in user_msgs[-8:]])

    system = "Sen AI mahsulot strategist va dasturchi. Faqat JSON qaytarasan. Hech qanday izoh yozma."

    prompt = f"""Somo AI chatbot uchun 6 ta ORIGINAL va JUDA QIZIQARLI yangi funksiya taklif qil.

{CURRENT_FEATURES}{ctx}

Talablar:
- Faqat AI chatbot uchun mantiqli funksiyalar
- Texnik jihatdan haqiqatan MUMKIN bo'lsin
- O'zbek foydalanuvchilar uchun REAL FOYDA
- Qiziqarli va zamonaviy g'oyalar

JSON:
[{{
  "name": "qisqa nom",
  "emoji": "emoji",
  "category": "UX/AI/Mahsuldorlik/O'zbek/Integratsiya",
  "description": "nima qiladi - 1 jumla",
  "why_cool": "nima uchun juda foydali va qiziqarli",
  "how_to_build": "qaysi API/kutubxona ishlatish",
  "difficulty": "oson/o'rta/qiyin",
  "priority": "yuqori/o'rta/past",
  "wow_factor": 1-10
}}]"""

    raw = ask_ai(prompt, system, 2500)
    import re
    m = re.search(r'\[.*\]', raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except:
            pass
    return [
        {"name": "Ovozli chat", "emoji": "🎙️", "category": "AI",
         "description": "Mikrofondan gapiring, AI javob bersin",
         "why_cool": "Qo'l bilan yozmasdan, tezroq va qulay",
         "how_to_build": "Whisper API + Cerebras", "difficulty": "o'rta",
         "priority": "yuqori", "wow_factor": 9},
        {"name": "O'zbek grammatika", "emoji": "📝", "category": "O'zbek",
         "description": "Yozgan matnidagi xatolarni topib tuzatadi",
         "why_cool": "O'zbek tilida bunday vosita deyarli yo'q",
         "how_to_build": "Cerebras + maxsus prompt", "difficulty": "oson",
         "priority": "yuqori", "wow_factor": 8},
    ]

# ══════════════════════════════════════════════
# SESSION
# ══════════════════════════════════════════════
for k, v in [("messages", []), ("is_creator", False),
              ("suggestions", []), ("last_scan", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px;">
        <div style="font-size:46px;margin-bottom:6px;">✨</div>
        <h2 style="font-size:21px;font-weight:700;color:#4f46e5 !important;margin:0;">Somo AI</h2>
        <p style="font-size:12px;color:#9ca3af !important;margin:4px 0 0;">Cerebras · Aqlli yordamchi</p>
    </div>
    <hr style="border:none;border-top:1px solid #eef0ff;margin:10px 0;">
    """, unsafe_allow_html=True)

    model_name = st.selectbox("⚡ Model:", ["llama-3.3-70b", "llama3.1-8b"])

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🗑️ Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid #eef0ff;margin:14px 0;'>",
                unsafe_allow_html=True)

    if not st.session_state.is_creator:
        st.markdown("<p style='font-size:12px;color:#9ca3af !important;text-align:center;margin-bottom:8px;'>🔐 Yaratuvchi paneli</p>",
                    unsafe_allow_html=True)
        pw = st.text_input("Parol:", type="password", placeholder="••••••••",
                            label_visibility="collapsed")
        if st.button("Kirish", use_container_width=True):
            if pw == CREATOR_PASSWORD:
                st.session_state.is_creator = True
                st.rerun()
            else:
                st.error("❌ Noto'g'ri parol")
    else:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#f0f4ff,#faf0ff);
                    border:1px solid #c7d2fe;border-radius:12px;
                    padding:10px;text-align:center;margin-bottom:10px;">
            <span style="font-size:18px;">👑</span>
            <p style="font-size:13px;font-weight:700;color:#4f46e5 !important;margin:4px 0 0;">
                Yaratuvchi rejimi</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🧠 Taklif yaratish", use_container_width=True, type="primary"):
            with st.spinner("AI o'zi haqida o'ylamoqda..."):
                st.session_state.suggestions = generate_suggestions(st.session_state.messages)
                st.session_state.last_scan = datetime.now()
            st.rerun()

        if st.session_state.last_scan:
            st.markdown(f"<p style='font-size:11px;color:#9ca3af !important;text-align:center;'>"
                        f"🕐 {st.session_state.last_scan.strftime('%H:%M')}</p>",
                        unsafe_allow_html=True)

        if st.button("🚪 Chiqish", use_container_width=True):
            st.session_state.is_creator = False
            st.session_state.suggestions = []
            st.rerun()

    msg_count = len(st.session_state.messages)
    st.markdown(f"""
    <div style="margin-top:14px;background:#f8f8ff;border:1px solid #eef0ff;
                border-radius:12px;padding:12px 14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:13px;color:#6b7280 !important;">💬 Xabarlar</span>
            <span style="font-size:15px;font-weight:700;color:#4f46e5 !important;">{msg_count}</span>
        </div>
    </div>
    <div style="padding-top:20px;text-align:center;">
        <p style="font-size:11px;color:#d1d5db !important;">© 2026 Somo AI</p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;padding:28px 0 14px;">
    <h1 style="font-size:30px;font-weight:700;color:#1e1e2e;letter-spacing:-0.8px;margin:0;">
        ✨ Somo <span style="color:#6366f1;">AI</span>
    </h1>
    <p style="font-size:14px;color:#9ca3af;margin:6px 0 0;">
        Savolingizni yozing — javob shu zahoti keladi
    </p>
</div>
""", unsafe_allow_html=True)

# ── Yaratuvchi takliflari ──
if st.session_state.is_creator and st.session_state.suggestions:
    diff_c = {"oson": "#10b981", "o'rta": "#f59e0b", "qiyin": "#ef4444"}
    diff_i = {"oson": "🟢", "o'rta": "🟡", "qiyin": "🔴"}
    pri_c  = {"yuqori": "#ef4444", "o'rta": "#f59e0b", "past": "#6b7280"}
    cat_bg = {"UX": "#eff6ff", "AI": "#f5f0ff", "Mahsuldorlik": "#f0fdf4",
              "O'zbek": "#fff7ed", "Integratsiya": "#fdf2f8"}
    cat_bc = {"UX": "#bfdbfe", "AI": "#ddd6fe", "Mahsuldorlik": "#bbf7d0",
              "O'zbek": "#fed7aa", "Integratsiya": "#fbcfe8"}

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#667eea18,#764ba218);
                border:1.5px solid #c7d2fe;border-radius:20px;
                padding:16px 20px;margin-bottom:20px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:22px;">🧠</span>
            <div>
                <p style="font-size:15px;font-weight:700;color:#4f46e5 !important;margin:0;">
                    AI Taklif Tizimi — {len(st.session_state.suggestions)} ta g'oya</p>
                <p style="font-size:12px;color:#9ca3af !important;margin:0;">
                    {st.session_state.last_scan.strftime('%d.%m.%Y %H:%M') if st.session_state.last_scan else ''}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for i, s in enumerate(st.session_state.suggestions):
        cat  = s.get("category", "AI")
        diff = s.get("difficulty", "o'rta")
        pri  = s.get("priority", "o'rta")
        wow  = s.get("wow_factor", 7)
        bg   = cat_bg.get(cat, "#f8f8ff")
        bc   = cat_bc.get(cat, "#e0e0ff")
        dc   = diff_c.get(diff, "#6b7280")
        di   = diff_i.get(diff, "🔵")
        pc   = pri_c.get(pri, "#6b7280")
        stars = "⭐" * min(int(wow // 2), 5)

        st.markdown(f"""
        <div style="background:{bg};border:1.5px solid {bc};border-radius:16px;
                    padding:16px 18px;margin:10px 0;position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;height:3px;
                        width:{wow*10}%;background:linear-gradient(90deg,#6366f1,#a855f7);"></div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:24px;">{s.get('emoji','💡')}</span>
                    <div>
                        <p style="font-size:15px;font-weight:700;color:#1e1e2e !important;margin:0;">
                            {s.get('name','')}</p>
                        <span style="font-size:11px;color:{pc} !important;font-weight:600;
                                     background:{pc}18;padding:1px 7px;border-radius:20px;">
                            {pri.upper()}</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <p style="font-size:11px;color:#9ca3af !important;margin:0;">{cat}</p>
                    <p style="font-size:13px;margin:2px 0 0;">{stars} {wow}/10</p>
                </div>
            </div>
            <p style="font-size:14px;color:#374151 !important;margin:0 0 8px;line-height:1.6;">
                {s.get('description','')}</p>
            <div style="background:rgba(99,102,241,0.07);border-radius:10px;padding:10px 12px;margin:8px 0;">
                <p style="font-size:12px;font-weight:700;color:#4f46e5 !important;margin:0 0 3px;">
                    ✨ Nima uchun qiziqarli:</p>
                <p style="font-size:13px;color:#374151 !important;margin:0;">{s.get('why_cool','')}</p>
            </div>
            <div style="background:rgba(16,185,129,0.07);border-radius:10px;padding:10px 12px;margin:8px 0;">
                <p style="font-size:12px;font-weight:700;color:#059669 !important;margin:0 0 3px;">
                    🔧 Qanday qurish:</p>
                <p style="font-size:13px;color:#374151 !important;margin:0;">{s.get('how_to_build','')}</p>
            </div>
            <span style="font-size:11px;color:{dc} !important;background:{dc}15;
                         padding:3px 10px;border-radius:20px;font-weight:600;">
                {di} {diff.upper()}</span>
        </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📥 JSON", 
            data=json.dumps(st.session_state.suggestions, ensure_ascii=False, indent=2),
            file_name=f"somo_ideas_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json", use_container_width=True)
    with c2:
        txt = f"SOMO AI — FUNKSIYA G'OYALAR\n{'='*40}\n{datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        for i, s in enumerate(st.session_state.suggestions, 1):
            txt += f"{i}. {s.get('emoji','')} {s.get('name','')}\n"
            txt += f"   {s.get('description','')}\n"
            txt += f"   ✨ {s.get('why_cool','')}\n"
            txt += f"   🔧 {s.get('how_to_build','')}\n\n"
        st.download_button("📄 TXT", data=txt.encode("utf-8"),
            file_name=f"somo_ideas_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain", use_container_width=True)

    st.markdown("<hr style='border:none;border-top:1px solid #eef0ff;margin:16px 0;'>",
                unsafe_allow_html=True)

# ── Bo'sh chat kartalar ──
if not st.session_state.messages:
    st.markdown("""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;
                max-width:520px;margin:10px auto 24px;">
        <div style="background:#fff;border:1px solid #eef0ff;border-radius:14px;padding:16px;
                    box-shadow:0 2px 8px rgba(99,102,241,0.06);">
            <span style="font-size:22px;">💡</span>
            <p style="font-size:13px;font-weight:600;color:#1e1e2e;margin:8px 0 2px;">Savol bering</p>
            <p style="font-size:12px;color:#9ca3af;margin:0;">Istalgan mavzu haqida</p>
        </div>
        <div style="background:#fff;border:1px solid #eef0ff;border-radius:14px;padding:16px;
                    box-shadow:0 2px 8px rgba(99,102,241,0.06);">
            <span style="font-size:22px;">✍️</span>
            <p style="font-size:13px;font-weight:600;color:#1e1e2e;margin:8px 0 2px;">Matn yozdiring</p>
            <p style="font-size:12px;color:#9ca3af;margin:0;">Maqola, xat, rezyume</p>
        </div>
        <div style="background:#fff;border:1px solid #eef0ff;border-radius:14px;padding:16px;
                    box-shadow:0 2px 8px rgba(99,102,241,0.06);">
            <span style="font-size:22px;">🔍</span>
            <p style="font-size:13px;font-weight:600;color:#1e1e2e;margin:8px 0 2px;">Tushuntirish</p>
            <p style="font-size:12px;color:#9ca3af;margin:0;">Murakkab mavzular</p>
        </div>
        <div style="background:#fff;border:1px solid #eef0ff;border-radius:14px;padding:16px;
                    box-shadow:0 2px 8px rgba(99,102,241,0.06);">
            <span style="font-size:22px;">💻</span>
            <p style="font-size:13px;font-weight:600;color:#1e1e2e;margin:8px 0 2px;">Kod yozdiring</p>
            <p style="font-size:12px;color:#9ca3af;margin:0;">Python, JS va boshqa</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Xabarlar
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ──
if prompt := st.chat_input("Somo AI ga xabar yuboring..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        models_to_try = [model_name]
        if model_name != "llama3.1-8b":
            models_to_try.append("llama3.1-8b")

        for try_model in models_to_try:
            try:
                stream = client.chat.completions.create(
                    model=try_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.messages]
                    ],
                    stream=True,
                    max_tokens=1024,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    for char in delta:
                        full_response += char
                        placeholder.markdown(full_response + "▌")
                        time.sleep(0.007)
                placeholder.markdown(full_response)
                break
            except Exception as e:
                err = str(e)
                if "404" in err or "not_found" in err:
                    continue
                full_response = f"❌ Xatolik: {err}"
                placeholder.markdown(full_response)
                break

        if not full_response:
            full_response = "❌ Model javob bermadi."
            placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
