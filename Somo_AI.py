import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import base64

# 1. Sahifa sozlamalari
st.set_page_config(page_title="Somo AI | Universal Analyst", page_icon="🚀", layout="wide")

# API Sozlamalari
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Somo AI, created by Usmonov Sodiq. How can I help you with math or any other tasks today?"}
    ]

# Sidebar - Yuklash
with st.sidebar:
    st.image("https://files.catbox.moe/o3f3b9.png", use_container_width=True)
    st.title("Somo AI Center")
    st.info("Creator: **Usmonov Sodiq**")
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload PDF, TXT or Image", type=["pdf", "txt", "png", "jpg", "jpeg"])
    
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Chat cleared."}]
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

# Asosiy interfeys
st.markdown("<h1 style='text-align: center;'>🚀 Somo AI Universal Analyst</h1>", unsafe_allow_html=True)

# Yuklangan fayl ishlovi
file_content = ""
image_base64 = None
if uploaded_file:
    if uploaded_file.type in ["image/png", "image/jpeg"]:
        image_base64 = encode_image(uploaded_file.getvalue())
        st.sidebar.image(uploaded_file)
    elif uploaded_file.type == "application/pdf":
        file_content = get_pdf_text(uploaded_file)
    else:
        file_content = uploaded_file.read().decode("utf-8")

# Chat tarixi (LaTeX qo'llab-quvvatlaydi)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat interfeysi
if prompt := st.chat_input("Type your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # MATEMATIKA VA TIL UCHUN MAXSUS SYSTEM PROMPT
        sys_prompt = (
            "You are Somo AI, created by Usmonov Sodiq. "
            "IMPORTANT: Always use LaTeX for mathematical formulas. "
            "For example, use $2^2$ for powers, $\\frac{a}{b}$ for fractions. "
            "Enclose math in dollar signs: $...$ for inline or $$...$$ for blocks. "
            "Respond in the language the user speaks. Default is English."
        )
        
        model_name = "llama-3.2-90b-vision-preview" if image_base64 else "llama-3.3-70b-versatile"
        
        # Xabarlarni tayyorlash
        messages_payload = [{"role": "system", "content": sys_prompt}]
        if file_content:
            messages_payload.append({"role": "user", "content": f"Context: {file_content[:5000]}"})
        
        if image_base64:
            messages_payload.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            })
        else:
            for m in st.session_state.messages:
                messages_payload.append({"role": m["role"], "content": m["content"]})

        try:
            completion = client.chat.completions.create(
                model=model_name,
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
            st.error(f"Error: {str(e)}")
