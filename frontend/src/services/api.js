import axios from 'axios';

export const beginExtraction = (formData) => {
  return axios.post('/begin_extraction', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

export const downloadResults = (jobId) => {
  return `/download_results/${jobId}`;
};
