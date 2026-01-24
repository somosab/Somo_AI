import streamlit as st
from groq import Groq

# 1. Sahifa sozlamalari
st.set_page_config(
    page_title="Somo AI | Professional",
    page_icon="🤖",
    layout="centered"
)

# Sidebar dizayni
with st.sidebar:
    # Siz tanlagan oq-qora logo (image_318039.png asosida)
    st.image("https://files.catbox.moe/o3f3b9.png", use_container_width=True)
    st.title("Somo AI Sozlamalari")
    st.markdown("---")
    st.info("Somo AI — bu Llama 3.3 modeli asosida ishlaydigan aqlli yordamchi.")
    
    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

# Markaziy sarlavha
st.markdown("<h1 style='text-align: center;'>🤖 Somo AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>Tezyurar va aqlli sun'iy intellekt</p>", unsafe_allow_html=True)

# 2. Xavfsizlik: API Kalit
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API kalit sozlamalarida xatolik bor!")
    st.stop()

# 3. Chat xotirasi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Xabarlarni ko'rsatish
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Chat interfeysi
if prompt := st.chat_input("Savolingizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen Somo AI yordamchisisan. Doim o'zbek tilida, aqlli va xushmuomala javob berasan."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                stream=True,
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Xatolik: {str(e)}")
