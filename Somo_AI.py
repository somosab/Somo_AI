import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from PIL import Image
import base64
import io

# 1. Sahifa sozlamalari
st.set_page_config(page_title="Somo AI | Universal Analyst", page_icon="🚀", layout="wide")

# API Sozlamalari
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar - Yuklash markazi
with st.sidebar:
    st.image("https://files.catbox.moe/97i5s7.png", use_container_width=True)
    st.title("Somo AI Markazi")
    st.markdown("---")
    
    st.subheader("➕ Fayl yoki Rasm qo'shish")
    uploaded_file = st.file_uploader("PDF, TXT yoki Rasm (PNG, JPG)", type=["pdf", "txt", "png", "jpg", "jpeg"])
    
    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

# Rasm va fayl tahlili funksiyalari
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def get_pdf_text(file):
    text = ""
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Asosiy interfeys
st.markdown("<h2 style='text-align: center;'>🚀 Somo AI Universal Analyst</h2>", unsafe_allow_html=True)

# Yuklangan faylni qayta ishlash
file_content = ""
image_data = None

if uploaded_file:
    if uploaded_file.type in ["image/png", "image/jpeg"]:
        image_data = encode_image(uploaded_file)
        st.sidebar.image(uploaded_file, caption="Yuklangan rasm", use_container_width=True)
    elif uploaded_file.type == "application/pdf":
        file_content = get_pdf_text(uploaded_file)
        st.sidebar.success("PDF o'qildi!")
    else:
        file_content = str(uploaded_file.read(), "utf-8")
        st.sidebar.success("Matn yuklandi!")

# Chat tarixi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat interfeysi
if prompt := st.chat_input("Savolingizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Modelni tanlash: Agar rasm bo'lsa Vision model, bo'lmasa oddiy
        current_model = "llama-3.2-11b-vision-preview" if image_data else "llama-3.3-70b-versatile"
        
        messages_to_send = [
            {"role": "system", "content": "Sen Somo AI yordamchisisan. O'zbek tilida javob berasan."}
        ]
        
        # Agar fayl mazmuni bo'lsa, context sifatida qo'shish
        if file_content:
            messages_to_send.append({"role": "user", "content": f"Fayl mazmuni: {file_content[:5000]}"})
        
        # Agar rasm bo'lsa, uni yuborish
        if image_data:
            messages_to_send.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            })
        else:
            for m in st.session_state.messages:
                messages_to_send.append({"role": m["role"], "content": m["content"]})

        try:
            completion = client.chat.completions.create(
                model=current_model,
                messages=messages_to_send,
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
