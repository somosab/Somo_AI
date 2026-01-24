import streamlit as st
from groq import Groq

# 1. Sahifa sozlamalari va chiroyli dizayn
st.set_page_config(
    page_title="Somo AI | Professional",
    page_icon="🤖",
    layout="centered"
)

# Sidebar (Yon panel) - Yangi Logo bilan
with st.sidebar:
    # Sizga yoqqan yangi Somo_AI logotipi
    st.image("https://files.catbox.moe/97i5s7.png", use_container_width=True)
    st.title("Somo AI Sozlamalari")
    st.markdown("---")
    st.info("Somo AI — bu Llama 3.3 modeli asosida ishlaydigan aqlli yordamchi.")
    
    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

# Asosiy sarlavha qismi
st.title("🤖 Somo AI")
st.caption("🚀 Tezyurar va aqlli sun'iy intellekt")

# 2. Xavfsizlik: API Kalitni Streamlit Secrets'dan olish
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API kalit sozlamalarida xatolik bor!")
    st.stop()

# 3. Chat tarixini saqlash
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tarixdagi xabarlarni ekranga chiqarish
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Foydalanuvchi xabari va AI javobi
if prompt := st.chat_input("Savolingizni yozing..."):
    # Foydalanuvchi xabarini qo'shish
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI javobini generatsiya qilish
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Eng yangi Llama-3.3-70b modeli
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen foydali yordamchisan va har doim O'zbek tilida javob berasan."},
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
            st.error(f"Xatolik yuz berdi: {str(e)}")
