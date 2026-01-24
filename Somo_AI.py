import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

# 1. Sahifa sozlamalari
st.set_page_config(page_title="Somo AI | File Analyst", page_icon="📂", layout="centered")

# Sidebar dizayni
with st.sidebar:
    st.image("https://files.catbox.moe/97i5s7.png", use_container_width=True)
    st.title("Somo AI Sozlamalari")
    st.markdown("---")
    
    # Fayl yuklash bo'limi
    uploaded_file = st.file_uploader("Fayl tahlili (PDF yoki TXT)", type=["pdf", "txt"])
    
    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

# Fayldan matnni ajratib olish funksiyasi
def get_file_text(file):
    text = ""
    if file.type == "application/pdf":
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    elif file.type == "text/plain":
        text = str(file.read(), "utf-8")
    return text

# API Sozlamalari
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sarlavha
st.markdown("<h1 style='text-align: center;'>📂 Somo AI File Analyst</h1>", unsafe_allow_html=True)

# Yuklangan fayl haqida ma'lumot
file_context = ""
if uploaded_file:
    with st.spinner("Fayl o'qilmoqda..."):
        file_context = get_file_text(uploaded_file)
        st.success(f"Fayl yuklandi: {uploaded_file.name}")

# Chat tarixi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat interfeysi
if prompt := st.chat_input("Fayl bo'yicha savol bering..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Tizimga fayl mazmunini tushuntirish
        system_msg = "Sen Somo AI yordamchisisan. O'zbek tilida javob ber."
        if file_context:
            system_msg += f"\nMana bu fayl mazmuni asosida javob ber: {file_context[:5000]}" # Limit uchun 5000 belgi

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_msg},
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
