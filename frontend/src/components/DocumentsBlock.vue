<!-- DocumentsBlock.vue -->
<template>
    <div class="block documents-block">
      <h2>Documents</h2>
      <div v-if="documents.length > 0" class="document-header">
        <div class="column-header name-header">Name</div>
        <div class="column-header alias-header">Alias</div>
        <div class="column-header size-header">Size</div>
      </div>
      <div v-for="(doc, index) in documents" :key="index" class="document-row">
        <div class="file-name">{{ doc.fileName }}</div>
        <input :value="doc.Alias" @input="updateAlias(index, $event.target.value)" :placeholder="'Document ' + (index + 1) + ' Alias'" class="document-alias" />
        <div class="file-size" :style="{ width: maxFileSizeWidth + 'px' }">{{ doc.size }}</div>
        <div class="document-controls">
          <div class="move-controls">
            <button @click="moveDocument(index, -1)" :disabled="index === 0" class="move-button">↑</button>
            <button @click="moveDocument(index, 1)" :disabled="index === documents.length - 1" class="move-button">↓</button>
          </div>
          <button @click="removeDocument(index)" class="remove-button">×</button>
        </div>
      </div>
      <input type="file" multiple @change="handleFileUpload" ref="fileInput" class="file-input" />
      <button @click="triggerFileInput" class="select-documents">Select documents</button>
    </div>
  </template>
  
  <script>
  import { mapState, mapMutations } from 'vuex'
  
  export default {
    name: 'DocumentsBlock',
    computed: {
      ...mapState(['documents']),
      maxFileSizeWidth() {
        if (this.documents.length === 0) return 80; // default width
        const maxSizeString = this.documents.reduce((max, doc) => 
          doc.size.length > max.length ? doc.size : max
        , '');
        return Math.max(80, maxSizeString.length * 8); // Approximate width based on character count
      }
    },
    methods: {
      ...mapMutations(['setDocuments']),
      triggerFileInput() {
        this.$refs.fileInput.click()
      },
      handleFileUpload(event) {
        const files = Array.from(event.target.files)
        const newDocuments = files.map(file => {
          const nameParts = file.name.split('.');
          return {
            file: file,
            fileName: file.name,
            Alias: nameParts.slice(0, -1).join('.'),
            Ext: nameParts.pop().toLowerCase(),
            size: this.formatFileSize(file.size)
          }
        })
        console.log('New documents:', newDocuments);
        this.setDocuments(documents => {
          const updatedDocuments = [...documents, ...newDocuments];
          console.log('Updated documents in store:', JSON.stringify(updatedDocuments));
          return updatedDocuments;
        })
      },
      moveDocument(index, direction) {
        const newIndex = index + direction
        if (newIndex >= 0 && newIndex < this.documents.length) {
          this.setDocuments(documents => {
            const newDocuments = [...documents]
            const temp = newDocuments[index]
            newDocuments[index] = newDocuments[newIndex]
            newDocuments[newIndex] = temp
            return newDocuments
          })
        }
      },
      removeDocument(index) {
        this.setDocuments(documents => documents.filter((_, i) => i !== index))
      },
      updateAlias(index, newAlias) {
        if (this.documents.some((doc, i) => i !== index && doc.Alias === newAlias)) {
          alert('This alias is already in use. Please choose a unique alias.');
          return;
        }
        this.setDocuments(documents => {
          const newDocuments = [...documents];
          newDocuments[index] = { ...newDocuments[index], Alias: newAlias };  // Changed from 'alias' to 'Alias'
          return newDocuments;
        });
      },
      getBackendDocuments() {
        return this.documents.map(doc => ({
          Alias: doc.Alias,
          Ext: doc.Ext
        }));
      },
      formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB';
        else return (bytes / 1048576).toFixed(2) + ' MB';
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

  .document-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    font-weight: bold;
  }

  .column-header {
    font-weight: bold;
    padding: 5px;
    background-color: #d0e0f0;
    border: 1px solid #b0c0d0;
  }

  .name-header {
    flex: 1;
    margin-right: 10px;
  }

  .alias-header {
    flex: 2;
    margin-right: 10px;
  }

  .size-header {
    width: 100px;
    margin-right: 10px;
    text-align: right;
  }

  .document-row {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }

  .file-name {
    flex: 1;
    margin-right: 10px;
    padding: 5px;
    font-size: 14px;
    line-height: 1.5;
    height: 30px;
    box-sizing: border-box;
    background-color: #f0f0f0;
    border: 1px solid #ccc;
  }

  .document-alias {
    flex: 2;
    margin-right: 10px;
    padding: 5px;
    font-size: 14px;
    line-height: 1.5;
    height: 30px;
    box-sizing: border-box;
    background-color: #fff;
    border: 1px solid #ccc;
  }

  .file-size {
    width: 100px;
    margin-right: 10px;
    padding: 5px;
    font-size: 14px;
    line-height: 1.5;
    height: 30px;
    box-sizing: border-box;
    background-color: #f0f0f0;
    border: 1px solid #ccc;
    text-align: right;
  }

  .document-controls {
    display: flex;
    align-items: center;
    width: 120px;
    flex-shrink: 0;
  }

  .move-controls {
    display: flex;
    margin-right: 10px;
  }

  .move-button, .remove-button {
    font-family: inherit;
    font-size: 14px;
    line-height: 1.5;
    padding: 5px 10px;
    cursor: pointer;
    height: 30px;
    vertical-align: middle;
    border: 1px solid #ccc;
    background-color: #f0f0f0;
    box-sizing: border-box;
  }

  .move-button {
    margin-right: 10px;
  }

  .move-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .remove-button {
    background-color: #ffeeee;
    border-color: #ffcccc;
  }

  .select-documents {
    font-family: inherit;
    font-size: 14px;
    line-height: 1.5;
    padding: 5px 10px;
    cursor: pointer;
    height: 30px;
    vertical-align: middle;
    border: 1px solid #ccc;
    background-color: #f0f0f0;
    box-sizing: border-box;
    margin-top: 10px;
    margin-left: 0;
  }

  .file-input {
    display: none;
  }
  </style>