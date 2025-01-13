// main.js
import { createApp } from 'vue'
import App from './App.vue'
import store from './store'
import './global.css'  // Import the global stylesheet

createApp(App).use(store).mount('#app')