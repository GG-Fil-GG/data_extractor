# Job Manager

## Overview

The Job Manager is a core service that maintains the state and data for extraction jobs. It serves as the central data store for the extraction process, tracking documents, queries, responses, and job status. All other components interact with the Job Manager to access and update job information.

## Responsibilities

- Creating and managing job IDs
- Initializing temporary directories for job files
- Storing document and query information
- Tracking extraction responses
- Maintaining job status
- Tracking file upload progress and failures
- Cleaning up temporary files when jobs are complete

## Class Structure

The `JobManager` class is defined in `backend/app/services/job_manager.py` and serves as the central data repository for the extraction process.

### Initialization

```python
def __init__(self):
    self.job_data = {
        "Job ID": str(uuid.uuid4()),
        "Temp Dir": "",
        "Documents": [],
        "Queries": [],
        "Responses": {},
        "Status": "Initialized",
        "Export Format": "",
        "Orientation": "",
        "state": {
            "file_uploads": {
                "total_files": 0,
                "uploaded_files": 0,
                "failed_files": [],
                "status": "pending"
            }
        }
    }
```

The Job Manager initializes with a job data dictionary containing:
- A unique job ID (UUID)
- An empty temporary directory path
- Empty lists for documents and queries
- An empty dictionary for responses
- Initial status of "Initialized"
- Empty export format and orientation (to be set later)
- File upload state tracking

## Key Methods

### initialize_temp_dir()

Creates a temporary directory for the job files.

```python
def initialize_temp_dir(self):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "../.."))
    temp_root_dir = os.path.join(root_dir, "temp")
    os.makedirs(temp_root_dir, exist_ok=True)
    temp_job_dir = os.path.join(temp_root_dir, f"{self.job_data['Job ID']}")
    os.makedirs(temp_job_dir, exist_ok=True)
    self.job_data["Temp Dir"] = temp_job_dir
    logging.info(f"Temporary directory created: {temp_job_dir}")
```

This method:
1. Finds the root directory of the application
2. Creates a root temporary directory if it doesn't exist
3. Creates a job-specific temporary directory using the job ID
4. Updates the job data with the temporary directory path

### update_status()

Updates the job status.

```python
def update_status(self, new_status):
    self.job_data["Status"] = new_status
    logging.info(f"Job status updated to: {new_status}")
```

### update_file_upload_progress()

Updates the file upload progress in the job state.

```python
def update_file_upload_progress(self):
    state = self.job_data["state"]["file_uploads"]
    state["uploaded_files"] = sum(
        1 for doc in self.job_data["Documents"]
        if doc.get("openai_file", {}).get("status") == "uploaded"
    )
    state["total_files"] = len(self.job_data["Documents"])
    state["status"] = "complete" if state["uploaded_files"] == state["total_files"] else "in_progress"
    logging.info(f"File upload progress: {state['uploaded_files']}/{state['total_files']}")
```

This method:
1. Gets the current file upload state
2. Counts successfully uploaded files
3. Updates total files count
4. Updates overall upload status
5. Logs the current progress

### add_failed_file()

Adds a file ID to the list of failed uploads.

```python
def add_failed_file(self, file_id):
    if file_id not in self.job_data["state"]["file_uploads"]["failed_files"]:
        self.job_data["state"]["file_uploads"]["failed_files"].append(file_id)
        logging.error(f"Added failed file to tracking: {file_id}")
```

This method:
1. Checks if the file ID is already in the failed files list
2. Adds the file ID to the list if not present
3. Logs the failure

### get_file_upload_status()

Returns the current file upload status.

```python
def get_file_upload_status(self):
    return self.job_data["state"]["file_uploads"]
```

This method returns a dictionary containing:
- total_files: Total number of files to upload
- uploaded_files: Number of successfully uploaded files
- failed_files: List of file IDs that failed to upload
- status: Overall upload status (pending/in_progress/complete)

### get_job_data()

Returns the current job data.

```python
def get_job_data(self):
    return self.job_data
```

### finalize_extraction()

Cleans up temporary files after the extraction is complete.

```python
def finalize_extraction(self):
    temp_dir = self.job_data.get("Temp Dir")
    logging.info(f"Attempting to delete temporary directory: {temp_dir}")
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            logging.info(f"Temporary directory {temp_dir} deleted successfully.")
        except Exception as e:
            logging.error(f"Error while deleting temporary directory {temp_dir}: {e}")
        finally:
            temp_root_dir = os.path.dirname(temp_dir)
            if not os.listdir(temp_root_dir):
                try:
                    os.rmdir(temp_root_dir)
                    logging.info(f"Root directory {temp_root_dir} deleted successfully.")
                except Exception as e:
                    logging.error(f"Error while deleting root directory {temp_root_dir}: {e}")
        self.update_status("Data Extraction Complete")
        logging.info("Temporary directory cleanup completed.")
```

This method:
1. Gets the temporary directory path from the job data
2. Deletes the job-specific temporary directory
3. Checks if the root temporary directory is empty and deletes it if so
4. Updates the job status to "Data Extraction Complete"
5. Handles errors during the cleanup process

## Error Handling

The Job Manager uses a decorator pattern for error handling:

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
1. Wraps methods to catch exceptions
2. Logs the error with the method name and error message
3. Re-raises the exception for higher-level handling

## Job Data Structure

The job data is a dictionary with the following structure:

```json
{
  "Job ID": "unique-uuid-string",
  "Temp Dir": "/path/to/temp/directory",
  "Documents": [
    {
      "Alias": "Document Name",
      "Path": "/path/to/document.txt",
      "Ext": "pdf",
      "openai_file": {
        "file_id": "openai-file-id",
        "purpose": "assistants",
        "status": "uploaded",
        "error": null,
        "upload_time": "2024-03-20T12:00:00Z",
        "retry_count": 0
      }
    }
  ],
  "Queries": [
    {
      "Alias": "Query Name",
      "Text": "What is the main conclusion?",
      "Format": "free-form"
    }
  ],
  "Responses": {
    "Document Name": {
      "Query Name": "Response text..."
    }
  },
  "Status": "Current Status",
  "Export Format": "csv or docx",
  "Orientation": "doc_row or query_row",
  "state": {
    "file_uploads": {
      "total_files": 5,
      "uploaded_files": 4,
      "failed_files": ["file-id-1"],
      "status": "in_progress"
    }
  }
}
```

## Job Status Flow

The Job Manager tracks the following status transitions:

1. **Initialized**: Initial job state
2. **uploading_files**: Files are being uploaded to OpenAI
3. **upload_complete**: All files successfully uploaded
4. **upload_failed**: One or more files failed to upload
5. **Queries Processed, Responses Collected**: Extraction complete
6. **CSV/DOCX Output Generated**: Output file created
7. **Data Extraction Complete**: Job finalized and cleaned up

## Integration with Other Services

The Job Manager integrates with all other components:

- **Document Handler**: Stores document information and tracks upload status
- **Query Manager**: Stores query information
- **Data Extractor**: Coordinates the extraction process
- **LLM Interface**: Indirectly through the Data Extractor
- **Output Generator**: Generates output files based on job data

## Temporary File Management

The Job Manager creates a directory structure for temporary files:

```
backend/
└── temp/
    └── {job_id}/
        ├── document1.txt
        ├── document2.txt
        └── {job_id}.{format}
```

Where:
- `{job_id}` is the UUID for the job
- `document*.txt` are the processed document text files
- `{job_id}.{format}` is the output file (CSV or DOCX)

## Example Flow

1. Job Manager is created with a new job ID
2. Temporary directory is initialized
3. Documents and queries are added to the job data
4. Document Handler uploads files to OpenAI and updates status
5. Job Manager tracks upload progress and failures
6. Data Extractor collects responses and updates the job data
7. Output Generator creates the output file
8. Job Manager finalizes the extraction and cleans up

## Performance Considerations

- Job data is stored in memory during the extraction process
- Temporary files are created for document text and output
- Cleanup is performed after the download is complete
- Each job has a unique ID and temporary directory
- File upload status is tracked in memory for real-time updates 