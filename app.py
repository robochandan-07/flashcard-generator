import os
from flask import Flask, request, render_template, send_from_directory, session, redirect
from PyPDF2 import PdfReader
from flask_session import Session
import keys
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=keys.api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_text_from_pdf(pdf_file):
    text = ''
    with open(pdf_file, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n\n"
    return text

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

    # Save flashcards to a text file
    with open("flashcards.txt", "w", encoding='utf-8') as f:
        f.write(flashcards_t)

    flashcards = flashcards_t.split("\n")
    cards_dict = {}
    for card in flashcards:
        if "|" in card:
            parts = card.split("|", 1)
            cards_dict[parts[0].strip()] = parts[1].strip()

    return cards_dict


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            text = extract_text_from_pdf(file_path)
            flashcards = create_flashcards(text)
            session["flashcards"] = flashcards
            return redirect("/flashcards")

    return render_template('uploads.html', text=None)


@app.route('/flashcards')
def display_flashcards():
    flashcards = session.get("flashcards", None)
    return render_template('flashcards.html', flashcards=flashcards)


if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    app.run(debug=True)
