# Job Data Structure

## Overview

The `job_data` object is the central data structure that maintains the state and configuration of each extraction job. It is managed by the JobManager service and is used throughout the application to coordinate the extraction process.

## Structure

```json
{
    "job_id": "string (UUID)",
    "temp_dir": "string (path)",
    "status": "string (status code)",
    "system_message": "string",
    "documents": [
        {
            "id": "string (UUID)",
            "name": "string (filename)",
            "path": "string (path)",
            "format": "string (PDF|DOCX|TXT)",
            "size": "integer (bytes)"
        }
    ],
    "threads": [
        {
            "id": "string (UUID)",
            "title": "string",
            "queries": [
                {
                    "id": "string (UUID)",
                    "title": "string",
                    "text": "string",
                    "format": "string (format_type)"
                }
            ]
        }
    ],
    "responses": {
        "document_id": {
            "thread_id": {
                "query_id": "string (response)"
            }
        }
    },
    "export": {
        "format": "string (CSV|DOCX)",
        "orientation": "string (documents_in_rows|documents_in_columns)"
    },
    "state": {
        "is_paused": "boolean",
        "active_operations": {
            "document_id": {
                "status": "string (processing|complete)",
                "active_threads": {
                    "thread_id": {
                        "status": "string (processing|complete)",
                        "current_query_id": "string (UUID|null)",
                        "completed_queries": ["string (UUID)"]
                    }
                }
            }
        },
        "progress": {
            "total_operations": "integer",
            "completed_operations": "integer",
            "completed_documents": ["string (UUID)"]
        }
    }
}
```

## Field Descriptions

### Core Fields

- **job_id**: Unique identifier for the extraction job
- **temp_dir**: Path to temporary directory for job files
- **status**: Current status of the job. Valid values:
  - "initialized": Job created, ready to begin processing
  - "processing": Actively processing documents and queries
  - "paused": Processing temporarily halted, can be resumed
  - "complete": All processing finished
  - "error": Job encountered an unrecoverable error
- **system_message**: Global developer message used to guide LLM behavior across all interactions in this job. Can contain extensive context and instructions (max length: 32,768 characters)

### Documents Array

Each document object contains:
- **id**: Unique identifier for the document
- **name**: Original filename (used for output instead of previous alias system, max length: 255 characters). Spaces in filenames are preserved, and the application handles proper escaping where needed (e.g., in URLs or command-line operations).
- **path**: Path to the document in the temporary directory (max length: 4096 characters)
- **format**: File format of the document
- **size**: Size of the document in bytes

### Threads Array

Each thread object contains:
- **id**: Unique identifier for the thread
- **title**: Display title for the thread (used in output generation, max length: 255 characters)
- **queries**: Array of query objects belonging to this thread

### Query Objects

Each query object within a thread contains:
- **id**: Unique identifier for the query
- **title**: Display title for the query (max length: 255 characters)
- **text**: The actual query text (max length: 32,768 characters to accommodate complex queries)
- **format**: Response format specification. The application supports multiple formats including:
  - Basic formats: free_form, integer, floating_point_number, comma_separated_list, yes_no, date_dd_mm_yyyy
  - Statistical formats: median_95ci, mean_sd, mean_se, range
  Each format has associated parsing rules and format guidance defined in the parsers module.

### Responses Object

Organized hierarchically by:
1. document_id (primary organization for efficient output generation)
2. thread_id (maintains thread context)
3. query_id (preserves query sequence within threads)

This structure optimizes response organization for output generation while maintaining thread context and query relationships.

### Export Configuration

- **format**: Desired output format
- **orientation**: How data should be organized in the output

### State Object

Tracks the current state of the extraction process, supporting both sequential and parallel processing:

#### Active Operations
Maintains the current state of all processing operations:
- **document_id**: Maps to an object tracking the document's processing state
  - **status**: Current status of document processing. Valid values:
    - "processing": Document is being actively processed
    - "complete": All threads and queries for this document are complete
    - "error": Document processing failed (e.g., file corruption)
  - **active_threads**: Maps thread IDs to their processing state
    - **status**: Current status of thread processing. Valid values:
      - "processing": Thread has queries being processed
      - "complete": All queries in thread are complete
      - "error": Thread processing failed

#### Progress Tracking
Maintains overall job progress:
- **total_operations**: Total number of operations to perform (documents × queries)
- **completed_operations**: Number of completed operations
- **completed_documents**: Array of document IDs that have been fully processed

#### Pause State
- **is_paused**: When true, processing should halt at the next safe point
  - Safe points occur between query processing operations
  - Allows for clean resumption of processing

### State Transitions Example
```json
// Initial state when starting document processing
{
    "is_paused": false,
    "active_operations": {
        "doc-uuid-1": {
            "status": "processing",
            "active_threads": {
                "thread-uuid-1": {
                    "status": "processing",
                    "current_query_id": "query-uuid-1",
                    "completed_queries": []
                }
            }
        }
    },
    "progress": {
        "total_operations": 15,
        "completed_operations": 0,
        "completed_documents": []
    }
}

// Mid-processing state
{
    "is_paused": false,
    "active_operations": {
        "doc-uuid-1": {
            "status": "processing",
            "active_threads": {
                "thread-uuid-1": {
                    "status": "complete",
                    "current_query_id": null,
                    "completed_queries": ["query-uuid-1", "query-uuid-2"]
                },
                "thread-uuid-2": {
                    "status": "processing",
                    "current_query_id": "query-uuid-4",
                    "completed_queries": ["query-uuid-3"]
                }
            }
        },
        "doc-uuid-2": {
            "status": "processing",
            "active_threads": {
                "thread-uuid-1": {
                    "status": "processing",
                    "current_query_id": "query-uuid-1",
                    "completed_queries": []
                }
            }
        }
    },
    "progress": {
        "total_operations": 15,
        "completed_operations": 3,
        "completed_documents": []
    }
}
```

### State Management Notes

1. **Processing Order**:
   - Documents can be processed in parallel
   - Multiple threads within a document can be processed simultaneously
   - Queries within a single thread must be processed sequentially to maintain conversation context

2. **Progress Tracking**:
   - Total operations calculated as: number of documents × total number of queries across all threads
   - Operations are counted at the query level (one operation = one query processed for one document)
   - Documents are marked complete only when all their threads are complete

3. **Pause/Resume Behavior**:
   - Pausing sets is_paused to true
   - Processing completes current query before stopping
   - State structure preserves exact position for resuming
   - Can resume processing from any partially completed state

## Usage Examples

### Adding a New Document
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "report.pdf",
    "path": "/temp/550e8400/report.pdf",
    "format": "PDF",
    "size": 1048576
}
```

### Adding a New Thread with Queries
```json
{
    "id": "7b2ff47f-ea91-4b5f-b3a5-9c2ec59f9abc",
    "title": "demographic_data",
    "queries": [
        {
            "id": "a1b2c3d4-e5f6-4a5b-9c3d-12345678abcd",
            "title": "study_population_age",
            "text": "What was the mean age and standard deviation of the study population?",
            "format": "mean_sd"
        }
    ]
}
```

### Storing a Response
```json
{
    "responses": {
        "550e8400-e29b-41d4-a716-446655440000": {
            "7b2ff47f-ea91-4b5f-b3a5-9c2ec59f9abc": {
                "a1b2c3d4-e5f6-4a5b-9c3d-12345678abcd": "45.7 (SD: 12.3)"
            }
        }
    }
}
```

### Example CSV Output Structure
```
Thread          | Demographic Data     | Demographic Data     | Treatment Data    | Treatment Data
Query           | Population Age       | Gender Distribution  | Dosage           | Side Effects
Document 1.pdf  | 45.7 (SD: 12.3)     | M: 60%, F: 40%      | 500mg            | Headache, Nausea
Document 2.pdf  | 52.3 (SD: 15.1)     | M: 45%, F: 55%      | 750mg            | None reported
```

## Important Notes

1. **Document Names**: With the removal of aliases, document names (original filenames) are used directly in output generation

2. **Thread Sequence**: Threads are processed in their array order, with queries within each thread processed sequentially to maintain conversation context

3. **Response Organization**: The nested structure of responses preserves thread context while maintaining document-query relationships

4. **State Tracking**: The addition of the state object enables pause/resume functionality and progress tracking

5. **System Message**: Now global to the job rather than per-query, ensuring consistent context across all threads

## Migration Considerations

When migrating from the previous structure:

1. Document aliases will be replaced with original filenames
2. Queries will be organized into threads
3. Responses will be restructured to maintain thread context
4. New state tracking fields will be added
5. System message will be moved to the job level 