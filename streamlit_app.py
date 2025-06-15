import streamlit as st
from PyPDF2 import PdfReader
import os
import google.generativeai as genai

# Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Title
st.set_page_config(page_title="Flashcard Generator", layout="centered")

# CSS Styling (converted from your style1.css)
st.markdown("""
    <style>
    * {
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        position: relative;
        overflow: hidden;
    }
    h1 {
        color: #333;
        font-size: 2.5rem;
        text-shadow: 1px 1px 2px #fff;
        margin-bottom: 30px;
    }
    .upload-box {
        background: rgb(236, 236, 236);
        padding: 30px 40px;
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    .upload-box:hover {
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
    }
    .background-overlay {
        background-image: url("https://cdn-icons-png.flaticon.com/512/3909/3909444.png");
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-size: cover;
        background-position: center;
        opacity: 0.05;
        z-index: 0;
    }
    </style>
    <div class="background-overlay"></div>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>Flashcard Generator</h1>", unsafe_allow_html=True)

# File uploader section
with st.container():
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file:
        with st.spinner("Reading PDF..."):
            reader = PdfReader(uploaded_file)
            raw_text = ''
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    raw_text += content + "\n\n"

        if st.button("Generate Flashcards"):
            with st.spinner("Generating flashcards with Gemini..."):
                system_prompt = (
                    "Take in the following notes. For each key word or key phrase, "
                    "write the key phrase first, then the '|' delimiter, then the definition. "
                    "Avoid using '|' within definitions or key phrases. "
                    "Make as many flashcards as possible to cover all content."
                )
                prompt = system_prompt + "\n\n" + raw_text
                response = model.generate_content(prompt)
                flashcards_text = response.text
                flashcards = {}
                for line in flashcards_text.split("\n"):
                    if "|" in line:
                        term, definition = line.split("|", 1)
                        flashcards[term.strip()] = definition.strip()

            st.success("Flashcards created successfully!")
            st.subheader("📚 Flashcards")

            for idx, (term, definition) in enumerate(flashcards.items(), 1):
                with st.expander(f"{idx}. {term}"):
                    st.markdown(f"<p style='font-size:16px;'>{definition}</p>", unsafe_allow_html=True)

