import requests
import logging
import tiktoken
from functools import wraps
from typing import Dict, List, Optional, Union, Any
import time
from datetime import datetime
from backend.app.services import parsers

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

class LLMInterface:
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

    def _get_openai_config(self) -> Dict:
        """Get OpenAI configuration from job data."""
        return self.job_manager.job_data.get("openai_config", {
            "model": "gpt-4o",
            "temperature": 0.0,
            "max_tokens": None
        })

    def _get_response_format(self, format_type: str) -> Optional[Dict]:
        """Get OpenAI response format based on query format type."""
        format_mapping = {
            "free_form": None,
            "integer": {"type": "json_object", "schema": {"type": "integer"}},
            "floating_point_number": {"type": "json_object", "schema": {"type": "number"}},
            "comma_separated_list": {"type": "json_object", "schema": {"type": "array", "items": {"type": "string"}}},
            "yes_no": {"type": "json_object", "schema": {"type": "boolean"}},
            "date_dd_mm_yyyy": {"type": "json_object", "schema": {"type": "string", "pattern": "^\\d{2}/\\d{2}/\\d{4}$"}},
            "median_95ci": {"type": "json_object", "schema": {
                "type": "object",
                "properties": {
                    "median": {"type": "number"},
                    "ci_lower": {"type": "number"},
                    "ci_upper": {"type": "number"}
                },
                "required": ["median"]
            }},
            "mean_sd": {"type": "json_object", "schema": {
                "type": "object",
                "properties": {
                    "mean": {"type": "number"},
                    "sd": {"type": "number"}
                },
                "required": ["mean"]
            }},
            "mean_se": {"type": "json_object", "schema": {
                "type": "object",
                "properties": {
                    "mean": {"type": "number"},
                    "se": {"type": "number"}
                },
                "required": ["mean"]
            }},
            "range": {"type": "json_object", "schema": {
                "type": "object",
                "properties": {
                    "range_min": {"type": "number"},
                    "range_max": {"type": "number"}
                },
                "required": ["range_min", "range_max"]
            }}
        }
        return format_mapping.get(format_type)

    def _count_tokens(self, messages: List[Dict]) -> int:
        """Count tokens in a list of messages."""
        return sum(len(self.encoding.encode(msg["content"])) for msg in messages)

    def _validate_context_window(self, messages: List[Dict]) -> bool:
        """Validate that messages fit within context window."""
        config = self._get_openai_config()
        max_tokens = config.get("max_tokens", 128000)
        return self._count_tokens(messages) <= max_tokens

    @handle_errors
    def process_messages(self, messages: List[Dict], format_type: str = "free_form") -> Any:
        """
        Process a list of messages through the OpenAI API.
        
        Args:
            messages: List of message dictionaries with role and content
            format_type: Type of response format expected
            
        Returns:
            Processed response in the appropriate format
        """
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

    def _make_request_with_retry(self, data: Dict) -> str:
        """
        Make API request with retry logic and rate limiting.
        
        Args:
            data: Request payload
            
        Returns:
            str: API response content
        """
        retry_count = 0
        last_error = None

        while retry_count < self.max_retries:
            try:
                # Implement rate limiting
                time.sleep(self.rate_limit_delay)
                
                response = requests.post(
                    self.url,
                    headers=self.headers,
                    json=data
                )
                response.raise_for_status()
                
                return response.json()['choices'][0]['message']['content']
                
            except requests.exceptions.RequestException as e:
                last_error = e
                retry_count += 1
                
                if retry_count < self.max_retries:
                    logging.warning(f"API request failed, retrying ({retry_count}/{self.max_retries}): {e}")
                    time.sleep(self.retry_delay * retry_count)  # Exponential backoff
                else:
                    logging.error(f"API request failed after {self.max_retries} retries: {e}")
                    raise

    def cleanup(self):
        """Clean up any resources used by the interface."""
        # Currently no cleanup needed, but method is available for future use
        pass