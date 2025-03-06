# Backend Documentation

## Overview

The backend of DataExtractor is built with Flask and provides the API endpoints that power the application's core functionality. It handles document processing, AI-powered data extraction, and result formatting.

## Architecture

The backend follows a modular architecture with the following key components:

1. **Flask Application** - The main web server that handles HTTP requests
2. **Route Handlers** - API endpoints that process frontend requests
3. **Document Handler** - Processes different document types (PDF, DOCX, TXT)
4. **Query Manager** - Manages extraction queries and their formats
5. **Data Extractor** - Core extraction logic that processes documents with queries
6. **LLM Interface** - Communicates with AI models for data extraction
7. **Job Manager** - Manages extraction jobs and their lifecycle
8. **Output Generator** - Creates formatted output files (CSV, DOCX)
9. **Token Counter** - Counts tokens in documents to ensure they're within limits
10. **Parsers** - Formats and validates responses based on query format requirements
11. **Cleanup** - Handles temporary file cleanup and resource management

## API Endpoints

The backend exposes the following REST API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/count_tokens` | POST | Upload a document and get token count |
| `/begin_extraction` | POST | Start the extraction process |
| `/download_results` | GET | Get download URL for results |

## Core Services

### Document Handler

Responsible for:
- Extracting text from different file formats (PDF, DOCX, TXT)
- Preprocessing text for optimal extraction
- Managing document metadata

### Query Manager

Responsible for:
- Validating query formats
- Preparing queries for the AI model
- Formatting query responses according to specified formats

### Data Extractor

Responsible for:
- Coordinating the extraction process
- Processing documents with queries
- Collecting and organizing extraction results

### LLM Interface

Responsible for:
- Communicating with AI language models
- Optimizing prompts for accurate extraction
- Managing token usage and rate limits

### Job Manager

Responsible for:
- Creating and tracking extraction jobs
- Managing temporary files and directories
- Cleaning up resources after job completion

### Output Generator

Responsible for:
- Creating CSV or DOCX output files
- Formatting data according to the selected orientation
- Generating download links for completed jobs

### Parsers

Responsible for:
- Defining response format requirements for different query types
- Validating and formatting AI model responses
- Converting raw responses to structured data formats

### Cleanup

Responsible for:
- Periodically removing old temporary files
- Managing disk space usage
- Ensuring the system remains stable during long-term operation

## Data Flow

1. Frontend uploads documents to the backend
2. Backend processes documents to extract text
3. Frontend sends extraction request with queries and settings
4. Backend creates an extraction job
5. Documents and queries are processed by the AI model
6. Results are formatted according to user preferences
7. Output file is generated and made available for download
8. Frontend retrieves the download link

## File Structure

backend/
├── app/
│ ├── init.py # Flask application initialization
│ ├── routes.py # API endpoint definitions
│ ├── cleanup.py # Temporary file cleanup utilities
│ ├── services/
│ │ ├── document_handler.py # Document processing logic
│ │ ├── query_manager.py # Query processing logic
│ │ ├── data_extractor.py # Core extraction logic
│ │ ├── llm_interface.py # AI model integration
│ │ ├── job_manager.py # Job management
│ │ ├── output_generator.py # Result formatting
│ │ ├── token_counter.py # Token counting utility
│ │ └── parsers.py # Response format parsers
├── run.py # Application entry point
└── requirements.txt # Python dependencies

## Error Handling

The backend implements comprehensive error handling:
- Input validation for all API requests
- Proper HTTP status codes for different error types
- Detailed error messages for debugging
- Graceful handling of AI model failures

## Security Considerations

- File validation to prevent malicious uploads
- Temporary file cleanup to prevent storage issues
- Rate limiting to prevent abuse
- Input sanitization to prevent injection attacks

## Performance Optimization

- Asynchronous job processing for long-running extractions
- Efficient text extraction from large documents
- Optimized AI model prompts to reduce token usage
- Caching of intermediate results where appropriate

## Environment Configuration

The backend requires an OpenAI API key to function properly. This is configured through:

- A `.env` file in the root directory containing the `OPENAI_API_KEY` variable
- The application reads this key at runtime to authenticate with OpenAI's services

Example `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

If the API key is not found, the application will raise an error when attempting to process extraction requests.
