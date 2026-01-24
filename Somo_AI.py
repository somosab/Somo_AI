import streamlit as st
from groq import Groq

# --- SAHIFA KONFIGURATSIYASI ---
st.set_page_config(page_title="Somo AI (Groq)", page_icon="⚡", layout="centered")

# --- STIL (DIZAYN) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stChatMessage { border-radius: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Somo AI Web-Dasturi")
st.caption("Groq LPU texnologiyasi asosida ishlovchi eng tezkor SI")

# --- API ULANISH ---
# Siz bergan kalitni shu yerga joyladim
client = Groq(api_key="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")

# --- CHAT TARIXI ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Salom! Men Somo AI-man. Sizga qanday yordam bera olaman?"}
    ]

# Tarixni chiqarish
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ASOSIY MANTIQ ---
if prompt := st.chat_input("Savolingizni yozing..."):
    # Foydalanuvchi xabari
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Groq API orqali javob olish
    with st.chat_message("assistant"):
        try:
            # Llama 3 - 70B modeli juda aqlli va o'zbek tilini yaxshi tushunadi
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sizning ismingiz Somo AI. Foydalanuvchilarga o'zbek tilida, do'stona va aniq javob berasiz."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                stream=False
            )
            
            response_text = completion.choices[0].message.content
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            st.error(f"Xatolik yuz berdi: {e}")
