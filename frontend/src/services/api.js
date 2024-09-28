import axios from 'axios';

export const beginExtraction = (formData) => {
  return axios.post('/begin_extraction', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

export const downloadResults = async (jobId) => {
  const response = await axios.get(`/download_results`, { params: { job_id: jobId } });
  return response.data.downloadUrl;
};

// Add the countTokens function
export const countTokens = (formData) => {
  return axios.post('/count_tokens', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};
