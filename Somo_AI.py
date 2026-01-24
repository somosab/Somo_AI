import streamlit as st
from groq import Groq

# 1. Sahifa sozlamalari va Dizayn
st.set_page_config(
    page_title="Somo AI | Aqlli Yordamchi",
    page_icon="🤖",
    layout="centered"
)

# Sidebar (Yon panel) dizayni
with st.sidebar:
    # Rasm linkini yangiladim, sidebar chiroyliroq chiqadi
    st.image("https://img.freepik.com/free-vector/ai-technology-brain-background_53876-90611.jpg")
    st.title("Somo AI Sozlamalari")
    st.info("Bu Somo AI yordamchisi. U eng so'nggi Llama-3.3 modeli asosida ishlaydi.")
    if st.button("Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

# Asosiy sarlavha
st.title("🤖 Somo AI")
st.caption("🚀 Tezkor va aqlli sun'iy intellekt yordamchisi")

# 2. Xavfsizlik: API Kalitni Streamlit Secrets'dan olish
# Secrets bo'limida GROQ_API_KEY borligiga ishonch hosil qiling
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API kalit topilmadi! Streamlit Secrets sozlamalarini tekshiring.")
    st.stop()

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
        
        try:
            # Model nomini eng barqaroriga o'zgartirdim: llama-3.3-70b-versatile
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
            st.info("Maslahat: Model nomi yoki API limitini tekshiring.")
