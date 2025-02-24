# Lecture Notes Organizer

A web application that helps students organize and search through their lecture notes using OCR technology.

## Features

- Upload and process images of lecture notes
- Convert images to searchable text using Tesseract OCR
- Tag notes for better organization
- Search through notes by content or tags
- Modern and responsive UI

## Prerequisites

- Python 3.7+
- Tesseract OCR installed on your system
- pip (Python package manager)

## Installation

1. Install Tesseract OCR:
   - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - Make sure to add Tesseract to your system PATH

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Upload Notes**
   - Click the file input to select an image of your lecture notes
   - Add relevant tags (comma-separated)
   - Click "Upload and Process"

2. **Search Notes**
   - Use the search bar to search through the text content of your notes
   - Use the tag search to filter by specific tags
   - Results will show matching notes with previews

## Tech Stack

- Backend: Python Flask
- OCR: Tesseract
- Frontend: HTML, CSS (Tailwind CSS)
- Database: SQLite with SQLAlchemy
