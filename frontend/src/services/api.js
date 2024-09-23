import axios from 'axios';

const API_URL = 'http://localhost:5000';

export const uploadFiles = (files) => {
  let formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });
  return axios.post(`${API_URL}/begin_extraction`, formData);
};

export const startExtraction = (data) => {
  return axios.post(`${API_URL}/begin_extraction`, data);
};
