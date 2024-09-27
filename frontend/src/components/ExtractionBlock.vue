<!-- ExtractionBlock.vue -->
<template>
    <div class="block extraction-block">
      <h2>Extraction</h2>
      <button @click="beginExtraction" :disabled="!canExtract" class="begin-extraction">Begin extraction</button>
      <p v-if="extractionStatus">{{ extractionStatus }}</p>
      <button v-if="downloadLink" @click="downloadResults" class="download-results">Download results</button>
    </div>
  </template>
  
  <script>
  import { mapState, mapGetters, mapMutations } from 'vuex'
  import { beginExtraction, downloadResults } from '../services/api'

  export default {
    name: 'ExtractionBlock',
    computed: {
      ...mapState(['documents', 'queries', 'exportFormat', 'orientation', 'extractionStatus', 'downloadLink']),
      ...mapGetters(['isExtractionReady', 'hasValidDocuments']),
      canExtract() {
        console.log('Documents in ExtractionBlock:', JSON.stringify(this.documents));
        return this.isExtractionReady && this.hasValidDocuments;
      }
    },
    methods: {
      ...mapMutations(['setExtractionStatus', 'setDownloadLink']),
      async beginExtraction() {
        console.log('Documents at beginning of extraction:', JSON.stringify(this.documents));
        console.log('Beginning extraction. Documents:', JSON.stringify(this.documents));
        const formData = new FormData();

        // Prepare documents metadata
        const documentsMetadata = this.documents.map((doc) => ({
          Alias: doc.Alias,
          Ext: doc.Ext
        }));
        console.log('Documents metadata being sent:', documentsMetadata);
        formData.append('documents', JSON.stringify(documentsMetadata));

        // Add files separately
        this.documents.forEach((doc, index) => {
          formData.append(`file_${index}`, doc.file);
        });

        // Add queries as JSON string
        formData.append('queries', JSON.stringify(this.queries));

        // Add export format and orientation
        formData.append('export_format', this.exportFormat.toLowerCase());
        formData.append('orientation', this.orientation);

        console.log('FormData contents:');
        for (let [key, value] of formData.entries()) {
          console.log(key, value);
        }

        try {
          console.log("Sending request to backend");
          const response = await beginExtraction(formData);
          console.log("Received response from backend:", response);
          const jobId = response.data.job_id
          this.setExtractionStatus('Extraction complete')
          this.setDownloadLink(downloadResults(jobId))
        } catch (error) {
          console.error('Extraction failed:', error);
          if (error.response) {
            console.error('Error data:', error.response.data);
            console.error('Error status:', error.response.status);
            console.error('Error headers:', error.response.headers);
          } else if (error.request) {
            console.error('Error request:', error.request);
          } else {
            console.error('Error message:', error.message);
          }
          this.setExtractionStatus('Extraction failed. Please try again.');
        }
      },
      downloadResults() {
        if (this.downloadLink) {
          window.location.href = this.downloadLink
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .extraction-block {
    background-color: #e6f3ff;
    padding: 20px;
    margin-bottom: 20px;
    text-align: center;
    border-radius: 5px;
  }
  
  .begin-extraction, .download-results {
    margin-top: 10px;
    padding: 10px 20px;
    font-size: 16px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .begin-extraction:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  
  .begin-extraction:hover:not(:disabled), .download-results:hover {
    background-color: #45a049;
  }
  
  p {
    margin-top: 10px;
    font-weight: bold;
  }
  </style>