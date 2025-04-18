# Query Manager

## Overview

The Query Manager is a service component in the DataExtractor backend that manages extraction queries and their conversation threads. It handles the creation and management of conversation threads, maintains message history, and ensures proper context management for LLM interactions.

## Class Structure

The `QueryManager` class is defined in `backend/app/services/query_manager.py` and works closely with the Job Manager to process queries as part of the extraction workflow.

### Initialization

```python
def __init__(self, job_manager):
    self.job_manager = job_manager
    self.context_window = 128000  # GPT-4o context window
    self.max_history_messages = 10  # Maximum number of messages to keep in history
    self.encoding = tiktoken.get_encoding("cl100k_base")  # Tokenizer for GPT-4o
```

The Query Manager is initialized with:
- A reference to the Job Manager for job data and status updates
- Configuration for thread management and context windows
- Tokenizer for message processing

## Key Methods

### create_thread()

Creates a new conversation thread in the job data.

```python
def create_thread(self, title: str) -> Dict:
    thread = {
        "id": str(uuid.uuid4()),
        "title": title,
        "status": "initialized",
        "messages": [],
        "queries": []
    }
    self.job_manager.job_data["threads"].append(thread)
    self.job_manager.job_data["state"]["threads"]["total_threads"] += 1
```

This method:
1. Creates a new thread with initial state
2. Adds the thread to the job data
3. Updates thread count in job state

### add_message()

Adds a message to a thread's history while managing context window limits.

```python
def add_message(self, thread_id: str, role: str, content: str) -> Dict:
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    thread["messages"].append(message)
    self._manage_context_window(thread_id)
```

This method:
1. Creates a message with role, content, and timestamp
2. Adds the message to the thread's history
3. Manages context window limits

### process_query()

Processes a query within an existing thread context.

```python
def process_query(self, thread_id: str, query_id: str) -> Dict:
    # Add user query
    self.add_message(thread_id, "user", query["text"])
    
    # Update thread status
    self.update_thread_status(thread_id, "processing")
    
    try:
        # Get thread history for context
        messages = self.get_thread_history(thread_id)
        
        # Call LLMInterface to process the query
        response = self.llm_interface.process_messages(messages)
        
        # Add assistant response to thread
        self.add_message(thread_id, "assistant", response)
        
        return {
            "thread_id": thread_id,
            "query_id": query_id,
            "response": response,
            "format": query["format"]
        }
```

This method:
1. Adds the user query to the thread
2. Updates thread status
3. Processes the query through LLMInterface
4. Adds the response to the thread
5. Returns the processing result

## Thread Management

The Query Manager maintains conversation threads with the following features:

1. **Message History**:
   - Tracks all messages in a thread
   - Maintains message order and timing
   - Enforces maximum message count

2. **Context Window Management**:
   - Enforces maximum message count (10 messages)
   - Automatically trims message history when needed
   - Maintains conversation flow

3. **Status Tracking**:
   - Monitors thread processing status
   - Updates thread state in job data
   - Tracks overall thread progress

## Integration with Other Services

The Query Manager integrates with:

- **Job Manager**: 
  - Accesses job data and thread information
  - Updates job status and progress
  - Maintains thread state in job data
  - Manages thread lifecycle

- **LLMInterface**:
  - Provides message history for processing
  - Handles query responses
  - Manages conversation context

## Thread Structure

Each thread maintains the following information in the job data:

```json
{
    "id": "thread-uuid",
    "title": "Thread Title",
    "status": "initialized",
    "messages": [
        {
            "role": "user",
            "content": "query_text",
            "timestamp": "2024-03-20T12:01:00Z"
        },
        {
            "role": "assistant",
            "content": "response_text",
            "timestamp": "2024-03-20T12:02:00Z"
        }
    ],
    "queries": [
        {
            "id": "query-uuid",
            "title": "Query Title",
            "text": "Query text",
            "format": "format_type"
        }
    ]
}
```

## Query Structure

Queries are defined in the job data structure as part of the threads array:

```json
{
    "threads": [
        {
            "id": "thread-uuid",
            "title": "Thread Title",
            "queries": [
                {
                    "id": "query-uuid",
                    "title": "Query Title",
                    "text": "Query text",
                    "format": "format_type"
                }
            ]
        }
    ]
}
```

Where:
- `id`: Unique identifier for the query
- `title`: Display title for the query
- `text`: The actual query text
- `format`: Response format specification

## Error Handling

The Query Manager uses a decorator pattern for error handling:

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
1. Wraps each method to catch exceptions
2. Logs the error with the method name and error message
3. Re-raises the exception for higher-level handling

## Performance Considerations

- Context window management ensures efficient message history
- Message history trimming prevents excessive memory usage
- Thread status tracking enables efficient progress monitoring
- Integration with job data structure ensures consistent state management

## Future Enhancements

Potential enhancements to the Query Manager could include:

- Methods for validating query formats
- Functions for transforming queries into optimal prompts
- Support for query templates and presets
- Query categorization and organization
- Enhanced context window management with token counting
- Support for streaming responses
- Query result caching

## Notes

The minimal implementation suggests that query management in the current system is relatively straightforward, with most of the query-related logic potentially handled by the Data Extractor or other components. 