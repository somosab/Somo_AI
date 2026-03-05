import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Somo AI | Aqlli Yordamchi",
    page_icon="🤖",
    layout="centered"
)

with st.sidebar:
    st.image("https://img.freepik.com/free-vector/ai-technology-brain-background_53876-90611.jpg")
    st.title("Somo AI Sozlamalari")
    st.info("Bu Somo AI yordamchisi. U Groq Llama-3 modeli asosida ishlaydi.")

    model = st.selectbox("Model tanlang:", [
        "llama-3.3-70b-versatile",
        "llama3-8b-8192",
        "llama3-70b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ])

    if st.button("Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 Somo AI")
st.caption("🚀 Tezkor va aqlli sun'iy intellekt yordamchisi")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("❌ GROQ_API_KEY topilmadi. Streamlit Secrets ga qo'shing.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Savolingizni bu yerga yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                max_tokens=1024,
            )

            for chunk in completion:
                delta = chunk.choices[0].delta.content or ""
                full_response += delta
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            err = str(e)
            if "rate_limit" in err.lower():
                full_response = "⏳ So'rovlar juda ko'p. Bir daqiqa kuting."
            elif "model" in err.lower():
                full_response = f"❌ Model topilmadi: `{model}`. Boshqa model tanlang."
            elif "auth" in err.lower() or "api_key" in err.lower():
                full_response = "❌ API kalit noto'g'ri. GROQ_API_KEY ni tekshiring."
            else:
                full_response = f"❌ Xatolik: {err}"
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
