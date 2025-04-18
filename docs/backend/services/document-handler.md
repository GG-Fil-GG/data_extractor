# Document Handler

## Overview

The Document Handler is a core service responsible for managing document uploads to OpenAI's API. It handles the secure and efficient transfer of documents to OpenAI's infrastructure, where they can be processed by AI models. The service includes robust error handling and retry mechanisms to ensure reliable file processing.

## Responsibilities

- Managing file uploads to OpenAI's API
- Validating file sizes and PDF page counts
- Tracking upload status and progress
- Implementing retry mechanisms for failed uploads
- Handling file cleanup after processing
- Managing document metadata and OpenAI file references

## Class Structure

The `DocumentHandler` class is defined in `backend/app/services/document_handler.py` and works closely with the Job Manager to process documents as part of the extraction workflow.

### Initialization

```python
def __init__(self, job_manager, openai_client):
    self.job_manager = job_manager
    self.openai_client = openai_client
    self.max_retries = 3
    self.retry_delay = 5  # seconds
    self.max_total_size = 32 * 1024 * 1024  # 32MB in bytes
    self.max_total_pages = 100  # Only applies to PDFs
```

The Document Handler is initialized with:
- A reference to the Job Manager for job data and status updates
- An OpenAI client for file operations
- Configuration for retry attempts and delays
- File size and page count limits

## Key Methods

### validate_documents()

Validates all documents collectively before upload:
- Total size limit (32MB) applies to all file types
- Page count limit (100) only applies to PDF files

```python
def validate_documents(self):
    total_size = 0
    total_pdf_pages = 0
    
    for document in self.job_manager.job_data["documents"]:
        # Check file size for all files
        file_size = os.path.getsize(document["path"])
        total_size += file_size
        
        # Only count pages for PDF files
        if document["format"].lower() == "pdf":
            try:
                page_count = self.get_pdf_page_count(document)
                total_pdf_pages += page_count
            except ValueError as ve:
                raise ve
    
    # Validate total size
    if total_size > self.max_total_size:
        raise ValueError(f"Total file size {total_size/1024/1024:.2f}MB exceeds maximum of 32MB")
    
    # Validate PDF pages
    if total_pdf_pages > self.max_total_pages:
        raise ValueError(f"Total PDF pages {total_pdf_pages} exceeds maximum of 100 pages")
    
    return total_size, total_pdf_pages
```

### process_documents()

Processes all documents in the current job by uploading them to OpenAI and tracking their status.

```python
def process_documents(self):
    self.job_manager.update_status("uploading_files")
    
    try:
        # Validate all documents collectively
        total_size, total_pdf_pages = self.validate_documents()
        
        # Update job data with total counts
        self.job_manager.job_data["state"]["file_uploads"].update({
            "total_size": total_size,
            "total_pdf_pages": total_pdf_pages
        })
        
    except ValueError as ve:
        logging.error(f"Document validation failed: {ve}")
        self.job_manager.update_status("upload_failed")
        return
    
    for document in self.job_manager.job_data["documents"]:
        try:
            # Initialize OpenAI file info
            document["openai_file"] = {
                "file_id": None,
                "purpose": "assistants",
                "status": "pending",
                "error": None,
                "upload_time": None,
                "retry_count": 0
            }
            
            # Upload file to OpenAI
            self.upload_file_to_openai(document)
            
            # Update job state
            self.job_manager.update_file_upload_progress()
            
        except Exception as e:
            logging.error(f"Failed to process document {document['name']}: {e}")
            document["openai_file"]["status"] = "error"
            document["openai_file"]["error"] = str(e)
            self.job_manager.add_failed_file(document["id"])
    
    # Check if all files were uploaded successfully
    if self.job_manager.job_data["state"]["file_uploads"]["failed_files"]:
        self.job_manager.update_status("upload_failed")
    else:
        self.job_manager.update_status("upload_complete")
```

This method:
1. Updates the job status to indicate file uploads are in progress
2. Validates all documents collectively
3. Updates job state with total size and PDF page counts
4. Iterates through each document in the job
5. Initializes OpenAI file metadata
6. Uploads the file to OpenAI with retry mechanism
7. Updates the job state with upload progress
8. Handles any upload failures
9. Updates the final job status based on upload success

### upload_file_to_openai()

Handles the actual file upload to OpenAI with retry mechanism.

```python
def upload_file_to_openai(self, document):
    retry_count = 0
    while retry_count < self.max_retries:
        try:
            # Upload file to OpenAI
            with open(document["path"], "rb") as file:
                response = self.openai_client.files.create(
                    file=file,
                    purpose="assistants"
                )
            
            # Update document with OpenAI file info
            document["openai_file"].update({
                "file_id": response.id,
                "status": "uploaded",
                "upload_time": response.created_at,
                "retry_count": retry_count
            })
            
            return
            
        except Exception as e:
            retry_count += 1
            document["openai_file"]["retry_count"] = retry_count
            
            if retry_count == self.max_retries:
                raise Exception(f"Failed to upload file after {self.max_retries} attempts: {e}")
            
            logging.warning(f"Retry {retry_count} for file {document['name']}: {e}")
            time.sleep(self.retry_delay)
```

This method:
1. Attempts to upload the file to OpenAI
2. Implements a retry mechanism with configurable attempts and delays
3. Updates document metadata with upload status and file ID
4. Handles and logs upload failures

### cleanup_files()

Manages the cleanup of uploaded files from OpenAI after processing is complete.

```python
def cleanup_files(self):
    for document in self.job_manager.job_data["documents"]:
        if document["openai_file"]["file_id"]:
            try:
                self.openai_client.files.delete(file_id=document["openai_file"]["file_id"])
                document["openai_file"]["status"] = "deleted"
            except Exception as e:
                logging.error(f"Failed to delete file {document['name']} from OpenAI: {e}")
                document["openai_file"]["error"] = str(e)
```

This method:
1. Iterates through all processed documents
2. Deletes uploaded files from OpenAI
3. Updates document status
4. Handles and logs any deletion failures

## Error Handling

The Document Handler uses a decorator pattern for error handling:

```python
def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper
```

This decorator:
1. Wraps each method to catch exceptions
2. Logs the error with the method name and error message
3. Re-raises the exception for higher-level handling

## Integration with Other Services

The Document Handler integrates with:

- **Job Manager**: Receives job data and updates job status
- **OpenAI API**: Handles file uploads and management
- **Data Extractor**: Provides access to uploaded files for processing
- **Token Counter**: Indirectly supports token counting through OpenAI's processing

## File Status Tracking

The Document Handler maintains detailed status information for each file:

| Status | Description |
|--------|-------------|
| pending | Initial state before upload |
| uploaded | Successfully uploaded to OpenAI |
| error | Failed to upload after retries |
| deleted | Successfully removed from OpenAI |

## File Validation Rules

The Document Handler enforces the following validation rules:

1. **Total Size Limit**:
   - Applies to all file types
   - Maximum total size: 32MB
   - Includes all files in the job

2. **Page Count Limit**:
   - Only applies to PDF files
   - Maximum total pages: 100
   - Non-PDF files are not counted towards this limit

## Performance Considerations

- Network latency can affect upload times
- Large files may require more retry attempts
- Rate limits should be considered for bulk uploads
- Proper cleanup is essential to manage OpenAI storage usage

## Example Flow

1. User uploads documents through the frontend
2. Backend receives the documents and creates a job
3. Document Handler processes each document:
   - Validates total size and PDF page counts
   - Initializes OpenAI file metadata
   - Uploads file to OpenAI with retry mechanism
   - Tracks upload status and progress
4. The uploaded files are available for subsequent processing steps
5. Files are cleaned up after processing is complete 