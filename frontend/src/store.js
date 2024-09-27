// store.js
import { createStore } from 'vuex'

export default createStore({
  state: {
    documents: [],
    queries: [],
    exportFormat: 'csv',
    orientation: 'doc_row',
    extractionStatus: '',
    downloadLink: ''
  },
  mutations: {
    setDocuments(state, documentsOrUpdater) {
      if (typeof documentsOrUpdater === 'function') {
        state.documents = documentsOrUpdater(state.documents)
      } else {
        state.documents = documentsOrUpdater
      }
      // Validate documents
      state.documents = state.documents.filter(doc => doc && doc.file);
      console.log('Documents in store after update:', JSON.stringify(state.documents));
    },
    setQueries(state, queriesOrUpdater) {
      if (typeof queriesOrUpdater === 'function') {
        state.queries = queriesOrUpdater(state.queries)
      } else {
        state.queries = queriesOrUpdater
      }
    },
    setExportFormat(state, format) {
      state.exportFormat = format
    },
    setOrientation(state, orientation) {
      state.orientation = orientation
    },
    setExtractionStatus(state, status) {
      state.extractionStatus = status
    },
    setDownloadLink(state, link) {
      state.downloadLink = link
    }
  },
  actions: {
    initializeStore({ commit }) {
      // Initialize store with default values if needed
      commit('setDocuments', [])
      commit('setQueries', [])
      commit('setExportFormat', 'csv')
      commit('setOrientation', 'doc_row')
      commit('setExtractionStatus', '')
      commit('setDownloadLink', '')
    }
  },
  getters: {
    isExtractionReady: state => {
      return state.documents.length > 0 && 
             state.queries.length > 0 && 
             state.queries.every(q => q.Text && q.Alias && q.Format) &&
             state.exportFormat && 
             state.orientation
    },
    hasValidDocuments: state => {
      return state.documents.some(doc => doc && doc.file);
    }
  }
})