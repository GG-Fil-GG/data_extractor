<!-- DocumentsBlock.vue -->
<template>
    <div class="block documents-block">
      <h2>Documents</h2>
      <div v-for="(doc, index) in documents" :key="index" class="document-row">
        <div class="file-name">{{ doc.fileName }}</div>
        <input v-model="doc.alias" :placeholder="'Document ' + (index + 1) + ' Alias'" class="document-alias" />
        <div class="file-size">{{ doc.size }}</div>
        <div class="document-controls">
          <button @click="moveDocument(index, -1)" :disabled="index === 0">↑</button>
          <button @click="moveDocument(index, 1)" :disabled="index === documents.length - 1">↓</button>
          <button @click="removeDocument(index)">×</button>
        </div>
      </div>
      <input type="file" multiple @change="handleFileUpload" class="file-input" />
      <button @click="triggerFileInput" class="select-documents">Select documents</button>
    </div>
  </template>
  
  <script>
  import { mapState, mapMutations } from 'vuex'
  
  export default {
    name: 'DocumentsBlock',
    computed: {
      ...mapState(['documents'])
    },
    methods: {
      ...mapMutations(['setDocuments']),
      triggerFileInput() {
        this.$refs.fileInput.click()
      },
      handleFileUpload(event) {
        const files = Array.from(event.target.files)
        const newDocuments = files.map(file => ({
          fileName: file.name,
          alias: file.name,
          size: (file.size / (1024 * 1024)).toFixed(2) + ' MB'
        }))
        this.setDocuments([...this.documents, ...newDocuments])
      },
      moveDocument(index, direction) {
        const newIndex = index + direction
        if (newIndex >= 0 && newIndex < this.documents.length) {
          const temp = this.documents[index]
          this.$set(this.documents, index, this.documents[newIndex])
          this.$set(this.documents, newIndex, temp)
          this.setDocuments(this.documents)
        }
      },
      removeDocument(index) {
        this.documents.splice(index, 1)
        this.setDocuments(this.documents)
      }
    }
  }
  </script>
  
  <style scoped>
  .documents-block {
    background-color: #e6f3ff;
    padding: 20px;
    margin-bottom: 20px;
  }
  
  .document-row {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .file-name {
    flex: 1;
    background-color: #f0f0f0;
    padding: 5px;
    margin-right: 10px;
  }
  
  .document-alias {
    flex: 2;
    padding: 5px;
    margin-right: 10px;
  }
  
  .file-size {
    width: 100px;
    text-align: right;
    margin-right: 10px;
  }
  
  .document-controls button {
    margin-left: 5px;
  }
  
  .select-documents {
    margin-top: 10px;
  }
  
  .file-input {
    display: none;
  }
  </style>