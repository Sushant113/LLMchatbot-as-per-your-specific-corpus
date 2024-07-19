import os
import json
import time
import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from transformers import pipeline
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Set environment variable to avoid TensorFlow warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Initialize FastAPI app
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# Initialize QA pipeline
qa_pipeline = None
try:
    qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error initializing the pipeline: {e}")

# Initialize SQLite database
conn = sqlite3.connect('chat_history.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS history (user_input TEXT, bot_response TEXT)''')
conn.commit()

# Load corpus from JSON file
corpus_path = 'Corpus.json'
corpus = {}
try:
    with open(corpus_path, 'r') as f:
        corpus = json.load(f)
except Exception as e:
    print(f"Error loading corpus: {e}")

# Function to find the best match in the corpus
def find_best_match(question):
    for q in corpus.get('questions', []):
        if q['question'].lower() in question.lower():
            return q['answer']
    return None

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    question = data.get('question', '')
    start_time = time.time()

    # Search for the answer in the corpus
    answer = find_best_match(question)
    
    # If no match is found, use the QA model
    if not answer and qa_pipeline:
        context = " ".join([q['question'] + " " + q['answer'] for q in corpus.get('questions', [])])
        try:
            result = qa_pipeline(question=question, context=context)
            answer = result['answer'] if result['score'] > 0.5 else "I'm sorry, I don't have information about that, Please contact the business directly for more information."
        except Exception as e:
            print(f"Error using the QA model: {e}")
            answer = "I'm sorry, I don't have information about that,Please contact the business directly for more information."
    elif not answer:
        answer = "I'm sorry, I don't have information about that, Please contact the business directly for more information."

    # Save to history
    try:
        c.execute("INSERT INTO history (user_input, bot_response) VALUES (?, ?)", (question, answer))
        conn.commit()
    except Exception as e:
        print(f"Error saving to history: {e}")

    latency = time.time() - start_time
    return JSONResponse({"answer": answer, "latency": latency})

# Run with `uvicorn filename:app --reload` (replace `filename` with the actual filename)
