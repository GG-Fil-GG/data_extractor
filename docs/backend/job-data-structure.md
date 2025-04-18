# Job Data Structure

## Overview

The `job_data` object is the central data structure that maintains the state and configuration of each extraction job. It is managed by the JobManager service and is used throughout the application to coordinate the extraction process.

## Structure

```json
{
    "job_id": "string (UUID)",
    "created_at": "string (ISO datetime)",
    "temp_dir": "string (path)",
    "status": "string (status code)",
    "system_message": "string",
    "documents": [
        {
            "id": "string (UUID)",
            "name": "string (filename)",
            "path": "string (path, optional after upload)",
            "format": "string (PDF|DOCX|TXT)",
            "size": "integer (bytes)",
            "openai_file": {
                "file_id": "string",
                "purpose": "string",
                "status": "string",
                "error": "string",
                "upload_time": "string (ISO datetime)",
                "retry_count": "integer"
            }
        }
    ],
    "threads": [
        {
            "id": "string (UUID)",
            "title": "string",
            "status": "string",
            "messages": [],
            "queries": [
                {
                    "id": "string (UUID)",
                    "title": "string",
                    "text": "string",
                    "format": "string (format_type)"
                }
            ]
        }
    ],
    "responses": {
        "document_id": {
            "thread_id": {
                "query_id": "string (response)"
            }
        }
    },
    "openai_config": {
        "model": "string",
        "assistant_id": "string",
        "max_tokens": "integer",
        "temperature": "number (default: 0.0)",
        "file_purpose": "string"
    },
    "export": {
        "format": "string (CSV|DOCX)",
        "orientation": "string (documents_in_rows|documents_in_columns)"
    },
    "state": {
        "is_paused": "boolean",
        "active_operations": {
            "document_id": {
                "status": "string (processing|complete)",
                "active_threads": {
                    "thread_id": {
                        "status": "string (processing|complete)",
                        "current_query_id": "string (UUID|null)",
                        "completed_queries": ["string (UUID)"]
                    }
                }
            }
        },
        "file_uploads": {
            "total_files": "integer",
            "uploaded_files": "integer",
            "failed_files": ["string (document_id)"],
            "status": "string",
            "total_size": "integer",
            "total_pdf_pages": "integer",
            "validation_status": "string"
        },
        "progress": {
            "total_operations": "integer (documents × total queries)",
            "completed_operations": "integer",
            "current_document": "string (document_id|null)",
            "current_thread": "string (thread_id|null)",
            "current_query": "string (query_id|null)",
            "completed_documents": ["string (UUID)"]
        }
    }
}
```

## Field Descriptions

### Core Fields

- **job_id**: Unique identifier for the extraction job
- **created_at**: ISO datetime string indicating when the job was created
- **temp_dir**: Path to temporary directory for job files
- **status**: Current status of the job. Valid values:
  - "initialized": Job created, ready to begin processing
  - "uploading_files": Files are being uploaded to OpenAI
  - "upload_complete": All files successfully uploaded
  - "upload_failed": One or more file uploads failed
  - "processing_threads": Threads are being processed
  - "threads_complete": All threads processed successfully
  - "threads_failed": One or more threads failed
  - "completed": Job finalized and cleaned up
- **system_message**: Global developer message used to guide LLM behavior across all interactions in this job (max length: 32,768 characters)

### Documents Array

Each document object contains:
- **id**: Unique identifier for the document
- **name**: Original filename
- **path**: Path to the document in the temporary directory
- **format**: File format of the document
- **size**: Size of the document in bytes
- **openai_file**: OpenAI file information

### Threads Array

Each thread object contains:
- **id**: Unique identifier for the thread
- **title**: Display title for the thread
- **status**: Current status of the thread
- **messages**: Array of conversation messages
- **queries**: Array of query objects belonging to this thread

### Responses Object

Organized hierarchically by:
1. document_id (primary organization for efficient output generation)
2. thread_id (maintains thread context)
3. query_id (preserves query sequence within threads)

This structure optimizes response organization for output generation while maintaining thread context and query relationships.

### Query Objects

Each query object within a thread contains:
- **id**: Unique identifier for the query
- **title**: Display title for the query
- **text**: The actual query text
- **format**: Response format specification

### OpenAI Configuration

- **model**: OpenAI model to use
- **assistant_id**: OpenAI assistant ID
- **max_tokens**: Maximum tokens for responses
- **temperature**: Temperature setting for responses
- **file_purpose**: Purpose for uploaded files

### Export Configuration

- **format**: Desired output format (CSV|DOCX)
- **orientation**: How data should be organized in the output (documents_in_rows|documents_in_columns)

### State Object

Tracks the current state of the extraction process:

#### File Uploads State
- **total_files**: Total number of files to upload
- **uploaded_files**: Number of successfully uploaded files
- **failed_files**: List of failed file IDs
- **status**: Current upload status
- **total_size**: Total size of all files in bytes
- **total_pdf_pages**: Total pages across all PDF files
- **validation_status**: Status of document validation

#### Threads State
- **total_threads**: Total number of threads
- **completed_threads**: Number of completed threads
- **failed_threads**: List of failed thread IDs
- **status**: Current thread processing status

#### Progress State
- **total_operations**: Total number of operations (documents × total queries)
- **completed_operations**: Number of completed operations
- **current_document**: Current document being processed
- **current_thread**: Current thread being processed
- **current_query**: Current query being processed
- **completed_documents**: List of completed document IDs

### State Management Notes

1. **Document Validation**:
   - Occurs during document upload
   - Size and page count limits are checked immediately
   - Validation errors are shown to user at upload time
   - Status tracked in `state.file_uploads.validation_status`

2. **Processing Order**:
   - Documents can be processed in parallel
   - Multiple threads within a document can be processed simultaneously
   - Queries within a single thread must be processed sequentially to maintain conversation context

3. **Progress Tracking**:
   - Total operations = number of documents × total number of queries across all threads
   - Each query processed for each document counts as one operation
   - Current document, thread, and query are tracked for UI feedback
   - Progress shown as completed operations / total operations

4. **Pause/Resume Behavior**:
   - Pausing sets `is_paused` to true
   - Processing completes current query before stopping
   - State structure preserves exact position for resuming
   - Can resume from any partially completed state

## State Transitions

1. **File Upload Phase**:
   - Initialized → uploading_files → upload_complete/upload_failed

2. **Thread Processing Phase**:
   - upload_complete → processing_threads → threads_complete/threads_failed

3. **Completion**:
   - threads_complete → completed

## Usage Examples

### Creating a New Thread
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Analysis Thread",
    "status": "initialized",
    "messages": [],
    "queries": []
}
```

### Adding a Query to a Thread
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Main Conclusion",
    "text": "What is the main conclusion of the document?",
    "format": "free_form"
}
```