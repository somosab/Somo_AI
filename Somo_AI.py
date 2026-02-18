import streamlit as st
import gspread
import hashlib
import mammoth
import base64
import time
import json
import io
import os
import csv
import re
import pandas as pd
from pypdf import PdfReader
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# 1. SAHIFA SOZLAMALARI (MUKAMMAL DIZAYN)
st.set_page_config(
    page_title="Somo AI | Professional Pro",
    page_icon="📑",
    layout="wide"
)

# 2. AVTOMATLASHTIRILGAN HUJJAT YARATISH FUNKSIYALARI
class DocumentGenerator:
    @staticmethod
    def create_docx(content, filename="hujjat.docx"):
        doc = Document()
        doc.add_heading('Somo AI Professional Hisoboti', 0)
        doc.add_paragraph(content)
        buffer = io.BytesIO()
        doc.save(buffer)
        return buffer.getvalue()

    @staticmethod
    def create_pptx(content):
        prs = Presentation()
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        title.text = "Somo AI Taqdimoti"
        subtitle.text = "Avtomatik generatsiya qilingan tahlil"
        
        # Mazmunni qismlarga bo'lib slaydga joylash
        lines = content.split('\n')[:10]
        for line in lines:
            if line.strip():
                bullet_slide_layout = prs.slide_layouts[1]
                s = prs.slides.add_slide(bullet_slide_layout)
                s.shapes.title.text = "Tahliliy nuqta"
                s.placeholders[1].text = line
        
        buffer = io.BytesIO()
        prs.save(buffer)
        return buffer.getvalue()

    @staticmethod
    def create_excel(text_data):
        # Matndagi jadval ma'lumotlarini qidirish va Excelga o'tkazish
        rows = []
        for line in text_data.split('\n'):
            if '|' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if parts: rows.append(parts)
        
        df = pd.DataFrame(rows)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
        return buffer.getvalue()

# 3. AI BILAN ISHLASH (FAQAT MATN VA ANALITIKA)
def get_ai_response(messages, model="llama-3.3-70b-versatile"):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
            stream=True
        )
        return completion
    except Exception as e:
        st.error(f"Xato yuz berdi: {e}")
        return None

# 4. ASOSIY INTERFEYS
def main():
    # CSS dizayn (Rasm generatsiyasiz, toza va biznes uslubida)
    st.markdown("""
    <style>
    .main-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background: #0f172a;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("📑 Somo AI: Professional Intelligence")
    
    # Sidebar - Sozlamalar
    with st.sidebar:
        st.header("⚙️ Boshqaruv")
        mode = st.selectbox("Ish tartibi", ["Universal Chat", "Hujjat Analizi", "Hisobot Tayyorlash"])
        if st.button("Tarixni tozalash"):
            st.session_state.messages = []
            st.rerun()

    # Chat qismi
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Savolingizni yoki topshirig'ingizni yozing..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            # AI dan javob olish
            stream = get_ai_response(st.session_state.messages)
            if stream:
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
                
                # AVTOMATIK FAYL YARATISH TUGMALARI
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    docx_file = DocumentGenerator.create_docx(full_response)
                    st.download_button("📥 Word formatda yuklash", docx_file, "javob.docx")
                
                with col2:
                    pptx_file = DocumentGenerator.create_pptx(full_response)
                    st.download_button("📊 PPTX (Slayd) yuklash", pptx_file, "taqdimot.pptx")
                
                with col3:
                    if "|" in full_response: # Agar jadval bo'lsa
                        xls_file = DocumentGenerator.create_excel(full_response)
                        st.download_button("📈 Excelda yuklash", xls_file, "maʼlumotlar.xlsx")

                st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
