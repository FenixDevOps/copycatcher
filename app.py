from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
import docx
import PyPDF2
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.error(f"Failed to download NLTK data: {e}")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5500", "https://*.onrender.com"]}})
UPLOAD_FOLDER = 'Uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DATABASE = 'copy_catcher.db'

def init_db():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Drop existing tables to ensure fresh schema
        cursor.execute("DROP TABLE IF EXISTS UploadedFiles")
        cursor.execute("DROP TABLE IF EXISTS TextAnalysis")
        
        # Create UploadedFiles table with file_content column
        cursor.execute("""
            CREATE TABLE UploadedFiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_content TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create TextAnalysis table
        cursor.execute("""
            CREATE TABLE TextAnalysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_preview TEXT,
                similarity REAL,
                duplicates TEXT,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        logger.info("Database initialized successfully with correct schema")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        conn.close()

# Initialize database
init_db()

def extract_text(file):
    try:
        if file.filename.endswith('.docx'):
            doc = docx.Document(file)
            return "\n".join([para.text for para in doc.paragraphs])
        elif file.filename.endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            return "\n".join([reader.pages[i].extract_text() for i in range(len(reader.pages))])
        elif file.filename.endswith('.txt'):
            return file.read().decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to extract text from file {file.filename}: {e}")
        return None
    return None

def preprocess_text(text):
    try:
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
        stemmer = PorterStemmer()
        return " ".join([stemmer.stem(word) for word in tokens])
    except Exception as e:
        logger.error(f"Text preprocessing failed: {e}")
        return ""

def fetch_online_content(query):
    sample_corpus = [
        "Python is a high-level programming language designed to be easy to read and simple to implement.",
        "Artificial intelligence is the simulation of human intelligence processes by machines, especially computer systems.",
        "The history of artificial intelligence began in the 1950s with pioneers like Alan Turing.",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "The quick brown fox jumps over the lazy dog."
    ]
    return preprocess_text(" ".join(sample_corpus))

def analyze_text(input_text):
    try:
        processed_text = preprocess_text(input_text)
        if not processed_text:
            return {"similarity": 0, "message": "Text processing failed", "duplicates": []}
        online_content = fetch_online_content("sample query")
        
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([processed_text, online_content])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        plagiarism_percentage = similarity * 100
        
        message = "Content appears original." if plagiarism_percentage <= 20 else "Warning: Potential plagiarism detected!"
        duplicates = [{"phrase": input_text[:50], "source": "Simulated online database"}] if plagiarism_percentage > 20 else []
        
        return {
            "similarity": plagiarism_percentage,
            "message": message,
            "duplicates": duplicates
        }
    except Exception as e:
        logger.error(f"Text analysis failed: {e}")
        return {"similarity": 0, "message": f"Analysis error: {str(e)}", "duplicates": []}

@app.route('/upload-file', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files['file']
        file_content = extract_text(file)
        if file_content is None:
            return jsonify({"error": "Failed to extract text from file"}), 400
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        analysis_result = analyze_text(file_content)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO UploadedFiles (file_name, file_content) VALUES (?, ?)", 
                       (file.filename, file_content))
        cursor.execute("INSERT INTO TextAnalysis (text_preview, similarity, duplicates) VALUES (?, ?, ?)", 
                       (file_content[:100], analysis_result["similarity"], str(analysis_result["duplicates"])))
        conn.commit()
        conn.close()
        return jsonify({
            "status": "File processed successfully!",
            "file_name": file.filename,
            "similarity": f"{analysis_result['similarity']:.2f}%",
            "message": analysis_result["message"],
            "duplicates": analysis_result["duplicates"]
        })
    except Exception as e:
        logger.error(f"File upload endpoint error: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/upload-text', methods=['POST'])
def upload_text():
    try:
        data = request.json
        if 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
        input_text = data['text']
        if not input_text.strip():
            return jsonify({"error": "Text is empty"}), 400
        analysis_result = analyze_text(input_text)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO TextAnalysis (text_preview, similarity, duplicates) VALUES (?, ?, ?)", 
                       (input_text[:100], analysis_result["similarity"], str(analysis_result["duplicates"])))
        conn.commit()
        conn.close()
        return jsonify({
            "status": "Text processed successfully!",
            "text_preview": input_text[:100],
            "similarity": f"{analysis_result['similarity']:.2f}%",
            "message": analysis_result["message"],
            "duplicates": analysis_result["duplicates"]
        })
    except Exception as e:
        logger.error(f"Text upload endpoint error: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)))