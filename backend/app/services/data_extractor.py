import logging
from functools import wraps
from app.services.document_handler import DocumentHandler
from app.services.query_manager import QueryManager
from app.services.job_manager import JobManager
from app.services.llm_interface import LLMInterface
from app.services.output_generator import OutputGenerator
from app.services.parsers import parsers

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

class DataExtractor:
    def __init__(self, job_manager, document_handler, query_manager, llm_interface):
        self.job_manager = job_manager
        self.document_handler = document_handler
        self.query_manager = query_manager
        self.llm_interface = llm_interface

    @handle_errors
    def initialize_job(self):
        self.job_manager.initialize_temp_dir()
        self.job_manager.update_status("Initialized")

    @handle_errors
    def process_documents(self):
        self.document_handler.process_documents()

    @handle_errors
    def process_queries_and_collect_responses(self):
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
        self.initialize_job()
        self.process_documents()
        self.process_queries_and_collect_responses()
        logging.info("Responses collected.")
        return self.job_manager.get_job_data()