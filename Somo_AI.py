import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import base64

# 1. Sahifa sozlamalari
st.set_page_config(page_title="Somo AI | Universal Analyst", page_icon="🚀", layout="wide")

# API Sozlamalari
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar - Dizayn va Yuklash
with st.sidebar:
    # Logotip joylashuvi
    st.image("https://files.catbox.moe/o3f3b9.png", use_container_width=True)
    st.title("Somo AI Markazi")
    st.info("Yaratuvchi: **Usmonov Sodiq**")
    st.markdown("---")
    
    # "+" belgisi bilan yuklash bo'limi
    st.subheader("➕ Fayl yoki Rasm qo'shish")
    uploaded_file = st.file_uploader("PDF, TXT yoki Rasm yuklang", 
                                     type=["pdf", "txt", "png", "jpg", "jpeg"],
                                     label_visibility="collapsed")
    
    if st.button("🗑 Chatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Funksiyalar
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def get_pdf_text(file):
    text = ""
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Asosiy sarlavha
st.markdown("<h1 style='text-align: center;'>🚀 Somo AI Universal Analyst</h1>", unsafe_allow_html=True)

# Yuklangan faylni tahlil qilish
file_content = ""
image_base64 = None

if uploaded_file:
    if uploaded_file.type in ["image/png", "image/jpeg"]:
        img_bytes = uploaded_file.getvalue()
        image_base64 = encode_image(img_bytes)
        st.sidebar.image(uploaded_file, caption="Yuklangan rasm", use_container_width=True)
    elif uploaded_file.type == "application/pdf":
        file_content = get_pdf_text(uploaded_file)
        st.sidebar.success("PDF tayyor ✅")
    else:
        file_content = uploaded_file.read().decode("utf-8")
        st.sidebar.success("Matn yuklandi ✅")

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
        
        # TIZIM KO'RSATMASI - USMONOV SODIQ
        sys_prompt = "Sen Somo AI yordamchisisan. Sen Usmonov Sodiq tomonidan yaratilgansan. Agar yaratuvching haqida so'rashsa, 'Meni Usmonov Sodiq yaratgan' deb javob ber. O'zbek tilida javob ber."
        
        # MODEL TANLASH (Hozirda ishlaydigan Vision modeli)
        model_to_use = "llama-3.2-90b-vision-preview" if image_base64 else "llama-3.3-70b-versatile"
        
        if image_base64:
            messages_payload = [
                {"role": "system", "content": sys_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ]
        else:
            messages_payload = [{"role": "system", "content": sys_prompt}]
            if file_content:
                messages_payload.append({"role": "user", "content": f"Fayl mazmuni: {file_content[:5000]}"})
            for m in st.session_state.messages:
                messages_payload.append({"role": m["role"], "content": m["content"]})

        try:
            completion = client.chat.completions.create(
                model=model_to_use,
                messages=messages_payload,
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
