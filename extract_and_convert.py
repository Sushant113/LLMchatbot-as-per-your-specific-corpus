import pdfplumber
import json

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def convert_text_to_json(text):
    lines = text.split('\n')
    qa_pairs = []
    for i in range(0, len(lines), 2):
        question = lines[i].strip()
        answer = lines[i+1].strip() if (i+1) < len(lines) else ""
        qa_pairs.append({"question": question, "answer": answer})
    return {"questions": qa_pairs}

# Extract text from the PDF corpus file
corpus_pdf_path = "your path to/Corpus.pdf"
corpus_text = extract_text_from_pdf(corpus_pdf_path)

# Convert the extracted text to JSON
corpus_json = convert_text_to_json(corpus_text)

# Save JSON to file
with open('Corpus.json', 'w') as f:
    json.dump(corpus_json, f, indent=4)
