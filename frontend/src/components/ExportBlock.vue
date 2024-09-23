<!-- ExportBlock.vue -->
<template>
    <div class="block export-block">
      <h2>Export</h2>
      <div class="export-options">
        <label for="export-format">Export Format:</label>
        <select v-model="exportFormat" id="export-format">
          <option value="csv">CSV</option>
          <option value="docx">DOCX</option>
        </select>
      </div>
      <div class="export-options">
        <label for="orientation">Orientation:</label>
        <select v-model="orientation" id="orientation">
          <option value="doc_row">Documents in rows</option>
          <option value="query_row">Queries in rows</option>
        </select>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ExportBlock',
    data() {
      return {
        exportFormat: 'csv',
        orientation: 'doc_row'
      }
    }
  }
  </script>
  
  <style scoped>
  .export-block {
    background-color: #e6f3ff;
    padding: 20px;
    margin-bottom: 20px;
  }
  
  .export-options {
    margin-bottom: 10px;
  }
  
  label {
    margin-right: 10px;
  }
  </style>