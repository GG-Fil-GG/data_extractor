import os
import uuid
import logging
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import wraps

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

class JobManager:
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

    @handle_errors
    def initialize_temp_dir(self) -> None:
        """Initialize the temporary directory for the job."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(script_dir, "../.."))
        temp_root_dir = os.path.join(root_dir, "temp")
        os.makedirs(temp_root_dir, exist_ok=True)
        temp_job_dir = os.path.join(temp_root_dir, self.job_data["job_id"])
        os.makedirs(temp_job_dir, exist_ok=True)
        self.job_data["temp_dir"] = temp_job_dir
        logging.info(f"Temporary directory created: {temp_job_dir}")

    @handle_errors
    def update_status(self, new_status: str) -> None:
        """Update the overall job status."""
        self.job_data["status"] = new_status
        logging.info(f"Job status updated to: {new_status}")
        
        # Update validation status based on job status
        if new_status == "validation_failed":
            self.job_data["state"]["file_uploads"]["validation_status"] = "failed"
        elif new_status == "uploading_files":
            self.job_data["state"]["file_uploads"]["validation_status"] = "passed"

    @handle_errors
    def update_file_upload_progress(self) -> None:
        """Update the file upload progress in the job state."""
        state = self.job_data["state"]["file_uploads"]
        state["uploaded_files"] = sum(
            1 for doc in self.job_data["documents"]
            if doc.get("openai_file", {}).get("status") == "uploaded"
        )
        state["total_files"] = len(self.job_data["documents"])
        
        # Update total size and PDF pages
        state["total_size"] = sum(
            doc.get("openai_file", {}).get("file_size", 0)
            for doc in self.job_data["documents"]
        )
        state["total_pdf_pages"] = sum(
            doc.get("openai_file", {}).get("page_count", 0)
            for doc in self.job_data["documents"]
            if doc.get("ext", "").lower() == "pdf"
        )
        
        # Update overall status
        if state["uploaded_files"] == state["total_files"]:
            state["status"] = "complete"
        elif state["failed_files"]:
            state["status"] = "failed"
        else:
            state["status"] = "in_progress"
            
        logging.info(f"File upload progress: {state['uploaded_files']}/{state['total_files']}")

    @handle_errors
    def add_failed_file(self, file_id: str) -> None:
        """Add a file ID to the list of failed uploads."""
        if file_id not in self.job_data["state"]["file_uploads"]["failed_files"]:
            self.job_data["state"]["file_uploads"]["failed_files"].append(file_id)
            logging.error(f"Added failed file to tracking: {file_id}")

    @handle_errors
    def get_file_upload_status(self) -> Dict:
        """Get the current file upload status."""
        return self.job_data["state"]["file_uploads"]

    @handle_errors
    def create_thread(self, title: str) -> Dict:
        """Create a new thread in the job data."""
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
        logging.info(f"Created new thread: {thread['id']}")
        return thread

    @handle_errors
    def get_thread(self, thread_id: str) -> Optional[Dict]:
        """Get a thread by its ID."""
        return next(
            (thread for thread in self.job_data["threads"] if thread["id"] == thread_id),
            None
        )

    @handle_errors
    def update_thread_status(self, thread_id: str, new_status: str) -> None:
        """Update the status of a thread."""
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
            
            logging.info(f"Thread {thread_id} status updated to: {new_status}")

    @handle_errors
    def add_query_to_thread(self, thread_id: str, query: Dict) -> None:
        """Add a query to a thread."""
        thread = self.get_thread(thread_id)
        if thread:
            thread["queries"].append(query)
            logging.info(f"Added query to thread {thread_id}")

    @handle_errors
    def get_thread_status(self) -> Dict:
        """Get the current thread processing status."""
        return self.job_data["state"]["threads"]

    @handle_errors
    def get_openai_config(self) -> Dict:
        """Get the OpenAI configuration."""
        return self.job_data["openai_config"]

    @handle_errors
    def update_openai_config(self, config: Dict) -> None:
        """Update the OpenAI configuration."""
        self.job_data["openai_config"].update(config)
        logging.info("OpenAI configuration updated")

    @handle_errors
    def finalize_extraction(self) -> None:
        """Clean up temporary files and finalize the job."""
        temp_dir = self.job_data.get("temp_dir")
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
            self.update_status("completed")
            logging.info("Temporary directory cleanup completed.")

    @handle_errors
    def get_job_data(self) -> Dict:
        """Get the complete job data."""
        return self.job_data