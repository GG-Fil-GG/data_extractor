# QueriesBlock Component

## Purpose

The QueriesBlock component allows users to define and manage queries that will be used to extract specific information from documents.

## Features

- Create multiple queries with custom aliases
- Define the query text (the actual question to be answered)
- Select the expected format for each query response
- Reorder queries using up/down controls
- Remove queries from the list

## Component Structure

The component consists of:
- A header section with column labels
- A list of query rows, each with alias, text, format options, and controls
- Controls to add new queries

## State Management

This component interacts with the Vuex store to:
- Add new queries to the `queries` array
- Update query properties (alias, text, format)
- Reorder queries
- Remove queries

## Query Format Options

Users can specify the expected format for each query response:
- Free-form (default)
- Integer
- Floating-point number
- Comma-separated list
- Yes/No
- Median (95% CI)
- Mean (SD)
- Mean (SE)
- Range
- Date (DD-MM-YYYY)

## Key Methods

- `addQuery()` - Adds a new query to the list
- `updateQueryField()` - Updates a specific field of a query
- `moveQuery()` - Changes the order of queries in the list
- `removeQuery()` - Removes a query from the list
- `validateQueries()` - Ensures all queries have valid properties

## User Interaction Flow

1. User enters query information (alias, text)
2. User selects the expected format for the response
3. User can add additional queries as needed
4. User can reorder or remove queries
5. Validation ensures all queries are properly configured before extraction 