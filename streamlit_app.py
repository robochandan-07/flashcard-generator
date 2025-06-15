import os
import streamlit as st
from PyPDF2 import PdfReader
import keys
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=keys.api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# PDF Text Extraction
def extract_text_from_pdf(pdf_file):
    text = ''
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n\n"
    return text

# Create Flashcards
def create_flashcards(notes):
    system_prompt = (
        "Take in the following notes. For each key word or key phrase, "
        "write the key phrase first, then the '|' delimiter, then the definition. "
        "Avoid using '|' within definitions or key phrases. "
        "Make as many flashcards as possible to cover all content."
    )
    prompt = system_prompt + "\n\n" + notes
    response = model.generate_content(prompt)
    flashcards_t = response.text

    flashcards = flashcards_t.split("\n")
    cards_dict = {}
    for card in flashcards:
        if "|" in card:
            parts = card.split("|", 1)
            cards_dict[parts[0].strip()] = parts[1].strip()
    return cards_dict

# Streamlit UI
st.title("📄 PDF to Flashcard Generator")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    with st.spinner("Reading PDF..."):
        text = extract_text_from_pdf(uploaded_file)
    
    if st.button("Generate Flashcards"):
        with st.spinner("Generating flashcards using Gemini..."):
            flashcards = create_flashcards(text)
        st.success("Flashcards Generated!")
        
        st.subheader("🧠 Flashcards")
        for i, (key, definition) in enumerate(flashcards.items(), 1):
            with st.expander(f"{i}. {key}"):
                st.write(definition)
