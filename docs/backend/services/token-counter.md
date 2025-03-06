# Token Counter

## Overview

The Token Counter is a utility service that counts the number of tokens in a text string. This is important for managing API costs and ensuring that text sent to the language model doesn't exceed token limits. The service uses the tiktoken library from OpenAI to perform accurate token counting.

## Responsibilities

- Counting tokens in text strings
- Using the appropriate tokenizer for the selected model
- Providing token count information to other components

## Module Structure

The `token_counter.py` module is defined in `backend/app/services/token_counter.py` and provides a simple function for token counting.

```python
import tiktoken

def count_tokens(text):
    # Initialize the tokenizer for the model you are using
    tokenizer = tiktoken.get_encoding("o200k_base") 

    # Encode the text to get the tokens
    tokens = tokenizer.encode(text)

    # Return the number of tokens
    return len(tokens)
```

## Token Counting Process

The token counting process is straightforward:

1. Initialize the tokenizer for the specific model (in this case, "o200k_base")
2. Encode the text using the tokenizer to get the tokens
3. Return the count of tokens

## Integration with Other Services

The Token Counter can be integrated with:

- **Document Handler**: To count tokens in document text
- **LLM Interface**: To ensure requests don't exceed token limits
- **Data Extractor**: To manage token usage across multiple queries

## Example Usage

```python
from app.services.token_counter import count_tokens

# Count tokens in a document
document_text = "This is a sample document text."
token_count = count_tokens(document_text)
print(f"Document contains {token_count} tokens")

# Check if a text exceeds token limits
max_tokens = 8192
if count_tokens(document_text) > max_tokens:
    print("Document exceeds token limit")
else:
    print("Document is within token limit")
```

## Token Limits

Different OpenAI models have different token limits:

| Model | Token Limit |
|-------|-------------|
| gpt-3.5-turbo | 16,385 tokens |
| gpt-4 | 8,192 tokens |
| gpt-4o | 128,000 tokens |

The token counter helps ensure that text sent to these models doesn't exceed these limits.

## Performance Considerations

- Token counting is a lightweight operation
- For very large documents, token counting can help identify if the document needs to be chunked
- The "o200k_base" tokenizer is appropriate for the latest OpenAI models

## Future Enhancements

Potential enhancements to the Token Counter include:

1. **Model-specific tokenizers**: Dynamically select the tokenizer based on the model being used
2. **Token optimization**: Suggest ways to reduce token count while preserving meaning
3. **Cost estimation**: Estimate API costs based on token count
4. **Chunking strategies**: Provide strategies for chunking large documents 