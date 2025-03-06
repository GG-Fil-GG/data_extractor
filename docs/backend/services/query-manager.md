# Query Manager

## Overview

The Query Manager is a service component in the DataExtractor backend that manages extraction queries. It serves as a container for query-related data and provides a reference point for other components that need to access query information.

## Class Structure

The `QueryManager` class is defined in `backend/app/services/query_manager.py` and has a minimal implementation:

```python
class QueryManager:
    def __init__(self, job_manager):
        self.job_manager = job_manager
```

## Responsibilities

While the Query Manager has a minimal implementation, its conceptual responsibilities in the system include:

- Storing references to extraction queries
- Providing access to query data for other components
- Maintaining the relationship between queries and the job manager

## Integration with Other Services

The Query Manager integrates with:

- **Job Manager**: Receives job data that contains query information
- **Data Extractor**: Provides query information for extraction processing

## Data Flow

Based on the system architecture:

1. Queries are defined by the user in the frontend
2. The frontend sends these queries to the backend as part of the extraction request
3. The Job Manager stores these queries in the job data
4. The Query Manager provides a reference to these queries for other components

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