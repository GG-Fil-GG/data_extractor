import re
from datetime import datetime
from langchain_core.output_parsers import JsonOutputParser

class IntegerOutputParser:
    def parse(self, text: str) -> int:
        match = re.search(r'-?\d+', text)
        if match:
            return int(match.group(0))
        else:
            raise ValueError(f"Could not parse integer from text: {text}")

class FloatingPointOutputParser:
    def parse(self, text: str) -> float:
        match = re.search(r'-?\d+\.\d+', text)
        if match:
            return float(match.group(0))
        else:
            raise ValueError(f"Could not parse floating-point number from text: {text}")

def comma_separated_list_parser(text):
    items = [item.strip() for item in text.split(",")]
    return ", ".join(items)

def date_parser(text):
    try:
        match = re.search(r'(\d{2}-\d{2}-\d{4})', text)
        if match:
            return datetime.strptime(match.group(0), "%d-%m-%Y").date()
        else:
            raise ValueError(f"Could not parse date from text: {text}")
    except ValueError as e:
        return "Not available"

class YesNoOutputParser:
    def parse(self, text: str) -> str:
        text = text.strip().lower().rstrip(".")
        if text in ["yes", "no"]:
            return text.capitalize()
        else:
            raise ValueError(f"Could not parse yes/no from text: {text}")

class Median95CIOutputParser:
    def parse(self, text: str):
        data = JsonOutputParser(schema={
            "type": "object",
            "properties": {
                "median": {"type": "number"},
                "ci_lower": {"type": "number"},
                "ci_upper": {"type": "number"}
            },
            "required": ["median"]
        }).parse(text)
        median = data.get("median", "Not available")
        ci_lower = data.get("ci_lower", "Not available")
        ci_upper = data.get("ci_upper", "Not available")
        return f"{median} ({ci_lower} - {ci_upper})"

class MeanSDOutputParser:
    def parse(self, text: str):
        data = JsonOutputParser(schema={
            "type": "object",
            "properties": {
                "mean": {"type": "number"},
                "sd": {"type": "number"}
            },
            "required": ["mean"]
        }).parse(text)
        mean = data.get("mean", "Not available")
        sd = data.get("sd", "Not available")
        return f"{mean} (SD: {sd})"

class MeanSEOutputParser:
    def parse(self, text: str):
        data = JsonOutputParser(schema={
            "type": "object",
            "properties": {
                "mean": {"type": "number"},
                "se": {"type": "number"}
            },
            "required": ["mean"]
        }).parse(text)
        mean = data.get("mean", "Not available")
        se = data.get("se", "Not available")
        return f"{mean} (SE: {se})"

class RangeOutputParser:
    def parse(self, text: str):
        data = JsonOutputParser(schema={
            "type": "object",
            "properties": {
                "range_min": {"type": "number"},
                "range_max": {"type": "number"}
            },
            "required": ["range_min", "range_max"]
        }).parse(text)
        range_min = data.get("range_min", "Not available")
        range_max = data.get("range_max", "Not available")
        return f"{range_min} - {range_max}"

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
