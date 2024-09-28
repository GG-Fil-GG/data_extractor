<!-- DocumentsBlock.vue -->
<template>
  <div class="block">
    <h2 class="block-heading">Documents</h2>
    <div v-if="documents.length > 0" class="fields-header">
      <div class="document-name-header">Name</div>
      <div class="document-alias-header">Alias</div>
      <div class="document-size-header" :style="{ width: maxDocumentSizeWidth + 'px' }">Size</div>
      <div class="move-up-button-header"></div>
      <div class="move-down-button-header"></div>
      <div class="remove-button-header"></div>
    </div>
    <div v-for="(doc, index) in documents" :key="index" class="document-row">
      <div class="document-name-field">{{ doc.fileName }}</div>
      <input 
        :value="doc.Alias" 
        @input="updateAlias(index, $event.target.value)" 
        :placeholder="'Document ' + (index + 1) + ' Alias'" 
        class="document-alias-field" 
      />
      <div class="document-size-field" :style="{ width: maxDocumentSizeWidth + 'px' }">{{ doc.size }}</div>
      <button 
        @click="moveDocument(index, -1)" 
        :disabled="index === 0" 
        class="move-up-button"
        :class="{ 'disabled': index === 0 }"
      >↑</button>
      <button 
        @click="moveDocument(index, 1)" 
        :disabled="index === documents.length - 1" 
        class="move-down-button"
        :class="{ 'disabled': index === documents.length - 1 }"
      >↓</button>
      <button @click="removeDocument(index)" class="remove-button">×</button>
    </div>
    <input type="file" ref="fileInput" @change="handleFileUpload" accept=".txt,.docx,.pdf" multiple class="file-input" />
    <button @click="triggerFileInput" class="select-documents-button">Select documents</button>
  </div>
</template>

<script>
import { mapState, mapMutations } from 'vuex'

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
    handleFileUpload(event) {
      const supportedFormats = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      const files = Array.from(event.target.files);
      const validFiles = files.filter(file => supportedFormats.includes(file.type));

      if (validFiles.length !== files.length) {
        alert('Some files were removed because they are not in supported formats (txt, docx, pdf).');
      }

      const newDocuments = validFiles.map(file => {
        const nameParts = file.name.split('.');
        return {
          file: file,
          fileName: file.name,
          Alias: nameParts.slice(0, -1).join('.'),
          Ext: nameParts.pop().toLowerCase(),
          size: this.formatFileSize(file.size)
        }
      });

      this.setDocuments(documents => [...documents, ...newDocuments]);
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
  font-size: 24px;
  color: #333;
}

.fields-header {
  display: flex;
  align-items: stretch;
  margin-bottom: 10px;
}

.document-name-header {
  flex: 1;
  margin-right: 5px;
  padding: 5px;
  font-size: 16px;
  font-weight: bold;
  box-sizing: border-box;
}

.document-alias-header {
  flex: 2;
  margin: 0 5px;
  padding: 5px;
  font-size: 16px;
  font-weight: bold;
  box-sizing: border-box;
}

.document-size-header {
  flex: none;
  margin: 0 5px;
  padding: 5px;
  font-size: 16px;
  font-weight: bold;
  box-sizing: border-box;
}

.move-up-button-header {
  flex: none;
  margin: 0 5px;
  width: 30px;
  border: none;
}

.move-down-button-header {
  flex: none;
  margin: 0 5px;
  width: 30px;
  border: none;
}

.remove-button-header {
  flex: none;
  margin-left: 5px;
  width: 30px;
  border: none;
}

.document-row {
  display: flex;
  align-items: stretch;
  height: 30px;
  margin-bottom: 10px;
}

.document-name-field {
  flex: 1;
  margin-right: 5px;
  padding: 5px;
  font-size: 16px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
}

.document-alias-field {
  flex: 2;
  margin: 0 5px;
  padding: 5px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
}

.document-size-field {
  flex: none;
  margin: 0 5px;
  padding: 5px;
  font-size: 16px;
  background-color: #f0f0f0;
  text-align: right;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
}

.move-up-button {
  flex: none;
  margin: 0 5px;
  width: 30px;
  background-color: #008CBA;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 3px;
}

.move-down-button {
  flex: none;
  margin: 0 5px;
  width: 30px;
  background-color: #008CBA;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 3px;
}

.remove-button {
  flex: none;
  margin-left: 5px;
  width: 30px;
  background-color: #008CBA;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 3px;
}

.move-up-button.disabled, .move-down-button.disabled {
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