# DocumentsBlock Component

## Purpose

The DocumentsBlock component allows users to upload, manage, and organize documents for data extraction.

## Features

- Upload multiple documents (PDF, DOCX, TXT)
- Assign aliases to documents for easier identification
- Reorder documents using up/down controls
- Remove documents from the list
- Display document metadata (name, size)

## Component Structure

The component consists of:
- A header section with column labels
- A list of document rows, each showing file information and controls
- File upload controls at the bottom

## State Management

This component interacts with the Vuex store to:
- Add new documents to the `documents` array
- Update document aliases
- Reorder documents
- Remove documents

## Key Methods

- `handleFileUpload()` - Processes files selected by the user
- `updateAlias()` - Updates the alias for a document
- `moveDocument()` - Changes the order of documents in the list
- `removeDocument()` - Removes a document from the list
- `triggerFileInput()` - Opens the file selection dialog

## User Interaction Flow

1. User clicks "Select documents" button
2. File selection dialog opens
3. User selects one or more files
4. Files are processed and added to the document list
5. User can modify aliases, reorder, or remove documents as needed 