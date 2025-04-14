import os
import logging
from functools import wraps
from openai import OpenAI
import time

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

class DocumentHandler:
    def __init__(self, job_manager, openai_client):
        self.job_manager = job_manager
        self.openai_client = openai_client
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    @handle_errors
    def process_documents(self):
        """
        Process all documents in the current job by uploading them to OpenAI.
        Updates job status and tracks upload progress.
        """
        self.job_manager.update_status("uploading_files")
        
        for document in self.job_manager.job_data["Documents"]:
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

    @handle_errors
    def upload_file_to_openai(self, document):
        """
        Upload a file to OpenAI with retry mechanism.
        
        Args:
            document: Document object containing file information
        """
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

    @handle_errors
    def cleanup_files(self):
        """
        Clean up uploaded files from OpenAI.
        """
        for document in self.job_manager.job_data["Documents"]:
            if document["openai_file"]["file_id"]:
                try:
                    self.openai_client.files.delete(file_id=document["openai_file"]["file_id"])
                    document["openai_file"]["status"] = "deleted"
                except Exception as e:
                    logging.error(f"Failed to delete file {document['name']} from OpenAI: {e}")
                    document["openai_file"]["error"] = str(e)