import os
import sys
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Set Tesseract CMD path - update this path according to your installation
if os.name == 'nt':  # for Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    text_content = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

def init_db():
    with app.app_context():
        db.create_all()

# Check Tesseract installation
def check_tesseract():
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception as e:
        print(f"Tesseract not properly installed: {str(e)}")
        return False

@app.route('/')
def index():
    if not check_tesseract():
        return render_template('index.html', error="Tesseract OCR is not installed. Please install it first.")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    tags = request.form.get('tags', '')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            # Save the file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            saved_filename = timestamp + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
            file.save(filepath)

            # Perform OCR
            try:
                image = Image.open(filepath)
                text_content = pytesseract.image_to_string(image)
                
                # Save to database
                note = Note(
                    filename=saved_filename,
                    original_filename=filename,
                    text_content=text_content,
                    tags=tags
                )
                db.session.add(note)
                db.session.commit()

                return jsonify({
                    'success': True,
                    'message': 'File uploaded and processed successfully',
                    'text': text_content
                })
            except Exception as e:
                # Clean up the file if OCR fails
                os.remove(filepath)
                return jsonify({'error': f'OCR processing failed: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'error': f'File upload failed: {str(e)}'}), 500

@app.route('/search', methods=['GET'])
def search():
    try:
        query = request.args.get('query', '').lower()
        tag = request.args.get('tag', '').lower()
        
        # Build the query
        notes_query = Note.query
        
        if query:
            notes_query = notes_query.filter(
                db.or_(
                    Note.text_content.ilike(f'%{query}%'),
                    Note.original_filename.ilike(f'%{query}%')
                )
            )
        
        if tag:
            notes_query = notes_query.filter(Note.tags.ilike(f'%{tag}%'))
        
        notes = notes_query.order_by(Note.upload_date.desc()).all()
        
        results = [{
            'filename': note.original_filename,
            'upload_date': note.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
            'tags': note.tags,
            'text_preview': note.text_content[:200] + '...' if len(note.text_content) > 200 else note.text_content
        } for note in notes]
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
