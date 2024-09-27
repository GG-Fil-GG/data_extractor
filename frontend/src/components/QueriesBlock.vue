<!-- QueriesBlock.vue -->
<template>
    <div class="block queries-block">
      <h2>Queries</h2>
      <div v-for="(query, index) in queries" :key="index" class="query-row">
        <input :value="query.Alias" @input="updateQueryField(index, 'Alias', $event.target.value)" :placeholder="'Query ' + (index + 1)" class="query-alias" />
        <input :value="query.Text" @input="updateQueryField(index, 'Text', $event.target.value)" placeholder="Please enter your query here" class="query-text" />
        <select :value="query.Format" @change="updateQueryField(index, 'Format', $event.target.value)" class="query-format">
          <option value="free-form">Free-form</option>
          <option value="integer">Integer</option>
          <option value="floating-point number">Floating-point number</option>
          <option value="comma-separated list">Comma-separated list</option>
          <option value="yes/no">Yes/No</option>
          <option value="median (95% CI)">Median (95% CI)</option>
          <option value="mean (SD)">Mean (SD)</option>
          <option value="mean (SE)">Mean (SE)</option>
          <option value="range">Range</option>
          <option value="date (DD-MM-YYYY)">Date (DD-MM-YYYY)</option>
        </select>
        <div class="query-controls">
          <button @click="moveQuery(index, -1)" :disabled="index === 0">↑</button>
          <button @click="moveQuery(index, 1)" :disabled="index === queries.length - 1">↓</button>
          <button @click="removeQuery(index)">×</button>
        </div>
      </div>
      <button @click="addQuery" class="add-query">Add query</button>
    </div>
  </template>
  
  <script>
  import { mapState, mapMutations } from 'vuex'
  
  export default {
    name: 'QueriesBlock',
    computed: {
      ...mapState(['queries'])
    },
    methods: {
      ...mapMutations(['setQueries']),
      addQuery() {
        this.setQueries(queries => [
          ...queries,
          { Alias: `Query ${queries.length + 1}`, Text: '', Format: 'free-form' }
        ])
      },
      moveQuery(index, direction) {
        const newIndex = index + direction
        if (newIndex >= 0 && newIndex < this.queries.length) {
          this.setQueries(queries => {
            const newQueries = [...queries]
            const temp = newQueries[index]
            newQueries[index] = newQueries[newIndex]
            newQueries[newIndex] = temp
            return newQueries
          })
        }
      },
      removeQuery(index) {
        this.setQueries(queries => queries.filter((_, i) => i !== index))
      },
      updateQueryField(index, field, value) {
        this.setQueries(queries => {
          const newQueries = [...queries]
          newQueries[index] = { ...newQueries[index], [field]: value }
          return newQueries
        })
      },
      validateQueries() {
        return this.queries.every(query => query.Text.trim() !== '')
      }
    }
  }
  </script>
  
  <style scoped>
  .queries-block {
    background-color: #e6f3ff;
    padding: 20px;
    margin-bottom: 20px;
  }
  
  .query-row {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .query-alias {
    width: 100px;
    padding: 5px;
    margin-right: 10px;
  }
  
  .query-text {
    flex: 2;
    padding: 5px;
    margin-right: 10px;
  }
  
  .query-format {
    width: 200px;
    padding: 5px;
    margin-right: 10px;
  }
  
  .query-controls button {
    margin-left: 5px;
  }
  
  .add-query {
    margin-top: 10px;
  }
  </style>