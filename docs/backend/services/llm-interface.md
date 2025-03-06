# LLM Interface

## Overview

The LLM Interface is a core service that manages communication with OpenAI's language models. It provides a standardized way to send queries to the AI model and process the responses, handling error conditions and formatting requirements.

## Responsibilities

- Communicating with OpenAI's API
- Formatting prompts for optimal extraction
- Handling API errors and retries
- Processing and parsing AI responses

## Class Structure

The `LLMInterface` class is defined in `backend/app/services/llm_interface.py` and serves as the bridge between the application and OpenAI's language models.

### Initialization

```python
def __init__(self, api_key, model="gpt-4o", temperature=0.0):
    self.api_key = api_key
    self.url = "https://api.openai.com/v1/chat/completions"
    self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
    self.model = model
    self.temperature = temperature
```

The LLM Interface is initialized with:
- An OpenAI API key for authentication
- A model identifier (default: "gpt-4o")
- A temperature setting for controlling randomness (default: 0.0 for deterministic responses)

## Key Methods

### ask()

Sends a query to the OpenAI API and processes the response.

```python
def ask(self, query, context, parser, format_guidance_message=None, response_format=None):
    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": query}
    ]

    if format_guidance_message:
        messages.append({"role": "user", "content": format_guidance_message})

    data = {
        "model": self.model,
        "messages": messages,
        "temperature": self.temperature
    }

    if response_format:
        data["response_format"] = response_format

    response = self._make_request(data)
    
    if parser:
        try:
            if callable(parser):
                parsed_response = parser(response)
            elif hasattr(parser, 'parse'):
                parsed_response = parser.parse(response)
            else:
                raise ValueError("Invalid parser provided.")

            if parsed_response is None or parsed_response == "":
                raise ValueError("Parsed response is invalid or empty")

            return parsed_response
        except Exception as e:
            logging.error(f"Error in ask: {e}")
            return "Not available"
    else:
        return response
```

This method:
1. Constructs a message array with system context and user query
2. Adds format guidance if provided
3. Configures the API request with model and temperature settings
4. Sends the request to the OpenAI API
5. Processes the response using the provided parser
6. Handles parsing errors gracefully

### _make_request()

Makes the actual HTTP request to the OpenAI API.

```python
def _make_request(self, data):
    response = requests.post(self.url, headers=self.headers, json=data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']
```

This method:
1. Sends a POST request to the OpenAI API
2. Raises an exception if the request fails
3. Extracts and returns the message content from the response

## Error Handling

The LLM Interface uses a decorator pattern for error handling:

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

Additionally, the `ask()` method includes specific error handling for parsing responses:
- Validates that the parser is either callable or has a `parse` method
- Checks that the parsed response is not empty
- Returns "Not available" if parsing fails

## Integration with Other Services

The LLM Interface integrates with:

- **Data Extractor**: Receives queries and context for extraction
- **Parsers**: Uses parsers to format and validate responses
- **Query Manager**: Works with query formats to structure prompts

## OpenAI API Configuration

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| model | "gpt-4o" | The OpenAI model to use for extraction |
| temperature | 0.0 | Controls randomness (0.0 = deterministic) |
| url | "https://api.openai.com/v1/chat/completions" | The API endpoint |

## Message Structure

The interface uses OpenAI's chat completion format:

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "Context information..."},
    {"role": "user", "content": "Query text..."},
    {"role": "user", "content": "Format guidance..." }
  ],
  "temperature": 0.0
}
```

## Response Parsing

The interface supports two types of parsers:
1. **Function parsers**: Simple functions that take a string and return a parsed result
2. **Object parsers**: Objects with a `parse` method that processes the response

If parsing fails, the interface returns "Not available" rather than raising an exception, ensuring robustness in the extraction process.

## Example Flow

1. Data Extractor prepares a query and context
2. LLM Interface sends the query to OpenAI's API
3. OpenAI processes the query and returns a response
4. LLM Interface parses the response using the provided parser
5. Parsed result is returned to the Data Extractor

## Performance Considerations

- API calls are synchronous and may take time to complete
- Error handling ensures the application remains responsive even if API calls fail
- The temperature setting of 0.0 ensures consistent responses for the same input 