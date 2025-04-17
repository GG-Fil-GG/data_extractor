import os
import uuid
import logging
import shutil
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

    @handle_errors
    def initialize_temp_dir(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(script_dir, "../.."))
        temp_root_dir = os.path.join(root_dir, "temp")
        os.makedirs(temp_root_dir, exist_ok=True)
        temp_job_dir = os.path.join(temp_root_dir, f"{self.job_data['Job ID']}")
        os.makedirs(temp_job_dir, exist_ok=True)
        self.job_data["Temp Dir"] = temp_job_dir
        logging.info(f"Temporary directory created: {temp_job_dir}")

    def update_status(self, new_status):
        self.job_data["Status"] = new_status
        logging.info(f"Job status updated to: {new_status}")

    def update_file_upload_progress(self):
        """
        Updates the file upload progress in the job state.
        """
        state = self.job_data["state"]["file_uploads"]
        state["uploaded_files"] = sum(
            1 for doc in self.job_data["Documents"]
            if doc.get("openai_file", {}).get("status") == "uploaded"
        )
        state["total_files"] = len(self.job_data["Documents"])
        state["status"] = "complete" if state["uploaded_files"] == state["total_files"] else "in_progress"
        logging.info(f"File upload progress: {state['uploaded_files']}/{state['total_files']}")

    def add_failed_file(self, file_id):
        """
        Adds a file ID to the list of failed uploads.
        
        Args:
            file_id: The ID of the file that failed to upload
        """
        if file_id not in self.job_data["state"]["file_uploads"]["failed_files"]:
            self.job_data["state"]["file_uploads"]["failed_files"].append(file_id)
            logging.error(f"Added failed file to tracking: {file_id}")

    def get_file_upload_status(self):
        """
        Returns the current file upload status.
        
        Returns:
            dict: Current file upload status including:
                - total_files: Total number of files to upload
                - uploaded_files: Number of successfully uploaded files
                - failed_files: List of file IDs that failed to upload
                - status: Overall upload status (pending/in_progress/complete)
        """
        return self.job_data["state"]["file_uploads"]

    @handle_errors
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

    def get_job_data(self):
        return self.job_data