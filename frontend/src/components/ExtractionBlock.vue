<!-- ExtractionBlock.vue -->
<template>
  <div class="block">
    <h2 class="block-heading">Extraction</h2>
    <div class="extraction-content">
      <button v-if="!isExtracting && !downloadLink" @click="beginExtraction" :disabled="!canExtract" class="extraction-button">Begin extraction</button>
      <p v-if="isExtracting" class="extraction-status">Extraction in progress</p>
      <button v-if="downloadLink" @click="downloadResults" class="extraction-button">Download results</button>
      <p v-if="extractionStatus && !isExtracting" class="extraction-status">{{ extractionStatus }}</p>
      <button v-if="downloadLink || extractionStatus" @click="resetExtraction" class="reset-button">Reset</button>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from 'vuex'
import { beginExtraction, downloadResults } from '../services/api'

export default {
  name: 'ExtractionBlock',
  data() {
    return {
      jobId: null,
      currentJobId: null,
      isExtracting: false,
    }
  },
  computed: {
    ...mapState(['documents', 'queries', 'exportFormat', 'orientation', 'extractionStatus', 'downloadLink']),
    ...mapGetters(['isExtractionReady', 'hasValidDocuments']),
    canExtract() {
      console.log('isExtractionReady:', this.isExtractionReady);
      console.log('hasValidDocuments:', this.hasValidDocuments);
      return this.isExtractionReady && this.hasValidDocuments;
    }
  },
  methods: {
    ...mapMutations(['setExtractionStatus', 'setDownloadLink']),
    ...mapActions(['initializeStore']),
    async beginExtraction() {
      this.isExtracting = true;
      this.setExtractionStatus('');
      console.log('Beginning extraction. Documents:', JSON.stringify(this.documents));
      const formData = new FormData();

      // Prepare documents metadata
      const documentsMetadata = this.documents.map((doc) => ({
        Alias: doc.Alias,
        Ext: doc.Ext,
        Path: doc.filePath
      }));
      console.log('Documents metadata being sent:', documentsMetadata);
      formData.append('documents', JSON.stringify(documentsMetadata));

      // Prepare queries
      formData.append('queries', JSON.stringify(this.queries));

      // Add export format and orientation
      formData.append('export_format', this.exportFormat);
      formData.append('orientation', this.orientation);

      try {
        console.log("Sending request to backend");
        const response = await beginExtraction(formData);
        console.log("Received response from backend:", response);
        this.currentJobId = response.data.job_id;
        this.setExtractionStatus('Extraction complete');
        const downloadUrl = await downloadResults(this.currentJobId);
        this.setDownloadLink(downloadUrl);
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
      } finally {
        this.isExtracting = false;
      }
    },
    downloadResults() {
      if (this.downloadLink) {
        window.open(this.downloadLink, '_blank');
      } else {
        console.error('No download link available');
        this.setExtractionStatus('Download failed. Please try again.');
      }
    },
    resetExtraction() {
      this.setExtractionStatus('');
      this.setDownloadLink('');
      this.isExtracting = false;
      this.currentJobId = null;
      this.initializeStore(); // Reset the store state
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

.extraction-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.extraction-button {
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

.extraction-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.extraction-button:hover:not(:disabled) {
  background-color: #007B9A;
}

.extraction-status {
  margin-top: 10px;
  font-weight: bold;
  color: #333;
}

.reset-button {
  margin-top: 10px;
  height: 30px;
  padding: 5px 10px;
  font-size: 16px;
  background-color: #f44336;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 3px;
}

.reset-button:hover {
  background-color: #d32f2f;
}
</style>