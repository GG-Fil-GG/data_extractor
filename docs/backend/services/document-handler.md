# Document Handler

## Overview

The Document Handler is a core service responsible for processing different document types and extracting their text content. It supports multiple file formats including PDF, DOCX, and TXT files, and provides a unified interface for text extraction regardless of the source format.

## Responsibilities

- Extracting text from different file formats (PDF, DOCX, TXT)
- Cleaning and preprocessing text for optimal extraction
- Managing document metadata
- Handling encoding issues during text extraction

## Class Structure

The `DocumentHandler` class is defined in `backend/app/services/document_handler.py` and works closely with the Job Manager to process documents as part of the extraction workflow.

### Initialization

```python
def __init__(self, job_manager):
    self.job_manager = job_manager
```

The Document Handler is initialized with a reference to the Job Manager, which provides access to job data and status updates.

## Key Methods

### process_documents()

Processes all documents in the current job, extracting text from each file and saving it as a text file for further processing.

```python
def process_documents(self):
    temp_dir = self.job_manager.job_data["Temp Dir"]
    for document in self.job_manager.job_data["Documents"]:
        path = document["Path"]
        alias = os.path.splitext(document["Alias"])[0]
        ext = document["Ext"]
        text = self.extract_text_from_file(path, ext)
        cleaned_text = self.clean_text(text)
        txt_path = os.path.join(temp_dir, alias + '.txt')
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(cleaned_text)
        document["Path"] = txt_path
    self.job_manager.update_status("Documents Processed")
```

This method:
1. Gets the temporary directory from the job data
2. Iterates through each document in the job
3. Extracts text from the document using the appropriate parser
4. Cleans the extracted text
5. Saves the cleaned text to a new text file
6. Updates the document's path to point to the new text file
7. Updates the job status

### extract_text_from_file()

Extracts text from a file based on its extension.

```python
def extract_text_from_file(self, path, ext):
    parse_methods = {
        '.pdf': self.parse_pdf,
        '.docx': self.parse_docx,
        '.txt': self.parse_txt
    }
    if f".{ext}" in parse_methods:
        return parse_methods[f".{ext}"](path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
```

This method:
1. Maps file extensions to their respective parsing methods
2. Calls the appropriate parsing method based on the file extension
3. Raises an error if the file extension is not supported

### File-Specific Parsers

#### parse_txt()

Extracts text from a plain text file.

```python
def parse_txt(self, path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()
```

#### parse_docx()

Extracts text from a Microsoft Word document.

```python
def parse_docx(self, path):
    doc = Document(path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])
```

#### parse_pdf()

Extracts text from a PDF document.

```python
def parse_pdf(self, file_path):
    text = ""
    document = fitz.open(file_path)
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text
```

### Text Processing

#### clean_text()

Cleans the extracted text by removing non-printable characters.

```python
def clean_text(self, text):
    text = re.sub(r'[^\x20-\x7E]+', ' ', text)
    return text
```

### Utility Methods

#### load_text()

Loads text from a file with fallback encoding support.

```python
def load_text(self, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        logging.warning(f"UTF-8 decoding failed for {file_path}, trying ISO-8859-1 encoding")
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            return file.read()
```

## Error Handling

The Document Handler uses a decorator pattern for error handling:

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

## Integration with Other Services

The Document Handler integrates with:

- **Job Manager**: Receives job data and updates job status
- **Data Extractor**: Provides processed text for extraction
- **Token Counter**: Indirectly supports token counting through text extraction

## Supported File Types

| File Type | Extension | Library Used |
|-----------|-----------|-------------|
| PDF | .pdf | PyMuPDF (fitz) |
| Microsoft Word | .docx | python-docx |
| Plain Text | .txt | Built-in Python file handling |

## Example Flow

1. User uploads documents through the frontend
2. Backend receives the documents and creates a job
3. Document Handler processes each document:
   - Extracts text using the appropriate parser
   - Cleans the text to remove non-printable characters
   - Saves the processed text to a temporary file
4. The processed text files are used for subsequent extraction steps

## Performance Considerations

- PDF parsing can be memory-intensive for large documents
- Text cleaning helps reduce token count and improve extraction quality
- Fallback encoding support ensures compatibility with various text encodings 