# LLM Interface

## Overview

The LLM Interface is a core service that manages communication with OpenAI's language models. It provides a standardized way to process thread-based conversations, handle response formats, and manage API interactions with proper error handling and retries.

## Responsibilities

- Managing thread-based conversations with OpenAI's API
- Handling response formats and parsing
- Managing context windows and token limits
- Implementing robust error handling and retries
- Rate limiting and backoff strategies

## Class Structure

The `LLMInterface` class is defined in `backend/app/services/llm_interface.py` and serves as the bridge between the application and OpenAI's language models.

### Initialization

```python
def __init__(self, api_key: str, job_manager):
    self.api_key = api_key
    self.job_manager = job_manager
    self.url = "https://api.openai.com/v1/chat/completions"
    self.headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.api_key}"
    }
    self.encoding = tiktoken.get_encoding("cl100k_base")
    self.max_retries = 3
    self.retry_delay = 5  # seconds
    self.rate_limit_delay = 1  # seconds between requests
```

The LLM Interface is initialized with:
- An OpenAI API key for authentication
- A reference to the Job Manager for configuration
- Tokenizer for context window management
- Retry and rate limiting settings

## Key Methods

### process_messages()

Processes a list of messages through the OpenAI API and returns the parsed response.

```python
def process_messages(self, messages: List[Dict], format_type: str = "free_form") -> Any:
    if not self._validate_context_window(messages):
        raise ValueError("Messages exceed context window limit")

    config = self._get_openai_config()
    response_format = self._get_response_format(format_type)

    # Add format guidance if needed
    if format_type in parsers.parsers and parsers.parsers[format_type]["format_guidance"]:
        messages.append({
            "role": "user",
            "content": parsers.parsers[format_type]["format_guidance"]
        })

    data = {
        "model": config["model"],
        "messages": messages,
        "temperature": config["temperature"]
    }

    if response_format:
        data["response_format"] = response_format
    if config.get("max_tokens"):
        data["max_tokens"] = config["max_tokens"]

    # Get raw response from API
    raw_response = self._make_request_with_retry(data)

    # Parse response using appropriate parser
    if format_type in parsers.parsers:
        parser = parsers.parsers[format_type]["parser"]
        if parser:
            try:
                return parser.parse(raw_response)
            except Exception as e:
                logging.error(f"Failed to parse response for format {format_type}: {e}")
                raise ValueError(f"Invalid response format for {format_type}")
    
    return raw_response
```

This method:
1. Validates the context window size
2. Gets OpenAI configuration from job data
3. Adds format guidance if needed
4. Configures the API request with model settings
5. Sends the request with retry logic
6. Parses the response using the appropriate parser

### _make_request_with_retry()

Makes the API request with retry logic and rate limiting.

```python
def _make_request_with_retry(self, data: Dict) -> str:
    retry_count = 0
    last_error = None

    while retry_count < self.max_retries:
        try:
            time.sleep(self.rate_limit_delay)
            response = requests.post(self.url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            last_error = e
            retry_count += 1
            if retry_count < self.max_retries:
                time.sleep(self.retry_delay * retry_count)
            else:
                raise
```

This method:
1. Implements rate limiting between requests
2. Handles API errors with exponential backoff
3. Retries failed requests up to the maximum retry count
4. Returns the processed response content

## Response Format Handling

The interface supports multiple response formats through the `_get_response_format()` method:

```python
def _get_response_format(self, format_type: str) -> Optional[Dict]:
    format_mapping = {
        "free_form": None,
        "integer": {"type": "json_object", "schema": {"type": "integer"}},
        "floating_point_number": {"type": "json_object", "schema": {"type": "number"}},
        "comma_separated_list": {"type": "json_object", "schema": {"type": "array", "items": {"type": "string"}}},
        "yes_no": {"type": "json_object", "schema": {"type": "boolean"}},
        "date_dd_mm_yyyy": {"type": "json_object", "schema": {"type": "string", "pattern": "^\\d{2}/\\d{2}/\\d{4}$"}},
        "median_95ci": {"type": "json_object", "schema": {...}},
        "mean_sd": {"type": "json_object", "schema": {...}},
        "mean_se": {"type": "json_object", "schema": {...}},
        "range": {"type": "json_object", "schema": {...}}
    }
    return format_mapping.get(format_type)
```

## Context Window Management

The interface manages context windows through token counting:

```python
def _count_tokens(self, messages: List[Dict]) -> int:
    return sum(len(self.encoding.encode(msg["content"])) for msg in messages)

def _validate_context_window(self, messages: List[Dict]) -> bool:
    config = self._get_openai_config()
    max_tokens = config.get("max_tokens", 128000)
    return self._count_tokens(messages) <= max_tokens
```

## Error Handling

The LLM Interface uses multiple layers of error handling:

1. **Method-level error handling** through the `handle_errors` decorator
2. **API request retries** with exponential backoff
3. **Response parsing validation** with specific error messages
4. **Context window validation** to prevent oversized requests

## Integration with Other Services

The LLM Interface integrates with:

- **Job Manager**: 
  - Accesses OpenAI configuration
  - Updates job status and progress
  - Maintains API settings

- **Query Manager**:
  - Processes thread-based conversations
  - Handles message history
  - Manages context windows

- **Parsers**:
  - Uses format-specific parsers
  - Applies format guidance
  - Validates response formats

## OpenAI API Configuration

Configuration is managed through the job data structure:

```json
{
    "openai_config": {
        "model": "gpt-4o",
        "assistant_id": "string",
        "max_tokens": "integer",
        "temperature": "number",
        "file_purpose": "string"
    }
}
```

## Performance Considerations

- **Rate Limiting**: Implements delays between requests
- **Retry Logic**: Uses exponential backoff for failed requests
- **Token Management**: Validates context window sizes
- **Response Parsing**: Uses efficient parser implementations
- **Error Handling**: Graceful degradation on failures

## Example Flow

1. Query Manager prepares a thread with messages
2. LLM Interface validates context window size
3. Interface adds format guidance if needed
4. Request is sent to OpenAI with retry logic
5. Response is parsed using the appropriate parser
6. Parsed result is returned to the Query Manager 