<!-- ExportBlock.vue -->
<template>
    <div class="block export-block">
      <h2>Export</h2>
      <div class="export-options">
        <label for="export-format">Export Format:</label>
        <select :value="exportFormat" @change="updateExportFormat" id="export-format">
          <option value="csv">CSV</option>
          <option value="docx">DOCX</option>
        </select>
      </div>
      <div class="export-options">
        <label for="orientation">Orientation:</label>
        <select :value="orientation" @change="updateOrientation" id="orientation">
          <option value="doc_row">Documents in rows</option>
          <option value="query_row">Queries in rows</option>
        </select>
      </div>
    </div>
  </template>
  
  <script>
  import { mapState, mapMutations } from 'vuex'
  
  export default {
    name: 'ExportBlock',
    computed: {
      ...mapState(['exportFormat', 'orientation'])
    },
    methods: {
      ...mapMutations(['setExportFormat', 'setOrientation']),
      updateExportFormat(event) {
        this.setExportFormat(event.target.value)
      },
      updateOrientation(event) {
        this.setOrientation(event.target.value)
      }
    }
  }
  </script>
  
  <style scoped>
  .export-block {
    background-color: #e6f3ff;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 5px;
  }
  
  h2 {
    margin-top: 0;
    margin-bottom: 15px;
  }
  
  .export-options {
    margin-bottom: 15px;
    display: flex;
    align-items: center;
  }
  
  label {
    margin-right: 10px;
    min-width: 120px;
  }
  
  select {
    padding: 5px;
    border-radius: 3px;
    border: 1px solid #ccc;
    font-size: 14px;
    width: 200px;
  }
  </style>