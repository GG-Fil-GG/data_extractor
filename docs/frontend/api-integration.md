# API Integration

## Overview

The frontend communicates with the backend through a set of REST API endpoints. These interactions are managed through the `services/api.js` module, which provides a centralized interface for all API calls.

## API Service Module

The API service module (`frontend/src/services/api.js`) encapsulates all HTTP requests to the backend, providing a clean interface for components to use without directly handling HTTP details.

## API Endpoints

The frontend communicates with the backend through the following REST endpoints:

| Endpoint | Method | Purpose | Request Data | Response |
|----------|--------|---------|--------------|----------|
| `/count_tokens` | POST | Upload a document and get token count | FormData with file | Object with file path and token count |
| `/begin_extraction` | POST | Start the extraction process | FormData with documents, queries, export settings | Object with job ID |
| `/download_results` | GET | Get download URL for results | Query param: job_id | Object with download URL |

### Endpoint Details

#### `/count_tokens`
- **Purpose**: Uploads a document and returns its token count and file path
- **Request**: FormData containing the file to be processed
- **Response**: JSON object with file path and token count
- **Used by**: DocumentsBlock component during file upload

#### `/begin_extraction`
- **Purpose**: Initiates the extraction process with all necessary data
- **Request**: FormData containing document metadata, queries, export format, and orientation
- **Response**: JSON object with the job ID for tracking
- **Used by**: ExtractionBlock component when user clicks "Begin extraction"

#### `/download_results`
- **Purpose**: Retrieves the download URL for a completed extraction job
- **Request**: Job ID as a query parameter
- **Response**: JSON object with the download URL
- **Used by**: ExtractionBlock component and Vuex store to provide download link

## Key API Functions

| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `countTokens` | Uploads a document and returns its token count and file path | `formData` (containing the file) | Object with file path and token count |
| `beginExtraction` | Initiates the extraction process | `formData` (with documents, queries, export format, orientation) | Job ID for the extraction task |
| `downloadResults` | Retrieves the download URL for completed extraction | `jobId` | URL to download the results file |

## Request Format

### Document Upload

When uploading documents, the frontend:
1. Creates a FormData object
2. Appends the file to it
3. Sends it to the backend using a POST request

```js
const formData = new FormData();
formData.append('file', file);
const response = await countTokens(formData);
```

### Extraction Request

When initiating extraction, the frontend:
1. Creates a FormData object
2. Appends document metadata as JSON
3. Appends queries as JSON
4. Adds export format and orientation settings
5. Sends the complete package to the backend

```js
const formData = new FormData();
formData.append('documents', JSON.stringify(documentsMetadata));
formData.append('queries', JSON.stringify(queries));
formData.append('export_format', exportFormat);
formData.append('orientation', orientation);
const response = await beginExtraction(formData);
```

## Response Handling

The API service handles responses and errors consistently:

1. Successful responses are passed directly to the calling component
2. Errors are caught and can be handled by the component
3. Network issues and server errors are properly identified

## Integration with Vuex

The API service works closely with the Vuex store:

1. Components dispatch Vuex actions that call API functions
2. API responses update the store state through mutations
3. Components react to state changes

Example flow:
1. Component triggers an action
2. Vuex Action is dispatched
3. API Call is made to the backend
4. Backend Processing occurs
5. API Response is returned to frontend
6. Vuex Mutation updates the store
7. Component Updates based on new state

## Error Handling

The API integration includes robust error handling:

1. Network errors are caught and logged
2. Server errors include detailed information when available
3. User-friendly error messages are displayed to the user
4. The application maintains a stable state even when API calls fail

## Security Considerations

1. No sensitive data is sent in URL parameters
2. File uploads are properly validated on both client and server
3. Error messages don't expose internal system details

## Example: Complete Extraction Flow

1. User uploads documents via `DocumentsBlock` component
2. Files are sent to backend using `countTokens` API function
3. User defines queries and export settings
4. User clicks "Begin extraction" in `ExtractionBlock` component
5. Component calls `beginExtraction` API function with all required data
6. Backend processes the request and returns a job ID
7. Frontend polls or waits for completion
8. When complete, `downloadResults` API function is called with the job ID
9. Backend returns a download URL
10. Frontend updates the Vuex store with the download link
11. User can click to download the results
