# App.vue Component

## Purpose

App.vue is the root component of the application that provides the overall structure and layout. It serves as the container for all other components and initializes the application state.

## Features

- Provides the main application layout
- Includes the application title/header
- Organizes the component hierarchy
- Initializes the Vuex store

## Component Structure

The component consists of:
- Application header with the title "DataExtractor.com"
- Container for all child components
- Sequential arrangement of the main functional blocks

## Child Components

App.vue imports and renders the following components in order:
1. `DocumentsBlock` - For document management
2. `QueriesBlock` - For query definition
3. `ExportBlock` - For export configuration
4. `ExtractionBlock` - For extraction control and results

## State Management

This component:
- Initializes the Vuex store when created
- Provides the store context to all child components

## Key Methods

- `initializeStore()` - Called during component creation to set up the initial application state

## Styling

The component applies:
- Global font family (Roboto)
- Responsive width constraints
- Consistent padding and margins
- Centered layout

## Application Flow

1. When the application loads, App.vue is the first component rendered
2. It initializes the Vuex store
3. It renders all child components in the specified order
4. The user interacts with the child components to configure and run extractions 