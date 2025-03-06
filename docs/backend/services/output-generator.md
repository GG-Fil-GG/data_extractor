# Output Generator

## Overview

The Output Generator is responsible for creating the final output files from the extraction results. It supports multiple output formats (CSV and DOCX) and different data orientations, providing flexibility in how extraction results are presented to the user.

## Responsibilities

- Generating output files in different formats (CSV, DOCX)
- Supporting different data orientations (document-row, query-row)
- Ensuring output directories exist
- Formatting extraction results for readability
- Handling errors during output generation

## Class Structure

The `OutputGenerator` class is defined in `backend/app/services/output_generator.py` and works with the Job Manager to access extraction results.

### Initialization

```python
def __init__(self, job_manager):
    self.job_manager = job_manager
```

The Output Generator is initialized with a reference to the Job Manager, which provides access to job data including extraction results.

## Key Methods

### generate_output()

The main method that generates the output file based on the job configuration.

```python
def generate_output(self):
    job_data = self.job_manager.get_job_data()
    job_id = job_data["Job ID"]
    output_format = job_data["Export Format"]
    temp_dir = job_data["Temp Dir"]
    output_path = os.path.join(temp_dir, f'{job_id}.{output_format}')
    
    self.ensure_output_directory_exists(output_path)
    
    if output_format == 'csv':
        self.generate_csv(output_path)
    elif output_format == 'docx':
        self.generate_docx(output_path)
    else:
        raise ValueError("Unrecognized output format specified. Use 'csv' or 'docx'.")
```

This method:
1. Gets the job data from the Job Manager
2. Determines the output format and path
3. Ensures the output directory exists
4. Calls the appropriate generator method based on the format
5. Raises an error for unsupported formats

### ensure_output_directory_exists()

Creates the output directory if it doesn't exist.

```python
def ensure_output_directory_exists(self, output_path):
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Output directory ensured: {output_dir}")
```

### generate_csv()

Generates a CSV file from the extraction results.

```python
def generate_csv(self, output_path):
    headers, rows = [], []
    job_data = self.job_manager.get_job_data()
    orientation = job_data["Orientation"]

    if orientation == "doc_row":
        headers = ["Documents"] + [q["Alias"] for q in job_data["Queries"]]
        for doc_alias, responses in job_data["Responses"].items():
            row = [doc_alias] + [responses.get(q["Alias"], "") for q in job_data["Queries"]]
            rows.append(row)
    elif orientation == "query_row":
        headers = ["Queries"] + [d["Alias"] for d in job_data["Documents"]]
        for query in job_data["Queries"]:
            row = [query["Alias"]]
            for doc in job_data["Documents"]:
                response = job_data["Responses"].get(doc["Alias"], {}).get(query["Alias"], "")
                row.append(response)
            rows.append(row)
    else:
        raise ValueError("Unrecognized orientation specified.")

    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(rows)
    self.job_manager.update_status("CSV Output Generated")
    logging.info("CSV output generated successfully.")
```

This method:
1. Creates headers and rows based on the orientation
2. For document-row orientation:
   - Headers are document name followed by query names
   - Each row represents a document with responses to all queries
3. For query-row orientation:
   - Headers are query name followed by document names
   - Each row represents a query with responses from all documents
4. Writes the data to a CSV file
5. Updates the job status

### generate_docx()

Generates a Microsoft Word document from the extraction results.

```python
def generate_docx(self, output_path):
    job_data = self.job_manager.get_job_data()
    doc = Document()
    orientation = job_data["Orientation"]

    if orientation == "doc_row":
        for query in job_data["Queries"]:
            doc.add_heading(query["Alias"], level=2)
            for doc_alias, responses in job_data["Responses"].items():
                response = responses.get(query["Alias"], "")
                doc.add_paragraph(f"{doc_alias}: {response}")
    elif orientation == "query_row":
        for doc_info in job_data["Documents"]:
            doc_alias = doc_info["Alias"]
            doc.add_heading(doc_alias, level=2)
            for query in job_data["Queries"]:
                response = job_data["Responses"].get(doc_alias, {}).get(query["Alias"], "")
                doc.add_paragraph(f"{query['Alias']}: {response}")
    else:
        raise ValueError("Unrecognized orientation specified.")

    doc.save(output_path)
    self.job_manager.update_status("DOCX Output Generated")
    logging.info("DOCX output generated successfully.")
```

This method:
1. Creates a new Word document
2. For document-row orientation:
   - Creates a heading for each query
   - Under each query, lists responses from all documents
3. For query-row orientation:
   - Creates a heading for each document
   - Under each document, lists responses to all queries
4. Saves the document to the specified path
5. Updates the job status

## Error Handling

The Output Generator uses a decorator pattern for error handling:

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

## Supported Output Formats

| Format | File Extension | Library Used |
|--------|---------------|-------------|
| CSV | .csv | Built-in Python csv module |
| Microsoft Word | .docx | python-docx |

## Data Orientations

The Output Generator supports two data orientations:

### Document-Row Orientation (`doc_row`)

- Each row (or section) represents a document
- Columns (or subsections) represent queries
- Best for comparing different documents across the same queries

Example CSV:
```
Documents,Query1,Query2,Query3
Document1,Response1,Response2,Response3
Document2,Response1,Response2,Response3
```

### Query-Row Orientation (`query_row`)

- Each row (or section) represents a query
- Columns (or subsections) represent documents
- Best for comparing different queries across the same documents

Example CSV:
```
Queries,Document1,Document2
Query1,Response1,Response1
Query2,Response2,Response2
```

## Integration with Other Services

The Output Generator integrates with:

- **Job Manager**: Accesses job data and updates job status
- **Data Extractor**: Indirectly through the job data

## Output File Naming

Output files are named using the job ID and the appropriate extension:
- `{job_id}.csv` for CSV files
- `{job_id}.docx` for DOCX files

## Example Flow

1. User requests extraction results download
2. Backend routes the request to the Output Generator
3. Output Generator determines the format and orientation from job data
4. Output Generator creates the appropriate file
5. Backend provides a download URL for the generated file

## Performance Considerations

- CSV generation is generally faster than DOCX generation
- Large numbers of documents or queries may result in larger file sizes
- The output generation process is synchronous and may take time for large datasets 