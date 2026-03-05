import streamlit as st
from groq import Groq

# 1. Sahifa sozlamalari
st.set_page_config(
    page_title="Somo AI | Aqlli Yordamchi",
    page_icon="🤖",
    layout="centered"
)

# Sidebar
with st.sidebar:
    st.image("https://img.freepik.com/free-vector/ai-technology-brain-background_53876-90611.jpg")
    st.title("Somo AI Sozlamalari")
    st.info("Bu Somo AI yordamchisi. U Groq Llama-3 modeli asosida ishlaydi.")
    if st.button("Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

# Asosiy sarlavha
st.title("🤖 Somo AI")
st.caption("🚀 Tezkor va aqlli sun'iy intellekt yordamchisi")

# 2. API kalitni Streamlit Secrets'dan olish
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. Chat tarixini boshqarish
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tarixdagi xabarlarni ko'rsatish
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Foydalanuvchi kirishi va AI javobi
if prompt := st.chat_input("Savolingizni bu yerga yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )

        for chunk in completion:
            full_response += (chunk.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
