# Query Manager

## Overview

The Query Manager is a service component in the DataExtractor backend that manages extraction queries and their conversation threads. It handles the creation and management of conversation threads, maintains message history, and ensures proper context management for LLM interactions.

## Class Structure

The `QueryManager` class is defined in `backend/app/services/query_manager.py` and works closely with the Job Manager to process queries as part of the extraction workflow.

### Initialization

```python
def __init__(self, job_manager):
    self.job_manager = job_manager
    self.threads: Dict[str, Dict] = {}  # Store thread states
    self.context_window = 128000  # GPT-4o context window
    self.max_history_messages = 10  # Maximum number of messages to keep in history
    self.encoding = tiktoken.get_encoding("cl100k_base")  # Tokenizer for GPT-4o
```

The Query Manager is initialized with:
- A reference to the Job Manager for job data and status updates
- Configuration for thread management and context windows
- Tokenizer for accurate message size tracking

## Key Methods

### create_thread()

Creates a new conversation thread and initializes it with the system message from job data.

```python
def create_thread(self, thread_id: str) -> Dict:
    thread = {
        "id": thread_id,
        "created_at": datetime.utcnow().isoformat(),
        "messages": [],
        "token_count": 0,
        "status": "pending",
        "last_response_id": None,
        "error": None
    }
    
    # Add system_message as initial developer message
    system_message = self.job_manager.job_data.get("system_message")
    if system_message:
        self.add_message(thread_id, "developer", system_message)
```

This method:
1. Creates a new thread with initial state
2. Adds the system message as the first developer message
3. Tracks thread creation time and status

### add_message()

Adds a message to a thread's history while managing context window limits.

```python
def add_message(self, thread_id: str, role: str, content: str) -> Dict:
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
        "token_count": len(self.encoding.encode(content))
    }
    
    thread["messages"].append(message)
    thread["token_count"] += message["token_count"]
    
    # Ensure we don't exceed context window
    self._manage_context_window(thread_id)
```

This method:
1. Creates a message with role, content, and metadata
2. Updates thread token count
3. Manages context window limits
4. Preserves system message when trimming history

### process_query()

Processes a query within an existing thread context.

```python
def process_query(self, thread_id: str, query_text: str) -> Dict:
    # Add user query
    self.add_message(thread_id, "user", query_text)
    
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
            "response": response,
            "status": "complete"
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
   - Preserves system message as initial context

2. **Context Window Management**:
   - Enforces GPT-4o context window limits (128k tokens)
   - Automatically trims message history when needed
   - Preserves system message during trimming

3. **Status Tracking**:
   - Monitors thread processing status
   - Tracks successful and failed queries
   - Updates overall job progress

## Integration with Other Services

The Query Manager integrates with:

- **Job Manager**: 
  - Accesses job data and system message
  - Updates job status and progress
  - Maintains query state

- **LLMInterface**:
  - Provides message history for processing
  - Handles query responses
  - Manages conversation context

## Thread Structure

Each thread maintains the following information:

```json
{
    "id": "thread-uuid",
    "created_at": "2024-03-20T12:00:00Z",
    "messages": [
        {
            "role": "developer",
            "content": "system_message",
            "timestamp": "2024-03-20T12:00:00Z",
            "token_count": 100
        },
        {
            "role": "user",
            "content": "query_text",
            "timestamp": "2024-03-20T12:01:00Z",
            "token_count": 50
        },
        {
            "role": "assistant",
            "content": "response_text",
            "timestamp": "2024-03-20T12:02:00Z",
            "token_count": 200
        }
    ],
    "token_count": 350,
    "status": "complete",
    "last_response_id": "response-uuid",
    "error": null
}
```

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

- Context window management ensures efficient token usage
- Message history trimming prevents excessive memory usage
- Token counting helps track and optimize context usage
- Thread status tracking enables efficient progress monitoring

## Query Structure

From what we've seen in other parts of the system, queries have the following structure:

```json
{
  "Alias": "Query Name",
  "Text": "What is the main conclusion?",
  "Format": "free-form"
}
```

Where:
- `Alias` is a user-friendly name for the query
- `Text` is the actual query text sent to the LLM
- `Format` specifies how the response should be structured

## Future Enhancements

Potential enhancements to the Query Manager could include:

- Methods for validating query formats
- Functions for transforming queries into optimal prompts
- Support for query templates and presets
- Query categorization and organization

## Notes

The minimal implementation suggests that query management in the current system is relatively straightforward, with most of the query-related logic potentially handled by the Data Extractor or other components. 