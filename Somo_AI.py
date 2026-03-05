import streamlit as st
from cerebras.cloud.sdk import Cerebras
import time
import json
import requests
from datetime import datetime, timedelta

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

/* Taklif kartasi */
.suggestion-card {
    background: linear-gradient(135deg, #f0f4ff, #faf0ff);
    border: 1.5px solid #c7d2fe;
    border-radius: 16px;
    padding: 16px 18px;
    margin: 8px 0;
    position: relative;
}
.suggestion-title {
    font-size: 13px; font-weight: 700;
    color: #4f46e5 !important;
    text-transform: uppercase; letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.suggestion-text {
    font-size: 14px; color: #374151 !important; line-height: 1.6;
}
.suggestion-source {
    font-size: 11px; color: #9ca3af !important; margin-top: 8px;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #c7d2fe; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #6366f1; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# CREATOR PASSWORD — faqat yaratuvchi ko'radi
# ══════════════════════════════════════════════
CREATOR_PASSWORD = st.secrets.get("CREATOR_PASSWORD", "somo2026")

# ══════════════════════════════════════════════
# AI CLIENTS
# ══════════════════════════════════════════════
@st.cache_resource
def get_client():
    return Cerebras(api_key=st.secrets["CEREBRAS_API_KEY"])

try:
    client = get_client()
except Exception:
    st.error("❌ CEREBRAS_API_KEY topilmadi.")
    st.code('CEREBRAS_API_KEY = "csk-xxxx"\nCREATOR_PASSWORD = "sizning_parolingiz"', language="toml")
    st.stop()

# ══════════════════════════════════════════════
# INTERNET YANGILIKLARI OLISH
# ══════════════════════════════════════════════
def fetch_ai_news():
    """AI va tech yangiliklar RSS orqali olish"""
    feeds = [
        "https://techcrunch.com/feed/",
        "https://feeds.feedburner.com/oreilly/radar",
        "https://huggingface.co/blog/feed.xml",
    ]
    articles = []
    for url in feeds:
        try:
            r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                # RSS dan sarlavhalarni oddiy parse qilish
                import re
                titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', r.text)
                if not titles:
                    titles = re.findall(r'<title>(.*?)</title>', r.text)
                titles = [t.strip() for t in titles[1:6] if t.strip()]  # birinchisi feed nomi
                source = url.split('/')[2].replace('www.', '').replace('feeds.', '')
                for t in titles:
                    articles.append({"title": t, "source": source})
        except:
            continue
    return articles[:12]  # max 12 ta yangilik

def generate_suggestions(articles, current_features, client):
    """AI yordamida funksiya takliflari yaratish"""
    if not articles:
        news_text = "Internet yangiliklari mavjud emas (tarmoq xatosi)."
    else:
        news_text = "\n".join([f"- {a['title']} ({a['source']})" for a in articles])

    prompt = f"""Sen Somo AI dasturining tahlilchisisan.
    
Hozirgi dastur funksiyalari:
{current_features}

Internetdan olingan so'nggi AI/tech yangiliklar:
{news_text}

Ushbu yangiliklarni tahlil qilib, dasturga QO'SHISH MUMKIN bo'lgan 5 ta yangi funksiya taklif qil.
Har bir taklif uchun:
1. Funksiya nomi
2. Nima uchun kerak (yangilikka asoslanib)
3. Qanday qo'shish mumkin (texnik jihat)

JSON formatida qaytarasan:
[
  {{
    "name": "Funksiya nomi",
    "reason": "Nima uchun kerak",
    "how": "Qanday amalga oshirish",
    "priority": "yuqori/o'rta/past",
    "source": "qaysi yangilikdan ilhomlangan"
  }}
]
Faqat JSON. Hech qanday izoh yozma."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            stream=False,
        )
        text = response.choices[0].message.content
        import re
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        # fallback: llama3.1-8b
        try:
            response = client.chat.completions.create(
                model="llama3.1-8b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                stream=False,
            )
            text = response.choices[0].message.content
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
    return []

# ══════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_creator" not in st.session_state:
    st.session_state.is_creator = False
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []
if "last_scan" not in st.session_state:
    st.session_state.last_scan = None
if "show_creator_panel" not in st.session_state:
    st.session_state.show_creator_panel = False

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px 0 10px;">
        <div style="font-size:52px; margin-bottom:8px;">✨</div>
        <h2 style="font-size:22px; font-weight:700; color:#4f46e5 !important; margin:0;">Somo AI</h2>
        <p style="font-size:12px; color:#9ca3af !important; margin:4px 0 0;">Cerebras · Aqlli yordamchi</p>
    </div>
    <hr style="border:none; border-top:1px solid #eef0ff; margin:12px 0;">
    """, unsafe_allow_html=True)

    model_name = st.selectbox("Model:", ["llama-3.3-70b", "llama3.1-8b"], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🗑️ Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # ── Yaratuvchi paneli ──
    st.markdown("<hr style='border:none;border-top:1px solid #eef0ff;margin:16px 0;'>", unsafe_allow_html=True)

    if not st.session_state.is_creator:
        st.markdown("<p style='font-size:12px;color:#9ca3af !important;text-align:center;'>🔐 Yaratuvchi paneli</p>",
                    unsafe_allow_html=True)
        creator_pw = st.text_input("Parol:", type="password", placeholder="••••••••",
                                    label_visibility="collapsed")
        if st.button("Kirish", use_container_width=True):
            if creator_pw == CREATOR_PASSWORD:
                st.session_state.is_creator = True
                st.rerun()
            else:
                st.error("❌ Noto'g'ri parol")
    else:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#f0f4ff,#faf0ff);border:1px solid #c7d2fe;
                    border-radius:12px;padding:12px;text-align:center;margin-bottom:12px;">
            <span style="font-size:20px;">👑</span>
            <p style="font-size:13px;font-weight:700;color:#4f46e5 !important;margin:4px 0 0;">
                Yaratuvchi rejimi</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔍 Internetni skanerlash", use_container_width=True, type="primary"):
            with st.spinner("Yangiliklar tekshirilmoqda..."):
                articles = fetch_ai_news()
                current_features = """
                - Cerebras AI bilan oddiy chat
                - Streaming animatsiyali javoblar
                - Model tanlash (70b / 8b)
                - Chat tarixi tozalash
                - Yaratuvchi paneli
                """
                suggestions = generate_suggestions(articles, current_features, client)
                st.session_state.suggestions = suggestions
                st.session_state.last_scan = datetime.now()
            st.rerun()

        if st.session_state.last_scan:
            elapsed = datetime.now() - st.session_state.last_scan
            st.markdown(f"""
            <p style="font-size:11px;color:#9ca3af !important;text-align:center;margin-top:8px;">
                🕐 Oxirgi skan: {st.session_state.last_scan.strftime('%H:%M')}
                ({elapsed.seconds // 60} daqiqa oldin)
            </p>
            """, unsafe_allow_html=True)

        if st.button("🚪 Chiqish", use_container_width=True):
            st.session_state.is_creator = False
            st.session_state.suggestions = []
            st.rerun()

    # Statistika
    msg_count = len(st.session_state.messages)
    st.markdown(f"""
    <div style="margin-top:16px;background:#f8f8ff;border:1px solid #eef0ff;
                border-radius:12px;padding:14px 16px;">
        <p style="font-size:11px;color:#9ca3af !important;margin:0 0 8px;
                  font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Sessiya</p>
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:13px;color:#6b7280 !important;">💬 Xabarlar</span>
            <span style="font-size:15px;font-weight:700;color:#4f46e5 !important;">{msg_count}</span>
        </div>
    </div>
    <div style="padding-top:24px;text-align:center;">
        <p style="font-size:11px;color:#d1d5db !important;">© 2026 Somo AI</p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# ASOSIY KONTENT
# ══════════════════════════════════════════════
st.markdown("""
<div style="text-align:center; padding:32px 0 16px;">
    <h1 style="font-size:30px; font-weight:700; color:#1e1e2e; letter-spacing:-0.8px; margin:0;">
        ✨ Somo <span style="color:#6366f1;">AI</span>
    </h1>
    <p style="font-size:14px; color:#9ca3af; margin:8px 0 0;">
        Savolingizni yozing — javob shu zahoti keladi
    </p>
</div>
""", unsafe_allow_html=True)

# ── Yaratuvchi: takliflar paneli ──────────────────────
if st.session_state.is_creator and st.session_state.suggestions:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#667eea15,#764ba215);
                border:1.5px solid #c7d2fe;border-radius:20px;padding:20px 22px;margin-bottom:24px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
            <span style="font-size:24px;">🤖</span>
            <div>
                <p style="font-size:15px;font-weight:700;color:#4f46e5 !important;margin:0;">
                    AI Taklif Tizimi</p>
                <p style="font-size:12px;color:#9ca3af !important;margin:0;">
                    Internet yangiliklari asosida yangi funksiyalar</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    priority_colors = {"yuqori": "#ef4444", "o'rta": "#f59e0b", "past": "#10b981"}
    priority_icons  = {"yuqori": "🔴", "o'rta": "🟡", "past": "🟢"}

    for i, sug in enumerate(st.session_state.suggestions):
        p = sug.get("priority", "o'rta")
        pc = priority_colors.get(p, "#6366f1")
        pi = priority_icons.get(p, "🔵")
        st.markdown(f"""
        <div style="background:white;border:1px solid #eef0ff;border-left:4px solid {pc};
                    border-radius:12px;padding:14px 16px;margin:8px 0;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <p style="font-size:14px;font-weight:700;color:#1e1e2e !important;margin:0;">
                    {i+1}. {sug.get('name','')}</p>
                <span style="font-size:11px;color:{pc} !important;font-weight:600;
                             background:{pc}15;padding:2px 8px;border-radius:20px;">
                    {pi} {p.upper()}</span>
            </div>
            <p style="font-size:13px;color:#374151 !important;margin:8px 0 4px;line-height:1.5;">
                📌 <b>Nima uchun:</b> {sug.get('reason','')}</p>
            <p style="font-size:13px;color:#374151 !important;margin:4px 0;line-height:1.5;">
                🔧 <b>Qanday:</b> {sug.get('how','')}</p>
            <p style="font-size:11px;color:#9ca3af !important;margin:8px 0 0;">
                💡 Manba: {sug.get('source','internet')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Export
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 JSON yuklab olish",
            data=json.dumps(st.session_state.suggestions, ensure_ascii=False, indent=2),
            file_name=f"somo_suggestions_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )
    with col2:
        # Oddiy matn formatida
        text_report = f"SOMO AI — FUNKSIYA TAKLIFLARI\n{datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        for i, s in enumerate(st.session_state.suggestions):
            text_report += f"{i+1}. {s.get('name','')}\n"
            text_report += f"   Nima uchun: {s.get('reason','')}\n"
            text_report += f"   Qanday: {s.get('how','')}\n"
            text_report += f"   Muhimlik: {s.get('priority','')}\n\n"
        st.download_button(
            "📄 TXT yuklab olish",
            data=text_report.encode("utf-8"),
            file_name=f"somo_suggestions_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ── Bo'sh chat kartalar ───────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;
                max-width:500px; margin:10px auto 28px;">
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
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ══════════════════════════════════════════════
# CHAT INPUT
# ══════════════════════════════════════════════
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
                elif "api_key" in err.lower() or "auth" in err.lower():
                    full_response = "❌ API kalit noto'g'ri."
                    placeholder.markdown(full_response)
                    break
                else:
                    full_response = f"❌ Xatolik: {err}"
                    placeholder.markdown(full_response)
                    break

        if not full_response:
            full_response = "❌ Model javob bermadi."
            placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
