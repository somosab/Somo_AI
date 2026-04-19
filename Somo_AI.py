"""
Somo AI — Streamlit versiyasi
Ishga tushirish: streamlit run app.py
"""

import streamlit as st
import json
import time
import datetime
from typing import Generator

# ─── Sahifa sozlamalari ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Somo AI — Aqlli Yordamchi",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Umumiy stil */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #080e1c;
}
[data-testid="stSidebar"] * {
    color: #f0f4ff;
}

/* Chat xabarlari */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    margin-bottom: 8px;
}

/* Input */
[data-testid="stChatInputContainer"] {
    border-top: 1px solid rgba(255,255,255,0.08);
    padding-top: 10px;
}

/* Tugmalar */
.stButton > button {
    border-radius: 8px;
    transition: all 0.2s ease;
}

/* Muvaffaqiyat rangi */
.success-msg {
    color: #10b981;
    font-size: 13px;
}

/* Token panel */
.token-box {
    background: rgba(0,229,255,0.06);
    border: 1px solid rgba(0,229,255,0.15);
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 8px;
}

/* Sarlavha gradient */
.main-title {
    background: linear-gradient(135deg, #00e5ff, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 28px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# ─── Konstantlar ──────────────────────────────────────────────────────────────
MODELS = {
    "llama-3.3-70b-versatile": {"icon": "🦙", "label": "Llama 3.3 70B", "desc": "Kuchli · Groq"},
    "llama-3.1-8b-instant":    {"icon": "⚡", "label": "Llama 3.1 8B",  "desc": "Eng tez · Groq"},
    "mixtral-8x7b-32768":      {"icon": "🔀", "label": "Mixtral 8x7B",  "desc": "MoE · Groq"},
    "gemma2-9b-it":            {"icon": "💎", "label": "Gemma 2 9B",    "desc": "Google · Groq"},
}

DEFAULT_SYSTEM = (
    "Sen Somo AI — O'zbekistondagi eng aqlli AI yordamchisan. "
    "Foydalanuvchilarga dasturlash, ta'lim va boshqa sohalarda O'zbek tilida yordam berasan."
)

# ─── Session state boshlash ───────────────────────────────────────────────────
def init_state():
    defaults = {
        "api_key": "",
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.7,
        "max_tokens": 2048,
        "system_prompt": DEFAULT_SYSTEM,
        "conversations": {},       # {id: {title, messages, created_at}}
        "current_conv_id": None,
        "total_tokens_used": 0,
        "user_name": "Foydalanuvchi",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── Yordamchi funksiyalar ────────────────────────────────────────────────────
def new_conv_id() -> str:
    return f"conv_{int(time.time()*1000)}"

def create_conversation(title: str = "Yangi suhbat") -> str:
    cid = new_conv_id()
    st.session_state.conversations[cid] = {
        "title": title,
        "messages": [],
        "created_at": datetime.datetime.now().strftime("%H:%M"),
    }
    st.session_state.current_conv_id = cid
    return cid

def get_current_messages() -> list:
    cid = st.session_state.current_conv_id
    if cid and cid in st.session_state.conversations:
        return st.session_state.conversations[cid]["messages"]
    return []

def add_message(role: str, content: str):
    cid = st.session_state.current_conv_id
    if cid and cid in st.session_state.conversations:
        st.session_state.conversations[cid]["messages"].append(
            {"role": role, "content": content}
        )
        # Birinchi user xabardan suhbat nomini avtomatik qil
        msgs = st.session_state.conversations[cid]["messages"]
        if len(msgs) == 1 and role == "user":
            title = content[:45] + "..." if len(content) > 45 else content
            st.session_state.conversations[cid]["title"] = title

def groq_stream(messages: list) -> Generator:
    """Groq API orqali streaming javob qaytaradi."""
    try:
        from groq import Groq
        client = Groq(api_key=st.session_state.api_key)
        system = [{"role": "system", "content": st.session_state.system_prompt}]
        response = client.chat.completions.create(
            model=st.session_state.model,
            messages=system + messages,
            temperature=st.session_state.temperature,
            max_tokens=st.session_state.max_tokens,
            stream=True,
        )
        total = 0
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            total += len(delta.split())
            yield delta
        st.session_state.total_tokens_used += total
    except ImportError:
        yield "⚠️ `groq` kutubxonasi o'rnatilmagan. Terminalda: `pip install groq`"
    except Exception as e:
        err = str(e)
        if "401" in err or "api_key" in err.lower() or "authentication" in err.lower():
            yield "🔑 API kaliti noto'g'ri yoki kiritilmagan. Iltimos, sidebar dagi sozlamalarda Groq API kalitingizni kiriting."
        elif "model" in err.lower():
            yield f"⚠️ Model xatosi: {err}"
        else:
            yield f"⚠️ Xato yuz berdi: {err}"

def greeting() -> str:
    h = datetime.datetime.now().hour
    if   5  <= h < 12: return "Xayrli tong"
    elif 12 <= h < 17: return "Xayrli kun"
    elif 17 <= h < 21: return "Xayrli kech"
    else:              return "Yaxshi tunlar"

def export_json() -> str:
    cid = st.session_state.current_conv_id
    if not cid:
        return ""
    conv = st.session_state.conversations.get(cid, {})
    data = {
        "title": conv.get("title", "Suhbat"),
        "model": st.session_state.model,
        "created_at": conv.get("created_at", ""),
        "exported_at": datetime.datetime.now().isoformat(),
        "messages": conv.get("messages", []),
    }
    return json.dumps(data, ensure_ascii=False, indent=2)

def export_markdown() -> str:
    cid = st.session_state.current_conv_id
    if not cid:
        return ""
    conv = st.session_state.conversations.get(cid, {})
    lines = [f"# {conv.get('title', 'Suhbat')}\n",
             f"**Model:** {st.session_state.model}  \n**Sana:** {conv.get('created_at', '')}\n\n---\n"]
    for m in conv.get("messages", []):
        role_label = "**Siz:**" if m["role"] == "user" else "**Somo AI:**"
        lines.append(f"{role_label}\n\n{m['content']}\n\n---\n")
    return "\n".join(lines)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 0 16px">
        <div style="width:38px;height:38px;border-radius:10px;
                    background:linear-gradient(135deg,#00e5ff,#7c3aed);
                    display:flex;align-items:center;justify-content:center;
                    font-weight:800;font-size:18px;color:#000">S</div>
        <span style="font-size:20px;font-weight:700;">Somo AI</span>
    </div>
    """, unsafe_allow_html=True)

    # Yangi suhbat
    if st.button("✨  Yangi suhbat", use_container_width=True, type="primary"):
        create_conversation()
        st.rerun()

    st.divider()

    # Suhbat tarixi
    convs = st.session_state.conversations
    if convs:
        st.markdown("**💬 Suhbatlar**")
        for cid, conv in reversed(list(convs.items())):
            is_active = cid == st.session_state.current_conv_id
            label = ("🟢 " if is_active else "   ") + conv["title"][:32]
            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(label, key=f"load_{cid}", use_container_width=True):
                    st.session_state.current_conv_id = cid
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"del_{cid}"):
                    del st.session_state.conversations[cid]
                    if st.session_state.current_conv_id == cid:
                        st.session_state.current_conv_id = None
                    st.rerun()
    else:
        st.caption("Hali suhbatlar yo'q")

    st.divider()

    # Token hisoblagichi
    tok = st.session_state.total_tokens_used
    st.markdown(f"""
    <div class="token-box">
        <div style="font-size:11px;color:#8899bb;margin-bottom:4px">📊 Taxminiy token sarfi</div>
        <div style="font-size:16px;font-weight:600;color:#00e5ff">{tok:,}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ─── SOZLAMALAR ───────────────────────────────────────────────────────────
    with st.expander("⚙️ Sozlamalar", expanded=False):

        st.markdown("**🔑 Groq API kaliti**")
        api_key_input = st.text_input(
            "API kaliti",
            value=st.session_state.api_key,
            type="password",
            placeholder="gsk-xxxxxxxxxxxxxxxxxxxxxxxx",
            label_visibility="collapsed",
        )
        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input
        if st.session_state.api_key:
            st.markdown('<span class="success-msg">✅ API kaliti kiritilgan</span>', unsafe_allow_html=True)
        else:
            st.warning("API kaliti kiritilmagan", icon="⚠️")
        st.caption("[Groq API kaliti olish →](https://console.groq.com/keys)")

        st.markdown("---")
        st.markdown("**🤖 Model**")
        model_labels = {k: f"{v['icon']} {v['label']} — {v['desc']}" for k, v in MODELS.items()}
        selected_model = st.selectbox(
            "Model tanlang",
            options=list(MODELS.keys()),
            format_func=lambda x: model_labels[x],
            index=list(MODELS.keys()).index(st.session_state.model),
            label_visibility="collapsed",
        )
        st.session_state.model = selected_model

        st.markdown("---")
        st.markdown("**🌡️ Temperatura**")
        st.session_state.temperature = st.slider(
            "Temperatura", 0.0, 2.0, st.session_state.temperature, 0.1,
            help="Yuqori = ijodiy, past = aniqroq",
            label_visibility="collapsed",
        )

        st.markdown("**📏 Max tokenlar**")
        st.session_state.max_tokens = st.select_slider(
            "Max tokenlar",
            options=[256, 512, 1024, 2048, 4096, 8192],
            value=st.session_state.max_tokens,
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("**👤 Foydalanuvchi ismi**")
        st.session_state.user_name = st.text_input(
            "Ismingiz",
            value=st.session_state.user_name,
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("**📝 Tizim xabari**")
        st.session_state.system_prompt = st.text_area(
            "System prompt",
            value=st.session_state.system_prompt,
            height=100,
            label_visibility="collapsed",
        )

    # Eksport
    with st.expander("💾 Eksport", expanded=False):
        cid = st.session_state.current_conv_id
        if cid and cid in convs and convs[cid]["messages"]:
            title = convs[cid]["title"][:20]
            st.download_button(
                "⬇️ JSON yuklab olish",
                data=export_json(),
                file_name=f"somo-ai-{title}.json",
                mime="application/json",
                use_container_width=True,
            )
            st.download_button(
                "⬇️ Markdown yuklab olish",
                data=export_markdown(),
                file_name=f"somo-ai-{title}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.caption("Eksport uchun avval suhbat boshlang")

    # Hammasini o'chirish
    st.divider()
    if st.button("🗑️ Hammasini o'chirish", use_container_width=True):
        st.session_state.conversations = {}
        st.session_state.current_conv_id = None
        st.rerun()

# ─── ASOSIY KONTENT ───────────────────────────────────────────────────────────
cid = st.session_state.current_conv_id

# Agar suhbat tanlanmagan bo'lsa — Xush kelibsiz ekrani
if not cid or cid not in st.session_state.conversations:
    st.markdown(f"""
    <div style="text-align:center;padding:60px 20px 20px">
        <div style="font-size:64px;margin-bottom:12px">🤖</div>
        <div class="main-title">{greeting()}, {st.session_state.user_name}!</div>
        <p style="color:#8899bb;font-size:16px;margin-top:8px;margin-bottom:32px">
            Savolingizni yozing yoki quyidagi mavzulardan birini tanlang
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Taklif chiplar
    suggestions = [
        ("🤖", "Python da Telegram bot",     "Python da Telegram bot qanday yasaladi? Bosqichma-bosqich tushuntirib ber."),
        ("🗄️", "SQL va NoSQL farqi",           "SQL va NoSQL ma'lumotlar bazalari orasidagi asosiy farqlar nima?"),
        ("📄", "Resume yaxshilash",            "Mening resumemni yaxshilashga yordam ber."),
        ("🇬🇧", "Ingliz tilini o'rganish",     "Ingliz tilini tez o'rganish uchun samarali usullar qanday?"),
        ("⚛️", "React.js 30 kunlik reja",      "React.js ni o'rganish uchun 30 kunlik reja tuzib ber."),
        ("🧠", "Machine Learning asoslari",    "Machine Learning uchun Python kutubxonalari qaysilar?"),
    ]

    col1, col2 = st.columns(2)
    for i, (icon, title, prompt) in enumerate(suggestions):
        with (col1 if i % 2 == 0 else col2):
            if st.button(f"{icon} **{title}**", key=f"sug_{i}", use_container_width=True):
                cid = create_conversation(title)
                add_message("user", prompt)
                st.rerun()

    # Modeli ko'rsatish
    m = MODELS[st.session_state.model]
    st.markdown(f"""
    <div style="text-align:center;margin-top:24px;color:#4a5a7a;font-size:13px">
        {m['icon']} {m['label']} — {m['desc']}
        {'&nbsp;·&nbsp; 🟢 Tayyor' if st.session_state.api_key else '&nbsp;·&nbsp; ⚠️ API kaliti kerak'}
    </div>
    """, unsafe_allow_html=True)

else:
    # ─── CHAT EKRANI ──────────────────────────────────────────────────────────
    conv = st.session_state.conversations[cid]
    messages = conv["messages"]

    # Topbar
    m = MODELS[st.session_state.model]
    col_title, col_info = st.columns([3, 1])
    with col_title:
        st.markdown(f"### 💬 {conv['title']}")
    with col_info:
        st.markdown(f"""
        <div style="text-align:right;color:#4a5a7a;font-size:12px;padding-top:12px">
            {m['icon']} {m['label']}<br>
            <span style="color:#10b981">🟢 Online</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Xabarlarni ko'rsatish
    for msg in messages:
        role = msg["role"]
        with st.chat_message("user" if role == "user" else "assistant",
                             avatar="👤" if role == "user" else "🤖"):
            st.markdown(msg["content"])

    # Foydalanuvchi inputi
    user_input = st.chat_input(
        "Savolingizni yozing... (Shift+Enter yangi qator)",
        key="chat_input",
    )

    if user_input:
        if not st.session_state.api_key:
            st.error("⚠️ Iltimos, sidebar dagi **Sozlamalar** bo'limida Groq API kalitingizni kiriting.", icon="🔑")
        else:
            # Foydalanuvchi xabarini qo'sh
            add_message("user", user_input)
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)

            # AI javobi
            with st.chat_message("assistant", avatar="🤖"):
                msgs_for_api = [
                    {"role": m["role"], "content": m["content"]}
                    for m in messages + [{"role": "user", "content": user_input}]
                ]
                response_placeholder = st.empty()
                full_response = ""
                try:
                    for chunk in groq_stream(msgs_for_api):
                        full_response += chunk
                        response_placeholder.markdown(full_response + "▌")
                    response_placeholder.markdown(full_response)
                except Exception as e:
                    full_response = f"⚠️ Kutilmagan xato: {e}"
                    response_placeholder.markdown(full_response)

                add_message("assistant", full_response)

            st.rerun()

# ─── PASTKI FOOTER ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#2a3550;font-size:11px;padding-top:20px">
    Somo AI · Groq bilan ishlaydi · O'zbekistonda ishlab chiqilgan 🇺🇿
</div>
""", unsafe_allow_html=True)
