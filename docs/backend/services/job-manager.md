# Job Manager

## Overview

The Job Manager is a core service that maintains the state and data for extraction jobs. It serves as the central data store for the extraction process, managing threads, documents, queries, and job status. All other components interact with the Job Manager to access and update job information.

## Responsibilities

- Creating and managing job IDs and threads
- Initializing temporary directories for job files
- Managing OpenAI configuration
- Tracking thread and query status
- Maintaining job status and progress
- Tracking file upload progress and failures
- Cleaning up temporary files when jobs are complete

## Class Structure

The `JobManager` class is defined in `backend/app/services/job_manager.py` and serves as the central data repository for the extraction process.

### Initialization

```python
def __init__(self):
    self.job_data = {
        "job_id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat(),
        "status": "initialized",
        "temp_dir": "",
        "documents": [],
        "threads": [],
        "openai_config": {
            "model": "gpt-4o",
            "assistant_id": "",
            "max_tokens": 128000,
            "temperature": 0.0,
            "file_purpose": "assistants"
        },
        "state": {
            "file_uploads": {
                "total_files": 0,
                "uploaded_files": 0,
                "failed_files": [],
                "status": "pending",
                "total_size": 0,
                "total_pdf_pages": 0,
                "validation_status": "pending"
            },
            "threads": {
                "total_threads": 0,
                "completed_threads": 0,
                "failed_threads": [],
                "status": "pending"
            }
        }
    }
```

The Job Manager initializes with a job data dictionary containing:
- A unique job ID (UUID) and creation timestamp
- An empty temporary directory path
- Empty lists for documents and threads
- OpenAI configuration with default values
- File upload state tracking
- Thread state tracking

## Key Methods

### Thread Management

#### create_thread()

Creates a new thread in the job data.

```python
def create_thread(self, title: str) -> Dict:
    thread = {
        "id": str(uuid.uuid4()),
        "title": title,
        "status": "initialized",
        "created_at": datetime.now().isoformat(),
        "messages": [],
        "queries": []
    }
    self.job_data["threads"].append(thread)
    self.job_data["state"]["threads"]["total_threads"] += 1
    return thread
```

This method:
1. Creates a new thread with a unique ID
2. Sets initial status and timestamp
3. Initializes empty message and query lists
4. Updates thread state tracking

#### get_thread()

Retrieves a thread by its ID.

```python
def get_thread(self, thread_id: str) -> Optional[Dict]:
    return next(
        (thread for thread in self.job_data["threads"] if thread["id"] == thread_id),
        None
    )
```

#### update_thread_status()

Updates the status of a thread and overall thread state.

```python
def update_thread_status(self, thread_id: str, new_status: str) -> None:
    thread = self.get_thread(thread_id)
    if thread:
        thread["status"] = new_status
        if new_status == "completed":
            self.job_data["state"]["threads"]["completed_threads"] += 1
        elif new_status == "failed":
            self.job_data["state"]["threads"]["failed_threads"].append(thread_id)
        
        # Update overall thread state
        state = self.job_data["state"]["threads"]
        if state["completed_threads"] == state["total_threads"]:
            state["status"] = "complete"
        elif state["failed_threads"]:
            state["status"] = "failed"
        else:
            state["status"] = "in_progress"
```

### OpenAI Configuration

#### get_openai_config()

Retrieves the current OpenAI configuration.

```python
def get_openai_config(self) -> Dict:
    return self.job_data["openai_config"]
```

#### update_openai_config()

Updates the OpenAI configuration.

```python
def update_openai_config(self, config: Dict) -> None:
    self.job_data["openai_config"].update(config)
```

### File Management

#### initialize_temp_dir()

Creates a temporary directory for the job files.

```python
def initialize_temp_dir(self) -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "../.."))
    temp_root_dir = os.path.join(root_dir, "temp")
    os.makedirs(temp_root_dir, exist_ok=True)
    temp_job_dir = os.path.join(temp_root_dir, self.job_data["job_id"])
    os.makedirs(temp_job_dir, exist_ok=True)
    self.job_data["temp_dir"] = temp_job_dir
```

#### update_file_upload_progress()

Updates the file upload progress in the job state.

```python
def update_file_upload_progress(self) -> None:
    state = self.job_data["state"]["file_uploads"]
    state["uploaded_files"] = sum(
        1 for doc in self.job_data["documents"]
        if doc.get("openai_file", {}).get("status") == "uploaded"
    )
    state["total_files"] = len(self.job_data["documents"])
    state["total_size"] = sum(
        doc.get("openai_file", {}).get("file_size", 0)
        for doc in self.job_data["documents"]
    )
    state["total_pdf_pages"] = sum(
        doc.get("openai_file", {}).get("page_count", 0)
        for doc in self.job_data["documents"]
        if doc.get("ext", "").lower() == "pdf"
    )
```

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

## Job Data Structure

The job data is a dictionary with the following structure:

```json
{
  "job_id": "unique-uuid-string",
  "created_at": "2024-03-20T12:00:00Z",
  "temp_dir": "/path/to/temp/directory",
  "status": "initialized",
  "documents": [
    {
      "id": "document-uuid",
      "name": "Document Name",
      "path": "/path/to/document.txt",
      "format": "PDF",
      "size": 1024,
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
  "threads": [
    {
      "id": "thread-uuid",
      "title": "Thread Title",
      "status": "initialized",
      "messages": [],
      "queries": [
        {
          "id": "query-uuid",
          "title": "Query Title",
          "text": "What is the main conclusion?",
          "format": "free_form"
        }
      ]
    }
  ],
  "openai_config": {
    "model": "gpt-4o",
    "assistant_id": "",
    "max_tokens": 128000,
    "temperature": 0.0,
    "file_purpose": "assistants"
  },
  "state": {
    "file_uploads": {
      "total_files": 5,
      "uploaded_files": 4,
      "failed_files": ["file-id-1"],
      "status": "in_progress",
      "total_size": 5120,
      "total_pdf_pages": 50,
      "validation_status": "passed"
    },
    "threads": {
      "total_threads": 3,
      "completed_threads": 1,
      "failed_threads": [],
      "status": "in_progress"
    }
  }
}
```

## Integration with Other Services

The Job Manager integrates with:

- **Query Manager**:
  - Provides thread management
  - Tracks thread status
  - Manages query state

- **LLM Interface**:
  - Provides OpenAI configuration
  - Manages API settings
  - Tracks conversation state

- **Document Handler**:
  - Stores document information
  - Tracks upload status
  - Manages file metadata

## Job Status Flow

The Job Manager tracks the following status transitions:

1. **initialized**: Initial job state
2. **uploading_files**: Files are being uploaded to OpenAI
3. **upload_complete**: All files successfully uploaded
4. **upload_failed**: One or more files failed to upload
5. **processing_threads**: Threads are being processed
6. **threads_complete**: All threads processed successfully
7. **threads_failed**: One or more threads failed
8. **completed**: Job finalized and cleaned up

## Performance Considerations

- Job data is stored in memory during the extraction process
- Temporary files are created for document text and output
- Cleanup is performed after the job is complete
- Each job has a unique ID and temporary directory
- Thread and file status is tracked in memory for real-time updates
- OpenAI configuration is managed centrally
- Thread state is tracked independently of file state 