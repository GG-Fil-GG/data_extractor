# ExtractionBlock Component

## Purpose

The ExtractionBlock component is responsible for initiating the extraction process, displaying its status, and providing access to the results.

## Features

- Start the extraction process
- Display the current status of extraction
- Provide a download link for the results
- Show extraction progress indicators

## Component Structure

The component consists of:
- An extraction button to start the process
- Status display area showing the current state
- Progress indicators during extraction
- Download link for completed extractions

## State Management

This component interacts with the Vuex store to:
- Access document and query data
- Update the extraction status
- Set the download link for results

## Key Properties

- `isExtracting` - Boolean indicating if extraction is in progress
- `jobId` - Identifier for the current extraction job
- `currentJobId` - Identifier for the most recently completed job

## Key Methods

- `beginExtraction()` - Initiates the extraction process by sending data to the backend
- `canExtract()` - Computed property that determines if extraction can begin
- `downloadResults()` - Retrieves the results file from the backend

## API Interactions

- Sends document metadata, queries, export format, and orientation to the backend
- Receives job ID and status updates from the backend
- Retrieves the download URL for completed extractions

## User Interaction Flow

1. User configures documents, queries, and export options in other components
2. User clicks the extraction button to begin the process
3. Status updates are displayed as the extraction progresses
4. When complete, a download link appears
5. User can download the results in the selected format 