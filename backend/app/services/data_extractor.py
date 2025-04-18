import logging
from functools import wraps
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.services.document_handler import DocumentHandler
from app.services.query_manager import QueryManager
from app.services.job_manager import JobManager
from app.services.llm_interface import LLMInterface
from app.services.output_generator import OutputGenerator
from app.services.parsers import parsers

def handle_errors(func):
    """
    A decorator that wraps functions to handle and log exceptions.
    
    Args:
        func: The function to be wrapped.
        
    Returns:
        wrapper: The wrapped function that includes error handling.
        
    Raises:
        Exception: Re-raises any caught exception after logging it.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

class DataExtractor:
    """
    A class that manages the extraction of data from documents using LLM-based queries.
    
    This class orchestrates the entire data extraction process, including document processing,
    query execution, and response collection. It works with multiple service components to
    handle different aspects of the extraction pipeline.
    
    Attributes:
        job_manager (JobManager): Manages job state and temporary storage.
        document_handler (DocumentHandler): Handles document processing and text extraction.
        query_manager (QueryManager): Manages query operations.
        llm_interface (LLMInterface): Interface for LLM interactions.
    """

    def __init__(self, job_manager: JobManager, document_handler: DocumentHandler, 
                 query_manager: QueryManager, llm_interface: LLMInterface):
        """
        Initialize the DataExtractor with required service components.
        
        Args:
            job_manager: Instance of JobManager for job handling.
            document_handler: Instance of DocumentHandler for document processing.
            query_manager: Instance of QueryManager for query handling.
            llm_interface: Instance of LLMInterface for LLM interactions.
        """
        self.job_manager = job_manager
        self.document_handler = document_handler
        self.query_manager = query_manager
        self.llm_interface = llm_interface

    @handle_errors
    def initialize_job(self) -> None:
        """
        Initialize a new data extraction job.
        
        Creates necessary temporary directories and sets initial job status.
        Updates the job status to "initialized" upon completion.
        """
        self.job_manager.initialize_temp_dir()
        self.job_manager.update_status("initialized")

    @handle_errors
    def process_documents(self) -> None:
        """
        Process all documents associated with the current job.
        
        Delegates document processing to the DocumentHandler service.
        Updates job status to "uploading_files" during processing.
        """
        self.job_manager.update_status("uploading_files")
        self.document_handler.process_documents()
        
        # Update state after document processing
        state = self.job_manager.job_data["state"]["file_uploads"]
        if state["failed_files"]:
            self.job_manager.update_status("upload_failed")
        else:
            self.job_manager.update_status("upload_complete")

    @handle_errors
    def create_threads(self) -> None:
        """
        Create threads for processing queries.
        
        Creates a thread for each document-query combination.
        Updates thread state in job data.
        """
        for document in self.job_manager.job_data["documents"]:
            for query in self.job_manager.job_data["queries"]:
                thread_title = f"{document['name']} - {query['title']}"
                thread = self.query_manager.create_thread(thread_title)
                
                # Add query to thread
                thread["queries"].append(query)
                
                # Update thread state
                self.job_manager.job_data["state"]["threads"]["total_threads"] += 1

    @handle_errors
    def process_threads(self) -> None:
        """
        Process all threads and collect responses.
        
        For each thread:
        1. Processes the query using the LLM interface
        2. Updates thread status
        3. Collects responses
        
        Updates job status to "processing_threads" during processing.
        """
        self.job_manager.update_status("processing_threads")
        
        for thread in self.job_manager.job_data["threads"]:
            try:
                # Process each query in the thread
                for query in thread["queries"]:
                    result = self.query_manager.process_query(thread["id"], query["id"])
                    
                    # Add response to thread
                    thread["messages"].append({
                        "role": "assistant",
                        "content": result["response"],
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                # Update thread status
                self.query_manager.update_thread_status(thread["id"], "complete")
                
            except Exception as e:
                logging.error(f"Error processing thread {thread['id']}: {e}")
                self.query_manager.update_thread_status(thread["id"], "failed")
                self.job_manager.job_data["state"]["threads"]["failed_threads"].append(thread["id"])
        
        # Update overall thread state
        state = self.job_manager.job_data["state"]["threads"]
        if state["failed_threads"]:
            self.job_manager.update_status("threads_failed")
        else:
            self.job_manager.update_status("threads_complete")

    @handle_errors
    def run(self) -> Dict[str, Any]:
        """
        Execute the complete data extraction pipeline.
        
        This method orchestrates the entire extraction process by:
        1. Initializing the job
        2. Processing all documents
        3. Creating threads for queries
        4. Processing threads and collecting responses
        
        Returns:
            Dict containing the complete job data including all documents, threads, and responses.
        """
        self.initialize_job()
        self.process_documents()
        
        if self.job_manager.job_data["status"] == "upload_complete":
            self.create_threads()
            self.process_threads()
            
            if self.job_manager.job_data["status"] == "threads_complete":
                self.job_manager.finalize_extraction()
        
        return self.job_manager.job_data