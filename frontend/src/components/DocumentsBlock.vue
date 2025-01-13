<!-- DocumentsBlock.vue -->
<template>
  <div class="block">
    <h2 class="block-heading">Documents</h2>
    <div v-if="documents.length > 0" class="fields-header">
      <div class="document-name-header">Name</div>
      <div class="document-alias-header">Alias</div>
      <div class="document-size-header">Size</div>
      <div class="actions-header">Actions</div>
    </div>
    <div v-for="(doc, index) in documents" :key="index" class="document-row">
      <div class="document-name-field">{{ doc.fileName }}</div>
      <input 
        :value="doc.Alias" 
        @input="updateAlias(index, $event.target.value)" 
        :placeholder="'Document ' + (index + 1) + ' Alias'" 
        class="document-alias-field" 
      />
      <div class="document-size-field">{{ doc.size }}</div>
      <div class="actions">
        <button 
          @click="moveDocument(index, -1)" 
          :disabled="index === 0" 
          class="move-up-button"
        >↑</button>
        <button 
          @click="moveDocument(index, 1)" 
          :disabled="index === documents.length - 1" 
          class="move-down-button"
        >↓</button>
        <button @click="removeDocument(index)" class="remove-button">×</button>
      </div>
    </div>
    <input type="file" ref="fileInput" @change="handleFileUpload" accept=".txt,.docx,.pdf" multiple class="file-input" />
    <button @click="triggerFileInput" class="select-documents-button">Select documents</button>
  </div>
</template>

<script>
import { mapState, mapMutations } from 'vuex'
import { countTokens } from '../services/api';

export default {
  name: 'DocumentsBlock',
  computed: {
    ...mapState(['documents']),
    maxDocumentSizeWidth() {
      if (this.documents.length === 0) return 80;
      const maxSizeString = this.documents.reduce((max, doc) => {
        const sizeLength = doc.size.length;
        const unitLength = this.getUnitLength(doc.size);
        return sizeLength + unitLength > max ? sizeLength + unitLength : max;
      }, 'Size'.length);
      return Math.max(80, maxSizeString * 8);
    },
  },
  methods: {
    ...mapMutations(['setDocuments']),
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    async handleFileUpload(event) {
      const supportedFormats = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      const files = Array.from(event.target.files);
      const validFiles = files.filter(file => supportedFormats.includes(file.type));

      if (validFiles.length !== files.length) {
        alert('Some files were removed because they are not in supported formats (txt, docx, pdf).');
      }

      for (const file of validFiles) {
        const formData = new FormData();
        formData.append('file', file);

        try {
          const response = await countTokens(formData);
          console.log('countTokens response:', response);  // Add this line to check the response
          const filePath = response.data.file_path;

          const nameParts = file.name.split('.');
          const newDocument = {
            filePath: filePath,
            fileName: file.name,
            Alias: nameParts.slice(0, -1).join('.'),
            Ext: nameParts.pop().toLowerCase(),
            size: this.formatFileSize(file.size),
            file: file  // Ensure the file property is set
          };
          this.setDocuments(documents => [...documents, newDocument]);
        } catch (error) {
          console.error('Error counting tokens:', error);
          alert('There was an error processing your file. Please try again.');
        }
      }
    },
    moveDocument(index, direction) {
      const newIndex = index + direction;
      if (newIndex >= 0 && newIndex < this.documents.length) {
        this.setDocuments(documents => {
          const newDocuments = [...documents];
          const temp = newDocuments[index];
          newDocuments[index] = newDocuments[newIndex];
          newDocuments[newIndex] = temp;
          return newDocuments;
        });
      }
    },
    removeDocument(index) {
      this.setDocuments(documents => documents.filter((_, i) => i !== index));
    },
    updateAlias(index, newAlias) {
      if (this.documents.some((doc, i) => i !== index && doc.Alias === newAlias)) {
        alert('This alias is already in use. Please choose a unique alias.');
        return;
      }
      this.setDocuments(documents => {
        const newDocuments = [...documents];
        newDocuments[index] = { ...newDocuments[index], Alias: newAlias };
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
    },
    getUnitLength(sizeString) {
      const units = ['bytes', 'KB', 'MB'];
      for (const unit of units) {
        if (sizeString.includes(unit)) {
          return unit.length;
        }
      }
      return 0;
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
  font-size: 28px;
  color: #333;
}

.fields-header, .document-row {
  display: grid;
  grid-template-columns: 1fr 2fr minmax(80px, auto) 110px;
  align-items: stretch;
  height: 30px;
  gap: 10px;
  margin-bottom: 10px;
}

.document-name-header, .document-alias-header, .document-size-header, .actions-header {
  padding: 5px;
  font-size: 16px;
  font-weight: bold;
}

.document-name-field, .document-alias-field, .document-size-field {
  padding: 5px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 3px;
}

.actions {
  display: flex;
  gap: 10px;
}

.move-up-button, .move-down-button, .remove-button {
  width: 30px;
  background-color: #008CBA;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 3px;
  padding: 5px;
  box-sizing: border-box; /* Ensure padding is included in the width */
}

.move-up-button:disabled, .move-down-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.select-documents-button {
  margin-top: 20px;
  margin-bottom: 20px;
  height: 30px;
  padding: 5px 10px;
  font-size: 16px;
  background-color: #008CBA;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 3px;
}

.file-input {
  display: none;
}
</style>