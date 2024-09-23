<!-- QueriesBlock.vue -->
<template>
    <div class="block queries-block">
      <h2>Queries</h2>
      <div v-for="(query, index) in queries" :key="index" class="query-row">
        <input v-model="query.alias" :placeholder="'Query ' + (index + 1)" class="query-alias" />
        <input v-model="query.text" placeholder="Please enter your query here" class="query-text" />
        <select v-model="query.format" class="query-format">
          <option value="free-form">Free-form</option>
          <option value="integer">Integer</option>
          <option value="float">Floating-point number</option>
          <!-- Add more options as needed -->
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
  export default {
    name: 'QueriesBlock',
    data() {
      return {
        queries: []
      }
    },
    methods: {
      addQuery() {
        this.queries.push({
          alias: `Query ${this.queries.length + 1}`,
          text: '',
          format: 'free-form'
        })
      },
      moveQuery(index, direction) {
        const newIndex = index + direction
        if (newIndex >= 0 && newIndex < this.queries.length) {
          const temp = this.queries[index]
          this.$set(this.queries, index, this.queries[newIndex])
          this.$set(this.queries, newIndex, temp)
        }
      },
      removeQuery(index) {
        this.queries.splice(index, 1)
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
    width: 150px;
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