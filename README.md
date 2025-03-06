# DataExtractor.com

## Overview

DataExtractor is a web application that extracts structured data from documents using AI. The application allows users to:

1. Upload multiple document files (PDF, DOCX, TXT)
2. Define custom queries to extract specific information
3. Process documents with AI to answer these queries
4. Export results in various formats (CSV, DOCX)

## Project Structure

The project consists of a Vue.js frontend and a Flask backend:

### Frontend (`/frontend`)
- Built with Vue.js 3 and Vuex for state management
- Components for document upload, query definition, and export options
- Communicates with the backend via REST API

### Backend (`/backend`)
- Built with Flask
- Handles document processing, AI extraction, and result formatting
- Core services:
  - Document handling (text extraction from PDFs, DOCX, TXT)
  - AI-powered data extraction
  - Job management and tracking
  - Output generation in multiple formats

## Setup and Installation

### Backend Setup
1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```
   python run.py
   ```
   The server will start on http://localhost:5001

### Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run serve
   ```
   The frontend will be available at http://localhost:8080

4. Build for production:
   ```
   npm run build
   ```

## How It Works

1. Users upload documents through the frontend interface
2. Users define custom queries to extract specific information
3. When extraction begins, documents are processed to extract text
4. Each query is run against each document using AI models
5. Results are collected and formatted according to user preferences
6. The final output is made available for download in CSV or DOCX format

## Key Features

- **Multiple Document Support**: Process several documents at once
- **Custom Queries**: Define specific questions to extract targeted information
- **Format Options**: Specify the expected format of responses (free-form, integer, date, etc.)
- **Flexible Export**: Choose between different export formats and orientations
- **Document Aliasing**: Assign friendly names to documents for easier identification

## Development

- The backend uses a temporary directory for file processing
- Automatic cleanup runs periodically to remove old files
- Error handling is implemented throughout the application
- The frontend uses Vuex for state management
- API communication is handled through Axios

## Deployment

For production deployment:
1. Build the frontend (`npm run build` in the frontend directory)
2. Configure the backend to serve the built frontend files
3. Set up a production WSGI server (like Gunicorn) for the Flask application
4. Consider using a reverse proxy (like Nginx) in front of the application
