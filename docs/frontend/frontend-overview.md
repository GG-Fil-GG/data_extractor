# Frontend Documentation

## Overview

The frontend of DataExtractor is built with Vue.js 3 and uses Vuex for state management. It provides a user interface for uploading documents, defining queries, setting export options, and initiating the extraction process.

## Component Structure

The application is organized into the following main components:

1. **App.vue** - The root component that contains the overall layout and imports all other components
2. **DocumentsBlock.vue** - Handles document uploading and management
3. **QueriesBlock.vue** - Allows users to define and manage extraction queries
4. **ExportBlock.vue** - Provides options for export format and orientation
5. **ExtractionBlock.vue** - Controls the extraction process and displays results

## Data Flow

1. Users upload documents through the DocumentsBlock component
2. Users define queries in the QueriesBlock component
3. Users select export options in the ExportBlock component
4. Users initiate extraction in the ExtractionBlock component
5. The Vuex store maintains the application state across all components
6. API calls to the backend are made through the services/api.js module

## State Management

The application uses Vuex for state management with the following main state properties:

- `documents` - Array of uploaded documents with metadata
- `queries` - Array of user-defined queries
- `exportFormat` - Selected export format (CSV or DOCX)
- `orientation` - Selected orientation (doc_row or query_row)
- `extractionStatus` - Current status of the extraction process
- `downloadLink` - Link to download the extraction results

## Key Files

- `src/App.vue` - Main application component
- `src/components/` - Directory containing all Vue components
- `src/store.js` - Vuex store configuration
- `src/services/api.js` - API communication with the backend
- `src/global.css` - Global CSS styles
- `src/main.js` - Application entry point 