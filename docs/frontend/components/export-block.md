# ExportBlock Component

## Purpose

The ExportBlock component allows users to configure how the extracted data will be formatted and exported.

## Features

- Select the export file format (CSV or DOCX)
- Choose the orientation of data in the output file
- Simple interface with dropdown selectors

## Component Structure

The component consists of:
- A header section with column labels
- A row with dropdown selectors for format and orientation

## Export Format Options

Users can choose between two export formats:
- **CSV** - Comma-separated values format, suitable for spreadsheet applications
- **DOCX** - Microsoft Word document format, providing a more formatted output

## Orientation Options

Users can select how data is organized in the output:
- **Documents in rows** (`doc_row`) - Each row represents a document, with queries as columns
- **Queries in rows** (`query_row`) - Each row represents a query, with documents as columns

## State Management

This component interacts with the Vuex store to:
- Update the `exportFormat` state property
- Update the `orientation` state property

## Key Methods

- `updateExportFormat()` - Updates the selected export format in the store
- `updateOrientation()` - Updates the selected orientation in the store

## User Interaction Flow

1. User selects the desired export format from the dropdown
2. User selects the preferred data orientation from the dropdown
3. These settings are applied when the extraction is performed 