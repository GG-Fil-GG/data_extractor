<!-- QueriesBlock.vue -->
<template>
  <div class="block">
    <h2 class="block-heading">Queries</h2>
    <div v-if="queries.length > 0" class="fields-header">
      <div class="query-alias-header">Alias</div>
      <div class="query-text-header">Text</div>
      <div class="query-format-header">Format</div>
      <div class="actions-header">Actions</div>
    </div>
    <div v-for="(query, index) in queries" :key="index" class="query-row">
      <input :value="query.Alias" @input="updateQueryField(index, 'Alias', $event.target.value)" :placeholder="'Query ' + (index + 1)" class="query-alias-field" />
      <span v-if="errors[index] && errors[index].Alias" class="error">{{ errors[index].Alias }}</span>
      <input :value="query.Text" @input="updateQueryField(index, 'Text', $event.target.value)" placeholder="Please enter your query here" class="query-text-field" />
      <span v-if="errors[index] && errors[index].Text" class="error">{{ errors[index].Text }}</span>
      <select :value="query.Format" @change="updateQueryField(index, 'Format', $event.target.value)" class="query-format-field">
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
      <div class="actions">
        <button
          @click="moveQuery(index, -1)"
          :disabled="index === 0"
          class="move-up-button"
        >↑</button>
        <button
          @click="moveQuery(index, 1)"
          :disabled="index === queries.length - 1"
          class="move-down-button"
        >↓</button>
        <button @click="removeQuery(index)" class="remove-button">×</button>
      </div>
    </div>
    <button @click="addQuery" class="add-query">Add query</button>
  </div>
</template>

<script>
import { mapState, mapMutations } from 'vuex'

export default {
  name: 'QueriesBlock',
  data() {
    return {
      errors: []
    }
  },
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
      const newQueries = [...this.queries]
      newQueries[index] = { ...newQueries[index], [field]: value }

      // Validate the updated field
      this.errors[index] = this.errors[index] || {}
      if (field === 'Alias') {
        if (!value.trim()) {
          this.errors[index].Alias = 'Alias cannot be empty'
        } else if (newQueries.some((query, i) => i !== index && query.Alias === value)) {
          this.errors[index].Alias = 'Alias must be unique'
        } else {
          this.errors[index].Alias = ''
        }
      } else if (field === 'Text') {
        if (!value.trim()) {
          this.errors[index].Text = 'Text cannot be empty'
        } else {
          this.errors[index].Text = ''
        }
      }

      // Update the queries if there are no errors
      if (!this.errors[index].Alias && !this.errors[index].Text) {
        this.setQueries(() => newQueries)
      }
    },
    validateQueries() {
      return this.queries.every(query => query.Text.trim() !== '')
    },
  },
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
  font-size: 28px;
  color: #333;
}

.fields-header, .query-row {
  display: grid;
  grid-template-columns: 200px 3fr 200px 110px;
  align-items: stretch;
  height: 30px;
  gap: 10px;
  margin-bottom: 10px;
}

.query-alias-header, .query-text-header, .query-format-header, .actions-header {
  padding: 5px;
  font-size: 16px;
  font-weight: bold;
}

.query-alias-field, .query-text-field, .query-format-field {
  padding: 5px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 3px;
}

.actions {
  display: flex;
  gap: 10px;
}

.move-up-button, .move-down-button, .remove-button {
  width: 30px;
  background-color: #008CBA;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 3px;
  padding: 5px;
  box-sizing: border-box;
}

.move-up-button:disabled, .move-down-button:disabled {
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

.error {
  color: red;
  font-size: 12px;
  margin-left: 5px;
}
</style>