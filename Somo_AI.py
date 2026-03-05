import streamlit as st
import google.generativeai as genai

st.set_page_config(
    page_title="Somo AI | Aqlli Yordamchi",
    page_icon="🤖",
    layout="centered"
)

with st.sidebar:
    st.image("https://img.freepik.com/free-vector/ai-technology-brain-background_53876-90611.jpg")
    st.title("Somo AI Sozlamalari")
    st.info("Gemini AI modeli asosida ishlaydi.")

    model_name = st.selectbox("Model tanlang:", [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ])

    if st.button("Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 Somo AI")
st.caption("🚀 Tezkor va aqlli sun'iy intellekt yordamchisi")

# API kalit
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("❌ GEMINI_API_KEY topilmadi. Streamlit Secrets ga qo'shing.")
    st.code('[secrets]\nGEMINI_API_KEY = "AIza-xxxxxxxxxxxx"', language="toml")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Xabarlarni ko'rsatish
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
            # Gemini chat tarixi formatiga o'tkazish
            history = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})

            model = genai.GenerativeModel(model_name)
            chat = model.start_chat(history=history)

            # Streaming javob
            response = chat.send_message(prompt, stream=True)

            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            err = str(e)
            if "quota" in err.lower() or "rate" in err.lower():
                full_response = "⏳ So'rovlar limiti tugadi. Bir daqiqa kuting."
            elif "api_key" in err.lower() or "auth" in err.lower():
                full_response = "❌ API kalit noto'g'ri. GEMINI_API_KEY ni tekshiring."
            elif "model" in err.lower():
                full_response = f"❌ Model topilmadi: `{model_name}`. Boshqasini tanlang."
            else:
                full_response = f"❌ Xatolik: {err}"
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
