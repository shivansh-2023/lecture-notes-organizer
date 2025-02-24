import os
from flask import Flask, request, render_template, jsonify
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://your-connection-string')
client = MongoClient(MONGODB_URI)
db = client.lecture_notes
notes_collection = db.notes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Get text content and tags from the request
        text_content = request.form.get('text_content', '')
        tags = request.form.get('tags', '')
        title = request.form.get('title', 'Untitled Note')

        # Save to MongoDB
        note = {
            'title': title,
            'text_content': text_content,
            'tags': tags.split(',') if tags else [],
            'upload_date': datetime.utcnow()
        }
        
        result = notes_collection.insert_one(note)
        
        return jsonify({
            'success': True,
            'message': 'Note saved successfully',
            'id': str(result.inserted_id)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['GET'])
def search():
    try:
        query = request.args.get('query', '').lower()
        tag = request.args.get('tag', '').lower()
        
        # Build the MongoDB query
        search_query = {}
        
        if query:
            search_query['$or'] = [
                {'text_content': {'$regex': query, '$options': 'i'}},
                {'title': {'$regex': query, '$options': 'i'}}
            ]
        
        if tag:
            search_query['tags'] = {'$regex': tag, '$options': 'i'}
        
        # Get notes from MongoDB
        notes = notes_collection.find(
            search_query,
            {'text_content': 1, 'title': 1, 'tags': 1, 'upload_date': 1}
        ).sort('upload_date', -1)
        
        results = [{
            'title': note.get('title', 'Untitled'),
            'upload_date': note['upload_date'].strftime('%Y-%m-%d %H:%M:%S'),
            'tags': note.get('tags', []),
            'text_preview': note['text_content'][:200] + '...' if len(note['text_content']) > 200 else note['text_content']
        } for note in notes]
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# For Vercel deployment
app = app
