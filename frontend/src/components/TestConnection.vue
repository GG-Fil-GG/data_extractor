<!-- frontend/src/components/TestConnection.vue -->

<template>
  <div>
    <h2>Test API Connection</h2>
    <input type="file" multiple @change="handleFileUpload">
    <button @click="uploadFiles">Upload Files</button>
    <button @click="startExtraction">Start Extraction</button>
    <p>{{ message }}</p>
  </div>
</template>

<script>
import { uploadFiles, startExtraction } from '../services/api';

export default {
  data() {
    return {
      files: [],
      message: ''
    };
  },
  methods: {
    handleFileUpload(event) {
      this.files = Array.from(event.target.files);
    },
    async uploadFiles() {
      try {
        const response = await uploadFiles(this.files);
        this.message = response.data.message;
      } catch (error) {
        console.error(error);
        this.message = 'Error uploading files';
      }
    },
    async startExtraction() {
      try {
        const response = await startExtraction({ /* data */ });
        this.message = response.data.message;
      } catch (error) {
        console.error(error);
        this.message = 'Error starting extraction';
      }
    }
  }
};
</script>
