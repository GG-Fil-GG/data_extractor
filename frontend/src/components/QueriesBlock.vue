<!-- QueriesBlock.vue -->
<template>
  <div class="block">
    <h2 class="block-heading">Queries</h2>
    <div v-if="queries.length > 0" class="fields-header">
      <div class="query-alias-header">Alias</div>
      <div class="query-text-header">Text</div>
      <div class="query-format-header" :style="{ width: maxQueryFormatWidth + 'px' }">Format</div>
      <div class="move-up-button-header"></div>
      <div class="move-down-button-header"></div>
      <div class="remove-button-header"></div>
    </div>
    <div v-for="(query, index) in queries" :key="index" class="query-row">
      <input :value="query.Alias" @input="updateQueryField(index, 'Alias', $event.target.value)" :placeholder="'Query ' + (index + 1)" class="query-alias-field" />
      <input :value="query.Text" @input="updateQueryField(index, 'Text', $event.target.value)" placeholder="Please enter your query here" class="query-text-field" />
      <select :value="query.Format" @change="updateQueryField(index, 'Format', $event.target.value)" class="query-format-field" :style="{ width: maxQueryFormatWidth + 'px' }">
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
      <button
        @click="moveQuery(index, -1)"
        :disabled="index === 0"
        class="move-up-button"
        :class="{ 'disabled': index === 0 }"
      >↑</button>
      <button
        @click="moveQuery(index, 1)"
        :disabled="index === queries.length - 1"
        class="move-down-button"
        :class="{ 'disabled': index === queries.length - 1 }"
      >↓</button>
      <button @click="removeQuery(index)" class="remove-button">×</button>
    </div>
    <button @click="addQuery" class="add-query">Add query</button>
  </div>
</template>

<script>
import { mapState, mapMutations } from 'vuex'

export default {
  name: 'QueriesBlock',
  computed: {
    ...mapState(['queries']),
    maxQueryFormatWidth() {
      const options = [
        'Free-form', 'Integer', 'Floating-point number', 'Comma-separated list', 
        'Yes/No', 'Median (95% CI)', 'Mean (SD)', 'Mean (SE)', 'Range', 'Date (DD-MM-YYYY)'
      ];
      const maxLength = options.reduce((max, option) => option.length > max ? option.length : max, 0);
      return maxLength * 8;
    }
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

.fields-header {
  display: flex;
  align-items: stretch;
  margin-bottom: 10px;
}

.query-alias-header {
  width: 100px;
  flex: none;
  margin-right: 5px;
  padding: 5px;
  font-size: 16px;
  font-weight: bold;
  box-sizing: border-box;
}

.query-text-header {
  flex: 1;
  margin: 0 5px;
  padding: 5px;
  font-size: 16px;
  font-weight: bold;
  box-sizing: border-box;
}

.query-format-header {
  flex: none;
  margin: 0 5px;
  padding: 5px;
  font-size: 16px;
  font-weight: bold;
  box-sizing: border-box;
}

.move-up-button-header {
  flex: none;
  margin: 0 5px;
  width: 30px;
  border: none;
}

.move-down-button-header {
  flex: none;
  margin: 0 5px;
  width: 30px;
  border: none;
}

.remove-button-header {
  flex: none;
  margin-left: 5px;
  width: 30px;
  border: none;
}

.query-row {
  display: flex;
  align-items: stretch;
  height: 30px;
  margin-bottom: 10px;
}

.query-alias-field {
  width: 100px;
  flex: none;
  margin-right: 5px;
  padding: 5px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
}

.query-text-field {
  flex: 1;
  margin: 0 5px;
  padding: 5px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
}

.query-format-field {
  flex: none;
  margin: 0 5px;
  padding: 5px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
}

.move-up-button {
  flex: none;
  margin: 0 5px;
  width: 30px;
  background-color: #008CBA;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 3px;
}

.move-down-button {
  flex: none;
  margin: 0 5px;
  width: 30px;
  background-color: #008CBA;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 3px;
}

.remove-button {
  flex: none;
  margin-left: 5px;
  width: 30px;
  background-color: #008CBA;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 3px;
}

.move-up-button.disabled, .move-down-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.add-query {
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
</style>