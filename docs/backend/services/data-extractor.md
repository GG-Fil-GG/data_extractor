# Data Extractor

## Overview

The Data Extractor is the central orchestration component of the extraction system. It coordinates the entire data extraction process, from initializing jobs to collecting responses from the language model. This service integrates with multiple other components to provide a seamless extraction workflow.

## Responsibilities

- Orchestrating the end-to-end extraction process
- Coordinating between document handling, query processing, and LLM interaction
- Managing the extraction job lifecycle
- Collecting and organizing extraction responses
- Handling errors throughout the extraction process

## Class Structure

The `DataExtractor` class is defined in `backend/app/services/data_extractor.py` and serves as the main controller for the extraction workflow.

### Initialization

```python
def __init__(self, job_manager, document_handler, query_manager, llm_interface):
    self.job_manager = job_manager
    self.document_handler = document_handler
    self.query_manager = query_manager
    self.llm_interface = llm_interface
```

The Data Extractor is initialized with references to:
- Job Manager: Manages job data and status
- Document Handler: Processes documents and extracts text
- Query Manager: Manages query information
- LLM Interface: Communicates with the language model

## Key Methods

### run()

The main method that executes the complete extraction workflow.

```python
def run(self):
    self.initialize_job()
    self.process_documents()
    self.process_queries_and_collect_responses()
    logging.info("Responses collected.")
    return self.job_manager.get_job_data()
```

This method:
1. Initializes the extraction job
2. Processes all documents
3. Processes all queries and collects responses
4. Returns the complete job data

### initialize_job()

Prepares the job for extraction.

```python
def initialize_job(self):
    self.job_manager.initialize_temp_dir()
    self.job_manager.update_status("Initialized")
```

This method:
1. Initializes the temporary directory for job files
2. Updates the job status to "Initialized"

### process_documents()

Processes all documents in the job.

```python
def process_documents(self):
    self.document_handler.process_documents()
```

This method delegates document processing to the Document Handler, which:
1. Extracts text from each document
2. Cleans the text
3. Saves the processed text to temporary files

### process_queries_and_collect_responses()

The core extraction method that processes each query against each document.

```python
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
```

This method:
1. Iterates through each document in the job
2. Loads the processed text for the document
3. Creates a response container for the document if it doesn't exist
4. Iterates through each query in the job
5. Gets the appropriate parser and format guidance for the query format
6. Configures JSON response format if required
7. Sends the query to the LLM Interface
8. Stores the response in the job data
9. Handles errors gracefully, providing a fallback response
10. Updates the job status when complete

## Error Handling

The Data Extractor uses a decorator pattern for error handling:

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

Additionally, the `process_queries_and_collect_responses()` method includes specific error handling:
- Catches ValueError separately for parsing errors
- Catches general exceptions for other errors
- Provides a fallback response of "Information not available"
- Logs detailed error information

## Integration with Other Services

The Data Extractor integrates with:

- **Job Manager**: Manages job data and status updates
- **Document Handler**: Processes documents and extracts text
- **Query Manager**: Provides access to query information
- **LLM Interface**: Sends queries to the language model and processes responses
- **Parsers**: Uses parsers to format and validate responses

## Extraction Workflow

The complete extraction workflow is:

1. **Initialization**: Set up the job and create temporary directories
2. **Document Processing**: Extract and clean text from all documents
3. **Query Processing**: For each document and query combination:
   - Load the document text
   - Get the appropriate parser and format guidance
   - Send the query to the language model
   - Parse and validate the response
   - Store the response in the job data
4. **Completion**: Return the complete job data with all responses

## Response Structure

Responses are organized in a nested dictionary structure:

```json
{
  "Responses": {
    "Document1": {
      "Query1": "Response text...",
      "Query2": "Response text..."
    },
    "Document2": {
      "Query1": "Response text...",
      "Query2": "Response text..."
    }
  }
}
```

This structure allows for easy access to responses by document and query.

## Error Handling Strategy

The Data Extractor implements a robust error handling strategy:

1. **Method-level error handling**: Each method is wrapped with error handling
2. **Query-level error handling**: Each query is processed in a try-except block
3. **Fallback responses**: If a query fails, a fallback response is provided
4. **Detailed logging**: Errors are logged with context information

This ensures that the extraction process continues even if individual queries fail.

## Performance Considerations

- Processing is sequential, with each document and query processed in order
- Error handling ensures the process continues even if individual queries fail
- The extraction process can be time-consuming for large numbers of documents and queries 