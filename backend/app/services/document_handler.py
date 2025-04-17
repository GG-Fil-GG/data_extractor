import os
import logging
import fitz  # PyMuPDF for PDF page counting
from docx import Document as DocxDocument  # For .docx files
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
        self.max_total_size = 32 * 1024 * 1024  # 32MB in bytes
        self.max_total_pages = 100  # Only applies to PDFs
        self.supported_extensions = {
            "pdf": self.get_pdf_page_count,
            "docx": self.get_docx_page_count,
            "txt": lambda _: 1  # Text files are considered as 1 page
        }

    def get_pdf_page_count(self, document):
        """Get page count for PDF files."""
        try:
            doc = fitz.open(document["path"])
            page_count = len(doc)
            doc.close()
            return page_count
        except Exception as e:
            raise ValueError(f"Failed to get PDF page count for {document['name']}: {str(e)}")

    def get_docx_page_count(self, document):
        """Get page count for DOCX files."""
        try:
            doc = DocxDocument(document["path"])
            # This is an approximation as docx doesn't have a direct page count
            # We'll count paragraphs as a rough estimate
            return len(doc.paragraphs)
        except Exception as e:
            raise ValueError(f"Failed to get DOCX page count for {document['name']}: {str(e)}")

    def validate_documents(self):
        """
        Validates all documents collectively before upload.
        - Total size limit applies to all file types
        - Page count limit only applies to PDF files
        
        Raises:
            ValueError: If total size exceeds limit or PDF page count exceeds limit
        """
        total_size = 0
        total_pdf_pages = 0
        
        for document in self.job_manager.job_data["Documents"]:
            # Check file size for all files
            file_size = os.path.getsize(document["path"])
            total_size += file_size
            
            # Only count pages for PDF files
            if document["Ext"].lower() == "pdf":
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

    @handle_errors
    def process_documents(self):
        """
        Process all documents in the current job by uploading them to OpenAI.
        Updates job status and tracks upload progress.
        """
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
            self.job_manager.update_status("validation_failed")
            return
        
        for document in self.job_manager.job_data["Documents"]:
            try:
                # Initialize OpenAI file info
                document["openai_file"] = {
                    "file_id": None,
                    "purpose": "user_data",
                    "status": "pending",
                    "error": None,
                    "upload_time": None,
                    "retry_count": 0,
                    "file_size": os.path.getsize(document["path"]),
                    "page_count": self.get_pdf_page_count(document) if document["Ext"].lower() == "pdf" else None
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
                        purpose="user_data"
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