# State Management (Vuex Store)

## Overview

The application uses Vuex for centralized state management. The store maintains all the data needed across components, including documents, queries, export settings, and extraction status.

## Store Structure

The Vuex store is defined in `frontend/src/store.js` and consists of:

- **State**: The central data store
- **Mutations**: Functions that directly modify the state
- **Actions**: Functions that can perform asynchronous operations before committing mutations
- **Getters**: Computed properties based on the state

## State Properties

| Property | Type | Description |
|----------|------|-------------|
| `documents` | Array | List of uploaded documents with metadata |
| `queries` | Array | List of user-defined queries |
| `exportFormat` | String | Selected export format ('csv' or 'docx') |
| `orientation` | String | Selected data orientation ('doc_row' or 'query_row') |
| `extractionStatus` | String | Current status of the extraction process |
| `downloadLink` | String | URL to download the extraction results |

## Mutations

| Mutation | Parameters | Description |
|----------|------------|-------------|
| `setDocuments` | documentsOrUpdater | Updates the documents array, either with a new array or using an updater function |
| `setQueries` | queriesOrUpdater | Updates the queries array, either with a new array or using an updater function |
| `setExportFormat` | format | Updates the export format setting |
| `setOrientation` | orientation | Updates the orientation setting |
| `setExtractionStatus` | status | Updates the extraction status message |
| `setDownloadLink` | link | Sets the download link for extraction results |
| `resetState` | none | Resets all state properties to their default values |

## Actions

| Action | Parameters | Description |
|--------|------------|-------------|
| `initializeStore` | none | Initializes the store with default values by calling the resetState mutation |
| `setDownloadLink` | jobId | Asynchronously fetches the download URL for a completed job and updates the state |

## Getters

| Getter | Description |
|--------|-------------|
| `isExtractionReady` | Returns true if all required data is present to start extraction (documents, queries with all fields, export format, orientation) |
| `hasValidDocuments` | Returns true if there is at least one valid document in the store |

## Usage in Components

Components interact with the store using:

- `mapState` - To access state properties
- `mapMutations` - To commit mutations
- `mapActions` - To dispatch actions
- `mapGetters` - To access getter properties

Example:

```js
import { mapState, mapMutations, mapActions, mapGetters } from 'vuex'

export default {
  computed: {
    ...mapState(['documents', 'queries']),
    ...mapGetters(['isExtractionReady'])
  },
  methods: {
    ...mapMutations(['setDocuments']),
    ...mapActions(['initializeStore'])
  }
}
```

## Data Flow

1. Components access state via computed properties
2. User interactions trigger methods that commit mutations
3. Mutations update the state
4. Components reactively update when state changes
5. Actions handle asynchronous operations before committing mutations