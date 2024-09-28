<!-- ExportBlock.vue -->
<template>
  <div class="block">
    <h2 class="block-heading">Export</h2>
    <div class="fields-header">
      <div class="export-format-header">Export Format</div>
      <div class="orientation-header">Orientation</div>
    </div>
    <div class="export-row">
      <select :value="exportFormat" @change="updateExportFormat" class="export-format-select">
        <option value="csv">CSV</option>
        <option value="docx">DOCX</option>
      </select>
      <select :value="orientation" @change="updateOrientation" class="orientation-select">
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
.block {
  background-color: #e6f3ff;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 3px;
}

.block-heading {
  margin-top: 10px;
  margin-bottom: 20px;
  padding: 5px;
  font-size: 24px;
  color: #333;
}

.fields-header {
  display: flex;
  align-items: stretch;
  justify-content: left;
  margin-bottom: 10px;
}

.export-format-header {
  width: 200px;
  margin-right: 5px;
  padding: 5px;
  font-size: 16px;
  font-weight: bold;
  box-sizing: border-box;
}

.orientation-header {
  width: 200px;
  margin-left: 5px;
  padding: 5px;
  font-size: 16px;
  font-weight: bold;
  box-sizing: border-box;
}

.export-row {
  display: flex;
  align-items: stretch;
  height: 30px;
  justify-content: left;
  margin-bottom: 20px;
}

.export-format-select {
  width: 200px;
  margin-right: 5px;
  padding: 5px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
}

.orientation-select {
  width: 200px;
  margin-left: 5px;
  padding: 5px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
}
</style>