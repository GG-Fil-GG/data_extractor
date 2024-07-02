import requests
import logging
from functools import wraps

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
    def __init__(self, api_key, model="gpt-4o", temperature=0.0):
        self.api_key = api_key
        self.url = "https://api.openai.com/v1/chat/completions"
        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        self.model = model
        self.temperature = temperature

    @handle_errors
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

        logging.debug(f"OpenAI API request payload: {data}")

        response = self._make_request(data)
        
        logging.debug(f"OpenAI API response: {response}")

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
            except ValueError as ve:
                logging.error(f"ValueError in ask: {ve}")
                return "Not available"
            except Exception as e:
                logging.error(f"Error in ask: {e}")
                return "Not available"
        else:
            return response

    def _make_request(self, data):
        response = requests.post(self.url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']