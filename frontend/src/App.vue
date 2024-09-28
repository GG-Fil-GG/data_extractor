<!-- App.vue -->
<template>
  <div id="app">
    <h1 class="app-heading">DataExtractor.com</h1>
    <DocumentsBlock />
    <QueriesBlock />
    <ExportBlock />
    <ExtractionBlock />
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import DocumentsBlock from './components/DocumentsBlock.vue'
import QueriesBlock from './components/QueriesBlock.vue'
import ExportBlock from './components/ExportBlock.vue'
import ExtractionBlock from './components/ExtractionBlock.vue'

export default {
  name: 'App',
  components: {
    DocumentsBlock,
    QueriesBlock,
    ExportBlock,
    ExtractionBlock
  },
  created() {
    this.initializeStore()
  },
  methods: {
    ...mapActions(['initializeStore'])
  }
}
</script>

<style>
#app {
  font-family: Calibri, sans-serif;
  max-width: 1123px;
  min-width: 794px;
  margin: 0 auto;
  padding: 20px;
}

.app-heading {
  text-align: center;
  font-size: 36px;
  margin-bottom: 20px;
}
</style>