# Backend Architecture

## Overview

The DataExtractor backend is designed as a modular system of interconnected services that work together to extract structured data from documents using AI. The architecture follows a service-oriented approach where each component has a specific responsibility in the extraction pipeline.

## Core Components

The backend consists of the following core components:

1. **Job Manager**: Central data store that maintains job state and coordinates between components
2. **Document Handler**: Processes different document formats and extracts text
3. **Query Manager**: Manages extraction queries and their formats
4. **LLM Interface**: Communicates with OpenAI's language models
5. **Parsers**: Transform raw LLM responses into structured formats
6. **Data Extractor**: Orchestrates the end-to-end extraction process
7. **Output Generator**: Creates output files in different formats
8. **Token Counter**: Counts tokens in text for managing API usage

## Component Relationships

![Component Diagram](../assets/component-diagram.png)

*Note: The diagram above is a conceptual representation. The actual diagram should be created and placed in the assets directory.*

### Dependency Flow

- **Data Extractor** depends on:
  - Job Manager
  - Document Handler
  - Query Manager
  - LLM Interface

- **Document Handler** depends on:
  - Job Manager
  - Token Counter (for token counting)

- **Query Manager** depends on:
  - Job Manager

- **Output Generator** depends on:
  - Job Manager

- **LLM Interface** uses:
  - Parsers
  - Token Counter (for token counting)

## Data Flow

The extraction process follows this general flow:

1. **Initialization**:
   - Job Manager creates a new job with a unique ID
   - Temporary directory is initialized

2. **Document Processing**:
   - Document Handler extracts text from uploaded documents
   - Text is cleaned and saved to temporary files
   - Token Counter may be used to count tokens in document text

3. **Query Processing**:
   - For each document and query combination:
     - Document text is loaded
     - Token Counter may be used to ensure text doesn't exceed limits
     - Query is sent to the LLM Interface
     - Response is parsed and stored in the job data

4. **Output Generation**:
   - Output Generator creates CSV or DOCX files
   - Files are made available for download

5. **Cleanup**:
   - Temporary files are deleted after download

## Key Interfaces

### Job Manager Interface

The Job Manager provides a central data store for all components:

```python
job_manager = JobManager()
job_manager.initialize_temp_dir()
job_manager.update_status("Processing")
job_data = job_manager.get_job_data()
job_manager.finalize_extraction()
```

### Document Handler Interface

The Document Handler processes documents and extracts text:

```python
document_handler = DocumentHandler(job_manager)
document_handler.process_documents()
text = document_handler.load_text(file_path)
```

### LLM Interface

The LLM Interface communicates with OpenAI's language models:

```python
llm_interface = LLMInterface(api_key, model="gpt-4o")
response = llm_interface.ask(query, context, parser, format_guidance)
```

### Token Counter Interface

The Token Counter counts tokens in text:

```python
from app.services.token_counter import count_tokens
token_count = count_tokens(text)
```

### Data Extractor Interface

The Data Extractor orchestrates the extraction process:

```python
data_extractor = DataExtractor(job_manager, document_handler, query_manager, llm_interface)
data_extractor.initialize_job()
data_extractor.process_documents()
data_extractor.process_queries_and_collect_responses()
results = data_extractor.run()
```

### Output Generator Interface

The Output Generator creates output files:

```python
output_generator = OutputGenerator(job_manager)
output_generator.generate_output()
```

## Error Handling Strategy

The backend implements a consistent error handling strategy:

1. **Method-level error handling**: Each method is wrapped with a decorator that catches and logs exceptions
2. **Component-level error handling**: Components handle errors specific to their domain
3. **API-level error handling**: The API routes handle errors and return appropriate HTTP responses

Example error handling decorator:

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

## Configuration

The backend uses environment variables for configuration:

- `OPENAI_API_KEY`: API key for OpenAI
- `MODEL_NAME`: The model to use (default: "gpt-4o")
- `TEMPERATURE`: Temperature setting for the model (default: 0.0)

## Extensibility

The architecture is designed to be extensible:

1. **New document formats**: Add new extraction methods to the Document Handler
2. **New query formats**: Add new parsers to the Parsers module
3. **New output formats**: Add new generation methods to the Output Generator
4. **Alternative LLM providers**: Create new implementations of the LLM Interface
5. **Different tokenizers**: Update the Token Counter for different models

## Performance Considerations

1. **Memory usage**: Document text is stored in memory during processing
2. **API costs**: Each query to the LLM incurs a cost based on token usage
3. **Processing time**: Large documents or many queries can take significant time
4. **Concurrency**: The current implementation processes documents and queries sequentially
5. **Token management**: Token counting helps optimize API usage and costs

## Security Considerations

1. **API key protection**: The OpenAI API key should be securely stored
2. **Temporary file management**: Temporary files are created in a controlled directory
3. **Input validation**: All inputs should be validated before processing
4. **Output sanitization**: Outputs should be sanitized before returning to the client

## Deployment Architecture

The backend is designed to be deployed as a containerized service:

1. **Docker container**: The backend runs in a Docker container
2. **API server**: FastAPI serves the API endpoints
3. **Temporary storage**: A volume mount provides temporary storage
4. **Environment variables**: Configuration is provided via environment variables

## Future Enhancements

Potential enhancements to the architecture include:

1. **Asynchronous processing**: Process documents and queries asynchronously
2. **Job queuing**: Implement a job queue for handling multiple extraction jobs
3. **Caching**: Cache LLM responses to reduce API costs
4. **Streaming responses**: Stream extraction results as they become available
5. **Alternative LLM providers**: Support for other LLM providers
6. **Advanced token management**: Implement strategies for handling documents that exceed token limits 