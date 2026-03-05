import streamlit as st
from cerebras.cloud.sdk import Cerebras
import time
import json
from datetime import datetime

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
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e8eaf6 !important;
    box-shadow: 2px 0 12px rgba(99,102,241,0.06);
}
[data-testid="stSidebar"] * { color: #1e1e2e !important; }
[data-testid="stSidebarNav"] { display: none !important; }
div[data-testid="stSidebar"] button {
    background: #f1f0ff !important; color: #4f46e5 !important;
    border: 1px solid #e0e0ff !important; border-radius: 10px !important;
    font-weight: 600 !important; transition: all 0.2s !important;
}
div[data-testid="stSidebar"] button:hover {
    background: #4f46e5 !important; color: white !important; border-color: transparent !important;
}
#MainMenu, footer, header { display: none !important; }
.stChatMessage {
    background: #ffffff !important; border: 1px solid #eef0ff !important;
    border-radius: 16px !important; box-shadow: 0 2px 8px rgba(99,102,241,0.07) !important;
    padding: 14px 18px !important; margin: 8px 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #eef2ff, #f5f0ff) !important;
    border-color: #ddd6fe !important;
}
.stChatInputContainer { background: transparent !important; border: none !important; padding: 12px 0 20px !important; }
[data-testid="stChatInput"] {
    background: #ffffff !important; border: 1.5px solid #e0e0ff !important;
    border-radius: 16px !important; box-shadow: 0 4px 20px rgba(99,102,241,0.10) !important;
    transition: all 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #6366f1 !important; box-shadow: 0 4px 24px rgba(99,102,241,0.18) !important;
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
[data-testid="stChatInput"] button:hover { background: #4f46e5 !important; transform: scale(1.05) !important; }
.stSelectbox > div > div {
    background: #f8f8ff !important; border: 1.5px solid #e0e0ff !important; border-radius: 10px !important;
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

CURRENT_FEATURES = """
Hozirgi Somo AI funksiyalari:
- Cerebras AI (llama-3.3-70b / llama3.1-8b) bilan oddiy chat
- Animatsiyali streaming javoblar (harfma-harf)
- Model tanlash (sidebar)
- Chat tarixi tozalash
- Yaratuvchi paneli (parol bilan)
- Sessiya statistikasi

Dastur texnologiyasi: Python + Streamlit + Cerebras API
Foydalanuvchilar: O'zbek va rus tilida so'zlashuvchilar
"""

# ══════════════════════════════════════════════
# AI CLIENT
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

# ══════════════════════════════════════════════
# AI CALL (stream=False)
# ══════════════════════════════════════════════
def ask_ai(prompt, system="Sen foydali yordamchisan.", max_tokens=2000):
    for model in ["llama-3.3-70b", "llama3.1-8b"]:
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                max_tokens=max_tokens,
            )
            return r.choices[0].message.content
        except Exception as e:
            if "404" in str(e) or "not_found" in str(e):
                continue
            return f"Xatolik: {e}"
    return "Hech qanday model javob bermadi."

# ══════════════════════════════════════════════
# SMART SUGGESTIONS GENERATOR
# ══════════════════════════════════════════════
def generate_smart_suggestions(chat_history):
    # Chat tarixidan foydalanuvchi so'ragan narsalarni ajratib olish
    user_msgs = [m["content"] for m in chat_history if m["role"] == "user"]
    user_context = ""
    if user_msgs:
        user_context = f"\nFoydalanuvchilar so'ragan narsalar (oxirgi {len(user_msgs)} ta savol):\n"
        user_context += "\n".join([f"- {m[:100]}" for m in user_msgs[-10:]])

    system = """Sen Somo AI dasturining strategik tahlilchisisan.
Sen AI/tech sohasida chuqur bilimga egasan.
Faqat JSON formatida javob berasan. Hech qanday izoh yoki matn yozma."""

    prompt = f"""Quyidagi AI chatbot dasturini tahlil qil va unga QO'SHISH MUMKIN bo'lgan 6 ta JUDA QIZIQARLI va REAL funksiya taklif qil.

{CURRENT_FEATURES}
{user_context}

Muhim talablar:
1. Takliflar FAQAT AI chatbot/dastur uchun mantiqli bo'lsin
2. Har bir taklif texnik jihatdan AMALGA OSHIRILISHI MUMKIN bo'lsin
3. Foydalanuvchiga REAL FOYDA bersin
4. Qiziqarli, original va ZAMONAVIY g'oyalar bo'lsin
5. O'zbek foydalanuvchilar uchun mos bo'lsin

Takliflar kategoriyalari (har biridan bir-ikkitadan):
- UX/UI yaxshilash
- Yangi AI qobiliyatlar
- Mahsuldorlik vositalari
- O'zbek tili uchun maxsus
- Integratsiyalar

JSON formatda qaytarasan:
[
  {{
    "name": "Funksiya nomi (qisqa, jozibali)",
    "emoji": "mos emoji",
    "category": "UX/AI/Mahsuldorlik/O'zbek/Integratsiya",
    "description": "Nima qiladi - 1-2 jumlada tushunarli tushuntirish",
    "why_cool": "Nima uchun bu JUDA qiziqarli va foydali",
    "how_to_build": "Texnik jihatdan qanday qurish (konkret: qaysi API, kutubxona)",
    "difficulty": "oson/o'rta/qiyin",
    "priority": "yuqori/o'rta/past",
    "wow_factor": 1-10
  }}
]"""

    raw = ask_ai(prompt, system, max_tokens=2500)

    import re
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass

    # Fallback: manual takliflar
    return [
        {
            "name": "Ovozli chat",
            "emoji": "🎙️",
            "category": "AI",
            "description": "Foydalanuvchi mikrofondan gapiradi, AI javob beradi",
            "why_cool": "Qo'l bilan yozmasdan, xuddi odamga gaplashgandek",
            "how_to_build": "Streamlit audio input + Whisper API (OpenAI) + Cerebras",
            "difficulty": "o'rta",
            "priority": "yuqori",
            "wow_factor": 9
        },
        {
            "name": "O'zbek tili tekshirgich",
            "emoji": "📝",
            "category": "O'zbek",
            "description": "Yozgan matnidagi grammatika xatolarini topib tuzatadi",
            "why_cool": "O'zbek tilida bunday vosita deyarli yo'q",
            "how_to_build": "Cerebras ga maxsus o'zbek grammatika prompti",
            "difficulty": "oson",
            "priority": "yuqori",
            "wow_factor": 8
        },
    ]

# ══════════════════════════════════════════════
# SESSION
# ══════════════════════════════════════════════
defaults = {
    "messages": [],
    "is_creator": False,
    "suggestions": [],
    "last_scan": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px 0 10px;">
        <div style="font-size:48px; margin-bottom:8px;">✨</div>
        <h2 style="font-size:22px; font-weight:700; color:#4f46e5 !important; margin:0;">Somo AI</h2>
        <p style="font-size:12px; color:#9ca3af !important; margin:4px 0 0;">Cerebras · Aqlli yordamchi</p>
    </div>
    <hr style="border:none; border-top:1px solid #eef0ff; margin:10px 0;">
    """, unsafe_allow_html=True)

    model_name = st.selectbox("⚡ Model:", ["llama-3.3-70b", "llama3.1-8b"],
                               label_visibility="visible")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🗑️ Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # ── Yaratuvchi paneli ──
    st.markdown("<hr style='border:none;border-top:1px solid #eef0ff;margin:14px 0;'>",
                unsafe_allow_html=True)

    if not st.session_state.is_creator:
        st.markdown("<p style='font-size:12px;color:#9ca3af !important;text-align:center;margin-bottom:8px;'>🔐 Yaratuvchi</p>",
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
            <p style="font-size:13px;font-weight:700;color:#4f46e5 !important;margin:2px 0 0;">
                Yaratuvchi rejimi</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🧠 Taklif yaratish", use_container_width=True, type="primary"):
            with st.spinner("AI o'zi haqida o'ylamoqda..."):
                suggs = generate_smart_suggestions(st.session_state.messages)
                st.session_state.suggestions = suggs
                st.session_state.last_scan = datetime.now()
            st.rerun()

        if st.session_state.last_scan:
            st.markdown(f"""
            <p style="font-size:11px;color:#9ca3af !important;text-align:center;margin:6px 0;">
                🕐 {st.session_state.last_scan.strftime('%H:%M')} da yaratildi
            </p>""", unsafe_allow_html=True)

        if st.button("🚪 Chiqish", use_container_width=True):
            st.session_state.is_creator = False
            st.session_state.suggestions = []
            st.rerun()

    # Stat
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
# ASOSIY SAHIFA
# ══════════════════════════════════════════════
st.markdown("""
<div style="text-align:center; padding:28px 0 14px;">
    <h1 style="font-size:30px;font-weight:700;color:#1e1e2e;letter-spacing:-0.8px;margin:0;">
        ✨ Somo <span style="color:#6366f1;">AI</span>
    </h1>
    <p style="font-size:14px;color:#9ca3af;margin:6px 0 0;">
        Savolingizni yozing — javob shu zahoti keladi
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# YARATUVCHI: TAKLIFLAR
# ══════════════════════════════════════════════
if st.session_state.is_creator and st.session_state.suggestions:

    diff_color = {"oson": "#10b981", "o'rta": "#f59e0b", "qiyin": "#ef4444"}
    diff_icon  = {"oson": "🟢", "o'rta": "🟡", "qiyin": "🔴"}
    pri_color  = {"yuqori": "#ef4444", "o'rta": "#f59e0b", "past": "#6b7280"}
    cat_bg     = {
        "UX": "#eff6ff", "AI": "#f5f0ff", "Mahsuldorlik": "#f0fdf4",
        "O'zbek": "#fff7ed", "Integratsiya": "#fdf2f8"
    }
    cat_bc     = {
        "UX": "#bfdbfe", "AI": "#ddd6fe", "Mahsuldorlik": "#bbf7d0",
        "O'zbek": "#fed7aa", "Integratsiya": "#fbcfe8"
    }

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#667eea18,#764ba218);
                border:1.5px solid #c7d2fe;border-radius:20px;
                padding:18px 20px;margin-bottom:20px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <span style="font-size:22px;">🧠</span>
            <div>
                <p style="font-size:15px;font-weight:700;color:#4f46e5 !important;margin:0;">
                    AI Taklif Tizimi</p>
                <p style="font-size:12px;color:#9ca3af !important;margin:0;">
                    {len(st.session_state.suggestions)} ta taklif · 
                    {st.session_state.last_scan.strftime('%d.%m.%Y %H:%M') if st.session_state.last_scan else ''}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for i, s in enumerate(st.session_state.suggestions):
        cat   = s.get("category", "AI")
        diff  = s.get("difficulty", "o'rta")
        pri   = s.get("priority", "o'rta")
        wow   = s.get("wow_factor", 7)
        bg    = cat_bg.get(cat, "#f8f8ff")
        bc    = cat_bc.get(cat, "#e0e0ff")
        dc    = diff_color.get(diff, "#6b7280")
        di    = diff_icon.get(diff, "🔵")
        pc    = pri_color.get(pri, "#6b7280")
        wow_stars = "⭐" * min(int(wow // 2), 5)

        st.markdown(f"""
        <div style="background:{bg};border:1.5px solid {bc};border-radius:16px;
                    padding:16px 18px;margin:10px 0;position:relative;overflow:hidden;">

            <!-- Wow factor bar -->
            <div style="position:absolute;top:0;left:0;height:3px;width:{wow*10}%;
                        background:linear-gradient(90deg,#6366f1,#a855f7);border-radius:2px;"></div>

            <!-- Header -->
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
                    <p style="font-size:13px;margin:2px 0 0;">{wow_stars} {wow}/10</p>
                </div>
            </div>

            <!-- Description -->
            <p style="font-size:14px;color:#374151 !important;margin:0 0 8px;line-height:1.6;">
                {s.get('description','')}
            </p>

            <!-- Why cool -->
            <div style="background:rgba(99,102,241,0.07);border-radius:10px;padding:10px 12px;margin:8px 0;">
                <p style="font-size:12px;font-weight:700;color:#4f46e5 !important;margin:0 0 3px;">
                    ✨ Nima uchun qiziqarli:</p>
                <p style="font-size:13px;color:#374151 !important;margin:0;">
                    {s.get('why_cool','')}</p>
            </div>

            <!-- How to build -->
            <div style="background:rgba(16,185,129,0.07);border-radius:10px;padding:10px 12px;margin:8px 0;">
                <p style="font-size:12px;font-weight:700;color:#059669 !important;margin:0 0 3px;">
                    🔧 Qanday qurish:</p>
                <p style="font-size:13px;color:#374151 !important;margin:0;">
                    {s.get('how_to_build','')}</p>
            </div>

            <!-- Footer -->
            <div style="display:flex;gap:8px;margin-top:6px;">
                <span style="font-size:11px;color:{dc} !important;background:{dc}15;
                             padding:3px 10px;border-radius:20px;font-weight:600;">
                    {di} {diff.upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Export tugmalari
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "📥 JSON",
            data=json.dumps(st.session_state.suggestions, ensure_ascii=False, indent=2),
            file_name=f"somo_ideas_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )
    with c2:
        report = f"SOMO AI — FUNKSIYA G'OYALAR\n{'='*40}\n{datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        for i, s in enumerate(st.session_state.suggestions, 1):
            report += f"{i}. {s.get('emoji','')} {s.get('name','')}\n"
            report += f"   Kategoriya: {s.get('category','')} | Muhimlik: {s.get('priority','')} | Wow: {s.get('wow_factor','')}/10\n"
            report += f"   {s.get('description','')}\n"
            report += f"   ✨ {s.get('why_cool','')}\n"
            report += f"   🔧 {s.get('how_to_build','')}\n\n"
        st.download_button(
            "📄 TXT",
            data=report.encode("utf-8"),
            file_name=f"somo_ideas_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("<hr style='border:none;border-top:1px solid #eef0ff;margin:16px 0;'>",
                unsafe_allow_html=True)

# ══════════════════════════════════════════════
# CHAT
# ══════════════════════════════════════════════
if not st.session_state.messages:
    st.markdown("""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;
                max-width:500px;margin:10px auto 24px;">
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

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Somo AI ga xabar yuboring..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        models_to_try = [model_name, "llama3.1-8b"] if model_name != "llama3.1-8b" else ["llama3.1-8b"]

        for try_model in models_to_try:
            try:
                stream = client.chat.completions.create(
                    model=try_model,
                    messages=[{"role": m["role"], "content": m["content"]}
                               for m in st.session_state.messages],
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
