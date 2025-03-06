# Parsers

## Overview

The Parsers module provides a collection of specialized parsers that transform raw text responses from the language model into structured formats. These parsers ensure that extraction results are consistently formatted and validated according to the query's expected response type.

## Responsibilities

- Converting raw text responses into structured formats
- Validating response formats
- Providing format guidance for the language model
- Supporting various data types (numbers, dates, lists, etc.)
- Handling parsing errors gracefully

## Module Structure

The `parsers.py` module is defined in `backend/app/services/parsers.py` and contains:

1. Parser classes for different data types
2. Function-based parsers for simpler formats
3. A dictionary mapping format names to parser configurations

## Parser Types

### Class-Based Parsers

These parsers are implemented as classes with a `parse` method:

#### IntegerOutputParser

Extracts integer values from text.

```python
class IntegerOutputParser:
    def parse(self, text: str) -> int:
        match = re.search(r'-?\d+', text)
        if match:
            return int(match.group(0))
        else:
            raise ValueError(f"Could not parse integer from text: {text}")
```

#### FloatingPointOutputParser

Extracts floating-point numbers from text.

```python
class FloatingPointOutputParser:
    def parse(self, text: str) -> float:
        match = re.search(r'-?\d+\.\d+', text)
        if match:
            return float(match.group(0))
        else:
            raise ValueError(f"Could not parse floating-point number from text: {text}")
```

#### YesNoOutputParser

Extracts and normalizes yes/no responses.

```python
class YesNoOutputParser:
    def parse(self, text: str) -> str:
        text = text.strip().lower().rstrip(".")
        if text in ["yes", "no"]:
            return text.capitalize()
        else:
            raise ValueError(f"Could not parse yes/no from text: {text}")
```

#### Statistical Parsers

Several parsers handle statistical formats using JSON parsing:

- **Median95CIOutputParser**: Extracts median with 95% confidence intervals
- **MeanSDOutputParser**: Extracts mean with standard deviation
- **MeanSEOutputParser**: Extracts mean with standard error
- **RangeOutputParser**: Extracts minimum and maximum values

### Function-Based Parsers

These parsers are implemented as simple functions:

#### comma_separated_list_parser

Normalizes comma-separated lists.

```python
def comma_separated_list_parser(text):
    items = [item.strip() for item in text.split(",")]
    return ", ".join(items)
```

#### date_parser

Extracts and validates dates in DD-MM-YYYY format.

```python
def date_parser(text):
    try:
        match = re.search(r'(\d{2}-\d{2}-\d{4})', text)
        if match:
            return datetime.strptime(match.group(0), "%d-%m-%Y").date()
        else:
            raise ValueError(f"Could not parse date from text: {text}")
    except ValueError as e:
        return "Not available"
```

## Parser Registry

The module defines a `parsers` dictionary that maps format names to parser configurations:

```python
parsers = {
    "free-form": {"parser": None, "json_required": False, "format_guidance": ""},
    "integer": {"parser": IntegerOutputParser(), "json_required": False, "format_guidance": "Please provide your answer as an integer."},
    "floating-point number": {"parser": FloatingPointOutputParser(), "json_required": False, "format_guidance": "Please provide your answer as a floating-point number."},
    "comma-separated list": {"parser": comma_separated_list_parser, "json_required": False, "format_guidance": "Please provide your answer as a comma-separated list."},
    "yes/no": {"parser": YesNoOutputParser(), "json_required": False, "format_guidance": "Please provide your answer as yes or no."},
    "median (95% CI)": {"parser": Median95CIOutputParser(), "json_required": True, "format_guidance": "Please provide your answer as a JSON object with the following keys: 'median' for median, 'ci_lower' for the lower confidence interval boundary, and 'ci_upper' for the upper confidence interval boundary."},
    "mean (SD)": {"parser": MeanSDOutputParser(), "json_required": True, "format_guidance": "Please provide your answer as a JSON object with the following keys: 'mean' for mean and 'sd' for standard deviation."},
    "mean (SE)": {"parser": MeanSEOutputParser(), "json_required": True, "format_guidance": "Please provide your answer as a JSON object with the following keys: 'mean' for mean and 'se' for standard error."},
    "range": {"parser": RangeOutputParser(), "json_required": True, "format_guidance": "Please provide your answer as a JSON object with the following keys: 'range_min' for the minimum and 'range_max' for the maximum."},
    "date (DD-MM-YYYY)": {"parser": date_parser, "json_required": False, "format_guidance": "Please provide your answer as a date in the format DD-MM-YYYY."}
}
```

Each entry in the dictionary contains:
- **parser**: The parser object or function
- **json_required**: Whether the response should be in JSON format
- **format_guidance**: Instructions for the language model on how to format the response

## Supported Formats

| Format Name | Description | JSON Required | Example Output |
|-------------|-------------|--------------|----------------|
| free-form | Unstructured text | No | Any text |
| integer | Whole number | No | 42 |
| floating-point number | Decimal number | No | 3.14 |
| comma-separated list | List of items | No | item1, item2, item3 |
| yes/no | Boolean response | No | Yes or No |
| median (95% CI) | Statistical measure | Yes | 10.5 (9.2 - 11.8) |
| mean (SD) | Statistical measure | Yes | 15.3 (SD: 2.1) |
| mean (SE) | Statistical measure | Yes | 15.3 (SE: 0.5) |
| range | Min-max values | Yes | 5 - 10 |
| date (DD-MM-YYYY) | Date format | No | 01-01-2023 |

## Integration with Other Services

The Parsers module integrates with:

- **Data Extractor**: Uses parsers to format responses
- **LLM Interface**: Uses format guidance to instruct the language model
- **Query Manager**: Indirectly through query format specifications

## JSON Parsing

For complex statistical formats, the module uses the `JsonOutputParser` from LangChain:

```python
from langchain_core.output_parsers import JsonOutputParser

# Example usage
data = JsonOutputParser(schema={
    "type": "object",
    "properties": {
        "mean": {"type": "number"},
        "sd": {"type": "number"}
    },
    "required": ["mean"]
}).parse(text)
```

This ensures that JSON responses are properly validated against a schema.

## Error Handling

Most parsers include error handling:

1. **Class-based parsers**: Raise `ValueError` when parsing fails
2. **Function-based parsers**: May return "Not available" on failure
3. **JSON parsers**: Use schema validation to ensure correct structure

The Data Extractor handles these errors and provides fallback responses when necessary.

## Example Usage

```python
# Get parser configuration for a query format
query_format = "mean (SD)"
parser_entry = parsers.get(query_format)
parser = parser_entry["parser"]
json_required = parser_entry["json_required"]
format_guidance = parser_entry["format_guidance"]

# Use the parser to process a response
try:
    parsed_response = parser.parse("The mean is 15.3 with a standard deviation of 2.1")
    # Result: "15.3 (SD: 2.1)"
except ValueError:
    parsed_response = "Not available"
```

## Extending with New Parsers

To add a new parser:

1. Create a new parser class or function
2. Add an entry to the `parsers` dictionary with:
   - The parser object or function
   - Whether JSON is required
   - Format guidance for the language model 