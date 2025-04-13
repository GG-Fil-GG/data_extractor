import logging
from functools import wraps
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

    def __init__(self, job_manager, document_handler, query_manager, llm_interface):
        """
        Initialize the DataExtractor with required service components.
        
        Args:
            job_manager (JobManager): Instance of JobManager for job handling.
            document_handler (DocumentHandler): Instance of DocumentHandler for document processing.
            query_manager (QueryManager): Instance of QueryManager for query handling.
            llm_interface (LLMInterface): Instance of LLMInterface for LLM interactions.
        """
        self.job_manager = job_manager
        self.document_handler = document_handler
        self.query_manager = query_manager
        self.llm_interface = llm_interface

    @handle_errors
    def initialize_job(self):
        """
        Initialize a new data extraction job.
        
        Creates necessary temporary directories and sets initial job status.
        Updates the job status to "Initialized" upon completion.
        """
        self.job_manager.initialize_temp_dir()
        self.job_manager.update_status("Initialized")

    @handle_errors
    def process_documents(self):
        """
        Process all documents associated with the current job.
        
        Delegates document processing to the DocumentHandler service.
        This may include text extraction, preprocessing, and any necessary
        document-specific operations.
        """
        self.document_handler.process_documents()

    @handle_errors
    def process_queries_and_collect_responses(self):
        """
        Process all queries against each document and collect responses.
        
        For each document-query pair:
        1. Loads the document text
        2. Executes the query using the LLM interface
        3. Parses and stores the response
        
        The responses are stored in the job_data structure with the following format:
        {
            "Responses": {
                "document_alias": {
                    "query_alias": response_content
                }
            }
        }
        
        Updates job status to "Queries Processed, Responses Collected" upon completion.
        
        Raises:
            ValueError: If there are issues with query processing or response parsing.
            Exception: For any other unexpected errors during processing.
        """
        for document in self.job_manager.job_data["Documents"]:
            doc_text = self.document_handler.load_text(document["Path"])
            document_alias = document["Alias"]
            if document_alias not in self.job_manager.job_data["Responses"]:
                self.job_manager.job_data["Responses"][document_alias] = {}
            for query in self.job_manager.job_data["Queries"]:
                query_alias = query["Alias"]
                query_text = query["Text"]
                query_format = query["Format"]
                parser_entry = parsers.get(query_format)
                parser = parser_entry["parser"]
                json_required = parser_entry["json_required"]
                format_guidance_message = parser_entry["format_guidance"]

                response_format = None
                if json_required:
                    response_format = {"type": "json_object"}

                try:
                    response = self.llm_interface.ask(query_text, doc_text, parser, format_guidance_message, response_format)
                    if response is None:
                        response = "Information not available"
                    self.job_manager.job_data["Responses"][document_alias][query_alias] = response
                except ValueError as ve:
                    logging.error(f"ValueError in processing query '{query_alias}' for document '{document_alias}': {ve}")
                    self.job_manager.job_data["Responses"][document_alias][query_alias] = "Information not available"
                except Exception as e:
                    logging.error(f"Error in processing query '{query_alias}' for document '{document_alias}': {e}")
                    self.job_manager.job_data["Responses"][document_alias][query_alias] = "Information not available"
        self.job_manager.update_status("Queries Processed, Responses Collected")

    @handle_errors
    def run(self):
        """
        Execute the complete data extraction pipeline.
        
        This method orchestrates the entire extraction process by:
        1. Initializing the job
        2. Processing all documents
        3. Running queries and collecting responses
        
        Returns:
            dict: The complete job data including all documents, queries, and responses.
                Format:
                {
                    "Documents": [...],
                    "Queries": [...],
                    "Responses": {...},
                    "Status": "..."
                }
        """
        self.initialize_job()
        self.process_documents()
        self.process_queries_and_collect_responses()
        logging.info("Responses collected.")
        return self.job_manager.get_job_data()