# API Routes Documentation

## Overview

The backend exposes several REST API endpoints that allow the frontend to interact with the core functionality of the application. These endpoints handle document uploads, extraction requests, and result downloads.

## Base URL

All API routes are relative to the base URL of the backend server, which is typically:
- Development: `http://localhost:5001`
- Production: Depends on deployment configuration

## Authentication

Currently, the API does not require authentication as it's designed to be used by the frontend application directly. The backend validates incoming requests to ensure they contain the required data and file types, but does not implement rate limiting.

The only constraint is a token limit check in the `/count_tokens` endpoint, which rejects files exceeding 120,000 tokens.

## API Endpoints

### 1. Count Tokens

**Endpoint:** `/count_tokens`  
**Method:** POST  
**Purpose:** Upload a document and get its token count

#### Request

The request should be a `multipart/form-data` request with the following field:

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | The document file to be processed (PDF, DOCX, or TXT) |

Example using Axios:
```javascript
const formData = new FormData();
formData.append('file', file);
axios.post('/count_tokens', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

#### Response

A successful response returns a JSON object with the following structure:

```json
{
  "file_path": "/tmp/document.txt"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | String | Temporary path where the file is stored on the server |

#### Error Responses

| Status Code | Description | Response Body |
|-------------|-------------|--------------|
| 400 | Token Limit Exceeded | `{"error": "File exceeds token limit"}` |
| 400 | Bad Request (no file provided) | `{"error": "No file provided"}` |
| 500 | Server Error | `{"error": "Error message details"}` |

### 2. Begin Extraction

**Endpoint:** `/begin_extraction`  
**Method:** POST  
**Purpose:** Start the extraction process with documents, queries, and export settings

#### Request

The request should be a `multipart/form-data` request with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `documents` | JSON String | Array of document metadata objects |
| `queries` | JSON String | Array of query objects |
| `export_format` | String | Format for the output file (`csv` or `docx`) |
| `orientation` | String | Data orientation in the output (`doc_row` or `query_row`) |

Document metadata object structure:
```json
{
  "Alias": "Document 1",
  "Ext": "pdf",
  "Path": "/tmp/document.txt"
}
```

Query object structure:
```json
{
  "Alias": "Query 1",
  "Text": "What is the main conclusion?",
  "Format": "free-form"
}
```

Example using Axios:
```javascript
const formData = new FormData();
formData.append('documents', JSON.stringify(documentsMetadata));
formData.append('queries', JSON.stringify(queries));
formData.append('export_format', 'csv');
formData.append('orientation', 'doc_row');
axios.post('/begin_extraction', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

#### Response

A successful response returns a JSON object with the job ID:

```json
{
  "job_id": "job_123456789"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | String | Unique identifier for the extraction job (UUID format) |

#### Error Responses

| Status Code | Description | Response Body |
|-------------|-------------|--------------|
| 400 | Bad Request (missing required fields) | `{"error": "Missing required field: documents"}` |
| 500 | Server Error | `{"error": "Error message details"}` |

### 3. Download Results

**Endpoint:** `/download_results`  
**Method:** GET  
**Purpose:** Get the download URL for a completed extraction job

#### Request

The request should include the job ID as a query parameter:

| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | String | The ID of the extraction job |

Example using Axios:
```javascript
axios.get('/download_results', {
  params: { job_id: 'job_123456789' }
});
```

#### Response

A successful response returns a JSON object with the download URL:

```json
{
  "downloadUrl": "http://localhost:5001/get_file/job_123456789"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `downloadUrl` | String | Full URL to download the results file |

#### Error Responses

| Status Code | Description | Response Body |
|-------------|-------------|--------------|
| 400 | Bad Request (missing job ID) | `{"error": "No job ID provided"}` |
| 404 | Job Not Found | `{"error": "Results file not found"}` |
| 500 | Server Error | `{"error": "Error message details"}` |

### 4. Get File

**Endpoint:** `/get_file/<job_id>`  
**Method:** GET  
**Purpose:** Download the actual results file

#### Request

The job ID is included in the URL path:

Example using a browser or direct download:
```
http://localhost:5001/get_file/job_123456789
```

#### Response

A successful response returns the file as an attachment with the appropriate content type. The file will be named `{job_id}.{format}` where format is either `csv` or `docx` depending on the export format selected.

#### Error Responses

| Status Code | Description | Response Body |
|-------------|-------------|--------------|
| 404 | Job Not Found | "Results file not found" |
| 404 | File Not Found | "Results file not found" |

## Request and Response Formats

### Document Upload

When uploading documents, the frontend creates a FormData object, appends the file to it, and sends it to the backend using a POST request.

### Extraction Request

When initiating extraction, the frontend:
1. Creates a FormData object
2. Appends document metadata as JSON
3. Appends queries as JSON
4. Adds export format and orientation settings
5. Sends the complete package to the backend

### Response Handling

All API responses follow a consistent format:
- Successful responses return a JSON object with the requested data
- Error responses return a JSON object with an `error` field containing the error message
- Appropriate HTTP status codes are used to indicate the type of error

## Error Handling

The API implements comprehensive error handling:
- Input validation for all requests
- Proper HTTP status codes for different error types
- Detailed error messages for debugging
- Graceful handling of server-side errors

## Additional Notes

- The backend cleans up temporary files after the download is complete
- The job is removed from the job store once the download is complete
- The token limit for documents is set to 120,000 tokens
- Job IDs are generated as UUIDs
- Temporary files are stored in a directory structure: `backend/temp/{job_id}/`
- The output generator supports two orientations:
  - `doc_row`: Documents as rows, queries as columns
  - `query_row`: Queries as rows, documents as columns 