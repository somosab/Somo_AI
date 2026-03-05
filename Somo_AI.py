import streamlit as st
from cerebras.cloud.sdk import Cerebras

st.set_page_config(
    page_title="Somo AI | Aqlli Yordamchi",
    page_icon="🤖",
    layout="centered"
)

with st.sidebar:
    st.image("https://img.freepik.com/free-vector/ai-technology-brain-background_53876-90611.jpg")
    st.title("Somo AI Sozlamalari")
    st.info("Bu Somo AI yordamchisi. Cerebras llama-3.3-70b modeli asosida ishlaydi.")

    model = st.selectbox("Model tanlang:", [
        "llama-3.3-70b",
        "llama3.1-8b",
    ])

    if st.button("Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 Somo AI")
st.caption("🚀 Tezkor va aqlli sun'iy intellekt yordamchisi")

# API kalit Streamlit Secrets dan
try:
    client = Cerebras(api_key=st.secrets["CEREBRAS_API_KEY"])
except Exception:
    st.error("❌ CEREBRAS_API_KEY topilmadi. Streamlit Secrets ga qo'shing.")
    st.code('[secrets]\nCEREBRAS_API_KEY = "csk-xxxxxxxxxxxx"', language="toml")
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
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                max_tokens=1024,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_response += delta
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            err = str(e)
            if "rate_limit" in err.lower():
                full_response = "⏳ So'rovlar juda ko'p. Bir daqiqa kuting."
            elif "model" in err.lower():
                full_response = f"❌ Model topilmadi: `{model}`."
            elif "auth" in err.lower() or "api_key" in err.lower():
                full_response = "❌ API kalit noto'g'ri. CEREBRAS_API_KEY ni tekshiring."
            else:
                full_response = f"❌ Xatolik: {err}"
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
